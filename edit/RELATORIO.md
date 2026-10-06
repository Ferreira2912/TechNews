# Relatório de edição: Reel "INDIQUE E VIAJE!" (Parktur)

Todo o trabalho foi feito por código: FFmpeg, Python (venv local em `edit/.venv`), Node (npm local em
`edit/hf`) e HyperFrames 0.8.137. Nada foi instalado globalmente. A trilha e os efeitos são sintetizados,
sem nenhum arquivo de áudio externo.

> **Revisão 2 (pedido do cliente).** O layout dividido (cartão com a câmera embaixo e a cabeça recortada
> por cima) saiu do vídeo inteiro. Esses trechos agora mostram só o apresentador em tela cheia, com a
> legenda e animações no estilo do cartão "Contratação da viagem", sem cobrir o rosto. As imagens das
> peças também saíram do início e do fim: a peça 2 em S2 virou texto puro, e a peça 1 (S1) e a foto do
> lago (S6a) foram removidas. Detalhes em "Revisão 2" no fim deste relatório.

## Entregas

| Arquivo | Conteúdo |
| --- | --- |
| `final.mp4` | 1080×1920, 60 qps (CFR), H.264 High (CRF 14, preset slow, BT.709), ~12 Mb/s, AAC estéreo 48 kHz 320 kb/s, 37,667 s |
| `stems/voice.wav` | voz montada (J-cuts, pausas comprimidas), 37,667 s |
| `stems/sfx.wav` | efeitos sintetizados, 37,667 s |
| `stems/riser.wav` | riser grave do gancho, 37,667 s |
| `stems/music.wav` | trilha sintetizada, 37,667 s |
| `verificacao/` | pranchas de contato e de cortes, medições (JSON) de loudness, efeitos, legendas e verificação |

Todas as stems são WAV float 32 bits, 48 kHz, estéreo, com a duração exata do vídeo e começando em 0.
A soma das quatro stems (com o limitador do master) é o áudio do `final.mp4`.

## END

**END = 37 667 ms** (2 260 quadros a 60 qps). É o fim exclusivo da faixa de voz. Todas as camadas
(vídeo, legendas, CTA, voz, efeitos, riser e música) terminam exatamente em END.

## Tabela de trechos

A tabela foi escrita antes dos gráficos, em `PLANO.md`, e atualizada duas vezes:
- depois da verificação das pausas e junções, quando mudaram S2, S3c, S6a, S6b e todos os tempos a
  partir de S2;
- na revisão 2, quando o layout dividido saiu e S1, S3c, S4b e S6a passaram a câmera cheia.

"A + animação" é a câmera cheia, intacta, com uma camada gráfica transparente por cima.

| Trecho | Início (ms) | Fim (ms) | Duração | Layout | Fala | Quadros de origem (bruto, 60 qps) |
| --- | ---: | ---: | ---: | :---: | --- | --- |
| S1 | 0 | 4 500 | 4,50 s | **A** | E se eu te dissesse que indicar um amigo pode te auxiliar a pagar sua próxima viagem? | 0–270 |
| S2 | 4 500 | 8 033 | 3,53 s | **C** | Chegou o Indique e Viaje, a nova campanha aqui da Parktur. | 289–511 (pausa 398–408 removida) |
| S3a | 8 033 | 9 283 | 1,25 s | **A** | E é muito simples, | 519–594 |
| S3b | 9 283 | 14 767 | 5,48 s | **C** | você indica um amigo, um familiar ou um colega. Se essa pessoa fechar uma viagem com a Parktur, | 594–945 (pausa 768–790 removida) |
| S3c | 14 767 | 18 883 | 4,12 s | **A + animação** | você ganha R$ 100 de crédito para utilizar na sua próxima viagem | 945–1207 (pausa 1075–1090 removida) |
| S4a | 18 883 | 21 100 | 2,22 s | **A** | e quem você indicar também ganha, [é] | 1210–1343 |
| S4b | 21 100 | 24 517 | 3,42 s | **A + animação** | R$ 50 de benefício na contratação da viagem. | 1343–1548 |
| S5a | 24 517 | 27 300 | 2,78 s | **A** | e tem mais, o seu crédito é acumulativo. | 1556–1723 |
| S5b | 27 300 | 31 767 | 4,47 s | **C** | Então, quanto mais pessoas você indicar para viajar com a gente, mais você vai ganhar. | 1723–2002 (pausa 1919–1930 removida) |
| S6a | 31 767 | 34 117 | 2,35 s | **A + animação** | Já pensou em alguém que tá querendo viajar? | 2010–2151 |
| S6b | 34 117 | 37 667 | 3,55 s | **A** | Então mande o nome pra gente e faça sua primeira indicação. | 2151–2372 (pausa 2247–2255 removida) |

