import os
import subprocess
import yt_dlp

FFMPEG = r"C:\Users\Ayush\.gemini\antigravity\skills\faceless\.runtime\node_modules\ffmpeg-static\ffmpeg.exe"
VOICES_DIR = r"C:\Users\Ayush\.gemini\antigravity\scratch\content-master\packages\faceless\skills\faceless\voices"
os.makedirs(VOICES_DIR, exist_ok=True)

def download_and_slice(url: str, output_name: str, start_sec: int, duration_sec: int):
    raw_template = os.path.join(VOICES_DIR, f"{output_name}_raw.%(ext)s")
    final_wav = os.path.join(VOICES_DIR, f"{output_name}.wav")

    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': FFMPEG,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': raw_template,
        'quiet': False
    }

    print(f"Downloading from {url}...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    raw_wav = os.path.join(VOICES_DIR, f"{output_name}_raw.wav")
    if os.path.exists(raw_wav):
        print(f"Slicing clean voice reference: {output_name}.wav...")
        cmd = [
            FFMPEG, "-y",
            "-ss", str(start_sec),
            "-t", str(duration_sec),
            "-i", raw_wav,
            "-ar", "24000",
            "-ac", "1",
            final_wav
        ]
        subprocess.run(cmd, check=True)
        try:
            os.remove(raw_wav)
        except OSError:
            pass
        print(f"Successfully created clean reference: {final_wav}")
    else:
        print(f"Failed to find raw download for {output_name}")

if __name__ == "__main__":
    # 1. Rick Sanchez clean dialogue
    print("--- Fetching Rick Sanchez Reference Voice ---")
    download_and_slice("https://www.youtube.com/watch?v=GKPcHInn14c", "rick_reference", 6, 12)

    # 2. Morty Smith clean dialogue
    print("\n--- Fetching Morty Smith Reference Voice ---")
    download_and_slice("https://www.youtube.com/watch?v=OwCt5skZqWU", "morty_reference", 10, 10)

    print("\nReference voice extraction complete!")
