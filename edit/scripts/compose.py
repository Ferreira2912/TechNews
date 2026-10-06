"""Montagem final quadro a quadro (NumPy/OpenCV) → work/video.mkv (ou final.mp4 com áudio).

Camadas por trecho (tabela em hf/data/segments.json, mapa de quadros em work/edl.json):
  A  câmera cheia: quadro do bruto em 1080×1920, sem reescala nem movimento.
  A+ câmera cheia com animação por cima (segments.json "overlay": true): composição HyperFrames
     transparente renderizada em sequência PNG RGBA a 240 qps (work/gfx/<TRECHO>_240/), aplicada
     sobre o quadro intacto da câmera.
  C  composição gráfica cheia (work/gfx/<TRECHO>_240.mp4).
Gráficos: renderizados a 240 qps e combinados em grupos de 4 quadros (borrão de movimento de
obturador 270°) → 60 qps; nas animações transparentes a média é feita em RGBA pré-multiplicado.
Por cima de tudo: camada RGBA de capa/legendas/CTA (sequência PNG a 60 qps).

Uso: compose.py [--out caminho] [--audio master.wav] [--frames a:b] [--stills f1,f2,...]
"""
import argparse, glob, json, os, subprocess, sys
import numpy as np, cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W, H, FPS = 1080, 1920, 60
RAW = f"{ROOT}/brutoIndiqueeViaje.mp4"

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=f"{ROOT}/work/video.mkv")
ap.add_argument("--audio")
ap.add_argument("--frames")
ap.add_argument("--stills")
ap.add_argument("--no-overlay", action="store_true")
args = ap.parse_args()

edl = json.load(open(f"{ROOT}/work/edl.json"))
segs = json.load(open(f"{ROOT}/hf/data/segments.json"))
fmap = edl["frame_map"]
NF = edl["END_frames"]
order, f = [], 0
for k, s in segs.items():
    order.append((k, f, f + s["frames"])); f += s["frames"]
assert f == NF == len(fmap), (f, NF, len(fmap))
def seg_of(i):
    for k, a, b in order:
        if a <= i < b: return k, i - a
    raise IndexError(i)

def color_args(path):
    cs = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_space",
                         "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    m = {"bt709": "bt709", "smpte170m": "bt601", "bt470bg": "bt601"}.get(cs, "bt709")
    return ["-vf", f"scale=in_color_matrix={m}:in_range=tv:flags=bicubic+accurate_rnd+full_chroma_int,format=rgb24"]

class Reader:
    """Leitura sequencial de quadros RGB por pipe do ffmpeg (sem carregar o vídeo inteiro)."""
    def __init__(self, path):
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path] + color_args(path) +
                                  ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)
        self.i, self.cur = -1, None
    def get(self, f):
        assert f >= self.i, (f, self.i)
        while self.i < f:
            buf = self.p.stdout.read(W * H * 3)
            assert len(buf) == W * H * 3, f"fim inesperado no quadro {self.i + 1}"
            self.cur = np.frombuffer(buf, np.uint8).reshape(H, W, 3); self.i += 1
        return self.cur
    def close(self):
        self.p.stdout.close(); self.p.kill()

class PngSeq:
    """Sequência PNG RGBA do HyperFrames (frame_000001.png …): quadro f (base 0) em RGBA uint8."""
    def __init__(self, folder):
        self.files = sorted(glob.glob(f"{folder}/*.png"))
        assert self.files, f"sem PNGs em {folder}"
    def get(self, f):
        im = cv2.imread(self.files[f], cv2.IMREAD_UNCHANGED)
        assert im is not None and im.shape == (H, W, 4), (self.files[f], None if im is None else im.shape)
        return cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)
    def close(self): pass

