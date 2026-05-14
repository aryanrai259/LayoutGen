/**
 * SSE Text Processor
 * Intelligently extracts meaningful architectural messages from fragmented SSE tokens
 */

// Garbage patterns to ignore
const GARBAGE_PATTERNS = [
  /^[\s#\|\`\-\*\_]+$/,           // Markdown symbols only
  /^[→↓↑─]+$/,                     // ASCII arrows/separators
  /^\|.*\|$/,                      // Table rows
  /```/,                           // Code fences
  /^[\s\n]+$/,                     // Whitespace only
  /^[0-9\s]+$/,                    // Numbers only
  /^[\.\,\;\:\!\?]+$/              // Punctuation only
]

// Semantic extraction patterns with detail extraction
const SEMANTIC_PATTERNS = {
  // Pipeline initialization
  pipelineStart: {
    pattern: /starting.*generation|initializing.*pipeline/i,
    extract: (buffer) => ({
      title: 'Initializing generation pipeline',
      detail: null
    })
  },
  
  // RAG retrieval
  ragRetrieval: {
    pattern: /retrieving.*blueprint|retrieving.*bylaw|loading.*reference/i,
    extract: (buffer) => ({
      title: 'Loading architectural references',
      detail: null
    })
  },
  ragComplete: {
    pattern: /retrieved\s+(\d+)\s+(blueprint|bylaw)/i,
    extract: (buffer, match) => ({
      title: `Loaded ${match[1]} ${match[2]} references`,
      detail: 'Architectural database queried successfully'
    })
  },
  
  // Spatial planning
  plotDimensions: {
    pattern: /total\s+dimensions|plot\s+size|dimensions?:\s*(\d+)\s*[x×]\s*(\d+)|(\d+)\s*ft\s*[x×]\s*(\d+)\s*ft/i,
    extract: (buffer, match) => {
      const width = match[1] || match[3] || ''
      const height = match[2] || match[4] || ''
      return {
        title: 'Plot dimensions detected',
        detail: width && height ? `${width}ft × ${height}ft rectangular plot` : 'Plot boundaries identified'
      }
    }
  },
  orientation: {
    pattern: /orientation|facing\s+(north|south|east|west)/i,
    extract: (buffer, match) => ({
      title: 'Orientation confirmed',
      detail: match[1] ? `${match[1].charAt(0).toUpperCase() + match[1].slice(1)}-facing entrance alignment` : 'Entrance orientation set'
    })
  },
  publicZone: {
    pattern: /public\s+zone|living\s+area|common\s+area/i,
    extract: (buffer) => ({
      title: 'Public zone planned',
      detail: 'Living and dining grouped for ventilation'
    })
  },
  privateZone: {
    pattern: /private\s+zone|bedroom\s+zone|sleeping\s+area/i,
    extract: (buffer) => ({
      title: 'Bedroom zone configured',
      detail: 'Private sleeping zones arranged for privacy'
    })
  },
  serviceZone: {
    pattern: /service\s+zone|kitchen\s+zone|utility/i,
    extract: (buffer) => ({
      title: 'Kitchen/service zone planned',
      detail: 'Service areas positioned for efficiency'
    })
  },
  kitchenLayout: {
    pattern: /kitchen.*l-shaped|kitchen.*u-shaped|kitchen.*layout/i,
    extract: (buffer) => ({
      title: 'Kitchen layout finalized',
      detail: buffer.match(/l-shaped|u-shaped/i) ? `Kitchen configured as ${buffer.match(/l-shaped|u-shaped/i)[0]}` : 'Kitchen geometry optimized'
    })
  },
  bedroomPlacement: {
    pattern: /bedroom.*placement|bedroom.*position|bedroom\s+(\d+)/i,
    extract: (buffer, match) => ({
      title: 'Bedroom placement configured',
      detail: match[1] ? `${match[1]} bedroom(s) positioned` : 'Private sleeping zones arranged for privacy'
    })
  },
  bathroomPlacement: {
    pattern: /bathroom.*placement|bathroom.*position|washroom/i,
    extract: (buffer) => ({
      title: 'Bathroom placement configured',
      detail: 'Sanitary facilities positioned optimally'
    })
  },
  circulation: {
    pattern: /corridor|circulation|pathway|hallway/i,
    extract: (buffer) => ({
      title: 'Circulation path generated',
      detail: 'Main corridor flow optimized'
    })
  },
  
  // Geometry stages
  coordinateAssignment: {
    pattern: /assigning.*coordinate|coordinate.*assignment|placing.*room/i,
    extract: (buffer) => ({
      title: 'Assigning room coordinates',
      detail: 'Room geometry locked'
    })
  },
  svgGeneration: {
    pattern: /generating.*svg|creating.*svg|svg.*generation|generating.*base\s+svg/i,
    extract: (buffer) => ({
      title: 'Generating architectural SVG',
      detail: 'Blueprint structure being created'
    })
  },
  svgRefinement: {
    pattern: /refining.*wall|fixing.*opening|refining.*svg|refining.*layout/i,
    extract: (buffer) => ({
      title: 'Refining walls and openings',
      detail: 'Door and window placements optimized'
    })
  },
  
  // Completion
  stageComplete: {
    pattern: /stage\s+\d+.*complete|✓.*complete|completed/i,
    extract: (buffer) => ({
      title: 'Stage completed',
      detail: null
    })
  },
  layoutFinalized: {
    pattern: /layout.*finalized|generation.*complete|floor\s+plan.*ready/i,
    extract: (buffer) => ({
      title: 'Layout finalized successfully',
      detail: 'Floor plan ready for review'
    })
  }
}

class SSETextProcessor {
  constructor() {
    this.textBuffer = ''
    this.lastProcessTime = 0
    this.processInterval = 120 // ms
    this.commentary = []
    this.seenTitles = new Set()
    this.maxCommentary = 15
  }

  /**
   * Check if token is garbage
   */
  isGarbage(text) {
    if (!text || text.trim().length === 0) return true
    
    return GARBAGE_PATTERNS.some(pattern => pattern.test(text))
  }

  /**
   * Extract semantic message with detail from text
   */
  extractSemanticMessage(buffer) {
    // Check each semantic pattern
    for (const [key, { pattern, extract }] of Object.entries(SEMANTIC_PATTERNS)) {
      const match = buffer.match(pattern)
      if (match) {
        const result = extract(buffer, match)
        return result
      }
    }
    
    return null
  }

  /**
   * Process incoming text token
   */
  processToken(text, stage, stageName) {
    // Ignore garbage
    if (this.isGarbage(text)) {
      return []
    }

    // Add to buffer
    this.textBuffer += text

    const now = Date.now()
    const timeSinceLastProcess = now - this.lastProcessTime

    // Throttle processing
    if (timeSinceLastProcess < this.processInterval) {
      return this.getCommentary()
    }

    this.lastProcessTime = now

    // Check for sentence boundaries or sufficient length
    const hasBoundary = /[\n\.:]+/.test(this.textBuffer)
    const hasEnoughText = this.textBuffer.length >= 20

    if (!hasBoundary && !hasEnoughText) {
      return this.getCommentary()
    }

    // Extract semantic message with detail
    const semanticResult = this.extractSemanticMessage(this.textBuffer)

    if (semanticResult && !this.seenTitles.has(semanticResult.title)) {
      this.seenTitles.add(semanticResult.title)
      
      // Add to commentary
      this.commentary.push({
        id: Date.now() + Math.random(),
        title: semanticResult.title,
        detail: semanticResult.detail,
        timestamp: Date.now()
      })

      // Keep only last N messages
      if (this.commentary.length > this.maxCommentary) {
        this.commentary.shift()
      }

      // Clear buffer after extraction
      this.textBuffer = ''

      return [...this.commentary]
    }

    // If buffer is too long without semantic match, clear it
    if (this.textBuffer.length > 200) {
      this.textBuffer = ''
    }

    return this.getCommentary()
  }

  /**
   * Force process remaining buffer
   */
  flush() {
    if (this.textBuffer.trim().length > 0) {
      const semanticResult = this.extractSemanticMessage(this.textBuffer)
      if (semanticResult && !this.seenTitles.has(semanticResult.title)) {
        this.commentary.push({
          id: Date.now() + Math.random(),
          title: semanticResult.title,
          detail: semanticResult.detail,
          timestamp: Date.now()
        })
      }
      this.textBuffer = ''
    }
    return [...this.commentary]
  }

  /**
   * Reset processor
   */
  reset() {
    this.textBuffer = ''
    this.lastProcessTime = 0
    this.commentary = []
    this.seenTitles.clear()
  }

  /**
   * Get current commentary
   */
  getCommentary() {
    return [...this.commentary]
  }
}

export default SSETextProcessor
