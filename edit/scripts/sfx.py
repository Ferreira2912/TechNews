"""Efeitos sonoros sintetizados (NumPy/SciPy) e montagem de stems/sfx.wav.

Tipos e variações (4 por tipo; rodízio, nunca a mesma variação duas vezes seguidas):
  click, tecla, envio, impacto, confirmacao, moeda, passagem
Níveis (pico de amostra relativo ao pico da voz): click/impacto/confirmacao/moeda −10 dB,
passagem −9 dB, tecla/envio −16 dB.
Eventos: hf/comp/<SEG>/events.json (tempo local da seção, somado a start_ms) e
work/overlay_events.json (tempo global). "passagem" usa t = ponto médio do movimento (pico do som).
Uso: sfx.py <END_s> <voice.wav> <saida.wav>      |  sfx.py --preview <saida.wav>
"""
import glob, json, os, sys
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(2024)
def tt(d): return np.arange(int(round(d * SR))) / SR
def bp(x, f1, f2, o=2): return sosfilt(butter(o, [f1, f2], "band", fs=SR, output="sos"), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def atk(t, a): return np.minimum(1, t / a)
def norm(x): return x / np.abs(x).max()
def hz(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- instrumentos ----------------
def click(v):
    f = [1850, 2150, 2450, 1700][v]; dk = [55, 70, 48, 62][v]
    t = tt(0.08)
    tick = np.sin(2 * np.pi * f * t) * np.exp(-t * dk) * atk(t, 0.0006)
    burst = bp(rng.normal(0, 1, len(t)), 2500, 7000) * np.exp(-t * 600)
    body = np.sin(2 * np.pi * [190, 210, 175, 230][v] * t) * np.exp(-t * 90)
    return norm(0.7 * tick + 0.45 * burst + 0.35 * body)

def tecla(v):
    t = tt(0.07)
    c = [3200, 3800, 2900, 3500][v]
    press = bp(rng.normal(0, 1, len(t)), c * 0.6, c * 1.6) * np.exp(-t * 420) + \
        0.6 * np.sin(2 * np.pi * [420, 460, 390, 500][v] * t) * np.exp(-t * 160)
    y = np.zeros(int(0.12 * SR)); y[:len(t)] += press
    g = int([0.034, 0.041, 0.030, 0.038][v] * SR)                            # soltura da tecla, mais baixa
    y[g:g + len(t)] += 0.35 * bp(rng.normal(0, 1, len(t)), c, c * 1.9) * np.exp(-t * 700)
    return norm(y * atk(np.arange(len(y)) / SR, 0.0004))

def envio(v):
    f0, f1 = [(520, 1350), (600, 1500), (470, 1250), (560, 1600)][v]
    d = [0.20, 0.18, 0.22, 0.19][v]; t = tt(d); u = t / d
    f = f0 * (f1 / f0) ** (u ** 0.7); ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) * np.sin(np.pi * np.minimum(1, u * 1.15)) ** 1.5
    air = bp(rng.normal(0, 1, len(t)), 1800, 7000) * np.sin(np.pi * u) ** 2 * 0.35
    return norm(lp(tone + air, 6000))

def impacto(v):
    t = tt(0.75)
    f0, f1, dk = [(72, 44, 7.5), (66, 40, 8.5), (78, 47, 7.0), (69, 42, 9.0)][v]
    f = f1 + (f0 - f1) * np.exp(-t * 18); ph = 2 * np.pi * np.cumsum(f) / SR
    thump = np.sin(ph) * np.exp(-t * dk) * atk(t, 0.002)
    trans = lp(rng.normal(0, 1, len(t)), [1300, 1100, 1500, 1200][v]) * np.exp(-t * 45)
    mid = np.sin(2 * np.pi * [150, 140, 165, 155][v] * t) * np.exp(-t * 22)
    tail = lp(rng.normal(0, 1, len(t)), 400) * np.exp(-t * 6) * 0.25          # cauda curta, abafada
    return norm(thump + 0.55 * trans + 0.3 * mid + tail)

def bell(m, d, bright=1.0):
    t = tt(d); f = hz(m)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 6) + 0.30 * bright * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 11) \
        + 0.12 * bright * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 20) + 0.08 * np.sin(2 * np.pi * f * 4.2 * t) * np.exp(-t * 35)
    return y * atk(t, 0.0015)

def confirmacao(v):
    # notas do campo harmônico de Ré maior (a trilha está em Ré)
    seq = [[81, 86], [78, 81, 86], [86, 90], [76, 81]][v]
    y = np.zeros(int(0.85 * SR))
    for k, m in enumerate(seq):
        b = bell(m, 0.6, 1.0 - 0.15 * k); o = int(k * 0.085 * SR)
        y[o:o + len(b)] += b * (0.85 + 0.15 * k)
    return norm(y)

def moeda(v):
    f0 = [2350, 2620, 2180, 2480][v]
    ratios = [1, 1.47, 2.09, 2.56, 3.21]; dks = [7, 9, 12, 16, 22]
    t = tt(0.55)
    hit = sum(np.sin(2 * np.pi * f0 * r * t + k) * np.exp(-t * d) / (1 + 0.6 * k) for k, (r, d) in enumerate(zip(ratios, dks)))
    hit = hit * atk(t, 0.0005) + 0.4 * hp(rng.normal(0, 1, len(t)), 5000) * np.exp(-t * 300)
    y = np.zeros(int(0.65 * SR)); y[:len(hit)] += hit
    o = int([0.065, 0.075, 0.058, 0.07][v] * SR)                               # quique curto
    y[o:o + len(hit)] += 0.32 * hit[:len(y) - o]
    return norm(y)

