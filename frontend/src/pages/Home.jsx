import React from 'react'
import { Link } from 'react-router-dom'
import { Building2, Brain, Compass, Ruler } from 'lucide-react'
import BlueprintPreview from '../components/BlueprintPreview'
import PipelineStepper from '../components/PipelineStepper'
import SystemVisualization from '../components/SystemVisualization'
import { useScrollAnimation } from '../hooks/useScrollAnimation'
import './Home.css'

function Home() {
  const [capabilitiesRef, capabilitiesVisible] = useScrollAnimation({ threshold: 0.2 })
  const [visualizationRef, visualizationVisible] = useScrollAnimation({ threshold: 0.2 })
  const [ctaRef, ctaVisible] = useScrollAnimation({ threshold: 0.2 })

  const handleViewDemo = () => {
    visualizationRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="home">
      {/* Hero Section - Redesigned */}
      <section className="hero-section-new">
        <div className="hero-container-new">
          <div className="hero-content-new">
            <div className="hero-badge-new">
              <span>AI-POWERED ARCHITECTURAL PLANNING</span>
            </div>
            <h1 className="hero-heading-new">
              Generate Regulation-Compliant Floor Plans Instantly
            </h1>
            <p className="hero-subheading-new">
              Production-ready AI system that understands compliance rules, Vaastu principles, 
              and spatial optimization to deliver architect-grade floor plans in seconds.
            </p>
            <div className="hero-features-list">
              <div className="hero-feature-item">
                <span className="hero-feature-icon">✓</span>
                <span>Compliance-aware design</span>
              </div>
              <div className="hero-feature-item">
                <span className="hero-feature-icon">✓</span>
                <span>Vaastu logic integration</span>
              </div>
              <div className="hero-feature-item">
                <span className="hero-feature-icon">✓</span>
                <span>Spatial optimization</span>
              </div>
              <div className="hero-feature-item">
                <span className="hero-feature-icon">✓</span>
                <span>Production-ready SVG output</span>
              </div>
            </div>
            <div className="hero-cta-buttons">
              <Link to="/generate" className="hero-cta-primary">
                Start Designing
              </Link>
              <button className="hero-cta-secondary" onClick={handleViewDemo}>
                View Demo Layout
              </button>
            </div>
          </div>
          <div className="hero-visual-new">
            <BlueprintPreview />
          </div>
        </div>
      </section>

      {/* Product Capabilities Section */}
      <section 
        ref={capabilitiesRef}
        className={`capabilities-section ${capabilitiesVisible ? 'visible' : ''}`} 
        id="features"
      >
        <div className="capabilities-container">
          <div className="capabilities-header">
            <h2 className="capabilities-title">Built With Architectural Intelligence</h2>
            <p className="capabilities-subtitle">
              Advanced AI layers working together to deliver compliant, optimized floor plans
            </p>
          </div>
          <div className="capabilities-grid">
            <div className="capability-card">
              <div className="capability-icon">
                <Building2 size={32} />
              </div>
              <h3 className="capability-title">Compliance Engine</h3>
              <ul className="capability-features">
                <li>Auto validates zoning rules</li>
                <li>Setback aware planning</li>
                <li>Regulation aligned layouts</li>
              </ul>
            </div>
            <div className="capability-card">
              <div className="capability-icon">
                <Brain size={32} />
              </div>
              <h3 className="capability-title">Spatial Reasoning Core</h3>
              <ul className="capability-features">
                <li>Intelligent room adjacency</li>
                <li>Circulation optimization</li>
                <li>Space utilization balancing</li>
              </ul>
            </div>
            <div className="capability-card">
              <div className="capability-icon">
                <Compass size={32} />
              </div>
              <h3 className="capability-title">Vaastu Alignment Layer</h3>
              <ul className="capability-features">
                <li>Directional placement logic</li>
                <li>Traditional planning rules</li>
                <li>Cultural compliance</li>
              </ul>
            </div>
            <div className="capability-card">
              <div className="capability-icon">
                <Ruler size={32} />
              </div>
              <h3 className="capability-title">SVG CAD Output Engine</h3>
              <ul className="capability-features">
                <li>Vector precision</li>
                <li>Scalable output</li>
                <li>Production-ready format</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* System Visualization Section */}
      <section 
        ref={visualizationRef}
        className={`visualization-section ${visualizationVisible ? 'visible' : ''}`}
      >
        <div className="visualization-container">
          <div className="visualization-header">
            <h2 className="visualization-title">System Intelligence Flow</h2>
            <p className="visualization-subtitle">
              See how your inputs transform into optimized floor plans through our AI pipeline
            </p>
          </div>
          <SystemVisualization />
        </div>
      </section>

      {/* How It Works Section - Pipeline Stepper */}
      <section className="how-it-works-section-new" id="how-it-works">
        <div className="how-it-works-container-new">
          <div className="how-it-works-header-new">
            <h2 className="how-it-works-title-new">How It Works</h2>
            <p className="how-it-works-subtitle-new">
              Our AI engine combines multiple reasoning layers to deliver optimal results
            </p>
          </div>
          <PipelineStepper />
        </div>
      </section>

      {/* CTA Section */}
      <section 
        ref={ctaRef}
        className={`cta-section-new ${ctaVisible ? 'visible' : ''}`}
      >
        <div className="cta-container-new">
          <div className="cta-content-new">
            <div className="cta-badge-new">Ready to Get Started?</div>
            <h2 className="cta-title-new">Generate Your Perfect Floor Plan</h2>
            <p className="cta-description-new">
              Transform your plot into a compliant, optimized residential layout in minutes.
              Our AI understands regulations, spatial efficiency, and traditional principles.
            </p>
            <Link to="/generate" className="cta-button-new">
              Create Floor Plan Now
            </Link>
            <p className="cta-note-new">No sign-up required • Instant results</p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Home
