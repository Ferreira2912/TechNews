# Relatório de edição: Reel "INDIQUE E VIAJE!" (Parktur)

Todo o trabalho foi feito por código: FFmpeg, Python (venv local em `edit/.venv`), Node (npm local em
`edit/hf`) e HyperFrames 0.8.137. Nada foi instalado globalmente. A trilha e os efeitos são sintetizados,
sem nenhum arquivo de áudio externo.

## Entregas

| Arquivo | Conteúdo |
| --- | --- |
| `final.mp4` | 1080×1920, 60 qps, H.264 High (CRF 14, preset slow, BT.709), AAC estéreo 48 kHz 320 kb/s |
| `stems/voice.wav` | voz montada (J-cuts, pausas comprimidas), 38,300 s |
| `stems/sfx.wav` | efeitos sintetizados, 38,300 s |
| `stems/riser.wav` | riser grave do gancho, 38,300 s |
| `stems/music.wav` | trilha sintetizada, 38,300 s |

Todas as stems são WAV float 32 bits, 48 kHz, estéreo, com a duração exata do vídeo e começando em 0.
A soma das quatro stems (com o limitador do master) é o áudio do `final.mp4`.

## END

**END = 38 300 ms** (2 298 quadros a 60 qps). É o fim exclusivo da faixa de voz. Todas as camadas
(vídeo, legendas, CTA, voz, efeitos, riser e música) terminam exatamente em END.

## Tabela de trechos

A tabela foi escrita antes dos gráficos, em `PLANO.md`.

| Trecho | Início (ms) | Fim (ms) | Duração | Layout | Fala | Quadros de origem (bruto, 60 qps) |
| --- | ---: | ---: | ---: | :---: | --- | --- |
| S1 | 0 | 4 500 | 4,50 s | **B** | E se eu te dissesse que indicar um amigo pode te auxiliar a pagar sua próxima viagem? | 0–270 |
| S2 | 4 500 | 8 267 | 3,77 s | **C** | Chegou o Indique e Viaje, a nova campanha aqui da Parktur. | 285–511 |
| S3a | 8 267 | 9 517 | 1,25 s | **A** | E é muito simples, | 519–594 |
| S3b | 9 517 | 15 000 | 5,48 s | **C** | você indica um amigo, um familiar ou um colega. Se essa pessoa fechar uma viagem com a Parktur, | 594–945 (pausa interna 768–790 removida) |
| S3c | 15 000 | 19 367 | 4,37 s | **B** | você ganha R$ 100 de crédito para utilizar na sua próxima viagem | 945–1207 |
| S4a | 19 367 | 21 583 | 2,22 s | **A** | e quem você indicar também ganha, [é] | 1210–1343 |
| S4b | 21 583 | 25 000 | 3,42 s | **B** | R$ 50 de benefício na contratação da viagem. | 1343–1548 |
| S5a | 25 000 | 27 783 | 2,78 s | **A** | e tem mais, o seu crédito é acumulativo. | 1556–1723 |
| S5b | 27 783 | 32 250 | 4,47 s | **C** | Então, quanto mais pessoas você indicar para viajar com a gente, mais você vai ganhar. | 1723–2002 (pausa interna 1919–1930 removida) |
| S6a | 32 250 | 34 617 | 2,37 s | **B** | Já pensou em alguém que tá querendo viajar? | 2009–2151 |
| S6b | 34 617 | 38 300 | 3,68 s | **A** | Então mande o nome pra gente e faça sua primeira indicação. | 2151–2372 |

Regras conferidas:
- O gancho está em B e o encerramento a partir do CTA está em A.
- Sequência de layouts: B C A C B A B A C B A. Nunca há dois iguais seguidos, e os três aparecem.
- O maior trecho tem 5,48 s, abaixo do limite de cerca de 8 s.
- Mecânica (S3b) e tabela de acúmulo (S5b) estão em C. Valores isolados (S3c, S4b), a curiosidade (S6a)
  e o gancho estão em B. Frases de impacto e afirmações diretas (S3a, S4a, S5a, S6b) estão em A, com
  contato visual.

## Tomadas escolhidas e substituições

- O bruto (39,733 s, 2 384 quadros) já é uma montagem de **seis tomadas**, com cortes de imagem em
  4,733, 8,617, 20,117, 25,883 e 33,433 s.
