const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface MusicAnalysis {
  tempo: number
  key: string
  mode: string
  energy: number
  analysis: {
    genre: string
    mood: string
    instrumentation: string
    production: string
    tempo_descriptor: string
    vocal_style: string
    structure_tags: string
    prompt: string
    // v3 specific fields (optional)
    sections?: Array<{
      name: string
      description: string
    }>
    style_of_music?: string
  }
}

export interface AnalysisError {
  error: string
  details?: string
}

export async function analyzeAudio(file: File): Promise<MusicAnalysis> {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${API_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
      // Add timeout using AbortController
      signal: AbortSignal.timeout(60000), // 60 second timeout
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    return response.json()
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        throw new Error('Request timed out. Please try again.')
      }
      if (error.message === 'Failed to fetch') {
        throw new Error('Cannot connect to server. Make sure the backend is running.')
      }
      throw error
    }
    throw new Error('An unexpected error occurred')
  }
}