Regras conferidas:
- O encerramento a partir do CTA está em A.
- O maior trecho tem 5,48 s, abaixo do limite de cerca de 8 s.
- Mecânica (S3b) e tabela de acúmulo (S5b) estão em C.
- Valores isolados (S3c, S4b) e a curiosidade (S6a) estão na câmera cheia, com o valor ou o título
  animado por cima.
- Frases de impacto e afirmações diretas (S1, S3a, S4a, S5a, S6b) estão em A, com contato visual.

Regras do briefing original que a revisão do cliente substituiu:
- O gancho não está mais no layout dividido (B), e o B não aparece mais no vídeo.
- Há trechos A seguidos: S3c → S4a → S4b → S5a e S6a → S6b. Neles, a variação vem das animações por
  cima da câmera e dos cortes entre tomadas.

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
- Pausas internas: medidas com a mesma regra do fim de frase (janelas de 10 ms abaixo de −35 dB na voz
  limpa). Todas as que passam de 250 ms foram comprimidas para 120 ms (ficam 60 ms de cada lado):

  | Tomada | Pausa no bruto (s) | Duração | Entre | Onde cai o corte de imagem |
  | --- | --- | ---: | --- | --- |
  | 2 | 6,58–6,86 | 280 ms | "Viaje," / "A nova campanha" | S2 (C, gráfico cobre a câmera) |
  | 3 | 12,74–13,23 | 490 ms | "colega." / "Se essa pessoa" | S3b (C) |
  | 3 | 17,86–18,23 | 370 ms | "de crédito" / "para utilizar" | S3c (A): corte seco na câmera, sob o box animado |
  | 5 | 31,93–32,23 | 300 ms | "com a gente," / "mais você vai ganhar" | S5b (C) |
  | 6 | 37,39–37,65 | 260 ms | "pra gente" / "e faça" | S6b (A): corte seco na câmera |

  - Fica a de 240 ms em 23,94–24,18 (tomada 4), abaixo do limite.
  - Os dois cortes secos visíveis (S3c e S6b) unem quadros com o apresentador olhando para a lente.
- Fim verdadeiro de cada frase: última janela RMS de 10 ms com nível ≥ −35 dB, confirmada pela regra
  −32 dB/150 ms. Valores no bruto: 4,43 / 8,45 / 20,05 / 25,73 / 33,29 / 39,20 s.
- Início de cada frase: primeira janela ≥ −35 dB (tomada 2: "Chegou" em 4,865 s; tomada 6: "Já" em 33,54 s).
  O corte de imagem entra 40 ms antes da primeira palavra.

### Cortes, J-cut e junções

Silêncio medido na voz montada com a regra do fim de frase (RMS de 10 ms abaixo de −35 dB na voz
limpa, passo de 1 ms; ver Verificação).

| Junção (s) | Fim da fala anterior (s) | Próxima fala (s) | Silêncio medido | J-cut (áudio antes da imagem) |
| ---: | ---: | ---: | ---: | ---: |
| 4,500 | 4,430 | 4,548 | 136 ms | 50 ms |
| 8,033 | 7,967 | 8,073 | 130 ms | 33,3 ms* |
| 18,883 | 18,817 | 18,927 | 144 ms | 50 ms |
| 24,517 | 24,447 | 24,558 | 122 ms | 50 ms |
| 31,767 | 31,690 | 31,822 | 145 ms | 50 ms |

