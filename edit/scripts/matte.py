"""Recorte do apresentador com RobustVideoMatting (ONNX, recorrente → estável no tempo).

Uso: matte.py <modelo.onnx> <ini_quadro> <fim_quadro_exclusivo> <aquecimento_quadros> <saida.mkv>
Lê o bruto quadro a quadro (mesmos quadros de origem usados no cartão), escreve o alfa em vídeo
FFV1 cinza (sem perdas). Os primeiros quadros de aquecimento só alimentam o estado recorrente.
"""
import subprocess, sys, numpy as np, onnxruntime as ort
model, f0, f1, warm, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
W, H, FPS = 1080, 1920, 60
s0 = max(0, f0 - warm)
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession(model, so, providers=["CPUExecutionProvider"])
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{s0 / FPS:.6f}", "-i", "brutoIndiqueeViaje.mp4",
                        "-frames:v", str(f1 - s0), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "ffv1", "-level", "3", out], stdin=subprocess.PIPE)
rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
ratio = np.array([0.25], np.float32)
n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32).transpose(2, 0, 1)[None] / 255.0
    fgr, pha, *rec = sess.run(None, {"src": img, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": ratio})
    if s0 + n >= f0:
        enc.stdin.write((np.clip(pha[0, 0], 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    n += 1
enc.stdin.close(); enc.wait()
print(f"{out}: {n - (f0 - s0)} quadros de alfa (origem {f0}–{f1 - 1})")
