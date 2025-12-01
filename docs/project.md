# audiomood

## Goal
Extract audio features from a song, send to Claude, get a music AI prompt back.

## Stack
- FastAPI
- librosa (audio analysis)
- Anthropic API (prompt generation)

## Endpoints
- POST /analyze — upload audio, get prompt
- GET /health

## Features to Extract (v1)
- Tempo (BPM)
- Key + mode
- Energy (0-1)
- Valence (0-1)

## Out of Scope (for now)
- YouTube/Spotify URL input
- Batch processing
- Frontend
- Database/caching

## File Structure
- main.py — FastAPI app
- features.py — audio extraction
- prompt.py — Claude integration