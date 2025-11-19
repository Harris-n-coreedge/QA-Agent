export default function MetricCard({ label, value, unit = '', color = 'slate' }) {
  // Safety check for null/undefined values
  if (value == null || value === undefined) {
    return null
  }
  
  const colorClasses = {
    slate: 'bg-slate-800/50 border-slate-700/50 text-white',
    teal: 'bg-teal-500/10 border-teal-500/20 text-teal-300',
    purple: 'bg-purple-500/10 border-purple-500/20 text-purple-300',
    emerald: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300',
    amber: 'bg-amber-500/10 border-amber-500/20 text-amber-300',
    rose: 'bg-rose-500/10 border-rose-500/20 text-rose-300',
    indigo: 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300',
  }

  // Format value safely
  let displayValue = value
  if (typeof value === 'number') {
    displayValue = isNaN(value) ? 'N/A' : value.toLocaleString()
  } else if (typeof value === 'boolean') {
    displayValue = value ? 'Yes' : 'No'
  } else if (typeof value === 'object') {
    displayValue = 'N/A' // Don't try to display objects
  } else {
    displayValue = String(value || 'N/A')
  }

  return (
    <div className={`p-6 rounded-2xl border ${colorClasses[color] || colorClasses.slate} shadow-xl`}>
      <p className="text-sm mb-2 font-bold tracking-wide uppercase opacity-70">{label || 'Unknown'}</p>
      <p className="text-2xl font-bold font-mono">
        {displayValue}
        {unit && <span className="text-lg ml-1">{unit}</span>}
      </p>
    </div>
  )
}




