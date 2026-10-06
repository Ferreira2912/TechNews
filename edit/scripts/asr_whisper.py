"""Transcrição de conferência com Whisper turbo (sherpa-onnx), por tomada (cada corte do bruto)."""
import sys, json, soundfile as sf, sherpa_onnx
M = sys.argv[1]; wav = sys.argv[2]
cuts = [0, 4.7333, 8.6167, 20.1167, 25.8833, 33.4333, None]
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{M}/turbo-encoder.int8.onnx", decoder=f"{M}/turbo-decoder.int8.onnx",
    tokens=f"{M}/turbo-tokens.txt", language="pt", task="transcribe", num_threads=4, tail_paddings=800)
x, sr = sf.read(wav, dtype="float32")
out = []
for a, b in zip(cuts[:-1], cuts[1:]):
    seg = x[int(a*sr): int(b*sr) if b else len(x)]
    s = rec.create_stream(); s.accept_waveform(sr, seg); rec.decode_stream(s)
    print(f"[{a:6.2f}-{(b or len(x)/sr):6.2f}] {s.result.text.strip()}")
    out.append({"start": a, "end": b or len(x)/sr, "text": s.result.text.strip()})
json.dump(out, open("work/whisper_takes.json", "w"), ensure_ascii=False, indent=1)