\* Na tomada 3, o bruto só tem 33,3 ms de áudio dessa tomada antes do corte (o resto pertence à tomada
anterior). Para não puxar som de outra tomada, o J-cut ficou limitado ao material disponível.

- A cauda de cada frase fica em volume cheio até chegar ao ruído de fundo (−55 dB). Depois sai em
  rampa de até 170 ms, sem nunca passar do início do som seguinte.
  - Nas junções 1–5 a próxima fala chega antes, e a rampa ficou com 20 ms.
  - A última frase usa a rampa inteira de 170 ms, terminando em END.
- Os cortes de imagem são secos e quantizados ao quadro. Não há zoom nem movimento na imagem da câmera.

### Contato visual

- Detector de rosto YuNet (OpenCV) a cada 3 quadros, com proxies de guinada e arfagem.
- Inspeção visual de ~8 quadros por tomada e passos de 100 ms em torno de cada virada de cabeça.
- Resultado: o apresentador olha para a lente em todos os trechos usados, inclusive nos quadros finais
  de cada tomada até 39,7 s. Nenhum trecho de câmera precisou virar C por falta de contato visual.

## Composições (uma composição HyperFrames por trecho gráfico)

Ficam em `hf/comp/<TRECHO>/index.html` e usam o sistema visual em `hf/shared/brand.css`. Os eventos de
som de cada uma estão em `events.json`. Cada composição passou por uma prancha de revisão antes do
render (`work/review/*_sheet.jpg`):
- trechos C: os snapshots ao lado das peças de referência;
- animações sobre a câmera: os snapshots aplicados sobre o quadro real da câmera, com a caixa do rosto
  e as faixas livres desenhadas.

Na revisão 2, cada composição nova passou por um construtor e por um revisor independente. O revisor
mediu a pegada de cada animação (pixels com alfa > 8) contra as zonas do rosto em
`hf/data/zonas_rosto.json` e corrigiu o que estava fora.

