"""Verificação final de final.mp4 → work/verificacao.json + pranchas em work/verif/.

- formato (resolução, qps, quadros, codecs, áudio 48 kHz estéreo);
- quadros brancos, pretos ou congelados;
- quadros reais dos dois lados de cada corte (prancha de cortes);
- prancha de contato completa (1 quadro a cada 0,5 s);
- sincronia: áudio do MP4 × master (correlação) e início dos fluxos;
- loudness do MP4 (LUFS/pico verdadeiro), duração das stems = END;
- silêncios nas junções da voz (≤ 150 ms), fim audível do riser na junção 4,500 s;
- legendas: dentro das áreas seguras e sem cobrir o rosto (caixa YuNet por quadro);
- cabeça presente no 1º quadro de cada trecho B.
"""
import json, os, re, subprocess, sys
import numpy as np, cv2, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from alpha_io import read_alpha
W, H, FPS = 1080, 1920, 60
OUT = f"{ROOT}/work/verif"; os.makedirs(OUT, exist_ok=True)
FINAL = f"{ROOT}/final.mp4"
segs = json.load(open(f"{ROOT}/hf/data/segments.json"))
edl = json.load(open(f"{ROOT}/work/edl.json"))
END = edl["END"]; NF = edl["END_frames"]
R = {}

# ---------- formato ----------
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", FINAL],
                               capture_output=True, text=True).stdout)
v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
a = [s for s in pr["streams"] if s["codec_type"] == "audio"][0]
R["formato"] = dict(video=f'{v["codec_name"]} {v.get("profile")} {v["width"]}x{v["height"]} {v["r_frame_rate"]} {v["pix_fmt"]} {v.get("color_space")}',
                    quadros=int(v["nb_read_frames"]), duracao_video=float(v["duration"]),
                    audio=f'{a["codec_name"]} {a["sample_rate"]} Hz {a["channels"]} canais {int(a.get("bit_rate", 0))//1000} kb/s',
                    duracao_audio=float(a["duration"]), inicio_video=float(v["start_time"]), inicio_audio=float(a["start_time"]),
                    tamanho_mb=round(int(pr["format"]["size"]) / 2**20, 1))
assert v["width"] == W and v["height"] == H and v["r_frame_rate"] == "60/1" and int(v["nb_read_frames"]) == NF

# ---------- leitura dos quadros (1/4 de resolução para estatísticas) ----------
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", FINAL, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
means, diffs, prev = [], [], None
full = {}
bounds = []
f = 0
for k, s in segs.items():
    bounds.append((k, f)); f += s["frames"]
