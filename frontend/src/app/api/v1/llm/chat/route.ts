import { NextResponse } from 'next/server'

// Use localhost when running locally, backend when in Docker  
const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 
                   process.env.NEXT_PUBLIC_API_URL || 
                   'http://localhost:8000'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${BACKEND_URL}/api/v1/llm/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      cache: 'no-store'
    })

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying LLM chat request:', error)
    
    return NextResponse.json(
      { 
        error: 'Failed to process chat request',
        response: 'Sorry, I encountered an error processing your message. Please try again.'
      },
      { status: 500 }
    )
  }
}
