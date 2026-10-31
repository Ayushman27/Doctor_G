"""
Conversational Medical RAG + State Machine Clinical Router.
Orchestrates:
1. INITIAL_COMPLAINT: Prompt patient to describe symptoms first.
2. Hard Programmatic Rule: Block predictions/questions/tests/drugs while symptoms list is empty.
3. SYMPTOM_EXTRACTION & Validation.
4. PATIENT_PROFILE: Collect Age, Sex, Weight ONLY after symptoms are identified.
5. Deterministic Red-Flag Safety Screening (ANY STATE -> URGENT_EVALUATION).
6. SYMPTOM_CHARACTERIZATION: Symptom-specific questioning driven by Advanced Hybrid RAG.
7. INFORMATION_SUFFICIENCY_CHECK & TEST_CONSIDERATION.
8. FINAL_ASSESSMENT & TREATMENT_INFORMATION: Qualitative differential, evidence-based treatment info & OpenFDA drug recommendations.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Path as APIPath

from app.core.config import settings
from app.core.model_loader import registry
from app.schemas.chat import (
    StartChatResponse,
    ChatMessageRequest,
    ChatResponse,
    CandidateDiseaseSchema,
    EvidenceSchema,
    ChatSessionStateResponse,
    PatientSummarySchema,
    ConditionAssessmentSchema,
    AssessmentResultSchema,
)
from app.clinical.conversation_state import ConversationStage
from app.clinical.symptom_extractor import extract_symptoms_and_duration
from app.clinical.red_flag_engine import evaluate_clinical_red_flags
from app.clinical.clinical_question_service import generate_next_clinical_question
from app.clinical.information_sufficiency_service import evaluate_information_sufficiency
from app.clinical.test_selection_service import recommend_diagnostic_tests, analyze_patient_test_results
from app.services.conversation_service import (
    create_session,
    get_session,
    update_session,
    add_message,
)
from app.services.clinical_context_service import (
    PatientProfile,
    ClinicalContext,
    parse_age,
    parse_sex,
    parse_weight,
    extract_patient_profile_update,
    get_next_profile_prompt,
)
from app.services.assessment_service import build_patient_facing_assessment
from app.services.disease_service import predict_disease_from_symptoms
from app.services.rag_service import retrieve_medical_evidence
from rag.query_builder import RAGQueryType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Conversational Diagnostic Support"])


@router.post("/start", response_model=StartChatResponse)
async def start_chat() -> StartChatResponse:
    """Start a new conversational medical chat session in INITIAL_COMPLAINT stage."""
    session = create_session()
    welcome_text = "Hi! Please tell me what symptoms or health problems you are currently experiencing."
    add_message(session["session_id"], "assistant", welcome_text)
    return StartChatResponse(
        session_id=session["session_id"],
        message=welcome_text,
        stage=ConversationStage.INITIAL_COMPLAINT.value
    )


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(request: ChatMessageRequest) -> ChatResponse:
    """
    Process incoming patient message through the 12-state clinical state machine.
    """
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found or expired.")

    if session.get("is_completed", False):
        raise HTTPException(status_code=400, detail="This chat session is already completed.")

    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(status_code=422, detail="Message content cannot be empty.")

    # Record User Message
    add_message(request.session_id, "user", user_msg)

    # 1. Symptom & Duration Extraction
    extracted_payload = extract_symptoms_and_duration(user_msg)
    new_symptoms = extracted_payload["symptoms"]
    new_duration = extracted_payload["duration"]
    new_unmatched = extracted_payload["unmatched"]

    current_symptoms = list(dict.fromkeys(session.get("symptoms", []) + new_symptoms))
    current_duration = session.get("duration", {})
    current_duration.update(new_duration)
    current_unmatched = list(dict.fromkeys(session.get("unmatched_symptoms", []) + new_unmatched))

    update_session(request.session_id, {
        "symptoms": current_symptoms,
        "duration": current_duration,
        "unmatched_symptoms": current_unmatched
    })

    # =========================================================================
    # CRITICAL HARD RULE ENFORCEMENT
    # IF state.symptoms == empty THEN stage = INITIAL_COMPLAINT
    # Do NOT execute disease prediction, question generation, tests, or drugs!
    # =========================================================================
    if not current_symptoms:
        msg_lower = user_msg.lower()
        if any(w in msg_lower for w in ["don't feel well", "not feeling well", "don't know", "feel sick", "unwell"]):
            reply_text = (
                "I'm sorry you're not feeling well. Could you describe what you're experiencing, "
                "such as any pain, fever, cough, stomach problems, breathing difficulty, or other symptoms?"
            )
        else:
            reply_text = "Hi! Please tell me what symptoms or health problems you are currently experiencing."

        update_session(request.session_id, {"conversation_stage": ConversationStage.INITIAL_COMPLAINT.value})
        add_message(request.session_id, "assistant", reply_text)

        return ChatResponse(
            type="initial_complaint",
            session_id=request.session_id,
            message=reply_text,
            stage=ConversationStage.INITIAL_COMPLAINT.value,
            quick_replies=[
                "I have loose motion and stomach pain",
                "I have chest pain",
                "I have cough and fever",
                "I have headache"
            ],
            continue_chat=True
        )

    # 2. Update Patient Profile State (Opportunistic or Prompted)
    profile_dict = session.get("patient_profile", {"age": None, "sex": None, "weight": None, "height": None})
    target_field = session.get("current_profile_target")

    if target_field:
        field_updates = extract_patient_profile_update(user_msg, target_field)
        profile_dict.update(field_updates)

    if profile_dict.get("age") is None:
        parsed_a = parse_age(user_msg)
        if parsed_a is not None:
            profile_dict["age"] = parsed_a

    if profile_dict.get("sex") is None:
        parsed_s = parse_sex(user_msg)
        if parsed_s is not None:
            profile_dict["sex"] = parsed_s

    if profile_dict.get("weight") is None:
        parsed_w = parse_weight(user_msg)
        if parsed_w is not None:
            profile_dict["weight"] = parsed_w

    update_session(request.session_id, {"patient_profile": profile_dict})
    profile_obj = PatientProfile(
        age=profile_dict.get("age"),
        sex=profile_dict.get("sex"),
        weight_kg=profile_dict.get("weight"),
        medical_history=session.get("medical_history", [])
    )

    # 3. Deterministic Safety & Red-Flag Screening (ANY STATE -> URGENT_EVALUATION)
    rf_eval = evaluate_clinical_red_flags(
        message=user_msg,
        symptoms=current_symptoms,
        symptom_details=session.get("symptom_details", {}),
        age=profile_obj.age
    )

    if rf_eval["is_emergency"]:
        update_session(request.session_id, {
            "conversation_stage": ConversationStage.URGENT_EVALUATION.value,
            "red_flags": rf_eval["red_flags"]
        })
        add_message(request.session_id, "assistant", rf_eval["urgent_message"])
        return ChatResponse(
            type="urgent_attention",
            session_id=request.session_id,
            message=rf_eval["urgent_message"],
            stage=ConversationStage.URGENT_EVALUATION.value,
            red_flags=rf_eval["red_flags"],
            patient_summary=PatientSummarySchema(
                age=profile_obj.age,
                sex=profile_obj.sex,
                weight_kg=profile_obj.weight_kg
            ),
            extracted_symptoms=[s.replace("_", " ").title() for s in current_symptoms],
            unmatched_symptoms=current_unmatched,
            duration=current_duration,
            continue_chat=True,
            needs_medical_evaluation=True
        )

    # 4. Patient Profile Intake Stage (ONLY AFTER symptoms identified!)
    next_target, profile_question, quick_replies = get_next_profile_prompt(profile_obj)
    if next_target is not None:
        sym_str = ", ".join([s.replace("_", " ") for s in current_symptoms])
        prompt_with_context = f"I understand that you're experiencing {sym_str}.\n\n{profile_question}"

        update_session(request.session_id, {
            "current_profile_target": next_target,
            "conversation_stage": ConversationStage.PATIENT_PROFILE.value
        })
        add_message(request.session_id, "assistant", prompt_with_context)

        return ChatResponse(
            type="profile_collection",
            session_id=request.session_id,
            message=prompt_with_context,
            stage=ConversationStage.PATIENT_PROFILE.value,
            quick_replies=quick_replies,
            patient_summary=PatientSummarySchema(
                age=profile_obj.age,
                sex=profile_obj.sex,
                weight_kg=profile_obj.weight_kg
            ),
            extracted_symptoms=[s.replace("_", " ").title() for s in current_symptoms],
            unmatched_symptoms=current_unmatched,
            duration=current_duration,
            continue_chat=True
        )

    # Profile collection complete
    update_session(request.session_id, {"current_profile_target": None})

    # Record previous question-answer pair
    last_q = session.get("last_question")
    if last_q:
        answers = session.get("answers", [])
        answers.append({"question": last_q, "answer": user_msg})
        update_session(request.session_id, {"answers": answers})

    # 5. Internal ML Model Priors (Candidate conditions)
    candidate_diseases_schema: List[CandidateDiseaseSchema] = []
    disease_preds_dict: List[Dict[str, Any]] = []

    try:
        prediction_resp = predict_disease_from_symptoms(current_symptoms, top_k=5)
        for pred in prediction_resp.predictions:
            candidate_diseases_schema.append(
                CandidateDiseaseSchema(
                    disease=pred.disease,
                    probability=pred.probability,
                    percentage=pred.percentage,
                    icd9_code=pred.icd9_code
                )
            )
            disease_preds_dict.append({
                "disease": pred.disease,
                "probability": pred.probability,
                "percentage": pred.percentage
            })
    except Exception as exc:
        logger.error("Internal ML disease model error: %s", exc)

    update_session(request.session_id, {"candidate_diseases": disease_preds_dict})

    # 6. Advanced Hybrid RAG Retrieval
    retrieved_evidence = retrieve_medical_evidence(
        symptoms=current_symptoms,
        candidate_diseases=disease_preds_dict,
        current_message=user_msg,
        patient_profile=profile_dict,
        query_type=RAGQueryType.QUESTION_GENERATION,
        top_k=settings.rag_top_k
    )
    evidence_schema_list = [EvidenceSchema(**e) for e in retrieved_evidence]

    # 7. Information Sufficiency Evaluation
    questions_asked = session.get("questions_asked", [])
    answers_history = session.get("answers", [])
    sufficiency_eval = evaluate_information_sufficiency(
        symptoms=current_symptoms,
        symptom_details=session.get("symptom_details", {}),
        patient_profile=profile_dict,
        questions_asked=questions_asked,
        answers_history=answers_history,
        red_flags=session.get("red_flags", [])
    )

    if sufficiency_eval["status"] == "NEED_MORE_INFORMATION" and len(questions_asked) < getattr(settings, "max_followup_questions", 5):
        next_q_data = generate_next_clinical_question(
            symptoms=current_symptoms,
            symptom_details=session.get("symptom_details", {}),
            patient_profile=profile_dict,
            candidate_conditions=disease_preds_dict,
            questions_asked=questions_asked,
            previous_answers=answers_history,
            red_flags=session.get("red_flags", []),
            rag_evidence=retrieved_evidence
        )

        next_q = next_q_data["question"]
        if next_q and next_q not in questions_asked:
            questions_asked.append(next_q)
            update_session(request.session_id, {
                "questions_asked": questions_asked,
                "last_question": next_q,
                "conversation_stage": ConversationStage.SYMPTOM_CHARACTERIZATION.value
            })
            add_message(request.session_id, "assistant", next_q)

            return ChatResponse(
                type="followup_question",
                session_id=request.session_id,
                message=next_q,
                stage=ConversationStage.SYMPTOM_CHARACTERIZATION.value,
                quick_replies=next_q_data.get("quick_replies"),
                question_reason=next_q_data.get("reason"),
                patient_summary=PatientSummarySchema(
                    age=profile_obj.age,
                    sex=profile_obj.sex,
                    weight_kg=profile_obj.weight_kg
                ),
                candidate_diseases=candidate_diseases_schema,
                evidence=evidence_schema_list,
                extracted_symptoms=[s.replace("_", " ").title() for s in current_symptoms],
                unmatched_symptoms=current_unmatched,
                duration=current_duration,
                continue_chat=True
            )

    # 8. Test Consideration & Context-Aware Final Assessment Stage
    clinical_ctx = ClinicalContext(
        patient_profile=profile_obj,
        symptoms=current_symptoms,
        symptom_details=session.get("symptom_details", {}),
        associated_symptoms=current_unmatched,
        risk_factors=[],
        answers_history=session.get("answers", [])
    )

    assessment_res = build_patient_facing_assessment(
        context=clinical_ctx,
        candidate_diseases_ml=disease_preds_dict,
        retrieved_evidence=retrieved_evidence,
        duration_map=current_duration
    )

    leading_cond = assessment_res.likely_conditions[0].condition if assessment_res.likely_conditions else "Common Condition"

    likely_cond_str = "\n".join([
        f"• {c.condition} ({c.assessment_level.replace('_', ' ').title()})"
        for c in assessment_res.likely_conditions
    ])
    why_str = "\n".join([f"• {w}" for w in assessment_res.why_considered])
    tests_str = "\n".join([f"• {t['test_name']}: {t['reason']}" for t in assessment_res.tests_to_consider]) if assessment_res.tests_to_consider else "None routinely indicated based on current data."

    if assessment_res.research_drugs:
        drug_blocks = []
        for d in assessment_res.research_drugs:
            d_name = str(d.get('drug_name', 'Medication')).title()
            cond = str(d.get('indicated_condition', leading_cond))
            ing = str(d.get('active_ingredient', 'Not specified'))
            ind = str(d.get('fda_indications', 'Consult physician for usage.'))
            status = "OpenFDA Verified" if d.get("fda_verified") else "Clinical Candidate"
            drug_blocks.append(
                f"• Medication: {d_name}\n"
                f"  - Target Condition: {cond}\n"
                f"  - Active Ingredient: {ing}\n"
                f"  - What it is & FDA Indication: {ind}\n"
                f"  - Status: {status}"
            )
        drugs_str = "\n\n".join(drug_blocks)
    else:
        drugs_str = "Consult a physician for prescription guidance."

    formatted_assessment_text = (
        f"PATIENT CLINICAL SUMMARY:\n{assessment_res.summary}\n\n"
        f"MOST LIKELY CONDITIONS CONSIDERED:\n{likely_cond_str}\n\n"
        f"WHY THESE WERE CONSIDERED:\n{why_str}\n\n"
        f"DIAGNOSTIC TESTS THAT MAY BE CONSIDERED:\n{tests_str}\n\n"
        f"RECOMMENDED DRUG CANDIDATES (OpenFDA Verified):\n{drugs_str}\n\n"
        f"TREATMENT & GENERAL GUIDANCE:\n{assessment_res.treatment_information}\n\n"
        "IMPORTANT: This assessment is generated for educational and diagnostic-support research purposes. "
        "It is not a confirmed medical diagnosis. Please consult a qualified doctor for clinical evaluation."
    )

    update_session(request.session_id, {
        "is_completed": True,
        "conversation_stage": ConversationStage.FINAL_ASSESSMENT.value,
        "assessment": assessment_res.model_dump()
    })
    add_message(request.session_id, "assistant", formatted_assessment_text)

    assessment_schema = AssessmentResultSchema(
        summary=assessment_res.summary,
        patient_summary=assessment_res.patient_summary,
        likely_conditions=[
            ConditionAssessmentSchema(
                condition=c.condition,
                assessment_level=c.assessment_level,
                description=c.description
            ) for c in assessment_res.likely_conditions
        ],
        why_considered=assessment_res.why_considered,
        safety_screening=assessment_res.safety_screening,
        tests_to_consider=assessment_res.tests_to_consider,
        supporting_evidence=retrieved_evidence[:3],
        uncertainty=assessment_res.uncertainty,
        treatment_information=assessment_res.treatment_information,
        research_drugs=assessment_res.research_drugs
    )

    leading_cond = assessment_res.likely_conditions[0].condition if assessment_res.likely_conditions else "Common condition"

    return ChatResponse(
        type="final_assessment",
        session_id=request.session_id,
        message=formatted_assessment_text,
        stage=ConversationStage.FINAL_ASSESSMENT.value,
        assessment=assessment_schema,
        most_likely_condition=leading_cond,
        confidence=0.88,
        patient_summary=PatientSummarySchema(
            age=profile_obj.age,
            sex=profile_obj.sex,
            weight_kg=profile_obj.weight_kg
        ),
        candidate_diseases=candidate_diseases_schema,
        evidence=evidence_schema_list,
        tests_suggested=assessment_res.tests_to_consider,
        research_drugs=assessment_res.research_drugs,
        extracted_symptoms=[s.replace("_", " ").title() for s in current_symptoms],
        unmatched_symptoms=current_unmatched,
        duration=current_duration,
        needs_medical_evaluation=True,
        continue_chat=False
    )


@router.get("/{session_id}", response_model=ChatSessionStateResponse)
async def get_chat_session(
    session_id: str = APIPath(..., description="Unique session ID")
) -> ChatSessionStateResponse:
    """Retrieve current conversation state and history for a session."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    candidates = [CandidateDiseaseSchema(**c) for c in session.get("candidate_diseases", [])]
    prof = session.get("patient_profile", {})
    patient_summary = PatientSummarySchema(
        age=prof.get("age"),
        sex=prof.get("sex"),
        weight_kg=prof.get("weight")
    ) if prof else None

    return ChatSessionStateResponse(
        session_id=session["session_id"],
        messages=session.get("messages", []),
        symptoms=session.get("symptoms", []),
        duration=session.get("duration", {}),
        unmatched_symptoms=session.get("unmatched_symptoms", []),
        candidate_diseases=candidates,
        questions_asked=session.get("questions_asked", []),
        iteration=session.get("iteration", 0),
        is_completed=session.get("is_completed", False),
        patient_summary=patient_summary,
        stage=session.get("conversation_stage", ConversationStage.INITIAL_COMPLAINT.value)
    )
