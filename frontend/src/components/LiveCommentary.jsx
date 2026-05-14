import React, { useRef, useEffect } from 'react'
import './LiveCommentary.css'

function LiveCommentary({ commentary = [], isGenerating = false }) {
  const scrollContainerRef = useRef(null)

  // Auto-scroll to latest message
  useEffect(() => {
    if (scrollContainerRef.current && commentary.length > 0) {
      const container = scrollContainerRef.current
      container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth'
      })
    }
  }, [commentary])

  return (
    <div className="live-commentary-panel">
      <div className="commentary-header">
        <h3 className="commentary-title">Design Process Stream</h3>
        {isGenerating && (
          <div className="generating-badge">
            <span className="pulse-dot"></span>
            <span>Generating...</span>
          </div>
        )}
      </div>
      <div className="commentary-content" ref={scrollContainerRef}>
        {commentary.length === 0 ? (
          <div className="commentary-empty">
            <p>Architectural commentary will appear here...</p>
          </div>
        ) : (
          <div className="commentary-list">
            {commentary.map((item) => (
              <div key={item.id} className="commentary-item">
                <div className="commentary-item-main">
                  <span className="commentary-icon">✔</span>
                  <span className="commentary-title-text">{item.title}</span>
                </div>
                {item.detail && (
                  <div className="commentary-item-detail">
                    <span className="detail-arrow">→</span>
                    <span className="detail-text">{item.detail}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default LiveCommentary
