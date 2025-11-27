import pandas as pd
import os
import logging
import re
import argparse
from deep_translator import GoogleTranslator
import time 
from unidecode import unidecode

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

METADATA_PATH = "/home/samandari/Documents/ASYST/Perso/Kirundi_Dataset/metadata.csv" 

# --- STRUCTURE DE LA BASE DE DONNÉES (9 colonnes) ---
MASTER_COLUMNS = [
    'File_Path', 
    'Kirundi_Transcription', 
    'French_Translation',
    'English_Translation',  # <-- NEW: Colonne Anglais
    'Domain',               # <-- NEW: Colonne Domaine
    'Speaker_id', 
    'Age', 
    'Gender', 
    'Machine_Suggestion'
]
# ---------------------------------------------------

# --- UTILITY FUNCTIONS ---

def clean_for_translation(text):
    """Cleans text for Google Translate."""
    if pd.isna(text): return ""
    clean = unidecode(str(text))
    return clean

def normalize_text(text):
    """Cleans text for robust comparison."""
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def load_master_data(filepath):
    """Loads the CSV file and ensures all master columns exist."""
    try:
        df = pd.read_csv(filepath, engine='python', encoding='utf-8-sig', on_bad_lines='warn')
    except FileNotFoundError:
        logger.error(f"FATAL: Metadata file not found at '{filepath}'")
        return None
    except Exception as e:
        logger.error(f"FATAL: Could not read metadata.csv. Error: {e}")
        return None
    
    # Ensure all required master columns exist, adding them if necessary
    for col in MASTER_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
            logger.info(f"Added missing master column: '{col}'")
            
    # Reorder columns and create normalization helper
    df = df[MASTER_COLUMNS] 
    df['normalized_kirundi'] = df['Kirundi_Transcription'].apply(lambda x: normalize_text(x) if pd.notna(x) else "")
        
    logger.info(f"Master file chargé : {len(df)} lignes.")
    return df

# --- TASK 1: CLEANUP ---

def cleanup_completed_hints(df):
    """Removes AI suggestions from rows that now have a human translation."""
    cleaned_count = 0
    print("\n🧹 STEP 1: CLEANUP (Removing old AI hints)...")

    # Rows that have a human translation (French) AND an AI suggestion
    mask = (df['French_Translation'].notna() & (df['French_Translation'].str.strip() != "")) & \
           (df['Machine_Suggestion'].notna() & (df['Machine_Suggestion'].str.strip() != ""))
    
    hints_to_clean = df[mask].index
    
    if not hints_to_clean.empty:
        df.loc[hints_to_clean, 'Machine_Suggestion'] = ""
        cleaned_count = len(hints_to_clean)
    
    logger.info(f"✅ CLEANUP COMPLETE: Removed {cleaned_count} old AI suggestions.")
    return df, cleaned_count

# --- TASK 2: GENERATION (French Hints) ---

def generate_new_hints(df, filepath):
    """Generates new French AI hints for rows missing both a translation and a hint."""
    translator = GoogleTranslator(source='auto', target='fr')
    count = 0
    
    print("\n🤖 STEP 2: GENERATING FRENCH HINTS...")
    
    # Find rows that need a French hint
    rows_to_translate = df[
        df['Kirundi_Transcription'].notna() & 
        (df['French_Translation'].isna() | (df['French_Translation'].str.strip() == "")) &
        (df['Machine_Suggestion'].isna() | (df['Machine_Suggestion'].str.strip() == ""))
    ]
    
    if rows_to_translate.empty:
        logger.info("No new rows found that require French AI suggestions.")
        return df, 0

    print(f"Found {len(rows_to_translate)} rows to translate. Starting...")

    for index, row in rows_to_translate.iterrows():
        kirundi_text = row['Kirundi_Transcription']
        
        try:
            clean_text = clean_for_translation(kirundi_text)
            
            if clean_text:
                translation = translator.translate(clean_text)
                df.loc[index, 'Machine_Suggestion'] = translation
                count += 1
                print(f"[{count}] Kirundi: {clean_text[:30]}... -> French Hint: {translation[:30]}...")
                time.sleep(0.2)
                
                if count % 50 == 0: # Save less frequently for large runs
                     df.to_csv(filepath, index=False, encoding='utf-8-sig')

        except Exception as e:
            print(f"Error translating row {index}: {e}")

    logger.info(f"✅ GENERATION COMPLETE: Created {count} new French suggestions.")
    return df, count

