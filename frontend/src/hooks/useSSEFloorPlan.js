import { useState, useRef, useCallback, useEffect } from 'react'
import { generateStream, generateDirect as generateDirectAPI } from '../api/floorPlanApi.js'
import SSETextProcessor from '../utils/sseTextProcessor.js'

/**
 * Main SSE hook for floor plan generation with intelligent commentary extraction
 */
export function useSSEFloorPlan() {
  const [state, setState] = useState({
    status: 'idle', // idle | streaming | refining | done | error | cancelled
    commentary: [],
    svgDraft: null,
    svgFinal: null,
    metadata: null,
    error: null,
    currentLabel: null, // For GhostCanvas
    canvasMode: 'explore' // explore | draft
  })

  const abortControllerRef = useRef(null)
  const textProcessorRef = useRef(null)
  const commentaryTimerRef = useRef(null)

  // Initialize text processor
  useEffect(() => {
    textProcessorRef.current = new SSETextProcessor()
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      if (commentaryTimerRef.current) {
        clearTimeout(commentaryTimerRef.current)
      }
    }
  }, [])

  const generateStreaming = useCallback(async (payload) => {
    // Reset state
    textProcessorRef.current?.reset()
    abortControllerRef.current = new AbortController()

    setState({
      status: 'streaming',
      commentary: [],
      svgDraft: null,
      svgFinal: null,
      metadata: null,
      error: null,
      currentLabel: null
    })

    try {
      await generateStream(
        payload,
        {
          onProgress: (data) => {
            const { stage, stage_name, text } = data

            // Process through text processor
            if (textProcessorRef.current) {
              const updatedCommentary = textProcessorRef.current.processToken(text, stage, stage_name)
              
              // Update commentary with throttling (max 1 per 500ms)
              if (updatedCommentary.length > 0) {
                if (commentaryTimerRef.current) {
                  clearTimeout(commentaryTimerRef.current)
                }

                commentaryTimerRef.current = setTimeout(() => {
                  setState(prev => ({
                    ...prev,
                    commentary: updatedCommentary
                  }))
                }, 500)
              }

              // Update label and mode for GhostCanvas based on stage
              const stageLabels = {
                0: 'Initializing',
                1: 'Spatial Planning',
                2: 'Coordinates',
                3: 'SVG Layout',
                4: 'Refining'
              }
              
              // Switch to draft mode ONLY when SVG generation stage is reached
              // Stage 3 = "SVG Layout" / "Generating architectural SVG"
              // Stage 4 = "Refining" / "Refining walls and openings"
              const isSvgStage = stage === 3 || stage === 4
              
              if (stageLabels[stage]) {
                setState(prev => {
                  const updates = {}
                  
                  // Only update if label changed
                  if (prev.currentLabel !== stageLabels[stage]) {
                    updates.currentLabel = stageLabels[stage]
                  }
                  
                  // Switch to draft mode ONLY for SVG stages (3 or 4)
                  // This ensures draft mode only starts when "Generating architectural SVG" 
                  // appears in live updates, not during earlier stages
                  if (isSvgStage && prev.canvasMode !== 'draft') {
                    updates.canvasMode = 'draft'
                    console.log('🎨 Draft mode activated - SVG generation stage reached')
                  } else if (!isSvgStage && prev.canvasMode !== 'explore' && stage < 3) {
                    // Only switch back to explore if we're before SVG stage
                    // Once in SVG stage, stay in draft until complete
                    updates.canvasMode = 'explore'
                  }
                  
                  return Object.keys(updates).length > 0 ? { ...prev, ...updates } : prev
                })
              }
            }
          },
          onSvg: (data) => {
            const { svg, is_final } = data

            if (is_final) {
              // Add final commentary
              const finalCommentary = textProcessorRef.current?.flush() || []
              finalCommentary.push({
                id: Date.now(),
                title: 'Final architectural layout generated',
                detail: 'SVG blueprint completed',
                timestamp: Date.now()
              })

              setState(prev => ({
                ...prev,
                svgFinal: svg,
                status: 'refining',
                commentary: [...prev.commentary, ...finalCommentary],
                currentLabel: null
              }))
            } else {
              setState(prev => ({
                ...prev,
                svgDraft: svg
              }))
            }
          },
          onFinal: (data) => {
            const { text, metadata } = data

            // Flush any remaining commentary
            const finalCommentary = textProcessorRef.current?.flush() || []

            setState(prev => ({
              ...prev,
              status: 'done',
              metadata: metadata || {},
              commentary: [...prev.commentary, ...finalCommentary]
            }))
          },
          onError: (err) => {
            setState(prev => ({
              ...prev,
              status: 'error',
              error: err.message || 'Generation failed'
            }))
          }
        },
        abortControllerRef.current.signal
      )
    } catch (err) {
      if (err.name === 'AbortError') {
        setState(prev => ({
          ...prev,
          status: 'cancelled',
          commentary: [
            ...prev.commentary,
            {
              id: Date.now(),
              message: 'Generation cancelled',
              type: 'warning',
              timestamp: new Date()
            }
          ]
        }))
      } else {
        setState(prev => ({
          ...prev,
          status: 'error',
          error: err.message || 'Generation failed'
        }))
      }
    }
  }, [])

  const generateDirect = useCallback(async (payload) => {
    setState({
      status: 'streaming',
      commentary: [],
      svgDraft: null,
      svgFinal: null,
      metadata: null,
      error: null,
      currentLabel: null,
      canvasMode: 'explore'
    })

    try {
      const result = await generateDirectAPI(payload)
      
      setState({
        status: 'done',
        svgFinal: result.svg,
        metadata: {
          confidence: result.confidence,
          bylaws_used: result.bylaws_used || [],
          blueprints_referenced: result.blueprints_referenced || [],
          summary: result.summary
        },
        commentary: [
          {
            id: Date.now(),
            title: 'Generation complete',
            detail: 'Floor plan ready for review',
            timestamp: Date.now()
          }
        ],
        error: null,
        currentLabel: null,
        canvasMode: 'explore'
      })
    } catch (err) {
      setState(prev => ({
        ...prev,
        status: 'error',
        error: err.message || 'Generation failed'
      }))
    }
  }, [])

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
  }, [])

  const reset = useCallback(() => {
    textProcessorRef.current?.reset()
    setState({
      status: 'idle',
      commentary: [],
      svgDraft: null,
      svgFinal: null,
      metadata: null,
      error: null,
      currentLabel: null,
      canvasMode: 'explore'
    })
  }, [])

  return {
    state,
    generateStreaming,
    generateDirect,
    cancel,
    reset
  }
}
