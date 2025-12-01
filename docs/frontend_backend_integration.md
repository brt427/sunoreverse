# Frontend-Backend Integration Plan

Plan for connecting Next.js frontend to FastAPI backend with security considerations.

---

## Overview

**Goal:** Connect the frontend file upload to the FastAPI `/api/analyze` endpoint while ensuring security and good UX.

**Flow:**
1. User uploads audio file in frontend
2. Frontend validates file (client-side)
3. Frontend sends file to FastAPI backend
4. Backend validates again (server-side - never trust client)
5. Backend processes with librosa + Gemini
6. Frontend displays results

---

## Security Considerations

### 1. File Type Validation

**Why:** Prevent users from uploading executables, scripts, or other malicious files.

**Client-side (Frontend):**
```typescript
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

function validateFile(file: File): { valid: boolean; error?: string } {
  // Check MIME type
  if (!ALLOWED_TYPES.includes(file.type)) {
    return { valid: false, error: 'Invalid file type. Please upload an audio file.' }
  }

  // Check file extension (some browsers don't set MIME correctly)
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return { valid: false, error: 'Invalid file extension.' }
  }

  return { valid: true }
}
```

**Server-side (Backend - Already Implemented):**
```python
# backend/main.py already has this
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}

file_ext = Path(file.filename).suffix.lower()
if file_ext not in ALLOWED_EXTENSIONS:
    raise HTTPException(status_code=400, detail="Invalid file type")
```

**Defense in depth:** Check on both client (fast feedback) and server (security).

---

### 2. File Size Limits

**Why:** Prevent DoS attacks from huge file uploads. Prevent excessive Gemini API costs.

**Client-side:**
```typescript
const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50 MB

function validateFileSize(file: File): { valid: boolean; error?: string } {
  if (file.size > MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `File too large. Max size: ${MAX_FILE_SIZE / (1024 * 1024)} MB`
    }
  }

  if (file.size === 0) {
    return { valid: false, error: 'File is empty' }
  }

  return { valid: true }
}
```

**Server-side (Backend - Already Implemented):**
```python
# backend/main.py already has this
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

if len(content) > MAX_FILE_SIZE:
    raise HTTPException(status_code=413, detail="File too large")
```

---

### 3. Malicious Filename Handling

**Why:** Filenames could contain XSS attacks or path traversal attempts.

**Client-side:**
```typescript
function sanitizeFilename(filename: string): string {
  // Remove path separators
  return filename.replace(/[\/\\]/g, '')
}

// When displaying filename
<span>{sanitizeFilename(file.name)}</span>
```

**Server-side (Backend - Already Implemented):**
```python
# We use tempfile.NamedTemporaryFile which generates safe filenames
# User's filename is never used in file paths
```

---

### 4. CORS Protection

**Backend (Already Configured):**
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev - change to specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production TODO:**
Change `allow_origins=["*"]` to your actual frontend domain:
```python
allow_origins=["https://yourdomain.com"]
```

---

### 5. API Key (Optional - Future)

**If you add API key protection:**

**Backend:**
```python
API_KEY = os.getenv("AUDIOMOOD_API_KEY")

@app.post("/api/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    x_api_key: str = Header(...)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

**Frontend:**
```typescript
// In .env.local (NEVER commit this file)
NEXT_PUBLIC_API_KEY=your-secret-key

// In API call
headers: {
  'X-API-Key': process.env.NEXT_PUBLIC_API_KEY
}
```

---

### 6. Rate Limiting (Future)

**Server-side with slowapi:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/analyze")
@limiter.limit("10/day")
async def analyze_audio(...):
    # Only 10 requests per IP per day
```

---

## Implementation Plan

### Step 1: Environment Variables

**Create `frontend/.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Add to `frontend/.gitignore` (check if already there):**
```
.env.local
.env*.local
```

**Create `frontend/.env.example`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### Step 2: Create API Service

**Create `frontend/lib/api.ts`:**
```typescript
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
    prompt: string
  }
}

export interface AnalysisError {
  error: string
  details?: string
}

