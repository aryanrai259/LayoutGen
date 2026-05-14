import React, { useEffect, useRef, useState } from 'react'
import { Ruler, Brain, Layout } from 'lucide-react'
import './PipelineStepper.css'

function PipelineStepper() {
  const [activeStep, setActiveStep] = useState(0)
  const [isVisible, setIsVisible] = useState(false)
  const sectionRef = useRef(null)

  const steps = [
    {
      number: 1,
      title: 'Input Constraints',
      description: 'Plot size, orientation, and requirements',
      icon: Ruler
    },
    {
      number: 2,
      title: 'AI Reasoning Engine',
      description: 'Rules + retrieval + optimization',
      icon: Brain
    },
    {
      number: 3,
      title: 'Generated Layout',
      description: 'Preview-ready floor plans',
      icon: Layout
    }
  ]

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true)
            // Animate steps sequentially
            steps.forEach((_, index) => {
              setTimeout(() => {
                setActiveStep(index)
              }, index * 300)
            })
          }
        })
      },
      { threshold: 0.3 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current)
      }
    }
  }, [])

  return (
    <div ref={sectionRef} className="pipeline-stepper">
      <div className="pipeline-steps">
        {steps.map((step, index) => (
          <React.Fragment key={step.number}>
            <div
              className={`pipeline-step ${isVisible && index <= activeStep ? 'active' : ''} ${index === activeStep ? 'current' : ''}`}
            >
              <div className="pipeline-step-node">
                <div className="pipeline-step-icon">
                  {React.createElement(step.icon, { size: 20 })}
                </div>
                <div className="pipeline-step-number">{step.number}</div>
                <div className="pipeline-step-pulse"></div>
              </div>
              <div className="pipeline-step-content">
                <h3 className="pipeline-step-title">{step.title}</h3>
                <p className="pipeline-step-description">{step.description}</p>
              </div>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`pipeline-connector ${isVisible && index < activeStep ? 'filled' : ''}`}
              >
                <div className="pipeline-connector-line"></div>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}

export default PipelineStepper
