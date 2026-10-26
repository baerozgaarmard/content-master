import os
import sys
import re
import json
import io
import argparse
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
    stop_words = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'from', 'he', 'her', 'his', 'i', 'if', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'our', 'so', 'that', 'the', 'their', 'then', 'there', 'they', 'this', 'to', 'was', 'we', 'what', 'when', 'with', 'you', 'your'}
    for w in reversed(words):
        if w.lower() not in stop_words and len(w) > 2:
            return w
    return words[-1] if words else ""

def group_clause_words(words):
    if len(words) <= 3:
        return [words]
    groups = []
    i = 0
    while i < len(words):
        rem = len(words) - i
        if rem == 4:
            groups.append(words[i:i+2])
            groups.append(words[i+2:i+4])
            break
        elif rem == 5:
            groups.append(words[i:i+3])
            groups.append(words[i+3:i+5])
            break
        elif rem >= 3:
            groups.append(words[i:i+3])
            i += 3
        else:
            groups.append(words[i:])
            break
    return groups

def align_line_chunks(line_index, text, audio_path, base_time):
    dur, bursts = get_audio_bursts(audio_path)
    clauses = split_clauses(text)
    if not bursts:
        bursts = [(0.0, dur)]
        
    num_clauses = len(clauses)
    num_bursts = len(bursts)
    
    # Map clauses to bursts proportionally
    clause_bursts = []
    if num_clauses <= num_bursts:
        indices = np.linspace(0, num_bursts - 1, num_clauses).round().astype(int)
        for idx, cl in zip(indices, clauses):
            clause_bursts.append((cl, bursts[idx][0], bursts[idx][1]))
    else:
        # Fewer bursts than clauses -> subdivide bursts
        total_chars = sum(len(c) for c in clauses)
        b_idx = 0
        for cl in clauses:
            b_s, b_e = bursts[min(b_idx, num_bursts - 1)]
            clause_bursts.append((cl, b_s, b_e))
            if b_idx < num_bursts - 1:
                b_idx += 1
                
    chunks = []
    for cl_text, c_start, c_end in clause_bursts:
        cl_words = words_from(cl_text)
        if not cl_words:
            continue
        c_dur = max(0.2, c_end - c_start)
        groups = group_clause_words(cl_words)
        total_chars = sum(sum(len(w) for w in g) for g in groups)
        
        g_start = c_start
        for g in groups:
            g_weight = sum(len(w) for w in g) / max(1, total_chars)
            g_end = g_start + c_dur * g_weight
            
            clean_g_words = [re.sub(r'^\(+|\)+$', '', w) for w in g]
            clean_g_words = [w for w in clean_g_words if w]
            if clean_g_words:
                chunks.append({
                    "lineIndex": line_index,
                    "start": round(base_time + g_start, 3),
                    "end": round(base_time + g_end, 3),
                    "words": clean_g_words,
                    "stressWord": stress_word(clean_g_words)
                })
            g_start = g_end
            
    return dur, chunks

def main():
    parser = argparse.ArgumentParser(description="Acoustic Dialogue Alignment")
    parser.add_argument("pos_root", nargs="?", default=None, help="Positional root directory")
    parser.add_argument("pos_topic", nargs="?", default=None, help="Positional topic name")
    parser.add_argument("--root", default=".", help="Root directory")
    parser.add_argument("--topic", default="prompts-chat", help="Topic slug")
    parser.add_argument("--dialogue", default=None, help="Path to dialogue JSON")
    parser.add_argument("--audio", default=None, help="Path to master audio file or audio dir")
    parser.add_argument("--output", default=None, help="Path to output caption-chunks.json")
    args = parser.parse_args()

    root = args.pos_root or args.root
    topic = args.pos_topic or args.topic

    if args.dialogue:
        dialogue_path = args.dialogue
    else:
        dialogue_path = os.path.join(root, "faceless-output", "scripts", topic, "dialogue.json")

    audio_dir = os.path.join(root, "faceless-output", "audio", topic)
    if args.output:
        out_file = args.output
        os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)
    else:
        out_dir = os.path.join(root, "faceless-output", "video", topic)
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "caption-chunks.json")
    
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
        
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
        
    print(f"Generated {len(all_chunks)} acoustically-aligned chunks -> {out_file} (Total speech: {current_time:.2f}s)")

if __name__ == "__main__":
    main()
