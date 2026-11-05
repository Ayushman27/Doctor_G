# Intelligent Patient Stratification & Conversational Medical RAG + LLM System

> **⚠ Research & Educational Prototype Only.** This system is NOT an autonomous doctor or a clinical diagnostic system. It functions strictly as a research diagnostic-support layer.

A full-stack, production-structured medical platform combining:
1. **Existing Symptom → Disease Model**: Scikit-Learn Logistic Regression model (`disease_prediction_model.pkl`) predicting disease probabilities from 133 symptoms.
2. **Existing Patient/Lab Risk Stratification**: XGBoost and Random Forest models (`patient_ai_models/`) for patient risk stratification and drug candidate summary ranking.
3. **Conversational Medical RAG + LLM Layer**: Authoritative medical knowledge base (WHO, CDC, NIH, MedlinePlus, Merck Manual) indexed via FAISS vector store and `sentence-transformers`, coupled with modular LLM reasoning and intelligent follow-up questioning.

---

## Architecture Flow

```text
Patient Symptoms / Natural Language Input
                  ↓
       Symptom Extraction (LLM + Canonical Key Matcher)
                  ↓
   Existing Symptom → Disease ML Model (disease_model.pkl)
                  ↓
     Top Disease Candidates + Model Confidence Scores
                  ↓
      Medical RAG Retriever (FAISS + sentence-transformers)
                  ↓
       Retrieved Authoritative Medical Evidence Chunks
                  ↓
  Modular LLM Reasoning (Google Gemini / Cloud Deployment / Local Fallback)
                  ↓
   Determine: ASK_FOLLOWUP vs FINAL_ASSESSMENT vs URGENT_ATTENTION
                  ↓
┌─────────────────┴──────────────────┐
│                                    │
▼                                    ▼
Ask Targeted Follow-Up Question     Final Assessment
(Max 5, No Duplicates)             (Likely Condition + Scores + Evidence + Drug Candidates)
│
└──────────── Patient Answers ───────┘
```

---

## Project Structure

```text
patient-ai-system/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point & lifespan model/RAG initialization
│   │   ├── api/                     # Route handlers
│   │   │   ├── chat.py              # POST /api/chat/start, /message, GET /{session_id}
│   │   │   ├── disease.py           # POST /api/disease/predict, GET /symptoms
│   │   │   ├── patient.py           # POST /api/patient/predict, /api/analysis
│   │   │   ├── drugs.py             # GET /api/drugs/conditions, /recommendations
│   │   │   ├── health.py            # GET /api/health
│   │   │   └── models.py            # GET /api/models/info
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic Settings (.env configuration)
│   │   │   └── model_loader.py      # Singleton ModelRegistry
│   │   ├── services/
│   │   │   ├── llm_service.py       # Modular LLMProvider (Ollama, OpenAI, LocalMock)
│   │   │   ├── safety_service.py    # Clinical red-flag emergency detection
│   │   │   ├── conversation_service.py # In-memory session state manager
│   │   │   ├── question_service.py  # Intelligent follow-up question selector (Max 5 limit)
│   │   │   ├── rag_service.py       # RAG retriever coordinator
│   │   │   ├── disease_service.py   # Symptom model prediction
│   │   │   ├── patient_service.py   # Patient risk model prediction
│   │   │   └── drug_service.py      # Drug summary candidate ranking
│   │   └── schemas/                 # Pydantic models for chat, disease, and patient APIs
│   ├── models/
│   │   ├── disease_prediction_model/# Pre-trained symptom classifier
│   │   └── patient_ai_models/       # Pre-trained patient stratification models
│   ├── rag/
│   │   ├── documents/               # Medical reference JSON documents (WHO, CDC, NIH, MedlinePlus)
│   │   ├── vectorstore/             # FAISS index (index.faiss) & metadata (metadata.pkl)
│   │   ├── ingestion.py             # RAG document loader, chunker, & embedder
│   │   ├── retriever.py             # Persistent FAISS retriever
│   │   └── config.py                # Chunk size, overlap, & threshold settings
│   ├── prompts/
│   │   ├── symptom_extraction.txt   # Prompt for NL symptom extraction
│   │   ├── diagnostic_reasoning.txt # Prompt for structured diagnostic reasoning
│   │   └── question_generation.txt  # Prompt for follow-up question generation
│   ├── tests/                       # Pytest suite for models, RAG, chat, and safety
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/                   # ConversationalChat, Dashboard, Assessment, Results...
    │   ├── components/              # Sidebar, DisclaimerBanner, DrugTable...
    │   ├── services/api.js          # Centralized Axios API layer
    │   └── App.jsx                  # Main router with /chat navigation
    ├── package.json
    └── .env.example
```

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ / 20+

