export default function LineChart({ data, title, xLabel = 'Time', yLabel = 'Value' }) {
  // Show empty state message if no data
  if (!data || data.length === 0) {
    return (
      <div className="bg-black/30 p-6 rounded-2xl border border-white/10">
        <h4 className="text-lg font-bold text-white mb-4">{title}</h4>
        <div className="h-64 flex items-center justify-center">
          <p className="text-slate-400 text-sm">No data available</p>
        </div>
      </div>
    )
  }

  const values = data.map(d => d.value || 0).filter(v => v != null && !isNaN(v))
  if (values.length === 0) return null

  const maxValue = Math.max(...values)
  const minValue = Math.min(...values)
  
  // For ping times, ensure we have a reasonable range even if all values are similar
  // Add padding to make the chart more readable
  const isPingChart = title?.toLowerCase().includes('ping')
  let adjustedMin = minValue
  let adjustedMax = maxValue
  
  if (isPingChart) {
    // For ping times, if range is too small, add padding
    const range = maxValue - minValue
    if (range < maxValue * 0.1 || range < 5) {
      // Add 20% padding on both sides, or at least 5ms
      const padding = Math.max(maxValue * 0.2, 5)
      adjustedMin = Math.max(0, minValue - padding)
      adjustedMax = maxValue + padding
    }
  } else {
    // For other charts, add 10% padding
    const range = maxValue - minValue
    const padding = range * 0.1 || maxValue * 0.1 || 1
    adjustedMin = Math.max(0, minValue - padding)
    adjustedMax = maxValue + padding
  }
  
  const range = adjustedMax - adjustedMin || 1

  // Generate y-axis labels
  const yAxisLabels = []
  const numLabels = 5
  for (let i = 0; i <= numLabels; i++) {
    const value = adjustedMin + (range * (i / numLabels))
    yAxisLabels.push(value)
  }

  return (
    <div className="bg-black/30 p-6 rounded-2xl border border-white/10">
      <h4 className="text-lg font-bold text-white mb-4">{title}</h4>
      <div className="h-64 relative">
        <svg className="w-full h-full" viewBox="0 0 450 250" preserveAspectRatio="none">
          <defs>
            <linearGradient id={`lineGradient-${title}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgba(59, 130, 246, 0.4)" />
              <stop offset="50%" stopColor="rgba(59, 130, 246, 0.2)" />
              <stop offset="100%" stopColor="rgba(59, 130, 246, 0)" />
            </linearGradient>
            <filter id={`glow-${title}`}>
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* Y-axis labels */}
          {yAxisLabels.map((value, i) => {
            const y = 250 - (i / numLabels) * 250
            return (
              <g key={i}>
                <line
                  x1="40"
                  y1={y}
                  x2="420"
                  y2={y}
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="1"
                />
                <text
                  x="35"
                  y={y + 4}
                  fill="rgba(255, 255, 255, 0.5)"
                  fontSize="10"
                  textAnchor="end"
                >
                  {isPingChart ? `${value.toFixed(1)}ms` : value.toFixed(1)}
                </text>
              </g>
            )
          })}
          
          {/* Area under curve */}
          {data.length > 0 && (
            <path
              d={`M 40,${250 - ((data[0]?.value || adjustedMin) - adjustedMin) / range * 250} ${data.map((d, i) => `L ${40 + (i / Math.max(1, data.length - 1)) * 380},${250 - ((d.value || adjustedMin) - adjustedMin) / range * 250}`).join(' ')} L ${40 + (data.length - 1) / Math.max(1, data.length - 1) * 380},250 L 40,250 Z`}
              fill={`url(#lineGradient-${title})`}
            />
          )}
          
          {/* Line */}
          {data.length > 1 && (
            <polyline
              points={data.map((d, i) => `${40 + (i / Math.max(1, data.length - 1)) * 380},${250 - ((d.value || adjustedMin) - adjustedMin) / range * 250}`).join(' ')}
              fill="none"
              stroke="rgb(59, 130, 246)"
              strokeWidth="2.5"
              filter={`url(#glow-${title})`}
            />
          )}
          
          {/* Data points */}
          {data.map((d, i) => {
            const x = 40 + (i / Math.max(1, data.length - 1)) * 380
            const y = 250 - ((d.value || adjustedMin) - adjustedMin) / range * 250
            return (
              <g key={i}>
                <circle
                  cx={x}
                  cy={y}
                  r="5"
                  fill="rgb(59, 130, 246)"
                  stroke="white"
                  strokeWidth="1.5"
                  className="hover:r-7 transition-all"
                />
                {/* Value label on hover */}
                <title>{d.time || d.label || `Point ${i + 1}`}: {d.value?.toFixed(2) || '0'}{isPingChart ? 'ms' : ''}</title>
              </g>
            )
          })}
          
          {/* X-axis labels */}
          {data.map((d, i) => {
            const x = 40 + (i / Math.max(1, data.length - 1)) * 380
            return (
              <text
                key={i}
                x={x}
                y={245}
                fill="rgba(255, 255, 255, 0.5)"
                fontSize="9"
                textAnchor="middle"
              >
                {d.time || d.label || `${i + 1}`}
              </text>
            )
          })}
        </svg>
      </div>
      <div className="flex justify-between items-center text-xs text-slate-400 mt-4">
        <span>{xLabel}</span>
        <div className="flex items-center gap-2">
          <span className="text-slate-500">Range:</span>
          <span className="font-semibold text-blue-400">{adjustedMin.toFixed(isPingChart ? 1 : 0)}{isPingChart ? 'ms' : ''} - {adjustedMax.toFixed(isPingChart ? 1 : 0)}{isPingChart ? 'ms' : ''}</span>
          {isPingChart && (
            <span className="text-slate-500 ml-2">
              (Avg: {(values.reduce((a, b) => a + b, 0) / values.length).toFixed(1)}ms)
            </span>
          )}
        </div>
      </div>
    </div>
  )
}




