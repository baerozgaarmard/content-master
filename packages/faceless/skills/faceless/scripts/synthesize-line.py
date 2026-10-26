import asyncio
import argparse
import os
import re
import sys
import subprocess
import shutil
import urllib.request
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_ENV_PYTHON = r"C:\Users\Ayush\.gemini\antigravity\scratch\content-master\.ai_env\Scripts\python.exe"

# If current python is not the RVC environment, re-dispatch to .ai_env for RVC characters
if os.path.exists(AI_ENV_PYTHON) and os.path.normpath(sys.executable).lower() != os.path.normpath(AI_ENV_PYTHON).lower():
    # Check if this invocation is for an RVC character
    for i, arg in enumerate(sys.argv):
        if arg == "--voice" and i + 1 < len(sys.argv):
            voice_req = sys.argv[i + 1].lower()
            if voice_req in [
                "walter", "walter-white",
                "elon", "elon-musk",
                "peter", "peter-griffin", "e34b4e061b874623a08f41e5c4fecfb9",
                "stewie", "stewie-griffin", "fdffd3722cd040fcb3f95eec5a7f29f3"
            ]:
                result = subprocess.run([AI_ENV_PYTHON, os.path.abspath(__file__)] + sys.argv[1:])
                sys.exit(result.returncode)

# Fix PyTorch 2.6+ weights_only issue for Fairseq
try:
    import torch
    _orig_torch_load = torch.load
    def _safe_torch_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return _orig_torch_load(*args, **kwargs)
    torch.load = _safe_torch_load
except Exception:
    pass

import edge_tts

VOICESTUDIO_URL = os.environ.get("VOICESTUDIO_URL", "http://127.0.0.1:3900")
VOICES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "voices")

def resolve_model_path(subpath: str) -> str:
    candidates = [
        os.path.join(os.path.dirname(SCRIPT_DIR), "models", subpath),
        os.path.join(r"C:\Users\Ayush\.gemini\antigravity\scratch\content-master\skills\faceless\models", subpath),
        os.path.join(r"C:\Users\Ayush\.gemini\antigravity\skills\faceless\models", subpath),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]

