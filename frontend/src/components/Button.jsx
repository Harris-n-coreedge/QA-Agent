import React, { useState, useRef } from 'react'
import { Loader } from 'lucide-react'

/**
 * Enhanced Button component with micro-interactions
 * @param {object} props
 * @param {string} props.variant - Button style variant (primary, secondary, ghost, danger, success)
 * @param {string} props.size - Button size (sm, md, lg)
 * @param {boolean} props.loading - Show loading state
 * @param {boolean} props.disabled - Disable button
 * @param {boolean} props.ripple - Enable ripple effect
 * @param {React.ReactNode} props.leftIcon - Icon to show on the left
 * @param {React.ReactNode} props.rightIcon - Icon to show on the right
 * @param {string} props.className - Additional CSS classes
 * @param {function} props.onClick - Click handler
 * @param {React.ReactNode} props.children - Button content
 */
export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  ripple = true,
  leftIcon,
  rightIcon,
  className = '',
  onClick,
  children,
  type = 'button',
  ...props
}) {
  const [ripples, setRipples] = useState([])
  const buttonRef = useRef(null)

  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    ghost: 'btn-ghost',
    danger: 'bg-red-600 hover:bg-red-700 text-white border-red-700',
    success: 'bg-emerald-600 hover:bg-emerald-700 text-white border-emerald-700',
  }

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs min-h-[32px]',
    md: 'px-4 py-2.5 text-sm min-h-[40px]',
    lg: 'px-6 py-3 text-base min-h-[48px]',
  }

  const handleClick = (e) => {
    if (disabled || loading) return

    // Create ripple effect
    if (ripple && buttonRef.current) {
      const button = buttonRef.current
      const rect = button.getBoundingClientRect()
      const size = Math.max(rect.width, rect.height)
      const x = e.clientX - rect.left - size / 2
      const y = e.clientY - rect.top - size / 2

      const newRipple = {
        x,
        y,
        size,
        id: Date.now(),
      }

      setRipples((prev) => [...prev, newRipple])

      // Remove ripple after animation
      setTimeout(() => {
        setRipples((prev) => prev.filter((r) => r.id !== newRipple.id))
      }, 600)
    }

    onClick?.(e)
  }

  const isDisabled = disabled || loading

  return (
    <button
      ref={buttonRef}
      type={type}
      className={`
        btn
        ${variantClasses[variant] || variantClasses.primary}
        ${sizeClasses[size] || sizeClasses.md}
        ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'hover-lift'}
        ${ripple ? 'relative overflow-hidden' : ''}
        ${className}
      `}
      onClick={handleClick}
      disabled={isDisabled}
      aria-busy={loading}
      {...props}
    >
      {/* Ripple effects */}
      {ripple && ripples.map((ripple) => (
        <span
          key={ripple.id}
          className="absolute rounded-full bg-white/30 animate-ripple pointer-events-none"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: ripple.size,
            height: ripple.size,
          }}
        />
      ))}

      {/* Button content */}
      <span className="relative flex items-center justify-center gap-2">
        {loading && <Loader className="w-4 h-4 animate-spin" />}
        {!loading && leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
        {children}
        {!loading && rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
      </span>
    </button>
  )
}

/**
 * Icon Button component - circular button with just an icon
 */
export function IconButton({
  icon: Icon,
  label,
  variant = 'ghost',
  size = 'md',
  className = '',
  ...props
}) {
  const sizeClasses = {
    sm: 'w-8 h-8 p-1',
    md: 'w-10 h-10 p-2',
    lg: 'w-12 h-12 p-3',
  }

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  }

  return (
    <Button
      variant={variant}
      className={`rounded-full ${sizeClasses[size]} ${className}`}
      aria-label={label}
      title={label}
      {...props}
    >
      <Icon className={iconSizes[size]} />
    </Button>
  )
}

/**
 * Button Group component
 */
export function ButtonGroup({ children, className = '', ...props }) {
  return (
    <div
      className={`inline-flex rounded-lg overflow-hidden border border-gray-800 ${className}`}
      role="group"
      {...props}
    >
      {React.Children.map(children, (child, index) => {
        if (!React.isValidElement(child)) return child

        return React.cloneElement(child, {
          className: `${child.props.className || ''} ${
            index > 0 ? 'border-l border-gray-800' : ''
          } rounded-none`,
        })
      })}
    </div>
  )
}