| Trecho | O que mostra | Inspiração |
| --- | --- | --- |
| S1 (A) | Só o apresentador e a legenda (a capa ocupa o quadro 0). Sem gráfico e sem a peça 1. | — |
| S2 (C) | Primeira menção, só com texto e o logotipo, sem nenhuma imagem. Fundo radial roxo (#7A0A74 → #2B0029) com deriva suave.<br>• "Indique": o selo INDIQUE E VIAJE! surge grande e centralizado (1,75×, back.out) e assenta (impacto).<br>• "A nova campanha": o selo recua para a posição fixa (73,138), o logotipo entra (back.out leve) e a frase oficial da peça 2 aparece em texto puro, linha a linha por máscara: "SUA PRÓXIMA / VIAGEM COMEÇA / COM UMA / INDICAÇÃO.", 104 px, com PRÓXIMA, VIAGEM e INDICAÇÃO. em amarelo, base em y≈1228.<br>• O botão de seta aparece no fim. | peça 2 (texto e selo) |
| S3b (C) | Demonstração da mecânica, sem mudança nesta revisão.<br>• Cartão INDICAR / "Escolha um contato": as linhas Amigo, Familiar e Colega acendem na palavra falada.<br>• Botão ENVIAR INDICAÇÃO (click), avião de papel (envio) e "Indicação enviada".<br>• Passagem rápida de 0,5 s até o cartão de reserva "Sua viagem", com o carimbo verde VIAGEM FECHADA (confirmação). | peças 2, 3 e 5 (linguagem visual) |
| S3c (A + animação) | Box "VOCÊ GANHA / R$ 100 / em crédito para sua próxima viagem" sobre o peito, longe do rosto. Roxo sólido, borda amarela de 4 px, etiqueta roxa com contorno amarelo, 608×356 centrado em x 490, y 1290.<br>• Entra em "ganha" com back.out (impacto).<br>• Conta de R$ 0 a R$ 100 em "R$ 100".<br>• Cresce até 1,15× (demonstração) em "de crédito", com faíscas presas ao valor.<br>• Some suavemente antes do corte para S4a. | peça 2 (box de valor) |
| S4b (A + animação) | Na faixa sobre o peito (y 1054–1635):<br>• Box "SEU INDICADO GANHA / R$ 50 / de benefício na contratação" (impacto).<br>• Passagem de 0,5 s em "contratação": o box sai pela esquerda e o cartão branco "Contratação da viagem" entra pela direita (passagem).<br>• O cartão cresce até 1,15×, e a pílula amarela "Benefício Indique e Viaje − R$ 50" é carimbada na vaga, com check verde (confirmação).<br>É o cartão que o cliente indicou como referência. | peças 2 e 5 |
| S5b (C) | Tabela da peça 4 (1 indicação = R$ 100 / 3 = R$ 300 / 5 = R$ 500). Cada linha acende na fala, com moedas empilhando e contador R$ 100 → R$ 300 → R$ 500. Sem mudança nesta revisão. | peça 4 (e peça 2) |
| S6a (A + animação) | Título da peça 3 em texto puro, no alto e acima do cabelo: "JÁ TEM ALGUÉM / EM MENTE? 👀", amarelo, 104 px, em x 66–880 e y 147–376. Fica sobre um degradê escuro suave que some antes do cabelo, sem foto.<br>• Palavras sobem por máscara a partir de "Já".<br>• O 👀 entra em "alguém".<br>• Tudo sai suavemente nos últimos 0,27 s, porque S6b continua o mesmo plano. | peça 3 |

Movimentos usados:
- deriva (sine.inOut, ≤ 4%);
- passagem de 0,5 s (power3.inOut, começando 0,25 s antes da palavra): uma em S3b e uma em S4b;
- demos de janela de 1,15× a 1,2×;
- entradas com back.out.

A imagem da câmera nunca é ampliada nem movida. O quadro 0 de cada trecho é parado e nítido, e nenhuma
informação legível fica borrada.

## Fontes das imagens

Nenhuma imagem de banco e nenhum rosto gerado. As imagens vêm das cinco peças fornecidas
(`referencias/`). Depois da revisão 2, o vídeo usa só estas:

| Arquivo | Origem | Onde aparece |
| --- | --- | --- |
| `assets/logo_parktur.png` | logotipo da peça 5 (recorte 771,111 – 1032,270) | capa (quadro 0), S2, S3b e S5b |
| `assets/fotos/praia_sorriso.png` | peça 5 (0,615 – 1080,1225), muito desfocada | fundo de S3b (9,3–14,8 s) |
| `assets/fotos/costa_amalfi.png` | peça 1 (705,290 – 1080,1010) | miniatura no cartão "Sua viagem" de S3b (≈13–14,8 s) |
| `assets/fotos/paris_casal.png` | peça 4 (0,745 – 1080,1225), muito desfocada (só céu e torre) | fundo de S5b (27,3–31,8 s) |

O início do vídeo (capa, S1, S2) e o fim (S6a, S6b) não têm nenhuma imagem de peça ou foto, só texto,
o logotipo e a câmera. As peças inteiras (`assets/pecas/`) e as fotos `amigas_selfie` e `lago_chapeu`
não aparecem mais no vídeo; continuam em `assets/` só como referência.

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
   seus amigos **ajudassem a pagar** sua próxima viagem?". É a mesma ideia com outras palavras. Na
   revisão 2 a peça saiu do gancho, que ficou só com a câmera e a legenda da fala.
3. A pronúncia na fala é "cumulativo". As peças escrevem "acumulativo", e a legenda usa a forma das peças.
4. A fala de S6a é "Já pensou em alguém que tá querendo viajar?". O título em texto puro de S6a usa a
   frase da peça 3, "JÁ TEM ALGUÉM EM MENTE? 👀". A legenda, embaixo, segue a fala.
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
- No quadro 0 (câmera cheia), todo o resto está abaixo de y 620: o apresentador ainda está longe da
  câmera, e o topo do cabelo fica em y 669.

**Legendas**
- Geradas por `scripts/captions.py` a partir dos tempos finais das palavras (lista completa, com tempos de entrada e saída, em `verificacao/legendas.json`).
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
  | A (inclusive S1 e S6a) e C | 1267–1536 (nos C, o elemento principal termina em ~1215–1230) |
  | Encerramento (S6b) | 1037–1306 |

- Com o fim do layout dividido, sumiu também o desvio da versão anterior, em que as legendas do B
  ficavam sobre o tronco.

**CTA (só no encerramento)**
- Pílula roxa "INDIQUE AGORA →", com texto branco de 68 px/700, centralizada na área x 43, y 1344,
  994×276.
- Entra em "mande" (34,467 s) com escala 0,72→1 em back.out e impacto leve ao assentar (34,637 s).
- Em "indicação" (36,900 s), toque do dedo (círculo branco translúcido com onda), pulsação
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
| 5,173 | S2 | impacto | 1 | −11,5 | selo INDIQUE E VIAJE! grande assenta ("Indique" + 0,07 s) |
| 11,823 | S3b | click | 1 | −11,5 | botão ENVIAR INDICAÇÃO pressionado |
| 11,863 | S3b | envio | 1 | −17,5 | avião de papel sai do botão |
| 12,776 | S3b | passagem | 1 | −10,5 | ponto médio da passagem (12,526 → 13,026) |
| 13,396 | S3b | confirmação | 1 | −11,5 | carimbo VIAGEM FECHADA assenta |
| 15,267 | S3c | impacto | 2 | −11,5 | box VOCÊ GANHA assenta sobre a câmera ("ganha" + 0,12 s) |
| 21,307 | S4b | impacto | 3 | −11,5 | box SEU INDICADO GANHA R$ 50 assenta ("R$ 50" + 0,19 s) |
| 23,197 | S4b | passagem | 2 | −10,5 | ponto médio da passagem box → cartão (22,947 → 23,447) |
| 23,747 | S4b | confirmação | 2 | −11,5 | pílula − R$ 50 carimbada no cartão de contratação |
| 28,543 | S5b | moeda | 1 | −11,5 | 1ª moeda, R$ 100 |
| 30,188 | S5b | moeda | 2 | −11,5 | contador chega a R$ 300 |
| 31,435 | S5b | moeda | 3 | −11,5 | contador chega a R$ 500 |
| 34,637 | S6b | impacto | 4 | −11,5 | pílula INDIQUE AGORA assenta |
| 36,900 | S6b | click | 2 | −11,5 | toque do dedo na pílula |

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
| sfx | −24,1 | −10,2 dBTP |
| riser | −26,5 | −15,5 dBTP |
| music | −24,0 | −9,3 dBTP |
| soma das stems (antes do limitador) | −13,5 | +0,4 dBTP |
| **master** | **−13,6** | **−1,3 dBTP** |
| áudio dentro do final.mp4 (AAC) | −13,6 | −1,3 dBTP |

O master é a soma das stems sem mexer nos níveis. A soma passou de −1 dBTP (+0,4), então entrou um
limitador transparente de pico verdadeiro:
- detecção 4×, lookahead de 1,5 ms, liberação de 60 ms, teto de −1,3 dBTP;
- redução máxima de 1,71 dB, com cerca de 1,8 s no total acima de 0,1 dB.

A voz também passou por um limitador igual, com teto de −1,5 dBTP, para chegar a −14 LUFS: o ganho de
+6,75 dB levaria os picos a cerca de +2,5 dBFS. Esse limitador agiu em 22 transientes, com redução
máxima de 4,0 dB.

## Limpeza de áudio (`scripts/clean_voice.sh`)

- O bruto tem AAC 44,1 kHz estéreo com L == R. Foi convertido para 48 kHz e para mono por média.
- `highpass=f=80:poles=2`, para tirar ronco abaixo da voz.
- `afftdn=nr=10:nf=-56:tn=0`, redução de ruído suave e sem artefato metálico.
- A latência do afftdn (1 198 amostras, 25 ms) foi compensada com `atrim` + `apad`. O atraso medido
  contra o original é 0.
- De-esser não usado: os picos da banda 5–9 kHz ficam 20,6 dB abaixo dos picos gerais.

## Animações sobre a câmera (S3c, S4b, S6a)

- Composições HyperFrames com fundo transparente, renderizadas em sequência PNG RGBA a 240 qps
  (`work/gfx/<TRECHO>_240/`).
- O montador aplica cada uma sobre o quadro **intacto** da câmera, sem reescala, corte nem movimento.
- O borrão de movimento é o mesmo dos gráficos: 4 subquadros e preenchimento por fluxo óptico. Aqui ele
  é calculado em RGBA pré-multiplicado, para a borda das peças não escurecer.
- Zonas do rosto medidas em todos os quadros de origem de cada trecho (topo do cabelo pelo matte RVM,
  rosto pelo YuNet), guardadas em `hf/data/zonas_rosto.json`:

  | Trecho | Topo do cabelo (mín.) | Queixo (máx.) | Onde fica a animação | Pegada medida (alfa > 8) |
  | --- | ---: | ---: | --- | --- |
  | S3c | 404 | 957 | faixa de baixo, sobre o peito | x 63–916, y 1021–1640 |
  | S4b | 368 | 1000 | faixa de baixo, sobre o peito | x 61–918, y 1054–1635 |
  | S6a | 431 | 1026 | faixa de cima, acima do cabelo | x 66–880, y 147–376 |

- Nenhum pixel das animações cai na caixa do rosto, à direita de x 940 entre y 900 e 1650, acima de
  y 110 ou abaixo de y 1650. A conferência foi feita em todos os subquadros (ver Verificação).
- Sobre o vídeo, os boxes e cartões são opacos e têm a sombra de três camadas. Assim leem bem sobre a
  camisa branca.

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
- **Capa:** box em y 282–603 em vez de 262–603, para não tocar o logotipo.
- **Fundos dos trechos C:**
  - S2 usa o radial roxo puro, porque fica no início do vídeo e o cliente pediu que não houvesse
    imagem ali.
  - S3b e S5b, no meio do vídeo, mantêm fotos das peças muito desfocadas, que funcionam como campo
    de cor, com véu roxo.

## Correções feitas na verificação

A primeira montagem (END 38 300 ms) passou pela verificação abaixo e foi corrigida antes da entrega:

1. **Quadros da tomada errada nas fronteiras.**
   - O mapa de quadros (saída → bruto) comparava tempos arredondados a 6 casas sem tolerância.
   - Por isso, os quadros 496, 745, 1162 e 1500 apontavam para a tomada vizinha. Isso criaria um
     quadro "relâmpago" da tomada anterior no início de S3a, S4a e S5a.
   - O montador acusou o erro (mapa não monotônico). A tolerância agora é de menos de meio quadro.
2. **Junção 1 com 180 ms de silêncio.**
   - O início da tomada 2 estava marcado em 4,80 s, que é ambiente. A fala ("Chegou") começa em 4,865 s.
   - Com o início real, a junção ficou com cerca de 136 ms.
   - Antes de corrigir na origem, foi testado um esticamento de 1,1% da tomada 2 (Rubber Band). Ele
     foi descartado: escondia o erro em vez de corrigir.
3. **Pausas internas acima de 250 ms que não estavam na lista de compressão.**
   - 280 ms (tomada 2), 370 ms (tomada 3) e 260 ms (tomada 6), medidas com a mesma regra de −35 dB.
   - Foram comprimidas para 120 ms. Duas delas viram cortes secos visíveis (S3c e S6b).
   - END passou para 37 667 ms.
4. **Junção 5 no limite (146–161 ms, conforme a janela).**
   - A tomada 6 entrava 1 quadro antes do necessário. Agora entra 40 ms antes de "Já" (33,50 s), e a
     junção mede cerca de 144 ms.
5. **Recorte da cabeça do layout dividido.**
   - Havia halo, um ponto rosa e pontinhos do fundo no contorno da cabeça. Foram corrigidos com
     limpeza do matte.
   - Na revisão 2 o layout dividido saiu por completo, e com ele o recorte.
6. **Borrão de movimento escalonado.** Corrigido com o preenchimento por fluxo óptico.

## Revisão 2: pedido do cliente

Pedido: "todas essas partes que tem o card com a cabeça aparecendo por cima meio a meio tem que
remover, não ficou legal, de todo o video, tem que deixar com ele apenas, a legenda, e as animações
assim […] não quero que utilize essa imagem no inicio do video, nem no final também, ou troque por
texto puro ou remova".

O que mudou:

| Trecho | Antes | Agora |
| --- | --- | --- |
| S1 (gancho) | layout dividido, com a peça 1 inteira como cartão | câmera cheia + legenda |
| S2 | selo, logotipo e a peça 2 como cartão sobre foto desfocada | selo, logotipo e a frase da peça 2 em **texto puro** sobre o roxo; nenhuma imagem |
| S3c | layout dividido, com foto das amigas e box R$ 100 | câmera cheia + box R$ 100 animado sobre o peito |
| S4b | layout dividido, com foto da praia, box R$ 50 e cartão de contratação | câmera cheia + box R$ 50 → cartão "Contratação da viagem" (o modelo indicado pelo cliente) sobre o peito |
| S6a | layout dividido, com foto do lago e título | câmera cheia + título "JÁ TEM ALGUÉM EM MENTE? 👀" em **texto puro** no alto |

Consequências:
- Saíram do pipeline o cartão da câmera, o matte RVM e as chaves de recorte.
- As legendas de S1 e S6a passaram para a faixa da câmera cheia.
- Saíram os efeitos do cartão da peça 1 (S1) e do cartão da peça 2 (S2).
- A edição da fala, os cortes, as junções, a trilha, o riser e o END não mudaram.

## Verificação final

Feita com `scripts/verify.py` sobre o `final.mp4` entregue. Dados em `verificacao/verificacao.json` e
pranchas em `verificacao/`.

| Item | Resultado |
| --- | --- |
| Formato | h264 High 1080x1920 60/1 yuv420p bt709; 2260 quadros = 37.666667 s; aac 48000 Hz 2 canais 327 kb/s; vídeo e áudio começam em 0 |
| Quadros brancos / pretos | 0 / 0 (luminância média por quadro entre 75.2 e 158.4) |
| Quadros congelados | maior sequência idêntica: 9 quadros (0,15 s), no quadro 0 parado de S3b (por regra) |
| Cortes | `verificacao/cortes_entre_trechos.jpg`: os 10 cortes entre trechos têm quadros reais dos dois lados e cada trecho A abre na tomada certa. `verificacao/cortes_secos_pausas.jpg`: os cortes secos de S3c e S6b ligam quadros com o apresentador olhando para a lente |
| Prancha completa | `verificacao/prancha_de_contato.jpg`: 1 quadro a cada 0,5 s |
| Cabeça × cartão | o recorte usa o mesmo quadro de origem do cartão em todos os quadros (por construção: um único índice de origem por quadro). Nos movimentos rápidos só o gráfico se move. A cabeça aparece desde o 1º quadro de cada B (fração da faixa y 1000–1195 fora do fundo roxo: S1 0.30, S3c 0.52, S4b 0.45, S6a 0.36) |
| Sincronia | atraso entre o áudio do MP4 e o master: 0 amostras. A imagem da câmera é sempre o quadro de origem da mesma tomada do áudio (J-cut só antecipa o som) |
| Loudness do MP4 | -13.6 LUFS, -1.3 dBTP (alvo −14 ± 0,5 LU e ≤ −1 dBTP) |
| Stems | as quatro com 37.666667 s = END |
| Silêncio nas junções | 136, 130, 144, 122, 145 ms (todas ≤ 150 ms; regra do fim de frase, −35 dB na voz limpa, passo de 1 ms) |
| Pausas internas | maior: 249 ms (tomada 4, abaixo de 250 ms); nenhuma outra ≥ 200 ms |
| Riser | audível de 2.014 s a 4.4996 s (junção em 4,500 s); pico -15.51 dBFS = voz -1.51 − 14 dB |
| Música | primeira amostra audível em 16.77 ms (quadro 1), fade-out terminando em END |
| Efeitos | passagens com pico no ponto médio dos movimentos (12,776 s e 23,197 s); 3 moedas; nenhum efeito em troca de layout |
| Legendas | 42 blocos visíveis e 6 ocultos pelo gráfico; largura máx. 800 px (x 140–940); nenhum bloco sobre o rosto (menor folga entre queixo e faixa: 49 px); nenhum acima de y 110 ou abaixo de y 1650 |

## Como reproduzir

```
scripts/clean_voice.sh brutoIndiqueeViaje.mp4 work          # voz limpa
.venv/bin/python scripts/asr_parakeet.py; .venv/bin/python scripts/asr_whisper.py   # transcrição
.venv/bin/python scripts/faces.py                            # rosto/contato visual
.venv/bin/python scripts/edl.py                              # EDL, trechos, palavras → work/edl.json
.venv/bin/python scripts/segments.py                         # hf/data/segments.* + data-duration das composições
.venv/bin/python scripts/matte.py <rvm.onnx> <f0> <f1> <aquecimento> work/matte/<TRECHO>.mkv   # S3c 945, S4b 1343, S6a 2009
#   (o quadro inicial de cada matte vai em work/matte/bases.json; o matte só serve para medir o topo do cabelo)
.venv/bin/python scripts/zonas_rosto.py                      # hf/data/zonas_rosto.json (faixas livres para as animações)
.venv/bin/python scripts/build_voice.py                      # stems/voice.wav
.venv/bin/python scripts/captions.py                         # hf/data/captions.js + eventos do CTA
.venv/bin/python scripts/music.py 37.666667 stems/music.wav
.venv/bin/python scripts/riser.py 37.666667 4.5 stems/voice.wav stems/riser.wav
.venv/bin/python scripts/sfx.py 37.666667 stems/voice.wav stems/sfx.wav
.venv/bin/python scripts/master.py                           # work/master.wav + loudness
(cd hf && npx hyperframes render comp/<S2|S3b|S5b> --fps 240 --crf 10 -o ../work/gfx/<TRECHO>_240.mp4)
(cd hf && npx hyperframes render comp/<S3c|S4b|S6a> --format png-sequence --fps 240 -o ../work/gfx/<TRECHO>_240)
(cd hf && npx hyperframes render comp/OVERLAY --format png-sequence --fps 60 -o ../work/overlay)
.venv/bin/python scripts/compose.py --audio work/master.wav --out final.mp4      # numa passada só
# (ou em partes paralelas: compose.py --frames a:b --out work/part_a.mkv; depois cada parte → MPEG-TS
#  com h264_mp4toannexb, junção com o protocolo concat e carimbos ajustados à grade exata de 1/60 s:
#  ffmpeg -i "concat:a.ts|b.ts|…" -i work/master.wav -c:v copy
#         -bsf:v "setts=pts=round(PTS*TB*60)/(60*TB):dts=round(DTS*TB*60)/(60*TB)" -c:a aac -b:a 320k final.mp4)
.venv/bin/python scripts/verify.py
```

Os modelos (Parakeet, Whisper, YuNet e RVM, usado só para medir o topo do cabelo) ficam em `edit/.models` e o venv em `edit/.venv`. Os dois
estão fora do git, assim como `work/` (arquivos intermediários, todos regeneráveis). O bruto
`brutoIndiqueeViaje.mp4` também fica fora do repositório: para reproduzir, coloque-o em `edit/`.
