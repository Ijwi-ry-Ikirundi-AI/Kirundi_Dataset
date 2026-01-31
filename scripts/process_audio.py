#!/usr/bin/env python3
"""
Audio Processing Pipeline for Kirundi Dataset
=============================================

This script processes raw audio recordings to meet the quality standards
required for STT/TTS model training.

Processing steps:
1. VAD (Voice Activity Detection) - Trim silence at start/end
2. Normalization - Unify volume levels
3. Denoising - Remove background noise

Audio specifications (from project guidelines):
- Format: WAV (16-bit PCM)
- Sample rate: 16kHz
- Channels: Mono
- Silence threshold: -30dB

Usage:
    python process_audio.py <input_file>
    python process_audio.py <input_file> --output <output_file>
    python process_audio.py --batch <input_folder> --output <output_folder>

Dependencies:
    pip install librosa soundfile noisereduce numpy scipy
"""

import os
import argparse
import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import librosa
import soundfile as sf

# Try to import noisereduce, provide helpful message if not installed
try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False
    print("⚠️  noisereduce not installed. Denoising will be skipped.")
    print("   Install with: pip install noisereduce")

# Configuration
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
CLIPS_DIR = BASE_DIR / "clips"
RAW_DIR = CLIPS_DIR / "raw"  # For unprocessed recordings

# Audio specifications (Whisper standard)
TARGET_SAMPLE_RATE = 16000  # 16kHz
TARGET_CHANNELS = 1  # Mono
SILENCE_THRESHOLD_DB = -30  # dB threshold for VAD
PEAK_NORMALIZE_DB = -0.1  # Target peak level

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
    """
    Load audio file and convert to mono if needed.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Tuple of (audio_data, sample_rate)
    """
    logger.info(f"Loading audio: {file_path}")
    
    # Load audio with librosa (automatically converts to mono and resamples)
    audio, sr = librosa.load(file_path, sr=TARGET_SAMPLE_RATE, mono=True)
    
    logger.info(f"   Original duration: {len(audio)/sr:.2f}s, Sample rate: {sr}Hz")
    
    return audio, sr


def trim_silence(audio: np.ndarray, sr: int, threshold_db: float = SILENCE_THRESHOLD_DB) -> np.ndarray:
    """
    Trim silence from the beginning and end of audio (VAD).
    
    Args:
        audio: Audio data as numpy array
        sr: Sample rate
        threshold_db: Silence threshold in dB
        
    Returns:
        Trimmed audio data
    """
    logger.info(f"🔇 Trimming silence (threshold: {threshold_db}dB)")
    
    # Convert dB threshold to amplitude
    # librosa.effects.trim uses top_db which is relative to the max amplitude
    top_db = abs(threshold_db)
    
    # Trim silence
    trimmed_audio, index = librosa.effects.trim(audio, top_db=top_db)
    
    original_duration = len(audio) / sr
    trimmed_duration = len(trimmed_audio) / sr
    removed = original_duration - trimmed_duration
    
    logger.info(f"   Trimmed {removed:.2f}s of silence")
    logger.info(f"   New duration: {trimmed_duration:.2f}s")
    
    return trimmed_audio


def normalize_audio(audio: np.ndarray, target_db: float = PEAK_NORMALIZE_DB) -> np.ndarray:
    """
    Normalize audio to target peak level.
    
    Args:
        audio: Audio data as numpy array
        target_db: Target peak level in dB (default: -0.1dB)
        
    Returns:
        Normalized audio data
    """
    logger.info(f"📊 Normalizing audio (target peak: {target_db}dB)")
    
    # Find current peak
    current_peak = np.max(np.abs(audio))
    
    if current_peak == 0:
        logger.warning("   Audio is silent, skipping normalization")
        return audio
    
    current_peak_db = 20 * np.log10(current_peak)
    
    # Calculate gain needed
    target_linear = 10 ** (target_db / 20)
    gain = target_linear / current_peak
    
    # Apply gain
    normalized = audio * gain
    
    # Clip to prevent any overflow
    normalized = np.clip(normalized, -1.0, 1.0)
    
    logger.info(f"   Peak adjusted from {current_peak_db:.1f}dB to {target_db}dB")
    
    return normalized