- A transcrição por palavra foi feita com Parakeet TDT 0.6B v3, via sherpa-onnx (timestamps por token,
  janelas de 20 s), e conferida com Whisper turbo por tomada.
- Cada frase aparece **uma única vez**. Não há recomeços, "ok", "vamos lá", sílabas soltas nem
  murmúrios. Por isso cada tomada usada é a última, e única, versão completa da frase. **Nenhuma
  substituição** foi necessária.
- Termos corrigidos na transcrição:
  - "Viagem." → "Viaje,"
  - "Parktor"/"Park Tour" → "Parktur"
  - "cumulativo" → "acumulativo"
  - "100 reais" → "R$ 100" e "50 reais" → "R$ 50"
  - Mantidos: indicado, indicação, crédito, Indique e Viaje.
- A hesitação "é" (em "também ganha, é, R$ 50") está colada às palavras vizinhas, sem pausa, e um corte
  ali seria audível. Ela fica no áudio e sai das legendas.
- Pausas internas acima de 250 ms foram comprimidas para 120 ms:
  - tomada 3: 12,74–13,23 s do bruto;
  - tomada 5: 31,93–32,23 s do bruto.
  - Os cortes de imagem nessas emendas são secos e caem dentro de trechos C (o gráfico cobre a câmera).
- Fim verdadeiro de cada frase: última janela RMS de 10 ms com nível ≥ −35 dB, confirmada pela regra
  −32 dB/150 ms. Valores no bruto: 4,43 / 8,45 / 20,05 / 25,73 / 33,29 / 39,20 s.
- Antes da primeira palavra ficam 40 ms.

### Cortes, J-cut e junções

| Junção (s) | Fim da fala anterior | Próxima fala | Silêncio na junção | J-cut (áudio antes da imagem) |
| ---: | ---: | ---: | ---: | ---: |
| 4,500 | 4,430 | 4,550 | 120 ms | 16,7 ms* |
| 8,267 | 8,200 | 8,307 | 107 ms | 33,3 ms* |
| 19,367 | 19,300 | 19,410 | 110 ms | 50 ms |
| 25,000 | 24,930 | 25,042 | 112 ms | 50 ms |
| 32,250 | 32,173 | 32,302 | 128 ms | 50 ms |

\* Nas tomadas 2 e 3, o bruto só tem 16,7 ms e 33,3 ms de áudio da própria tomada antes do corte
(o resto pertence à tomada anterior). Para não puxar som de outra tomada, o J-cut foi limitado ao
material disponível.

- A cauda de cada frase fica em volume cheio até chegar ao ruído de fundo (−55 dB). Depois sai em
  rampa de até 170 ms, sem nunca passar do início do som seguinte.
  - Nas junções 1–5 a próxima fala chega antes, e a rampa ficou com 20 ms.
  - A última frase usa a rampa inteira de 170 ms, terminando em END.
- Os cortes de imagem são secos e quantizados ao quadro. Não há zoom nem movimento na imagem da câmera.

### Contato visual

- Detector de rosto YuNet (OpenCV) a cada 3 quadros, com proxies de guinada e arfagem.
- Inspeção visual de ~8 quadros por tomada e passos de 100 ms em torno de cada virada de cabeça.
- Resultado: o apresentador olha para a lente em todos os trechos usados, inclusive nos quadros finais
  de cada tomada até 39,7 s. Nenhum trecho A ou B precisou virar C por falta de contato visual.

## Composições (uma composição HyperFrames por trecho gráfico)

Ficam em `hf/comp/<TRECHO>/index.html` e usam o sistema visual em `hf/shared/brand.css`. Os eventos de
som de cada uma estão em `events.json`. A prancha de revisão de cada trecho, com as peças de
referência lado a lado, foi conferida antes do render (`work/review/*_sheet.jpg`).

