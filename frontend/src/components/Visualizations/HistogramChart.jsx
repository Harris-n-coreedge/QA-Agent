export default function HistogramChart({ data, title }) {
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

  const maxValue = Math.max(...data.map(d => d.value || 0))

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
                  className="w-full bg-gradient-to-t from-purple-500 to-purple-400 rounded-t transition-all hover:from-purple-400 hover:to-purple-300"
                  style={{ height: `${height}%`, minHeight: height > 0 ? '4px' : '0' }}
                  title={`${item.range}: ${item.value}`}
                />
              </div>
              <div className="mt-2 text-xs text-slate-400 text-center truncate w-full" title={item.range}>
                {item.range}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}




