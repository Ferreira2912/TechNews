# Indique e Viaje! (Parktur): plano de edição

Escrito antes da construção dos gráficos. Os tempos estão em milissegundos da linha do tempo final,
com 60 qps. **END = 37 667 ms** (2 260 quadros).

> Revisão depois da verificação final: o plano original tinha END = 38 300 ms. A verificação achou o
> início da tomada 2 marcado no ambiente (e não em "Chegou") e três pausas internas acima de 250 ms
> que não estavam na lista de compressão. Com a correção, S2, S3c e S6b ficaram mais curtos, S6a perdeu
> um quadro, e os tempos abaixo já são os finais.
>
> Revisão 2 (pedido do cliente): o layout dividido (B) saiu do vídeo inteiro. S1 passou a câmera cheia
> só com legenda. S3c, S4b e S6a passaram a câmera cheia com animação transparente por cima (box R$ 100;
> box R$ 50 → cartão de contratação; título "JÁ TEM ALGUÉM EM MENTE? 👀" em texto puro). Em S2, a peça 2
> virou texto puro.

## Tabela de trechos (0 → END)

| Trecho | Início | Fim | Duração | Layout | Fala (faixa final) | Conteúdo visual |
| --- | ---: | ---: | ---: | :---: | --- | --- |
| S1 | 0 | 4 500 | 4 500 | **A** câmera | E se eu te dissesse que indicar um amigo pode te auxiliar a pagar sua próxima viagem? | Gancho só com a câmera e a legenda (revisão 2: sem a peça 1). Capa no quadro 0. Riser termina em 4 500. |
| S2 | 4 500 | 8 033 | 3 533 | **C** visual | Chegou o Indique e Viaje, a nova campanha aqui da Parktur. | Primeira menção: o selo INDIQUE E VIAJE! surge grande e centralizado, recua para a posição fixa e a frase da peça 2 entra em texto puro ("SUA PRÓXIMA VIAGEM COMEÇA COM UMA INDICAÇÃO."), com logotipo e botão de seta; fundo roxo, sem imagem. |
| S3a | 8 033 | 9 283 | 1 250 | **A** câmera | E é muito simples, | Fala direta ao espectador. |
| S3b | 9 283 | 14 767 | 5 483 | **C** visual | você indica um amigo, um familiar ou um colega. Se essa pessoa fechar uma viagem com a Parktur, | Mecânica: cartão de indicação genérico (contato → amigo/familiar/colega) sendo enviado; passagem para um cartão de reserva Parktur que recebe o carimbo verde VIAGEM FECHADA. |
| S3c | 14 767 | 18 883 | 4 117 | **A** câmera + animação | você ganha R$ 100 de crédito para utilizar na sua próxima viagem | Valor isolado: box VOCÊ GANHA com contador R$ 0 → R$ 100 e "em crédito para sua próxima viagem", animado sobre o peito do apresentador (câmera cheia). |
| S4a | 18 883 | 21 100 | 2 217 | **A** câmera | e quem você indicar também ganha [é] | Frase de impacto, contato visual. |
| S4b | 21 100 | 24 517 | 3 417 | **A** câmera + animação | R$ 50 de benefício na contratação da viagem. | Valor isolado: box SEU INDICADO GANHA R$ 50 e, na passagem, o cartão Contratação da viagem com o desconto carimbado, sobre o peito do apresentador (câmera cheia). |
| S5a | 24 517 | 27 300 | 2 783 | **A** câmera | e tem mais, o seu crédito é acumulativo. | Frase de impacto (legenda em destaque: ACUMULATIVO). |
| S5b | 27 300 | 31 767 | 4 467 | **C** visual | Então, quanto mais pessoas você indicar para viajar com a gente, mais você vai ganhar. | Tabela de acúmulo 1/3/5 indicações sincronizada com moedas empilhando e contador R$ 100 → R$ 300 → R$ 500. |
| S6a | 31 767 | 34 117 | 2 350 | **A** câmera + animação | Já pensou em alguém que tá querendo viajar? | Frase de curiosidade: título da peça 3 "JÁ TEM ALGUÉM EM MENTE? 👀" em texto puro no alto, acima do cabelo, com degradê de leitura (câmera cheia, sem foto). |
| S6b | 34 117 | 37 667 | 3 550 | **A** câmera | Então mande o nome pra gente e faça sua primeira indicação. | Encerramento/CTA: botão INDIQUE AGORA → com impacto, toque e pulsação. |

Regras conferidas:
- Gancho em B e encerramento em A.
- Nenhum trecho passa de 8 s (o maior tem 5,48 s).
- Nunca há dois layouts iguais seguidos (sequência B C A C B A B A C B A).
- Os três layouts aparecem.

## Tomadas

O bruto já era uma montagem de seis tomadas, com cortes de imagem em 4,733, 8,617, 20,117, 25,883 e 33,433 s.
A transcrição (Parakeet TDT v3 e Whisper turbo) mostra cada frase **uma única vez**. Não há tentativas
repetidas, recomeços nem expressões de preparação, então cada tomada é a última e única versão da frase.
A hesitação "é" em "também ganha, é, R$ 50" está colada às palavras vizinhas, sem pausa. Ela fica no
áudio (um corte ali seria audível) e sai das legendas.

## Decisões de layout dividido (B)

- Vídeo: escala 1210/1080 (fator 1,0 da faixa permitida), x = −65.
- Altura por trecho, com a linha dos ombros em y ≈ 1215:
  - S1: y = 31
  - S3c: y = 117
  - S4b: y = 69
  - S6a: y = 41
- A cabeça ocupa y ≈ 470–1200 no centro. Por isso o conteúdo crítico (valores, títulos) fica em y 40–460.
  O elemento principal (cartão de foto/peça) vai até y ≈ 890 e passa atrás da cabeça.
- Legendas no B: a faixa pedida (941–1114) coincide com boca e queixo nesta gravação, porque o
  enquadramento é médio. Para nunca cobrir o rosto, as legendas do B ficam dentro do cartão, sobre o
  torso (y ≈ 1530–1640).
