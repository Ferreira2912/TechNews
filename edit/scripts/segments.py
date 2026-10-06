"""work/edl.json → hf/data/segments.json e segments.js (tempos locais por trecho, para as composições).

Mantém os dados do layout dividido (video_y, cartão, topo da cabeça) já medidos em work/b_geometry.json
e na versão anterior de segments.json, e atualiza data-duration de cada composição em hf/comp/<TRECHO>.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = json.load(open(f"{ROOT}/work/edl.json"))
geo = json.load(open(f"{ROOT}/work/b_geometry.json"))
old = json.load(open(f"{ROOT}/hf/data/segments.json")) if os.path.exists(f"{ROOT}/hf/data/segments.json") else {}
segs = {}
for s in e["segments"]:
    a, b = s["out_in"], s["out_out"]
    ws = [dict(w=w["w"], t=round(w["start"] - a, 3), end=round(min(w["end"], b) - a, 3), filler=w["filler"])
          for w in e["words"] if a - 1e-6 <= w["start"] < b - 1e-6]
    d = dict(id=s["id"], layout=s["layout"], start_ms=round(a * 1000, 1), end_ms=round(b * 1000, 1),
             duration=round(s["frames"] / 60, 6), frames=s["frames"], words=ws, content=s["content"])
    if s["layout"] == "B":
        d["b"] = dict(old.get(s["id"], {}).get("b", {}), video_y=geo[s["id"]]["y0"],
                      card={"x": -65, "y": 1200, "w": 1210, "h": 864})
    segs[s["id"]] = d
json.dump(segs, open(f"{ROOT}/hf/data/segments.json", "w"), ensure_ascii=False, indent=1)
open(f"{ROOT}/hf/data/segments.js", "w").write(
    "/* Gerado por scripts/segments.py a partir de work/edl.json → tempos locais por trecho (s). Não editar. */\n"
    "window.SEGMENTS = " + json.dumps(segs, ensure_ascii=False) + ";\n")
END = round(sum(s["frames"] for s in segs.values()) / 60, 6)
for k, s in list(segs.items()) + [("OVERLAY", dict(duration=END))]:
    p = f"{ROOT}/hf/comp/{k}/index.html"
    if not os.path.exists(p): continue
    html = open(p).read()
    new = re.sub(r'data-duration="[\d.]+"', f'data-duration="{s["duration"]:.6f}"', html, count=1)
    if new != html:
        open(p, "w").write(new); print(f"{k}: data-duration → {s['duration']:.6f}")
for k, s in segs.items():
    print(f"{k:4s} {s['layout']} {s['start_ms']:8.1f}–{s['end_ms']:8.1f} {s['frames']:4d} q  " + " ".join(f"{w['w']}@{w['t']}" for w in s["words"][:4]))
print("END", END)
