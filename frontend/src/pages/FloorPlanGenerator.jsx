import React, { useState, useEffect } from 'react'
import { useSSEFloorPlan } from '../hooks/useSSEFloorPlan.js'
import InputForm from '../components/InputForm.jsx'
import LiveCommentary from '../components/LiveCommentary.jsx'
import SvgPreview from '../components/SvgPreview.jsx'
import SummaryPanel from '../components/SummaryPanel.jsx'
import './FloorPlanGenerator.css'

function FloorPlanGenerator() {
  const { state, generateStreaming, generateDirect, cancel, reset } = useSSEFloorPlan()
  const [formData, setFormData] = useState(null)
  const [uiMode, setUiMode] = useState('idle') // idle | streaming_active | streaming_final | normal_final
  const [generationMode, setGenerationMode] = useState(null) // 'stream' | 'direct' | null

  // Update UI mode based on state
  useEffect(() => {
    if (state.status === 'idle' || state.status === 'error') {
      setUiMode('idle')
      setGenerationMode(null)
    } else if (generationMode === 'stream') {
      if (state.status === 'streaming' || state.status === 'refining') {
        setUiMode('streaming_active')
      } else if (state.status === 'done' && state.svgFinal) {
        setUiMode('streaming_final')
      }
    } else if (generationMode === 'direct') {
      if (state.status === 'streaming') {
        // Keep showing input form during direct generation
        setUiMode('idle')
      } else if (state.status === 'done' && state.svgFinal) {
        setUiMode('normal_final')
      }
    }
  }, [state.status, state.svgFinal, generationMode])

  const handleGenerate = async (data, mode = 'stream') => {
    setFormData(data)
    setGenerationMode(mode)

    // Prepare payload
    const payload = {
      description: data.description.trim(),
      width: parseFloat(data.width),
      height: parseFloat(data.height),
      rooms: parseInt(data.rooms),
      orientation: data.orientation.toLowerCase(),
      room_types: Array.isArray(data.room_types) && data.room_types.length > 0 
        ? data.room_types 
        : ['living_room', 'bedroom', 'kitchen', 'bathroom'],
      jurisdiction: data.jurisdiction || 'residential'
    }

    if (mode === 'stream') {
      setUiMode('streaming_active')
      await generateStreaming(payload)
    } else {
      // For direct mode, keep showing input form until response arrives
      await generateDirect(payload)
    }
  }

  const handleCancel = () => {
    cancel()
    setUiMode('idle')
    setGenerationMode(null)
  }

  const handleReset = () => {
    reset()
    setFormData(null)
    setUiMode('idle')
    setGenerationMode(null)
  }

  const handleDownload = () => {
    const svg = state.svgFinal || state.svgDraft
    if (!svg) return

    const blob = new Blob([svg], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'floor-plan.svg'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const isGenerating = state.status === 'streaming' || state.status === 'refining'
  const isDone = state.status === 'done'
  const hasError = state.status === 'error'
  const hasSvg = state.svgFinal || state.svgDraft

  return (
    <div className="floor-plan-generator-dark">
      {/* Top Bar */}
      <div className="generator-top-bar-dark">
        <h1 className="generator-page-title-dark">Create Floor Plan</h1>
        <div className="generator-actions-dark">
          {isGenerating && (
            <button onClick={handleCancel} className="cancel-btn-dark">
              Cancel
            </button>
          )}
          {isDone && (
            <button onClick={handleReset} className="new-plan-btn-dark">
              New Plan
            </button>
          )}
        </div>
      </div>

      {/* IDLE STATE: Input Form Layout */}
      {uiMode === 'idle' && (
        <div className="input-form-layout-dark">
          <div className="input-form-center-dark">
            <InputForm 
              onSubmit={(data) => handleGenerate(data, 'stream')} 
              isGenerating={isGenerating}
              onDirectGenerate={(data) => {
                if (data) {
                  handleGenerate(data, 'direct')
                }
              }}
            />
          </div>
        </div>
      )}

      {/* STREAMING ACTIVE: 2-Grid Layout (40% Live Updates, 60% Ghost Canvas) */}
      {uiMode === 'streaming_active' && (
        <div className="generator-main-grid-dark generator-grid-2-dark">
          <div className="generator-column-dark generator-left-column-dark generator-column-40-dark">
            <LiveCommentary 
              commentary={state.commentary} 
              isGenerating={isGenerating}
            />
          </div>
          <div className="generator-column-dark generator-right-column-dark generator-column-60-dark">
            <SvgPreview
              svgDraft={state.svgDraft}
              svgFinal={null}
              isGenerating={true}
              currentLabel={state.currentLabel}
              canvasMode={state.canvasMode}
              onDownload={handleDownload}
            />
          </div>
        </div>
      )}

      {/* STREAMING FINAL: 3-Grid Layout (20% Live Updates, 20% Summary, 60% SVG) */}
      {uiMode === 'streaming_final' && (
        <div className="generator-main-grid-dark generator-grid-3-dark">
          <div className="generator-column-dark generator-left-column-dark generator-column-20-dark">
            <LiveCommentary 
              commentary={state.commentary} 
              isGenerating={false}
            />
          </div>
          <div className="generator-column-dark generator-center-column-dark generator-column-20-dark">
            <SummaryPanel 
              formData={formData}
              metadata={state.metadata}
            />
          </div>
          <div className="generator-column-dark generator-right-column-dark generator-column-60-dark">
            <SvgPreview
              svgDraft={state.svgDraft}
              svgFinal={state.svgFinal}
              isGenerating={false}
              currentLabel={null}
              canvasMode="explore"
              onDownload={handleDownload}
            />
          </div>
        </div>
      )}

      {/* NORMAL FINAL: 2-Grid Layout (30% Summary, 70% SVG) */}
      {uiMode === 'normal_final' && (
        <div className="generator-main-grid-dark generator-grid-normal-final">
          <div className="generator-column-dark generator-left-column-dark generator-column-30-dark">
            <SummaryPanel 
              formData={formData}
              metadata={state.metadata}
            />
          </div>
          <div className="generator-column-dark generator-right-column-dark generator-column-70-dark">
            <SvgPreview
              svgDraft={null}
              svgFinal={state.svgFinal}
              isGenerating={false}
              currentLabel={null}
              canvasMode="explore"
              onDownload={handleDownload}
            />
          </div>
        </div>
      )}

      {/* Error Display */}
      {hasError && (
        <div className="error-banner-dark">
          <div className="error-banner-content-dark">
            <span className="error-icon-dark">⚠</span>
            <span className="error-message-dark">{state.error}</span>
            <button onClick={handleReset} className="error-dismiss-btn-dark">
              Dismiss
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default FloorPlanGenerator
