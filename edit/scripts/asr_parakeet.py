"""Transcrição com Parakeet TDT 0.6B v3 (sherpa-onnx), com timestamps por token.
Processa o áudio em janelas sobrepostas (o modelo funciona melhor com < 30 s)."""
import sys, json, numpy as np, soundfile as sf, sherpa_onnx
M = sys.argv[1]; wav = sys.argv[2]; out = sys.argv[3]
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx", joiner=f"{M}/joiner.int8.onnx",
    tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=4, decoding_method="greedy_search")
x, sr = sf.read(wav, dtype="float32")
# janelas de 20 s com passo de 15 s; tokens atribuídos à janela cujo centro está mais próximo
WIN, HOP = 20.0, 15.0
toks = []
t = 0.0
while t < len(x)/sr:
    a, b = int(t*sr), int(min(len(x), (t+WIN)*sr))
    s = rec.create_stream(); s.accept_waveform(sr, x[a:b]); rec.decode_stream(s)
    r = s.result
    for tok, ts in zip(r.tokens, r.timestamps):
        T = t + ts
        lo = t + (0 if t == 0 else (WIN-HOP)/2); hi = t + WIN - (WIN-HOP)/2
        if lo <= T < hi or (b == len(x) and T >= lo):
            toks.append((T, tok))
    if b == len(x): break
    t += HOP
toks.sort()
json.dump([{"t": round(T,3), "tok": tok} for T, tok in toks], open(out, "w"), ensure_ascii=False, indent=0)
# palavras: token iniciando com espaço marca nova palavra
words=[]; cur=None
for T, tok in toks:
    if tok.startswith(" ") or cur is None:
        if cur: words.append(cur)
        cur={"w": tok.strip(), "start": T}
    else:
        cur["w"] += tok
    cur["last_tok"] = T
if cur: words.append(cur)
print(" ".join(w["w"] for w in words))
print(len(words), "palavras")
