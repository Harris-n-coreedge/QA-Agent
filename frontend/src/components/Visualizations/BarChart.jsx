export default function BarChart({ data, title, xLabel = 'Category', yLabel = 'Value' }) {
  if (!data || data.length === 0) return null

  const maxValue = Math.max(...data.map(d => d.value || 0))
  const barWidth = 100 / data.length

  return (
    <div className="bg-black/30 p-6 rounded-2xl border border-white/10">
      <h4 className="text-lg font-bold text-white mb-4">{title}</h4>
      <div className="h-64 flex items-end justify-between gap-2">
        {data.map((item, i) => {
          const height = maxValue > 0 ? (item.value / maxValue) * 100 : 0
          return (
            <div key={i} className="flex-1 flex flex-col items-center">
              <div className="w-full flex flex-col items-center justify-end" style={{ height: '200px' }}>
                <div
                  className="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-t transition-all hover:from-blue-400 hover:to-blue-300"
                  style={{ height: `${height}%`, minHeight: height > 0 ? '4px' : '0' }}
                  title={`${item.label}: ${item.value}`}
                />
              </div>
              <div className="mt-2 text-xs text-slate-400 text-center truncate w-full" title={item.label}>
                {item.label}
              </div>
            </div>
          )
        })}
      </div>
      <div className="text-xs text-slate-400 mt-4 text-center">{yLabel}</div>
    </div>
  )
}




