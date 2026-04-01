#!/usr/bin/env python3
"""
Audio Pipeline for Kirundi Dataset
===================================

Unified script that processes raw audio AND updates the dataset CSVs.

Commands:
    process   - Denoise, trim silence, normalize audio files
    update    - Scan clips/ and update split CSVs (status, duration, speaker)
    validate  - Mark a recording as validated
    reject    - Mark a recording as rejected
    summary   - Show audio status summary across all splits

Usage:
    python audio_pipeline.py process <file>
    python audio_pipeline.py process --batch <folder> [--output <folder>]
    python audio_pipeline.py update [--dry-run]
    python audio_pipeline.py validate <ID>
    python audio_pipeline.py reject <ID>
    python audio_pipeline.py summary

Audio specifications:
    - Format: WAV (16-bit PCM)
    - Sample rate: 16kHz
    - Channels: Mono
    - Silence threshold: -30dB

Audio_Status lifecycle:
    pending → recorded → validated
                       → rejected → (re-record) → recorded

Dependencies:
    pip install librosa soundfile noisereduce numpy pandas
"""

import argparse
import logging
import re
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
CLIPS_DIR = BASE_DIR / "clips"
SPLITS_DIR = BASE_DIR / "final_dataset_splits"

TARGET_SAMPLE_RATE = 16000
SILENCE_THRESHOLD_DB = -30
PEAK_NORMALIZE_DB = -0.1

FILENAME_PATTERN = re.compile(
    r'^(\d{8})_([A-Za-z0-9_]+)_([a-z-]+)_(krd_\d+_[a-z-]+)\.wav$',
    re.IGNORECASE,
)
ID_PATTERN = re.compile(r'(krd_\d+_[a-z-]+)', re.IGNORECASE)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Audio processing functions
# ---------------------------------------------------------------------------

def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
    """Load audio file, resample to 16kHz mono."""
    if not LIBROSA_AVAILABLE:
        raise ImportError("librosa is required: pip install librosa")

    logger.info("Loading audio: %s", file_path)
    audio, sr = librosa.load(file_path, sr=TARGET_SAMPLE_RATE, mono=True)
    logger.info("   Duration: %.2fs, Sample rate: %dHz", len(audio) / sr, sr)
    return audio, sr


def trim_silence(
    audio: np.ndarray,
    sr: int,
    threshold_db: float = SILENCE_THRESHOLD_DB,
) -> np.ndarray:
    """Trim silence from start/end (VAD)."""
    logger.info("Trimming silence (threshold: %sdB)", threshold_db)
    trimmed, _ = librosa.effects.trim(audio, top_db=abs(threshold_db))
    removed = (len(audio) - len(trimmed)) / sr
    logger.info("   Trimmed %.2fs of silence → %.2fs", removed, len(trimmed) / sr)
    return trimmed


def normalize_audio(
    audio: np.ndarray,
    target_db: float = PEAK_NORMALIZE_DB,
) -> np.ndarray:
    """Peak-normalize audio."""
    logger.info("Normalizing audio (target peak: %sdB)", target_db)
    peak = np.max(np.abs(audio))
    if peak == 0:
        logger.warning("   Audio is silent, skipping")
        return audio
    gain = 10 ** (target_db / 20) / peak
    return np.clip(audio * gain, -1.0, 1.0)


def denoise_audio(
    audio: np.ndarray,
    sr: int,
    noise_duration: float = 0.5,
) -> np.ndarray:
    """Remove background noise using first N seconds as profile."""
    if not NOISEREDUCE_AVAILABLE:
        logger.warning("noisereduce not available, skipping denoising")
        return audio

    logger.info("Denoising audio (noise sample: %.1fs)", noise_duration)
    noise_len = int(noise_duration * sr)
    noise_clip = audio if len(audio) < noise_len * 2 else audio[:noise_len]
    denoised = nr.reduce_noise(
        y=audio, sr=sr, y_noise=noise_clip,
        prop_decrease=0.8, stationary=True,
    )
    logger.info("   Denoising complete")
    return denoised


def process_single(
    input_path: str,
    output_path: Optional[str] = None,
    do_trim: bool = True,
    do_normalize: bool = True,
    do_denoise: bool = True,
) -> Tuple[str, float]:
    """Full processing pipeline for one audio file."""
    if not SOUNDFILE_AVAILABLE:
        raise ImportError("soundfile is required: pip install soundfile")

    inp = Path(input_path)
    if not inp.exists():
        raise FileNotFoundError(f"Input not found: {inp}")

    out = Path(output_path) if output_path else inp
    out.parent.mkdir(parents=True, exist_ok=True)

    logger.info("\n%s", "=" * 60)
    logger.info("Processing: %s", inp.name)
    logger.info("=" * 60)

    audio, sr = load_audio(str(inp))

    if do_denoise:
        audio = denoise_audio(audio, sr)
    if do_trim:
        audio = trim_silence(audio, sr)
    if do_normalize:
        audio = normalize_audio(audio)

    sf.write(str(out), audio, sr, subtype='PCM_16')
    duration = len(audio) / sr
    logger.info("Saved: %s (%.2fs)", out, duration)
    return str(out), duration


