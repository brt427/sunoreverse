import os
import time
import json
import re
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


def configure_genai():
    """Sets up the Google Gemini SDK"""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "CRITICAL: GEMINI_API_KEY not found in environment variables.\n"
            "Please create a .env file with your API key.\n"
            "See .env.example for reference."
        )

    genai.configure(api_key=api_key)


def analyze_audio(audio_path):
    """
    Analyze audio using Google Gemini API.

    Args:
        audio_path: Path to audio file

    Returns:
        str: Suno-optimized music description
    """
    if not os.path.exists(audio_path):
        return f"Error: File not found at {audio_path}"

    try:
        configure_genai()

        print(f"Uploading {os.path.basename(audio_path)} to Gemini...")

        # 1. Upload the file to Google's temporary storage
        audio_file = genai.upload_file(audio_path)

        # 2. Wait for processing (usually instant for MP3s, but good practice)
        while audio_file.state.name == "PROCESSING":
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)

        if audio_file.state.name == "FAILED":
            return "Error: Google failed to process the audio file."

        print("Analyzing Vibe...")

        # 3. Initialize the Vibe Reader (Gemini 1.5 Flash is fastest/cheapest)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # 4. The "Suno-Optimized" Prompt
        prompt = """
        You are an expert music curator analyzing this audio for AI music generation.

        Analyze this track and extract the following:
        1. GENRE: Be hyper-specific. Include era (e.g., "1980s Synth Pop" not just "Pop"). Use sub-genres and fusion when relevant.
        2. MOOD: Precise emotional descriptors (e.g., "melancholic", "euphoric", "gritty").
        3. INSTRUMENTATION: List 2-3 core instruments with TIMBRAL ADJECTIVES (e.g., "distorted guitar" not "guitar", "felt piano" not "piano").
        4. PRODUCTION: Describe the mix quality/texture (e.g., "lo-fi", "polished", "reverb-heavy", "compressed").
        5. TEMPO_DESCRIPTOR: Use words like "slow", "mid-tempo", "fast-paced", "driving" (NOT numeric BPM).
        6. VOCAL_STYLE: If vocals present, describe delivery (e.g., "raspy male vocals", "Auto-tuned female vocals", "choir harmonies"). If instrumental, say "Instrumental".
        7. PROMPT: Combine all of the above into a single Suno-style prompt string using this format:
           "[GENRE], [MOOD], [TEMPO_DESCRIPTOR], featuring [INSTRUMENTATION], [PRODUCTION], [VOCAL_STYLE]"

        Output ONLY valid JSON in this exact format:
        {
          "genre": "string",
          "mood": "string",
          "instrumentation": "string",
          "production": "string",
          "tempo_descriptor": "string",
          "vocal_style": "string",
          "prompt": "string"
        }

        Example:
        {
          "genre": "1990s Trip Hop",
          "mood": "dark and atmospheric",
          "instrumentation": "dusty vinyl samples, muted trumpet, deep sub-bass",
          "production": "lo-fi with vinyl crackle",
          "tempo_descriptor": "slow downtempo",
          "vocal_style": "breathy female vocals",
          "prompt": "1990s Trip Hop, dark and atmospheric, slow downtempo, featuring dusty vinyl samples, muted trumpet, deep sub-bass, lo-fi with vinyl crackle, breathy female vocals"
        }

        Do NOT include numeric BPM or musical key. Output ONLY the JSON, no other text.
        """

        # 5. Generate
        response = model.generate_content([prompt, audio_file])

        # Cleanup: Delete the file from cloud storage to keep it clean
        audio_file.delete()

        # Parse JSON response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)

        # Try to parse JSON
        try:
            analysis_data = json.loads(response_text)
            return analysis_data
        except json.JSONDecodeError as json_err:
            # If JSON parsing fails, return raw text wrapped in dict
            print(f"Warning: Could not parse JSON response: {json_err}")
            return {
                "error": "JSON parsing failed",
                "raw_response": response_text
            }

    except Exception as e:
        return {"error": f"Gemini Error: {str(e)}"}


# Test Block
if __name__ == "__main__":
    # Point this to your happy.mp3
    test_file = "/Users/blakethomas/Desktop/audiomood/audiomood/audioFiles/happy.mp3"

    print("\n" + "="*40)
    print(analyze_audio(test_file))
    print("="*40 + "\n")
