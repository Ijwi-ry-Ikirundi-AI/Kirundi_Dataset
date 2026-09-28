# Contributing to Kirundi Dataset

Thanks for helping build Kirundi speech and text data.

This repo is **data-only** and holds the **public version** of the dataset:

- `metadata.csv` — the Kirundi sentences that still need a translation, each with an AI draft (`Machine_Suggestion`).
- `clips/` — audio recordings (Git LFS).

The **full dataset** (complete Kirundi ↔ French ↔ English pairs, audio and speaker metadata) is private and maintained by the Ijwi ry'Ikirundi AI team in **Dataset-Management**. Accepted contributions are merged into it, and the next public version drops the sentences you translated.

---

## Quick map

| You want to…                       | Where                                                                                           | How                                      |
| ---------------------------------- | ----------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Translate / add sentences (no git) | [Contribution App](https://www.samandari.dev/kirundi-contribution-app/)                         | Easy / Medium / Hard → Google Sheets     |
| Add text / translations via PR     | [GitHub](https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset)                                | Edit `metadata.csv` → PR                 |
| Add audio                          | [Hugging Face](https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset) | WAV in `clips/` → HF PR (**not** GitHub) |
| Audit / merge / clean / export     | Dataset-Management                                                                              | Local back-office (maintainers)          |

This project has two homes:

- **Text, translations, or docs** → [GitHub](https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset)
- **Audio** → [Hugging Face](https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset) (required)

---

## Option 1 — Text / translation (GitHub)

**Goal:** Provide clean, high-quality Kirundi sentences and translations.

### What you may contribute

- Kirundi → French / English translations of the sentences already in `metadata.csv`
- New Kirundi sentences, with their translation
- Optional `Domain`

### Required columns

- `Kirundi_Transcription` → **required**
- `French_Translation` **or** `English_Translation` → **required (at least one)**
- Leave `ID` and `Machine_Suggestion` as they are

### Steps

#### 1. Fork & clone

Fork and clone: [https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset](https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset)

Branch example: `text/short-description`

#### 2. Quality & normalization (Kirundi_Transcription)

To keep ASR/TTS training clean, every Kirundi sentence must follow:

| Rule                       | Description                                                                  | Why it matters                     |
| -------------------------- | ---------------------------------------------------------------------------- | ---------------------------------- |
| **Full spelling**          | No abbreviations, numbers, symbols (e.g. `4` → `kane`; avoid `&`, `@`, etc.) | Models learn sounds, not shortcuts |
| **Ending punctuation**     | Every sentence ends with `.`, `?`, or `!`                                    | Helps TTS boundaries and tone      |
| **Initial capitalization** | Capitalize only the first word or proper nouns                               | Supports capitalization training   |
| **Diacritics**             | Keep tonal/long-vowel marks (`â`, `ū`, `é`, `í`, …) if the source uses them  | Pronunciation & prosody            |
| **Length**                 | Ideal 4–25 words (max ~30)                                                   | Easier recording and ASR alignment |

#### 3. Add your data

Open `metadata.csv`: translate existing rows, or add new rows at the end. Fill **only**:

| Column                  | Required         | Notes                                        |
| ----------------------- | ---------------- | -------------------------------------------- |
| `Kirundi_Transcription` | Yes              | Original Kirundi sentence                    |
| `French_Translation`    | Yes (or English) | High-quality translation                     |
| `English_Translation`   | Optional         | May be filled later if omitted               |
| `Domain`                | Optional         | `general`, `proverbs`, `grammar`, `jokes`, … |

Mention the source of new sentences (URL, book, document) in the pull request description.

#### Do not modify

- `ID` — assigned by maintainers (leave it empty on new rows)
- `Machine_Suggestion` — AI draft: a help to start from, **never** copy it as the translation without checking it

Audio and speaker columns are not part of the public file: maintainers add them to the full dataset.

#### 4. Pull request

Commit → push fork → open a PR on GitHub.  
Prefer conventional commits, e.g. `docs(data): add greetings batch`.

### Contribution App (no CSV)

Non-technical contributors can use
**[kirundi-contribution-app](https://www.samandari.dev/kirundi-contribution-app/)**:

- **Easy** — Kirundi → French
- **Medium** — French → Kirundi
- **Hard** — new KR + FR pairs

The app reads the public `metadata.csv` from Hugging Face. Submissions go to Google Sheets; maintainers review and merge them into the full dataset with **Dataset-Management**, then publish a new public version here and on Hugging Face.

### Maintainer ops

Text cleaning, Sheet merges, exports, splits, and AI assist run in the private **Dataset-Management** project — not in this repository.

---



## Option 2 — Audio (Hugging Face — critical)

**Goal:** High-quality Kirundi speech recordings.

**This step must be done on Hugging Face.**  
**Do not push audio files to GitHub.** Submit audio only on Hugging Face (Git LFS).

### Step 0 — First-time setup

1. Fork the [Hugging Face dataset](https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset).
2. Clone your fork (replace `Your-HF-Username`):

```bash
git clone https://huggingface.co/datasets/Your-HF-Username/Kirundi_Open_Speech_Dataset
cd Kirundi_Open_Speech_Dataset
```

3. Install Git LFS (one-time):

```bash
git lfs install
```

Download: [git-lfs.github.com](https://git-lfs.github.com/)

### Step 1 — Record

1. Pick a sentence in `metadata.csv` (or ask the maintainers for a recording list).
2. Record it following the [Recording guidelines](#recording-guidelines) below.
3. Save the file into `clips/<domain>/` using the [naming convention](#audio-naming-convention).
4. In the pull request description, list for each file: the sentence (ID or text), `Speaker_id`, `Age`, `Gender` and, if known, `Duration`. Maintainers add them to the full dataset.

#### Audio metadata normalization

| Column       | Required format                   | Explanation                 |
| ------------ | --------------------------------- | --------------------------- |
| `Speaker_id` | Anonymous, e.g. `S01_M`           | Privacy + consistency       |
| `Age`        | Ranges, e.g. `20s`, `30s`, `40s+` | Diversity without exact age |
| `Gender`     | `male`, `female` or `other`       | Balanced voices             |
| `Duration`   | Float seconds, e.g. `3.15`        | Text–audio alignment        |

### Step 2 — Submit

```bash
git add .
git commit -m "Added new audio clip clips/jokes/20260131_S01_M_jokes_krd_000001.wav"
git push
```

Git LFS uploads the audio. Then open a **Pull Request on Hugging Face**.

### Audio naming convention

```
Path: clips/[DOMAIN]/[DATE]_[SPEAKER]_[DOMAIN]_[SENTENCE_ID].wav
Example: clips/jokes/20260131_S01_M_jokes_krd_000001.wav

Speaker IDs:
- S01_M: César (Male)
- S02_M: Arsène (Male)
- S03_F: Blanche (Female)

Domain folders (examples):
proverbs, action-verbs, grammar, vocabulary, general, emotions,
jokes, adjectives, idioms, language, geography, food, greetings,
politeness, location, apologies, advice, time, adverbs
```

Maintainers process and validate recordings with Dataset-Management (peer review: `pending` → `recorded` → `validated` or `rejected`).

---

## Recording guidelines

### Best practices

| Aspect             | Requirement                         | Why                  |
| ------------------ | ----------------------------------- | -------------------- |
| **Environment**    | Quiet room, no background noise     | Clean training data  |
| **Microphone**     | Headset mic or phone close to mouth | Clear capture        |
| **Speaking style** | Natural, clear pronunciation        | Realistic speech     |
| **Accuracy**       | Read exactly as written             | Text–audio alignment |

### Technical specs

```yaml
Audio Format:
  - Primary: WAV (uncompressed)
  - Alternative: MP3 (high quality)

Settings:
  - Sample Rate: 16kHz or 22.05kHz
  - Channels: Mono (1 channel)
  - Bit Depth: 16-bit
  - Duration: Natural sentence length
```

### Recommended tools

- [Audacity](https://www.audacityteam.org/) (free, cross-platform)
- ASR Voice Recorder (Android)
- Smartphone built-in recorder
- Online recorders for quick takes

---

## Git workflow (maintainers)

**Never push directly to** `main` **on GitHub.** Use feature branches and PRs.

### One-time setup

```bash
git remote add hf https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset.git
git remote add origin https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset
git remote -v

# macOS
brew install git-lfs
git lfs install
```

### Standard flow: GitHub PR → Hugging Face

```bash
git checkout -b feature/your-feature-name
git add .
git commit -m "Your descriptive commit message"
git push origin feature/your-feature-name
# Open PR on GitHub → merge to main

git checkout main
git pull origin main
git push hf main
```

### How Git LFS works

Git stores tiny **pointer** files; real audio lives on the LFS server (GitHub and/or Hugging Face). Pushing to a remote uploads LFS objects for that remote. The git history stays small.

```
Local clips/*.wav
        │
        ├──▶ GitHub   (pointer + LFS object)
        └──▶ Hugging Face (pointer + LFS object)
```

### Branch & commit (devs)

- Branches: `type/short-kebab` — e.g. `text/add-greetings`, `docs/fix-contributing`
- Messages: `type(scope): description` — imperative, no trailing period
- Do not commit `.env`, secrets, `models/`, or training artifacts here

---

## Current priorities

1. Audio for complete sentences (native speakers)
2. French / English for the sentences in `metadata.csv`
3. More diverse Kirundi text (target 10k+)
4. Peer review of recordings

---

## Help

- Issues: [GitHub Issues](https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset/issues)
- Access to the full dataset: [open a discussion on Hugging Face](https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset/discussions)
- App: [Contribution App](https://www.samandari.dev/kirundi-contribution-app/)
- Project overview: [README](README.md)

---

## License & conduct

- Data (`metadata.csv`, `clips/`): **CC BY-NC 4.0** — research and non-commercial use with attribution; commercial use needs a licence from Ijwi ry'Ikirundi AI. Code: MIT. See [LICENSE](LICENSE).
- By contributing you confirm you have the rights to what you submit (your own text, translations and voice, or material you may share).
- You grant Ijwi ry'Ikirundi AI a perpetual, worldwide, royalty-free, non-exclusive licence to use, modify, publish and relicense your contribution — including in the private full dataset and under commercial licences. You keep the right to use your own contribution as you wish.
- Be respectful. No harassment, spam, or privacy violations.

**Ikirundi cacu, Ijwi ryacu.**