| Trecho | O que mostra | Inspiração |
| --- | --- | --- |
| S1 (B) | Quadro 0 só com o fundo (a costa de Amalfi da peça 1, desfocada, com véu roxo). A peça 1 inteira sobe como cartão de story (472×840, topo y 40, base 880), passa 8 px e assenta em 0,73 s (impacto). Depois, Ken Burns suave (1→1,02) e deriva do fundo. | peça 1 |
| S2 (C) | Primeira menção: o selo INDIQUE E VIAJE! surge grande e centralizado (1,75×) em "Indique" e assenta (impacto). Depois recua para a posição fixa (73,138), o logotipo aparece e a peça 2 sobe como cartão flutuante (base y≈1226, impacto). O botão de seta aparece no fim. Deriva contínua de 1→1,025. | peça 2 (+ selo e logo das peças) |
| S3b (C) | Demonstração da mecânica. Primeiro, cartão de interface INDICAR / "Escolha um contato" com as linhas Amigo, Familiar e Colega, que acendem na palavra falada; a janela cresce 0,86→1 em 0,55 s com a câmera parada. Botão ENVIAR INDICAÇÃO pressionado (click), avião de papel (envio) e "Indicação enviada". Passagem rápida de 0,5 s (power3.inOut, 0,25 s antes de "fechar"; o cartão anterior desfoca até 12 px e cai para 70%). Depois, cartão de reserva "Sua viagem" com o carimbo verde VIAGEM FECHADA (confirmação). | peças 2, 3 e 5 (linguagem visual) |
| S3c (B) | Cartão de foto (amigas, peça 1) e box VOCÊ GANHA com contador R$ 0 → R$ 100 e "em crédito para sua próxima viagem" (impacto). Aproximação de 1,6 s (power2.inOut) até 1,5×. | peça 2 (box de valor) e peça 1 (foto) |
| S4b (B) | Cartão de foto (praia, peça 5) com o box SEU INDICADO GANHA R$50 "de benefício na contratação" (impacto). Passagem rápida até o cartão "Contratação da viagem" (passagem); a janela cresce 1→1,2× e o desconto "Benefício Indique e Viaje − R$ 50" é carimbado (confirmação), com check verde. | peças 2 e 5 |
| S5b (C) | Tabela da peça 4 (1 indicação = R$ 100 / 3 = R$ 300 / 5 = R$ 500). Cada linha acende na fala, com moedas empilhando e contador R$ 100 → R$ 300 → R$ 500 (três moedas). Deriva 1→1,03. Fundo: foto de Paris da peça 4, desfocada. | peça 4 (e peça 2) |
| S6a (B) | Frase de curiosidade no visual da peça 3: cartão de foto do lago com chapéu, selo e logo fixos e "JÁ TEM ALGUÉM / EM MENTE? 👀" em amarelo. O título sobe por máscara, palavra por palavra; o 👀 entra em "alguém". Ken Burns só na foto. Sem efeitos sonoros. | peça 3 |

Movimentos de câmera virtual usados:
- deriva (sine.inOut, ≤ 4%);
- passagem de 0,5 s (power3.inOut, começando 0,25 s antes da palavra), uma em S3b e uma em S4b;
- aproximação de 1,6 s até 1,5× (S3c);
- demos de janela de 1,16× e 1,2× com a câmera parada.

O quadro 0 de cada trecho é parado e nítido. Os cartões que saem de cena desfocam até 12 px, e nenhuma
informação legível fica borrada.

## Fontes das imagens

Nenhuma imagem de banco e nenhum rosto gerado. Tudo vem das cinco peças fornecidas (`referencias/`):

| Arquivo | Origem | Recorte (x, y, x2, y2) | Onde aparece |
| --- | --- | --- | --- |
| `assets/pecas/peca1..5.png` | peças inteiras (WebP → PNG) | — | mockups em S1 (peça 1) e S2 (peça 2) |
| `assets/fotos/costa_amalfi.png` | peça 1, área sem texto | 705,290 – 1080,1010 | fundos de S1 e S2, miniatura em S3b, fundo da contratação em S4b |
| `assets/fotos/amigas_selfie.png` | peça 1 | 0,1000 – 1080,1640 | cartão de foto de S3c |
| `assets/fotos/lago_chapeu.png` | peça 3 | 0,860 – 1080,1195 | cartão de foto de S6a |
| `assets/fotos/paris_casal.png` | peça 4 (só céu/torre, desfocado) | 0,745 – 1080,1225 | fundo de S5b |
| `assets/fotos/praia_sorriso.png` | peça 5 | 0,615 – 1080,1225 | cartão de foto de S4b, fundo de S3b |
| `assets/logo_parktur.png` | logotipo da peça 5 | 771,111 – 1032,270 | logo fixo e capa |

