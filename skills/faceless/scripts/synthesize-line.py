import asyncio
import argparse
import re
import os
import edge_tts
import urllib.request
import json

VOICESTUDIO_URL = os.environ.get("VOICESTUDIO_URL", "http://127.0.0.1:3900")

# Character Voice Presets
VOICE_MAP = {
    # Rick Sanchez (deep, cynical, brisk)
    "d2e75a3e3fd6419893057c02a375a113": {
        "engine": "edge-tts",
        "voice": "en-US-ChristopherNeural",
        "pitch": "-3Hz",
        "rate": "+15%",
        "voicestudio_speaker": "rick_sanchez"
    },
    # Morty Smith (high pitch, anxious, fast)
    "3d445d095ba04681bcba7177faedf55a": {
        "engine": "edge-tts",
        "voice": "en-US-SteffanNeural",
        "pitch": "+12Hz",
        "rate": "+10%",
        "voicestudio_speaker": "morty_smith"
    },
    # Peter Griffin
    "e34b4e061b874623a08f41e5c4fecfb9": {
        "engine": "edge-tts",
        "voice": "en-US-GuyNeural",
        "pitch": "-5Hz",
        "rate": "-5%",
        "voicestudio_speaker": "peter_griffin"
    },
    # Stewie Griffin (British, sharp, animated)
    "fdffd3722cd040fcb3f95eec5a7f29f3": {
        "engine": "edge-tts",
        "voice": "en-GB-RyanNeural",
        "pitch": "+10Hz",
        "rate": "+12%",
        "voicestudio_speaker": "stewie_griffin"
    }
}

def clean_text(raw_text: str) -> str:
    # Strip (excited), (surprised), etc. emotion prefixes from spoken audio
    return re.sub(r'^\([a-zA-Z0-9_\-\s]+\)\s*', '', raw_text).strip()

async def try_voicestudio(text: str, voice_id: str, output_path: str) -> bool:
    """Attempts to generate audio using local VoiceStudio instance if running on port 3900."""
    try:
        req = urllib.request.Request(
            f"{VOICESTUDIO_URL}/v1/audio/speech",
            data=json.dumps({
                "model": "voicestudio-local",
                "input": text,
                "voice": VOICE_MAP.get(voice_id, {}).get("voicestudio_speaker", "default")
            }).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                with open(output_path, "wb") as f:
                    f.write(response.read())
                return True
    except Exception:
        pass
    return False

async def generate_speech(text: str, voice_id: str, output_path: str):
    speech_text = clean_text(text)
    
    # 1. First attempt VoiceStudio local backend (if active)
    if await try_voicestudio(speech_text, voice_id, output_path):
        print(f"Generated via VoiceStudio: {output_path}")
        return

    # 2. Free, zero-setup local neural TTS
    preset = VOICE_MAP.get(voice_id, {
        "voice": "en-US-ChristopherNeural",
        "pitch": "+0Hz",
        "rate": "+0%"
    })
    
    communicate = edge_tts.Communicate(
        text=speech_text,
        voice=preset["voice"],
        pitch=preset["pitch"],
        rate=preset["rate"]
    )
    await communicate.save(output_path)
    print(f"Generated via VoiceStudio Engine: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="VoiceStudio Speech Synthesizer")
    parser.add_argument("--text", required=True, help="Dialogue text")
    parser.add_argument("--voice", required=True, help="Character voice ID")
    parser.add_argument("--output", required=True, help="Output MP3 path")
    args = parser.parse_args()

    asyncio.run(generate_speech(args.text, args.voice, args.output))

if __name__ == "__main__":
    main()
