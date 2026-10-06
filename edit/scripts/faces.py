"""Detecção de rosto (YuNet) por quadro: caixa, olhos, nariz e proxies de rotação da cabeça."""
import cv2, json, numpy as np, sys
src, out, step = sys.argv[1], sys.argv[2], int(sys.argv[3])
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
det = cv2.FaceDetectorYN.create(".models/yunet.onnx", "", (1080, 1920), 0.5, 0.3, 5000)
rows = []; i = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    if i % step == 0:
        n, F = det.detect(fr); row = {"f": i, "t": round(i / fps, 4)}
        if F is not None and len(F):
            f = F[np.argmax(F[:, 2] * F[:, 3])]
            x, y, w, h = f[:4]; re, le, no = f[4:6], f[6:8], f[8:10]; mr, ml = f[10:12], f[12:14]
            em = (re + le) / 2; ed = np.linalg.norm(le - re)
            row.update(x=float(x), y=float(y), w=float(w), h=float(h), eyeY=float(em[1]),
                       yaw=round(float((no[0] - em[0]) / ed), 3), pitch=round(float((no[1] - em[1]) / ed), 3),
                       roll=round(float(np.degrees(np.arctan2(le[1] - re[1], le[0] - re[0]))), 1), score=round(float(f[14]), 3))
        rows.append(row)
    i += 1
json.dump(rows, open(out, "w")); print(len(rows))