O logotipo foi extraído da peça 5 assim:
- o fundo foi reconstruído por inpaint;
- o alfa foi calculado pelo canal vermelho, (R − fundo)/(252 − fundo), e a cor foi des-pré-multiplicada;
- a proporção original foi mantida, sem distorção.

Nenhum texto foi escrito sobre texto existente das peças.

## Valores e regras da campanha: fala × peças

| Fala | Peças | Situação |
| --- | --- | --- |
| "você ganha R$ 100 de crédito para utilizar na sua próxima viagem" | Peça 2: "VOCÊ GANHA R$100 em crédito para sua próxima viagem" | confere |
| "quem você indicar também ganha R$ 50 de benefício na contratação da viagem" | Peça 2: "SEU INDICADO GANHA R$50 de benefício na contratação"; peça 5: "Seu indicado recebe: R$50 de benefício na contratação da viagem." | confere |
| "o seu crédito é acumulativo" | Peças 2 e 4: "Seu crédito é acumulativo." | confere |
| "quanto mais pessoas você indicar…, mais você vai ganhar" | Peça 4: "Quanto mais você indica, mais você ganha" e a tabela 1 = R$ 100, 3 = R$ 300, 5 = R$ 500 | confere (a tabela aparece só no gráfico de S5b, com os valores da peça 4) |
| "Se essa pessoa fechar uma viagem com a Parktur" (condição do crédito) | Não está escrita nas cinco peças recebidas. Está no briefing ("Indicou. Fechou. Ganhou.") | confere com o briefing |
| "indicar um amigo, um familiar ou um colega" | Peça 3: "Indique um amigo, familiar ou colega" | confere |

Nenhum valor, prazo ou regra fora dessa lista foi mostrado.

## Divergências entre fala e peças

1. O briefing fala em **seis** peças, mas só **cinco** foram fornecidas (`referencias/peca1..5.webp`).
2. O gancho diz "indicar um amigo pode te **auxiliar a pagar** sua próxima viagem". A peça 1 diz "E se
   seus amigos **ajudassem a pagar** sua próxima viagem?". É a mesma ideia com outras palavras. A peça
   aparece inteira, como mockup, e a legenda segue a fala.
3. A pronúncia na fala é "cumulativo". As peças escrevem "acumulativo", e a legenda usa a forma das peças.
4. A fala de S6a é "Já pensou em alguém que tá querendo viajar?". A peça 3, reproduzida no gráfico, diz
   "JÁ TEM ALGUÉM EM MENTE? 👀". A legenda segue a fala.
5. O CTA falado é "mande o nome pra gente e faça sua primeira indicação". Ele não pede para comentar uma
   palavra, então o CTA visual é a pílula "INDIQUE AGORA →", o texto do botão das peças 2 e 3. Não foram
   acrescentados plataforma, telefone nem pedido de DM.
6. A fala não cita os valores R$ 300 e R$ 500. Eles aparecem só no gráfico de acúmulo (S5b), fiéis à
   peça 4 e ao briefing.

## Capa, legendas e CTA

**Capa (só no quadro 0)**
- Título em caixa alta, 110 px: "INDIQUE AMIGOS / E **VIAJE MAIS**", com "VIAJE MAIS" em amarelo. O
  termo vem da faixa "INDIQUE MAIS. ACUMULE MAIS. VIAJE MAIS." das peças.
- Box roxo #63005E com raio de 30 px (2,8%) e respiro de 56/50 px, em y 282–603.
  - O topo ficou em 282 e não em 262 para não encostar no logotipo, que ocupa y 110–270 no canto
    superior direito.
- No quadro 0, todo o resto está abaixo de y 620: a cabeça começa em y≈816 (o apresentador ainda está
  longe da câmera) e o cartão em y 1200.

**Legendas**
- Geradas de `work/captions.json` a partir dos tempos finais das palavras (`scripts/captions.py`).
- A primeira entra no quadro 1 (16,7 ms); a capa ocupa o quadro 0.
- Blocos de 1 a 3 palavras, 74 px, Inter Tight 700, branco com contorno preto de 9 px (traço de 18 px
  atrás do preenchimento, juntas arredondadas) e sem caixa.