export async function analyzeAudio(file: File): Promise<MusicAnalysis> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
    // If you add API key later:
    // headers: {
    //   'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || ''
    // }
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(errorData.detail || `HTTP ${response.status}`)
  }

  return response.json()
}
```

---

### Step 3: File Validation Utility

**Create `frontend/lib/file-validation.ts`:**
```typescript
const ALLOWED_TYPES = [
  'audio/mpeg',
  'audio/wav',
  'audio/x-wav',
  'audio/flac',
  'audio/ogg',
  'audio/aac',
  'audio/mp4',
  'audio/x-m4a',
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
```

---

### Step 4: Update analysis-form.tsx

**Replace mock analysis with real API call:**

```typescript
import { analyzeAudio } from "@/lib/api"
import { validateAudioFile, sanitizeFilename } from "@/lib/file-validation"

// Add error state
const [error, setError] = useState<string | null>(null)

const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setError(null) // Clear previous errors

  if (e.target.files?.[0]) {
    const selectedFile = e.target.files[0]

    // Validate file
    const validation = validateAudioFile(selectedFile)
    if (!validation.valid) {
      setError(validation.error || 'Invalid file')
      setFile(null)
      return
    }

    setFile(selectedFile)
  }
}

const handleAnalyze = async () => {
  if (!file) return

  setIsAnalyzing(true)
  setError(null)

  try {
    const result = await analyzeAudio(file)
    setAnalysis(result)
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to analyze audio')
  } finally {
    setIsAnalyzing(false)
  }
}

// Add error display in JSX
{error && (
  <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
    {error}
  </div>
)}
```

---

### Step 5: Error Handling Scenarios

**Handle different error types:**

1. **Network errors** (backend not running)
   ```
   Error: Failed to fetch
   Display: "Cannot connect to server. Please try again."
   ```

2. **File validation errors** (client-side)
   ```
   Display immediately: "File too large. Maximum size is 50MB"
   ```

3. **Backend validation errors** (400 status)
   ```
   Display: "Invalid file type. Please upload an audio file."
   ```

4. **Gemini API errors** (500 status)
   ```
   Display: "Error processing audio. Please try again."
   ```

5. **Timeout** (request takes too long)
   ```
   Add timeout to fetch:
   const controller = new AbortController()
   setTimeout(() => controller.abort(), 60000) // 60 second timeout

   fetch(url, { signal: controller.signal })
   ```

---

## Testing Checklist

### Client-Side Validation
- [ ] Upload non-audio file (e.g., .txt, .exe) → Should reject immediately
- [ ] Upload file > 50MB → Should reject immediately
- [ ] Upload empty file → Should reject
- [ ] Upload valid MP3 → Should accept

### Backend Integration
- [ ] Upload valid MP3 → Should analyze successfully
- [ ] Check Network tab in browser DevTools → Should see POST to `/api/analyze`
- [ ] Verify response contains all expected fields (tempo, key, mode, energy, analysis)

### Error Handling
- [ ] Stop backend server → Frontend should show connection error
- [ ] Upload corrupted audio file → Backend should reject gracefully
- [ ] Upload very long audio (>10 min) → Should handle processing time

### Security
- [ ] Try uploading .exe renamed to .mp3 → Should reject based on content type
- [ ] Try filename with path traversal (`../../../etc/passwd.mp3`) → Should sanitize
- [ ] Check CORS in Network tab → Should have proper headers

---

## Production Checklist

Before deploying:

1. **Environment Variables**
   - [ ] Set `NEXT_PUBLIC_API_URL` to production backend URL
   - [ ] Update CORS `allow_origins` in backend to production frontend URL

2. **Security**
   - [ ] Add API key protection (recommended)
   - [ ] Add rate limiting (10-50 requests/day)
   - [ ] Consider adding Cloudflare

3. **Error Tracking**
   - [ ] Add Sentry or similar for error monitoring
   - [ ] Log failed uploads for debugging

4. **Performance**
   - [ ] Add loading progress bar (if possible)
   - [ ] Add timeout handling (60 seconds)
   - [ ] Consider file compression before upload

---

## Implementation Order

**Do these in order:**

1. ✅ Create environment variable files (`.env.local`, `.env.example`)
2. ✅ Create `lib/file-validation.ts` with validation utilities
3. ✅ Create `lib/api.ts` with API service function
4. ✅ Update `analysis-form.tsx` to use real API
5. ✅ Test with backend running
6. ✅ Add error UI components
7. ✅ Test all error scenarios

**Time estimate:** 1-2 hours

---

## Notes

- **Never commit `.env.local`** - It contains API keys and secrets
- **Always validate on both client and server** - Defense in depth
- **Backend already has most security measures** - We're adding client-side UX
- **Start simple, add security later** - Get it working first, then add API keys/rate limiting

Ready to implement?
