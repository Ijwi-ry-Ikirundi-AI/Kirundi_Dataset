#!/usr/bin/env bash
#
# Conversion M4A/MP4 -> WAV sans perte de qualite
# Pour entrainement modele ASR Kirundi
#
# Parametres de sortie :
#   - Format : WAV (PCM non compresse)
#   - Echantillonnage : 48000 Hz (conserve l'original, pas de resampling)
#   - Canaux : mono (conserve l'original)
#   - Profondeur : 16-bit signed PCM (standard pour ML audio)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT_DIR="$SCRIPT_DIR/voices"
OUTPUT_DIR="$SCRIPT_DIR/voices/wav"

# Trouver ffmpeg
FFMPEG=""
if command -v ffmpeg &>/dev/null; then
    FFMPEG="ffmpeg"
elif [ -x "$HOME/.local/bin/ffmpeg" ]; then
    FFMPEG="$HOME/.local/bin/ffmpeg"
else
    echo "ERREUR: ffmpeg introuvable."
    exit 1
fi

echo "ffmpeg: $($FFMPEG -version | head -1)"
echo ""

mkdir -p "$OUTPUT_DIR"

total=0
converted=0
skipped=0
errors=0

shopt -s nullglob
files=("$INPUT_DIR"/*.m4a.mp4 "$INPUT_DIR"/*.m4a "$INPUT_DIR"/*.mp4 "$INPUT_DIR"/*.aac)
shopt -u nullglob

declare -A seen
unique_files=()
for f in "${files[@]}"; do
    base="$(basename "$f")"
    [[ "$base" == *.wav || "$base" == *.sh || "$base" == *.py ]] && continue
    if [[ -z "${seen[$base]+x}" ]]; then
        seen[$base]=1
        unique_files+=("$f")
    fi
done

total=${#unique_files[@]}

if [ "$total" -eq 0 ]; then
    echo "Aucun fichier audio trouve dans $INPUT_DIR"
    exit 0
fi

echo "Fichiers a convertir: $total"
echo "Sortie: $OUTPUT_DIR"
echo "==========================================="

for input_file in "${unique_files[@]}"; do
    filename="$(basename "$input_file")"

    wav_name="${filename%.m4a.mp4}"
    wav_name="${wav_name%.m4a}"
    wav_name="${wav_name%.mp4}"
    wav_name="${wav_name%.aac}"
    wav_name="${wav_name}.wav"

    output_file="$OUTPUT_DIR/$wav_name"

    if [ -f "$output_file" ]; then
        skipped=$((skipped + 1))
        continue
    fi

    if "$FFMPEG" -v warning -i "$input_file" \
        -acodec pcm_s16le \
        -ar 48000 \
        -ac 1 \
        -y "$output_file" 2>&1; then

        if [ -f "$output_file" ] && [ -s "$output_file" ]; then
            converted=$((converted + 1))
            printf "\r  [%3d/%d] %s" "$((converted + skipped))" "$total" "$wav_name"
        else
            echo "  ERREUR $filename : fichier vide"
            errors=$((errors + 1))
        fi
    else
        echo "  ERREUR $filename : echec"
        errors=$((errors + 1))
    fi
done

echo ""
echo "==========================================="
echo "  Total      : $total"
echo "  Convertis  : $converted"
echo "  Deja faits : $skipped"
echo "  Erreurs    : $errors"
echo "  Sortie     : $OUTPUT_DIR/"
echo "==========================================="
