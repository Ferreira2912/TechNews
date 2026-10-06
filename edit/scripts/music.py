"""Trilha original sintetizada (NumPy/SciPy): tropical house leve e ensolarada, 108 BPM, Ré maior.

Instrumentos: violão dedilhado (Karplus-Strong), marimba suave nos contratempos, baixo arredondado,
kick macio, shaker em semicolcheias e estalo de dedo nos tempos 2 e 4. Sem voz e sem melodia
principal. Primeira batida no quadro 1 (t = 1/60 s). Fade-in de 5 ms, fade-out de 800 ms no fim.
Nível único, normalizado a -24 LUFS integrados (sem automação, sem ducking).
Uso: music.py <END_s> <saida.wav>
"""
import sys
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.signal import butter, sosfilt

SR = 48000
END = float(sys.argv[1]); OUT = sys.argv[2]
N = int(round(END * SR))
BPM = 108.0
BEAT = 60.0 / BPM
T0 = 1.0 / 60.0                       # primeira batida no quadro 1
rng = np.random.default_rng(108)
L = np.zeros(N); R = np.zeros(N)

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def add(sig, t, pan=0.0, gain=1.0):
    i = int(round(t * SR))
    if i >= N: return
    s = sig[: N - i] * gain
    gl = np.cos((pan + 1) * np.pi / 4); gr = np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(s)] += s * gl; R[i:i + len(s)] += s * gr
def lp(x, f, order=2): return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)
def bp(x, f1, f2, order=2): return sosfilt(butter(order, [f1, f2], "band", fs=SR, output="sos"), x)

# ---------- instrumentos ----------
def pluck(m, dur=1.2, bright=0.5):
    """Karplus-Strong (corda dedilhada, timbre de violão de nylon)."""
    f = hz(m); p = int(SR / f); n = int(dur * SR)
    buf = lp(rng.uniform(-1, 1, p), 2500 + 3500 * bright, 1)
    y = np.zeros(n); y[:p] = buf
    damp = 0.996
    for i in range(p, n):
        y[i] = damp * 0.5 * (y[i - p] + y[i - p + 1 if i - p + 1 < i else i - p])
    env = np.minimum(1, np.arange(n) / (0.002 * SR))
    return lp(y * env, 5000, 1) * 0.6

def marimba(m, dur=0.6):
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    y = (np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 26)
         + 0.12 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 45))
    return y * np.minimum(1, t / 0.0015)

def bass(m, dur):
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    y = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) + 0.08 * np.sin(2 * np.pi * 3 * f * t)
    env = np.minimum(1, t / 0.012) * (0.55 + 0.45 * np.exp(-t * 3.0)) * np.minimum(1, (dur - t) / 0.04).clip(0, 1)
    return lp(y * env, 700, 2)

def pad(ms, dur):
    """Cama suave de acorde (serras desafinadas, passa-baixa), só para continuidade — sem melodia."""
    t = np.arange(int(dur * SR)) / SR; y = np.zeros(len(t))
    for m in ms:
        for d in (-0.08, 0.08):
            f = hz(m) * 2 ** (d / 12)
            y += 2 * ((t * f) % 1.0) - 1
    env = np.minimum(1, t / 0.35) * np.minimum(1, (dur - t) / 0.35).clip(0, 1)
    return lp(y * env / (2 * len(ms)), 1100, 2)

def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 52 + 70 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t * 9) * np.minimum(1, t / 0.0015)
    click = lp(rng.normal(0, 1, len(t)), 2500, 2) * np.exp(-t * 300) * 0.15
    return y + click

def shaker(acc=1.0):
    n = int(0.09 * SR); t = np.arange(n) / SR
    env = (t / 0.012).clip(0, 1) * np.exp(-np.maximum(0, t - 0.012) * 55)
    return bp(rng.normal(0, 1, n), 5500, 12000, 2) * env * acc

def snap():
    n = int(0.16 * SR); t = np.arange(n) / SR
    y = bp(rng.normal(0, 1, n), 1200, 5000, 2) * np.exp(-t * 38)
    return y + 0.3 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 60)

# ---------- harmonia: I – V – vi – IV em Ré maior (D A Bm G), um acorde por compasso ----------
CHORDS = [(50, [62, 66, 69, 74]), (45, [61, 64, 69, 73]), (47, [62, 66, 71, 74]), (43, [62, 67, 71, 74])]
ARP = [0, 2, 1, 3, 2, 1, 3, 2]          # ordem das notas do dedilhado em colcheias
bar = 4 * BEAT
nbars = int(np.ceil((END - T0) / bar)) + 1
for b in range(nbars):
    t_bar = T0 + b * bar
    root, notes = CHORDS[b % 4]
    # violão dedilhado em colcheias
    for k in range(8):
        t = t_bar + k * BEAT / 2
        m = notes[ARP[k]]
        add(pluck(m, 1.1, 0.35 + 0.15 * (k % 2)), t, pan=-0.35 if k % 2 else -0.15, gain=0.55 if k % 2 else 0.65)
    # marimba nos contratempos (acordes curtos, estilo tropical house)
    for k in range(4):
        t = t_bar + k * BEAT + BEAT / 2
        for j, m in enumerate(notes[1:]):
            add(marimba(m + 12, 0.45), t + j * 0.004, pan=0.35, gain=0.16)
    # baixo arredondado: tempo 1 e "e" do 2, tempo 3 e "e" do 4
    for (pos, d) in [(0, 1.45), (1.5, 0.5), (2, 1.45), (3.5, 0.5)]:
        add(bass(root - 12, d * BEAT), t_bar + pos * BEAT, gain=0.20)
    add(pad([n - 12 for n in notes[:3]], bar + 0.35), t_bar, gain=0.07)
    # bateria
    for k in range(4):
        add(kick(), t_bar + k * BEAT, gain=0.26)
        if k in (1, 3): add(snap(), t_bar + k * BEAT, pan=0.1, gain=0.22)
    for k in range(16):
        acc = [1.0, 0.45, 0.7, 0.45][k % 4]
        add(shaker(acc), t_bar + k * BEAT / 4, pan=0.45, gain=0.13)

mix = np.stack([L, R], 1)
# fade-in de 5 ms (anti-estalo) e fade-out de 800 ms terminando em END
fi = int(0.005 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(0.8 * SR); mix[-fo:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo)))[:, None]
mix[-1] = 0
meter = pyln.Meter(SR)
lufs = meter.integrated_loudness(mix)
mix *= 10 ** ((-24.0 - lufs) / 20)
sf.write(OUT, mix.astype(np.float32), SR, subtype="FLOAT")
print(f"música: {BPM} BPM, primeira batida em {T0*1000:.2f} ms, {lufs:.2f} → -24 LUFS, pico {20*np.log10(np.abs(mix).max()):.2f} dBFS, {len(mix)/SR:.4f} s")
