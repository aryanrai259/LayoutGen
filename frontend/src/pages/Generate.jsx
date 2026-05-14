import React from 'react'
import { Link } from 'react-router-dom'
import FloorPlanGenerator from './FloorPlanGenerator.jsx'
import './Generate.css'

function Generate() {
  return (
    <div className="generate-page">
      <div className="generate-container">
        <Link to="/" className="generate-back-link">← Back to Home</Link>
        <div className="generate-header">
          <h1 className="generate-title">Create Your Floor Plan</h1>
          <p className="generate-subtitle">
            Enter your requirements and let AI generate the perfect layout
          </p>
        </div>
        <FloorPlanGenerator />
      </div>
    </div>
  )
}

export default Generate
