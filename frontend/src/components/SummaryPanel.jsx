import React from 'react'
import './SummaryPanel.css'

function SummaryPanel({ formData = null, metadata = null }) {
  if (!formData) return null

  const builtUpArea = formData.width && formData.height 
    ? (formData.width * formData.height).toFixed(0) 
    : null

  return (
    <div className="summary-panel-dark">
      <div className="summary-header-dark">
        <h3 className="summary-title-dark">Generation Summary</h3>
      </div>
      <div className="summary-content-dark">
        <div className="summary-section-dark">
          <h4 className="summary-section-title-dark">Plot Details</h4>
          <div className="summary-grid-dark">
            <div className="summary-item-dark">
              <span className="summary-label-dark">Width</span>
              <span className="summary-value-dark">{formData.width} ft</span>
            </div>
            <div className="summary-item-dark">
              <span className="summary-label-dark">Height</span>
              <span className="summary-value-dark">{formData.height} ft</span>
            </div>
            {builtUpArea && (
              <div className="summary-item-dark">
                <span className="summary-label-dark">Built-up Area</span>
                <span className="summary-value-dark">{builtUpArea} sq ft</span>
              </div>
            )}
          </div>
        </div>

        <div className="summary-section-dark">
          <h4 className="summary-section-title-dark">Layout</h4>
          <div className="summary-grid-dark">
            <div className="summary-item-dark">
              <span className="summary-label-dark">Bedrooms</span>
              <span className="summary-value-dark">{formData.rooms}</span>
            </div>
            <div className="summary-item-dark">
              <span className="summary-label-dark">Orientation</span>
              <span className="summary-value-dark capitalize">{formData.orientation}</span>
            </div>
            {metadata?.confidence && (
              <div className="summary-item-dark">
                <span className="summary-label-dark">Confidence</span>
                <span className="summary-value-dark">{(metadata.confidence * 100).toFixed(1)}%</span>
              </div>
            )}
          </div>
        </div>

        {metadata && (metadata.bylaws_used?.length > 0 || metadata.blueprints_referenced?.length > 0) && (
          <div className="summary-section-dark">
            <h4 className="summary-section-title-dark">References</h4>
            <div className="summary-grid-dark">
              {metadata.bylaws_used?.length > 0 && (
                <div className="summary-item-dark">
                  <span className="summary-label-dark">Bylaws Used</span>
                  <span className="summary-value-dark">{metadata.bylaws_used.length}</span>
                </div>
              )}
              {metadata.blueprints_referenced?.length > 0 && (
                <div className="summary-item-dark">
                  <span className="summary-label-dark">Blueprints</span>
                  <span className="summary-value-dark">{metadata.blueprints_referenced.length}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SummaryPanel
