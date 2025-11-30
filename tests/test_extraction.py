"""
Simple test script to extract audio features locally.

Usage:
    python tests/test_extraction.py <path_to_audio_file>

Example:
    python tests/test_extraction.py test_audio/song.mp3
"""

import sys
from pathlib import Path

# Add backend to path so we can import features
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.features import extract_features


def main():
    if len(sys.argv) < 2:
        print("Usage: python tests/test_extraction.py <audio_file>")
        print("\nExample: python tests/test_extraction.py test_audio/song.mp3")
        sys.exit(1)

    audio_file = sys.argv[1]

    # Check if file exists
    if not Path(audio_file).exists():
        print(f"Error: File not found: {audio_file}")
        sys.exit(1)

    print(f"Analyzing: {audio_file}")
    print("-" * 50)

    try:
        features = extract_features(audio_file)

        print("\nExtracted Features:")
        print(f"  Tempo:  {features['tempo']} BPM")
        print(f"  Key:    {features['key']} {features['mode']}")
        print(f"  Energy: {features['energy']}")
        print("-" * 50)

        # Interpret results
        print("\nInterpretation:")
        if features['tempo'] > 140:
            print("  - Fast tempo (energetic)")
        elif features['tempo'] < 80:
            print("  - Slow tempo (calm/relaxed)")
        else:
            print("  - Moderate tempo")

        if features['mode'] == 'major':
            print("  - Major key")
        else:
            print("  - Minor key")

        # Display Gemini analysis
        if "analysis" in features:
            print("\n" + "=" * 50)
            print("GEMINI ANALYSIS")
            print("=" * 50)
            print(features['analysis'])
            print("=" * 50)

    except Exception as e:
        print(f"\nError during extraction: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
