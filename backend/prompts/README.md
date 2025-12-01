# AudioMood Prompts

This directory contains prompt templates for the Gemini API audio analysis.

## Available Prompts

### `suno_v1.txt` (Original)
- Simple 7-field structure
- Basic genre, mood, instrumentation
- Good baseline performance

### `suno_v2.txt` (Suno Tag Bank Optimized)
- 8-field structure with `structure_tags`
- Uses Suno's tag bank vocabulary
- Includes structure markers ([Intro], [Verse], [Chorus], [Drop], etc.)
- Softer guidance: PREFER tag bank terms, but allows unique instruments

### `suno_v3.txt` (Section-by-Section Analysis) **NEW**
- Temporal analysis: Breaks song into sections
- Outputs array of sections with instrumentation details
- Two outputs: `style_of_music` (120 char) + `combined_prompt`
- Best for: Creating detailed Suno custom lyrics with section tags
- More context usage, but highly detailed

## Switching Between Prompts

Edit `.env` in project root:

```env
# Use v1 (original)
PROMPT_VERSION=v1

# Use v2 (Suno optimized)
PROMPT_VERSION=v2
```

Then restart the backend server.

## Creating New Prompts

1. Create new file: `backend/prompts/suno_v3.txt`
2. Write your prompt template
3. Update `.env`: `PROMPT_VERSION=v3`
4. Update TypeScript interfaces if JSON structure changes

## Prompt Guidelines

- Keep prompts under ~500 tokens (Gemini cost)
- Always output JSON only
- Include clear examples
- Use "PREFER" not "ONLY" for vocabulary constraints
- Test with diverse audio samples

## JSON Structure

**v1 Fields:**
```json
{
  "genre": "string",
  "mood": "string",
  "instrumentation": "string",
  "production": "string",
  "tempo_descriptor": "string",
  "vocal_style": "string",
  "prompt": "string"
}
```

**v2 Fields (adds structure_tags):**
```json
{
  "genre": "string",
  "mood": "string",
  "instrumentation": "string",
  "production": "string",
  "tempo_descriptor": "string",
  "vocal_style": "string",
  "structure_tags": "string",
  "prompt": "string"
}
```

## Testing

Test prompts with:
```bash
python tests/test_features.py audio_samples/happy.mp3
```

Compare outputs from v1 vs v2.
