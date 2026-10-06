"""Monta stems/voice.wav a partir da EDL (work/edl.json) e da voz limpa (work/voice_clean_mono.wav).

- Cada tomada entra com J-cut (áudio 50 ms antes do corte de imagem), com fade-in de 5 ms anti-estalo.
- Pausas internas removidas com crossfade de 8 ms nas emendas.
- Cauda de cada frase em volume normal até o ruído de fundo; depois, saída gradual até o
  fim calculado na EDL (nunca passa do início da próxima fala).
- Faixa com duração exata END (48 kHz, estéreo, float32), normalizada a -14 LUFS integrados.
"""
import json
import numpy as np
import soundfile as sf
import pyloudnorm as pyln

SR = 48000
e = json.load(open("work/edl.json"))
END = e["END"]
N = int(round(END * SR))
src, sr = sf.read("work/voice_clean_mono.wav", dtype="float64")
assert sr == SR
out = np.zeros(N)
XF = int(0.008 * SR)

def ramp(n, up=True):
    r = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))
    return r if up else r[::-1]

report = []
for a in e["audio"]:
    k = a["take"]
    take = e["takes"][k - 1]
    # trechos de origem mantidos (com a pré-rolagem do J-cut no primeiro)
    spans = [list(s) for s in take["spans"]]
    spans[0][0] = a["src_in"]
    spans[-1][1] = a["fade_end"]                 # a cauda vai além do corte de imagem
    # posição de saída de cada trecho
    pos = a["out_in"]
    clip = []
    for i, (s0, s1) in enumerate(spans):
        seg = src[int(round(s0 * SR)):int(round(s1 * SR))].copy()
        clip.append((pos, s0, seg))
        pos += s1 - s0
    # monta a tomada num buffer próprio, com crossfades nas emendas internas
    t0 = clip[0][0]
    buf = np.zeros(int(round((pos - t0) * SR)) + XF)
    for i, (p, s0, seg) in enumerate(clip):
        o = int(round((p - t0) * SR))
        g = np.ones(len(seg))
        if i > 0:                                   # entra com crossfade
            g[:XF] *= ramp(XF, True)
        if i < len(clip) - 1:                       # sai com crossfade (estende XF/2 além da emenda)
            g[-XF:] *= ramp(XF, False)
        buf[o:o + len(seg)] += seg * g
    # fade-in anti-estalo de 5 ms
    fi = int(0.005 * SR); buf[:fi] *= ramp(fi, True)
    # cauda: volume normal até o ruído; saída gradual de fade_start até fade_end (tempo de origem)
    last_p, last_s0, last_seg = clip[-1]
    fs_out = last_p + (a["fade_start"] - last_s0) - t0
    fe_out = last_p + (a["fade_end"] - last_s0) - t0
    i0, i1 = int(round(fs_out * SR)), int(round(fe_out * SR))
    buf[i0:i1] *= ramp(i1 - i0, False)
    buf[i1:] = 0
    o = int(round(t0 * SR))
    end = min(N, o + len(buf))
    out[o:end] += buf[:end - o]
    report.append(dict(take=k, out_start=round(t0, 4), out_end=round(t0 + fe_out, 4), fade_ms=round((fe_out - fs_out) * 1000, 1)))

from scipy.signal import resample_poly
from scipy.ndimage import minimum_filter1d

def peak_limit(x, ceiling_db, look_ms=1.5, rel_ms=60.0):
    """Limitador transparente: detecção de pico verdadeiro (4x), lookahead e liberação suave."""
    ceil = 10 ** (ceiling_db / 20)
    tp = np.abs(resample_poly(x, 4, 1)).reshape(-1, 4).max(1)[:len(x)]
    need = np.minimum(1.0, ceil / np.maximum(tp, 1e-12))
    la = max(1, int(look_ms / 1000 * SR))
    need = minimum_filter1d(need, size=2 * la + 1, mode="nearest")   # começa a reduzir antes do pico
    g = np.empty_like(need); cur = 1.0; rc = np.exp(-1.0 / (rel_ms / 1000 * SR))
    for i, v in enumerate(need):
        cur = v if v < cur else v + (cur - v) * rc
        g[i] = cur
    return x * g, g

meter = pyln.Meter(SR)
TARGET, CEIL = -14.0, -1.5
st = lambda v: np.stack([v, v], 1)
lufs0 = meter.integrated_loudness(st(out))
gain_db = TARGET - lufs0
for it in range(8):
    y, g = peak_limit(out * 10 ** (gain_db / 20), CEIL)
    L = meter.integrated_loudness(st(y))
    if abs(L - TARGET) < 0.03: break
    gain_db += TARGET - L
gr = -20 * np.log10(g.min())
red = g < 10 ** (-0.5 / 20)
events = np.count_nonzero(np.diff(red.astype(int)) == 1)
out = y
sf.write("stems/voice.wav", st(out).astype(np.float32), SR, subtype="FLOAT")
gain = 10 ** (gain_db / 20)
print(f"voz: {lufs0:.2f} LUFS (estéreo) → ganho {gain_db:+.2f} dB; limitador: máx {gr:.2f} dB, {events} transientes com >0,5 dB, "
      f"{red.sum()/SR*1000:.0f} ms no total → {L:.2f} LUFS; {len(out)/SR:.4f} s")
for r in report: print("  ", r)
json.dump(dict(gain_db=gain_db, limiter_max_db=gr, limiter_events=int(events), clips=report), open("work/voice_report.json", "w"), indent=1)