cut_frames = {b for _, b in bounds[1:]} | {b - 1 for _, b in bounds[1:]}
sheet_frames = set(range(0, NF, 30)) | {NF - 1}
b_first = {b for k, b in bounds if segs[k]["layout"] == "B"}
for i in range(NF):
    buf = p.stdout.read(W * H * 3)
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    sm = cv2.resize(img, (W // 8, H // 8), interpolation=cv2.INTER_AREA).astype(np.float32)
    means.append(float(sm.mean()))
    if prev is not None: diffs.append(float(np.abs(sm - prev).mean()))
    prev = sm
    if i in cut_frames or i in sheet_frames or i in b_first: full[i] = img.copy()
p.stdout.close(); p.wait()
means = np.array(means); diffs = np.array(diffs)
run, best, start = 0, (0, 0), 0
for j, d in enumerate(diffs):
    if d < 0.02: run += 1
    else: run = 0
    if run > best[0]: best = (run, j - run + 2)
R["quadros"] = dict(luminancia_min=round(means.min(), 1), luminancia_max=round(means.max(), 1),
                    brancos=int((means > 245).sum()), pretos=int((means < 8).sum()),
                    maior_sequencia_identica=dict(quadros=best[0] + 1 if best[0] else 1, a_partir_do_quadro=best[1]))

def label(img, txt):
    im = img.copy()
    cv2.putText(im, txt, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 2.4, (0, 0, 0), 10)
    cv2.putText(im, txt, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 2.4, (255, 255, 0), 4)
    return im

# ---------- prancha dos cortes ----------
tiles = []
for k, b in bounds[1:]:
    prevk = [kk for kk, bb in bounds if bb < b][-1]
    tiles.append(np.hstack([cv2.resize(label(full[b - 1], f"{prevk} {b-1}"), (270, 480)),
                            cv2.resize(label(full[b], f"{k} {b}"), (270, 480))]))
rows = [np.hstack(tiles[i:i + 5]) if len(tiles[i:i + 5]) == 5 else np.hstack(tiles[i:i + 5] + [np.zeros_like(tiles[0])] * (5 - len(tiles[i:i + 5])))
        for i in range(0, len(tiles), 5)]
cv2.imwrite(f"{OUT}/cortes.jpg", cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
R["cortes"] = [dict(trecho_anterior=[kk for kk, bb in bounds if bb < b][-1], trecho=k, quadro=b,
                    lum_antes=round(means[b - 1], 1), lum_depois=round(means[b], 1)) for k, b in bounds[1:]]

# ---------- prancha de contato ----------
ks = sorted(sheet_frames)
t = [cv2.resize(label(full[i], f"{i/FPS:.1f}s"), (216, 384)) for i in ks]
while len(t) % 10: t.append(np.zeros_like(t[0]))
cv2.imwrite(f"{OUT}/contato.jpg", cv2.cvtColor(np.vstack([np.hstack(t[i:i + 10]) for i in range(0, len(t), 10)]), cv2.COLOR_RGB2BGR),
            [cv2.IMWRITE_JPEG_QUALITY, 82])

# ---------- cabeça no 1º quadro de cada B ----------
heads = {}
for k, b in bounds:
    if segs[k]["layout"] != "B": continue
    img = full[b].astype(np.int16)
    # região acima do cartão e abaixo de 900 (fora do gráfico): pele/cabelo do apresentador vs. fundo roxo
    reg = img[1000:1195, 200:880]
    purple = (np.abs(reg[..., 0] - 0x63) < 60) & (reg[..., 1] < 60) & (np.abs(reg[..., 2] - 0x5e) < 70)
    heads[k] = dict(quadro=b, fracao_nao_fundo=round(1 - float(purple.mean()), 3))
R["cabeca_primeiro_quadro_B"] = heads

# ---------- áudio ----------
tmp = f"{OUT}/final_audio.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", FINAL, "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_f32le", tmp], check=True)
fa, sr = sf.read(tmp); ma, _ = sf.read(f"{ROOT}/work/master.wav")
n = min(len(fa), len(ma)); x = fa[:n, 0]; y = ma[:n, 0]
seg = slice(int(10 * sr), int(14 * sr))
xc = np.correlate(x[seg], y[seg][2000:-2000], mode="valid")
lag = int(np.argmax(xc)) - 2000
R["sincronia"] = dict(atraso_audio_mp4_vs_master_amostras=lag, atraso_ms=round(lag / sr * 1000, 3),
                      inicio_video=R["formato"]["inicio_video"], inicio_audio=R["formato"]["inicio_audio"])
def ebur(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return dict(lufs=float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1]), true_peak_dbtp=float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", out)[-1]))
R["loudness_mp4"] = ebur(tmp)
R["stems_duracao_s"] = {s: round(sf.info(f"{ROOT}/stems/{s}.wav").frames / 48000, 6) for s in ["voice", "sfx", "riser", "music"]}

# junções da voz: silêncio contínuo (RMS 10 ms abaixo do ruído de fundo + 6 dB) em torno de cada corte
vo, _ = sf.read(f"{ROOT}/stems/voice.wav"); vm = vo[:, 0]
w = int(0.01 * sr); nw = len(vm) // w
rms = 20 * np.log10(np.sqrt((vm[:nw * w].reshape(nw, w) ** 2).mean(1)) + 1e-12)
floor = np.percentile(rms, 5); thr = floor + 6
jun = []
for j in edl["junctions"]:
    c = int(round(j["cut_out"] / 0.01))
    lo = c
    while lo > 0 and rms[lo - 1] < thr: lo -= 1
    hi = c
    while hi < nw and rms[hi] < thr: hi += 1
    jun.append(dict(corte_s=round(j["cut_out"], 3), silencio_ms=(hi - lo) * 10, plano_edl_ms=j["gap_ms"]))
R["juncoes_voz"] = dict(limiar_db=round(thr, 1), juncoes=jun)
ri, _ = sf.read(f"{ROOT}/stems/riser.wav"); rm = np.abs(ri[:, 0])
aud = np.nonzero(rm > 10 ** (-60 / 20))[0]
R["riser"] = dict(inicio_audivel_s=round(aud[0] / sr, 4), fim_audivel_s=round(aud[-1] / sr, 4), juncao_s=4.5,
                  pico_dbfs=round(20 * np.log10(rm.max()), 2), pico_voz_dbfs=round(20 * np.log10(np.abs(vm).max()), 2))
mu, _ = sf.read(f"{ROOT}/stems/music.wav"); mm = np.abs(mu[:, 0])
R["musica"] = dict(primeira_amostra_audivel_ms=round(np.nonzero(mm > 10 ** (-60 / 20))[0][0] / sr * 1000, 2),
                   ultima_amostra_audivel_s=round(np.nonzero(mm > 10 ** (-60 / 20))[0][-1] / sr, 4))

# ---------- legendas × rosto e áreas seguras ----------
faces = json.load(open(f"{ROOT}/work/faces.json"))
fmap = edl["frame_map"]
fidx = {d["f"]: d for d in faces}
caps = json.load(open(f"{ROOT}/work/captions.json"))
S = 1210 / 1080
def face_out(i):
    k = [kk for kk, bb in bounds if bb <= i][-1]
    src = fmap[i][1]
    near = [fidx[q] for q in range(src - 3, src + 4) if q in fidx]
    if not near: return None
    d = near[0]
    if segs[k]["layout"] == "A": return (d["x"], d["y"], d["x"] + d["w"], d["y"] + d["h"])
    if segs[k]["layout"] == "B":
        y0 = segs[k]["b"]["video_y"]
        return (d["x"] * S - 65, d["y"] * S + y0, (d["x"] + d["w"]) * S - 65, (d["y"] + d["h"]) * S + y0)
    return None
probs = []
for c in caps:
    if c["kind"] == "x": continue
    y0b, y1b = c["band"]
    if y1b > 1650 or y0b < 110: probs.append(dict(texto=c["text"], problema="fora da área segura vertical"))
    for i in range(int(round(c["in"] * FPS)), int(round(c["out"] * FPS))):
        fb = face_out(i)
        if fb and fb[3] > y0b - 5 and fb[1] < y1b:
            probs.append(dict(texto=c["text"], quadro=i, rosto_y=[round(fb[1]), round(fb[3])], faixa=[y0b, y1b])); break
R["legendas"] = dict(blocos_visiveis=sum(c["kind"] != "x" for c in caps), ocultos=sum(c["kind"] == "x" for c in caps),
                     largura_max_px=800, x=[140, 940], problemas=probs)
json.dump(R, open(f"{ROOT}/work/verificacao.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1))
