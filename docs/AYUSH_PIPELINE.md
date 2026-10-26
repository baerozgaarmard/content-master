# 🚀 Ayush Pipeline

**Ayush Pipeline** is an end-to-end autonomous production suite for generating viral, high-retention 60 FPS short-form reels (TikTok, Instagram Reels, YouTube Shorts) featuring iconic voice-cloned characters, sample-accurate acoustic subtitle synchronization, dynamic visual overlays, and automated viral cover art.

---

## 🌟 Key Architecture & Breakthroughs

### 1. Ultra-Natural Voice Synthesis (Hugging Face RVC v2 + PyWorld Harvest)
- **Peter Griffin Voice**: Powered by `Delik/Peter_Griffin_RVCv2` from Hugging Face (`peter_delik.pth` 52.67 MB + `peter_delik.index` **81.57 MB** high-fidelity vocal dataset).
  - Base Voice: `en-US-ChristopherNeural` (`pitch="+1Hz"`, `rate="+2%"`).
  - Pitch Extraction Engine: **PyWorld `Harvest`** (`f0method="harvest"`, `index_rate=0.92`, `protect=0.33`).
  - *Result*: Deep chest resonance, rich vocal fry, and authentic comedic inflection of Seth MacFarlane—completely eliminating the robotic buzzing and tinny artifacts of older PM pitch models.
- **Stewie Griffin Voice**: Powered by RVC v2 (`Stewie.pth` + `added_IVF425_Flat_nprobe_1_Stewie_v2.index`) with British accent base (`en-GB-RyanNeural`).
- **Resampling Uniformity**: Every spoken line is normalized to 44.1 kHz mono PCM (`-ar 44100 -ac 1`) before concatenation.

### 2. Acoustic Speech Burst Subtitle Alignment
- Built-in RMS audio energy burst detection (`energies > 0.015`).
- Divides dialogue clauses into rapid 1–3 word cadence bursts strictly locked to active vocal cords.
- **Zero Subtitle Drift**: Words never persist across silent pauses, breaths, or character transitions.
- **No Annoying Name Tags**: Automatically strips `PETER:` and `STEWIE:` prefixes so the screen stays clean, bold, and focused.

### 3. High-Impact 60 FPS HD Visual Compositing
- **Gameplay**: 1080×1920 60 FPS smooth parkour background (`minecraft_hd_new.mp4`).
- **Typography**: 96px Arial Black, 12px deep black outline, 5px drop shadow.
  - Peter: High-contrast bright Yellow fill (`&H0033FFFF`).
  - Stewie: High-contrast Cyan fill (`&H00FFFF00`).
- **Authentic Overlays**: Seamlessly fades in genuine GitHub screenshots (`prompts_chat_overlays.json`) at precise timestamps with drop shadows and rounded corner frames.

### 4. Viral 1080×1920 Cover Generation & SEO Bundle
- Autonomous generation of 1080×1920 clickable covers (`generate_cover.py`) featuring:
  - High-saturation dark gradient background.
  - Project screenshot displayed inside an electric cyan glow card.
  - Big bold curiosity-inducing headline.
  - Character sticker cutouts with white outline and drop shadow.
  - Viral badge (`★ 174,000 STARS ON GITHUB | 100% FREE`).
- Automatic generation of SEO title and 4 viral hashtags (`#chatgpt #chatgptprompts #ai #github`).

---

## ⚡ Quick Start

### Run with npm
```bash
# Run Ayush Pipeline for prompts-chat (or any custom topic)
npm run ayush-pipeline -- --topic prompts-chat
```

### Run with Node CLI
```bash
node scripts/ayush-pipeline.mjs --topic prompts-chat
```

---

## 🛠️ CLI Options & Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--topic <name>` | Topic slug identifier | `prompts-chat` |
| `--script <path>` | Custom dialogue JSON path | `faceless-output/scripts/<topic>/dialogue.json` |
| `--template <path>` | Vertical background video | `video-templates/minecraft_hd_new.mp4` |
| `--overlays <path>` | JSON configuration for image overlays | `assets/overlays/prompts_chat_overlays.json` |
| `--output <dir>` | Directory to store output assets | `faceless-output` |
| `--skip-audio` | Skip voice synthesis if audio already exists | `false` |
| `--skip-align` | Skip acoustic burst subtitle alignment | `false` |
| `--skip-video` | Skip 60 FPS video rendering | `false` |
| `--skip-cover` | Skip cover image generation | `false` |

---

## 📁 Pipeline Output Structure

When executed, Ayush Pipeline produces:
```
faceless-output/
├── audio/<topic>/
│   ├── 000.mp3 ... 007.mp3         # Individual character line audio (44.1 kHz mono)
│   └── full-dialogue.mp3           # Seamless master audio track
├── video/<topic>/
│   ├── caption-chunks.json         # Acoustically-aligned micro subtitle chunks
│   ├── caption-timing.ass          # Styled ASS subtitle file
│   └── final-faceless-reel.mp4     # Master 1080x1920 60 FPS reel
├── thumbnails/<topic>/
│   └── cover.png                   # Viral 1080x1920 thumbnail / reel cover
└── seo/
    └── <topic>-seo.json            # High-CTR title & 4 SEO hashtags
```

---

## 🎬 Ayush Pipeline Prompts-Chat Reel Deliverables

- **Master Reel**: `faceless-output/video/prompts-chat/final-faceless-reel.mp4` (66.9s, 1080×1920 @ 60 FPS)
- **Natural Heavy Peter Audio**: `faceless-output/audio/prompts-chat/full-dialogue.mp3`
- **Viral Cover Image**: `faceless-output/thumbnails/prompts-chat/cover.png`
- **SEO Title**: `Stop Paying for ChatGPT Prompts! (174k Star Secret) 🤫`
- **Hashtags**: `#chatgpt #chatgptprompts #ai #github`
