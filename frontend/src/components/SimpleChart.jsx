import { useMemo } from 'react'

export function SimpleBarChart({ data, colors = ['#64748b', '#475569', '#334155'] }) {
  const maxValue = Math.max(...data.map(d => d.value), 1)
  const chartHeight = 200
  const barWidth = 100 / data.length

  return (
    <svg viewBox="0 0 400 200" className="w-full h-full" preserveAspectRatio="none">
      {data.map((item, index) => {
        const barHeight = (item.value / maxValue) * chartHeight
        const x = (index * 400) / data.length
        const y = chartHeight - barHeight
        const color = colors[index % colors.length]

        return (
          <g key={index}>
            <defs>
              <linearGradient id={`gradient-${index}`} x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor={color} stopOpacity="0.8" />
                <stop offset="100%" stopColor={color} stopOpacity="0.4" />
              </linearGradient>
            </defs>
            <rect
              x={x + 10}
              y={y}
              width={(400 / data.length) - 20}
              height={barHeight}
              fill={`url(#gradient-${index})`}
              rx="4"
              className="transition-all duration-500 hover:opacity-80"
              style={{ transformOrigin: 'bottom' }}
            >
              <animate
                attributeName="height"
                from="0"
                to={barHeight}
                dur="0.8s"
                fill="freeze"
              />
              <animate
                attributeName="y"
                from={chartHeight}
                to={y}
                dur="0.8s"
                fill="freeze"
              />
            </rect>
            <text
              x={x + 400 / data.length / 2}
              y={chartHeight + 15}
              fill="#94a3b8"
              fontSize="12"
              textAnchor="middle"
              className="font-medium"
            >
              {item.label}
            </text>
            <text
              x={x + 400 / data.length / 2}
              y={y - 5}
              fill="#e2e8f0"
              fontSize="11"
              textAnchor="middle"
              className="font-semibold"
            >
              {item.value}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

export function SimpleLineChart({ data, color = '#64748b' }) {
  const maxValue = Math.max(...data.map(d => d.value), 1)
  const chartHeight = 200
  const chartWidth = 400
  const pointSpacing = chartWidth / (data.length - 1)

  const pathData = data.map((item, index) => {
    const x = index * pointSpacing
    const y = chartHeight - (item.value / maxValue) * chartHeight
    return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')

  const areaPath = `${pathData} L ${chartWidth} ${chartHeight} L 0 ${chartHeight} Z`

  return (
    <svg viewBox="0 0 400 200" className="w-full h-full" preserveAspectRatio="none">
      <defs>
        <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0.05" />
        </linearGradient>
        <linearGradient id="lineStroke" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={color} stopOpacity="0.8" />
          <stop offset="100%" stopColor={color} stopOpacity="1" />
        </linearGradient>
      </defs>
      
      {/* Area fill */}
      <path
        d={areaPath}
        fill="url(#lineGradient)"
        className="transition-all duration-1000"
      >
        <animate
          attributeName="opacity"
          from="0"
          to="1"
          dur="1s"
          fill="freeze"
        />
      </path>

      {/* Line */}
      <path
        d={pathData}
        fill="none"
        stroke="url(#lineStroke)"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="transition-all duration-1000"
      >
        <animate
          attributeName="stroke-dasharray"
          from={`0 ${pathData.length}`}
          to={`${pathData.length} 0`}
          dur="1.5s"
          fill="freeze"
        />
      </path>

      {/* Points */}
      {data.map((item, index) => {
        const x = index * pointSpacing
        const y = chartHeight - (item.value / maxValue) * chartHeight

        return (
          <g key={index}>
            <circle
              cx={x}
              cy={y}
              r="4"
              fill={color}
              className="transition-all duration-500"
            >
              <animate
                attributeName="r"
                from="0"
                to="4"
                dur="0.5s"
                begin={`${index * 0.1}s`}
                fill="freeze"
              />
            </circle>
            <circle
              cx={x}
              cy={y}
              r="8"
              fill={color}
              opacity="0.2"
              className="transition-all duration-500"
            >
              <animate
                attributeName="r"
                from="0"
                to="8"
                dur="0.8s"
                begin={`${index * 0.1}s`}
                fill="freeze"
              />
            </circle>
          </g>
        )
      })}
    </svg>
  )
}

export function SimplePieChart({ data, size = 200 }) {
  const total = data.reduce((sum, item) => sum + item.value, 0)
  const radius = size / 2 - 10
  const centerX = size / 2
  const centerY = size / 2

  let currentAngle = -90

  const paths = data.map((item, index) => {
    const percentage = (item.value / total) * 100
    const angle = (item.value / total) * 360
    const startAngle = currentAngle
    const endAngle = currentAngle + angle
    currentAngle += angle

    const startAngleRad = (startAngle * Math.PI) / 180
    const endAngleRad = (endAngle * Math.PI) / 180

    const x1 = centerX + radius * Math.cos(startAngleRad)
    const y1 = centerY + radius * Math.sin(startAngleRad)
    const x2 = centerX + radius * Math.cos(endAngleRad)
    const y2 = centerY + radius * Math.sin(endAngleRad)

    const largeArcFlag = angle > 180 ? 1 : 0

    const pathData = [
      `M ${centerX} ${centerY}`,
      `L ${x1} ${y1}`,
      `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
      'Z'
    ].join(' ')

    return {
      path: pathData,
      color: item.color,
      label: item.label,
      value: item.value,
      percentage,
      index
    }
  })

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg viewBox={`0 0 ${size} ${size}`} className="w-full h-full">
        {paths.map(({ path, color, label, value, percentage, index }) => (
          <g key={index}>
            <defs>
              <linearGradient id={`pieGradient-${index}`} x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor={color} stopOpacity="0.9" />
                <stop offset="100%" stopColor={color} stopOpacity="0.6" />
              </linearGradient>
            </defs>
            <path
              d={path}
              fill={`url(#pieGradient-${index})`}
              stroke="rgba(15, 23, 42, 0.8)"
              strokeWidth="2"
              className="transition-all duration-500 hover:opacity-80 cursor-pointer"
            >
              <animateTransform
                attributeName="transform"
                type="rotate"
                from={`-90 ${centerX} ${centerY}`}
                to={`-90 ${centerX} ${centerY}`}
                dur="1s"
                begin={`${index * 0.1}s`}
              />
            </path>
          </g>
        ))}
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl font-bold text-white">{total}</div>
          <div className="text-xs text-slate-400">Total</div>
        </div>
      </div>
      <div className="absolute -bottom-6 left-0 right-0 flex flex-wrap justify-center gap-3">
        {paths.map(({ label, color, percentage }, index) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-xs text-slate-400">{label}</span>
            <span className="text-xs font-semibold text-white">{percentage.toFixed(0)}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

