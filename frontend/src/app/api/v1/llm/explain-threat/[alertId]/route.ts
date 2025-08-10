import { NextResponse } from 'next/server'

// Use localhost when running locally, backend when in Docker
const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 
                   process.env.NEXT_PUBLIC_API_URL || 
                   'http://localhost:8000'

export async function GET(
  request: Request,
  { params }: { params: { alertId: string } }
) {
  try {
    const { alertId } = params
    
    const response = await fetch(`${BACKEND_URL}/api/v1/llm/explain-threat/${alertId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store'
    })

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying threat explanation request:', error)
    
    return NextResponse.json(
      { 
        error: 'Failed to explain threat',
        alert_id: params.alertId,
        explanation: {
          summary: 'Unable to generate explanation at this time',
          details: 'The LLM service encountered an error',
          risk_level: 'unknown',
          impact: 'Could not assess impact',
          recommendations: 'Please try again later'
        }
      },
      { status: 500 }
    )
  }
}