### Backend Setup

```powershell
cd patient-ai-system/backend

# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Copy .env configuration
copy .env.example .env

# Run RAG Ingestion (generates persistent FAISS vectorstore)
python -m rag.ingestion

# Start FastAPI server
uvicorn app.main:app --reload
```

Backend runs at: **http://localhost:8000**  
Swagger interactive docs: **http://localhost:8000/docs**

### Frontend Setup

```powershell
cd patient-ai-system/frontend

# Copy environment file
copy .env.example .env

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## LLM Configuration (Google Gemini)

The system is configured for cloud deployment using **Google Gemini** with an automatic deterministic local fallback for testing. Configured in `backend/.env`:

```env
# LLM Configuration (Google Gemini API for Deployment)
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Setting Up Google Gemini
1. Obtain an API key from [Google AI Studio](https://aistudio.google.com/).
2. Add your key to `backend/.env` under `GEMINI_API_KEY`.
3. Set `LLM_PROVIDER=gemini` and choose your model (e.g. `gemini-1.5-flash` or `gemini-1.5-pro`).

---

## RAG Knowledge Base & Rebuilding Vector Database

Medical reference documents are stored in `backend/rag/documents/` with metadata:
```json
{
  "title": "Pneumonia Diagnosis and Symptoms",
  "source": "MedlinePlus / NIH",
  "url": "https://medlineplus.gov/pneumonia.html",
  "disease": "Pneumonia",
  "section": "Clinical Presentation",
  "source_type": "medical_reference",
  "content": "Pneumonia is an infection that inflames the air sacs in lungs..."
}
```

### Rebuilding RAG Database
Whenever you add or update documents in `backend/rag/documents/`, execute:
```powershell
python -m rag.ingestion
```
This re-chunks documents, re-computes embeddings with `sentence-transformers`, and updates `index.faiss` and `metadata.pkl` in `backend/rag/vectorstore/`.

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/start` | Start a new conversational diagnostic chat session |
| POST | `/api/chat/message` | Send patient message, run ML + RAG + LLM, return follow-up or final assessment |
| GET | `/api/chat/{session_id}` | Retrieve current conversation state and history |
| GET | `/api/disease/symptoms` | List all 133 supported symptoms |
| POST | `/api/disease/predict` | Direct symptom ML model disease prediction |
| POST | `/api/patient/predict` | Direct patient risk stratification prediction |
| GET | `/api/drugs/recommendations` | Rank historical research drug candidates |

### Example Request (`POST /api/chat/message`)

```json
{
  "session_id": "7b8f9e61-3a21-4f12-9c3b-123456789abc",
  "message": "I have fever, cough, and body pain for 3 days."
}
```

### Example Follow-up Response

```json
{
  "type": "followup_question",
  "session_id": "7b8f9e61-3a21-4f12-9c3b-123456789abc",
  "message": "Have you experienced any shortness of breath or difficulty breathing?",
  "candidate_diseases": [
    {"disease": "Influenza", "probability": 0.62, "percentage": 62.0},
    {"disease": "Pneumonia", "probability": 0.21, "percentage": 21.0}
  ],
  "extracted_symptoms": ["High Fever", "Cough", "Muscle Pain"],
  "continue_chat": true
}
```

---

## Automated Test Suite

Run unit tests covering disease model predictions, RAG retrieval, chat loops, and emergency safety:

```powershell
cd patient-ai-system/backend
python -m pytest tests/
```

---

## Medical Safety Limitations & Terminology

- **Research Support Only**: This platform is a research prototype. It does NOT make clinical diagnoses or issue prescriptions.
- **Terminology Used**: *Most likely condition*, *Differential diagnosis*, *Candidate disease*, *Model confidence*, *Supporting evidence*, *Follow-up question*, *Clinical red flag*.
- **Emergency Interruption**: If severe warning symptoms (severe chest pain, acute shortness of breath, loss of consciousness, stroke signs, severe bleeding, self-harm) are reported, the standard diagnostic questioning halts immediately and an urgent emergency warning is returned.

