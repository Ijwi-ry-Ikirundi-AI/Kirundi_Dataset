import csv
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
METADATA_FILE = BASE_DIR / "metadata.csv"
SOURCE_TEXT_FILE = SCRIPT_DIR / "kirundi_prompts_scraped.txt"

TARGET_COLUMN = "kirundi_transcription"
DOMAIN = "proverbs"


def append_from_txt_to_csv(domain: Optional[str] = None) -> None:
    """Append new, non-duplicate sentences from the text file to metadata.csv.

    Args:
        domain: Category for new entries (e.g. 'proverbs', 'jokes').
                Falls back to the module-level DOMAIN constant when None.
    """
    if domain is None:
        domain = DOMAIN

    if not METADATA_FILE.exists():
        logger.error(f"Master file not found at: '{METADATA_FILE}'")
        return

    if not SOURCE_TEXT_FILE.exists():
        logger.error(f"Source file not found at: '{SOURCE_TEXT_FILE}'")
        return

    existing_sentences: set[str] = set()
    transcription_index = -1

    try:
        with METADATA_FILE.open("r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)

            try:
                header = next(reader)
            except StopIteration:
                logger.error(f"The file {METADATA_FILE} is empty.")
                return

            cleaned_header = [h.strip().lower() for h in header]

            try:
                transcription_index = cleaned_header.index(TARGET_COLUMN)
            except ValueError:
                logger.error(
                    f"Could not find '{TARGET_COLUMN}' column in {METADATA_FILE}. "
                    f"Headers found: {header}"
                )
                return

            for row in reader:
                if row and len(row) > transcription_index and row[transcription_index]:
                    existing_sentences.add(row[transcription_index])

        logger.info(f"Loaded {len(existing_sentences)} existing sentences from {METADATA_FILE}.")

    except Exception as e:
        logger.error(f"Could not read {METADATA_FILE}: {e}")
        return

    new_sentences: list[str] = []
    try:
        with SOURCE_TEXT_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                sentence = line.strip()
                if sentence and sentence not in existing_sentences:
                    new_sentences.append(sentence)
                    existing_sentences.add(sentence)

        if not new_sentences:
            logger.info("No new sentences found. CSV is already up to date.")
            return

        logger.info(f"Found {len(new_sentences)} new sentences to add.")

    except Exception as e:
        logger.error(f"Could not read {SOURCE_TEXT_FILE}: {e}")
        return

    try:
        with METADATA_FILE.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for sentence in new_sentences:
                writer.writerow(["", sentence, "", "", domain, "", "", "", "", "", "", ""])

        logger.info(
            f"Successfully added {len(new_sentences)} sentences "
            f"to {METADATA_FILE} with domain '{domain}'."
        )

    except Exception as e:
        logger.error(f"Failed to write to {METADATA_FILE}: {e}")


if __name__ == "__main__":
    append_from_txt_to_csv()
    SOURCE_TEXT_FILE.write_text("", encoding="utf-8")
