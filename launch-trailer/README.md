# Claude Opus 5.5 — trailer de lançamento

Filme de 18 s, 2560 × 1440, 60 fps, feito só com código e renderizado com
[HyperFrames](https://github.com/heygen-com/hyperframes).

- **Imagem:** HTML, CSS, SVG, canvas 2D e GSAP. Não usa imagens, vídeos nem mídia gerada por IA.
- **Som:** Web Audio API (osciladores, ruído com semente, filtros, delay e reverb
  de convolução com resposta ao impulso calculada), renderizado com
  `OfflineAudioContext`, exportado em WAV e embutido no MP4 pelo HyperFrames.
  Não usa samples nem arquivos de áudio externos.
- **Entregável:** `renders/claude-opus-5-5-trailer.mp4`
- **Roteiro técnico:** [`ROTEIRO.md`](ROTEIRO.md)

## Estrutura

| Arquivo | Papel |
| --- | --- |
| `index.html` | Composição HyperFrames: cenas, timeline GSAP, canvas (poeira, onda, grão). |
| `timing.js` | Marcas de tempo (80 BPM) compartilhadas por imagem e som. |
| `audio/score.js` | A trilha: todos os instrumentos e a partitura em Web Audio. |
| `audio/render.html` | Página que roda o `OfflineAudioContext`. |
| `scripts/render-audio.mjs` | Abre o Chrome headless, renderiza a trilha, aplica um limitador de pico leve (≤ 3 dB, só no clímax) e grava `assets/score.wav` (PCM 24 bits/48 kHz) e `assets/score-wave.js` (envelope usado para desenhar a onda real na tela). |
| `scripts/extract-code.mjs` | Copia as linhas de `index.html` marcadas com `// ◆` para `assets/code-lines.js`. O painel de código do filme mostra trechos reais do próprio filme. |
| `fonts/` | Newsreader (títulos) e Inter (demais textos), ambas sob a SIL Open Font License 1.1. |
| `vendor/gsap.min.js` | GSAP 3.15.0, local para a renderização não depender de rede. |

## Como reproduzir

Requisitos: Node.js ≥ 22 e FFmpeg.

```bash
cd launch-trailer
npm install
npx hyperframes browser ensure   # baixa o Chrome Headless Shell fixado pelo HyperFrames
npm run build                    # = npm run code && npm run audio && npm run render
```

Etapas isoladas:

```bash
npm run code      # atualiza assets/code-lines.js a partir de index.html
npm run audio     # regera assets/score.wav e assets/score-wave.js
npm run check     # lint + validação em runtime do HyperFrames
npm run snapshot  # quadros-chave em snapshots/
npm run preview   # HyperFrames Studio para inspecionar a timeline
npm run render    # MP4 final em renders/claude-opus-5-5-trailer.mp4
```

## Veracidade

Toda frase na tela pode ser verificada no próprio projeto:

- "Nada aqui foi filmado." / "Cada quadro é código." / "Cada som também.":
  ver `index.html` e `audio/score.js`.
- "Escrito pelo próprio modelo.": a sessão do Claude Code que escreveu este
  projeto rodava no modelo `claude-opus-5-5` (Claude Opus 5.5).
- "Anthropic" e `claude-opus-5-5`: desenvolvedora e identificador do modelo.

O filme não cita benchmarks, recursos nem comparações com outros modelos.

## Fontes

- Newsreader: Production Type, SIL Open Font License 1.1.
- Inter: Rasmus Andersson, SIL Open Font License 1.1.

Os arquivos `.woff2` (subconjunto latino) foram obtidos do Google Fonts.
