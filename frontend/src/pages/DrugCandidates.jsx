import { useState, useEffect } from 'react'
import { Pill, Search } from 'lucide-react'
import { getConditions, getDrugCandidates } from '../services/api'
import DrugTable from '../components/DrugTable'
import DisclaimerBanner from '../components/DisclaimerBanner'
import { formatConditionName } from '../utils/formatters'

export default function DrugCandidates() {
  const [conditions, setConditions] = useState([])
  const [selected, setSelected] = useState('')
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(false)
  const [condLoading, setCondLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')

  useEffect(() => {
    getConditions()
      .then(d => setConditions(d.conditions))
      .catch(err => setError(err.message))
      .finally(() => setCondLoading(false))
  }, [])

  const handleSelect = async (condition) => {
    setSelected(condition)
    setLoading(true)
    setError(null)
    setCandidates([])
    try {
      const data = await getDrugCandidates(condition, 20)
      setCandidates(data.candidates)
    } catch (err) {
      setError(err.message || 'Failed to load drug candidates.')
    } finally {
      setLoading(false)
    }
  }

  const filtered = conditions.filter(c =>
    c.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="p-6 lg:p-8 max-w-5xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <Pill size={22} className="text-teal-600" />
          <h1 className="text-2xl font-bold text-slate-800">Drug Candidate Analysis</h1>
        </div>
        <p className="text-sm text-slate-500">
          Browse historical drug candidate rankings by medical condition.
          Select a condition to view ranked drug data.
        </p>
      </div>

      <DisclaimerBanner />
      <div className="mt-6" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Condition sidebar */}
        <div className="card h-fit">
          <h2 className="text-sm font-semibold text-slate-800 mb-3">Select Condition</h2>
          <div className="relative mb-3">
            <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter conditions..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="form-input pl-8 py-2 text-xs"
            />
          </div>
          {condLoading ? (
            <div className="space-y-1.5">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-7 bg-slate-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="space-y-0.5 max-h-96 overflow-y-auto pr-1">
              {filtered.map(cond => (
                <button
                  key={cond}
                  onClick={() => handleSelect(cond)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors duration-100
                    ${selected === cond
                      ? 'bg-teal-50 text-teal-700 font-semibold'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800'
                    }`}
                >
                  {formatConditionName(cond)}
                </button>
              ))}
              {filtered.length === 0 && (
                <p className="text-xs text-slate-400 text-center py-4">No conditions found</p>
              )}
            </div>
          )}
          <div className="mt-3 pt-3 border-t border-slate-100 text-xs text-slate-400">
            {conditions.length} conditions available
          </div>
        </div>

        {/* Drug table */}
        <div className="lg:col-span-2">
          {!selected && !loading && (
            <div className="card flex flex-col items-center justify-center py-20 text-slate-400">
              <Pill size={40} className="opacity-20 mb-3" />
              <p className="text-base font-medium">Select a condition</p>
              <p className="text-sm mt-1">Choose from the list to view drug candidates</p>
            </div>
          )}
          {selected && (
            <div className="card">
              <div className="flex items-center gap-2 mb-5">
                <div>
                  <h2 className="text-base font-semibold text-slate-800">
                    {formatConditionName(selected)}
                  </h2>
                  <p className="text-xs text-slate-400">Historical research drug candidates</p>
                </div>
              </div>
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-700 mb-4">
                  {error}
                </div>
              )}
              <DrugTable candidates={candidates} condition={selected} loading={loading} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
