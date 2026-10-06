"""Riser grave crescente (síntese própria): fim audível exatamente na junção gancho → 1º ponto.

- Duração 2,6 s, termina em T_END (junção S1→S2 = 4,500 s).
- Camadas: sub-seno com glissando 42→96 Hz + 2º harmônico, ruído rosa em passa-baixa que abre
  de 180 Hz a 1,4 kHz e leve "shimmer" por modulação de amplitude que acelera (6→14 Hz).
- Envelope exponencial crescente; o ápice fica nos últimos 40 ms e cai a zero em 6 ms
  terminando exatamente em T_END (sem cauda depois da junção).
- Pico ajustado para (pico da voz − 14 dB). Arquivo com a duração total do vídeo.
Uso: riser.py <END_s> <T_END_s> <voice.wav> <saida.wav>
"""
import sys
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, lfilter

SR = 48000
END, T_END, VOICE, OUT = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3], sys.argv[4]
DUR = 2.6
N = int(round(END * SR))
rng = np.random.default_rng(7)

n = int(round(DUR * SR)); t = np.arange(n) / SR; u = t / DUR           # 0 → 1
f = 42 * (96 / 42) ** (u ** 1.6)
ph = 2 * np.pi * np.cumsum(f) / SR
sub = np.sin(ph) + 0.35 * np.sin(2 * ph + 0.3)

# ruído rosa (filtro de Voss-McCartney aproximado por IIR) com passa-baixa variável em blocos
b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]; a = [1, -2.494956002, 2.017265875, -0.522189400]
pink = lfilter(b, a, rng.normal(0, 1, n)); pink /= np.abs(pink).max()
noise = np.zeros(n); blk = 480
zi = None
for i in range(0, n, blk):
    fc = 180 * (1400 / 180) ** (u[i] ** 1.4)
    sos = butter(2, fc, "low", fs=SR, output="sos")
    if zi is None: zi = np.zeros((sos.shape[0], 2))
    seg, zi = sosfilt(sos, pink[i:i + blk], zi=zi)
    noise[i:i + blk] = seg
noise /= np.abs(noise).max()
am_rate = 6 + 8 * u ** 2
shimmer = 1 - 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(am_rate) / SR)) * u

env = (np.expm1(3.2 * u) / np.expm1(3.2))                              # crescimento exponencial
y = (0.85 * sub + 0.55 * noise * shimmer) * env
fo = int(0.006 * SR); y[-fo:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo))   # termina em zero
y[:int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))

v, _ = sf.read(VOICE); vpk = np.abs(v).max()
y *= vpk * 10 ** (-14 / 20) / np.abs(y).max()                        # pico = pico da voz − 14 dB
out = np.zeros(N); i1 = int(round(T_END * SR)); i0 = i1 - n
out[i0:i1] = y
st = np.stack([out, out], 1)
sf.write(OUT, st.astype(np.float32), SR, subtype="FLOAT")
pk = 20 * np.log10(np.abs(out).max())
nz = np.nonzero(np.abs(out) > 10 ** (-80 / 20))[0]
print(f"riser: {i0/SR:.3f}–{i1/SR:.3f} s, pico {pk:.2f} dBFS (voz {20*np.log10(vpk):.2f} dBFS → −14 dB), "
      f"último amostra > −80 dBFS em {nz[-1]/SR*1000:.2f} ms")