def process_batch(input_folder: str, output_folder: str, **kwargs):
    """Process all audio files in a folder."""
    inp_dir = Path(input_folder)
    out_dir = Path(output_folder)
    exts = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    files = sorted(f for f in inp_dir.iterdir() if f.suffix.lower() in exts)

    if not files:
        logger.warning("No audio files found in %s", inp_dir)
        return []

    logger.info("\nBatch processing %d files", len(files))
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for af in files:
        out_path = out_dir / f"{af.stem}.wav"
        try:
            path, dur = process_single(str(af), str(out_path), **kwargs)
            results.append({'input': str(af), 'output': path, 'duration': dur, 'status': 'ok'})
        except Exception as e:
            logger.error("Failed: %s — %s", af.name, e)
            results.append({'input': str(af), 'output': None, 'duration': None, 'status': str(e)})

    ok = sum(1 for r in results if r['status'] == 'ok')
    logger.info("\nBatch complete: %d/%d succeeded", ok, len(results))
    return results


# ---------------------------------------------------------------------------
# CSV status functions
# ---------------------------------------------------------------------------

def _require_pandas():
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required: pip install pandas")


def get_audio_duration(file_path: str) -> Optional[float]:
    """Get duration of an audio file in seconds."""
    if not LIBROSA_AVAILABLE:
        return None
    try:
        return round(librosa.get_duration(path=file_path), 2)
    except Exception as e:
        logger.warning("Could not get duration for %s: %s", file_path, e)
        return None


def parse_audio_filename(filename: str) -> Optional[dict]:
    """Extract metadata from audio filename."""
    match = FILENAME_PATTERN.match(filename)
    if match:
        return {
            'date': match.group(1),
            'speaker_id': match.group(2),
            'domain': match.group(3),
            'sentence_id': match.group(4),
        }
    id_match = ID_PATTERN.search(filename)
    if id_match:
        return {'date': None, 'speaker_id': None, 'domain': None, 'sentence_id': id_match.group(1)}
    return None


def load_split_index() -> dict:
    """Build an index mapping sentence_id → (csv_path, row_index)."""
    _require_pandas()
    index = {}
    for csv_path in sorted(SPLITS_DIR.glob("final_dataset_part_*.csv")):
        df = pd.read_csv(csv_path)
        for idx, row in df.iterrows():
            index[row['ID']] = {'csv_path': csv_path, 'row_index': idx}
    return index


def scan_clips() -> list:
    """Scan clips/ for audio files and extract metadata."""
    if not CLIPS_DIR.exists():
        logger.warning("Clips folder missing: %s", CLIPS_DIR)
        return []

    exts = {'.wav', '.mp3', '.flac'}
    results = []
    for af in CLIPS_DIR.rglob('*'):
        if af.suffix.lower() not in exts or not af.is_file() or af.name == '.gitkeep':
            continue
        results.append({
            'full_path': af,
            'relative_path': str(af.relative_to(BASE_DIR)),
            'filename': af.name,
            'parsed': parse_audio_filename(af.name),
            'duration': get_audio_duration(str(af)),
        })
    return results


def update_csv_from_audio(audio_info: dict, index: dict, dry_run: bool = False) -> bool:
    """Update a split CSV row with audio metadata."""
    _require_pandas()

    if audio_info['parsed'] is None:
        logger.warning("Could not parse filename: %s", audio_info['filename'])
        return False

    sid = audio_info['parsed']['sentence_id']
    if sid not in index:
        logger.warning("ID not found in dataset: %s", sid)
        return False

    loc = index[sid]
    csv_path = loc['csv_path']
    df = pd.read_csv(csv_path)
    mask = df['ID'] == sid

    if not mask.any():
        logger.warning("ID %s not found in %s", sid, csv_path.name)
        return False

    updates = {'File_Path': audio_info['relative_path'], 'Audio_Status': 'recorded'}
    if audio_info['duration'] is not None:
        updates['Duration'] = audio_info['duration']
    if audio_info['parsed']['speaker_id']:
        updates['Speaker_id'] = audio_info['parsed']['speaker_id']

    old_status = df.loc[mask, 'Audio_Status'].values[0]
    logger.info(
        "%s: %s → recorded (file: %s)",
        sid, old_status, csv_path.name,
    )

    if dry_run:
        logger.info("   [DRY RUN]")
        return True

    for col, val in updates.items():
        df.loc[mask, col] = val
    df.to_csv(csv_path, index=False)
    return True


