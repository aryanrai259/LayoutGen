import React from 'react'
import './NLDescriptionCard.css'

/**
 * Simple markdown renderer - strips code fences and formats basic markdown
 */
function renderMarkdown(text) {
  if (!text) return ''

  // Remove code fences
  let cleaned = text
    .replace(/```svg[\s\S]*?```/g, '')
    .replace(/```[\s\S]*?```/g, '')
    .replace(/```/g, '')

  // Convert headings
  cleaned = cleaned.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  cleaned = cleaned.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  cleaned = cleaned.replace(/^# (.*$)/gim, '<h1>$1</h1>')

  // Convert bullet lists
  cleaned = cleaned.replace(/^\* (.*$)/gim, '<li>$1</li>')
  cleaned = cleaned.replace(/^- (.*$)/gim, '<li>$1</li>')

  // Wrap consecutive <li> in <ul>
  cleaned = cleaned.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
    return `<ul>${match}</ul>`
  })

  // Convert bold
  cleaned = cleaned.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

  // Convert line breaks
  cleaned = cleaned.replace(/\n/g, '<br />')

  return cleaned
}

function NLDescriptionCard({ description = '', isLoading = false }) {
  const renderedContent = renderMarkdown(description)

  return (
    <div className="nl-description-card">
      <div className="nl-description-header">
        <h3 className="nl-description-title">Natural Language Description</h3>
        {isLoading && (
          <div className="nl-description-typing">
            <span className="typing-indicator">●</span>
            <span className="typing-indicator">●</span>
            <span className="typing-indicator">●</span>
          </div>
        )}
      </div>
      <div className="nl-description-content">
        {!description && !isLoading ? (
          <div className="nl-description-empty">
            <p>The natural language description of your floor plan will appear here...</p>
          </div>
        ) : (
          <div
            className="nl-description-text"
            dangerouslySetInnerHTML={{ __html: renderedContent }}
          />
        )}
      </div>
    </div>
  )
}

export default NLDescriptionCard
