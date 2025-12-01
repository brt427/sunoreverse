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

# Prompt version to use (v1 or v2)
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v2")


def load_prompt(version="v2"):
    """Load prompt from file"""
    prompt_dir = Path(__file__).parent / "prompts"
    prompt_file = prompt_dir / f"suno_{version}.txt"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    return prompt_file.read_text()


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

        # 3. Initialize the Vibe Reader (Gemini 2.0 Flash is fastest/cheapest)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # 4. Load the Suno-Optimized Prompt
        prompt = load_prompt(PROMPT_VERSION)

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

            # Normalize v3 format to match v1/v2 structure for backward compatibility
            if PROMPT_VERSION == "v3" and "style_of_music" in analysis_data:
                # v3 has different structure, create a compatible wrapper
                return {
                    "genre": analysis_data.get("style_of_music", ""),
                    "mood": analysis_data.get("mood", ""),  # v3 now includes mood field
                    "instrumentation": "",  # In sections
                    "production": "",  # In sections
                    "tempo_descriptor": "",  # In style_of_music
                    "vocal_style": "",  # In sections
                    "structure_tags": "",
                    "prompt": analysis_data.get("combined_prompt", ""),
                    "sections": analysis_data.get("sections", []),  # v3 specific
                    "style_of_music": analysis_data.get("style_of_music", "")  # v3 specific
                }

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
