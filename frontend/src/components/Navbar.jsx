import React from 'react'
import { Link } from 'react-router-dom'
import './Navbar.css'

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <span className="navbar-logo">
            AI <span className="navbar-logo-highlight">Floor Plan</span> Designer
          </span>
        </div>
        <div className="navbar-links">
          <a href="/#features" className="navbar-link">Features</a>
          <a href="/#how-it-works" className="navbar-link">How It Works</a>
          <Link to="/generate" className="navbar-link navbar-link-cta">Create Plan</Link>
        </div>
      </div>
      <div className="navbar-accent-line"></div>
    </nav>
  )
}

export default Navbar