# --- TASK 3: AUTO-TRANSLATE ENGLISH (NEW REQUIREMENT) ---

def generate_english_hints(df):
    """Génère des traductions anglaises si la traduction française existe mais pas l'anglaise."""
    
    translator = GoogleTranslator(source='fr', target='en')
    count = 0
    
    print("\n🌐 STEP 4: AUTO-GÉNÉRATION DES TRADUCTIONS EN ANGLAIS...")

    # Masque: Trouver les lignes qui ont du Français (non vide) MAIS pas d'Anglais (vide)
    mask = (df['French_Translation'].notna()) & (df['French_Translation'].str.strip() != "") & \
           (df['English_Translation'].isna() | (df['English_Translation'].str.strip() == ""))
    
    rows_to_translate = df[mask].copy()
    total_to_translate = len(rows_to_translate)
    
    if rows_to_translate.empty:
        logger.info("Aucune ligne trouvée nécessitant une traduction Française -> Anglaise.")
        return df
    
    logger.info(f"Trouvé {len(rows_to_translate)} lignes à traduire en Anglais...")

    for index, row in rows_to_translate.iterrows():
        french_text = row['French_Translation']
        
        try:
            clean_french = french_text.replace('"', '').strip()
            
            if clean_french:
                english_translation = translator.translate(clean_french)
                
                df.loc[index, 'English_Translation'] = english_translation
                
                count += 1

                 # --- NOUVEAU PRINT : Affiche la progression en temps réel ---
                # flush=True force l'affichage immédiat dans le terminal
                print(f"[{count}/{total_to_translate}] FR->EN: '{clean_french[:40]}...' -> '{english_translation[:20]}...'", flush=True)
                
                time.sleep(0.2)
                
        except Exception as e:
            print(f"Error translating French->English at index {index}: {e}")

    logger.info(f"✅ TRADUCTION ANGLAISE TERMINÉE : {count} lignes traduites.")
    return df

# --- TASK 4: AUTO-FILL DOMAINS ---

def fill_missing_domains(df, default_domain="general"):
    """Automatically fills empty 'Domain' cells."""
    print(f"\n🏷️ STEP 5: BACKFILLING DOMAINS (Default: '{default_domain}')...")
    empty_mask = df['Domain'].isna() | (df['Domain'].astype(str).str.strip() == "")
    empty_count = empty_mask.sum()
    
    if empty_count > 0:
        df['Domain'] = df['Domain'].fillna(default_domain)
        df.loc[df['Domain'].astype(str).str.strip() == "", 'Domain'] = default_domain
        logger.info(f"✅ Auto-filled {empty_count} rows with domain '{default_domain}'.")
    else:
        logger.info("All rows already have a domain.")
        
    return df

# --- TASK 5: SORTING THE OUTPUT (MULTI-LEVEL TRI) ---

