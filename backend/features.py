import librosa
import numpy as np


def extract_features(file_path: str) -> dict:
    """
    Extract audio features from an audio file.

    Args:
        file_path: Path to audio file (mp3, wav, etc.)

    Returns:
        Dictionary with tempo, key, and mode
    """
    # Load audio file
    y, sr = librosa.load(file_path)

    # Extract features
    tempo = extract_tempo(y, sr)
    key_info = extract_key(y, sr)

    return {
        "tempo": tempo,
        "key": key_info['key'],
        "mode": key_info['mode']
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

