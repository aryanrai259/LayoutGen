import React, { useState } from 'react'
import './InputForm.css'

const DEFAULT_ROOM_TYPES = ['living_room', 'bedroom', 'kitchen', 'bathroom']

function InputForm({ onSubmit, isGenerating = false, onDirectGenerate }) {
  const [formData, setFormData] = useState({
    description: '',
    width: 30,
    height: 40,
    rooms: 3,
    orientation: 'north',
    room_types: [...DEFAULT_ROOM_TYPES],
    jurisdiction: 'residential'
  })

  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value, type } = e.target
    
    if (type === 'checkbox') {
      const checked = e.target.checked
      const roomType = value
      setFormData(prev => ({
        ...prev,
        room_types: checked
          ? [...prev.room_types, roomType]
          : prev.room_types.filter(rt => rt !== roomType)
      }))
    } else {
      const newValue = type === 'number' ? parseFloat(value) || 0 : value
      setFormData(prev => ({
        ...prev,
        [name]: newValue
      }))
    }

    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const validate = () => {
    const newErrors = {}

    if (!formData.description || formData.description.trim().length < 10) {
      newErrors.description = 'Description must be at least 10 characters'
    }

    if (!formData.width || formData.width <= 0) {
      newErrors.width = 'Width must be greater than 0'
    }

    if (!formData.height || formData.height <= 0) {
      newErrors.height = 'Height must be greater than 0'
    }

    if (!formData.rooms || formData.rooms < 1 || formData.rooms > 20) {
      newErrors.rooms = 'Rooms must be between 1 and 20'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const isFormValid = () => {
    return formData.description.trim().length >= 10 &&
           formData.width > 0 &&
           formData.height > 0 &&
           formData.rooms >= 1 &&
           formData.rooms <= 20
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validate() && onSubmit) {
      onSubmit(formData)
    }
  }

  const handleDirectGenerate = () => {
    if (validate() && onDirectGenerate) {
      onDirectGenerate(formData)
    }
  }

  return (
    <form className="input-form input-form-idle-layout" onSubmit={handleSubmit}>
      {/* Two Column Layout for Idle State */}
      <div className="input-form-grid-idle">
        {/* Left/Center: Description Section */}
        <div className="input-form-description-column">
          <div className="form-section form-section-description">
            <div className="form-section-header">
              <h2 className="form-section-title">Describe Your Floor Plan</h2>
            </div>
            <div className="form-section-content">
              <div className="form-group">
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  className={`form-textarea form-textarea-large ${errors.description ? 'form-input-error' : ''}`}
                  placeholder="e.g., 3bhk house with 3 washrooms, open living-dining area, separate kitchen, good ventilation, and vastu-compliant bedroom placement"
                  rows="8"
                  required
                />
                {errors.description && (
                  <span className="form-error">{errors.description}</span>
                )}
                <span className="form-hint">
                  Minimum 10 characters. Include details about room types, layout preferences, and special requirements.
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Other Fields Sidebar */}
        <div className="input-form-sidebar-column">
          {/* Dimensions Section */}
          <div className="form-section form-section-sidebar">
            <div className="form-section-header">
              <h2 className="form-section-title">Dimensions</h2>
            </div>
            <div className="form-section-content">
              <div className="form-group">
                <label htmlFor="width" className="form-label">
                  Width
                </label>
                <div className="input-wrapper">
                  <input
                    type="number"
                    id="width"
                    name="width"
                    value={formData.width}
                    onChange={handleChange}
                    className={`form-input ${errors.width ? 'form-input-error' : ''}`}
                    placeholder="30"
                    min="0.1"
                    step="0.1"
                    required
                  />
                  <span className="input-unit">ft</span>
                </div>
                {errors.width && (
                  <span className="form-error">{errors.width}</span>
                )}
              </div>
              <div className="form-group">
                <label htmlFor="height" className="form-label">
                  Height
                </label>
                <div className="input-wrapper">
                  <input
                    type="number"
                    id="height"
                    name="height"
                    value={formData.height}
                    onChange={handleChange}
                    className={`form-input ${errors.height ? 'form-input-error' : ''}`}
                    placeholder="40"
                    min="0.1"
                    step="0.1"
                    required
                  />
                  <span className="input-unit">ft</span>
                </div>
                {errors.height && (
                  <span className="form-error">{errors.height}</span>
                )}
              </div>
            </div>
          </div>

          {/* Requirements Section */}
          <div className="form-section form-section-sidebar">
            <div className="form-section-header">
              <h2 className="form-section-title">Requirements</h2>
            </div>
            <div className="form-section-content">
              <div className="form-group">
                <label htmlFor="rooms" className="form-label">
                  Number of Rooms
                </label>
                <input
                  type="number"
                  id="rooms"
                  name="rooms"
                  value={formData.rooms}
                  onChange={handleChange}
                  className={`form-input ${errors.rooms ? 'form-input-error' : ''}`}
                  placeholder="3"
                  min="1"
                  max="20"
                  required
                />
                {errors.rooms && (
                  <span className="form-error">{errors.rooms}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="orientation" className="form-label">
                  Orientation
                </label>
                <select
                  id="orientation"
                  name="orientation"
                  value={formData.orientation}
                  onChange={handleChange}
                  className="form-select"
                  required
                >
                  <option value="north">North</option>
                  <option value="south">South</option>
                  <option value="east">East</option>
                  <option value="west">West</option>
                </select>
              </div>
            </div>
          </div>

          {/* Room Types Section */}
          <div className="form-section form-section-sidebar">
            <div className="form-section-header">
              <h2 className="form-section-title">Room Types</h2>
            </div>
            <div className="form-section-content">
              <div className="form-checkbox-group">
                {['living_room', 'bedroom', 'kitchen', 'bathroom', 'dining_room', 'study', 'balcony'].map((roomType) => (
                  <label key={roomType} className="form-checkbox-label">
                    <input
                      type="checkbox"
                      className="form-checkbox"
                      value={roomType}
                      checked={formData.room_types.includes(roomType)}
                      onChange={handleChange}
                    />
                    <span className="form-checkbox-text">
                      {roomType.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Jurisdiction Section */}
          <div className="form-section form-section-sidebar">
            <div className="form-section-header">
              <h2 className="form-section-title">Jurisdiction</h2>
            </div>
            <div className="form-section-content">
              <div className="form-group">
                <input
                  type="text"
                  id="jurisdiction"
                  name="jurisdiction"
                  value={formData.jurisdiction}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="residential"
                  required
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Generate Buttons - Below both columns */}
      <div className="form-actions form-actions-idle">
        <button 
          type="submit" 
          className="form-submit-btn form-submit-btn-primary"
          disabled={!isFormValid() || isGenerating}
        >
          {isGenerating ? 'Generating...' : 'Generate with Streaming'}
        </button>
        <button 
          type="button" 
          className="form-submit-btn form-submit-btn-secondary"
          onClick={handleDirectGenerate}
          disabled={!isFormValid() || isGenerating}
        >
          Quick Generate
        </button>
      </div>
    </form>
  )
}

export default InputForm
