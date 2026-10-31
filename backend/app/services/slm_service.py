"""
Placeholder module for future SLM (Small Language Model) service.

This module will provide natural language explanations of risk predictions
once an SLM/RAG layer is integrated. The API contract for /api/slm/explain
is reserved and must not be used by other services.

Future integration points:
  - slm_service.explain_prediction(prediction_result, patient_data) -> str
  - rag_service.search_clinical_context(condition, risk_label) -> List[str]
  - feedback_service.record_feedback(session_id, feedback) -> None
  - rl_service.update_policy(feedback_batch) -> None

DO NOT implement these services in the current version.
"""

# This file intentionally left empty for future SLM/RAG integration.
# See: Section 37-38 of project specification.
