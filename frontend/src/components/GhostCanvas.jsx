import React, { useRef, useEffect, useState } from 'react'
import './GhostCanvas.css'

function GhostCanvas({ isActive = false, currentLabel = null, mode = 'explore', onComplete }) {
  const canvasRef = useRef(null)
  const animationFrameRef = useRef(null)
  const [fadeOut, setFadeOut] = useState(false)

  // Canvas state
  const stateRef = useRef({
    // Explore mode
    currentX: 0,
    currentY: 0,
    targetX: 0,
    targetY: 0,
    trail: [],
    marks: [],
    label: null,
    labelTimer: null,
    targetTimer: null,
    // Draft mode - realistic floor plan
    drawingPath: [],
    currentPathIndex: 0,
    pathProgress: 0,
    completedPaths: [],
    roomOutlines: [],
    wallLines: [],
    doorOpenings: [],
    drawingComplete: false
  })

  useEffect(() => {
    if (!isActive || fadeOut) return

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const dpr = window.devicePixelRatio || 1

    // Set canvas size
    const resize = () => {
      const rect = canvas.getBoundingClientRect()
      canvas.width = rect.width * dpr
      canvas.height = rect.height * dpr
      ctx.scale(dpr, dpr)
      canvas.style.width = rect.width + 'px'
      canvas.style.height = rect.height + 'px'
    }

    resize()
    window.addEventListener('resize', resize)

    const rect = canvas.getBoundingClientRect()
    const gridSize = 25

    // Initialize explore mode position
    stateRef.current.currentX = rect.width / 2
    stateRef.current.currentY = rect.height / 2
    stateRef.current.targetX = stateRef.current.currentX
    stateRef.current.targetY = stateRef.current.currentY

    // Initialize realistic floor plan structure
    const initRealisticFloorPlan = () => {
      const margin = 60
      const plotWidth = rect.width - margin * 2
      const plotHeight = rect.height - margin * 2
      const startX = margin
      const startY = margin

      // Define realistic room layout
      const rooms = [
        // Living room (large, front)
        { x: startX + 20, y: startY + 20, width: plotWidth * 0.45, height: plotHeight * 0.35, label: 'Living' },
        // Kitchen (middle left)
        { x: startX + 20, y: startY + plotHeight * 0.4, width: plotWidth * 0.25, height: plotHeight * 0.3, label: 'Kitchen' },
        // Bedroom 1 (top right)
        { x: startX + plotWidth * 0.5, y: startY + 20, width: plotWidth * 0.45, height: plotHeight * 0.35, label: 'Bedroom 1' },
        // Bedroom 2 (bottom right)
        { x: startX + plotWidth * 0.5, y: startY + plotHeight * 0.4, width: plotWidth * 0.45, height: plotHeight * 0.3, label: 'Bedroom 2' },
        // Bathroom (small, bottom left)
        { x: startX + 20, y: startY + plotHeight * 0.75, width: plotWidth * 0.25, height: plotHeight * 0.2, label: 'Bathroom' },
        // Corridor (connecting)
        { x: startX + plotWidth * 0.3, y: startY + plotHeight * 0.4, width: plotWidth * 0.18, height: plotHeight * 0.35, label: 'Corridor' }
      ]

      // Create drawing paths for each room (outline drawing)
      const paths = []

      // 1. Draw outer plot boundary
      paths.push({
        type: 'outline',
        points: [
          { x: startX, y: startY },
          { x: startX + plotWidth, y: startY },
          { x: startX + plotWidth, y: startY + plotHeight },
          { x: startX, y: startY + plotHeight },
          { x: startX, y: startY } // Close the path
        ],
        label: 'Plot Boundary',
        progress: 0
      })

      // 2. Draw room outlines
      rooms.forEach(room => {
        paths.push({
          type: 'room',
          points: [
            { x: room.x, y: room.y },
            { x: room.x + room.width, y: room.y },
            { x: room.x + room.width, y: room.y + room.height },
            { x: room.x, y: room.y + room.height },
            { x: room.x, y: room.y } // Close
          ],
          label: room.label,
          progress: 0
        })
      })

      // 3. Draw internal walls (partition lines)
      const walls = [
        // Vertical wall between living and bedroom
        { x1: startX + plotWidth * 0.5, y1: startY + 20, x2: startX + plotWidth * 0.5, y2: startY + plotHeight * 0.4 },
        // Horizontal wall between living/kitchen and bedrooms
        { x1: startX + 20, y1: startY + plotHeight * 0.4, x2: startX + plotWidth - 20, y2: startY + plotHeight * 0.4 },
        // Vertical wall for corridor
        { x1: startX + plotWidth * 0.3, y1: startY + plotHeight * 0.4, x2: startX + plotWidth * 0.3, y2: startY + plotHeight * 0.75 },
        { x1: startX + plotWidth * 0.48, y1: startY + plotHeight * 0.4, x2: startX + plotWidth * 0.48, y2: startY + plotHeight * 0.75 }
      ]

      walls.forEach(wall => {
        paths.push({
          type: 'wall',
          points: [
            { x: wall.x1, y: wall.y1 },
            { x: wall.x2, y: wall.y2 }
          ],
          label: null,
          progress: 0
        })
      })

      // 4. Draw door openings (small gaps in walls)
      const doors = [
        { x: startX + plotWidth * 0.25, y: startY + plotHeight * 0.4, width: 30, isVertical: false },
        { x: startX + plotWidth * 0.5, y: startY + plotHeight * 0.5, width: 30, isVertical: true },
        { x: startX + plotWidth * 0.48, y: startY + plotHeight * 0.6, width: 30, isVertical: false }
      ]

      doors.forEach(door => {
        paths.push({
          type: 'door',
          points: door.isVertical
            ? [
                { x: door.x, y: door.y },
                { x: door.x, y: door.y + door.width }
              ]
            : [
                { x: door.x, y: door.y },
                { x: door.x + door.width, y: door.y }
              ],
          label: null,
          progress: 0
        })
      })

      stateRef.current.drawingPath = paths
      stateRef.current.currentPathIndex = 0
      stateRef.current.pathProgress = 0
      stateRef.current.completedPaths = []
      stateRef.current.drawingComplete = false
    }

    // Draw grid
    const drawGrid = () => {
      ctx.strokeStyle = mode === 'draft' ? 'rgba(255, 255, 255, 0.03)' : 'rgba(34, 211, 238, 0.1)'
      ctx.lineWidth = 0.5

      for (let x = 0; x < rect.width; x += gridSize) {
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, rect.height)
        ctx.stroke()
      }

      for (let y = 0; y < rect.height; y += gridSize) {
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(rect.width, y)
        ctx.stroke()
      }
    }

    // Draw vignette
    const drawVignette = () => {
      const gradient = ctx.createRadialGradient(
        rect.width / 2,
        rect.height / 2,
        0,
        rect.width / 2,
        rect.height / 2,
        Math.max(rect.width, rect.height) * 0.7
      )
      gradient.addColorStop(0, 'rgba(11, 18, 32, 0)')
      gradient.addColorStop(1, 'rgba(11, 18, 32, 0.3)')
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, rect.width, rect.height)
    }

    // EXPLORE MODE FUNCTIONS
    const drawCursor = () => {
      if (mode !== 'explore') return
      
      const { currentX, currentY } = stateRef.current
      const size = 8

      ctx.strokeStyle = '#22D3EE'
      ctx.lineWidth = 1.5
      ctx.shadowBlur = 10
      ctx.shadowColor = '#22D3EE'

      ctx.beginPath()
      ctx.moveTo(currentX - size, currentY)
      ctx.lineTo(currentX + size, currentY)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(currentX, currentY - size)
      ctx.lineTo(currentX, currentY + size)
      ctx.stroke()

      ctx.shadowBlur = 0
    }

    const drawTrail = () => {
      if (mode !== 'explore') return
      
      const { trail } = stateRef.current
      if (trail.length < 2) return

      for (let i = 1; i < trail.length; i++) {
        const alpha = i / trail.length * 0.4
        ctx.strokeStyle = `rgba(34, 211, 238, ${alpha})`
        ctx.lineWidth = 2
        ctx.lineCap = 'round'
        
        ctx.beginPath()
        ctx.moveTo(trail[i - 1].x, trail[i - 1].y)
        ctx.lineTo(trail[i].x, trail[i].y)
        ctx.stroke()
      }
    }

    const drawMarks = () => {
      if (mode !== 'explore') return
      
      const { marks } = stateRef.current
      const now = Date.now()

      marks.forEach((mark) => {
        const age = now - mark.time
        if (age > 500) return

        const alpha = 1 - (age / 500)
        const size = 4 + (age / 500) * 8

        ctx.strokeStyle = `rgba(34, 211, 238, ${alpha * 0.8})`
        ctx.lineWidth = 2

        const { x, y } = mark
        ctx.beginPath()
        ctx.moveTo(x, y)
        ctx.lineTo(x + size, y)
        ctx.moveTo(x, y)
        ctx.lineTo(x, y + size)
        ctx.stroke()
      })
    }

    const updateExplorePosition = () => {
      if (mode !== 'explore') return
      
      const { currentX, currentY, targetX, targetY } = stateRef.current
      const speed = 3

      if (Math.abs(currentX - targetX) > speed) {
        stateRef.current.currentX += currentX < targetX ? speed : -speed
      } else {
        stateRef.current.currentX = targetX
      }

      if (Math.abs(currentY - targetY) > speed && Math.abs(currentX - targetX) < speed) {
        stateRef.current.currentY += currentY < targetY ? speed : -speed
      } else if (Math.abs(currentX - targetX) < speed) {
        stateRef.current.currentY = targetY
      }

      stateRef.current.trail.push({
        x: stateRef.current.currentX,
        y: stateRef.current.currentY
      })

      if (stateRef.current.trail.length > 50) {
        stateRef.current.trail.shift()
      }

      const reachedX = Math.abs(stateRef.current.currentX - targetX) < speed
      const reachedY = Math.abs(stateRef.current.currentY - targetY) < speed
      
      if (reachedX && reachedY) {
        stateRef.current.marks.push({
          x: stateRef.current.currentX,
          y: stateRef.current.currentY,
          time: Date.now()
        })

        if (!stateRef.current.targetTimer) {
          stateRef.current.targetTimer = setTimeout(() => {
            const newTargetX = Math.floor(Math.random() * Math.floor(rect.width / gridSize)) * gridSize
            const newTargetY = Math.floor(Math.random() * Math.floor(rect.height / gridSize)) * gridSize
            stateRef.current.targetX = newTargetX
            stateRef.current.targetY = newTargetY
            stateRef.current.targetTimer = null
          }, 150)
        }
      }
    }

    // DRAFT MODE - Realistic Floor Plan Drawing
    const lerp = (start, end, t) => start + (end - start) * t

    const drawPath = (path, progress) => {
      if (!path || path.points.length < 2) return

      const points = path.points
      const totalLength = points.length
      const currentPointIndex = Math.floor(progress * (totalLength - 1))
      const segmentProgress = (progress * (totalLength - 1)) % 1

      // Set drawing style based on path type
      if (path.type === 'outline') {
        ctx.strokeStyle = '#22D3EE'
        ctx.lineWidth = 2.5
        ctx.shadowBlur = 8
        ctx.shadowColor = 'rgba(34, 211, 238, 0.6)'
      } else if (path.type === 'room') {
        ctx.strokeStyle = '#22D3EE'
        ctx.lineWidth = 2
        ctx.shadowBlur = 6
        ctx.shadowColor = 'rgba(34, 211, 238, 0.5)'
      } else if (path.type === 'wall') {
        ctx.strokeStyle = '#22D3EE'
        ctx.lineWidth = 1.5
        ctx.shadowBlur = 4
        ctx.shadowColor = 'rgba(34, 211, 238, 0.4)'
      } else if (path.type === 'door') {
        ctx.strokeStyle = '#34D399'
        ctx.lineWidth = 2
        ctx.shadowBlur = 6
        ctx.shadowColor = 'rgba(52, 211, 153, 0.5)'
      }

      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'

      // Draw completed segments
      for (let i = 0; i < currentPointIndex; i++) {
        if (i < points.length - 1) {
          ctx.beginPath()
          ctx.moveTo(points[i].x, points[i].y)
          ctx.lineTo(points[i + 1].x, points[i + 1].y)
          ctx.stroke()
        }
      }

      // Draw current segment being drawn
      if (currentPointIndex < points.length - 1) {
        const startPoint = points[currentPointIndex]
        const endPoint = points[currentPointIndex + 1]
        const currentX = lerp(startPoint.x, endPoint.x, segmentProgress)
        const currentY = lerp(startPoint.y, endPoint.y, segmentProgress)

        ctx.beginPath()
        ctx.moveTo(startPoint.x, startPoint.y)
        ctx.lineTo(currentX, currentY)
        ctx.stroke()

        // Draw drawing cursor (marker tip)
        ctx.fillStyle = '#22D3EE'
        ctx.shadowBlur = 12
        ctx.beginPath()
        ctx.arc(currentX, currentY, 4, 0, Math.PI * 2)
        ctx.fill()
      }

      // Draw room label if path is complete
      if (progress >= 1 && path.label) {
        const centerX = points.reduce((sum, p) => sum + p.x, 0) / points.length
        const centerY = points.reduce((sum, p) => sum + p.y, 0) / points.length

        ctx.fillStyle = 'rgba(34, 211, 238, 0.8)'
        ctx.font = '11px Inter, sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.shadowBlur = 8
        ctx.shadowColor = 'rgba(34, 211, 238, 0.5)'
        ctx.fillText(path.label, centerX, centerY)
        ctx.shadowBlur = 0
      }

      ctx.shadowBlur = 0
    }

    const updateDraftMode = () => {
      if (mode !== 'draft') return

      const { drawingPath, currentPathIndex, pathProgress } = stateRef.current

      if (drawingPath.length === 0) {
        initRealisticFloorPlan()
        return
      }

      if (currentPathIndex >= drawingPath.length) {
        // All paths drawn, keep showing completed drawing
        stateRef.current.drawingComplete = true
        return
      }

      const currentPath = drawingPath[currentPathIndex]
      if (!currentPath) return

      // Animate drawing this path (slow motion speed)
      stateRef.current.pathProgress += 0.01 // Drawing speed - reduced for slow motion effect

      if (stateRef.current.pathProgress >= 1) {
        // Path complete, move to next
        stateRef.current.pathProgress = 0
        stateRef.current.currentPathIndex++
        
        // Longer pause between paths for slow motion effect
        if (stateRef.current.currentPathIndex < drawingPath.length) {
          setTimeout(() => {
            // Continue to next path
          }, 600)
        }
      }
    }

    // Draw label
    const drawLabel = () => {
      const { label, labelTimer, currentX, currentY } = stateRef.current
      if (!label || !labelTimer) return

      const age = Date.now() - labelTimer
      if (age > 1200) {
        stateRef.current.label = null
        stateRef.current.labelTimer = null
        return
      }

      const alpha = age < 200 ? age / 200 : (1200 - age) / 1000
      const offsetY = -30 - (age / 1200) * 10
      const x = mode === 'explore' ? currentX : rect.width / 2
      const y = mode === 'explore' ? currentY : 30

      ctx.fillStyle = `rgba(34, 211, 238, ${alpha})`
      ctx.font = '12px Inter, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.shadowBlur = 8
      ctx.shadowColor = 'rgba(34, 211, 238, 0.5)'

      ctx.fillText(label, x, y + offsetY)
      ctx.shadowBlur = 0
    }

    // Initialize draft mode if needed
    if (mode === 'draft' && stateRef.current.drawingPath.length === 0) {
      initRealisticFloorPlan()
    }

    // Animation loop
    const animate = () => {
      if (fadeOut) return

      ctx.clearRect(0, 0, rect.width, rect.height)

      drawGrid()
      drawVignette()

      if (mode === 'explore') {
        updateExplorePosition()
        drawTrail()
        drawMarks()
        drawCursor()
      } else if (mode === 'draft') {
        updateDraftMode()
        
        // Draw all completed paths
        for (let i = 0; i < stateRef.current.currentPathIndex; i++) {
          const path = stateRef.current.drawingPath[i]
          if (path) {
            drawPath(path, 1) // Draw completed
          }
        }
        
        // Draw current path being drawn
        if (stateRef.current.currentPathIndex < stateRef.current.drawingPath.length) {
          const currentPath = stateRef.current.drawingPath[stateRef.current.currentPathIndex]
          if (currentPath) {
            drawPath(currentPath, stateRef.current.pathProgress)
          }
        }
      }

      drawLabel()

      animationFrameRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resize)
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
      if (stateRef.current.targetTimer) {
        clearTimeout(stateRef.current.targetTimer)
      }
    }
  }, [isActive, fadeOut, mode])

  // Handle label changes
  useEffect(() => {
    if (currentLabel) {
      stateRef.current.label = currentLabel
      stateRef.current.labelTimer = Date.now()
    }
  }, [currentLabel])

  // Handle mode switch
  useEffect(() => {
    if (mode === 'draft') {
      // Reset explore mode state
      stateRef.current.trail = []
      stateRef.current.marks = []
    }
  }, [mode])

  // Handle completion
  useEffect(() => {
    if (onComplete && !isActive) {
      setFadeOut(true)
      setTimeout(() => {
        onComplete()
      }, 500)
    }
  }, [isActive, onComplete])

  return (
    <div className={`ghost-canvas-container ${fadeOut ? 'fade-out' : ''} ${mode === 'draft' ? 'draft-mode' : ''}`}>
      <canvas ref={canvasRef} className="ghost-canvas" />
      <div className="ghost-canvas-overlay">
        <div className="scanline"></div>
      </div>
    </div>
  )
}

export default GhostCanvas
