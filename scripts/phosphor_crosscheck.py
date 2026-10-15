#!/usr/bin/env python3
"""phosphor_crosscheck.py: independent numpy recomputation of the Phosphor band values (check V2).

Decodes a local audio or video file with ffmpeg to mono float samples, then repeats the page's analysis with numpy:
2048-point Hann FFT at 30 frames a second, 64 log bands from 40 Hz to min(16 kHz, 0.45 * sample rate), power in dB,
normalized with the same rule (5th percentile floored at 66 dB under the 99.5th percentile, strided sample).
Prints JSON {"duration": s, "frames": {frame: [64 normalized values]}} for the requested times (fractions of the
duration), so a browser run can compare what the page draws. Usage: phosphor_crosscheck.py FILE FRAC [FRAC ...]
"""
import json, subprocess, sys
import numpy as np

FPS, N, NB = 30, 2048, 64


def main():
    path, fracs = sys.argv[1], [float(x) for x in sys.argv[2:]]
    sr = 44100
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    hop = round(sr / FPS)
    nf = max(1, (len(x) - N) // hop + 1)
    fmax = min(16000.0, sr * 0.45)
    edges = 40.0 * (fmax / 40.0) ** (np.arange(NB + 1) / NB)
    bin_hz = sr / N
    lo, hi = [], []
    for b in range(NB):
        c = np.sqrt(edges[b] * edges[b + 1])
        l, h = int(np.ceil(edges[b] / bin_hz)), int(np.floor(edges[b + 1] / bin_hz))
        if h < l:
            l = h = int(round(c / bin_hz))
        lo.append(max(1, l)); hi.append(max(1, h))
    win = np.hanning(N)
    raw_db = np.empty(nf * NB)
    for f in range(nf):
        seg = x[f * hop: f * hop + N]
        if len(seg) < N:
            seg = np.pad(seg, (0, N - len(seg)))
        spec = np.fft.rfft(seg * win)
        pw = (spec.real ** 2 + spec.imag ** 2)
        for b in range(NB):
            raw_db[f * NB + b] = 10 * np.log10(pw[lo[b]:hi[b] + 1].mean() / (N * N) + 1e-12)
    sample = np.sort(raw_db[::7])
    pick = lambda p: sample[min(len(sample) - 1, int(np.floor(p * (len(sample) - 1))))]
    dhi = pick(0.995)
    dlo = max(pick(0.05), dhi - 66)
    span = max(1.0, dhi - dlo)
    norm = np.clip((raw_db - dlo) / span, 0, 1).reshape(nf, NB)
    dur = len(x) / sr
    frames = {}
    for fr in fracs:
        f = min(nf - 1, max(0, int(np.floor(fr * dur * FPS))))
        frames[str(fr)] = [round(float(v), 4) for v in norm[f]]
    print(json.dumps({"duration": dur, "frames": frames}))


main()
