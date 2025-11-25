import pandas as pd
from deep_translator import GoogleTranslator
import time
import logging
import os
import re
from unidecode import unidecode
import argparse

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

METADATA_PATH = "metadata.csv" 

# --- UTILITY FUNCTIONS ---

def clean_for_translation(text):
    """Cleans text for Google Translate."""
    if pd.isna(text): return ""
    clean = unidecode(str(text))
    return clean

def load_data(filepath):
    """Loads the CSV file with error handling."""
    try:
        df = pd.read_csv(filepath, engine='python', encoding='utf-8-sig', on_bad_lines='warn')
    except FileNotFoundError:
        logger.error(f"FATAL: Metadata file not found at '{filepath}'")
        return None
    except Exception as e:
        logger.error(f"FATAL: Could not read metadata.csv. Error: {e}")
        return None
    
    if 'Machine_Suggestion' not in df.columns:
        df['Machine_Suggestion'] = ""
        logger.info("Created new 'Machine_Suggestion' column.")
        
    return df

# --- TASK 1: CLEANUP ---

def cleanup_completed_hints(df):
    """Removes AI suggestions from rows that now have a human translation."""
    cleaned_count = 0
    print("\n🧹 STEP 1: CLEANUP (Removing old AI hints)...")

    # Rows that have a Human translation AND an AI suggestion
    mask = (df['French_Translation'].notna() & (df['French_Translation'].str.strip() != "")) & \
           (df['Machine_Suggestion'].notna() & (df['Machine_Suggestion'].str.strip() != ""))
    
    hints_to_clean = df[mask].index
    
    if not hints_to_clean.empty:
        df.loc[hints_to_clean, 'Machine_Suggestion'] = ""
        cleaned_count = len(hints_to_clean)
    
    logger.info(f"✅ CLEANUP COMPLETE: Removed {cleaned_count} old AI suggestions.")
    return df, cleaned_count

# --- TASK 2: GENERATION ---

def generate_new_hints(df, filepath):
    """Generates new AI hints for rows missing both a translation and a hint."""
    translator = GoogleTranslator(source='auto', target='fr')
    count = 0
    
    print("\n🤖 STEP 2: GENERATING NEW HINTS...")
    
    # Find rows that need a hint
    rows_to_translate = df[
        df['Kirundi_Transcription'].notna() & 
        (df['French_Translation'].isna() | (df['French_Translation'].str.strip() == "")) &
        (df['Machine_Suggestion'].isna() | (df['Machine_Suggestion'].str.strip() == ""))
    ]
    
    if rows_to_translate.empty:
        logger.info("No new rows found that require AI suggestions.")
        return df, 0

    print(f"Found {len(rows_to_translate)} rows to translate. Starting...")

    for index, row in rows_to_translate.iterrows():
        kirundi_text = row['Kirundi_Transcription']
        
        try:
            clean_text = clean_for_translation(kirundi_text)
            
            if clean_text:
                translation = translator.translate(clean_text)
                df.at[index, 'Machine_Suggestion'] = translation
                count += 1
                print(f"[{count}] Kirundi: {clean_text[:30]}... -> French: {translation[:30]}...")
                time.sleep(0.2)
                
                # Periodic save
                if count % 20 == 0:
                     df.to_csv(filepath, index=False, encoding='utf-8-sig')

        except Exception as e:
            print(f"Error translating row {index}: {e}")

    logger.info(f"✅ GENERATION COMPLETE: Created {count} new suggestions.")
    return df, count

# --- TASK 3: SORTING ---

def sort_dataframe_for_readability(df):
    """Sorts translated rows to the top."""
    print("\n🔄 STEP 3: SORTING OUTPUT...")

    # Create temporary priority column: 0 = Done, 1 = Todo
    df['Sort_Priority'] = df['French_Translation'].apply(
        lambda x: 0 if pd.notna(x) and str(x).strip() != "" else 1
    )

    # Sort by Priority then Alphabetical
    df.sort_values(by=['Sort_Priority', 'Kirundi_Transcription'], ascending=[True, True], inplace=True)

    # Remove helper column
    df.drop(columns=['Sort_Priority'], inplace=True)
    
    logger.info("✅ SORT COMPLETE.")
    return df

# --- TASK 4: AUDIT & REPORT ---

def audit_progress(df):
    """Calculates stats and saves missing translations."""
    
    # Define what "clean" means (has a translation)
    clean_rows = df[df['French_Translation'].notna() & (df['French_Translation'].str.strip() != "")]
    
    # Define what "missing" means (no translation)
    missing_rows = df[df['French_Translation'].isna() | (df['French_Translation'].str.strip() == "")]
    
    total = len(df)
    done_count = len(clean_rows)
    missing_count = len(missing_rows)
    percent_done = (done_count / total) * 100 if total > 0 else 0

    print("\n" + "="*40)
    print("📊 FINAL DATASET REPORT")
    print("="*40)
    print(f"🔹 Total Phrases:           {total}")
    print(f"✅ Translated (Human):      {done_count} ({percent_done:.1f}%)")
    print(f"⚠️  Missing Translation:     {missing_count}")
    print("="*40)
    
    # Save missing list
    # if not missing_rows.empty:
    #     with open("missing_translations.txt", "w", encoding="utf-8") as f:
    #         for line in missing_rows['Kirundi_Transcription']:
    #             f.write(f"{str(line).strip()}\n")
    #     print(f"💡 List of missing translations saved to 'missing_translations.txt'")
    
    return missing_rows

# --- MAIN EXECUTION ---

def run_manager(metadata_path):
    # 1. Load data
    df = load_data(metadata_path)
    if df is None:
        return

    # 2. Run Cleanup
    df, cleaned_count = cleanup_completed_hints(df)
    
    # 3. Run Generation
    df, generated_count = generate_new_hints(df, metadata_path)
    
    # 4. Run Sorting
    df = sort_dataframe_for_readability(df)

    # 5. Save
    try:
        df.to_csv(metadata_path, index=False, encoding='utf-8-sig')
        logger.info(f"\n✨ SUCCESS! Main file '{metadata_path}' updated and saved.")
    except Exception as e:
        logger.error(f"FATAL: Could not save file. Error: {e}")
        return
        
    # 6. Audit (This will now work because missing_rows is defined inside it)
    audit_progress(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default='.', help='Path to the project root.')
    args = parser.parse_args()
    
    # Determine path
    if args.path != '.':
        # If user provided a path
        target_file = os.path.join(args.path, "metadata.csv")
    else:
        # Default: assume script is in 'scripts/' and csv is in parent
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Check if we are inside the 'scripts' folder
        if os.path.basename(current_dir) == 'scripts':
             target_file = os.path.join(os.path.dirname(current_dir), "metadata.csv")
        else:
             # Assume we are in the root
             target_file = os.path.join(current_dir, "metadata.csv")
    
    print(f"Targeting Metadata File: {target_file}")
    run_manager(target_file)