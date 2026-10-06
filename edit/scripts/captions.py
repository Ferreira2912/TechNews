"""Blocos de legenda a partir dos tempos finais das palavras (hf/data/segments.json).

Plano por trecho: lista de (nº de palavras, tipo). Tipos:
  n = bloco normal (branco),  h = destaque (amarelo, MAIÚSCULAS),
  x = oculto porque o gráfico já mostra a mesma frase (o gráfico faz o papel do destaque).
Palavras marcadas como hesitação (filler) não entram nas legendas.
Saídas: hf/data/captions.js (window.CAPTIONS) e work/captions.json.
"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 60
segs = json.load(open(f"{ROOT}/hf/data/segments.json"))
END = sum(s["frames"] for s in segs.values()) / FPS

PLAN = {
    "S1":  [(3, "n"), (3, "n"), (1, "h"), (2, "n"), (3, "n"), (3, "n"), (2, "h")],
    "S2":  [(2, "n"), (3, "x"), (3, "n"), (3, "n")],
    "S3a": [(2, "n"), (2, "h")],
    "S3b": [(2, "n"), (2, "x"), (2, "x"), (3, "x"), (3, "n"), (1, "h"), (2, "n"), (3, "n")],
    "S3c": [(11, "x")],
    "S4a": [(3, "n"), (2, "n"), (1, "h")],
    "S4b": [(7, "x")],
    "S5a": [(3, "h"), (2, "n"), (2, "n"), (1, "h")],
    "S5b": [(1, "n"), (3, "n"), (3, "n"), (1, "h"), (3, "n"), (3, "n"), (1, "h")],
    "S6a": [(2, "n"), (2, "n"), (3, "n"), (1, "h")],
    "S6b": [(1, "n"), (2, "n"), (1, "h"), (2, "n"), (2, "n"), (2, "n"), (1, "h")],
}
# faixa vertical (centro, px) por trecho — uma posição por trecho
FAIXA = {"B": (1530, 1640), "A": (1267, 1536), "C": (1267, 1536), "C_topo": (365, 634), "FECHO": (1037, 1306)}
POS = {k: ("FECHO" if k == "S6b" else s["layout"]) for k, s in segs.items()}
POS_OVERRIDE = json.load(open(f"{ROOT}/work/caption_pos.json")) if os.path.exists(f"{ROOT}/work/caption_pos.json") else {}
POS.update(POS_OVERRIDE)

blocks = []
for k, s in segs.items():
    t0 = s["start_ms"] / 1000
    words = [w for w in s["words"] if not w.get("filler")]
    plan = PLAN[k]
    assert sum(n for n, _ in plan) == len(words), (k, sum(n for n, _ in plan), len(words), [w["w"] for w in words])
    i = 0
    for n, kind in plan:
        ws = words[i:i + n]; i += n
        txt = " ".join(w["w"] for w in ws)
        blocks.append(dict(seg=k, kind=kind, text=txt.upper() if kind == "h" else txt,
                           start=round(t0 + ws[0]["t"], 4), word_end=round(t0 + ws[-1]["end"], 4),
                           band=FAIXA[POS[k]], pos=POS[k]))

# tempos de exibição: entra no início da 1ª palavra (quantizado ao quadro, nunca no quadro 0 — capa);
# fica até o próximo bloco começar; se houver respiro > 0,6 s, sai 0,3 s depois da última palavra.
for j, b in enumerate(blocks):
    b["in"] = max(1, math.floor(b["start"] * FPS + 1e-6)) / FPS
    nxt = blocks[j + 1]["start"] if j + 1 < len(blocks) else END
    out = nxt if nxt - b["word_end"] <= 0.6 else b["word_end"] + 0.3
    b["out"] = min(END, math.floor(out * FPS + 1e-6) / FPS)
    if blocks[j + 1:] and blocks[j + 1]["seg"] != b["seg"]:     # nunca atravessa o corte de trecho
        seg_end = segs[b["seg"]]["end_ms"] / 1000
        b["out"] = min(b["out"], round(seg_end * FPS) / FPS)
vis = [b for b in blocks if b["kind"] != "x"]

# conferência do ritmo. Batidas = destaques (h) e gráficos que mostram a frase (x/g).
#  - nunca mais de 3 blocos normais sem uma batida;
#  - entre dois destaques de legenda, pelo menos 2 normais quando não há gráfico entre eles; nunca h-h.
seq = "".join("g" if b["kind"] == "x" else b["kind"] for b in blocks)
runs = [len(r) for r in seq.replace("g", "h").split("h")]
assert max(runs[:-1]) <= 3, f"mais de 3 normais sem batida: {seq}"
for a, b in zip([i for i, c in enumerate(seq) if c == "h"], [i for i, c in enumerate(seq) if c == "h"][1:]):
    mid = seq[a + 1:b]
    assert "g" in mid or mid.count("n") >= 2, f"destaques próximos demais: {seq[a:b + 1]}"
print("ritmo ok — normais entre batidas:", runs, " sequência:", seq)
json.dump(blocks, open(f"{ROOT}/work/captions.json", "w"), ensure_ascii=False, indent=1)
open(f"{ROOT}/hf/data/captions.js", "w").write(
    "/* Gerado por scripts/captions.py. Não editar. */\nwindow.CAPTIONS = " +
    json.dumps([dict(text=b["text"], hl=b["kind"] == "h", t_in=round(b["in"], 6), t_out=round(b["out"], 6),
                     y0=b["band"][0], y1=b["band"][1], seg=b["seg"]) for b in vis], ensure_ascii=False) + ";\n")
for b in blocks:
    print(f"{b['seg']:4s} {b['kind']} {b['in']:7.3f}–{b['out']:7.3f}  {b['pos']:6s} {b['text']}")
