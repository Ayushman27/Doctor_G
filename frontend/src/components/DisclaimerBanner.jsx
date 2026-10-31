import { AlertTriangle } from 'lucide-react'

export default function DisclaimerBanner() {
  return (
    <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 flex items-start gap-3">
      <AlertTriangle size={16} className="text-amber-600 mt-0.5 flex-shrink-0" />
      <p className="text-xs text-amber-800 leading-relaxed">
        <span className="font-semibold">Research & Educational Prototype Only.</span>{' '}
        This system provides decision-support information based on historical data.
        It does not diagnose disease, prescribe medication, or replace professional medical judgment.
        All drug candidate rankings are derived from historical review data and are NOT prescriptions.
        A qualified healthcare professional must make all treatment decisions.
      </p>
    </div>
  )
}
