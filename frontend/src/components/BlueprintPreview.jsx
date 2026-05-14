import React, { useEffect, useRef, useState } from 'react'
import './BlueprintPreview.css'

function BlueprintPreview() {
  const canvasRef = useRef(null)
  const containerRef = useRef(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const container = containerRef.current

    // Set canvas size
    const resizeCanvas = () => {
      if (container) {
        canvas.width = container.clientWidth
        canvas.height = container.clientHeight
      }
    }
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // Grid settings
    const gridSize = 25
    const gridColor = 'rgba(34, 211, 238, 0.1)'
    const lineColor = 'rgba(34, 211, 238, 0.3)'

    // Sample floor plan paths (simplified)
    const floorPlanPaths = [
      // Outer boundary
      { points: [[50, 50], [350, 50], [350, 300], [50, 300], [50, 50]], color: 'rgba(34, 211, 238, 0.6)', width: 2 },
      // Living room
      { points: [[80, 80], [200, 80], [200, 150], [80, 150], [80, 80]], color: 'rgba(34, 211, 238, 0.4)', width: 1.5 },
      // Kitchen
      { points: [[220, 80], [320, 80], [320, 150], [220, 150], [220, 80]], color: 'rgba(34, 211, 238, 0.4)', width: 1.5 },
      // Bedroom
      { points: [[80, 180], [200, 180], [200, 280], [80, 280], [80, 180]], color: 'rgba(34, 211, 238, 0.4)', width: 1.5 },
      // Bathroom
      { points: [[220, 180], [320, 180], [320, 250], [220, 250], [220, 180]], color: 'rgba(34, 211, 238, 0.4)', width: 1.5 },
    ]

    let animationFrame
    let time = 0
    let animationComplete = false

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Draw grid
      ctx.strokeStyle = gridColor
      ctx.lineWidth = 0.5
      for (let x = 0; x < canvas.width; x += gridSize) {
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
      }
      for (let y = 0; y < canvas.height; y += gridSize) {
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(canvas.width, y)
        ctx.stroke()
      }

      // Draw floor plan with subtle animation
      if (!animationComplete) {
        time += 0.02
        if (time >= 3) {
          animationComplete = true
          time = 3
        }
      }

      floorPlanPaths.forEach((path, index) => {
        ctx.strokeStyle = path.color
        ctx.lineWidth = path.width
        ctx.beginPath()
        
        const startTime = index * 0.3
        const endTime = startTime + 0.8
        const progress = Math.max(0, Math.min(1, (time - startTime) / (endTime - startTime)))
        
        if (progress > 0) {
          path.points.forEach((point, i) => {
            if (i === 0) {
              ctx.moveTo(point[0], point[1])
            } else {
              ctx.lineTo(point[0], point[1])
            }
          })
          
          // Draw with opacity based on progress
          ctx.globalAlpha = Math.min(1, progress * 1.2)
          ctx.stroke()
          
          // Glow effect
          ctx.shadowBlur = 8
          ctx.shadowColor = path.color
          ctx.stroke()
          ctx.shadowBlur = 0
          ctx.globalAlpha = 1
        }
      })

      // Parallax cursor effect
      const cursorX = mousePos.x
      const cursorY = mousePos.y
      if (cursorX > 0 && cursorY > 0) {
        ctx.strokeStyle = 'rgba(34, 211, 238, 0.5)'
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(cursorX - 10, cursorY)
        ctx.lineTo(cursorX + 10, cursorY)
        ctx.moveTo(cursorX, cursorY - 10)
        ctx.lineTo(cursorX, cursorY + 10)
        ctx.stroke()
        
        ctx.shadowBlur = 6
        ctx.shadowColor = 'rgba(34, 211, 238, 0.8)'
        ctx.stroke()
        ctx.shadowBlur = 0
      }

      animationFrame = requestAnimationFrame(draw)
    }

    draw()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      cancelAnimationFrame(animationFrame)
    }
  }, [mousePos])

  const handleMouseMove = (e) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect()
      setMousePos({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      })
    }
  }

  const handleMouseLeave = () => {
    setMousePos({ x: 0, y: 0 })
  }

  return (
    <div
      ref={containerRef}
      className="blueprint-preview"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <canvas ref={canvasRef} className="blueprint-canvas" />
      <div className="blueprint-overlay">
        <div className="blueprint-label">Live Preview</div>
      </div>
    </div>
  )
}

export default BlueprintPreview
