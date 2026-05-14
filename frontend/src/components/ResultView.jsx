import React from 'react'
import './ResultView.css'

function ResultView() {
  return (
    <div className="result-view">
      <div className="result-view-header">
        <h3 className="result-view-title">Generated Floor Plan</h3>
        <p className="result-view-subtitle">
          Your AI-generated layout will appear here
        </p>
      </div>
      <div className="result-view-content">
        <div className="result-view-placeholder">
          <div className="result-view-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 3H21V21H3V3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M9 3V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M15 3V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M3 9H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M3 15H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <p className="result-view-placeholder-text">
            Generated floor plan preview will appear here
          </p>
        </div>
      </div>
    </div>
  )
}

export default ResultView
