# 🚀 Ayush Pipeline

**Ayush Pipeline** is an end-to-end autonomous production suite for generating viral, high-retention 60 FPS short-form reels (TikTok, Instagram Reels, YouTube Shorts) featuring iconic voice-cloned characters, sample-accurate acoustic subtitle synchronization, dynamic visual overlays, and automated viral cover art.

---

## 🌟 Key Architecture & Breakthroughs

### 1. Ultra-Natural High-Tempo Voice Synthesis (Hugging Face RVC v2 + PyWorld Harvest)
- **Peter Griffin Voice**: Powered by `Delik/Peter_Griffin_RVCv2` from Hugging Face (`peter_delik.pth` 52.67 MB + `peter_delik.index` **81.57 MB** high-fidelity vocal dataset).
  - Base Voice: `en-US-ChristopherNeural` (`pitch="+1Hz"`, `rate="+15%"` high-energy animated cadence).
  - Pitch Extraction Engine: **PyWorld `Harvest`** (`f0method="harvest"`, `index_rate=0.92`, `protect=0.33`).
  - *Result*: Deep chest resonance, rich vocal fry, and fast comedic Seth MacFarlane inflection—completely eliminating sluggish delivery and robotic buzzing.
- **Stewie Griffin Voice**: Powered by RVC v2 (`Stewie.pth` + `added_IVF425_Flat_nprobe_1_Stewie_v2.index`) with British accent base (`en-GB-RyanNeural`, `rate="+16%"`).
- **Conversational Pace**: Snappy back-and-forth banter targeted for 35–45s total runtime to maximize short-form viral retention.
- **Resampling Uniformity**: Every spoken line is normalized to 44.1 kHz mono PCM (`-ar 44100 -ac 1`) before concatenation.

### 2. Acoustic Speech Burst Subtitle Alignment
- Built-in RMS audio energy burst detection (`energies > 0.015`).
- Divides dialogue clauses into rapid 1–3 word cadence bursts strictly locked to active vocal cords.
- **Zero Subtitle Drift**: Words never persist across silent pauses, breaths, or character transitions.
- **No Annoying Name Tags**: Automatically strips `PETER:` and `STEWIE:` prefixes so the screen stays clean, bold, and focused.

### 3. Genuine Real-Browser Overlays & 60 FPS HD Compositing
- **100% Real Screenshots (Zero Hidden Info Standard)**: Uses headless browser automation (Edge/Chrome) to capture genuine, unedited GitHub repository views. **Never hide, crop out, blur, or obscure any repository metadata**. Always maintain 100% visibility of:
  - Repository owner & name (e.g. `DietrichGebert/ponytail`)
  - Real star counts, watch counters, and forks
  - Verified commit history, branch info, and contributors
  - Full uncropped README sections and real code snippets
- **Gameplay**: 1080×1920 60 FPS smooth parkour background (`minecraft_hd_new.mp4`).
- **Typography**: 96px Arial Black, 12px deep black outline, 5px drop shadow.
  - Peter: High-contrast bright Yellow fill (`&H0033FFFF`).
  - Stewie: High-contrast Cyan fill (`&H00FFFF00`).

### 4. Clean Viral Cover Generation (No AI Slop Boxes)
- High-CTR 1080×1920 cover generation featuring:
  - Clean, bold, viral headline (`STOP LETTING AI WRITE BLOATED CODE!`).
  - **Actual Real GitHub Repository Screenshot** as the prominent centerpiece.
  - Character sticker cutouts (Peter & Stewie).
  - **Zero AI Slop**: Strictly avoids cluttered synthetic pills, cheesy fake badges, and artificial gradient boxes.

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
