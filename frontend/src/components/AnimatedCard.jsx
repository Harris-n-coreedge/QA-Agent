import React from 'react'
import { useScrollAnimation } from '../hooks/useIntersectionObserver'

/**
 * Animated Card that fades in when scrolling into view
 * @param {object} props
 * @param {React.ReactNode} props.children - Card content
 * @param {string} props.className - Additional CSS classes
 * @param {number} props.delay - Animation delay in ms
 * @param {string} props.animation - Animation type (fadeIn, slideIn, scaleIn)
 */
export function AnimatedCard({
  children,
  className = '',
  delay = 0,
  animation = 'fadeIn',
  threshold = 0.1,
  ...props
}) {
  const [ref, isVisible] = useScrollAnimation({ threshold, delay })

  const animationClasses = {
    fadeIn: 'fade-in',
    slideIn: 'slide-in',
    scaleIn: 'scale-in',
  }

  return (
    <div
      ref={ref}
      className={`card ${isVisible ? animationClasses[animation] || animationClasses.fadeIn : 'opacity-0'} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

/**
 * Staggered animation for list items
 * @param {object} props
 * @param {React.ReactNode} props.children - List items
 * @param {number} props.staggerDelay - Delay between each item in ms
 * @param {string} props.animation - Animation type
 */
export function StaggeredList({
  children,
  staggerDelay = 100,
  animation = 'fadeIn',
  className = '',
  ...props
}) {
  const [ref, isVisible] = useScrollAnimation({ threshold: 0.05 })

  return (
    <div ref={ref} className={className} {...props}>
      {React.Children.map(children, (child, index) => {
        if (!React.isValidElement(child)) return child

        const animationClasses = {
          fadeIn: 'fade-in',
          slideIn: 'slide-in',
          scaleIn: 'scale-in',
        }

        return (
          <div
            className={isVisible ? animationClasses[animation] : 'opacity-0'}
            style={{
              animationDelay: isVisible ? `${index * staggerDelay}ms` : '0ms',
            }}
          >
            {child}
          </div>
        )
      })}
    </div>
  )
}

/**
 * Hover scale effect card
 */
export function HoverScaleCard({ children, className = '', ...props }) {
  return (
    <div
      className={`card hover-lift transition-all duration-300 ease-out hover:scale-[1.02] ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

/**
 * Glow card that highlights on hover
 */
export function GlowCard({ children, className = '', glowColor = 'purple', ...props }) {
  const glowColors = {
    purple: 'hover:shadow-[0_0_30px_rgba(139,92,246,0.3)]',
    blue: 'hover:shadow-[0_0_30px_rgba(59,130,246,0.3)]',
    green: 'hover:shadow-[0_0_30px_rgba(16,185,129,0.3)]',
    red: 'hover:shadow-[0_0_30px_rgba(239,68,68,0.3)]',
    yellow: 'hover:shadow-[0_0_30px_rgba(245,158,11,0.3)]',
  }

  return (
    <div
      className={`card hover-lift transition-all duration-300 ${glowColors[glowColor] || glowColors.purple} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

/**
 * Interactive card with press effect
 */
export function InteractiveCard({
  children,
  onClick,
  className = '',
  ...props
}) {
  return (
    <div
      className={`card card-interactive cursor-pointer transition-all duration-200 active:scale-[0.98] ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyPress={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault()
          onClick(e)
        }
      }}
      {...props}
    >
      {children}
    </div>
  )
}

/**
 * Flip card with front and back content
 */
export function FlipCard({ front, back, className = '', ...props }) {
  const [isFlipped, setIsFlipped] = React.useState(false)

  return (
    <div
      className={`relative h-full cursor-pointer ${className}`}
      onClick={() => setIsFlipped(!isFlipped)}
      onKeyPress={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          setIsFlipped(!isFlipped)
        }
      }}
      tabIndex={0}
      role="button"
      aria-label="Flip card"
      {...props}
    >
      <div
        className={`relative w-full h-full transition-transform duration-500 transform-style-3d ${
          isFlipped ? 'rotate-y-180' : ''
        }`}
        style={{ transformStyle: 'preserve-3d' }}
      >
        {/* Front */}
        <div
          className="absolute inset-0 backface-hidden"
          style={{ backfaceVisibility: 'hidden' }}
        >
          {front}
        </div>

        {/* Back */}
        <div
          className="absolute inset-0 backface-hidden rotate-y-180"
          style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
        >
          {back}
        </div>
      </div>
    </div>
  )
}
