import asyncio
import argparse
import re
import os
import urllib.request
import json
import edge_tts

VOICESTUDIO_URL = os.environ.get("VOICESTUDIO_URL", "http://127.0.0.1:3900")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOICES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "voices")

# Character Mapping with Isolated Reference Audio Samples
CHARACTER_MAP = {
    # Rick Sanchez (deep, cynical, brisk)
    "d2e75a3e3fd6419893057c02a375a113": {
        "speaker": "Rick Sanchez",
        "reference_wav": os.path.join(VOICES_DIR, "rick_reference.wav"),
        "fallback_voice": "en-US-ChristopherNeural",
        "pitch": "-3Hz",
        "rate": "+15%"
    },
    # Morty Smith (high pitch, anxious, fast)
    "3d445d095ba04681bcba7177faedf55a": {
        "speaker": "Morty Smith",
        "reference_wav": os.path.join(VOICES_DIR, "morty_reference.wav"),
        "fallback_voice": "en-US-SteffanNeural",
        "pitch": "+12Hz",
        "rate": "+10%"
    },
    # Peter Griffin
    "e34b4e061b874623a08f41e5c4fecfb9": {
        "speaker": "Peter Griffin",
        "reference_wav": os.path.join(VOICES_DIR, "peter_reference.wav"),
        "fallback_voice": "en-US-GuyNeural",
        "pitch": "-5Hz",
        "rate": "-5%"
    },
    # Stewie Griffin
    "fdffd3722cd040fcb3f95eec5a7f29f3": {
        "speaker": "Stewie Griffin",
        "reference_wav": os.path.join(VOICES_DIR, "stewie_reference.wav"),
        "fallback_voice": "en-GB-RyanNeural",
        "pitch": "+10Hz",
        "rate": "+12%"
    }
}

def clean_text(raw_text: str) -> str:
    return re.sub(r'^\([a-zA-Z0-9_\-\s]+\)\s*', '', raw_text).strip()

async def try_voicestudio_clone(text: str, char_info: dict, output_path: str) -> bool:
    """Attempts to clone voice using VoiceStudio local API with isolated reference WAV."""
    ref_wav = char_info.get("reference_wav")
    if not ref_wav or not os.path.exists(ref_wav):
        return False

    try:
        # Check if VoiceStudio backend is listening
        req = urllib.request.Request(f"{VOICESTUDIO_URL}/.well-known/voicestudio-speech")
        with urllib.request.urlopen(req, timeout=1) as response:
            if response.status != 200:
                return False
    except Exception:
        return False

    # Send zero-shot clone request with reference audio to VoiceStudio
    try:
        with open(ref_wav, "rb") as f:
            ref_bytes = f.read()

        import mimetypes
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = []
        body.extend([
            f'--{boundary}'.encode(),
            b'Content-Disposition: form-data; name="text"',
            b'',
            text.encode('utf-8'),
            f'--{boundary}'.encode(),
            f'Content-Disposition: form-data; name="reference_audio"; filename="{os.path.basename(ref_wav)}"'.encode(),
            b'Content-Type: audio/wav',
            b'',
            ref_bytes,
            f'--{boundary}--'.encode(),
            b''
        ])
        payload = b'\r\n'.join(body)

        clone_req = urllib.request.Request(
            f"{VOICESTUDIO_URL}/v1/audio/clone",
            data=payload,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Content-Length": str(len(payload))
            }
        )
        with urllib.request.urlopen(clone_req, timeout=15) as response:
            if response.status == 200:
                with open(output_path, "wb") as out_f:
                    out_f.write(response.read())
                print(f"[VoiceStudio] Cloned {char_info['speaker']} from {os.path.basename(ref_wav)} -> {output_path}")
                return True
    except Exception as e:
        print(f"[VoiceStudio] Clone notice: {e}")
    return False

async def generate_speech(text: str, voice_id: str, output_path: str):
    speech_text = clean_text(text)
    char_info = CHARACTER_MAP.get(voice_id, {
        "speaker": "Unknown",
        "fallback_voice": "en-US-ChristopherNeural",
        "pitch": "+0Hz",
        "rate": "+0%"
    })

    # 1. Try VoiceStudio zero-shot voice cloning with reference audio
    if await try_voicestudio_clone(speech_text, char_info, output_path):
        return

    # 2. Local fallback using neural synthesis tuned to character cadence
    communicate = edge_tts.Communicate(
        text=speech_text,
        voice=char_info["fallback_voice"],
        pitch=char_info["pitch"],
        rate=char_info["rate"]
    )
    await communicate.save(output_path)

    # Add a natural conversational pause (180ms) to the tail of each line for organic human turn-taking
    try:
        import subprocess
        ffmpeg_bin = os.path.join(os.path.dirname(SCRIPT_DIR), ".runtime", "node_modules", "ffmpeg-static", "ffmpeg.exe")
        if not os.path.exists(ffmpeg_bin):
            ffmpeg_bin = "ffmpeg"
        tmp_pad = output_path + ".pad.mp3"
        subprocess.run([
            ffmpeg_bin, "-y", "-i", output_path,
            "-af", "apad=pad_dur=0.18",
            "-c:a", "libmp3lame", "-b:a", "192k",
            tmp_pad
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(tmp_pad) and os.path.getsize(tmp_pad) > 0:
            os.replace(tmp_pad, output_path)
    except Exception:
        pass

    ref_note = f" (Ref: {os.path.basename(char_info.get('reference_wav', ''))})" if char_info.get('reference_wav') else ""
    print(f"[Speech Engine] Generated {char_info['speaker']}{ref_note} -> {os.path.basename(output_path)}")

def main():
    parser = argparse.ArgumentParser(description="VoiceStudio Character Voice Synthesizer")
    parser.add_argument("--text", required=True, help="Dialogue line text")
    parser.add_argument("--voice", required=True, help="Character voice ID")
    parser.add_argument("--output", required=True, help="Destination MP3 path")
    args = parser.parse_args()

    asyncio.run(generate_speech(args.text, args.voice, args.output))

if __name__ == "__main__":
    main()
