# Contributing to Kirundi Dataset

Thank you for your interest in contributing to the **Kirundi Open Speech & Text Dataset**! This project aims to create the first comprehensive, open-source dataset for the Kirundi language.

## Ways to Contribute

### Text Contributions
- Add clean Kirundi sentences to `metadata.csv`
- Help with text cleaning and validation
- Improve sentence quality and diversity
- Use the [Contribution App](https://www.samandari.dev/kirundi-contribution-app/) for an easy web-based experience

### Translation Contributions
- Translate Kirundi sentences to French or English
- Review and improve existing translations
- Use the [Contribution App](https://www.samandari.dev/kirundi-contribution-app/) (Easy mode: KR→FR, Medium mode: FR→KR)

### Audio Contributions
- Record high-quality Kirundi speech for sentences in `final_dataset_splits/`
- Follow our [Recording Guidelines](README.md#-recording-guidelines)
- Help validate existing recordings through peer review
- Audio must be submitted via [Hugging Face](https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset), **not** GitHub

### Technical Contributions
- Improve automation scripts in `scripts/`
- Enhance the `dataset_manager.ipynb` notebook
- Fix bugs and add features to the data pipeline

## Quality Standards

### Text Normalization Rules

| Rule | Description |
|------|-------------|
| **Full Spelling** | No abbreviations, numbers, symbols (e.g., "4" → "cane") |
| **Ending Punctuation** | Every sentence ends with `.`, `?`, or `!` |
| **Initial Capitalization** | Capitalize only the first word or proper nouns |
| **Diacritics Required** | Keep tonal/long-vowel marks (â, ū, é, í, etc.) |
| **Length Limits** | Ideal: 4–25 words (max 30) |

### Audio Standards
- **Format**: WAV (16-bit, mono, 16kHz)
- **Environment**: Quiet room, no background noise
- **Style**: Natural, clear pronunciation
- **Accuracy**: Read exactly as written

## Submission Process

### For Text/Translations (GitHub)
1. Fork the [GitHub repository](https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset)
2. Create a feature branch (`git checkout -b text/your-contribution`)
3. Add your data to `metadata.csv` (only fill `Kirundi_Transcription`, `French_Translation`, `English_Translation`, `Domain`, `Source`)
4. Do **NOT** modify admin columns (`ID`, `File_Path`, `Duration`, `Audio_Status`, etc.)
5. Submit a Pull Request

### For Audio (Hugging Face)
1. Fork the [Hugging Face dataset](https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset)
2. Pick sentences from `final_dataset_splits/` with `Audio_Status: pending`
3. Record and save audio to `clips/[domain]/`
4. Push to your Hugging Face fork and submit a Pull Request

## Current Priorities

1. **Audio Recording** — Native speakers needed for voice contributions (102/2,903 recorded)
2. **Translation** — 1,826 sentences still need French/English translations
3. **Text Collection** — More diverse Kirundi sentences (target: 10,000+)
4. **Validation** — Peer review of existing recordings

## Getting Help

- Open an [issue](https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset/issues) for questions
- Check the [README](README.md) for detailed documentation
- Use the [Contribution App](https://www.samandari.dev/kirundi-contribution-app/) for the easiest way to help

## Recognition

All contributors will be:
- Listed in our contributors section
- Credited in dataset releases
- Acknowledged in related publications

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, identity, or experience level.

### Our Standards
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Celebrate diverse perspectives

### Unacceptable Behavior
- Harassment or discrimination
- Offensive or inappropriate content
- Spam or self-promotion
- Violation of privacy

## Legal

By contributing, you agree that:
- Your contributions will be licensed under CC BY 4.0
- You have the right to submit your contributions
- Your contributions are original or properly attributed

---

**Thank you for helping preserve and digitize the Kirundi language!**
