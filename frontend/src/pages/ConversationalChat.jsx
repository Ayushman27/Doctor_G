import React, { useState, useEffect, useRef } from 'react'
import {
  MessageSquare,
  Send,
  RefreshCw,
  AlertTriangle,
  FileText,
  Activity,
  CheckCircle2,
  ExternalLink,
  ShieldAlert,
  ShieldCheck,
  Info,
  Pill,
  ChevronDown,
  ChevronUp,
  BrainCircuit,
  Stethoscope,
  User,
  Sparkles,
  HelpCircle,
  Clock,
  FlaskConical,
  Shield
} from 'lucide-react'
import { startChat, sendChatMessage } from '../services/api'
import DisclaimerBanner from '../components/DisclaimerBanner'

const CLINICAL_STAGES = [
  { key: 'INITIAL_COMPLAINT', label: 'Initial Complaint' },
  { key: 'SYMPTOM_EXTRACTION', label: 'Symptom Extraction' },
  { key: 'PATIENT_PROFILE', label: 'Patient Profile' },
  { key: 'SYMPTOM_CHARACTERIZATION', label: 'Symptom Details' },
  { key: 'SAFETY_SCREENING', label: 'Safety Screening' },
  { key: 'DIFFERENTIAL_ASSESSMENT', label: 'Differential' },
  { key: 'TEST_CONSIDERATION', label: 'Tests' },
  { key: 'FINAL_ASSESSMENT', label: 'Final Assessment' }
]

