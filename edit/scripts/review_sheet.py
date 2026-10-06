"""Prancha de revisão de uma composição: snapshots do HyperFrames + guia da cabeça (layout B)
+ linhas das áreas seguras + peças de referência lado a lado.

Uso: .venv/bin/python scripts/review_sheet.py <SEG> <t1> <t2> ... [--ref peca2,peca4]
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
    if a.startswith("--ref="): refs = a.split("=", 1)[1].split(",")
    else: times.append(float(a))
segs = json.load(open(f"{ROOT}/hf/data/segments.json"))
layout = segs[seg]["layout"]
out = f"{ROOT}/work/review/{seg}"
os.makedirs(out, exist_ok=True)
for f in glob.glob(f"{out}/frame-*.png"): os.remove(f)
cmd = ["npx", "--prefix", f"{ROOT}/hf", "hyperframes", "snapshot", f"{ROOT}/hf/comp/{seg}", "--at",
       ",".join(f"{t:.3f}" for t in times), "--no-end", "-o", out]
subprocess.run(cmd, check=True, capture_output=True)
frames = sorted(glob.glob(f"{out}/frame-*.png"))
guide = None
if layout == "B":
    g = cv2.imread(f"{ROOT}/hf/guides/{seg}_head.png", cv2.IMREAD_UNCHANGED)
    guide = (g[..., :3], g[..., 3:4].astype(np.float32) / 255)
tiles = []
for f in frames:
    im = cv2.imread(f)
    if guide is not None:
        im = (im * (1 - guide[1]) + guide[0] * guide[1]).astype(np.uint8)
        cv2.rectangle(im, (-65, 1200), (1145, 2064), (0, 195, 255), 4)  # cartão da câmera
    lines = [(110, (0, 255, 255))]
    lines += [(900, (255, 255, 0))] if layout == "B" else [(1200, (255, 255, 0)), (1230, (255, 255, 0)), (1650, (0, 255, 255))]
    for y, c in lines: cv2.line(im, (0, y), (1080, y), c, 2)
    if layout != "B": cv2.line(im, (940, 900), (940, 1650), (0, 255, 255), 2)
    t = os.path.basename(f).split("-at-")[1].replace(".png", "")
    cv2.putText(im, t, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (0, 0, 0), 9)
    cv2.putText(im, t, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (255, 255, 255), 3)
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
