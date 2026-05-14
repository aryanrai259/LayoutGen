import React, { useState, useEffect } from 'react'
import GhostCanvas from './GhostCanvas.jsx'
import './SvgPreview.css'

function SvgPreview({ 
  svgDraft = null, 
  svgFinal = null, 
  isGenerating = false, 
  currentLabel = null,
  canvasMode = 'explore',
  onDownload 
}) {
  const [showGhost, setShowGhost] = useState(true)
  const [svgOpacity, setSvgOpacity] = useState(0)

  const hasSvg = svgFinal || svgDraft

  // Reset when starting new generation
  useEffect(() => {
    if (isGenerating && !hasSvg) {
      setShowGhost(true)
      setSvgOpacity(0)
    }
  }, [isGenerating, hasSvg])

  // Handle transition from ghost to SVG
  useEffect(() => {
    if (svgFinal && showGhost) {
      // Fade out ghost, fade in SVG
      setTimeout(() => {
        setShowGhost(false)
        setTimeout(() => {
          setSvgOpacity(1)
        }, 100)
      }, 500)
    } else if (hasSvg && !isGenerating) {
      setShowGhost(false)
      setSvgOpacity(1)
    }
  }, [svgFinal, hasSvg, isGenerating, showGhost])

  const handleGhostComplete = () => {
    setShowGhost(false)
  }

  return (
    <div className="svg-preview-dark">
      <div className="svg-preview-header-dark">
        <h3 className="svg-preview-title-dark">Plan Preview</h3>
        {hasSvg && !isGenerating && (
          <button onClick={onDownload} className="svg-download-btn-dark">
            Download SVG
          </button>
        )}
      </div>
      <div className={`svg-preview-content-dark ${isGenerating && !hasSvg ? 'generating' : ''}`}>
        {/* Ghost Canvas */}
        {showGhost && (isGenerating || !hasSvg) && (
          <GhostCanvas
            isActive={isGenerating && !hasSvg}
            currentLabel={currentLabel}
            mode={canvasMode}
            onComplete={handleGhostComplete}
          />
        )}

        {/* SVG Display */}
        {hasSvg && (
          <div 
            className="svg-viewer-dark"
            style={{ opacity: svgOpacity }}
          >
            <div
              className="svg-content-dark"
              dangerouslySetInnerHTML={{ __html: svgFinal || svgDraft }}
            />
          </div>
        )}

        {/* Empty State */}
        {!hasSvg && !isGenerating && !showGhost && (
          <div className="svg-preview-empty-dark">
            <p>Your floor plan preview will appear here...</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default SvgPreview
