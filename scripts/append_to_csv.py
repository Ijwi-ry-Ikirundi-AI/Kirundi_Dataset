import csv
import os
import logging

# --- Set up correct paths ---
# This finds the script's own directory
SCRIPT_DIR = os.path.dirname(__file__)
# This creates a path to the parent directory (where metadata.csv is)
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

METADATA_FILE = os.path.join(BASE_DIR, "metadata.csv")
SOURCE_TEXT_FILE = "kirundi_prompts_scraped.txt"
# ----------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- THIS IS THE KEY ---
# The target column name MUST be all lowercase, because
# the script converts all headers from the file to lowercase.
TARGET_COLUMN = "kirundi_transcription"

# --- DOMAIN CONFIGURATION ---
# Set the domain for all new rows being added
# Examples: "proverbs", "jokes", "grammar", "lessons", etc.
DOMAIN = "proverbs"  # Change this value based on what you're importing

def append_from_txt_to_csv(domain=None):
    """Append new sentences from text file to CSV with specified domain.
    
    Args:
        domain: The domain/category for the new entries (e.g., 'proverbs', 'jokes').
                If None, uses the DOMAIN variable defined at module level.
    """
    # Use provided domain or fall back to module-level DOMAIN
    if domain is None:
        domain = DOMAIN
    
    if not os.path.exists(METADATA_FILE):
        logger.error(f"Error: Master file not found at: '{METADATA_FILE}'")
        return
        
    if not os.path.exists(SOURCE_TEXT_FILE):
        logger.error(f"Error: Source file not found at: '{SOURCE_TEXT_FILE}'")
        logger.error(f"Please run 'STEP_1_scrape_and_clean.py' first.")
        return

    existing_sentences = set()
    transcription_index = -1
    
    try:
        # --- THIS IS THE FIX ---
        # Use encoding='utf-8-sig' to automatically handle
        # invisible BOM characters at the start of the file.
        with open(METADATA_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            
            try:
                header = next(reader) # Read the header row
            except StopIteration:
                logger.error(f"Error: The file {METADATA_FILE} is empty.")
                return

            # Clean up header names (remove whitespace, make lowercase)
            cleaned_header = [h.strip().lower() for h in header]
            
            # Find the index of our target column
            try:
                transcription_index = cleaned_header.index(TARGET_COLUMN)
            except ValueError:
                logger.error(f"Error: Could not find '{TARGET_COLUMN}' column in {METADATA_FILE}.")
                logger.error(f"--> Headers found in file: {header}")
                logger.error(f"--> Cleaned headers (what script searched for): {cleaned_header}")
                return

            # Add all existing sentences to a set
            for row in reader:
                if row and len(row) > transcription_index and row[transcription_index]:
                    existing_sentences.add(row[transcription_index])
            
        logger.info(f"Loaded {len(existing_sentences)} existing sentences from {METADATA_FILE}.")
    
    except Exception as e:
        logger.error(f"Could not read {METADATA_FILE}: {e}")
        return

    # --- Step 3: Read all sentences from your CLEANED text file ---
    new_sentences_to_add = []
    try:
        with open(SOURCE_TEXT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                sentence = line.strip()
                if sentence and sentence not in existing_sentences:
                    new_sentences_to_add.append(sentence)
                    existing_sentences.add(sentence) 
        
        if not new_sentences_to_add:
            logger.info("No new sentences found in the text file. Your CSV is already up to date!")
            return
        logger.info(f"Found {len(new_sentences_to_add)} new sentences from {SOURCE_TEXT_FILE} to add.")

    except Exception as e:
        logger.error(f"Could not read {SOURCE_TEXT_FILE}: {e}")
        return

    # --- Step 4: Append (add) the new sentences to your CSV ---
    try:
        with open(METADATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for sentence in new_sentences_to_add:
                # Row format matching metadata.csv structure (12 columns):
                # [File_Path, Kirundi_Transcription, French_Translation, English_Translation, 
                #  Domain, Machine_Suggestion, Source, Duration, Speaker_id, Age, Gender, Kirundi_Length]
                writer.writerow(['', sentence, '', '', domain, '', '', '', '', '', '', ''])
        
        logger.info(f"✅ Successfully added {len(new_sentences_to_add)} new sentences to {METADATA_FILE} with domain '{domain}'!")

    except Exception as e:
        logger.error(f"Failed to write to {METADATA_FILE}: {e}")
        logger.error("Please make sure the file is not open in Excel.")

if __name__ == "__main__":
    append_from_txt_to_csv()
    with open("kirundi_prompts_scraped.txt", "w", encoding="utf-8") as f:
        f.write("")