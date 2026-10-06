"""Zonas do rosto dos trechos de câmera com animação por cima → hf/data/zonas_rosto.json.

Para cada trecho com "overlay" em hf/data/segments.json, em todos os quadros de origem que o trecho usa:
- topo do cabelo (mínimo): primeira linha do maior componente do matte RVM (work/matte/<TRECHO>.mkv,
  quadro inicial em work/matte/bases.json);
- caixa do rosto: YuNet (work/faces.json), descartando detecções isoladas (centro a mais de 150 px da
  mediana de ±12 quadros).
Faixas livres para gráficos: de y 110 até (topo do cabelo − 30) e de (queixo + 50, arredondado para cima
em 10 px) até y 1650; se o trecho tem legendas visíveis, a faixa de baixo para em 1250 (legendas em 1267–1536).
Uso: zonas_rosto.py
"""
import json, os, subprocess
import numpy as np, cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
segs = json.load(open(f"{ROOT}/hf/data/segments.json"))
edl = json.load(open(f"{ROOT}/work/edl.json"))
bases = json.load(open(f"{ROOT}/work/matte/bases.json"))
caps = json.load(open(f"{ROOT}/work/captions.json"))
faces = {d["f"]: d for d in json.load(open(f"{ROOT}/work/faces.json"))}
fmap = edl["frame_map"]

def read_alpha(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    return np.frombuffer(p, np.uint8).reshape(-1, 1920, 1080)

def face_ok(d):
    near = [faces[q] for q in range(d["f"] - 12, d["f"] + 13) if q in faces]
    my = np.median([n["y"] + n["h"] / 2 for n in near]); mx = np.median([n["x"] + n["w"] / 2 for n in near])
    return abs(d["y"] + d["h"] / 2 - my) < 150 and abs(d["x"] + d["w"] / 2 - mx) < 150

out = {"_nota": "Coordenadas do quadro 1080x1920 da câmera (layout A, sem reescala). Medido em todos os quadros "
                "de origem do trecho: topo do cabelo pelo matte RVM, caixa do rosto pelo YuNet (detecções isoladas "
                "descartadas). 'livre' = faixas onde gráficos podem ficar sem cobrir o rosto (conteúdo sólido em x ≤ 940 quando y entre "
                "900 e 1650). Gerado por scripts/zonas_rosto.py."}
start = 0
for k, s in segs.items():
    a, b = start, start + s["frames"]; start = b
    if not s.get("overlay"): continue
    src = sorted({fmap[i][1] for i in range(a, b)})
    A = read_alpha(f"{ROOT}/work/matte/{k}.mkv")
    tops = []
    for q in src:
        m = (A[q - bases[k]] > 128).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        if n > 1:
            big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); tops.append(int(np.nonzero((lab == big).any(1))[0][0]))
    fs = [faces[q] for q in src if q in faces and face_ok(faces[q])]
    top = min(tops); fy0 = min(d["y"] for d in fs); chin = max(d["y"] + d["h"] for d in fs)
    fx0 = min(d["x"] for d in fs); fx1 = max(d["x"] + d["w"] for d in fs)
    visiveis = any(c["seg"] == k and c["kind"] != "x" for c in caps)
    baixo0 = int(np.ceil((chin + 50) / 10) * 10)
    out[k] = dict(topo_cabelo_min=top, rosto_y=[round(fy0), round(chin)], queixo_max=round(chin), rosto_x=[round(fx0), round(fx1)],
                  livre=[[110, top - 30], [baixo0, 1250 if visiveis else 1650]],
                  legendas="visíveis na faixa y 1267–1536 (não ocupar)" if visiveis else "ocultas (o gráfico mostra a frase)")
    print(k, out[k])
json.dump(out, open(f"{ROOT}/hf/data/zonas_rosto.json", "w"), ensure_ascii=False, indent=1)
