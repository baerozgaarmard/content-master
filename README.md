# Content Master

Open-source tools to turn scripts and transcripts into animations, character reels, and automated video workflows.

Maintained by [Bearozgaarmard](https://github.com/baerozgaarmard).

---

## What's Inside

| Package | Role | Description |
|---|---|---|
| [**`flick`**](packages/flick) | **Motion Director** | Turns videos, links, or transcripts into scene-by-scene animations in Remotion Studio. |
| [**`faceless`**](packages/faceless) | **Dialogue Reels** | Generates Peter & Stewie or Rick & Morty dialogue reels with VoiceStudio / free local voice synthesis and Minecraft parkour backgrounds. |
| [**`mcp`**](packages/mcp) | **Agent Connector** | Connects Claude Code, Codex, and Antigravity agents to video analytics, outlier hooks, and transcript tools. |

---

## Demos

### 1. Flick (Scene-by-Scene Remotion Animations)

![Flick motion animations](assets/flick-hero.gif)

Turn a transcript or script into timed, editable scene animations with audio-matched sound effects.

### 2. Faceless (Character Dialogue Shorts)

![Faceless reel generator](assets/faceless.gif)

Split-screen character dialogue reels with voice generation, reactive speaker animations, and centered highlight captions.

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

### Content Master MCP

```bash
# Claude Code
npx --yes github:baerozgaarmard/content-master install --client claude

# Codex
npx --yes github:baerozgaarmard/content-master install --client codex
```

---

## Monorepo Structure

```text
content-master/
├── packages/
│   ├── flick/       # Remotion motion director, sound effects & templates
│   ├── faceless/    # Character dialogue engine, sprites & compositor
│   └── mcp/         # MCP server connector and CLI
├── skills/          # Root skill discovery for npx skills
│   ├── flick/
│   └── faceless/
├── assets/          # Real demo assets
├── package.json
└── LICENSE
```

---

## Local Development

```bash
git clone https://github.com/baerozgaarmard/content-master.git
cd content-master

# Run tests
npm test

# Check syntax
npm run check
```

---

## Search Topics

`ai-video-generator` • `remotion` • `youtube-automation` • `faceless-channel` • `faceless-reels` • `shorts-generator` • `text-to-video` • `whisper` • `voicestudio` • `voice-cloning` • `elevenlabs-alternative` • `claude-code` • `mcp-server` • `bearozgaarmard`

---

## License

MIT © 2026 Bearozgaarmard. Portions derived from Creatorberry under MIT license. See [LICENSE](LICENSE).
