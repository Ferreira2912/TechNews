# Claude Opus 5.5 — trailer de lançamento · roteiro técnico

**Conceito: "O ponto."** Nada neste filme foi filmado. Um único ponto cor de argila
cai na tela, vira o cursor que escreve a primeira frase, vira o ponto final dessa
frase, vira a linha que carrega o som, volta a ser ponto e, no clímax, explode
numa tela creme. Ali ele é o ponto decimal de **5.5**. O espectador acompanha
a mesma forma do primeiro quadro ao último.

Toda afirmação na tela é verificável no próprio projeto. A imagem é código
(HTML, CSS, SVG, canvas, GSAP). O som é código (Web Audio, OfflineAudioContext).
O autor é o modelo apresentado: a sessão que escreveu este projeto roda em
`claude-opus-5-5`. Não há benchmarks, recursos nem comparações.

| Item         | Valor                                                                        |
| ------------ | ---------------------------------------------------------------------------- |
| Formato      | MP4 H.264 + AAC, 2560 × 1440, 60 fps, 18,0 s (1080 quadros)                  |
| Paleta       | creme `#F0EEE6` · tinta `#1F1E1D` · argila `#D97757` (só no ponto e na onda) |
| Tipografia   | **Newsreader** (serifada, títulos) · **Inter** (sem serifa, demais textos)   |
| Andamento    | **80 BPM**, 4/4. 1 tempo = 0,75 s = 45 quadros; 1 compasso = 3 s            |
| Estrutura    | 6 compassos = 6 ideias, uma por compasso                                     |
| Tonalidade   | Ré. Progressão i → ♭VI → ♭VII → **I** (Rém → Si♭ → Dó → **Ré maior**)        |
| Motivo       | Lá – Ré – Mi – Fá (menor) que, na revelação, resolve em Lá – Ré – Mi – **Fá♯** |

## Linha do tempo

