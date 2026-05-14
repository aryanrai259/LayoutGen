import React, { useEffect, useRef, useState } from 'react'
import './SystemVisualization.css'

function SystemVisualization() {
  const svgRef = useRef(null)
  const [isVisible, setIsVisible] = useState(false)
  const sectionRef = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true)
          }
        })
      },
      { threshold: 0.3 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current)
      }
    }
  }, [])

  return (
    <div ref={sectionRef} className="system-visualization">
      <svg
        ref={svgRef}
        className="system-visualization-svg"
        viewBox="0 0 1200 400"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Input Node */}
        <g className={`visualization-group ${isVisible ? 'animate' : ''}`}>
          <rect
            x="100"
            y="120"
            width="200"
            height="140"
            rx="16"
            className="visualization-node visualization-input"
          />
          <text x="200" y="180" className="visualization-label">
            Input
          </text>
          <text x="200" y="210" className="visualization-sublabel">
            Constraints
          </text>
        </g>

        {/* Arrow 1 */}
        <path
          d="M 300 190 L 450 190"
          className={`visualization-arrow ${isVisible ? 'animate' : ''}`}
          style={{ animationDelay: '0.3s' }}
        />
        <circle
          cx="450"
          cy="190"
          r="6"
          className={`visualization-arrow-head ${isVisible ? 'animate' : ''}`}
          style={{ animationDelay: '0.3s' }}
        />

        {/* AI Engine Node */}
        <g className={`visualization-group ${isVisible ? 'animate' : ''}`} style={{ animationDelay: '0.5s' }}>
          <rect
            x="500"
            y="120"
            width="200"
            height="140"
            rx="16"
            className="visualization-node visualization-engine"
          />
          <text x="600" y="180" className="visualization-label">
            AI Engine
          </text>
          <text x="600" y="210" className="visualization-sublabel">
            Reasoning
          </text>
        </g>

        {/* Arrow 2 */}
        <path
          d="M 700 190 L 850 190"
          className={`visualization-arrow ${isVisible ? 'animate' : ''}`}
          style={{ animationDelay: '0.7s' }}
        />
        <circle
          cx="850"
          cy="190"
          r="6"
          className={`visualization-arrow-head ${isVisible ? 'animate' : ''}`}
          style={{ animationDelay: '0.7s' }}
        />

        {/* Output Node */}
        <g className={`visualization-group ${isVisible ? 'animate' : ''}`} style={{ animationDelay: '0.9s' }}>
          <rect
            x="900"
            y="120"
            width="200"
            height="140"
            rx="16"
            className="visualization-node visualization-output"
          />
          <text x="1000" y="180" className="visualization-label">
            Output
          </text>
          <text x="1000" y="210" className="visualization-sublabel">
            SVG Layout
          </text>
        </g>

        {/* Connection lines with animation */}
        <defs>
          <linearGradient id="arrowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="rgba(34, 211, 238, 0.3)" />
            <stop offset="100%" stopColor="rgba(34, 211, 238, 0.8)" />
          </linearGradient>
        </defs>
        
        {/* Animated flow particles */}
        <circle
          cx="300"
          cy="190"
          r="4"
          className={`visualization-particle ${isVisible ? 'animate' : ''}`}
          style={{ animationDelay: '0.5s' }}
        >
          <animate
            attributeName="cx"
            from="300"
            to="850"
            dur="2s"
            repeatCount="indefinite"
          />
        </circle>
      </svg>
    </div>
  )
}

export default SystemVisualization
