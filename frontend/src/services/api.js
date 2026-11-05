/**
 * Centralized API service layer.
 * All backend communication goes through this module — no scattered axios calls.
 *
 * Base URL: VITE_API_BASE_URL environment variable (default: https://doctor-g-j7sp.onrender.com)
 */

import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://doctor-g-j7sp.onrender.com'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// Response interceptor — never expose raw errors to components
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      return Promise.reject({
        message: 'Unable to connect to AI backend. Please make sure the FastAPI server is running.',
        code: 'NETWORK_ERROR',
      })
    }
    const detail = error.response.data?.detail
    return Promise.reject({
      message: typeof detail === 'string' ? detail : 'An unexpected error occurred.',
      status: error.response.status,
      code: 'API_ERROR',
    })
  }
)

// ─── Health ───────────────────────────────────────────────────────────────────

export const getHealth = async () => {
  const { data } = await api.get('/api/health')
  return data
}

// ─── Model Info ───────────────────────────────────────────────────────────────

export const getModelInfo = async () => {
  const { data } = await api.get('/api/models/info')
  return data
}

// ─── Drugs ────────────────────────────────────────────────────────────────────

export const getConditions = async () => {
  const { data } = await api.get('/api/drugs/conditions')
  return data
}

export const getDrugCandidates = async (condition, topK = 5) => {
  const { data } = await api.get('/api/drugs/recommendations', {
    params: { condition, top_k: topK },
  })
  return data
}

// ─── Patient ──────────────────────────────────────────────────────────────────

export const predictPatient = async (patientData, condition = null) => {
  const { data } = await api.post('/api/patient/predict', {
    patient_data: patientData,
    condition,
  })
  return data
}

export const analyzePatient = async (patientData, condition, topK = 5) => {
  const { data } = await api.post('/api/analysis', {
    patient_data: patientData,
    condition,
    top_k: topK,
  })
  return data
}

// ─── Symptom Disease Prediction (disease_prediction_model.zip) ───────────────

export const getSymptoms = async () => {
  const { data } = await api.get('/api/disease/symptoms')
  return data
}

export const predictDisease = async (symptoms, topK = 5) => {
  const { data } = await api.post('/api/disease/predict', {
    symptoms,
    top_k: topK,
  })
  return data
}

// ─── Conversational Medical RAG + LLM Chat ───────────────────────────────────

export const startChat = async () => {
  const { data } = await api.post('/api/chat/start')
  return data
}

export const sendChatMessage = async (sessionId, message) => {
  const { data } = await api.post('/api/chat/message', {
    session_id: sessionId,
    message,
  })
  return data
}

export const getChatHistory = async (sessionId) => {
  const { data } = await api.get(`/api/chat/${sessionId}`)
  return data
}

export default api
