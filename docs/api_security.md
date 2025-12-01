# API Security & Protection Guide

Protecting your Gemini API from abuse before deployment.

---

## The Threat

Right now, anyone can:
```bash
curl -X POST http://yourdomain.com/api/analyze -F "file=@song.mp3"
```

At ~$0.001-0.01 per song, someone could:
- Upload 10,000 songs = $10-100 in API costs
- Automate it with a script = Unlimited abuse

---

## Protection Strategies (Ranked by Effectiveness)

### 1. API Key (Simplest)

Require a secret key in the request header.

**Implementation:**
```python
from fastapi import Header, HTTPException
import os

API_KEY = os.getenv("AUDIOMOOD_API_KEY")  # Set in .env

@app.post("/api/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    x_api_key: str = Header(...)  # Require header
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of code
```

**Usage:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "X-API-Key: your-secret-key" \
  -F "file=@song.mp3"
```

**Pros:**
- Takes 5 minutes to implement
- Stops casual abuse
- No database needed
- Simple to understand

**Cons:**
- If someone gets your key, they can abuse it
- Can't track individual users
- No usage limits per user
- Key could leak in frontend code

**Time to implement:** 5 minutes

---

### 2. Rate Limiting (Medium)

Limit requests per IP address.

**Installation:**
```bash
pip install slowapi
```

**Implementation:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/analyze")
@limiter.limit("10/day")  # Max 10 requests per IP per day
async def analyze_audio(request: Request, file: UploadFile = File(...)):
    # ... your code
```

**Configuration options:**
- `"10/day"` - 10 requests per day
- `"5/hour"` - 5 requests per hour
- `"1/minute"` - 1 request per minute

**Pros:**
- Prevents mass abuse
- No user accounts needed
- Works per IP address
- Easy to configure limits

**Cons:**
- Users behind same IP share the limit (office buildings, cafes)
- Can be bypassed with VPN/proxies
- Legitimate users get frustrated if they hit limit
- Hard to make exceptions for power users

**Time to implement:** 10 minutes

---

### 3. Supabase Auth (Best for Production)

Require users to log in (Google OAuth, email, etc.).

**Installation:**
```bash
pip install supabase
```

**Backend Implementation:**
```python
from fastapi import Depends
from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def verify_user(authorization: str = Header(...)):
    """Verify JWT token from Supabase"""
    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)
        return user
    except:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/api/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    user = Depends(verify_user)  # Must be logged in
):
    # Track usage per user in database
    # Enforce per-user limits (e.g., 5 free analyses, then pay)
    user_id = user.id

    # Check usage in database
    usage = supabase.table("usage").select("*").eq("user_id", user_id).execute()

    # Your business logic here
    # ...
```

**Frontend Setup (Next.js example):**
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Login with Google
async function signInWithGoogle() {
  await supabase.auth.signInWithOAuth({ provider: 'google' })
}

