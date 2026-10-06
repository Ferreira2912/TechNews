"""Lista de decisão de edição (EDL): tomadas, cortes, J-cuts, compressão de pausas, trechos e palavras.

Todas as decisões vêm de medições do envelope RMS de 10 ms da voz limpa (work/voice_clean_mono.wav)
e dos timestamps por token do Parakeet. Os pontos de corte de imagem são quantizados em quadros de 1/60 s.
Saída: work/edl.json
"""
import json, math, sys
import numpy as np
sys.path.insert(0, "scripts")
from envelope import env10, words_from_parakeet

FPS = 60
Q = lambda t: round(t * FPS) / FPS          # quantiza ao quadro mais próximo
QF = lambda t: math.floor(t * FPS + 1e-9) / FPS
QC = lambda t: math.ceil(t * FPS - 1e-9) / FPS

rms, sr = env10("work/voice_clean_mono.wav")
lvl = lambda t: rms[int(t * 100)]

RAW_CUTS = [0.0, 4.7333, 8.6167, 20.1167, 25.8833, 33.4333, 39.7333]  # cortes de imagem do bruto (frame-exatos)
RAW_CUTS = [round(c * FPS) / FPS for c in RAW_CUTS]

# Por tomada: início da fala (primeira subida acima do ruído) e fim verdadeiro (regra -35/-32 dB),
# ambos medidos no envelope (ver relatório). Pausas internas > 250 ms são comprimidas para ~120 ms.
TAKES = [
    dict(onset=0.035, end=4.43, pauses=[]),
    dict(onset=4.80, end=8.45, pauses=[]),
    dict(onset=8.69, end=20.05, pauses=[(12.74, 13.23)]),
    dict(onset=20.21, end=25.73, pauses=[]),
    dict(onset=25.975, end=33.29, pauses=[(31.93, 32.23)]),
    dict(onset=33.535, end=39.20, pauses=[]),
]
NOISE = -55.0     # nível em que a cauda chega ao ruído de fundo
FADE = 0.170      # saída gradual depois do ruído
JLEAD = 0.050     # J-cut: o áudio da nova frase começa 50 ms antes do corte de imagem
PRE = 0.040       # margem antes da primeira palavra
KEEP_PAUSE = 0.120
JUNCTION_TAIL = 0.07  # imagem da frase anterior continua ~70 ms após o fim verdadeiro

# Trechos (layout) em tempo de origem: (id, tomada, início, layout, conteúdo)
SEGMENTS = [
    ("S1", 0, None, "B", "Gancho: 'E se eu te dissesse que indicar um amigo pode te auxiliar a pagar sua próxima viagem?'"),
    ("S2", 1, None, "C", "'Chegou o Indique e Viaje, a nova campanha aqui da Parktur.' — selo grande, logotipo, peça oficial"),
    ("S3a", 2, None, "A", "'E é muito simples,'"),
    ("S3b", 2, 9.90, "C", "'você indica um amigo, um familiar ou um colega. Se essa pessoa fechar uma viagem com a Parktur,' — demonstração indicou → fechou"),
    ("S3c", 2, 15.75, "B", "'você ganha R$ 100 de crédito para utilizar na sua próxima viagem' — box VOCÊ GANHA R$ 100"),
    ("S4a", 3, None, "A", "'E quem você indicar também ganha, é,'"),
    ("S4b", 3, 22.38, "B", "'R$ 50 de benefício na contratação da viagem.' — box SEU INDICADO GANHA R$ 50"),
    ("S5a", 4, None, "A", "'E tem mais, o seu crédito é acumulativo.'"),
    ("S5b", 4, 28.72, "C", "'Então, quanto mais pessoas você indicar para viajar com a gente, mais você vai ganhar.' — tabela 1/3/5 e moedas"),
    ("S6a", 5, None, "B", "'Já pensou em alguém que tá querendo viajar?' 👀"),
    ("S6b", 5, 35.85, "A", "CTA: 'Então mande o nome pra gente e faça sua primeira indicação.' + botão INDIQUE AGORA"),
]

def first_below(t0, t1, thr):
    for i in range(int(t0 * 100), int(t1 * 100)):
        if rms[i] <= thr: return i / 100
    return t1

# ---------- montagem: peças de vídeo (origem → saída) ----------
pieces = []      # {take, src_in, src_out, out_in}
takes_out = []
P = 0.0
for k, tk in enumerate(TAKES):
    r0, r1 = RAW_CUTS[k], RAW_CUTS[k + 1]
    vin = 0.0 if k == 0 else max(r0, QF(tk["onset"] - PRE))
    last = k == len(TAKES) - 1
    if last:
        nr = first_below(tk["end"], r1, NOISE)
        voice_end = min(nr + FADE, r1)
        vout = min(r1, QC(voice_end))
    else:
        vout = min(r1, Q(tk["end"] + JUNCTION_TAIL))
    # pausas internas: remove o miolo e deixa ~120 ms
    cuts = []
    for a, b in tk["pauses"]:
        ca, cb = Q(a + KEEP_PAUSE / 2), Q(b - KEEP_PAUSE / 2)
        cuts.append((ca, cb))
    spans = []; s = vin
    for ca, cb in cuts:
        spans.append((s, ca)); s = cb
    spans.append((s, vout))
    tk_out_in = P
    for a, b in spans:
        pieces.append(dict(take=k + 1, src_in=a, src_out=b, out_in=round(P, 6)))
        P += b - a
    takes_out.append(dict(take=k + 1, vin=vin, vout=vout, out_in=tk_out_in, out_out=round(P, 6), cuts=cuts, spans=spans))