def set_status(sentence_id: str, new_status: str, index: dict) -> bool:
    """Set Audio_Status for a specific sentence."""
    _require_pandas()

    if sentence_id not in index:
        logger.error("ID not found: %s", sentence_id)
        return False

    loc = index[sentence_id]
    csv_path = loc['csv_path']
    df = pd.read_csv(csv_path)
    mask = df['ID'] == sentence_id
    old = df.loc[mask, 'Audio_Status'].values[0]
    df.loc[mask, 'Audio_Status'] = new_status
    df.to_csv(csv_path, index=False)
    logger.info("Updated %s: %s → %s", sentence_id, old, new_status)
    return True


def print_summary():
    """Print audio status counts across all splits."""
    _require_pandas()

    counts = {'pending': 0, 'recorded': 0, 'validated': 0, 'rejected': 0}
    for csv_path in sorted(SPLITS_DIR.glob("final_dataset_part_*.csv")):
        df = pd.read_csv(csv_path)
        for status in counts:
            counts[status] += int((df['Audio_Status'] == status).sum())

    total = sum(counts.values())
    if total == 0:
        print("No splits found.")
        return

    print(f"\n{'=' * 50}")
    print("AUDIO STATUS SUMMARY")
    print(f"{'=' * 50}")
    print(f"   Total sentences:  {total}")
    for label, emoji in [('pending', '⏳'), ('recorded', '🎙️'), ('validated', '✅'), ('rejected', '❌')]:
        pct = 100 * counts[label] / total
        print(f"   {emoji} {label.capitalize():>10}: {counts[label]:>5} ({pct:.1f}%)")
    print(f"{'=' * 50}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Kirundi audio pipeline: process, update, validate, reject',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command')

    # -- process --
    p_proc = sub.add_parser('process', help='Process raw audio files')
    p_proc.add_argument('input', nargs='?', help='Input audio file')
    p_proc.add_argument('--batch', '-b', help='Batch process a folder')
    p_proc.add_argument('--output', '-o', help='Output path')
    p_proc.add_argument('--no-trim', action='store_true')
    p_proc.add_argument('--no-normalize', action='store_true')
    p_proc.add_argument('--no-denoise', action='store_true')

    # -- update --
    p_upd = sub.add_parser('update', help='Scan clips/ and update split CSVs')
    p_upd.add_argument('--dry-run', action='store_true', help='Preview only')

    # -- validate --
    p_val = sub.add_parser('validate', help='Mark a recording as validated')
    p_val.add_argument('id', help='Sentence ID (e.g. krd_000001_jokes)')

    # -- reject --
    p_rej = sub.add_parser('reject', help='Mark a recording as rejected')
    p_rej.add_argument('id', help='Sentence ID (e.g. krd_000001_jokes)')

    # -- summary --
    sub.add_parser('summary', help='Show audio status summary')

    args = parser.parse_args()

    if args.command == 'process':
        if args.batch:
            out = args.output or str(CLIPS_DIR)
            process_batch(
                args.batch, out,
                do_trim=not args.no_trim,
                do_normalize=not args.no_normalize,
                do_denoise=not args.no_denoise,
            )
        elif args.input:
            process_single(
                args.input, args.output,
                do_trim=not args.no_trim,
                do_normalize=not args.no_normalize,
                do_denoise=not args.no_denoise,
            )
        else:
            p_proc.print_help()

    elif args.command == 'update':
        logger.info("Loading dataset...")
        index = load_split_index()
        logger.info("   %d sentences indexed", len(index))
        logger.info("Scanning clips/...")
        audio_files = scan_clips()
        if not audio_files:
            logger.info("No audio files found in clips/")
            print_summary()
            return
        logger.info("   %d audio files found", len(audio_files))
        ok = sum(
            update_csv_from_audio(a, index, dry_run=args.dry_run)
            for a in audio_files
        )
        logger.info("Updated %d/%d files", ok, len(audio_files))
        if not args.dry_run:
            print_summary()

    elif args.command == 'validate':
        index = load_split_index()
        set_status(args.id, 'validated', index)

    elif args.command == 'reject':
        index = load_split_index()
        set_status(args.id, 'rejected', index)

    elif args.command == 'summary':
        print_summary()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