- Largura máxima de 800 px (x 140–940). Uma posição por trecho.
- Destaques em amarelo e caixa alta: INDICAR, PRÓXIMA VIAGEM?, MUITO SIMPLES, FECHAR, GANHA, E TEM MAIS,
  ACUMULATIVO., VIAJAR, GANHAR., VIAJAR?, NOME e INDICAÇÃO.
  - Ritmo: 2 a 3 blocos normais entre batidas, nunca dois destaques seguidos e nenhum destaque só com
    palavras funcionais.
  - "NOME" é o objeto do CTA ("mande o nome"), e "MUITO SIMPLES"/"E TEM MAIS" são as frases de impacto.
- Legendas escondidas porque o gráfico já mostra a mesma frase (o gráfico conta como batida de destaque):
  - "Indique e Viaje," (S2), com o selo grande na tela;
  - "um amigo, / um familiar / ou um colega." (S3b), com as linhas Amigo, Familiar e Colega;
  - todo o S3c, com o box VOCÊ GANHA R$ 100 em crédito para sua próxima viagem;
  - todo o S4b, com os textos SEU INDICADO GANHA R$50 de benefício na contratação e Contratação da viagem.
- Posições:

  | Layout | Faixa (y) |
  | --- | --- |
  | A e C | 1267–1536 (nos C, o elemento principal termina em ~1215–1230) |
  | Encerramento (S6b) | 1037–1306 |
  | B | **1530–1640**, ver desvio abaixo |

- **Desvio:** a faixa pedida para o B (941–1114) cai exatamente sobre a boca e o queixo nesta gravação,
  porque o enquadramento é médio e o rosto ocupa y≈560–1110 no layout B. Para nunca cobrir o rosto, as
  legendas do B ficam dentro do cartão, sobre o tronco.

**CTA (só no encerramento)**
- Pílula roxa "INDIQUE AGORA →", com texto branco de 68 px/700, centralizada na área x 43, y 1344,
  994×276.
- Entra em "mande" (34,967 s) com escala 0,72→1 em back.out e impacto leve ao assentar (35,137 s).
- Em "indicação" (37,533 s), toque do dedo (círculo branco translúcido com onda), pulsação
  1,0 → 1,06 → 1,0 e click.

## Efeitos sonoros

Todos são sintetizados em NumPy/SciPy (`scripts/sfx.py`), com quatro variações por tipo em rodízio
(nunca a mesma duas vezes seguidas). Não há efeito em troca de layout, deriva ou zoom. Os níveis são de
pico de amostra relativos ao pico da voz (−1,5 dBFS):
- click, impacto, confirmação e moeda: −10 dB;
- passagem: −9 dB;
- tecla e envio: −16 dB.

| Tempo (s) | Trecho | Tipo | Var. | Pico (dBFS) | Evento |
| ---: | --- | --- | :---: | ---: | --- |
| 0,700 | S1 | impacto | 1 | −11,5 | cartão da peça 1 assenta |
| 5,350 | S2 | impacto | 2 | −11,5 | selo INDIQUE E VIAJE! grande assenta |
| 7,210 | S2 | impacto | 3 | −11,5 | cartão da peça 2 assenta |
| 12,057 | S3b | click | 1 | −11,5 | botão ENVIAR INDICAÇÃO pressionado |
| 12,097 | S3b | envio | 1 | −17,5 | avião de papel sai do botão |
| 13,010 | S3b | passagem | 1 | −10,5 | ponto médio da passagem (12,760 → 13,260) |
| 13,630 | S3b | confirmação | 1 | −11,5 | carimbo VIAGEM FECHADA assenta |
| 15,620 | S3c | impacto | 4 | −11,5 | box VOCÊ GANHA assenta |
| 21,883 | S4b | impacto | 1 | −11,5 | box SEU INDICADO GANHA R$50 assenta |
| 23,680 | S4b | passagem | 2 | −10,5 | ponto médio da passagem (23,430 → 23,930) |
| 24,220 | S4b | confirmação | 2 | −11,5 | desconto − R$ 50 carimbado na contratação |
| 29,026 | S5b | moeda | 1 | −11,5 | 1ª moeda, R$ 100 |
| 30,671 | S5b | moeda | 2 | −11,5 | contador chega a R$ 300 |
| 31,918 | S5b | moeda | 3 | −11,5 | contador chega a R$ 500 |
| 35,137 | S6b | impacto | 2 | −11,5 | pílula INDIQUE AGORA assenta |
| 37,533 | S6b | click | 2 | −11,5 | toque do dedo na pílula |