def sort_dataframe_for_readability(df):
    """
    Sorts the dataframe using a 3-level priority:
    0: Fully Complete (FR + EN + Domain)
    1: Needs English (Has FR, Needs EN/Domain)
    2: Missing French (Needs core translation)
    """
    print("\n🔄 STEP 6: SORTING OUTPUT (Tri à 3 niveaux)...")

    # Créer les masques de complétude
    has_fr = df['French_Translation'].notna() & (df['French_Translation'].astype(str).str.strip() != "")
    has_en = df['English_Translation'].notna() & (df['English_Translation'].astype(str).str.strip() != "")
    has_domain = df['Domain'].notna() & (df['Domain'].astype(str).str.strip() != "")
    
    def calculate_priority(row):
        # Priority 0: Fully Complete (FR + EN + Domain)
        if row['FR_CHECK'] and row['EN_CHECK'] and row['DOM_CHECK']:
            return 0
        # Priority 1: Has French (Needs EN or other metadata)
        elif row['FR_CHECK']:
            return 1
        # Priority 2: Missing French (Needs core translation)
        else:
            return 2
    
    # Appliquer les masques temporaires
    df['FR_CHECK'] = has_fr
    df['EN_CHECK'] = has_en
    df['DOM_CHECK'] = has_domain
    
    # Calculer la priorité
    df['Sort_Priority'] = df.apply(calculate_priority, axis=1)
    
    # Tri: Priority (0, 1, 2) puis par texte Kirundi
    df.sort_values(by=['Sort_Priority', 'Kirundi_Transcription'], ascending=[True, True], inplace=True)

    # Nettoyage des colonnes temporaires
    df.drop(columns=['Sort_Priority', 'FR_CHECK', 'EN_CHECK', 'DOM_CHECK'], inplace=True, errors='ignore')
    
    logger.info("✅ SORT COMPLETE.")
    return df

# --- TASK 6: AUDIT & REPORT ---

def audit_progress(df):
    """Calculates stats."""
    
    total = len(df)
    
    # Définir les niveaux de complétion pour le rapport détaillé
    complete_mask = (df['French_Translation'].notna()) & (df['English_Translation'].notna()) & (df['Domain'].notna())
    complete_count = complete_mask.sum()
    
    fr_missing_mask = (df['French_Translation'].isna() | (df['French_Translation'].str.strip() == ""))
    fr_missing_count = fr_missing_mask.sum()
    
    en_missing_mask = (df['English_Translation'].isna() | (df['English_Translation'].str.strip() == "")) & (~fr_missing_mask) # Missing EN, but has FR
    en_missing_count = en_missing_mask.sum()
    
    percent_done = (complete_count / total) * 100 if total > 0 else 0

    print("\n" + "="*40)
    print("📊 FINAL DATASET REPORT")
    print("="*40)
    print(f"🔹 Total Phrases:             {total}")
    print("-" * 40)
    print(f"🟢 Fully Complete (FR+EN):    {complete_count} ({percent_done:.1f}%)")
    print(f"🟡 Needs English (Has FR):    {en_missing_count}")
    print(f"🔴 Needs French (Core Trans.):{fr_missing_count}")
    print("="*40)
    
# --- MAIN EXECUTION ---

def run_manager():
    # Déterminer le chemin du fichier metadata.csv (dans le dossier parent)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    metadata_path = os.path.join(os.path.dirname(script_dir), METADATA_PATH)
    
    # 1. Load Master Data
    df = load_master_data(metadata_path)
    if df is None:
        return

    # NOTE: L'étape 2 (Ingestion de clean_datas.csv) est supposée avoir été faite.
    
    # 3. Auto-Fill Missing Domains (NEW)
    df = fill_missing_domains(df, default_domain="general")

    # 4. Génération des Hints Anglais (NEW)
    df = generate_english_hints(df)

    # 5. Tri des données (Implémentation du tri à 3 niveaux)
    df = sort_dataframe_for_readability(df)

    # 6. Sauvegarde
    try:
        df.drop(columns=['normalized_kirundi'], inplace=True, errors='ignore')
        df.to_csv(metadata_path, index=False, encoding='utf-8-sig')
        logger.info(f"\n✨ SUCCESS! Your main file '{metadata_path}' has been updated and saved.")
    except Exception as e:
        logger.error(f"FATAL: Could not save the final metadata file. Error: {e}")
        return
        
    # 7. Audit 
    audit_progress(df)

if __name__ == "__main__":
    # Correction du chemin d'exécution si le script est lancé depuis le dossier racine
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir)) # Change le répertoire de travail au dossier parent (racine)
    
    # Le METADATA_PATH est maintenant le fichier dans le répertoire courant.
    METADATA_PATH = os.path.join(os.getcwd(), METADATA_PATH)
    
    run_manager()