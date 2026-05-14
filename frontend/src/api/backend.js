export async function generateFloorPlan(data) {
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
  
  const response = await fetch(`${backendUrl}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error('Failed to generate floor plan')
  }

  return response.json()
}