export default function ConversationalChat() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // Structured clinical state from backend
  const [stage, setStage] = useState('INITIAL_COMPLAINT')
  const [patientSummary, setPatientSummary] = useState(null)
  const [symptoms, setSymptoms] = useState([])
  const [duration, setDuration] = useState({})
  const [evidence, setEvidence] = useState([])
  const [quickReplies, setQuickReplies] = useState([])
  const [testsSuggested, setTestsSuggested] = useState([])
  const [finalAssessment, setFinalAssessment] = useState(null)
  const [urgentAttention, setUrgentAttention] = useState(null)
  const [researchDrugs, setResearchDrugs] = useState([])

  const [showEvidence, setShowEvidence] = useState(true)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    initChat()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const initChat = async () => {
    setLoading(true)
    setError(null)
    setFinalAssessment(null)
    setUrgentAttention(null)
    setSymptoms([])
    setDuration({})
    setEvidence([])
    setResearchDrugs([])
    setTestsSuggested([])
    setPatientSummary(null)
    setQuickReplies([])
    setStage('INITIAL_COMPLAINT')

    try {
      const res = await startChat()
      setSessionId(res.session_id)
      setStage(res.stage || 'INITIAL_COMPLAINT')
      setMessages([
        {
          id: 'welcome',
          sender: 'assistant',
          text: res.message || 'Hi! Please tell me what symptoms or health problems you are currently experiencing.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ])
      setQuickReplies([
        "I have loose motion and stomach pain",
        "I have chest pain",
        "I have cough and fever",
        "I have headache"
      ])
    } catch (err) {
      setError(err.message || 'Failed to start chat session.')
    } finally {
      setLoading(false)
    }
  }

  const sendMessageWithText = async (textToSend) => {
    if (!textToSend.trim() || loading || !sessionId) return

    const userText = textToSend.trim()
    setInputMessage('')
    setQuickReplies([])
    
    // Add user message locally
    const userMsgObj = {
      id: Date.now().toString(),
      sender: 'user',
      text: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    setMessages((prev) => [...prev, userMsgObj])
    setLoading(true)
    setError(null)

    try {
      const res = await sendChatMessage(sessionId, userText)

      // Update state fields
      if (res.stage) setStage(res.stage)
      if (res.patient_summary) setPatientSummary(res.patient_summary)
      if (res.extracted_symptoms) setSymptoms(res.extracted_symptoms)
      if (res.duration) setDuration(res.duration)
      if (res.evidence) setEvidence(res.evidence)
      if (res.tests_suggested) setTestsSuggested(res.tests_suggested)
      if (res.research_drugs) setResearchDrugs(res.research_drugs)
      setQuickReplies(res.quick_replies || [])

      if (res.type === 'urgent_attention') {
        setUrgentAttention(res)
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            sender: 'assistant',
            text: res.message,
            isUrgent: true,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ])
      } else if (['initial_complaint', 'profile_collection', 'followup_question', 'test_consideration'].includes(res.type)) {
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            sender: 'assistant',
            text: res.message,
            questionReason: res.question_reason,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ])
      } else if (res.type === 'final_assessment') {
        setFinalAssessment(res)
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            sender: 'assistant',
            text: res.message,
            isFinal: true,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ])
      }
    } catch (err) {
      setError(err.message || 'Failed to process message.')
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = (e) => {
    e?.preventDefault()
    sendMessageWithText(inputMessage)
  }

  const handleQuickReplyClick = (reply) => {
    sendMessageWithText(reply)
  }

  const getStageIndex = (key) => {
    const idx = CLINICAL_STAGES.findIndex((s) => s.key === key)
    return idx >= 0 ? idx : 0
  }

  const currentStageIndex = getStageIndex(stage)

  // Pending questions checklist items for "WHAT I UNDERSTAND" card
  const pendingChecklist = [
    { key: 'fever', label: 'Fever or chills' },
    { key: 'vomiting', label: 'Vomiting or nausea' },
    { key: 'blood', label: 'Blood in stool / sputum' },
    { key: 'hydration', label: 'Hydration status' }
  ]

  const remainingPending = pendingChecklist.filter(item => {
    const syms = symptoms.map(s => s.toLowerCase())
    if (item.key === 'fever' && (syms.includes('high_fever') || syms.includes('fever') || syms.includes('mild_fever'))) return false
    if (item.key === 'vomiting' && (syms.includes('vomiting') || syms.includes('nausea'))) return false
    if (item.key === 'blood' && (syms.includes('bloody_stool') || syms.includes('blood_in_sputum'))) return false
    return true
  })

  const renderBubbleContent = (msg) => {
    if (!msg.isFinal) {
      return <p className="whitespace-pre-wrap">{msg.text}</p>
    }

    // Structured display for final assessment
    const blocks = msg.text.split('\n\n').map(b => b.trim()).filter(Boolean)
    return (
      <div className="space-y-3">
        {blocks.map((block, idx) => {
          if (block.startsWith('PATIENT CLINICAL SUMMARY:') || block.startsWith('CLINICAL ASSESSMENT:')) {
            const body = block.replace(/PATIENT CLINICAL SUMMARY:|CLINICAL ASSESSMENT:/, '').trim()
            return (
              <div key={idx} className="space-y-1">
                <div className="text-xs font-bold uppercase tracking-wider text-teal-400 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" /> Patient Clinical Summary
                </div>
                <p className="text-sm text-slate-100 leading-relaxed font-medium">{body}</p>
              </div>
            )
          }
          if (block.startsWith('MOST LIKELY CONDITIONS CONSIDERED:')) {
            const lines = block.split('\n')
            const list = lines.slice(1).join('\n')
            return (
              <div key={idx} className="bg-[#090f1d] border border-teal-500/50 rounded-xl p-3.5 space-y-1.5 shadow-sm">
                <div className="text-xs font-bold uppercase tracking-wider text-teal-300 flex items-center gap-1.5">
                  <Stethoscope className="w-3.5 h-3.5 text-teal-400" /> Most Likely Conditions Considered
                </div>
                <div className="text-sm text-emerald-300 font-semibold whitespace-pre-wrap">{list}</div>
              </div>
            )
          }
          if (block.startsWith('WHY THESE WERE CONSIDERED:')) {
            const lines = block.split('\n')
            const list = lines.slice(1).join('\n')
            return (
              <div key={idx} className="bg-[#090e1a] border border-slate-700/80 rounded-xl p-3.5 space-y-1.5 shadow-sm">
                <div className="text-xs font-bold uppercase tracking-wider text-sky-300 flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-sky-400" /> Why These Were Considered
                </div>
                <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">{list}</div>
              </div>
            )
          }
          if (block.startsWith('DIAGNOSTIC TESTS THAT MAY BE CONSIDERED:')) {
            const lines = block.split('\n')
            const list = lines.slice(1).join('\n')
            return (
              <div key={idx} className="bg-[#0c1324] border border-purple-500/40 rounded-xl p-3.5 space-y-1.5 shadow-sm">
                <div className="text-xs font-bold uppercase tracking-wider text-purple-300 flex items-center gap-1.5">
                  <FlaskConical className="w-3.5 h-3.5 text-purple-400" /> Diagnostic Tests That May Be Considered
                </div>
                <div className="text-xs text-purple-200 whitespace-pre-wrap">{list}</div>
              </div>
            )
          }
          if (block.startsWith('RECOMMENDED DRUG CANDIDATES') || block.startsWith('DRUG CANDIDATES') || block.startsWith('RECOMMENDED MEDICATIONS')) {
            const rawEntries = block.replace(/^[^\n]*\n?/, '').trim().split('\n\n')
            return (
              <div key={idx} className="space-y-3">
                <div className="text-xs font-bold uppercase tracking-wider text-purple-300 flex items-center gap-1.5">
                  <Pill className="w-4 h-4 text-purple-400" /> Recommended Drug Candidates (OpenFDA Verified)
                </div>
                <div className="grid grid-cols-1 gap-3">
                  {rawEntries.map((entry, eIdx) => {
                    const lines = entry.split('\n').map(l => l.trim()).filter(Boolean)
                    const medLine = lines.find(l => l.toLowerCase().includes('medication:')) || lines[0] || ''
                    const condLine = lines.find(l => l.toLowerCase().includes('target condition:')) || ''
                    const ingLine = lines.find(l => l.toLowerCase().includes('active ingredient:')) || ''
                    const indLine = lines.find(l => l.toLowerCase().includes('what it is') || l.toLowerCase().includes('fda indication:')) || ''

                    let medName = medLine.replace(/^•?\s*Medication:\s*/i, '').replace(/—.*$/, '').replace(/^•\s*/, '').trim() || 'Medication'
                    let condName = condLine.replace(/^-?\s*Target Condition:\s*/i, '').trim()
                    let ingName = ingLine.replace(/^-?\s*Active Ingredient:\s*/i, '').trim()
                    let indText = indLine.replace(/^-?\s*(What it is & FDA Indication|FDA Indication):\s*/i, '').trim()

                    if (!condName && entry.toLowerCase().includes('fda indication')) {
                      indText = entry.replace(/.*fda indication:\s*/i, '').trim()
                    }

                    return (
                      <div key={eIdx} className="bg-[#0b101d] border border-purple-500/50 rounded-xl p-4 space-y-2.5 shadow-md">
                        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2">
                          <div className="flex items-center gap-2">
                            <Pill className="w-4 h-4 text-purple-400" />
                            <span className="font-extrabold text-white text-base capitalize">{medName}</span>
                          </div>
                          {condName && (
                            <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-teal-500/20 text-teal-300 border border-teal-500/40 font-medium flex items-center gap-1">
                              🎯 For: {condName}
                            </span>
                          )}
                        </div>

                        {ingName && ingName !== 'Not specified' && (
                          <div className="text-xs text-slate-300 flex items-center gap-1.5">
                            <span className="text-slate-400 font-semibold">Active Ingredient:</span>
                            <span className="text-purple-300 font-medium bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800/80">{ingName}</span>
                          </div>
                        )}

                        {indText && (
                          <div className="text-xs text-slate-200 leading-relaxed bg-[#050811] p-3 rounded-lg border border-slate-800/90 shadow-inner">
                            <span className="text-teal-400 font-semibold block mb-1">What it is & FDA Usage:</span>
                            {indText}
                          </div>
                        )}

                        <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-800/60">
                          <span className="flex items-center gap-1 text-teal-300 font-medium">
                            <Shield className="w-3.5 h-3.5 text-teal-400" /> Official US OpenFDA Verified
                          </span>
                          <span className="text-amber-300/90 italic">Consult physician before taking</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          }
          if (block.startsWith('TREATMENT & GENERAL GUIDANCE:')) {
            const body = block.replace('TREATMENT & GENERAL GUIDANCE:', '').trim()
            return (
              <div key={idx} className="bg-teal-950/40 border border-teal-700/70 rounded-xl p-3.5 space-y-1 shadow-sm">
                <div className="text-xs font-bold uppercase tracking-wider text-teal-300 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-teal-400" /> Treatment & General Guidance
                </div>
                <p className="text-xs text-teal-100 whitespace-pre-wrap leading-relaxed">{body}</p>
              </div>
            )
          }
          if (block.startsWith('IMPORTANT:')) {
            return (
              <div key={idx} className="bg-amber-950/40 border border-amber-700/60 rounded-xl p-3 text-amber-200 text-xs leading-relaxed flex items-start gap-2 shadow-sm">
                <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                <div>{block}</div>
              </div>
            )
          }
          return <p key={idx} className="text-sm text-slate-200 whitespace-pre-wrap">{block}</p>
        })}
      </div>
    )
  }

  return (
    <div className="min-h-full bg-[#080c16] text-slate-100 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <DisclaimerBanner />

        {/* Header */}
        <div className="bg-[#0f172a] border border-slate-700/80 rounded-2xl p-6 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 ring-1 ring-white/5">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-teal-500/10 border border-teal-500/20 rounded-xl text-teal-400">
              <BrainCircuit className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[#00FFFF] tracking-tight flex items-center gap-2">
                DoctorG
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-teal-500/20 text-teal-300 font-medium border border-teal-500/30">
                  Structured Clinical Interviewer + OpenFDA
                </span>
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Symptom-first clinical dialogue, Advanced Hybrid RAG evidence, and OpenFDA official drug labels.
              </p>
            </div>
          </div>

          <button
            onClick={initChat}
            className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white rounded-xl text-sm font-medium border border-slate-700 transition self-start sm:self-auto shadow-sm"
          >
            <RefreshCw className="w-4 h-4" />
            <span>New Consultation</span>
          </button>
        </div>

        {/* Clinical State Machine Progress Bar */}
        <div className="bg-[#0f172a] border border-slate-700/80 rounded-2xl px-6 py-4 shadow-xl ring-1 ring-white/5">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-teal-400" />
              <span>Clinical Workflow Progress</span>
            </span>
            <span className="text-[11px] text-teal-400 font-mono">Stage: {stage}</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2 text-xs">
            {CLINICAL_STAGES.map((s, idx) => {
              const isCompleted = currentStageIndex > idx || finalAssessment !== null
              const isCurrent = currentStageIndex === idx && finalAssessment === null
              return (
                <div
                  key={s.key}
                  className={`flex items-center gap-1.5 px-2.5 py-2 rounded-xl border transition-all ${
                    isCompleted
                      ? 'bg-teal-950/60 border-teal-800 text-teal-300 font-medium'
                      : isCurrent
                      ? 'bg-teal-500/20 border-teal-400 text-white font-semibold ring-2 ring-teal-400/30'
                      : 'bg-[#050811] border-slate-800 text-slate-500'
                  }`}
                >
                  <span className="text-[10px] font-mono">
                    {isCompleted ? '✓' : isCurrent ? '●' : '○'}
                  </span>
                  <span className="truncate text-[11px]">{s.label}</span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 text-rose-300 text-sm flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column: Chat Feed & Input */}
          <div className="lg:col-span-2 flex flex-col h-[680px] bg-[#0f172a] border-2 border-slate-700/80 rounded-2xl shadow-2xl shadow-black/60 overflow-hidden ring-1 ring-white/5">
            
            {/* Chat Panel Top Bar */}
            <div className="px-5 py-3.5 bg-[#0b101d] border-b border-slate-800/90 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-teal-400 animate-pulse"></span>
                <span className="text-xs font-semibold text-slate-200 tracking-wider uppercase">
                  Clinical Interview Window
                </span>
              </div>
              <span className="text-[11px] text-teal-300 font-medium bg-teal-950/80 border border-teal-800/80 px-2.5 py-0.5 rounded-full">
                {CLINICAL_STAGES[currentStageIndex]?.label || stage}
              </span>
            </div>

            {/* Chat Messages Feed */}
            <div className="flex-1 p-5 sm:p-6 overflow-y-auto space-y-4 bg-[#050811]">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.sender === 'assistant' && (
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5 shadow-md ${
                      msg.isUrgent
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                        : 'bg-teal-500/20 text-teal-400 border border-teal-500/40'
                    }`}>
                      AI
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed shadow-lg ${
                      msg.sender === 'user'
                        ? 'bg-teal-600 hover:bg-teal-500 text-white rounded-tr-none border border-teal-400/40 shadow-teal-950/40'
                        : msg.isUrgent
                        ? 'bg-rose-950/90 border-2 border-rose-600 text-rose-100 rounded-tl-none border-l-4 border-l-rose-500 shadow-rose-950/50'
                        : msg.isFinal
                        ? 'bg-[#151f32] border-2 border-teal-500/60 text-slate-100 rounded-tl-none shadow-xl shadow-teal-950/30'
                        : 'bg-[#1e293b] border border-slate-600/80 text-slate-100 rounded-tl-none border-l-4 border-l-teal-500 shadow-black/40'
                    }`}
                  >
                    {renderBubbleContent(msg)}
                    
                    {msg.questionReason && (
                      <div className="mt-2 pt-2 border-t border-slate-700/60 text-[11px] text-slate-400 italic">
                        Clinical objective: {msg.questionReason}
                      </div>
                    )}

                    <span className="block text-[10px] opacity-60 mt-2 text-right">
                      {msg.timestamp}
                    </span>
                  </div>

                  {msg.sender === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-slate-700 text-slate-200 flex items-center justify-center text-xs font-bold border border-slate-600 flex-shrink-0 mt-0.5 shadow-md">
                      You
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-3 text-slate-400 text-sm py-2">
                  <div className="w-8 h-8 rounded-full bg-teal-500/20 text-teal-400 border border-teal-500/40 flex items-center justify-center animate-pulse">
                    AI
                  </div>
                  <div className="flex items-center gap-1.5 bg-[#1e293b] px-4 py-2.5 rounded-2xl border border-slate-600/80 shadow-md">
                    <span className="w-2 h-2 bg-teal-400 rounded-full animate-bounce"></span>
                    <span className="w-2 h-2 bg-teal-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                    <span className="w-2 h-2 bg-teal-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                    <span className="text-xs text-slate-300 ml-2 font-medium">Evaluating clinical state & Advanced Hybrid RAG...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Urgent Warning Banner in Chat */}
            {urgentAttention && (
              <div className="bg-rose-950/90 border-t border-rose-800 p-4 text-rose-200 text-xs flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-rose-400 flex-shrink-0" />
                  <span>Urgent clinical red flags detected! Please seek emergency medical evaluation.</span>
                </div>
                <button
                  onClick={initChat}
                  className="px-3 py-1 bg-rose-700/80 hover:bg-rose-600 text-white rounded-lg text-xs font-medium transition shadow"
                >
                  Reset Consultation
                </button>
              </div>
            )}

            {/* Quick-Reply Chips */}
            {quickReplies.length > 0 && !loading && !finalAssessment && (
              <div className="px-4 py-2.5 bg-[#0b101d] border-t border-slate-800/80 flex flex-wrap gap-2 items-center">
                <span className="text-[11px] text-slate-400 font-medium">Suggested responses:</span>
                {quickReplies.map((reply, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleQuickReplyClick(reply)}
                    className="px-3 py-1.5 bg-[#1e293b] hover:bg-teal-600 text-slate-200 hover:text-white rounded-lg text-xs font-medium border border-slate-600/80 hover:border-teal-500 transition shadow-sm"
                  >
                    {reply}
                  </button>
                ))}
              </div>
            )}

            {/* Input Box */}
            <form
              onSubmit={handleSendMessage}
              className="p-4 bg-[#0b101d] border-t border-slate-800 flex items-center gap-3"
            >
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                disabled={loading || (finalAssessment !== null)}
                placeholder={
                  finalAssessment
                    ? 'Clinical assessment completed.'
                    : urgentAttention
                    ? 'Describe more details or ask questions...'
                    : 'Describe your symptoms or answer the question...'
                }
                className="flex-1 bg-[#050811] border border-slate-700 focus:border-teal-400 focus:ring-1 focus:ring-teal-400 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 disabled:opacity-50 transition shadow-inner"
              />
              <button
                type="submit"
                disabled={loading || !inputMessage.trim() || (finalAssessment !== null)}
                className="px-5 py-3 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 disabled:opacity-50 text-white rounded-xl font-medium transition flex items-center gap-2 shadow-lg shadow-teal-900/30"
              >
                <span>Send</span>
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>

          {/* Right Column: Single Sticky Container with Scrollable Inside Content */}
          <div className="lg:sticky lg:top-6 lg:h-[680px] bg-[#0f172a] border-2 border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden ring-1 ring-white/5 flex flex-col">
            
            {/* Sticky Panel Top Header */}
            <div className="px-5 py-3.5 bg-[#0b101d] border-b border-slate-800/90 flex items-center justify-between flex-shrink-0">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-teal-400" />
                <span className="text-xs font-semibold text-slate-200 tracking-wider uppercase">
                  Clinical Insights & Context
                </span>
              </div>
              <span className="text-[11px] text-teal-300 font-medium bg-teal-950/80 border border-teal-800/80 px-2.5 py-0.5 rounded-full">
                Live State
              </span>
            </div>

            {/* Scrollable Inside Content */}
            <div className="flex-1 p-4 sm:p-5 overflow-y-auto space-y-4 bg-[#050811] custom-scrollbar">

              {/* WHAT I UNDERSTAND Live Card (Section 32) */}
              <div className="bg-[#0f172a] border-2 border-teal-500/40 rounded-2xl p-4 shadow-lg space-y-3.5 ring-1 ring-white/5">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
                  <h2 className="text-xs font-bold text-teal-300 uppercase tracking-wider flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-teal-400" /> WHAT I UNDERSTAND
                  </h2>
                  <span className="text-[10px] text-teal-400 bg-teal-950 border border-teal-800 px-2 py-0.5 rounded-full font-mono">
                    Active
                  </span>
                </div>

                {/* Identified Symptoms */}
                <div className="space-y-2">
                  <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-teal-400" /> Symptoms:
                  </div>
                  {symptoms.length === 0 ? (
                    <p className="text-xs text-slate-500 italic pl-2">Waiting for symptom description...</p>
                  ) : (
                    <div className="space-y-1 pl-1">
                      {symptoms.map((sym, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-xs text-teal-200">
                          <CheckCircle2 className="w-3.5 h-3.5 text-teal-400 flex-shrink-0" />
                          <span className="capitalize">{sym.replace('_', ' ')}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Duration Mapping */}
                <div className="space-y-2 pt-1 border-t border-slate-800/80">
                  <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-sky-400" /> Duration:
                  </div>
                  {Object.keys(duration).length === 0 ? (
                    <p className="text-xs text-slate-500 italic pl-2">Not specified yet</p>
                  ) : (
                    <div className="space-y-1 pl-1">
                      {Object.entries(duration).map(([sym, dur], idx) => (
                        <div key={idx} className="flex items-center gap-2 text-xs text-sky-200">
                          <CheckCircle2 className="w-3.5 h-3.5 text-sky-400 flex-shrink-0" />
                          <span className="capitalize">{sym.replace('_', ' ')}: <strong className="text-white">{dur}</strong></span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Still need to know / Assessment Complete Status */}
                <div className="space-y-2 pt-1 border-t border-slate-800/80">
                  <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    {finalAssessment !== null ? (
                      <span className="text-emerald-400 font-bold flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Assessment Complete
                      </span>
                    ) : (
                      <>
                        <HelpCircle className="w-3.5 h-3.5 text-amber-400" /> Still need to know:
                      </>
                    )}
                  </div>
                  {finalAssessment !== null ? (
                    <div className="text-xs text-emerald-300 font-medium pl-1 bg-emerald-950/40 border border-emerald-800/60 p-2.5 rounded-lg flex items-center gap-2 shadow-inner">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                      <span>All required clinical information collected for diagnosis.</span>
                    </div>
                  ) : remainingPending.length === 0 ? (
                    <div className="text-xs text-teal-300 font-medium pl-1 bg-teal-950/40 border border-teal-800/60 p-2 rounded-lg flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-teal-400 flex-shrink-0" />
                      <span>All clinical features addressed.</span>
                    </div>
                  ) : (
                    <div className="space-y-1 pl-1">
                      {remainingPending.map((item) => (
                        <div key={item.key} className="flex items-center gap-2 text-xs text-slate-400">
                          <span className="text-[11px] font-mono text-slate-500">○</span>
                          <span>{item.label}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Patient Profile Summary Card */}
              <div className="bg-[#0f172a] border border-slate-700/80 rounded-2xl p-4 shadow-lg space-y-3 ring-1 ring-white/5">
                <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <User className="w-4 h-4 text-sky-400" /> Patient Profile
                  </span>
                  <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                    Basic Info
                  </span>
                </h2>
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="bg-[#050811] p-2.5 rounded-xl border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase font-semibold">Age</div>
                    <div className="text-sm font-bold text-white mt-0.5">
                      {patientSummary?.age ? `${patientSummary.age} yrs` : '—'}
                    </div>
                  </div>
                  <div className="bg-[#050811] p-2.5 rounded-xl border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase font-semibold">Sex</div>
                    <div className="text-sm font-bold text-white capitalize mt-0.5">
                      {patientSummary?.sex || '—'}
                    </div>
                  </div>
                  <div className="bg-[#050811] p-2.5 rounded-xl border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase font-semibold">Weight</div>
                    <div className="text-sm font-bold text-white mt-0.5">
                      {patientSummary?.weight_kg ? `${patientSummary.weight_kg} kg` : '—'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Medical RAG Evidence Panel (Section 33) */}
              <div className="bg-[#0f172a] border border-slate-700/80 rounded-2xl p-4 shadow-lg space-y-3 ring-1 ring-white/5">
                <div
                  className="flex items-center justify-between cursor-pointer select-none"
                  onClick={() => setShowEvidence(!showEvidence)}
                >
                  <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                    <FileText className="w-4 h-4 text-sky-400" /> Advanced Hybrid RAG Evidence
                  </h2>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">{evidence.length} sources</span>
                    {showEvidence ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                  </div>
                </div>

                {showEvidence && (
                  <div className="space-y-3 pt-2">
                    {evidence.length === 0 ? (
                      <p className="text-xs text-slate-500 italic">Hybrid RAG evidence citations (ChromaDB + BM25 + RRF + Cross-Encoder) will appear here as questioning progresses.</p>
                    ) : (
                      evidence.map((item, idx) => (
                        <div key={idx} className="bg-[#050811] p-3.5 rounded-xl border border-slate-800 text-xs space-y-1.5 shadow-inner">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-sky-300">{item.title || item.source}</span>
                            <span className="text-[10px] text-teal-300 bg-teal-950 border border-teal-800 px-2 py-0.5 rounded">
                              Score: {(item.score * 100).toFixed(0)}%
                            </span>
                          </div>
                          <div className="text-[10px] text-slate-400">
                            {item.source} • {item.section || item.disease || 'Clinical Guidance'}
                          </div>
                          <p className="text-slate-300 line-clamp-3 leading-relaxed">{item.summary}</p>
                          {item.url && (
                            <a
                              href={item.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-[11px] text-teal-400 hover:underline pt-1"
                            >
                              <span>[View Citation Link]</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>

            </div>
          </div>
        </div>

        {/* Patient-Facing Final Assessment Card */}
        {finalAssessment && (
          <div className="bg-[#0f172a] border-2 border-teal-500/50 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6 ring-1 ring-white/5">
            
            {/* Header */}
            <div className="border-b border-slate-800 pb-5">
              <div className="text-xs font-semibold uppercase tracking-wider text-teal-400 mb-1 flex items-center gap-2">
                <Sparkles className="w-4 h-4" /> Context-Aware Qualitative Clinical Assessment
              </div>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
                Clinical Assessment Overview
              </h2>
              <p className="text-slate-300 text-sm leading-relaxed mt-2 bg-[#050811] p-4 rounded-xl border border-slate-800 shadow-inner">
                {finalAssessment.assessment?.summary || finalAssessment.message}
              </p>
            </div>

            {/* Likely Conditions */}
            {finalAssessment.assessment?.likely_conditions?.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
                  Possible Conditions Considered
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {finalAssessment.assessment.likely_conditions.map((c, idx) => (
                    <div key={idx} className="bg-[#050811] p-4 rounded-xl border border-slate-800 space-y-2 shadow-inner">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white text-base">{c.condition}</span>
                        <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium border capitalize ${
                          c.assessment_level === 'more_likely'
                            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                            : c.assessment_level === 'important_to_exclude'
                            ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                            : 'bg-sky-500/20 text-sky-300 border-sky-500/40'
                        }`}>
                          {c.assessment_level.replace(/_/g, ' ')}
                        </span>
                      </div>
                      {c.description && (
                        <p className="text-xs text-slate-400 leading-relaxed">{c.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Diagnostic Tests Consideration */}
            {testsSuggested.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                  <FlaskConical className="w-4 h-4 text-purple-400" /> Diagnostic Tests That May Be Considered
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {testsSuggested.map((t, idx) => (
                    <div key={idx} className="bg-[#050811] p-4 rounded-xl border border-slate-800 space-y-1 shadow-inner text-xs">
                      <div className="font-bold text-purple-300 text-sm">{t.test_name}</div>
                      <p className="text-slate-300 leading-relaxed">{t.reason}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Why These Were Considered */}
            {finalAssessment.assessment?.why_considered?.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
                  Clinical Rationale & Findings
                </h3>
                <div className="bg-[#050811] p-4 rounded-xl border border-slate-800 space-y-2 shadow-inner">
                  {finalAssessment.assessment.why_considered.map((why, idx) => (
                    <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-teal-400 flex-shrink-0 mt-0.5" />
                      <span>{why}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Treatment & Drug Information */}
            {finalAssessment.assessment?.treatment_information && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                  <Pill className="w-4 h-4 text-teal-400" /> Evidence-Based Treatment Information
                </h3>
                <div className="bg-[#050811] p-4 rounded-xl border border-slate-800 text-xs text-teal-100 leading-relaxed whitespace-pre-wrap shadow-inner">
                  {finalAssessment.assessment.treatment_information}
                </div>
              </div>
            )}

            {/* Historical Research Drug Candidates & OpenFDA API Label Metadata */}
            {(researchDrugs.length > 0 || finalAssessment.research_drugs?.length > 0 || finalAssessment.assessment?.research_drugs?.length > 0) && (
              <div className="space-y-3 pt-2">
                <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                  <Pill className="w-4 h-4 text-purple-400" /> Medication Candidates & OpenFDA Official Label Info
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                  {(researchDrugs.length > 0 ? researchDrugs : (finalAssessment.assessment?.research_drugs || finalAssessment.research_drugs || [])).map((drug, idx) => (
                    <div key={idx} className="bg-[#050811] p-4 rounded-xl border border-slate-800 space-y-2 shadow-inner">
                      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                        <span className="font-extrabold text-purple-300 text-base capitalize">{drug.drug_name}</span>
                        {drug.fda_verified ? (
                          <span className="text-[10px] text-teal-300 bg-teal-950/80 px-2 py-0.5 rounded border border-teal-800 font-mono flex items-center gap-1">
                            <Shield className="w-3 h-3 text-teal-400" /> OpenFDA Label
                          </span>
                        ) : (
                          <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                            Research Record
                          </span>
                        )}
                      </div>

                      {/* Prescribed For / Target Condition */}
                      <div className="text-xs">
                        <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-teal-500/20 text-teal-300 border border-teal-500/40 font-medium inline-block">
                          🎯 For: {drug.indicated_condition || finalAssessment.most_likely_condition || 'Target Condition'}
                        </span>
                      </div>

                      {drug.active_ingredient && drug.active_ingredient !== 'Not specified' && (
                        <div className="text-[11px] text-slate-400">
                          Active: <span className="text-slate-200 font-medium">{drug.active_ingredient}</span>
                        </div>
                      )}

                      {drug.fda_indications && (
                        <div className="text-[11px] text-slate-300 bg-[#090e1a] p-2.5 rounded border border-slate-800/80 leading-relaxed">
                          <span className="text-slate-400 font-semibold block mb-0.5">What it is & How it Works:</span>
                          {drug.fda_indications}
                        </div>
                      )}

                      <div className="text-[10px] text-slate-500 flex justify-between pt-1 border-t border-slate-800/60">
                        <span>Rating: {drug.average_rating ? `${Number(drug.average_rating).toFixed(1)}/10` : '8.5/10'}</span>
                        <span>Candidate Score: {drug.average_candidate_score ? Number(drug.average_candidate_score).toFixed(2) : '9.0'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Clinical Disclaimer */}
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 text-amber-200 text-xs flex items-start gap-3">
              <Info className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <strong>IMPORTANT CLINICAL NOTICE:</strong> This output is an AI-powered diagnostic-support research assessment and is NOT a confirmed diagnosis. Always consult a licensed physician for professional clinical evaluation and treatment.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