# Character Mapping with Reference Audio & RVC Models
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
    # Peter Griffin (Seth MacFarlane - Family Guy)
    "e34b4e061b874623a08f41e5c4fecfb9": {
        "speaker": "Peter Griffin",
        "reference_wav": os.path.join(VOICES_DIR, "peter_reference.wav"),
        "model_path": resolve_model_path(os.path.join("peter_griffin", "peter.pth")),
        "index_path": resolve_model_path(os.path.join("peter_griffin", "peter.index")),
        "fallback_voice": "en-US-GuyNeural",
        "pitch": "-5Hz",
        "rate": "-5%",
        "f0up_key": 0,
        "index_rate": 0.8,
        "f0method": "pm"
    },
    "peter": {
        "speaker": "Peter Griffin",
        "reference_wav": os.path.join(VOICES_DIR, "peter_reference.wav"),
        "model_path": resolve_model_path(os.path.join("peter_griffin", "peter.pth")),
        "index_path": resolve_model_path(os.path.join("peter_griffin", "peter.index")),
        "fallback_voice": "en-US-GuyNeural",
        "pitch": "-5Hz",
        "rate": "-5%",
        "f0up_key": 0,
        "index_rate": 0.8,
        "f0method": "pm"
    },
    "peter-griffin": {
        "speaker": "Peter Griffin",
        "reference_wav": os.path.join(VOICES_DIR, "peter_reference.wav"),
        "model_path": resolve_model_path(os.path.join("peter_griffin", "peter.pth")),
        "index_path": resolve_model_path(os.path.join("peter_griffin", "peter.index")),
        "fallback_voice": "en-US-GuyNeural",
        "pitch": "-5Hz",
        "rate": "-5%",
        "f0up_key": 0,
        "index_rate": 0.8,
        "f0method": "pm"
    },
    # Stewie Griffin (Seth MacFarlane - Family Guy)
    "fdffd3722cd040fcb3f95eec5a7f29f3": {
        "speaker": "Stewie Griffin",
        "reference_wav": os.path.join(VOICES_DIR, "stewie_reference.wav"),
        "model_path": resolve_model_path(os.path.join("stewie_griffin", "Stewie.pth")),
        "index_path": resolve_model_path(os.path.join("stewie_griffin", "added_IVF425_Flat_nprobe_1_Stewie_v2.index")),
        "fallback_voice": "en-GB-RyanNeural",
        "pitch": "+12Hz",
        "rate": "+10%",
        "f0up_key": 0,
        "index_rate": 0.8,
        "f0method": "pm"
    },
    "stewie": {
        "speaker": "Stewie Griffin",
        "reference_wav": os.path.join(VOICES_DIR, "stewie_reference.wav"),
        "model_path": resolve_model_path(os.path.join("stewie_griffin", "Stewie.pth")),
        "index_path": resolve_model_path(os.path.join("stewie_griffin", "added_IVF425_Flat_nprobe_1_Stewie_v2.index")),
        "fallback_voice": "en-GB-RyanNeural",
        "pitch": "+12Hz",
        "rate": "+10%",
        "f0up_key": 0,
        "index_rate": 0.8,
        "f0method": "pm"
    },
    "stewie-griffin": {
        "speaker": "Stewie Griffin",
        "reference_wav": os.path.join(VOICES_DIR, "stewie_reference.wav"),
        "model_path": resolve_model_path(os.path.join("stewie_griffin", "Stewie.pth")),
        "index_path": resolve_model_path(os.path.join("stewie_griffin", "added_IVF425_Flat_nprobe_1_Stewie_v2.index")),
        "fallback_voice": "en-GB-RyanNeural",
        "pitch": "+12Hz",
        "rate": "+10%",
        "f0up_key": 0,
        "index_rate": 0.8,
        "f0method": "pm"
    },
    # Walter White (Bryan Cranston - Heisenberg)
    "walter": {
        "speaker": "Walter White",
        "reference_wav": os.path.join(VOICES_DIR, "walter_reference.wav"),
        "model_path": resolve_model_path(os.path.join("walter_white", "walt.pth")),
        "index_path": resolve_model_path(os.path.join("walter_white", "added_IVF249_Flat_nprobe_1_walt_v2.index")),
        "fallback_voice": "en-US-BrianNeural",
        "pitch": "-2Hz",
        "rate": "-6%",
        "f0up_key": -1,
        "index_rate": 0.8,
        "f0method": "pm"
    },
    "walter-white": {
        "speaker": "Walter White",
        "reference_wav": os.path.join(VOICES_DIR, "walter_reference.wav"),
        "model_path": resolve_model_path(os.path.join("walter_white", "walt.pth")),
        "index_path": resolve_model_path(os.path.join("walter_white", "added_IVF249_Flat_nprobe_1_walt_v2.index")),
        "fallback_voice": "en-US-BrianNeural",
        "pitch": "-2Hz",
        "rate": "-6%",
        "f0up_key": -1,
        "index_rate": 0.8,
        "f0method": "pm"
    },
    # Elon Musk
    "elon": {
        "speaker": "Elon Musk",
        "reference_wav": os.path.join(VOICES_DIR, "elon_reference.wav"),
        "model_path": resolve_model_path(os.path.join("elon_musk", "Elonmusk (1).pth")),
        "index_path": resolve_model_path(os.path.join("elon_musk", "added_IVF819_Flat_nprobe_1_Elonmusk_v2.index")),
        "fallback_voice": "en-US-EricNeural",
        "pitch": "+0Hz",
        "rate": "-4%",
        "f0up_key": 0,
        "index_rate": 0.8,
        "f0method": "pm"
    },
    "elon-musk": {
        "speaker": "Elon Musk",
        "reference_wav": os.path.join(VOICES_DIR, "elon_reference.wav"),
        "model_path": resolve_model_path(os.path.join("elon_musk", "Elonmusk (1).pth")),
        "index_path": resolve_model_path(os.path.join("elon_musk", "added_IVF819_Flat_nprobe_1_Elonmusk_v2.index")),
        "fallback_voice": "en-US-EricNeural",
        "pitch": "+0Hz",
        "rate": "-4%",
        "f0up_key": 0,
        "index_rate": 0.8,
        "f0method": "pm"
    }
}

def clean_text(raw_text: str) -> str:
    return re.sub(r'^\([a-zA-Z0-9_\-\s]+\)\s*', '', raw_text).strip()

def get_ffmpeg_bin() -> str:
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    cand = os.path.join(os.path.dirname(SCRIPT_DIR), ".runtime", "node_modules", "ffmpeg-static", "ffmpeg.exe")
    if os.path.exists(cand):
        return cand
    cand_global = r"C:\Users\Ayush\.gemini\antigravity\skills\faceless\.runtime\node_modules\ffmpeg-static\ffmpeg.exe"
    if os.path.exists(cand_global):
        return cand_global
    return "ffmpeg"

_rvc_instance = None