Contagens:
- 3 moedas (máx. 3);
- 2 passagens (máx. 3, no máximo 1 por trecho), com pico exatamente no ponto médio do movimento;
- tecla: nenhuma (não houve digitação).

**Riser** (`scripts/riser.py`)
- Sub-seno com glissando de 42→96 Hz, ruído rosa com passa-baixa abrindo de 180 Hz a 1,4 kHz e leve
  modulação acelerando.
- Envelope exponencial de 2,6 s (1,900 → 4,500 s).
- O fim audível é exatamente a junção gancho → S2: última amostra acima de −80 dBFS em 4,4998 s, com
  rampa final de 6 ms.
- Pico −15,5 dBFS = pico da voz (−1,5) − 14 dB.

**Música** (`scripts/music.py`)
- Tropical house leve e acústica, 108 BPM, Ré maior, I–V–vi–IV.
- Instrumentos: violão dedilhado (Karplus-Strong), marimba nos contratempos, baixo redondo, cama de
  acorde filtrada, kick macio, estalo nos tempos 2 e 4 e shaker em semicolcheias.
- Sem voz e sem melodia principal.
- A primeira batida cai no quadro 1 (16,67 ms). Fade-in de 5 ms e fade-out de 800 ms terminando em END.
- Nível constante, sem ducking nem automação, normalizado a −24 LUFS.

## Loudness (ffmpeg ebur128)

| Faixa | LUFS integrado | Pico verdadeiro |
| --- | ---: | ---: |
| voice | −14,0 | −1,5 dBTP |
| sfx | −24,3 | −10,3 dBTP |
| riser | −26,5 | −15,5 dBTP |
| music | −24,0 | −9,3 dBTP |
| soma das stems (antes do limitador) | −13,5 | −0,1 dBTP |
| **master** | **−13,6** | **−1,3 dBTP** |
| áudio dentro do final.mp4 (AAC) | ⟨mp4_lufs⟩ | ⟨mp4_tp⟩ |

O master é a soma das stems sem mexer nos níveis. A soma passou de −1 dBTP (−0,1), então entrou um
limitador transparente de pico verdadeiro:
- detecção 4×, lookahead de 1,5 ms, liberação de 60 ms, teto de −1,3 dBTP;
- redução máxima de 1,19 dB, com cerca de 2,4 s no total acima de 0,1 dB.

A voz também passou por um limitador igual, com teto de −1,5 dBTP, para chegar a −14 LUFS: o ganho de
+6,8 dB levaria os picos a +2,4 dBFS. Esse limitador agiu em 23 transientes, com redução máxima de 4,1 dB.

## Limpeza de áudio (`scripts/clean_voice.sh`)

- O bruto tem AAC 44,1 kHz estéreo com L == R. Foi convertido para 48 kHz e para mono por média.
- `highpass=f=80:poles=2`, para tirar ronco abaixo da voz.
- `afftdn=nr=10:nf=-56:tn=0`, redução de ruído suave e sem artefato metálico.
- A latência do afftdn (1 198 amostras, 25 ms) foi compensada com `atrim` + `apad`. O atraso medido
  contra o original é 0.
- De-esser não usado: os picos da banda 5–9 kHz ficam 20,6 dB abaixo dos picos gerais.

## Geometria do layout dividido (B)

**Composição gráfica**
- Ocupa 1080×1920 atrás de tudo, com o conteúdo entre y 40 e 900.
- Some de y 900 a 1060 por uma máscara de 160 px.
- O elemento principal termina em y 880–897.

**Cartão da câmera**
- 1210×864 em x −65, y 1200.
- Cantos superelípticos (expoente 5) de raio 200, anti-serrilhados em 4×.
- Contorno interno de 4 px #FFC300 e a sombra de três camadas do sistema.

**Vídeo no cartão**
- O bruto é escalado para 1210 px de largura (fator 1,12037 = 1,0 da faixa 1,0–1,25), com Lanczos e
  x = −65.
- O y foi escolhido por trecho para a linha dos ombros ficar logo abaixo do topo do cartão (y≈1215):

  | Trecho | video_y | Topo da cabeça (mín./mediana) |
  | --- | ---: | --- |
  | S1 | 61 | 497/534 |
  | S3c | 136 | 588/637 |
  | S4b | 88 | 501/653 |
  | S6a | 76 | 559/598 |

