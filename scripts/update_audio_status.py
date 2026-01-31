#!/usr/bin/env python3
"""
Update Audio Status Script for Kirundi Dataset
==============================================

This script scans the clips/ folder for audio files and updates the
corresponding CSV files in final_dataset_splits/ with:
- File_Path: path to the audio file
- Duration: audio length in seconds
- Speaker_id: extracted from filename
- Audio_Status: changed from 'pending' to 'recorded'

Filename convention: [DATE]_[SPEAKER]_[DOMAIN]_[SENTENCE_ID].wav
Example: 20260131_S01_M_jokes_krd_000001.wav

Usage:
    python update_audio_status.py                    # Scan and update
    python update_audio_status.py --dry-run          # Preview changes only
    python update_audio_status.py --validate ID123   # Validate specific recording
    python update_audio_status.py --reject ID123     # Reject specific recording

Audio_Status values:
    - pending: Not recorded yet
    - recorded: Audio file exists, awaiting review
    - validated: Peer-review passed
    - rejected: Needs re-recording

Dependencies:
    pip install pandas librosa
"""

import os
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

# Try to import librosa for duration calculation
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️  librosa not installed. Duration calculation will be skipped.")

# Configuration
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
CLIPS_DIR = BASE_DIR / "clips"
SPLITS_DIR = BASE_DIR / "final_dataset_splits"

# Filename pattern: DATE_SPEAKER_DOMAIN_ID.wav
# Example: 20260131_S01_M_jokes_krd_000001.wav
FILENAME_PATTERN = re.compile(
    r'^(\d{8})_([A-Za-z0-9_]+)_([a-z-]+)_(krd_\d+_[a-z-]+)\.wav$',
    re.IGNORECASE
)

# Alternative simpler pattern: just look for the ID
ID_PATTERN = re.compile(r'(krd_\d+_[a-z-]+)', re.IGNORECASE)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_audio_duration(file_path: str) -> float:
    """Get duration of audio file in seconds."""
    if not LIBROSA_AVAILABLE:
        return None
    
    try:
        duration = librosa.get_duration(path=file_path)
        return round(duration, 2)
    except Exception as e:
        logger.warning(f"Could not get duration for {file_path}: {e}")
        return None


def parse_filename(filename: str) -> dict:
    """
    Parse audio filename to extract metadata.
    
    Args:
        filename: Audio filename (e.g., 20260131_S01_M_jokes_krd_000001.wav)
        
    Returns:
        Dictionary with date, speaker_id, domain, sentence_id or None
    """
    # Try full pattern first
    match = FILENAME_PATTERN.match(filename)
    if match:
        return {
            'date': match.group(1),
            'speaker_id': match.group(2),
            'domain': match.group(3),
            'sentence_id': match.group(4)
        }
    
    # Try to at least extract the ID
    id_match = ID_PATTERN.search(filename)
    if id_match:
        return {
            'date': None,
            'speaker_id': None,
            'domain': None,
            'sentence_id': id_match.group(1)
        }
    
    return None


def load_all_csvs() -> dict:
    """
    Load all CSV files from final_dataset_splits/ into a dictionary.
    
    Returns:
        Dictionary mapping sentence_id to (csv_path, row_index)
    """
    id_to_location = {}
    
    csv_files = sorted(SPLITS_DIR.glob("final_dataset_part_*.csv"))
    
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        
        for idx, row in df.iterrows():
            sentence_id = row['ID']
            id_to_location[sentence_id] = {
                'csv_path': csv_path,
                'row_index': idx
            }
    
    return id_to_location


def scan_clips_folder() -> list:
    """
    Scan clips/ folder for audio files.
    
    Returns:
        List of dictionaries with file info
    """
    if not CLIPS_DIR.exists():
        logger.warning(f"Clips folder does not exist: {CLIPS_DIR}")
        return []
    
    audio_files = []
    audio_extensions = {'.wav', '.mp3', '.flac'}
    
    # Scan clips/ and subdirectories
    for audio_file in CLIPS_DIR.rglob('*'):
        if audio_file.suffix.lower() in audio_extensions and audio_file.is_file():
            # Skip .gitkeep
            if audio_file.name == '.gitkeep':
                continue
            
            parsed = parse_filename(audio_file.name)
            
            # Calculate relative path from BASE_DIR
            rel_path = audio_file.relative_to(BASE_DIR)
            
            audio_files.append({
                'full_path': audio_file,
                'relative_path': str(rel_path),
                'filename': audio_file.name,
                'parsed': parsed,
                'duration': get_audio_duration(str(audio_file))
            })
    
    return audio_files


