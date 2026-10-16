#!/usr/bin/env python3
"""beat_reference.py: an independent tempo estimate (numpy only) to cross-check the page. It does NOT share code with the page:
mono 22.05 kHz decode through ffmpeg, a log-compressed spectral-flux onset envelope at about 86 frames a second, its autocorrelation,
and the strongest period in 70 to 180 BPM with a log-Gaussian prior around 120. Prints bpm and the next-best candidates.
  python3 scripts/beat_reference.py <audio file> ..."""
import subprocess, sys
import numpy as np

def decode(path, sr=22050):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32), sr

def tempo(path):
    x, sr = decode(path); hop, nfft = 256, 1024; win = np.hanning(nfft)
    n = (len(x) - nfft) // hop; S = np.empty((n, nfft // 2 + 1), dtype=np.float32)
    for i in range(n): S[i] = np.abs(np.fft.rfft(x[i * hop:i * hop + nfft] * win))
    S = np.log1p(30 * S); flux = np.maximum(0, np.diff(S, axis=0)).sum(axis=1); flux = flux - np.convolve(flux, np.ones(43) / 43, mode='same'); flux[flux < 0] = 0
    fr = sr / hop; f = flux - flux.mean(); ac = np.correlate(f, f, mode='full')[len(f) - 1:]; ac /= ac[0] + 1e-9
    lags = np.arange(int(fr * 60 / 180), int(fr * 60 / 70) + 1); bpm = 60 * fr / lags
    score = np.array([ac[l] + 0.5 * ac[2 * l] if 2 * l < len(ac) else ac[l] for l in lags]) * np.exp(-0.5 * (np.log2(bpm / 120) / 0.9) ** 2)
    order = np.argsort(score)[::-1]; out = []
    for o in order:
        b = bpm[o]
        if all(abs(b - c) > 4 for c in out): out.append(float(b))
        if len(out) == 3: break
    return out

for p in sys.argv[1:]:
    print(p.split('/')[-1], '->', ', '.join(f'{b:.1f}' for b in tempo(p)))
