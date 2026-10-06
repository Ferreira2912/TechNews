"""Montagem final quadro a quadro (NumPy/OpenCV) → work/video.mkv (ou final.mp4 com áudio).

Camadas por trecho (tabela em hf/data/segments.json, mapa de quadros em work/edl.json):
  A  câmera cheia: quadro do bruto em 1080×1920, sem reescala.
  B  dividido: composição gráfica atrás; cartão da câmera 1210×864 em (−65, 1200), cantos superelípticos
     de raio 200, contorno 4 px #FFC300; vídeo escalado para 1210 de largura em (−65, video_y);
     recorte da cabeça (matte RVM do MESMO quadro de origem) por cima do topo do cartão, com
     transição de 40 px na borda do cartão.
  C  composição gráfica cheia.
Gráficos: renderizados a 240 qps e combinados em grupos de 4 quadros (borrão de movimento de
obturador 270°) → 60 qps. Por cima de tudo: camada RGBA de capa/legendas/CTA (sequência PNG).

Uso: compose.py [--out caminho] [--audio master.wav] [--frames a:b] [--stills f1,f2,...]
"""
import argparse, glob, json, os, subprocess, sys
import numpy as np, cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from alpha_io import read_alpha

W, H, FPS = 1080, 1920, 60
RAW = f"{ROOT}/brutoIndiqueeViaje.mp4"
CARD = dict(x=-65, y=1200, w=1210, h=864, r=200)
SCALE = 1210 / 1080
AMARELO = np.array([255, 195, 0], np.float32) / 255
FEATHER = 40

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

# ---------------- máscaras fixas do cartão (superelipse, anti-serrilhado 4x) ----------------
def squircle_mask(x, y, w, h, r, ss=4, n=5.0):
    yy, xx = np.mgrid[0:H * ss, 0:W * ss].astype(np.float32) / ss + 0.5 / ss
    dx = np.maximum(0, np.maximum(x + r - xx, xx - (x + w - r))) / r
    dy = np.maximum(0, np.maximum(y + r - yy, yy - (y + h - r))) / r
    inside = (dx ** n + dy ** n <= 1) & (xx >= x) & (xx <= x + w) & (yy >= y) & (yy <= y + h)
    return inside.reshape(H, ss, W, ss).mean((1, 3)).astype(np.float32)
M_CARD = squircle_mask(CARD["x"], CARD["y"], CARD["w"], CARD["h"], CARD["r"])
M_IN = squircle_mask(CARD["x"] + 4, CARD["y"] + 4, CARD["w"] - 8, CARD["h"] - 8, CARD["r"] - 4)
M_BORDA = np.clip(M_CARD - M_IN, 0, 1)
# sombra de três camadas do sistema visual, projetada pelo cartão sobre o gráfico
SOMBRA = np.zeros((H, W), np.float32)
for oy, blur, a in [(60, 120, 0.28), (24, 48, 0.18), (4, 10, 0.10)]:
    sh = np.zeros_like(M_CARD); sh[oy:] = M_CARD[:-oy]
    SOMBRA = 1 - (1 - SOMBRA) * (1 - a * cv2.GaussianBlur(sh, (0, 0), blur / 2))
# rampa do recorte: opaco acima do topo do cartão, some em 40 px dentro dele
yy = np.arange(H, dtype=np.float32)
u = np.clip((yy - CARD["y"]) / FEATHER, 0, 1)
RAMPA = (1 - u * u * (3 - 2 * u))[:, None]