END = round(P, 6)

def src2out(t, take):
    """Mapeia tempo de origem (dentro da tomada) para tempo de saída; t numa pausa removida vai para o ponto do corte."""
    ps = [p for p in pieces if p["take"] == take]
    if t < ps[0]["src_in"]:
        return ps[0]["out_in"] + (t - ps[0]["src_in"])
    for p in ps:
        if p["src_in"] - 1e-9 <= t < p["src_out"]:
            return p["out_in"] + (t - p["src_in"])
        if t < p["src_in"]:  # dentro de um trecho removido
            return p["out_in"]
    p = ps[-1]
    return p["out_in"] + (t - p["src_in"])

def out2src(t):
    """Quadro de saída → (tomada, tempo de origem)."""
    for p in pieces:
        d = p["src_out"] - p["src_in"]
        if p["out_in"] - 1e-4 <= t < p["out_in"] + d - 1e-4:     # tolerância < meio quadro (out_in arredondado a 6 casas)
            return p["take"], p["src_in"] + (t - p["out_in"])
    p = pieces[-1]; return p["take"], p["src_in"] + (t - p["out_in"])

# ---------- áudio: clipes por tomada com J-cut, cauda e fade ----------
audio = []
for k, tk in enumerate(TAKES):
    to = takes_out[k]; r0, r1 = RAW_CUTS[k], RAW_CUTS[k + 1]
    a_in = to["vin"] - (0 if k == 0 else JLEAD)
    a_in_clamped = max(r0, a_in)     # nunca usa áudio de outra tomada do bruto
    nr = first_below(tk["end"], r1, NOISE)
    if k < len(TAKES) - 1:
        nxt = TAKES[k + 1]; nto = takes_out[k + 1]
        next_onset_out = nto["out_in"] + (nxt["onset"] - nto["vin"])
        next_onset_src = to["vout"] + (next_onset_out - to["out_out"])
        fade_start = nr
        fade_end = min(nr + FADE, next_onset_src, r1)
        if fade_end - fade_start < 0.02: fade_start = fade_end - 0.02
    else:
        fade_start = nr; fade_end = min(nr + FADE, r1, to["vout"])
    audio.append(dict(take=k + 1, src_in=a_in_clamped, pad_before=round(a_in_clamped - a_in, 6),
                      out_in=round(to["out_in"] - (0 if k == 0 else JLEAD) + (a_in_clamped - a_in), 6),
                      true_end=tk["end"], noise_reach=nr, fade_start=round(fade_start, 4), fade_end=round(fade_end, 4),
                      cuts=to["cuts"], vin=to["vin"]))

# junções: silêncio entre fim verdadeiro e próxima fala (tempo de saída)
junctions = []
for k in range(len(TAKES) - 1):
    end_out = takes_out[k]["out_out"] - (takes_out[k]["vout"] - TAKES[k]["end"])
    on_out = takes_out[k + 1]["out_in"] + (TAKES[k + 1]["onset"] - takes_out[k + 1]["vin"])
    junctions.append(dict(after_take=k + 1, cut_out=takes_out[k + 1]["out_in"], speech_end_out=round(end_out, 4),
                          next_onset_out=round(on_out, 4), gap_ms=round((on_out - end_out) * 1000, 1)))
for k, to in enumerate(takes_out):
    for (ca, cb) in to["cuts"]:
        pass

# ---------- trechos em tempo de saída ----------
segs = []
for i, (sid, k, s, lay, txt) in enumerate(SEGMENTS):
    to = takes_out[k]
    o_in = to["out_in"] if s is None else Q(src2out(Q(s), k + 1))
    segs.append(dict(id=sid, layout=lay, take=k + 1, out_in=round(o_in, 6), content=txt, src_in=to["vin"] if s is None else Q(s)))
for i in range(len(segs)):
    segs[i]["out_out"] = segs[i + 1]["out_in"] if i + 1 < len(segs) else END
    segs[i]["dur"] = round(segs[i]["out_out"] - segs[i]["out_in"], 4)
    segs[i]["frames"] = round(segs[i]["dur"] * FPS)

