export default function LineChart({ data, title, xLabel = 'Time', yLabel = 'Value' }) {
  if (!data || data.length === 0) return null

  const maxValue = Math.max(...data.map(d => d.value || 0))
  const minValue = Math.min(...data.map(d => d.value || 0))
  const range = maxValue - minValue || 1

  return (
    <div className="bg-black/30 p-6 rounded-2xl border border-white/10">
      <h4 className="text-lg font-bold text-white mb-4">{title}</h4>
      <div className="h-64 relative">
        <svg className="w-full h-full" viewBox="0 0 400 200" preserveAspectRatio="none">
          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgba(59, 130, 246, 0.5)" />
              <stop offset="100%" stopColor="rgba(59, 130, 246, 0)" />
            </linearGradient>
          </defs>
          
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
            <line
              key={ratio}
              x1="0"
              y1={200 * ratio}
              x2="400"
              y2={200 * ratio}
              stroke="rgba(255, 255, 255, 0.1)"
              strokeWidth="1"
            />
          ))}
          
          {/* Area under curve */}
          <path
            d={`M 0,${200 - ((data[0]?.value || 0) - minValue) / range * 200} ${data.map((d, i) => `L ${(i / (data.length - 1)) * 400},${200 - ((d.value || 0) - minValue) / range * 200}`).join(' ')} L 400,200 L 0,200 Z`}
            fill="url(#lineGradient)"
          />
          
          {/* Line */}
          <polyline
            points={data.map((d, i) => `${(i / (data.length - 1)) * 400},${200 - ((d.value || 0) - minValue) / range * 200}`).join(' ')}
            fill="none"
            stroke="rgb(59, 130, 246)"
            strokeWidth="2"
          />
          
          {/* Data points */}
          {data.map((d, i) => (
            <circle
              key={i}
              cx={(i / (data.length - 1)) * 400}
              cy={200 - ((d.value || 0) - minValue) / range * 200}
              r="3"
              fill="rgb(59, 130, 246)"
            />
          ))}
        </svg>
      </div>
      <div className="flex justify-between text-xs text-slate-400 mt-2">
        <span>{xLabel}</span>
        <span>{yLabel}: {minValue.toFixed(0)} - {maxValue.toFixed(0)}</span>
      </div>
    </div>
  )
}




