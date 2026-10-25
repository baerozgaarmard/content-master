# Content Master

Open-source tools to turn scripts and transcripts into animations, character reels, and automated video workflows.

Maintained by [Bearozgaarmard](https://github.com/baerozgaarmard).

---

## What's Inside

| Package | Role | Description |
|---|---|---|
| [**`flick`**](packages/flick) | **Motion Director** | Turns videos, links, or transcripts into scene-by-scene animations in Remotion Studio. |
| [**`faceless`**](packages/faceless) | **Dialogue Reels** | Generates Peter & Stewie or Rick & Morty dialogue reels with VoiceStudio local voice cloning and Minecraft parkour backgrounds. |

---

## Demos

### 1. Flick (Scene-by-Scene Remotion Animations)

![Flick motion animations](assets/flick-hero.gif)

Turn a transcript or script into timed, editable scene animations with audio-matched sound effects.

### 2. Faceless (Character Dialogue Shorts)

![Faceless reel generator](assets/faceless.gif)

Split-screen character dialogue reels with local voice cloning, reactive speaker animations, and centered highlight captions.

---

## Installation

### Agent Skills (Codex, Antigravity, Cursor)

```bash
# Install Flick
npx skills add baerozgaarmard/content-master --skill flick --global --yes

# Install Faceless
npx skills add baerozgaarmard/content-master --skill faceless --global --yes
```

### Claude Code Plugins

```bash
# Register marketplace
/plugin marketplace add baerozgaarmard/content-master

# Install skills
/plugin install flick@content-master
/plugin install faceless@content-master
```

---

## Monorepo Structure

```text
content-master/
├── packages/
│   ├── flick/       # Remotion motion director, sound effects & templates
│   └── faceless/    # Character dialogue engine, voice cloning & compositor
├── skills/          # Root skill discovery for npx skills
│   ├── flick/
│   └── faceless/
├── assets/          # Real demo assets
├── package.json
└── LICENSE
```

---

## Search Topics

`ai-video-generator` • `remotion` • `youtube-automation` • `faceless-channel` • `faceless-reels` • `shorts-generator` • `text-to-video` • `whisper` • `voicestudio` • `voice-cloning` • `elevenlabs-alternative` • `bearozgaarmard`

---

## License

MIT © 2026 Bearozgaarmard. Portions derived from Creatorberry under MIT license. See [LICENSE](LICENSE).
