#!/usr/bin/env bash
# Extração e limpeza leve da voz (sem arquivo de voz limpa fornecido).
#  - pan=mono: o bruto é estéreo com L == R; vira mono por média.
#  - highpass 80 Hz (2 polos): tira ronco e vento abaixo da voz.
#  - afftdn nr=10 dB, nf=-56 dB: redução de ruído suave (sem som metálico; nada de redução agressiva).
#  - o afftdn atrasa o sinal em 1198 amostras (25 ms): compensado com atrim + apad (atraso medido = 0).
#  - de-esser: não usado (picos da banda 5–9 kHz ficam 20,6 dB abaixo dos picos gerais).
# Uso: scripts/clean_voice.sh <bruto.mp4> <saida_dir>
set -euo pipefail
IN="${1:-brutoIndiqueeViaje.mp4}"; OUT="${2:-work}"
mkdir -p "$OUT"
ffmpeg -hide_banner -loglevel error -y -i "$IN" -vn -ar 48000 -c:a pcm_f32le "$OUT/raw48.wav"
ffmpeg -hide_banner -loglevel error -y -i "$OUT/raw48.wav" -ac 1 -ar 16000 -c:a pcm_s16le "$OUT/raw16.wav"
ffmpeg -hide_banner -loglevel error -y -i "$OUT/raw48.wav" -af \
  "pan=mono|c0=0.5*c0+0.5*c1,highpass=f=80:poles=2,afftdn=nr=10:nf=-56:tn=0,atrim=start_sample=1198,asetpts=PTS-STARTPTS,apad=pad_len=1198" \
  -c:a pcm_f32le "$OUT/voice_clean_mono.wav"
