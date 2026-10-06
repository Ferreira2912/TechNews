"""Pose da cabeça e posição da íris por quadro (MediaPipe FaceLandmarker) para checar contato visual."""
import cv2, json, numpy as np, mediapipe as mp, sys
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
src, out, step = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3
opts = vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=".models/face_landmarker.task"),
    running_mode=vision.RunningMode.VIDEO, num_faces=1,
    output_facial_transformation_matrixes=True, output_face_blendshapes=True)
det = vision.FaceLandmarker.create_from_options(opts)
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
rows = []; i = 0
def ratio(lm, a, b, c):  # posição relativa da íris c entre os cantos a e b
    pa, pb, pc = (np.array([lm[k].x, lm[k].y]) for k in (a, b, c))
    v = pb - pa; return float(np.dot(pc - pa, v) / np.dot(v, v))
while True:
    ok, fr = cap.read()
    if not ok: break
    if i % step == 0:
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        r = det.detect_for_video(img, int(i * 1000 / fps))
        row = {"f": i, "t": round(i / fps, 4)}
        if r.face_landmarks:
            lm = r.face_landmarks[0]
            M = np.array(r.facial_transformation_matrixes[0])
            R = M[:3, :3] / np.linalg.norm(M[:3, 0])
            yaw = np.degrees(np.arctan2(-R[2, 0], np.hypot(R[2, 1], R[2, 2])))
            pitch = np.degrees(np.arctan2(R[2, 1], R[2, 2]))
            # olho direito do sujeito: cantos 33 (ext) e 133 (int), íris 468; esquerdo: 362 (int), 263 (ext), íris 473
            rh = ratio(lm, 33, 133, 468); lh = ratio(lm, 362, 263, 473)
            bs = {c.category_name: c.score for c in r.face_blendshapes[0]}
            row.update(yaw=round(float(yaw), 1), pitch=round(float(pitch), 1), irisR=round(rh, 3), irisL=round(lh, 3),
                       lookL=round(bs.get("eyeLookOutLeft", 0) + bs.get("eyeLookInRight", 0), 3),
                       lookR=round(bs.get("eyeLookInLeft", 0) + bs.get("eyeLookOutRight", 0), 3),
                       lookD=round((bs.get("eyeLookDownLeft", 0) + bs.get("eyeLookDownRight", 0)) / 2, 3),
                       lookU=round((bs.get("eyeLookUpLeft", 0) + bs.get("eyeLookUpRight", 0)) / 2, 3),
                       blink=round((bs.get("eyeBlinkLeft", 0) + bs.get("eyeBlinkRight", 0)) / 2, 3),
                       cx=round(float(np.mean([p.x for p in lm])), 4), cy=round(float(np.mean([p.y for p in lm])), 4),
                       top=round(float(min(p.y for p in lm)), 4), chin=round(float(lm[152].y), 4))
        rows.append(row)
    i += 1
json.dump(rows, open(out, "w"))
print(len(rows), "amostras")
