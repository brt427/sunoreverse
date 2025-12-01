# AudioMood Deployment Roadmap

High-level roadmap to ship this to real users.

---

## Phase 1: Backend API (FastAPI)

**What you have:** Python scripts that run locally
**What you need:** HTTP API that accepts file uploads

```python
# backend/main.py (FastAPI)
from fastapi import FastAPI, UploadFile, File
from backend.features import extract_features
import tempfile

app = FastAPI()

@app.post("/api/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Extract features
    result = extract_features(tmp_path)

    # Cleanup
    os.unlink(tmp_path)

    return result

@app.get("/health")
def health():
    return {"status": "ok"}
```

**Time estimate:** 2-4 hours

---

## Phase 2: Frontend

### Option A: Simple HTML/JS (fastest)
- Drag-and-drop audio uploader
- Display results (tempo, key, Gemini analysis)
- Can deploy as static site

### Option B: React/Next.js (more polished)
- Better UX, animations
- State management
- Production-ready feel

### Key features:
1. File Upload UI
2. Loading state (Gemini takes ~3-5 seconds)
3. Results display:
   - Tempo: 160 BPM
   - Key: F minor
   - Energy: 0.72
   - Suno Prompt: [show the generated prompt]
4. Copy-to-clipboard button for Suno prompt

**Time estimate:** 1-2 days (simple), 3-5 days (polished)

---

## Phase 3: Deployment

### Backend Options:

#### Option A: Fly.io / Railway (easiest)
- Free tier available
- Auto-deploys from GitHub
- Handles Docker for you
- **Cost:** $0-5/month for low traffic

#### Option B: AWS Lambda / GCP Cloud Functions (cheapest at scale)
- Pay per request
- Need to handle cold starts
- **Cost:** ~$0.20 per 1000 requests

#### Option C: Vercel/Netlify serverless (fastest setup)
- Great for Next.js
- **Cost:** Free for hobby projects

### Frontend Options:

**Vercel / Netlify** (recommended)
- Free tier
- Auto-deploy from git
- CDN included
- **Cost:** $0

---

## Phase 4: Production Concerns

### 1. Cost Management (IMPORTANT)

**Current issue:** Gemini API costs
- Gemini Flash: ~$0.075 per 1M input tokens
- **Your audio uploads:** ~$0.001-0.01 per song analyzed

**With 1000 users/day:**
- Gemini cost: ~$10-30/month
- Hosting: ~$5-10/month
- **Total: $15-40/month**

**Mitigation:**
- Add rate limiting (max 10 uploads per IP/day)
- Require login (Google OAuth) to prevent abuse
- Consider freemium model (5 free analyses, then pay)

### 2. File Upload Size Limits
- Audio files are big (3-10 MB)
- Most serverless platforms have 10-50 MB limits
- You're good for normal songs

### 3. Processing Time
- Librosa: ~2-3 seconds
- Gemini upload + analysis: ~3-5 seconds
- **Total: 5-8 seconds per request**
- Show progress bar in frontend

### 4. Security
- Validate file types (only MP3, WAV, etc.)
- Scan for malware
- Set max file size (50 MB)
- Don't store user files (privacy)

---

## Recommended Tech Stack

```
Frontend:   Next.js (React) + Tailwind CSS
Backend:    FastAPI (Python)
Deployment: Vercel (frontend) + Railway (backend)
Database:   None needed (unless you add user accounts)
Auth:       Clerk / Supabase (if you need users)
```

---

## MVP Feature List (1 week timeline)

### Week 1: Core Product
1. Backend API (FastAPI) - 1 day
2. Simple frontend (file upload + results) - 2 days
3. Deploy to Vercel + Railway - 1 day
4. Add rate limiting - 0.5 days
5. Polish UI - 1 day

**What you'd have:** Working web app at `yourdomain.com` where users can upload audio and get Suno prompts.

---

## Biggest Risks

### 1. API Costs
**Risk:** Gemini bills can spike if someone abuses it
**Solution:** Auth + rate limiting from day 1

### 2. Gemini Accuracy
**Risk:** Sometimes returns bad JSON or weird analysis
**Solution:** Add fallback parsing, validate output

### 3. Scalability
**Risk:** Librosa is CPU-heavy
**Solution:** Use worker queues (Celery/Redis) if you get popular

---

## Next Steps

To start building the FastAPI backend:
1. Create `backend/main.py` with FastAPI app
2. Add CORS middleware for frontend communication
3. Test locally with `uvicorn backend.main:app --reload`
4. Build simple frontend that calls the API
5. Deploy when ready
