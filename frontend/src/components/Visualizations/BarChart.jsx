export default function BarChart({ data, title, xLabel = 'Category', yLabel = 'Value' }) {
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

  // Check if data is just a "No Data" placeholder
  const isNoDataPlaceholder = data.length === 1 && data[0]?.label === "No Data" && data[0]?.value === 0
  
  // Check if this is a connection test chart (binary success/failure)
  // Check title and also check if data looks like connection test (HTTP/HTTPS labels with 0/1 values)
  const titleLower = title?.toLowerCase() || ''
  const hasConnectionKeywords = titleLower.includes('connection') || titleLower.includes('connectivity')
  const hasHttpLabels = data.some(d => 
    (d.label || '').toUpperCase().includes('HTTP') && 
    (d.value === 0 || d.value === 1 || d.value === true || d.value === false || d.success !== undefined)
  )
  const isConnectionTest = hasConnectionKeywords || hasHttpLabels
  
  // If it's a "No Data" placeholder and not a connection test, show empty state
  if (isNoDataPlaceholder && !isConnectionTest) {
    return (
      <div className="bg-black/30 p-6 rounded-2xl border border-white/10">
        <h4 className="text-lg font-bold text-white mb-4">{title}</h4>
        <div className="h-64 flex items-center justify-center">
          <p className="text-slate-400 text-sm">No data available</p>
        </div>
      </div>
    )
  }
  
  if (isConnectionTest) {
    // Render connection test results with success/failure indicators
    return (
      <div className="bg-black/30 p-6 rounded-2xl border border-white/10">
        <h4 className="text-lg font-bold text-white mb-6">{title}</h4>
        <div className="grid grid-cols-2 gap-6">
          {data.map((item, i) => {
            // Determine success status - check multiple possible formats
            const isSuccess = item.value === 1 || item.value === true || item.success === true || 
                            (typeof item.value === 'boolean' && item.value === true) ||
                            (typeof item.value === 'string' && item.value.toLowerCase() === 'true')
            
            const statusColor = isSuccess 
              ? 'from-emerald-500 to-emerald-400' 
              : 'from-red-500 to-red-400'
            const statusBg = isSuccess 
              ? 'bg-emerald-500/20 border-emerald-500/40' 
              : 'bg-red-500/20 border-red-500/40'
            const statusText = isSuccess ? 'SUCCESS' : 'FAILED'
            const statusIcon = isSuccess ? '✓' : '✗'
            const statusValue = isSuccess ? 'True' : 'False'
            
            return (
              <div 
                key={i} 
                className={`${statusBg} p-6 rounded-xl border-2 transition-all hover:scale-105 hover:shadow-lg`}
              >
                <div className="flex flex-col items-center justify-center space-y-3">
                  {/* Protocol Label */}
                  <div className="text-center">
                    <div className="text-white font-bold text-xl mb-2">{item.label}</div>
                  </div>
                  
                  {/* Status Value - Show True/False prominently */}
                  <div className={`text-3xl font-bold ${
                    isSuccess 
                      ? 'text-emerald-400' 
                      : 'text-red-400'
                  }`}>
                    {statusValue}
                  </div>
                  
                  {/* Status Icon */}
                  <div className={`w-14 h-14 rounded-full bg-gradient-to-br ${statusColor} flex items-center justify-center text-white text-xl font-bold shadow-lg`}>
                    {statusIcon}
                  </div>
                  
                  {/* Status Badge */}
                  <div className={`text-xs font-semibold px-3 py-1 rounded-full ${
                    isSuccess 
                      ? 'bg-emerald-500/30 text-emerald-300' 
                      : 'bg-red-500/30 text-red-300'
                  }`}>
                    {statusText}
                  </div>
                  
                  {/* Additional info if available */}
                  {item.details && (
                    <div className="text-xs text-slate-400 text-center mt-2">
                      {item.details}
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
        <div className="text-xs text-slate-400 mt-6 text-center">
          {data.filter(d => {
            const success = d.value === 1 || d.value === true || d.success === true || 
                          (typeof d.value === 'boolean' && d.value === true) ||
                          (typeof d.value === 'string' && d.value.toLowerCase() === 'true')
            return success
          }).length} of {data.length} tests passed
        </div>
      </div>
    )
  }

  // Regular bar chart for other data types
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
              {height > 0 && (
                <div className="text-xs text-blue-400 font-semibold mt-1">
                  {typeof item.value === 'number' ? item.value.toFixed(1) : item.value}
                </div>
              )}
            </div>
          )
        })}
      </div>
      <div className="text-xs text-slate-400 mt-4 text-center">{yLabel}</div>
    </div>
  )
}




