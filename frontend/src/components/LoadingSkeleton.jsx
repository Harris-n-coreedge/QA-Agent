import React from 'react'

/**
 * Versatile loading skeleton component
 * @param {object} props
 * @param {string} props.variant - Type of skeleton (text, circle, rectangle, card, stat, button)
 * @param {number} props.count - Number of skeleton elements to render
 * @param {string} props.className - Additional CSS classes
 * @param {number} props.width - Width in pixels or percentage
 * @param {number} props.height - Height in pixels
 */
export function LoadingSkeleton({
  variant = 'rectangle',
  count = 1,
  className = '',
  width,
  height,
  ...props
}) {
  const baseClasses = 'skeleton-wave rounded-lg'

  const variantClasses = {
    text: 'h-4 w-full',
    circle: 'rounded-full',
    rectangle: 'w-full',
    card: 'w-full h-48',
    stat: 'w-full h-24',
    button: 'h-10 w-32',
  }

  const skeletonClass = `${baseClasses} ${variantClasses[variant] || variantClasses.rectangle} ${className}`

  const style = {
    width: width ? (typeof width === 'number' ? `${width}px` : width) : undefined,
    height: height ? `${height}px` : undefined,
    ...props.style,
  }

  const skeletons = Array.from({ length: count }, (_, index) => (
    <div
      key={index}
      className={skeletonClass}
      style={style}
      aria-busy="true"
      aria-live="polite"
      {...props}
    />
  ))

  return count === 1 ? skeletons[0] : <div className="space-y-3">{skeletons}</div>
}

/**
 * Skeleton for dashboard stat cards
 */
export function StatCardSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5">
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className="card-stat" style={{ animationDelay: `${index * 100}ms` }}>
          <div className="flex items-start justify-between mb-3">
            <LoadingSkeleton variant="circle" width={40} height={40} />
            <LoadingSkeleton width={50} height={20} />
          </div>
          <LoadingSkeleton variant="text" width="60%" className="mb-2" />
          <LoadingSkeleton width={80} height={32} />
        </div>
      ))}
    </div>
  )
}

/**
 * Skeleton for test result cards
 */
export function TestResultCardSkeleton({ count = 3 }) {
  return (
    <div className="space-y-6">
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className="card p-6" style={{ animationDelay: `${index * 100}ms` }}>
          <div className="flex items-start gap-4 mb-4">
            <LoadingSkeleton variant="circle" width={24} height={24} />
            <div className="flex-1 space-y-3">
              <div className="flex items-center justify-between">
                <LoadingSkeleton width="60%" height={28} />
                <LoadingSkeleton width={100} height={28} />
              </div>
              <LoadingSkeleton variant="text" count={2} />
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 4 }, (_, i) => (
              <div key={i} className="p-4 rounded-lg bg-[#1a1a1a] border border-gray-800">
                <LoadingSkeleton variant="text" className="mb-2" width="50%" />
                <LoadingSkeleton height={24} />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

/**
 * Skeleton for chart components
 */
export function ChartSkeleton({ height = 250 }) {
  return (
    <div className="card p-6">
      <div className="mb-6">
        <LoadingSkeleton width="40%" height={24} className="mb-2" />
        <LoadingSkeleton width="60%" height={16} />
      </div>
      <LoadingSkeleton height={height} />
    </div>
  )
}

/**
 * Skeleton for table rows
 */
export function TableRowSkeleton({ columns = 5, rows = 5 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }, (_, rowIndex) => (
        <div
          key={rowIndex}
          className="grid gap-4"
          style={{
            gridTemplateColumns: `repeat(${columns}, 1fr)`,
            animationDelay: `${rowIndex * 50}ms`,
          }}
        >
          {Array.from({ length: columns }, (_, colIndex) => (
            <LoadingSkeleton key={colIndex} height={40} />
          ))}
        </div>
      ))}
    </div>
  )
}

/**
 * Skeleton for list items
 */
export function ListItemSkeleton({ count = 5 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }, (_, index) => (
        <div
          key={index}
          className="flex items-center gap-4 p-4 rounded-lg bg-[#1a1a1a] border border-gray-800"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <LoadingSkeleton variant="circle" width={48} height={48} />
          <div className="flex-1 space-y-2">
            <LoadingSkeleton width="80%" height={20} />
            <LoadingSkeleton width="60%" height={16} />
          </div>
          <LoadingSkeleton width={80} height={36} />
        </div>
      ))}
    </div>
  )
}

/**
 * Full page loading skeleton
 */
export function PageSkeleton() {
  return (
    <div className="layout-container space-y-6 fade-in">
      {/* Page Header */}
      <div className="page-header">
        <LoadingSkeleton width="40%" height={40} className="mb-2" />
        <LoadingSkeleton width="60%" height={20} />
      </div>

      {/* Stats Grid */}
      <StatCardSkeleton />

      {/* Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartSkeleton />
        <ChartSkeleton />
      </div>

      {/* List Section */}
      <div className="card p-6">
        <LoadingSkeleton width="30%" height={24} className="mb-6" />
        <ListItemSkeleton count={4} />
      </div>
    </div>
  )
}