// Upload audio with auth
async function analyzeAudio(file) {
  const { data: { session } } = await supabase.auth.getSession()

  const response = await fetch('http://localhost:8000/api/analyze', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${session.access_token}`
    },
    body: formData
  })
}
```

**Pros:**
- Track individual users
- Can implement freemium (5 free, then $5/month)
- Can ban abusers by user ID
- Professional UX
- Users can see their usage history
- Supports multiple auth providers (Google, GitHub, Email)

**Cons:**
- More complex to implement
- Need to build login UI in frontend
- Requires database for user tracking
- More moving parts = more things to debug

**Time to implement:** 1-2 days

---

### 4. Cloudflare (Bonus Layer)

Put Cloudflare in front of your API.

**Setup:**
1. Sign up for Cloudflare (free tier)
2. Point your domain to Cloudflare nameservers
3. Enable:
   - DDoS protection
   - Bot detection
   - Rate limiting rules
   - WAF (Web Application Firewall)

**Features:**
- DDoS protection (stops massive automated attacks)
- Bot detection (blocks suspicious traffic)
- Rate limiting at CDN level (before hitting your server)
- Cache responses (if same song uploaded twice)
- Analytics dashboard

**Cloudflare Rate Limiting Example:**
```
Rule: Block if > 10 requests per minute from same IP to /api/analyze
Action: Return 429 Too Many Requests
```

**Pros:**
- Free tier available
- Stops attacks before they hit your server
- Professional-grade protection
- Analytics included
- SSL/TLS certificates included

**Cons:**
- Adds complexity to deployment
- Audio files don't cache well (unique uploads)
- Need to own a domain
- Learning curve for configuration

**Time to implement:** 30 minutes (if you have a domain)

---

## Recommended Approach

### For MVP (Launch This Week)

```
API Key + Rate Limiting
```

**Implementation:**
1. Add API key check (5 min)
2. Add rate limiting: 10 requests/IP/day (10 min)
3. **Total: 15 minutes**
4. **Blocks 95% of abuse**

**Code:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Header, HTTPException
import os

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API key from environment
API_KEY = os.getenv("AUDIOMOOD_API_KEY")

@app.post("/api/analyze")
@limiter.limit("10/day")
async def analyze_audio(
    request: Request,
    file: UploadFile = File(...),
    x_api_key: str = Header(...)
):
    # Verify API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # ... rest of your code
```

**.env:**
```
AUDIOMOOD_API_KEY=your-random-secret-key-here-make-it-long
GEMINI_API_KEY=your-gemini-key
```

---

### For Production (After You Get Users)

```
Supabase Auth + Rate Limiting + Cloudflare
```

**Stack:**
- User accounts with Google/GitHub login (Supabase)
- Track usage per user in database
- Freemium model: 5 free analyses, then $5/month
- Cloudflare for DDoS protection
- Rate limiting: 50 requests/day for free users, unlimited for paid

**Business Logic:**
```python
# Check if user has remaining credits
async def check_user_credits(user_id: str):
    usage = supabase.table("usage").select("*").eq("user_id", user_id).execute()

    if usage.data[0]["tier"] == "free" and usage.data[0]["count"] >= 5:
        raise HTTPException(402, "Free tier limit reached. Upgrade to continue.")

    # Increment usage counter
    supabase.table("usage").update({"count": usage.data[0]["count"] + 1}).eq("user_id", user_id).execute()
```

---

## Quick Wins You Can Do Right Now

### Option A: Environment-Based API Key

Add to `.env`:
```
AUDIOMOOD_API_KEY=some-random-secret-string-here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

Update CORS in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Only give the API key to your frontend. Random people won't know it.

---

### Option B: IP Whitelist (Nuclear Option)

Only allow requests from your frontend's IP:

```python
@app.middleware("http")
async def ip_whitelist(request: Request, call_next):
    client_ip = request.client.host
    allowed_ips = ["127.0.0.1", "your-frontend-server-ip"]

    if client_ip not in allowed_ips:
        raise HTTPException(403, "Forbidden")

    return await call_next(request)
```

**Warning:** This breaks if your frontend IP changes (which happens with most hosting providers).

---

### Option C: CORS Restriction Only

Not real security, but makes it harder for browsers to abuse:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Only your frontend
    allow_credentials=True,
    allow_methods=["POST"],  # Only POST, no GET
    allow_headers=["*"],
)
```

**Note:** This only protects against browser-based abuse. `curl` and scripts bypass CORS entirely.

---

## Cost Analysis

**Scenario: 1000 users/day, no protection**
- Gemini cost: $10-30/month
- Hosting: $5-10/month
- **Total: $15-40/month**

**Scenario: 1000 users/day WITH rate limiting (10/day)**
- Capped at 10,000 requests/day max (if every IP is unique)
- Gemini cost: Same, but predictable
- No surprise bills

**Scenario: Freemium with Supabase**
- 70% of users stay on free tier (5 analyses)
- 30% convert to paid ($5/month)
- **Revenue: 1000 users × 30% × $5 = $1,500/month**
- **Costs: $40/month (API) + $25/month (Supabase)**
- **Profit: $1,435/month**

---

## Summary Table

| Strategy | Time to Implement | Protection Level | Cost | Best For |
|----------|------------------|------------------|------|----------|
| API Key | 5 min | Low | $0 | Quick MVP |
| Rate Limiting | 10 min | Medium | $0 | MVP Launch |
| API Key + Rate Limiting | 15 min | High | $0 | **Recommended for MVP** |
| Supabase Auth | 1-2 days | Very High | $25/mo | Production |
| Cloudflare | 30 min | DDoS Protection | $0-20/mo | Scaling |
| Full Stack | 2-3 days | Enterprise | $50/mo | **Recommended for Production** |

---

## Next Steps

1. **Right now**: Implement API Key + Rate Limiting (15 min)
2. **Before launch**: Test with curl to verify protection works
3. **After first users**: Monitor Gemini API usage in Google Cloud Console
4. **If getting traction**: Implement Supabase auth + freemium model
5. **If viral**: Add Cloudflare

---

## Resources

- [Slowapi Documentation](https://github.com/laurentS/slowapi)
- [Supabase Auth Guide](https://supabase.com/docs/guides/auth)
- [FastAPI Security Tutorial](https://fastapi.tiangolo.com/tutorial/security/)
- [Cloudflare Rate Limiting](https://developers.cloudflare.com/waf/rate-limiting-rules/)
