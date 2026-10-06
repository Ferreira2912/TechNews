"""Prancha de revisão de uma composição: snapshots do HyperFrames + guias + peças de referência lado a lado.

- Trechos C: o snapshot como está, com as linhas das áreas seguras.
- Trechos A com animação por cima (segments.json "overlay": true): o snapshot (transparente) é aplicado
  sobre o quadro REAL da câmera daquele instante (mesmo mapa de quadros da montagem), com a caixa do
  rosto (YuNet) em vermelho, o topo do cabelo em laranja e a zona livre para gráficos em verde.

Uso: .venv/bin/python scripts/review_sheet.py <SEG> <t1> <t2> ... [--ref=peca2,peca4]
Saída: work/review/<SEG>_sheet.jpg (e os PNGs em work/review/<SEG>/)
"""
import glob, json, os, subprocess, sys
import cv2, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
seg = args[0]
refs = ["peca2"]
times = []
for a in args[1:]:
    if a.startswith("--ref="): refs = [r for r in a.split("=", 1)[1].split(",") if r]
    else: times.append(float(a))
segs = json.load(open(f"{ROOT}/hf/data/segments.json"))
layout = segs[seg]["layout"]; overlay = segs[seg].get("overlay", False)
out = f"{ROOT}/work/review/{seg}"
os.makedirs(out, exist_ok=True)
for f in glob.glob(f"{out}/frame-*.png"): os.remove(f)
cmd = ["npx", "--prefix", f"{ROOT}/hf", "hyperframes", "snapshot", f"{ROOT}/hf/comp/{seg}", "--at",
       ",".join(f"{t:.3f}" for t in times), "--no-end", "-o", out]
subprocess.run(cmd, check=True, capture_output=True)
frames = sorted(glob.glob(f"{out}/frame-*.png"))

edl = json.load(open(f"{ROOT}/work/edl.json"))
fmap = edl["frame_map"]
start = 0
for k, s in segs.items():
    if k == seg: break
    start += s["frames"]
faces = {d["f"]: d for d in json.load(open(f"{ROOT}/work/faces.json"))}
ZONES = json.load(open(f"{ROOT}/hf/data/zonas_rosto.json")) if os.path.exists(f"{ROOT}/hf/data/zonas_rosto.json") else {}

def raw_frame(src):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{src / 60:.6f}", "-i", f"{ROOT}/brutoIndiqueeViaje.mp4",
                        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    return np.frombuffer(p, np.uint8).reshape(1920, 1080, 3).copy()

def face_near(src):
    for q in sorted(range(src - 3, src + 4), key=lambda q: abs(q - src)):
        if q in faces: return faces[q]
    return None

tiles = []
for f in frames:
    t = float(os.path.basename(f).split("-at-")[1].replace("s.png", "").replace(".png", ""))
    im = cv2.imread(f, cv2.IMREAD_UNCHANGED)
    if overlay:
        i = min(start + segs[seg]["frames"] - 1, start + int(round(t * 60)))
        src = fmap[i][1]
        bg = raw_frame(src).astype(np.float32)
        a = im[..., 3:4].astype(np.float32) / 255 if im.shape[2] == 4 else np.ones(im.shape[:2] + (1,), np.float32)
        im = (bg * (1 - a) + im[..., :3].astype(np.float32) * a).astype(np.uint8)
        d = face_near(src)
        if d: cv2.rectangle(im, (int(d["x"]), int(d["y"])), (int(d["x"] + d["w"]), int(d["y"] + d["h"])), (0, 0, 255), 4)
        z = ZONES.get(seg)
        if z:
            cv2.line(im, (0, z["topo_cabelo_min"]), (1080, z["topo_cabelo_min"]), (0, 140, 255), 3)
            cv2.line(im, (0, z["queixo_max"]), (1080, z["queixo_max"]), (0, 140, 255), 3)
            for y0, y1 in z["livre"]:
                cv2.rectangle(im, (60, y0), (920, y1), (0, 220, 0), 3)
    else:
        im = im[..., :3] if im.shape[2] == 4 else im
    lines = [(110, (0, 255, 255)), (1650, (0, 255, 255))]
    if layout == "C": lines += [(1200, (255, 255, 0)), (1230, (255, 255, 0))]
    for y, c in lines: cv2.line(im, (0, y), (1080, y), c, 2)
    cv2.line(im, (940, 900), (940, 1650), (0, 255, 255), 2)
    label = f"{t:.2f}s"
    cv2.putText(im, label, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (0, 0, 0), 9)
    cv2.putText(im, label, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (255, 255, 255), 3)
    tiles.append(cv2.resize(im, (360, 640)))
for r in refs:
    im = cv2.imread(f"{ROOT}/hf/assets/pecas/{r}.png")
    cv2.putText(im, "REF " + r, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (0, 0, 0), 9)
    cv2.putText(im, "REF " + r, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (0, 255, 255), 3)
    tiles.append(cv2.resize(im, (360, 640)))
cols = 6
while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
sheet = np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)])
cv2.imwrite(f"{ROOT}/work/review/{seg}_sheet.jpg", sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
print(f"{ROOT}/work/review/{seg}_sheet.jpg")