def passagem(v, dur=0.5):
    """Whoosh com pico exato no meio do arquivo (o ponto médio do movimento)."""
    d = dur + 0.3; t = tt(d); u = t / d
    c = [(320, 2600, 700), (280, 2300, 600), (360, 2900, 760), (300, 2450, 650)][v]
    fc = np.where(u < 0.5, c[0] * (c[1] / c[0]) ** (u / 0.5), c[1] * (c[2] / c[1]) ** ((u - 0.5) / 0.5))
    x = rng.normal(0, 1, len(t)); y = np.zeros(len(t)); blk = 240; zi = np.zeros((2, 2))
    for i in range(0, len(t), blk):
        sos = butter(2, [fc[i] * 0.55, min(fc[i] * 1.8, 20000)], "band", fs=SR, output="sos")
        seg, zi = sosfilt(sos, x[i:i + blk], zi=zi); y[i:i + blk] = seg
    env = np.where(u < 0.5, (u / 0.5) ** 2.2, ((1 - u) / 0.5) ** 1.6)
    y = norm(y * env)
    pan = np.linspace(-0.6, 0.6, len(t)) * (1 if v % 2 == 0 else -1)
    return np.stack([y * np.cos((pan + 1) * np.pi / 4), y * np.sin((pan + 1) * np.pi / 4)], 1) * np.sqrt(2)

SYN = dict(click=click, tecla=tecla, envio=envio, impacto=impacto, confirmacao=confirmacao, moeda=moeda, passagem=passagem)
LEVEL = dict(click=-10, impacto=-10, confirmacao=-10, moeda=-10, passagem=-9, tecla=-16, envio=-16)
ALIAS = {"confirmação": "confirmacao", "whoosh": "passagem"}

def render(kind, v, **kw):
    y = SYN[kind](v, **kw) if kind == "passagem" else SYN[kind](v)
    if y.ndim == 1: y = np.stack([y, y], 1)
    n = int(0.002 * SR); y[-n:] *= np.linspace(1, 0, n)[:, None]
    return y / np.abs(y).max()

if __name__ == "__main__" and sys.argv[1] == "--preview":
    parts = []
    for k in SYN:
        for v in range(4):
            parts += [render(k, v), np.zeros((int(0.25 * SR), 2))]
        parts.append(np.zeros((int(0.6 * SR), 2)))
    sf.write(sys.argv[2], (np.concatenate(parts) * 0.5).astype(np.float32), SR, subtype="FLOAT")
    sys.exit()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
END = float(sys.argv[1]); N = int(round(END * SR))
vpk = np.abs(sf.read(sys.argv[2])[0]).max(); vdb = 20 * np.log10(vpk)
segs = json.load(open(f"{ROOT}/hf/data/segments.json"))
ev = []
for p in sorted(glob.glob(f"{ROOT}/hf/comp/*/events.json")):
    seg = os.path.basename(os.path.dirname(p))
    for e in json.load(open(p)):
        ev.append(dict(e, t=segs[seg]["start_ms"] / 1000 + e["t"], seg=seg))
ov = f"{ROOT}/work/overlay_events.json"
if os.path.exists(ov):
    ev += [dict(e, seg=e.get("seg", "overlay")) for e in json.load(open(ov))]
for e in ev: e["type"] = ALIAS.get(e["type"], e["type"])
ev.sort(key=lambda e: e["t"])
assert sum(e["type"] == "moeda" for e in ev) <= 3, "no máximo 3 moedas"
assert sum(e["type"] == "passagem" for e in ev) <= 3, "no máximo 3 passagens"
out = np.zeros((N, 2)); last = {}; log = []
for e in ev:
    k = e["type"]; v = (last.get(k, -1) + 1) % 4; last[k] = v
    if k == "passagem":
        y = render(k, v, dur=e.get("dur", 0.5)); i = int(round(e["t"] * SR)) - len(y) // 2
    else:
        y = render(k, v); i = int(round(e["t"] * SR))
    y = y * vpk * 10 ** (LEVEL[k] / 20)
    if i < 0: y = y[-i:]; i = 0
    m = min(len(y), N - i); out[i:i + m] += y[:m]
    log.append(dict(t=round(e["t"], 3), seg=e["seg"], type=k, var=v + 1, peak_db=round(vdb + LEVEL[k], 1), nota=e.get("nota", "")))
fo = int(0.005 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
sf.write(sys.argv[3], out.astype(np.float32), SR, subtype="FLOAT")
json.dump(log, open(f"{ROOT}/work/sfx_log.json", "w"), ensure_ascii=False, indent=1)
for r in log: print(f"{r['t']:7.3f}s  {r['seg']:7s} {r['type']:12s} v{r['var']}  {r['peak_db']:6.1f} dBFS  {r['nota']}")
print(f"sfx: {len(log)} eventos, pico {20*np.log10(np.abs(out).max()+1e-12):.2f} dBFS, {N/SR:.4f} s")
