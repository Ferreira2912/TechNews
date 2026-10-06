"""Master: soma das quatro stems sem mexer nos níveis; limitador de pico verdadeiro só se passar de −1 dBTP.
Mede LUFS integrado e pico verdadeiro (ffmpeg ebur128) de cada stem e do master → work/loudness.json.
Uso: master.py  (lê stems/*.wav, escreve work/master.wav)
"""
import json, os, re, subprocess
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from scipy.ndimage import minimum_filter1d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
STEMS = ["voice", "sfx", "riser", "music"]

def ebur(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true:framelog=quiet",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])
    tp = float(re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", out)[-1])
    return dict(lufs=I, true_peak_dbtp=tp)

def peak_limit(x, ceiling_db, look_ms=1.5, rel_ms=60.0):
    """Limitador transparente estéreo (canais ligados): pico verdadeiro 4x, lookahead, liberação suave."""
    ceil = 10 ** (ceiling_db / 20)
    tp = np.max([np.abs(resample_poly(x[:, c], 4, 1)).reshape(-1, 4).max(1)[:len(x)] for c in range(x.shape[1])], 0)
    need = np.minimum(1.0, ceil / np.maximum(tp, 1e-12))
    la = max(1, int(look_ms / 1000 * SR))
    need = minimum_filter1d(need, size=2 * la + 1, mode="nearest")
    g = np.empty_like(need); cur = 1.0; rc = np.exp(-1.0 / (rel_ms / 1000 * SR))
    for i, v in enumerate(need):
        cur = v if v < cur else v + (cur - v) * rc
        g[i] = cur
    return x * g[:, None], g

xs = {s: sf.read(f"{ROOT}/stems/{s}.wav", dtype="float64") for s in STEMS}
assert all(sr == SR for _, sr in xs.values())
lens = {k: len(v[0]) for k, v in xs.items()}
assert len(set(lens.values())) == 1, f"stems com durações diferentes: {lens}"
mix = sum(v[0] for v in xs.values())
res = {s: ebur(f"{ROOT}/stems/{s}.wav") for s in STEMS}
sf.write(f"{ROOT}/work/master_soma.wav", mix.astype(np.float32), SR, subtype="FLOAT")
res["soma"] = ebur(f"{ROOT}/work/master_soma.wav")
info = dict(limitador=False)
if res["soma"]["true_peak_dbtp"] > -1.0:
    mix, g = peak_limit(mix, -1.3)
    info = dict(limitador=True, reducao_max_db=round(-20 * np.log10(g.min()), 2),
                ms_com_reducao=round(float((g < 10 ** (-0.1 / 20)).sum()) / SR * 1000, 1))
sf.write(f"{ROOT}/work/master.wav", mix.astype(np.float32), SR, subtype="FLOAT")
res["master"] = dict(ebur(f"{ROOT}/work/master.wav"), duracao_s=len(mix) / SR, **info)
json.dump(res, open(f"{ROOT}/work/loudness.json", "w"), indent=1)
for k, v in res.items(): print(f"{k:7s} {v['lufs']:7.2f} LUFS   {v['true_peak_dbtp']:6.2f} dBTP")
print(info)
