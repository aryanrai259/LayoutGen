import React, { useState, useRef, useEffect } from 'react'
import './FloatingMetricsPanel.css'

function FloatingMetricsPanel({ 
  formData = null, 
  metadata = null, 
  isGenerating = false 
}) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const panelRef = useRef(null)

  // Handle drag
  useEffect(() => {
    if (!isDragging) return

    const handleMouseMove = (e) => {
      setPosition({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      })
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, dragOffset])

  const handleDragStart = (e) => {
    if (isCollapsed) return
    const rect = panelRef.current.getBoundingClientRect()
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    })
    setIsDragging(true)
  }

  const confidence = metadata?.confidence ? (metadata.confidence * 100).toFixed(1) : null
  const bylawsCount = metadata?.bylaws_used?.length || 0
  const blueprintsCount = metadata?.blueprints_referenced?.length || 0

  return (
    <div
      ref={panelRef}
      className={`floating-metrics-panel ${isCollapsed ? 'collapsed' : ''}`}
      style={{
        transform: `translate(${position.x}px, ${position.y}px)`
      }}
    >
      <div
        className="metrics-panel-header"
        onMouseDown={handleDragStart}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        <h3 className="metrics-panel-title">Metrics & Details</h3>
        <button
          className="metrics-collapse-btn"
          onClick={() => setIsCollapsed(!isCollapsed)}
          aria-label={isCollapsed ? 'Expand' : 'Collapse'}
        >
          {isCollapsed ? '▼' : '▲'}
        </button>
      </div>

      {!isCollapsed && (
        <div className="metrics-panel-content">
          {/* Input Summary */}
          {formData && (
            <div className="metrics-section">
              <h4 className="metrics-section-title">Input Parameters</h4>
              <div className="metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">Width</span>
                  <span className="metric-value">{formData.width} ft</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Height</span>
                  <span className="metric-value">{formData.height} ft</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Rooms</span>
                  <span className="metric-value">{formData.rooms}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Orientation</span>
                  <span className="metric-value capitalize">{formData.orientation}</span>
                </div>
              </div>
            </div>
          )}

          {/* Generation Metadata */}
          {metadata && (
            <div className="metrics-section">
              <h4 className="metrics-section-title">Generation Results</h4>
              <div className="metrics-grid">
                {confidence !== null && (
                  <div className="metric-item">
                    <span className="metric-label">Confidence</span>
                    <span className="metric-value">{confidence}%</span>
                  </div>
                )}
                <div className="metric-item">
                  <span className="metric-label">Bylaws Used</span>
                  <span className="metric-value">{bylawsCount}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Blueprints Referenced</span>
                  <span className="metric-value">{blueprintsCount}</span>
                </div>
              </div>
            </div>
          )}

          {/* Status */}
          <div className="metrics-section">
            <h4 className="metrics-section-title">Status</h4>
            <div className="metric-item">
              <span className="metric-label">Current State</span>
              <span className={`metric-value status-${isGenerating ? 'generating' : 'idle'}`}>
                {isGenerating ? 'Generating' : 'Ready'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default FloatingMetricsPanel