def get_rvc_inference():
    global _rvc_instance
    if _rvc_instance is None:
        try:
            from rvc_python.infer import RVCInference
            _rvc_instance = RVCInference(device="cpu:0")
        except Exception as e:
            print(f"[RVC Engine Warning] Failed to initialize RVC: {e}")
            _rvc_instance = False
    return _rvc_instance if _rvc_instance is not False else None

async def try_voicestudio_clone(text: str, char_info: dict, output_path: str) -> bool:
    """Attempts to clone voice using VoiceStudio local API with isolated reference WAV."""
    ref_wav = char_info.get("reference_wav")
    if not ref_wav or not os.path.exists(ref_wav):
        return False

    try:
        req = urllib.request.Request(f"{VOICESTUDIO_URL}/.well-known/voicestudio-speech")
        with urllib.request.urlopen(req, timeout=1) as response:
            if response.status != 200:
                return False
    except Exception:
        return False

    try:
        with open(ref_wav, "rb") as f:
            ref_bytes = f.read()

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

async def try_rvc_conversion(speech_text: str, char_info: dict, output_path: str) -> bool:
    """Performs neural RVC Hugging Face voice conversion."""
    model_path = char_info.get("model_path")
    if not model_path or not os.path.exists(model_path):
        return False

    rvc = get_rvc_inference()
    if not rvc:
        return False

    ffmpeg_bin = get_ffmpeg_bin()
    base_mp3 = output_path + ".base.mp3"
    base_wav = output_path + ".base.wav"
    rvc_out_wav = output_path + ".rvc.wav"

    try:
        # 1. Synthesize base TTS audio
        communicate = edge_tts.Communicate(
            text=speech_text,
            voice=char_info.get("fallback_voice", "en-US-BrianNeural"),
            pitch=char_info.get("pitch", "+0Hz"),
            rate=char_info.get("rate", "+0%")
        )
        await communicate.save(base_mp3)

        # 2. Resample base TTS to 16kHz mono WAV for RVC
        subprocess.run([
            ffmpeg_bin, "-y", "-i", base_mp3,
            "-ar", "16000", "-ac", "1",
            base_wav
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # 3. Load model and run inference
        index_path = char_info.get("index_path", "")
        rvc.load_model(model_path, version="v2", index_path=index_path if os.path.exists(index_path) else "")
        rvc.set_params(
            f0method=char_info.get("f0method", "pm"),
            f0up_key=char_info.get("f0up_key", 0),
            index_rate=char_info.get("index_rate", 0.8),
            protect=char_info.get("protect", 0.33),
            rms_mix_rate=char_info.get("rms_mix_rate", 0.25),
            filter_radius=3
        )
        rvc.infer_file(base_wav, rvc_out_wav)

        # 4. Transcode to high quality 192k MP3
        subprocess.run([
            ffmpeg_bin, "-y", "-i", rvc_out_wav,
            "-c:a", "libmp3lame", "-b:a", "192k",
            output_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        print(f"[RVC Engine] Generated authentic {char_info['speaker']} -> {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"[RVC Engine Warning] Inference failed, falling back: {e}")
        return False
    finally:
        for temp_file in [base_mp3, base_wav, rvc_out_wav]:
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except: pass

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

    # 2. Try RVC Hugging Face Model inference if configured for this character
    if char_info.get("model_path"):
        if await try_rvc_conversion(speech_text, char_info, output_path):
            pad_tail(output_path)
            return

    # 3. Fallback: Edge-TTS synthesis tuned to character cadence
    communicate = edge_tts.Communicate(
        text=speech_text,
        voice=char_info["fallback_voice"],
        pitch=char_info["pitch"],
        rate=char_info["rate"]
    )
    await communicate.save(output_path)
    pad_tail(output_path)

    ref_note = f" (Ref: {os.path.basename(char_info.get('reference_wav', ''))})" if char_info.get('reference_wav') else ""
    print(f"[Speech Engine] Generated {char_info['speaker']}{ref_note} -> {os.path.basename(output_path)}")

def pad_tail(output_path: str):
    """Add a natural conversational pause (180ms) to the tail of each line for organic human turn-taking."""
    try:
        ffmpeg_bin = get_ffmpeg_bin()
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

def main():
    parser = argparse.ArgumentParser(description="VoiceStudio Character Voice Synthesizer")
    parser.add_argument("--text", required=True, help="Dialogue line text")
    parser.add_argument("--voice", required=True, help="Character voice ID")
    parser.add_argument("--output", required=True, help="Destination MP3 path")
    args = parser.parse_args()

    asyncio.run(generate_speech(args.text, args.voice, args.output))

if __name__ == "__main__":
    main()