def update_csv_with_audio(audio_info: dict, id_to_location: dict, dry_run: bool = False) -> bool:
    """
    Update CSV file with audio information.
    
    Args:
        audio_info: Dictionary with audio file info
        id_to_location: Mapping of IDs to CSV locations
        dry_run: If True, only preview changes
        
    Returns:
        True if update was successful
    """
    if audio_info['parsed'] is None:
        logger.warning(f"Could not parse filename: {audio_info['filename']}")
        return False
    
    sentence_id = audio_info['parsed']['sentence_id']
    
    if sentence_id not in id_to_location:
        logger.warning(f"Sentence ID not found in dataset: {sentence_id}")
        return False
    
    location = id_to_location[sentence_id]
    csv_path = location['csv_path']
    
    # Load CSV
    df = pd.read_csv(csv_path)
    
    # Find the row
    mask = df['ID'] == sentence_id
    if not mask.any():
        logger.warning(f"ID {sentence_id} not found in {csv_path.name}")
        return False
    
    # Get current status
    current_status = df.loc[mask, 'Audio_Status'].values[0]
    current_file_path = df.loc[mask, 'File_Path'].values[0]
    
    # Prepare updates
    updates = {
        'File_Path': audio_info['relative_path'],
        'Audio_Status': 'recorded'
    }
    
    if audio_info['duration'] is not None:
        updates['Duration'] = audio_info['duration']
    
    if audio_info['parsed']['speaker_id']:
        updates['Speaker_id'] = audio_info['parsed']['speaker_id']
    
    # Log changes
    logger.info(f"📝 {sentence_id}:")
    logger.info(f"   File: {csv_path.name}")
    logger.info(f"   Status: {current_status} → recorded")
    logger.info(f"   Path: {audio_info['relative_path']}")
    if audio_info['duration']:
        logger.info(f"   Duration: {audio_info['duration']}s")
    
    if dry_run:
        logger.info("   [DRY RUN - no changes made]")
        return True
    
    # Apply updates
    for col, value in updates.items():
        df.loc[mask, col] = value
    
    # Save CSV
    df.to_csv(csv_path, index=False)
    logger.info(f"   ✅ Saved to {csv_path.name}")
    
    return True


def update_status(sentence_id: str, new_status: str, id_to_location: dict) -> bool:
    """
    Update the Audio_Status for a specific sentence.
    
    Args:
        sentence_id: The sentence ID (e.g., krd_000001_jokes)
        new_status: New status (validated, rejected, pending, recorded)
        id_to_location: Mapping of IDs to CSV locations
        
    Returns:
        True if update was successful
    """
    if sentence_id not in id_to_location:
        logger.error(f"❌ Sentence ID not found: {sentence_id}")
        return False
    
    location = id_to_location[sentence_id]
    csv_path = location['csv_path']
    
    # Load CSV
    df = pd.read_csv(csv_path)
    
    # Find and update
    mask = df['ID'] == sentence_id
    old_status = df.loc[mask, 'Audio_Status'].values[0]
    
    df.loc[mask, 'Audio_Status'] = new_status
    
    # Save
    df.to_csv(csv_path, index=False)
    
    logger.info(f"✅ Updated {sentence_id}: {old_status} → {new_status}")
    
    return True


def print_summary(id_to_location: dict):
    """Print summary of audio status across all files."""
    
    status_counts = {'pending': 0, 'recorded': 0, 'validated': 0, 'rejected': 0}
    
    csv_files = sorted(SPLITS_DIR.glob("final_dataset_part_*.csv"))
    
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        for status in status_counts:
            status_counts[status] += (df['Audio_Status'] == status).sum()
    
    total = sum(status_counts.values())
    
    print(f"\n{'='*50}")
    print("📊 AUDIO STATUS SUMMARY")
    print(f"{'='*50}")
    print(f"   Total sentences: {total}")
    print(f"   ⏳ Pending:   {status_counts['pending']:>5} ({100*status_counts['pending']/total:.1f}%)")
    print(f"   🎙️  Recorded:  {status_counts['recorded']:>5} ({100*status_counts['recorded']/total:.1f}%)")
    print(f"   ✅ Validated: {status_counts['validated']:>5} ({100*status_counts['validated']/total:.1f}%)")
    print(f"   ❌ Rejected:  {status_counts['rejected']:>5} ({100*status_counts['rejected']/total:.1f}%)")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Update audio status in Kirundi dataset',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--dry-run', action='store_true', 
                        help='Preview changes without saving')
    parser.add_argument('--validate', metavar='ID', 
                        help='Mark a recording as validated')
    parser.add_argument('--reject', metavar='ID', 
                        help='Mark a recording as rejected')
    parser.add_argument('--summary', action='store_true',
                        help='Show status summary only')
    
    args = parser.parse_args()
    
    # Load CSV mappings
    logger.info("📂 Loading dataset...")
    id_to_location = load_all_csvs()
    logger.info(f"   Found {len(id_to_location)} sentences")
    
    # Handle specific actions
    if args.validate:
        update_status(args.validate, 'validated', id_to_location)
        return
    
    if args.reject:
        update_status(args.reject, 'rejected', id_to_location)
        return
    
    if args.summary:
        print_summary(id_to_location)
        return
    
    # Scan clips folder
    logger.info(f"\n🔍 Scanning clips folder: {CLIPS_DIR}")
    audio_files = scan_clips_folder()
    
    if not audio_files:
        logger.info("No new audio files found in clips/")
        print_summary(id_to_location)
        return
    
    logger.info(f"   Found {len(audio_files)} audio files")
    
    # Update CSVs
    logger.info(f"\n{'='*50}")
    logger.info("UPDATING CSV FILES")
    logger.info(f"{'='*50}\n")
    
    success_count = 0
    for audio_info in audio_files:
        if update_csv_with_audio(audio_info, id_to_location, args.dry_run):
            success_count += 1
    
    logger.info(f"\n✅ Updated {success_count}/{len(audio_files)} files")
    
    # Show summary
    if not args.dry_run:
        print_summary(id_to_location)


if __name__ == "__main__":
    main()
