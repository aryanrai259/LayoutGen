import React from 'react'
import './LiveUpdatesPanel.css'

function LiveUpdatesPanel({ commentary = [], isGenerating = false }) {
  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return '✓'
      case 'warning':
        return '⚠'
      case 'error':
        return '✗'
      case 'stage':
        return '→'
      default:
        return '•'
    }
  }

  const getTypeClass = (type) => {
    return `commentary-item commentary-${type}`
  }

  return (
    <div className="live-updates-panel">
      <div className="live-updates-header">
        <h3 className="live-updates-title">Live Updates</h3>
        {isGenerating && (
          <div className="live-updates-indicator">
            <span className="pulse-dot"></span>
            <span>Generating...</span>
          </div>
        )}
      </div>
      <div className="live-updates-content">
        {commentary.length === 0 ? (
          <div className="live-updates-empty">
            <p>Updates will appear here as generation progresses...</p>
          </div>
        ) : (
          <div className="commentary-list">
            {commentary.map((item) => (
              <div key={item.id} className={getTypeClass(item.type)}>
                <span className="commentary-icon">{getIcon(item.type)}</span>
                <span className="commentary-message">{item.message}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default LiveUpdatesPanel
