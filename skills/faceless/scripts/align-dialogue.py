import os
import sys
import re
import json
import io
import subprocess
import soundfile as sf
import numpy as np

def get_audio_bursts(audio_path):
    cmd = ['ffmpeg', '-v', 'error', '-i', audio_path, '-f', 'wav', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, _ = p.communicate()
    data, sr = sf.read(io.BytesIO(out))
    dur = float(len(data) / sr)

    win = int(sr * 0.02)
    energies = np.array([np.sqrt(np.mean(data[i:i+win]**2)) for i in range(0, len(data), win)])
    times = np.arange(len(energies)) * 0.02

    is_speech = energies > 0.015
    bursts = []
    in_b = False
    s_t = 0
    sil_dur = 0
    for t, sp in zip(times, is_speech):
        if sp:
            if not in_b:
                in_b = True
                s_t = max(0.0, float(t - 0.04))
            sil_dur = 0
        else:
            if in_b:
                sil_dur += 0.02
                if sil_dur >= 0.16:
                    bursts.append((float(round(s_t, 3)), float(round(t - sil_dur + 0.04, 3))))
                    in_b = False
    if in_b:
        bursts.append((float(round(s_t, 3)), float(round(times[-1], 3))))
    return dur, bursts

def split_clauses(text):
    clean = re.sub(r'^\s*\([^)]*\)\s*', '', text).strip()
    parts = [p.strip() for p in re.split(r'([!?,.]+)', clean) if p.strip()]
    clauses = []
    i = 0
    while i < len(parts):
        clause = parts[i]
        if i + 1 < len(parts) and re.match(r'^[!?,.]+$', parts[i+1]):
            clause += parts[i+1]
            i += 2
        else:
            i += 1
        clauses.append(clause)
    return clauses

def words_from(text):
    return re.findall(r"[A-Za-z0-9]+(?:[''\-][A-Za-z0-9]+)*", text)

def stress_word(words):
    if not words:
        return ""
    return max(words, key=len)

def group_words(words, max_size=3):
    groups = []
    for i in range(0, len(words), max_size):
        groups.append(words[i:i+max_size])
    return groups

def align_line_chunks(line_index, line_text, audio_path, base_time):
    dur, bursts = get_audio_bursts(audio_path)
    clean_text = re.sub(r'^\s*\([^)]*\)\s*', '', line_text).strip()
    clauses = split_clauses(clean_text)
    
    chunks = []
    
    if len(clauses) == len(bursts) and len(clauses) > 0:
        for clause, (b_start, b_end) in zip(clauses, bursts):
            words = words_from(clause)
            if not words:
                continue
            groups = group_words(words, max_size=3)
            b_dur = b_end - b_start
            total_len = sum(len(w) for g in groups for w in g)
            g_start = base_time + b_start
            for g in groups:
                g_weight = sum(len(w) for w in g) / max(1, total_len)
                g_dur = b_dur * g_weight
                g_end = g_start + g_dur
                chunks.append({
                    "lineIndex": line_index,
                    "start": round(g_start, 3),
                    "end": round(g_end, 3),
                    "words": [w.upper() for w in g],
                    "stress": stress_word(g).upper()
                })
                g_start = g_end
    else:
        # Fallback to speech burst boundaries without stage directions
        speech_start = bursts[0][0] if bursts else 0.15
        speech_end = bursts[-1][1] if bursts else dur - 0.2
        active_dur = max(0.5, speech_end - speech_start)
        
        words = words_from(clean_text)
        groups = group_words(words, max_size=3)
        total_len = sum(len(w) for g in groups for w in g)
        g_start = base_time + speech_start
        for g in groups:
            g_weight = sum(len(w) for w in g) / max(1, total_len)
            g_dur = active_dur * g_weight
            g_end = g_start + g_dur
            chunks.append({
                "lineIndex": line_index,
                "start": round(g_start, 3),
                "end": round(g_end, 3),
                "words": [w.upper() for w in g],
                "stress": stress_word(g).upper()
            })
            g_start = g_end
            
    return dur, chunks

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    topic = sys.argv[2] if len(sys.argv) > 2 else "prompts-chat"
    
    dialogue_path = os.path.join(root, "faceless-output", "scripts", topic, "dialogue.json")
    audio_dir = os.path.join(root, "faceless-output", "audio", topic)
    out_dir = os.path.join(root, "faceless-output", "video", topic)
    os.makedirs(out_dir, exist_ok=True)
    
    with open(dialogue_path, "r", encoding="utf-8") as f:
        dialogue = json.load(f)
        
    all_chunks = []
    current_time = 0.0
    
    for line in sorted(dialogue, key=lambda x: x["index"]):
        idx = line["index"]
        audio_file = os.path.join(audio_dir, f"{idx:03d}.mp3")
        dur, chunks = align_line_chunks(idx, line["text"], audio_file, current_time)
        all_chunks.extend(chunks)
        current_time += dur
        
    out_file = os.path.join(out_dir, "caption-chunks.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
        
    print(f"Generated {len(all_chunks)} acoustically-aligned chunks -> {out_file} (Total speech: {current_time:.2f}s)")

if __name__ == "__main__":
    main()