**Recorte da cabeça**
- Matte do RobustVideoMatting (ResNet-50, ONNX, estados recorrentes, downsample 0,25), calculado no
  **mesmo quadro de origem** do cartão.
- Limpeza do matte:
  1. abertura morfológica e maior componente conectado;
  2. alfa abaixo de 0,25 zerado com smoothstep;
  3. descontaminação da borda, trocando a cor pela do interior vizinho;
  4. chave localizada para o luminoso rosa do fundo na fresta pescoço/gola de S1 (só numa faixa de
     40 px da borda, em y 950–1200).
- O recorte aparece por cima do topo do cartão e some numa transição de 40 px (smoothstep) logo abaixo
  da borda (y 1200–1240). Ali a imagem embaixo é idêntica (é o mesmo vídeo), então a transição não
  aparece e o pescoço cobre o contorno amarelo.

## Decisões técnicas

- **Fonte:** Inter Tight (OFL) com −2% de espaçamento, no lugar da Helvetica Neue Bold, que não está
  disponível. O 👀 usa um subconjunto do Noto Color Emoji.
- **Borrão de movimento:**
  - Os gráficos foram renderizados a 240 qps e combinados em grupos de 4 subquadros (obturador de 270°,
    sigma = 0,29 × v × 0,75/60).
  - Nos movimentos rápidos, 4 amostras deixavam cópias escalonadas visíveis. O intervalo entre os
    subquadros foi completado com quadros intermediários por fluxo óptico (DIS, uma amostra a cada
    ~3 px). Assim o borrão é contínuo, com o mesmo comprimento de obturador.
  - O sigma foi limitado a 40 px encurtando a janela do obturador.
  - Quadros parados não recebem borrão.
- **Cor:**
  - Bruto e gráficos são lidos com a matriz BT.709 declarada.
  - A saída sai em BT.709 de faixa limitada, com as tags gravadas.
- **Cortes de imagem:** secos, sem transição. A troca de layout acontece no corte, sem som.
- **J-cut:** limitado ao material da própria tomada (ver tabela).
- **Legendas do B:** fora da faixa pedida, sobre o tronco (ver desvio).
- **Capa:** box em y 282–603 em vez de 262–603, para não tocar o logotipo.
- **Fundos dos trechos C:** fotos das próprias peças, desfocadas e com véu roxo, em vez do fundo roxo
  sólido. O roxo sólido fica como reserva.

## Verificação final

⟨verificacao⟩

## Como reproduzir

```
scripts/clean_voice.sh brutoIndiqueeViaje.mp4 work          # voz limpa
.venv/bin/python scripts/asr_parakeet.py; .venv/bin/python scripts/asr_whisper.py   # transcrição
.venv/bin/python scripts/faces.py                            # rosto/contato visual
.venv/bin/python scripts/edl.py                              # EDL, trechos, palavras → work/edl.json, hf/data
.venv/bin/python scripts/matte.py <rvm.onnx> <f0> <f1> <aquecimento> work/matte/<B>.mkv   # S1, S3c, S4b, S6a
.venv/bin/python scripts/build_voice.py                      # stems/voice.wav
.venv/bin/python scripts/music.py 38.3 stems/music.wav
.venv/bin/python scripts/riser.py 38.3 4.5 stems/voice.wav stems/riser.wav
.venv/bin/python scripts/sfx.py 38.3 stems/voice.wav stems/sfx.wav
.venv/bin/python scripts/master.py                           # work/master.wav + loudness
.venv/bin/python scripts/captions.py                         # hf/data/captions.js
(cd hf && npx hyperframes render comp/<C|B> --fps 240 --crf 10 -o ../work/gfx/<TRECHO>_240.mp4)
(cd hf && npx hyperframes render comp/OVERLAY --format png-sequence --fps 60 -o ../work/overlay)
.venv/bin/python scripts/compose.py --audio work/master.wav --out final.mp4
.venv/bin/python scripts/verify.py
```

Os modelos (Parakeet, Whisper, YuNet, RVM) ficam em `edit/.models` e o venv em `edit/.venv`. Os dois
estão fora do git.
