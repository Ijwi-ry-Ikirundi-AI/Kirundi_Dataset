---
language:
  - rn
license: cc-by-nc-4.0
task_categories:
  - automatic-speech-recognition
  - text-to-speech
  - translation
pretty_name: Kirundi Open Speech & Text Dataset
tags:
  - kirundi
  - low-resource
  - audio
  - speech
size_categories:
  - 1K<n<10K
---

# 🇧🇮 Kirundi Open Speech & Text Dataset

[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](CONTRIBUTING.md)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face-yellow)](https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/data-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset?style=social)](https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset)

**Giving Kirundi a voice in AI.**

[📦 Dataset](#-dataset-at-a-glance) • [🫱🏿‍🫲🏾 Contribute](#-contribute) • [📄 Files](#-files-in-this-repository) • [📚 Citation](#-citation)

## 📦 Dataset at a Glance

|             | Public version (this repository)                                                   | Full dataset (private)                                                    |
| ----------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Content** | Kirundi sentences still to translate, each with an AI draft (`Machine_Suggestion`) | Complete Kirundi ↔ French ↔ English pairs, audio and speaker metadata     |
| **Size**    | 1,813 sentences                                              | 4,809 sentences, 2,996 complete pairs (62%) |
| **Access**  | Free under CC BY-NC 4.0, used by the [Contribution App](https://www.samandari.dev/kirundi-contribution-app/)                 | On request (research, partnerships, commercial licences)                  |

**Your contributions enrich the Ijwi ry'Ikirundi AI dataset, whose full version is private.**

### 📊 Full Dataset in Numbers

| Metric                                         | Value |
| ---------------------------------------------- | ----- |
| 📝 Kirundi sentences                           | 4,809 |
| 🏆 Complete pairs (Kirundi + French + English) | 2,996 (62%) |
| 🔤 Distinct complete Kirundi sentences         | 2,975 |
| 🗂️ Domains                                     | 7: general (2,423), proverbs (1,517), grammar (450), jokes (220), vocabulary (166), action-verbs (25), emotions (8) |
| 🎤 Validated recordings                        | 1 (3 s) |
| 👥 Speakers                                    | 1 (1 male) |
| 📅 Last updated                                | 2026-09-28 |

### 🔑 Access to the Full Dataset

Researchers, partners and companies can request access to the full dataset, including commercial licences. Tell us who you are and what you plan to build: 💬 [Hugging Face discussion](https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset/discussions) · 📱 [WhatsApp](https://wa.me/25777568903) · ✉️ [Email](mailto:cezaremardini10@gmail.com)

### 🔎 Sample of the Full Dataset

<details>
<summary>25 complete rows (Kirundi · French · English · domain)</summary>

| Kirundi | French | English | Domain |
| --- | --- | --- | --- |
| Ndiko ndasoma umuntu. | Je suis en train d'embrasser quelqu'un. | I am kissing someone. | action-verbs |
| Uyu musi ni mwiza. | Cette journée est belle. | This day is beautiful. | general |
| Umwana wanje nyakuri mu kwizera. | Mon véritable enfant dans la foi. | My true child in the faith. | grammar |
| Nakorēsheje amaherá yó kuriha inzu! | j'ai utilisé l'argent de mon loyer. | I used my rent money! | jokes |
| Abagabo bararyá imbwá zikīshura. | Parfois, ce sont les innocents qui paient pour les fautes des coupables. | Sometimes, it's the innocent who pay for the faults of the guilty. | proverbs |
| Iki ni igitabo. | Ceci est un livre. | This is a book. | vocabulary |
| Ndiko ndakoma amashi. | Je suis en train d'applaudir. | I am clapping. | action-verbs |
| Terefone yanje ntikora. | Mon téléphone ne fonctionne pas. | My phone doesn't work. | general |
| Ufise amapfundo abiri, rimwe n’arihe ūtarifise. | Celui qui a deux tuniques, qu'il en donne une à celui qui n'en a pas. | He who has two coats, let him give one to him who has none. | grammar |
| Iyó uríko usaba Amaherá yó gusohoka nyoko wāwe. | Chaque fois que je demande de l'argent à ma mère pour sortir. | Every time I ask my mom for money to go out. | jokes |
| Ikitâzí cīgānzira agahîye. | Les ignorants pensent souvent que toutes les bénédictions leur sont réservées. | The ignorant often assume that all the blessings are reserved for them. | proverbs |
| Hano hari imyungu myinshi. | Il y a beaucoup de courge ici. | There are many pumpkin here. | vocabulary |
| Ndiko ndasoma igitabu. | Je suis en train de lire un livre. | I am reading a book. | action-verbs |
| Murafise indero cane. | Vous êtes très gentil. | You are very kind. | general |
| Yohana amaze gushirwa mw ibohero, Yesu aja i Galilaya. | Quand Jean fut mis en prison, Jésus se rendit en Galilée. | When John had been put in prison, Jesus went to Galilee. | grammar |
| Iyó terekomânde iríko ikora nâbí. | Cette télécommande ne fonctionne pas. | This remote control is not working. | jokes |
| Imbeba irāríye umwôro iguguna urūgi. | Dans la maison d'un pauvre, la souris mange la porte. | In a poor man's home, the mouse eats the door. | proverbs |
| Ndashaka umusigati umwe. | Je veux un canne à sucre. | I want one sugar cane. | vocabulary |
| Ngira noze ivyombo. | Je vais faire la vaisselle. | I'm going to do the dishes. | general |
| Genda ubibwire Yohana, kibuze umuhamagare aze ino. | Va en parler à John, ou bien appelle-le pour qu'il vienne ici. | Go tell John about it, or else call him to come here. | grammar |
| Bella : Hèé màá, utânguriye iphone cumi na gatatu nca nîyahura. | Bella : Maman si tu ne m'achètes pas un Iphone 13 je pourrais me suicider. | Bella: Mom if you don't buy me an Iphone 13 i might kill my self. | jokes |
| Urugó rutagirá umugabo rutāha umugayo. | Une maison sans chef fort est une cible pour le manque de respect. | A home without a strong head is a target for disrespect. | proverbs |
| Iyi ni intumbaswa. | Ceci est un physalis. | This is a physalis. | vocabulary |
| Manjanja aca yiruka kuzana isuka. | Manjanja a couru apporter la houe. | Manjanja ran to bring the hoe. | general |
| Umbwire ivya Matayo. | Parle-moi de Matthieu. | Tell me about Matthew. | grammar |

</details>

## 🌍 About

**Kirundi** is spoken by more than 12 million people, yet it remains a **low-resource language** that most AI systems ignore. Ijwi ry'Ikirundi AI collects Kirundi sentences, their translations and recordings to build:

- 🎙️ **Speech-to-text (ASR)**: in progress
- 🌐 **Machine translation**: our NLLB model [Ijwi-ry-Ikirundi-AI/nllb-kirundi-multi](https://huggingface.co/Ijwi-ry-Ikirundi-AI/nllb-kirundi-multi) (Kirundi ↔ French / English)
- 🗣️ **Text-to-speech (TTS)** and 🎧 **speech translation**: planned

> *Ikirundi cacu, Ijwi ryacu*: our language, our voice.

## 🫱🏿‍🫲🏾 Contribute

| You want to…                         | Where                                                                                                                             |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| Translate sentences (no git, no CSV) | [Contribution App](https://www.samandari.dev/kirundi-contribution-app/)                                                                                                      |
| Add sentences or translations        | Pull request on [GitHub](https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset)                                                  |
| Record audio                         | Pull request on [Hugging Face](https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset) (never on GitHub) |

Rules, quality checklist, recording guidelines and Git workflow: **[CONTRIBUTING.md](CONTRIBUTING.md)**.

## 📄 Files in this Repository

| File              | Content                                                                         |
| ----------------- | ------------------------------------------------------------------------------- |
| `metadata.csv`    | Public version: the Kirundi sentences still to translate, each with an AI draft |
| `clips/`          | Audio recordings (Git LFS)                                                      |
| `CONTRIBUTING.md` | How to contribute                                                               |

`metadata.csv` columns: `ID`, `Kirundi_Transcription`, `French_Translation` and `English_Translation` (empty here, to fill in), `Domain`, `Machine_Suggestion` (AI draft to review, never to copy as is).

## 🎯 Roadmap

1. 📝 **Text collection**: 10,000+ Kirundi sentences (in progress)
2. 🌐 **Translation**: every sentence in French and English (in progress)
3. 🎤 **Audio recording**: 20+ hours of validated speech (in progress)
4. 🤖 **Models**: ASR, TTS and translation for Kirundi

## 📚 Citation

If you use this dataset or mention it in your work, please cite:

```bibtex
@misc{ijwi_kirundi_dataset,
  title        = {Kirundi Open Speech \& Text Dataset},
  author       = {{Ijwi ry'Ikirundi AI}},
  year         = {2024},
  howpublished = {\url{https://huggingface.co/datasets/Ijwi-ry-Ikirundi-AI/Kirundi_Open_Speech_Dataset}}
}
```

## 👥 Contributors

[![Contributors](https://contrib.rocks/image?repo=Ijwi-ry-Ikirundi-AI/Kirundi_Dataset)](https://github.com/Ijwi-ry-Ikirundi-AI/Kirundi_Dataset/graphs/contributors) [![lionel-k](https://images.weserv.nl/?url=github.com/lionel-k.png&h=60&w=60&fit=cover&mask=circle&maxage=7d)](https://github.com/lionel-k)

## ⚖️ License

Data (`metadata.csv`, `clips/`): [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), free for research and non-commercial use, with attribution. Commercial use needs a licence from us: see *Access to the Full Dataset* above. Code: MIT. Details: [LICENSE](LICENSE).

---

**🇧🇮 *Ikirundi cacu, Ijwi ryacu* 🇧🇮**

If this dataset helps your work, ⭐ star the repository and share it with other Kirundi speakers.