# ---------- palavras corrigidas em tempo de saída ----------
words = words_from_parakeet("work/parakeet_tokens.json")
FIX = {"Viagem.": "Viaje,", "Parktor.": "Parktur.", "cumulativo.": "acumulativo."}
out_words = []
i = 0
while i < len(words):
    w = dict(words[i]); txt = FIX.get(w["w"], w["w"]); filler = False
    if w["w"] == "Park" and i + 1 < len(words) and words[i + 1]["w"].startswith("Tour"):
        txt = "Parktur" + words[i + 1]["w"][4:]; w["e"] = words[i + 1]["e"]; i += 1
    if w["w"] in ("100", "50") and i + 1 < len(words) and words[i + 1]["w"].startswith("reais"):
        txt = "R$ " + w["w"] + words[i + 1]["w"][5:]; w["e"] = words[i + 1]["e"]; i += 1
    if w["w"] == "é" and words[i - 1]["w"] == "ganha" and words[i + 1]["w"] == "50":
        filler = True
    # tomada a que pertence
    k = max(j for j in range(6) if RAW_CUTS[j] - 0.05 <= w["s"])
    out_words.append(dict(w=txt, src=w["s"], take=k + 1, filler=filler))
    i += 1
# refina o início de cada palavra: se o token cair dentro de um silêncio (< -40 dB por >= 80 ms),
# move para o fim do silêncio; depois procura a subida de energia mais próxima (-30/+60 ms)
sil = rms < -40; runs = []; st = None
for i_, b_ in enumerate(sil):
    if b_ and st is None: st = i_
    if not b_ and st is not None:
        if i_ - st >= 8: runs.append((st / 100, i_ / 100))
        st = None
for ow in out_words:
    t = ow["src"]
    for a_, b_ in runs:
        if a_ <= t < b_: t = b_
    lo, hi = max(1, int((t - 0.03) * 100)), int((t + 0.06) * 100)
    d = np.diff(rms[lo - 1:hi + 1]); best = (lo + int(np.argmax(d))) / 100
    for a_, b_ in runs:
        if a_ <= best < b_: best = b_
    ow["src_start"] = round(max(best, t - 0.03), 3)
# inícios estritamente crescentes (mínimo 50 ms entre palavras da mesma tomada)
for j in range(1, len(out_words)):
    a_, b_ = out_words[j - 1], out_words[j]
    if b_["take"] == a_["take"] and b_["src_start"] < a_["src_start"] + 0.05:
        b_["src_start"] = round(a_["src_start"] + 0.05, 3)
for j, ow in enumerate(out_words):
    nxt = out_words[j + 1] if j + 1 < len(out_words) else None
    tk = TAKES[ow["take"] - 1]
    end_src = min(nxt["src_start"] if nxt and nxt["take"] == ow["take"] else tk["end"], tk["end"])
    ow["src_end"] = round(end_src, 3)
    ow["start"] = round(src2out(ow["src_start"], ow["take"]), 4)
    ow["end"] = round(src2out(ow["src_end"], ow["take"]), 4)
    for (ca, cb) in takes_out[ow["take"] - 1]["cuts"]:
        assert not (ca < ow["src_start"] < cb), f"palavra {ow['w']} dentro de pausa removida"

# quadro de origem de cada quadro de saída (usado na montagem e no recorte)
frame_map = []
for n in range(round(END * FPS)):
    tk, ts = out2src(n / FPS)
    frame_map.append([tk, round(ts * FPS)])
for s_ in segs:
    a = round(s_["out_in"] * FPS); b = round(s_["out_out"] * FPS)
    s_["src_frames"] = [frame_map[a][1], frame_map[b - 1][1] + 1]

edl = dict(fps=FPS, frame_map=frame_map, END=END, END_ms=round(END * 1000, 1), END_frames=round(END * FPS), raw_cuts=RAW_CUTS,
           pieces=pieces, takes=takes_out, audio=audio, junctions=junctions, segments=segs, words=out_words)
json.dump(edl, open("work/edl.json", "w"), ensure_ascii=False, indent=1)

print(f"END = {END:.4f} s = {END*1000:.1f} ms = {round(END*FPS)} quadros")
print("\nPeças de vídeo:")
for p in pieces: print(f"  tomada {p['take']}: origem {p['src_in']:.4f}–{p['src_out']:.4f} → saída {p['out_in']:.4f}")
print("\nJunções:")
for j in junctions: print(f"  após tomada {j['after_take']}: corte {j['cut_out']:.4f}, fim fala {j['speech_end_out']:.3f}, próxima fala {j['next_onset_out']:.3f}, silêncio {j['gap_ms']} ms")
print("\nÁudio:")
for a in audio: print(f"  tomada {a['take']}: origem {a['src_in']:.4f} → saída {a['out_in']:.4f} (pad {a['pad_before']*1000:.0f} ms), cauda até ruído {a['noise_reach']:.2f}, fade {a['fade_start']:.3f}–{a['fade_end']:.3f}")
print("\nTrechos:")
for s in segs: print(f"  {s['id']:4s} {s['layout']}  {s['out_in']:7.3f}–{s['out_out']:7.3f}  ({s['dur']:.3f} s, {s['frames']} q) origem q{s['src_frames']}  {s['content'][:60]}")
print("\nPalavras:", " ".join(("[" + w["w"] + "]") if w["filler"] else w["w"] for w in out_words))