def premultiply(rgba):
    a = rgba[..., 3:4].astype(np.uint16)
    out = rgba.copy(); out[..., :3] = ((rgba[..., :3].astype(np.uint16) * a + 127) // 255).astype(np.uint8)
    return out

# ---------------- fontes de quadros ----------------
raw = Reader(RAW)
gfx_cache = {}
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
DIS_Q = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
GX, GY = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
SIGMA_MAX = 40.0
mb_log = {}

def _gray(x):
    """Cinza para o fluxo óptico; RGBA pré-multiplicado é visto sobre cinza médio (o transparente não some)."""
    if x.shape[2] == 4:
        x = (x[..., :3].astype(np.float32) + (255 - x[..., 3:4].astype(np.float32)) * 0.5).clip(0, 255).astype(np.uint8)
    return cv2.cvtColor(x, cv2.COLOR_RGB2GRAY)

def _flow(a8, b8):
    ga = _gray(cv2.resize(a8, (W // 2, H // 2), interpolation=cv2.INTER_AREA))
    gb = _gray(cv2.resize(b8, (W // 2, H // 2), interpolation=cv2.INTER_AREA))
    return cv2.resize(DIS.calc(ga, gb, None), (W, H), interpolation=cv2.INTER_LINEAR) * 2

def motion_blur(subs):
    """Borrão de movimento de um quadro de 60 qps a partir de 4 subquadros de 240 qps (obturador 270°).
    Média dos 4 subquadros; quando há deslocamento grande entre eles, completa o intervalo com quadros
    intermediários por fluxo óptico (amostras a cada ~3 px), para o borrão ser contínuo em vez de
    4 cópias. Sigma do borrão = 0,29 × deslocamento no obturador, limitado a 40 px (encurta a janela).
    Aceita RGB ou RGBA pré-multiplicado (a média e a interpolação valem para os 4 canais)."""
    small = [cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA).astype(np.int16) for x in subs]
    if max(np.abs(small[k + 1] - small[k]).max() for k in range(3)) < 4:
        return sum(x.astype(np.float32) for x in subs) / (4 * 255), 0.0
    # estimativa barata (1/4 de resolução, subquadro 0 → 3): derivas lentas não precisam de interpolação
    g0 = _gray(small[0].astype(np.uint8)); g3 = _gray(small[3].astype(np.uint8))
    fq = DIS_Q.calc(g0, g3, None) * 4
    mq = np.abs(small[3] - small[0]).max(2) > 10
    d_est = float(np.percentile(np.hypot(fq[..., 0], fq[..., 1])[mq], 99)) if mq.sum() > 20 else 0.0
    if d_est < 4.5:
        return sum(x.astype(np.float32) for x in subs) / (4 * 255), 0.29 * d_est
    flows, mags = [], []
    for k in range(3):
        fab, fba = _flow(subs[k], subs[k + 1]), _flow(subs[k + 1], subs[k])
        diff = np.abs(subs[k + 1].astype(np.int16) - subs[k].astype(np.int16)).max(2) > 10
        m = float(np.percentile(np.hypot(fab[..., 0], fab[..., 1])[diff], 99)) if diff.sum() > 50 else 0.0
        flows.append((fab, fba)); mags.append(m)
    D = sum(mags)                                       # deslocamento no obturador (px)
    if D < 4.5:
        return sum(x.astype(np.float32) for x in subs) / (4 * 255), 0.29 * D
    w = min(1.0, SIGMA_MAX / (0.29 * D))                # janela do obturador (fração), limita o sigma
    t0, t1 = 1.5 - 1.5 * w, 1.5 + 1.5 * w
    n = int(np.ceil(D * w / 3.0)) + 1
    acc = np.zeros((H, W, subs[0].shape[2]), np.float32)
    for ts in np.linspace(t0, t1, n).tolist():
        k = min(2, int(np.floor(ts))); a = float(ts - k)
        A, B = subs[k], subs[k + 1]
        if a < 1e-3: acc += A; continue
        if a > 1 - 1e-3: acc += B; continue
        fab, fba = flows[k]
        ia = cv2.remap(A, GX - a * fab[..., 0], GY - a * fab[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        ib = cv2.remap(B, GX - (1 - a) * fba[..., 0], GY - (1 - a) * fba[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        acc += (1 - a) * ia.astype(np.float32) + a * ib.astype(np.float32)
    return acc / (n * 255), 0.29 * D * w

def gfx_frame(seg, j):
    """Quadro j (60 qps) do gráfico do trecho, a partir dos subquadros 4j..4j+3 (240 qps).
    C → RGB em [0,1]; trecho com animação transparente → RGBA pré-multiplicado em [0,1]."""
    st = gfx_cache.get(seg)
    if st is None or st["j"] > j:
        if st: st["r"].close()
        rgba = segs[seg].get("overlay", False)
        src = f"{ROOT}/work/gfx/{seg}_240" + ("" if rgba else ".mp4")
        st = gfx_cache[seg] = dict(r=PngSeq(src) if rgba else Reader(src), j=-1, img=None, rgba=rgba)
    if st["j"] != j:
        subs = [st["r"].get(4 * j + q).copy() for q in range(4)]
        if st["rgba"]: subs = [premultiply(x) for x in subs]
        st["img"], sig = motion_blur(subs); st["j"] = j
        mb_log[f"{seg}:{j}"] = round(sig, 1)
    return st["img"]

ov_files = sorted(glob.glob(f"{ROOT}/work/overlay/*.png"))
if not args.no_overlay: assert len(ov_files) == NF, f"overlay: {len(ov_files)} quadros (esperado {NF})"

def frame(i):
    seg, j = seg_of(i); lay = segs[seg]["layout"]
    take, sf_ = fmap[i]
    if lay == "A":
        out = raw.get(sf_).astype(np.float32) / 255
        if segs[seg].get("overlay"):
            g = gfx_frame(seg, j)                       # RGBA pré-multiplicado
            out = out * (1 - g[..., 3:4]) + g[..., :3]
    elif lay == "C":
        raw.get(sf_)                                   # mantém o leitor sincronizado
        out = gfx_frame(seg, j).copy()
    else:
        raise ValueError(f"layout desconhecido {lay} em {seg}")
    if not args.no_overlay:
        o = cv2.imread(ov_files[i], cv2.IMREAD_UNCHANGED)
        oa = o[..., 3:4].astype(np.float32) / 255
        out = out * (1 - oa) + o[..., 2::-1].astype(np.float32) / 255 * oa
    return np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)

if args.stills:
    os.makedirs(args.out, exist_ok=True)
    for i in sorted(int(x) for x in args.stills.split(",")):
        img = frame(i)
        cv2.imwrite(f"{args.out}/f{i:05d}.png", img[..., ::-1])
    raw.close(); sys.exit()

a, b = (0, NF) if not args.frames else map(int, args.frames.split(":"))
enc = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
if args.audio: enc += ["-i", args.audio]
enc += ["-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=bicubic+accurate_rnd+full_chroma_int,format=yuv420p",
        "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-profile:v", "high", "-level", "4.2", "-g", "120",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
if args.audio: enc += ["-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", "-shortest"]
enc += ["-movflags", "+faststart", args.out] if args.out.endswith(".mp4") else [args.out]
p = subprocess.Popen(enc, stdin=subprocess.PIPE)
for i in range(a, b):
    p.stdin.write(frame(i).tobytes())
    if i % 120 == 0: print(f"quadro {i}/{b}", flush=True)
p.stdin.close(); p.wait(); raw.close()
json.dump(mb_log, open(f"{ROOT}/work/motion_blur_log.json", "w"))
moving = {k: v for k, v in mb_log.items() if v > 0}
print(f"borrão de movimento: {len(moving)} quadros com movimento, sigma máx {max(moving.values(), default=0):.1f} px")
print("ok", args.out)