def warp(img, y0, interp):
    M = np.float32([[SCALE, 0, CARD["x"] - 0.5 + 0.5 * SCALE], [0, SCALE, y0 - 0.5 + 0.5 * SCALE]])
    return cv2.warpAffine(img, M, (W, H), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

ELIPSE = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
def clean_matte(a8):
    """Matte RVM → alfa limpo (0–1, resolução de origem):
    1) abertura morfológica (raio 4) e maior componente conectado: tira pontinhos e apêndices finos
       do fundo grudados no contorno; 2) aperta o alfa baixo (névoa de fundo < 0,25 some) com smoothstep."""
    a = a8.astype(np.float32) / 255
    m = cv2.morphologyEx((a > 0.5).astype(np.uint8), cv2.MORPH_OPEN, ELIPSE(4))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n > 1:
        big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
        keep = cv2.dilate((lab == big).astype(np.uint8), ELIPSE(3)).astype(np.float32)
        a = a * cv2.GaussianBlur(keep, (0, 0), 1.5)
    u = np.clip((a - 0.25) / 0.6, 0, 1)
    return u * u * (3 - 2 * u)

def key_pink(v8, a, ya=950, yb=1200, band=40):
    """Junto ao pescoço/gola (y 950–1200), tira do recorte os pixels rosados do fundo (luminoso rosa atrás
    do apresentador) que o matte deixou na fresta entre pescoço e gola. Só age numa faixa de 40 px na borda."""
    hsv = cv2.cvtColor(v8[ya:yb], cv2.COLOR_RGB2HSV)
    H, S_, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    pink = ((H >= 150) | (H <= 3)) & (S_ > 45) & (V > 150)
    inner = cv2.erode((a[ya:yb] > 0.5).astype(np.uint8), ELIPSE(band)) > 0
    kill = (pink & ~inner & (a[ya:yb] > 0.02)).astype(np.float32)
    if kill.sum() < 1: return a, 0
    kill = cv2.dilate(kill, ELIPSE(2))
    out = a.copy(); out[ya:yb] *= 1 - np.clip(cv2.GaussianBlur(kill, (0, 0), 1.5) * 1.5, 0, 1)
    return out, int(kill.sum())

def key_specks(v8, a, yb=1200, band=30):
    """Pontinhos do fundo (placa branca/azul atrás do apresentador) grudados no contorno da cabeça e do
    pescoço, acima do topo do cartão (y=1200), numa faixa de 30 px da borda do recorte:
    - azul saturado (H 85–135, S>45): nunca é do apresentador (pele, cabelo, camisa branca/roxa);
      saem os blocos de até 3000 px, de qualquer forma;
    - claro sem cor (S<60, V>170): pode ser a camisa, então só saem blocos compactos (20–3000 px,
      ocupando ≥25% da caixa); contornos finos de cabelo e a faixa dos ombros (alongados) ficam."""
    hsv = cv2.cvtColor(v8[:yb], cv2.COLOR_RGB2HSV)
    H, S_, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    inner = cv2.erode((a[:yb] > 0.5).astype(np.uint8), ELIPSE(band)) > 0
    ring = ~inner & (a[:yb] > 0.3)
    kill = np.zeros(ring.shape, np.uint8)
    for cand, compact in ((((H >= 85) & (H <= 135) & (S_ > 45) & (V > 60)) & ring, False),
                          (((S_ < 60) & (V > 170)) & ring, True)):
        n, lab, st, _ = cv2.connectedComponentsWithStats(cand.astype(np.uint8), connectivity=8)
        for j in range(1, n):
            x, y, w_, h_, area = st[j]
            if 20 <= area <= 3000 and (not compact or area >= 0.25 * w_ * h_):
                kill[lab == j] = 1
    if not kill.any(): return a, 0
    kill = cv2.dilate(kill, ELIPSE(5)).astype(np.float32)
    out = a.copy(); out[:yb] *= 1 - np.clip(cv2.GaussianBlur(kill, (0, 0), 1.5) * 1.5, 0, 1)
    return out, int(kill.sum())

def decontaminate(v, a, y1):
    """Borda do recorte: troca a cor contaminada pelo fundo original pela cor do interior vizinho."""
    vv, aa = v[:y1], a[:y1]
    solid = (aa > 0.98).astype(np.float32)
    den = cv2.GaussianBlur(solid, (0, 0), 6)
    num = cv2.GaussianBlur(vv * solid[..., None], (0, 0), 6)
    F = num / np.maximum(den, 1e-3)[..., None]
    w = (np.clip((0.98 - aa) / 0.5, 0, 1) * (den > 0.02))[..., None]
    out = v.copy(); out[:y1] = vv * (1 - w) + F * w
    return out

# ---------------- fontes de quadros ----------------
raw = Reader(RAW)
gfx_cache = {}
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
DIS_Q = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
GX, GY = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
SIGMA_MAX = 40.0
mb_log = {}
pink_log = {}
speck_log = {}

def _flow(a8, b8):
    ga = cv2.cvtColor(cv2.resize(a8, (W // 2, H // 2), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(cv2.resize(b8, (W // 2, H // 2), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    return cv2.resize(DIS.calc(ga, gb, None), (W, H), interpolation=cv2.INTER_LINEAR) * 2

def motion_blur(subs):
    """Borrão de movimento de um quadro de 60 qps a partir de 4 subquadros de 240 qps (obturador 270°).
    Média dos 4 subquadros; quando há deslocamento grande entre eles, completa o intervalo com quadros
    intermediários por fluxo óptico (amostras a cada ~3 px), para o borrão ser contínuo em vez de
    4 cópias. Sigma do borrão = 0,29 × deslocamento no obturador, limitado a 40 px (encurta a janela)."""
    small = [cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA).astype(np.int16) for x in subs]
    if max(np.abs(small[k + 1] - small[k]).max() for k in range(3)) < 4:
        return sum(x.astype(np.float32) for x in subs) / (4 * 255), 0.0
    # estimativa barata (1/4 de resolução, subquadro 0 → 3): derivas lentas não precisam de interpolação
    g0 = cv2.cvtColor(small[0].astype(np.uint8), cv2.COLOR_RGB2GRAY); g3 = cv2.cvtColor(small[3].astype(np.uint8), cv2.COLOR_RGB2GRAY)
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
    acc = np.zeros((H, W, 3), np.float32)
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
    """Quadro j (60 qps) do gráfico do trecho, a partir dos subquadros 4j..4j+3 (240 qps)."""
    st = gfx_cache.get(seg)
    if st is not None and st["r"] is None: return st["img"]
    if st is None or st["j"] > j:
        if st: st["r"].close()
        p240 = f"{ROOT}/work/gfx/{seg}_240.mp4"
        if not os.path.exists(p240) and args.stills:      # prévia de geometria antes do render dos gráficos
            snap = sorted(glob.glob(f"{ROOT}/work/review/{seg}/frame-*.png"))
            img = cv2.imread(snap[0])[..., ::-1].astype(np.float32) / 255 if snap else np.full((H, W, 3), (0.3, 0, 0.29), np.float32)
            gfx_cache[seg] = dict(r=None, j=j, img=img); return img
        st = gfx_cache[seg] = dict(r=Reader(p240), j=-1, img=None)
    if st["j"] != j:
        subs = [st["r"].get(4 * j + q).copy() for q in range(4)]
        st["img"], sig = motion_blur(subs); st["j"] = j
        mb_log[f"{seg}:{j}"] = round(sig, 1)
    return st["img"]

mattes = {}
def matte(seg, j):
    if seg not in mattes: mattes[seg] = read_alpha(f"{ROOT}/work/matte/{seg}.mkv")
    return mattes[seg][j]

ov_files = sorted(glob.glob(f"{ROOT}/work/overlay/*.png"))
if not args.no_overlay: assert len(ov_files) == NF, f"overlay: {len(ov_files)} quadros (esperado {NF})"

def frame(i):
    seg, j = seg_of(i); lay = segs[seg]["layout"]
    take, sf_ = fmap[i]
    if lay == "A":
        out = raw.get(sf_).astype(np.float32) / 255
    elif lay == "C":
        raw.get(sf_)                                   # mantém o leitor sincronizado
        out = gfx_frame(seg, j).copy()
    else:
        v8 = raw.get(sf_)
        y0 = segs[seg]["b"]["video_y"]
        v = warp(v8, y0, cv2.INTER_LANCZOS4).astype(np.float32) / 255
        g = gfx_frame(seg, j) * (1 - SOMBRA[..., None])
        out = g * (1 - M_CARD[..., None]) + v * M_CARD[..., None]
        out = out * (1 - M_BORDA[..., None]) + AMARELO * M_BORDA[..., None]
        a = warp(clean_matte(matte(seg, sf_ - B_SRC0[seg])), y0, cv2.INTER_LINEAR)
        v8w = warp(v8, y0, cv2.INTER_LINEAR)
        a, nk = key_pink(v8w, a)
        if nk: pink_log[i] = nk
        a, ns = key_specks(v8w, a)
        if ns: speck_log[i] = ns
        fg = decontaminate(v, a, CARD["y"] + FEATHER)
        a = a * RAMPA
        out = out * (1 - a[..., None]) + fg * a[..., None]
    if not args.no_overlay:
        o = cv2.imread(ov_files[i], cv2.IMREAD_UNCHANGED)
        oa = o[..., 3:4].astype(np.float32) / 255
        out = out * (1 - oa) + o[..., 2::-1].astype(np.float32) / 255 * oa
    return np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)

# quadro de origem do 1º quadro de cada arquivo de matte (scripts/matte.py <f0>): S1 0, S3c 945, S4b 1343, S6a 2009
B_SRC0 = json.load(open(f"{ROOT}/work/matte/bases.json"))
for s in edl["segments"]:
    if s["layout"] == "B":
        assert s["src_frames"][0] >= B_SRC0[s["id"]], (s["id"], s["src_frames"], B_SRC0[s["id"]])

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
json.dump(pink_log, open(f"{ROOT}/work/pink_key_log.json", "w"))
print(f"chave rosa: {len(pink_log)} quadros B com pixels removidos na borda pescoço/gola")
json.dump(speck_log, open(f"{ROOT}/work/speck_key_log.json", "w"))
print(f"pontinhos do fundo: {len(speck_log)} quadros B com blocos removidos do contorno")
moving = {k: v for k, v in mb_log.items() if v > 0}
print(f"borrão de movimento: {len(moving)} quadros com movimento, sigma máx {max(moving.values(), default=0):.1f} px")
print("ok", args.out)