def denoise_audio(audio: np.ndarray, sr: int, noise_sample_duration: float = 0.5) -> np.ndarray:
    """
    Remove background noise from audio.
    
    Uses the first portion of the audio as a noise profile.
    
    Args:
        audio: Audio data as numpy array
        sr: Sample rate
        noise_sample_duration: Duration in seconds to use as noise profile
        
    Returns:
        Denoised audio data
    """
    if not NOISEREDUCE_AVAILABLE:
        logger.warning("⚠️  noisereduce not available, skipping denoising")
        return audio
    
    logger.info(f"🔊 Denoising audio (noise sample: {noise_sample_duration}s)")
    
    # Use first portion as noise profile
    noise_sample_length = int(noise_sample_duration * sr)
    
    # Make sure we have enough audio
    if len(audio) < noise_sample_length * 2:
        logger.warning("   Audio too short for reliable denoising, using full audio as reference")
        noise_clip = audio
    else:
        noise_clip = audio[:noise_sample_length]
    
    # Apply noise reduction
    denoised = nr.reduce_noise(
        y=audio,
        sr=sr,
        y_noise=noise_clip,
        prop_decrease=0.8,  # How much to reduce noise (0-1)
        stationary=True
    )
    
    logger.info("   Denoising complete")
    
    return denoised


def process_audio(
    input_path: str,
    output_path: Optional[str] = None,
    do_trim: bool = True,
    do_normalize: bool = True,
    do_denoise: bool = True
) -> str:
    """
    Process a single audio file through the full pipeline.
    
    Args:
        input_path: Path to input audio file
        output_path: Path for output file (optional, auto-generated if not provided)
        do_trim: Whether to trim silence
        do_normalize: Whether to normalize volume
        do_denoise: Whether to remove noise
        
    Returns:
        Path to processed audio file
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Generate output path if not provided
    if output_path is None:
        # Save to clips/ folder with same name
        output_path = CLIPS_DIR / input_path.name
    else:
        output_path = Path(output_path)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing: {input_path.name}")
    logger.info(f"{'='*60}")
    
    # Load audio
    audio, sr = load_audio(str(input_path))
    
    # Process pipeline
    if do_denoise:
        audio = denoise_audio(audio, sr)
    
    if do_trim:
        audio = trim_silence(audio, sr)
    
    if do_normalize:
        audio = normalize_audio(audio)
    
    # Save processed audio
    logger.info(f"💾 Saving to: {output_path}")
    
    # Convert to 16-bit PCM for WAV
    sf.write(
        str(output_path),
        audio,
        sr,
        subtype='PCM_16'
    )
    
    # Get duration for metadata
    duration = len(audio) / sr
    logger.info(f"✅ Done! Duration: {duration:.2f}s")
    
    return str(output_path), duration


def process_batch(input_folder: str, output_folder: str):
    """
    Process all audio files in a folder.
    
    Args:
        input_folder: Folder containing raw audio files
        output_folder: Folder for processed output
    """
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    
    # Find all audio files
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    audio_files = [f for f in input_folder.iterdir() if f.suffix.lower() in audio_extensions]
    
    if not audio_files:
        logger.warning(f"No audio files found in {input_folder}")
        return
    
    logger.info(f"\n📂 Batch processing {len(audio_files)} files")
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    results = []
    for audio_file in sorted(audio_files):
        output_path = output_folder / f"{audio_file.stem}.wav"
        try:
            processed_path, duration = process_audio(str(audio_file), str(output_path))
            results.append({
                'input': str(audio_file),
                'output': processed_path,
                'duration': duration,
                'status': 'success'
            })
        except Exception as e:
            logger.error(f"❌ Failed to process {audio_file.name}: {e}")
            results.append({
                'input': str(audio_file),
                'output': None,
                'duration': None,
                'status': f'error: {e}'
            })
    
    # Summary
    success = sum(1 for r in results if r['status'] == 'success')
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Batch complete: {success}/{len(results)} files processed")
    logger.info(f"{'='*60}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Process audio files for Kirundi dataset',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process single file
    python process_audio.py recording.wav
    
    # Process with custom output
    python process_audio.py recording.wav --output clips/processed.wav
    
    # Batch process folder
    python process_audio.py --batch raw_recordings/ --output clips/
    
    # Process without denoising
    python process_audio.py recording.wav --no-denoise
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input audio file')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--batch', '-b', help='Batch process folder')
    parser.add_argument('--no-trim', action='store_true', help='Skip silence trimming')
    parser.add_argument('--no-normalize', action='store_true', help='Skip normalization')
    parser.add_argument('--no-denoise', action='store_true', help='Skip denoising')
    
    args = parser.parse_args()
    
    if args.batch:
        output_folder = args.output or str(CLIPS_DIR)
        process_batch(args.batch, output_folder)
    elif args.input:
        process_audio(
            args.input,
            args.output,
            do_trim=not args.no_trim,
            do_normalize=not args.no_normalize,
            do_denoise=not args.no_denoise
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