| Tempo (s)     | Compasso | Na tela | O espectador entende | Áudio |
| ------------- | -------- | ------- | -------------------- | ----- |
| 0,00 – 0,375  | 1 (anacruse) | Tinta quase preta, poeira em 3 profundidades. Um ponto argila despenca do alto, esticado pela velocidade. | Algo vai acontecer, rápido. | Sopro de ruído filtrado subindo (whip). |
| **0,375**     | 1 | O ponto aterrissa e se achata. Dois anéis de choque se expandem. | O ponto é o protagonista. | **Primeiro impacto**: sub de 38 Hz e clique brilhante. |
| 0,56 – 0,75  | 1 | O ponto dispara para a esquerda, esticado pela velocidade, e vira um cursor de texto. | É alguém escrevendo. | Whoosh panorâmico da direita para a esquerda; drone de Ré em quinta abrindo. |
| 0,75 – 2,15   | 1 | O cursor digita **"Nada aqui foi filmado"**, com cada palavra numa colcheia. Serifada grande no centro. | Frase-gancho, lida enquanto é escrita. | Cliques de digitação sintetizados, um por letra, palavra a palavra na colcheia. |
| **2,25**      | 1 (tempo 4) | O cursor encolhe e vira o **ponto final** argila da frase. Push-in lento. | A frase está completa. | Nota de sino Ré5: o ponto "soa". |
| 2,6 – 3,0     | 1 | Leitura. Respiração leve da câmera. | Releitura. | Swell reverso para o compasso 2. |
| **3,00 – 3,9** | 2 | **Match cut por zoom**: a câmera recua e revela que a frase é uma *string* dentro do código real deste filme. As linhas entram em profundidade 3D, as do fundo com desfoque. | Aquilo era código. | **Impacto 2**, o baixo pulsante em colcheias começa, whoosh descendente, pad em Rém. |
| 3,7 – 5,6    | 2 | Foco desloca (3,7): o código desfoca e escurece. Em 3,9 entra **"Cada quadro é *código*."** palavra por palavra, de baixo de uma máscara. Leitura de ~1,3 s com o título parado. | Cada imagem é programada. | Motivo no sino: Lá4 (3,75), Ré5, Mi5, Fá5 (5,25). |
| 5,6 – 6,0     | 2 → 3 | Título sai num deslocamento rápido. O bloco de código **colapsa verticalmente numa única linha argila**: a forma se transforma na próxima cena. | O código virou uma linha. | Whoosh reverso que suga para o tempo 1. |
| **6,00**      | 3 | A linha é "dedilhada" e vira a **forma de onda real da trilha** (dados extraídos do WAV), com cabeça de leitura (o ponto) no centro e ecos em profundidade. | A linha é o som que se está ouvindo. | **Impacto 3**, acorde Si♭, tique de relógio em colcheias. |
| 6,75 – 8,6    | 3 | **"Cada *som* também."** acima da onda. Leitura ~1,8 s. | O som também é código. | Motivo: Lá4, Ré5, Mi5, Fá5 sobre Si♭ (cor lídia). |
| 8,6 – 9,0     | 3 → 4 | Título sai em deslocamento. | — | Whoosh. |
| **9,00 – 11,25** | 4 | **"Escrito pelo *próprio* modelo."** A onda ganha energia, a câmera avança, o brilho argila cresce atrás. Leitura ~1,8 s. | Quem escreveu foi o próprio modelo… qual? | **Tensão**: acorde Dó, tiques em semicolcheias, riser de ruído em banda (200 Hz → 9 kHz), tremolo acelerando, motivo sobe até Sol5 (sus4). |
| 11,25 – 11,85 | 4 | Vácuo: o título se contrai, a onda se fecha horizontalmente num **ponto**, que viaja (com antecipação) até onde será o decimal de "5.5". | Toda a energia virou um ponto. | Swell reverso crescendo e corte seco. |
| 11,85 – 12,0  | 4 | O ponto se comprime (antecipação). Quase silêncio. | Suspensão. | **150 ms de silêncio.** |
| **12,00**     | 5 | **CLÍMAX.** O ponto estoura e explode numa máscara circular creme que inunda a tela a partir do decimal. **"Claude Opus 5.5"** em tinta, com o ponto argila no decimal, aterrissa de 112 % para 100 % com ultrapassagem sutil e desfoque saindo. Anéis de onda de choque. | **O nome. O ponto do início é o ponto de 5.5.** | **Impacto principal**: queda de sub 110 → 30 Hz, corpo grave, estalo, brilho de ar, acorde de **Ré maior** abrindo o filtro, reverb longo. |
| 12,0 – 14,25  | 5 | Nome em repouso, push-in lento, anéis finos se dissipando, grão. O ponto decimal "respira" a cada nota do motivo. | Leitura do nome (2,25 s). | Motivo em **maior**: Lá4 (12,75), Ré5, Mi5, **Fá♯5** (14,25). A resolução. |
| 14,25 – 15,3  | 5 → 6 | O nome sobe e reduz. Um fio argila se desenha. Entram **"Anthropic"** e `claude-opus-5-5` (Inter). | Quem fez e o identificador real do modelo. | Fá♯5 sustenta, whoosh suave. |
| **15,0 – 18,0** | 6 | **Composição final** estável por ≥ 2,7 s, apenas com push-in e grão discretos. | Assinatura. | Ré grave final e sino Lá5; cauda do reverb decai até o silêncio em ~17,9 s. |

## Regras de movimento aplicadas

- Todas as interpolações usam curvas (`expo`, `power`, `back`, `sine`). Nenhum `ease: "none"` em movimento visível. As derivas de partículas seguem senoides.
- Antecipação: queda do ponto (estica antes de cair), recuo de 2 % antes do zoom-out, compressão do ponto antes do clímax. Ultrapassagem: aterrissagem do ponto (`back.out`) e nome (`expo.out` de 112 %).
- Profundidade: zoom de câmera (escala), desfoque de foco (rack focus), linhas de código em `translateZ` com desfoque por distância, ecos da onda desfocados e 3 camadas de poeira com paralaxe.
- Transições nascem dos elementos: zoom-out do texto para o código, colapso do código numa linha, linha em onda, onda contraída em ponto, ponto em máscara circular.
- Pausas de leitura: só push-in lento, grão e partículas, sem nada competindo com o texto.

## Pipeline

1. `timing.js` guarda as marcas de tempo compartilhadas, usadas pelo áudio **e** pela imagem.
2. `audio/score.js` monta a trilha com nós Web Audio. `scripts/render-audio.mjs` abre o Chrome headless, roda o `OfflineAudioContext` (48 kHz, estéreo), normaliza o pico e grava `assets/score.wav` (PCM 24 bits) e `assets/score-wave.js` (envelope para desenhar a onda).
3. `index.html` é a composição HyperFrames, que inclui `<audio id="score" src="assets/score.wav">`.
4. `npx hyperframes render --fps 60 --quality high` gera o MP4 com o áudio embutido.
