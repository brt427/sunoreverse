import librosa
import numpy as np
from .audio_llm import analyze_audio


def extract_features(file_path: str) -> dict:
    """
    Extract audio features from an audio file.

    Args:
        file_path: Path to audio file (mp3, wav, etc.)

    Returns:
        Dictionary with tempo, key, mode, energy, and Gemini analysis
    """
    # Load audio file
    y, sr = librosa.load(file_path)

    # Extract librosa features
    tempo = extract_tempo(y, sr)
    key_info = extract_key(y, sr)
    energy = extract_energy(y, sr)

    # Extract Gemini analysis
    analysis = analyze_audio(file_path)

    # Append librosa BPM and key to the final prompt
    if "prompt" in analysis:
        key_mode = f"{key_info['key']} {key_info['mode']}"
        analysis["prompt"] = f"{analysis['prompt']}, {key_mode}, {tempo} bpm"

    return {
        "tempo": tempo,
        "key": key_info['key'],
        "mode": key_info['mode'],
        "energy": energy,
        "analysis": analysis
    }



def extract_tempo(y, sr):
    """
    Extract tempo (BPM) from audio, rounded to nearest 5.

    Args:
        y: Audio time series
        sr: Sample rate

    Returns:
        int: Tempo in beats per minute (rounded to nearest 5)
    """
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    # Round to nearest 5 BPM
    tempo = round(float(tempo) / 5) * 5
    return int(tempo)


def extract_key(y, sr):
    """
    Extract musical key and mode using Krumhansl-Schmuckler algorithm.

    Args:
        y: Audio time series
        sr: Sample rate

    Returns:
        dict: {'key': str, 'mode': str}
    """
    # Krumhansl-Kessler key profiles
    # Major and minor key profiles based on empirical studies
    MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    
    # Get chromagram (pitch class profile)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    # Average chroma over time to get pitch class distribution
    chroma_mean = np.mean(chroma, axis=1)

    # Normalize the chroma vector
    chroma_mean = chroma_mean / np.sum(chroma_mean)

    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Test all 24 possible keys (12 major + 12 minor)
    max_correlation = -1
    best_key = 'C'
    best_mode = 'major'

    for i in range(12):
        # Rotate the profile to match each key
        major_profile_rotated = np.roll(MAJOR_PROFILE, i)
        minor_profile_rotated = np.roll(MINOR_PROFILE, i)

        # Calculate correlation
        major_corr = np.corrcoef(chroma_mean, major_profile_rotated)[0, 1]
        minor_corr = np.corrcoef(chroma_mean, minor_profile_rotated)[0, 1]

        # Check if this is the best match so far
        if major_corr > max_correlation:
            max_correlation = major_corr
            best_key = keys[i]
            best_mode = 'major'

        if minor_corr > max_correlation:
            max_correlation = minor_corr
            best_key = keys[i]
            best_mode = 'minor'

    return {
        'key': best_key,
        'mode': best_mode
    }


def extract_energy(y, sr):
    """
    Extract energy level using RMS (Root Mean Square).

    Args:
        y: Audio time series
        sr: Sample rate

    Returns:
        float: Energy level from 0.0 (quiet) to 1.0 (loud)
    """
    # Calculate RMS energy
    rms = librosa.feature.rms(y=y)

    # Get mean energy across the entire track
    energy_mean = float(np.mean(rms))

    # Use a more reasonable normalization based on typical RMS ranges
    # Most music has RMS between 0.01-0.3
    # Map 0.0-0.25 to 0.0-1.0
    energy = min(1.0, energy_mean / 0.25)

    return round(energy, 2)

