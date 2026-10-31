import { useState, useMemo } from 'react'
import { ChevronUp, ChevronDown, Search } from 'lucide-react'
import { formatConditionName } from '../utils/formatters'

const SCORE_BAR_MAX = 1.0

function ScoreBar({ value, max = SCORE_BAR_MAX, color = 'bg-primary-500' }) {
  const pct = Math.min(100, (value / max) * 100)
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-slate-600 font-medium w-10 text-right">{value.toFixed(2)}</span>
    </div>
  )
}

function RatingBar({ value, max = 10 }) {
  const pct = (value / max) * 100
  const color = value >= 7.5 ? 'bg-green-500' : value >= 5 ? 'bg-amber-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-slate-600 font-medium w-10 text-right">{value.toFixed(1)}/10</span>
    </div>
  )
}

export default function DrugTable({ candidates = [], condition = '', loading = false }) {
  const [sortKey, setSortKey] = useState('average_candidate_score')
  const [sortDir, setSortDir] = useState('desc')
  const [search, setSearch] = useState('')
  const [topK, setTopK] = useState(10)

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  const filtered = useMemo(() => {
    let rows = [...candidates]
    if (search.trim()) {
      rows = rows.filter(r => r.drug_name.toLowerCase().includes(search.toLowerCase()))
    }
    rows.sort((a, b) => {
      const av = a[sortKey] ?? 0
      const bv = b[sortKey] ?? 0
      return sortDir === 'asc' ? av - bv : bv - av
    })
    return rows.slice(0, topK)
  }, [candidates, search, sortKey, sortDir, topK])

  const SortIcon = ({ col }) => {
    if (sortKey !== col) return <ChevronUp size={13} className="text-slate-300" />
    return sortDir === 'asc'
      ? <ChevronUp size={13} className="text-primary-500" />
      : <ChevronDown size={13} className="text-primary-500" />
  }

  const Th = ({ label, col, className = '' }) => (
    <th
      className={`px-4 py-3 text-left text-xs font-semibold text-slate-500 cursor-pointer select-none
                  hover:text-slate-800 transition-colors whitespace-nowrap ${className}`}
      onClick={() => handleSort(col)}
    >
      <span className="inline-flex items-center gap-1">
        {label} <SortIcon col={col} />
      </span>
    </th>
  )

  if (loading) {
    return (
      <div className="space-y-3">
        {[1,2,3,4,5].map(i => (
          <div key={i} className="h-14 bg-slate-100 rounded-xl animate-pulse" />
        ))}
      </div>
    )
  }

  if (!candidates.length) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p className="text-base font-medium">No historical candidates found</p>
        <p className="text-sm mt-1">Try selecting a different condition.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search drug name..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="form-input pl-9"
          />
        </div>
        <select
          value={topK}
          onChange={e => setTopK(Number(e.target.value))}
          className="form-select w-36"
        >
          <option value={5}>Top 5</option>
          <option value={10}>Top 10</option>
          <option value={20}>Top 20</option>
        </select>
      </div>

      {/* Research notice */}
      <div className="bg-blue-50 border border-blue-100 rounded-xl px-4 py-2.5 text-xs text-blue-700">
        <span className="font-semibold">Historical Research Candidates</span> — Rankings are based on historical
        review data and are <span className="font-semibold">NOT</span> prescriptions or clinical recommendations.
        A qualified healthcare professional must make all treatment decisions.
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-100">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-100">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 w-12">Rank</th>
              <Th label="Drug" col="drug_name" />
              <Th label="Rating" col="average_rating" className="w-36" />
              <Th label="Effectiveness" col="average_effectiveness" className="w-36" />
              <Th label="Side Effect Score" col="average_side_effect_score" className="w-36" />
              <Th label="Candidate Score" col="average_candidate_score" className="w-36" />
              <Th label="Reviews" col="review_count" className="w-24" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {filtered.map((drug, idx) => (
              <tr key={drug.drug_name} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold
                    ${idx === 0 ? 'bg-yellow-100 text-yellow-700' :
                      idx === 1 ? 'bg-slate-100 text-slate-600' :
                      idx === 2 ? 'bg-orange-100 text-orange-600' : 'bg-slate-50 text-slate-500'}`}>
                    {idx + 1}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="font-semibold text-slate-800 capitalize">{drug.drug_name}</span>
                </td>
                <td className="px-4 py-3 w-36">
                  <RatingBar value={drug.average_rating} />
                </td>
                <td className="px-4 py-3 w-36">
                  <ScoreBar value={drug.average_effectiveness} max={5} color="bg-teal-500" />
                </td>
                <td className="px-4 py-3 w-36">
                  <ScoreBar value={drug.average_side_effect_score} max={5} color="bg-amber-500" />
                </td>
                <td className="px-4 py-3 w-36">
                  <ScoreBar value={drug.average_candidate_score} max={1} color="bg-primary-500" />
                </td>
                <td className="px-4 py-3 text-center">
                  <span className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-lg font-medium">
                    {drug.review_count}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-slate-400 text-right">
        Showing {filtered.length} of {candidates.length} candidates for{' '}
        <span className="font-medium text-slate-600">{formatConditionName(condition)}</span>
      </p>
    </div>
  )
}
