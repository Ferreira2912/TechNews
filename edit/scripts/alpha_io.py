import subprocess, numpy as np
W, H = 1080, 1920
def read_alpha(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    return np.frombuffer(p, np.uint8).reshape(-1, H, W)
