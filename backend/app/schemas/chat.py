"""
Pydantic Schemas for Conversational Medical Chat endpoints.
Supports structured clinical conversation state machine, patient profile intake,
symptom characterization, safety screening, RAG evidence, and qualitative assessment.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class StartChatResponse(BaseModel):
    session_id: str = Field(..., description="Unique chat session identifier")
    message: str = Field(default="Hi! Please tell me what symptoms or health problems you are currently experiencing.", description="Initial clinical greeting")
    stage: str = Field(default="INITIAL_COMPLAINT", description="Current conversation stage")


class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., description="Active session ID")
    message: str = Field(..., description="Patient text message describing symptoms or answering questions")


class PatientSummarySchema(BaseModel):
    age: Optional[int] = Field(default=None, description="Patient age")
    sex: Optional[str] = Field(default=None, description="Patient biological sex")
    weight_kg: Optional[float] = Field(default=None, description="Weight in kg")


class CandidateDiseaseSchema(BaseModel):
    disease: str = Field(..., description="Disease name")
    probability: float = Field(..., description="Internal model confidence score (0.0 to 1.0)")
    percentage: Optional[float] = Field(default=None, description="Internal model percentage")
    icd9_code: Optional[str] = Field(default=None, description="ICD-9 code if available")


class ConditionAssessmentSchema(BaseModel):
    condition: str
    assessment_level: str = Field(..., description="'more_likely', 'possible', or 'important_to_exclude'")
    description: Optional[str] = None


class AssessmentResultSchema(BaseModel):
    summary: str
    patient_summary: Dict[str, Any] = Field(default_factory=dict)
    likely_conditions: List[ConditionAssessmentSchema] = Field(default_factory=list)
    why_considered: List[str] = Field(default_factory=list)
    safety_screening: Dict[str, Any] = Field(default_factory=dict)
    tests_to_consider: List[Dict[str, Any]] = Field(default_factory=list)
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    uncertainty: str = Field(default="moderate")
    treatment_information: Optional[str] = Field(default=None)
    research_drugs: List[Dict[str, Any]] = Field(default_factory=list)


class EvidenceSchema(BaseModel):
    title: str = Field(..., description="Document title")
    source: str = Field(..., description="Authoritative publication source")
    url: str = Field(default="", description="Source link URL")
    disease: Optional[str] = Field(default="", description="Associated disease name")
    section: Optional[str] = Field(default="", description="Section header")
    score: float = Field(default=0.0, description="RAG relevance score")
    summary: str = Field(..., description="Relevant text excerpt")
    why_retrieved: Optional[str] = Field(default="", description="Rationale for retrieval")


class ChatResponse(BaseModel):
    type: str = Field(..., description="Response type: 'initial_complaint', 'profile_collection', 'followup_question', 'test_consideration', 'final_assessment', or 'urgent_attention'")
    session_id: str = Field(..., description="Active session ID")
    message: Optional[str] = Field(default=None, description="Clinical response or question")
    stage: str = Field(default="INITIAL_COMPLAINT", description="Current state machine stage")
    patient_summary: Optional[PatientSummarySchema] = Field(default=None, description="Collected patient profile attributes")
    assessment: Optional[AssessmentResultSchema] = Field(default=None, description="Patient-facing qualitative assessment")
    quick_replies: Optional[List[str]] = Field(default=None, description="Optional quick-reply options")
    question_reason: Optional[str] = Field(default=None, description="Clinical reason for this question")
    most_likely_condition: Optional[str] = Field(default=None, description="Leading candidate condition name")
    confidence: Optional[float] = Field(default=None, description="Confidence score")
    candidate_diseases: List[CandidateDiseaseSchema] = Field(default_factory=list, description="Internal model candidate diseases")
    evidence: List[EvidenceSchema] = Field(default_factory=list, description="Retrieved medical evidence citations")
    red_flags: List[str] = Field(default_factory=list, description="Clinical red flags identified")
    tests_suggested: List[Dict[str, Any]] = Field(default_factory=list, description="Suggested diagnostic tests")
    research_drugs: List[Dict[str, Any]] = Field(default_factory=list, description="Historical research drug candidates")
    needs_medical_evaluation: bool = Field(default=True, description="Disclaimer flag")
    continue_chat: bool = Field(default=True, description="Whether conversation can continue")
    extracted_symptoms: List[str] = Field(default_factory=list, description="All recognized patient symptoms")
    unmatched_symptoms: List[str] = Field(default_factory=list, description="Unmatched patient symptom strings")
    duration: Dict[str, str] = Field(default_factory=dict, description="Symptom duration mapping")


class ChatSessionStateResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    symptoms: List[str]
    duration: Dict[str, str] = Field(default_factory=dict)
    unmatched_symptoms: List[str]
    candidate_diseases: List[CandidateDiseaseSchema]
    questions_asked: List[str]
    iteration: int
    is_completed: bool
    patient_summary: Optional[PatientSummarySchema] = None
    stage: str = "INITIAL_COMPLAINT"
