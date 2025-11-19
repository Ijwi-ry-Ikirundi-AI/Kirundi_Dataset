import pandas as pd
from deep_translator import GoogleTranslator
import time
import logging
import os
import re
from unidecode import unidecode

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mettez le chemin vers votre metadata.csv
METADATA_PATH = "/home/samandari/Documents/ASYST/Perso/Kirundi_Dataset/metadata.csv" 

def clean_for_translation(text):
    """
    Enlève les accents tonals complexes qui troublent Google Translate
    Exemple: "ibīntu" -> "ibintu"
    """
    if pd.isna(text): return ""
    # Unidecode change les caractères spéciaux en caractères normaux
    clean = unidecode(str(text))
    return clean

def generate_hints():
    if not os.path.exists(METADATA_PATH):
        logger.error(f"Fichier introuvable : {METADATA_PATH}")
        return

    # 1. Charger le CSV
    df = pd.read_csv(METADATA_PATH, engine='python', encoding='utf-8-sig')
    
    # Créer la colonne pour les suggestions si elle n'existe pas
    # (Ou vous pouvez remplir directement 'French_Translation' si vous préférez)
    if 'Machine_Suggestion' not in df.columns:
        df['Machine_Suggestion'] = ""

    # Initialiser le traducteur (Kirundi 'rn' -> Français 'fr')
    # Google supporte maintenant 'rn', mais parfois 'rw' (Kinyarwanda) marche mieux pour la structure.
    translator = GoogleTranslator(source='auto', target='fr')

    count = 0
    
    print("--- Début de la traduction automatique (Cela peut prendre du temps) ---")

    for index, row in df.iterrows():
        kirundi_text = row['Kirundi_Transcription']
        existing_french = row['French_Translation']
        existing_hint = row['Machine_Suggestion']

        # On traduit SEULEMENT si :
        # 1. Il y a du texte Kirundi
        # 2. Il n'y a PAS encore de traduction humaine (French_Translation est vide)
        # 3. Il n'y a PAS encore de suggestion (pour ne pas refaire le travail)
        if pd.notna(kirundi_text) and pd.isna(existing_french) and (pd.isna(existing_hint) or existing_hint == ""):
            
            try:
                # 1. Nettoyer le texte (enlever les accents bizarres)
                clean_text = clean_for_translation(kirundi_text)
                
                # 2. Traduire
                translation = translator.translate(clean_text)
                
                # 3. Sauvegarder
                df.at[index, 'Machine_Suggestion'] = translation
                
                count += 1
                print(f"[{count}] Kirundi: {clean_text[0:30]}... -> French: {translation[0:30]}...")
                
                # Pause pour ne pas être bloqué par Google (Important !)
                time.sleep(0.2)
                
                # Sauvegarder tous les 10 mots pour ne pas perdre le travail
                if count % 10 == 0:
                    df.to_csv(METADATA_PATH, index=False, encoding='utf-8-sig')

            except Exception as e:
                print(f"Erreur ligne {index}: {e}")

    # Sauvegarde finale
    df.to_csv(METADATA_PATH, index=False, encoding='utf-8-sig')
    print(f"--- Terminé ! {count} suggestions générées. ---")

if __name__ == "__main__":
    generate_hints()