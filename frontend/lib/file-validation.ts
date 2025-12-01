const ALLOWED_TYPES = [
  'audio/mpeg',        // MP3
  'audio/wav',         // WAV
  'audio/x-wav',       // WAV (alternative MIME)
  'audio/flac',        // FLAC
  'audio/ogg',         // OGG
  'audio/aac',         // AAC
  'audio/mp4',         // M4A
  'audio/x-m4a',       // M4A (alternative)
]

const ALLOWED_EXTENSIONS = ['.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a']
const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50 MB

export interface ValidationResult {
  valid: boolean
  error?: string
}

export function validateAudioFile(file: File): ValidationResult {
  // Check if file exists
  if (!file) {
    return { valid: false, error: 'No file selected' }
  }

  // Check file size
  if (file.size === 0) {
    return { valid: false, error: 'File is empty' }
  }

  if (file.size > MAX_FILE_SIZE) {
    const sizeMB = (MAX_FILE_SIZE / (1024 * 1024)).toFixed(0)
    return { valid: false, error: `File too large. Maximum size is ${sizeMB}MB` }
  }

  // Check MIME type
  if (file.type && !ALLOWED_TYPES.includes(file.type)) {
    return { valid: false, error: 'Invalid file type. Please upload an audio file (MP3, WAV, FLAC, etc.)' }
  }

  // Check file extension (fallback if MIME type is not set)
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return { valid: false, error: 'Invalid file extension. Supported formats: MP3, WAV, FLAC, OGG, AAC, M4A' }
  }

  return { valid: true }
}

export function sanitizeFilename(filename: string): string {
  // Remove path separators and limit length
  return filename.replace(/[\/\\]/g, '').slice(0, 100)
}
