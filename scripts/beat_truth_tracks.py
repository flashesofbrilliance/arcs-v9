#!/usr/bin/env python3
"""beat_truth_tracks.py: synthetic tracks with KNOWN tempo and downbeat for testing the page's beat detection (stdlib plus numpy).
Writes WAVs and truth.json into the folder you name. Truth: bpm (the quarter note), t0 (time of the first beat, seconds), pattern.
  python3 scripts/beat_truth_tracks.py <out-dir> [seconds]"""
import json, math, struct, sys, wave
import numpy as np

SR = 44100
out = sys.argv[1]; secs = float(sys.argv[2]) if len(sys.argv) > 2 else 24.0
rng = np.random.default_rng(20261016)

def kick(n):
    t = np.arange(n) / SR; f = 50 + 110 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 11) * 0.9

def snare(n):
    t = np.arange(n) / SR; nz = rng.standard_normal(n); return (nz * 0.5 + np.sin(2 * np.pi * 190 * t) * 0.4) * np.exp(-t * 22) * 0.6

def hat(n):
    t = np.arange(n) / SR; nz = rng.standard_normal(n); hp = np.diff(nz, prepend=0); return hp * np.exp(-t * 70) * 0.35

def place(buf, w, at):
    i = int(round(at * SR)); n = min(len(w), len(buf) - i)
    if i >= 0 and n > 0: buf[i:i + n] += w[:n]

KN, SN, HN = kick(int(0.4 * SR)), snare(int(0.3 * SR)), hat(int(0.08 * SR))
truth = []
def make(name, bpm, pat, t0=0.37, swing=0.5):
    n = int(secs * SR); buf = np.zeros(n); P = 60.0 / bpm; nb = int(secs / P) + 2
    for b in range(nb):
        t = t0 + b * P; bar = b // 4; beat = b % 4
        if pat == 'four': place(buf, KN, t); place(buf, HN, t + P / 2); (beat in (1, 3)) and place(buf, SN, t)
        elif pat == 'halfkick': (beat in (0, 2)) and place(buf, KN, t); place(buf, HN, t + P / 2); place(buf, HN, t)
        elif pat == 'hats': place(buf, HN, t); place(buf, HN, t + P / 2); (beat == 0) and place(buf, KN * 0.4, t)
        elif pat == 'swing':
            place(buf, KN, t); place(buf, HN, t + swing * P); (beat in (1, 3)) and place(buf, SN, t)
        elif pat == 'break':  # syncopated: kick on 1, the and of 2, 4 and a half of 3; snare on 2 and 4
            if beat == 0: place(buf, KN, t)
            if beat == 1: place(buf, SN, t); place(buf, KN, t + P / 2)
            if beat == 2: place(buf, KN, t + P * 0.75)
            if beat == 3: place(buf, SN, t)
            place(buf, HN, t + P / 2)
    buf = buf / (np.max(np.abs(buf)) + 1e-9) * 0.8
    pcm = (buf * 32767).astype('<i2')
    with wave.open(f"{out}/{name}.wav", 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    truth.append({'name': name, 'bpm': bpm, 't0': t0, 'pattern': pat, 'swing': swing})

for bpm in (70, 100, 120, 128, 140, 150, 174):
    for pat in ('four', 'break', 'halfkick', 'hats'): make(f"{pat}-{bpm}", bpm, pat)
    make(f"swing-{bpm}", bpm, 'swing', swing=0.62)
json.dump(truth, open(f"{out}/truth.json", 'w'), indent=1); print(len(truth), 'tracks in', out)
