import { NextResponse } from 'next/server'

// Use localhost when running locally, backend when in Docker
const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 
                   process.env.NEXT_PUBLIC_API_URL || 
                   'http://localhost:8000'

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/llm/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add cache control to prevent stale responses
      cache: 'no-store'
    })

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying LLM status request:', error)
    
    return NextResponse.json(
      { 
        available: false,
        provider: "groq",
        model: "llama3-8b-8192", 
        features: [],
        error: 'Failed to connect to backend LLM service'
      },
      { status: 500 }
    )
  }
}
