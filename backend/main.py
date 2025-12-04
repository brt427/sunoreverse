"""
AudioMood FastAPI Backend

HTTP API for audio feature extraction and analysis.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .features import extract_features


# Initialize FastAPI app
app = FastAPI(
    title="AudioMood API",
    description="Extract audio features and generate AI music prompts",
    version="1.0.0"
)

# Initialize rate limiter (8 requests per day per IP)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.

    Returns:
        Status message
    """
    return {"status": "ok"}


@app.post("/api/analyze")
@limiter.limit("8/day")
async def analyze_audio(request: Request, file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze an audio file and extract features.

    Rate limit: 8 requests per day per IP address.

    Args:
        request: FastAPI request object (for rate limiting)
        file: Uploaded audio file (MP3, WAV, FLAC, etc.)

    Returns:
        Dictionary with tempo, key, mode, energy, and AI analysis

    Raises:
        HTTPException: If file validation fails or processing error occurs
        RateLimitExceeded: If rate limit (8/day) is exceeded
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read file: {str(e)}"
        )

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / (1024 * 1024)} MB"
        )

    # Save to temporary file
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(content)
            temp_file = tmp.name

        # Extract features
        result = extract_features(temp_file)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )

    finally:
        # Cleanup temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception:
                pass  # Ignore cleanup errors


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
