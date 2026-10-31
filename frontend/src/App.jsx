import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import PatientAssessment from './pages/PatientAssessment'
import PredictionResult from './pages/PredictionResult'
import DrugCandidates from './pages/DrugCandidates'
import ModelInfo from './pages/ModelInfo'
import About from './pages/About'
import ConversationalChat from './pages/ConversationalChat'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-slate-50">
        {/* Sidebar */}
        <Sidebar />

        {/* Main content */}
        <main className="flex-1 min-w-0 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chat" element={<ConversationalChat />} />
            <Route path="/assessment" element={<PatientAssessment />} />
            <Route path="/results" element={<PredictionResult />} />
            <Route path="/drugs" element={<DrugCandidates />} />
            <Route path="/model" element={<ModelInfo />} />
            <Route path="/about" element={<About />} />
            {/* Catch-all */}
            <Route path="*" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

