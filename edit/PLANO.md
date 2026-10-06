# Indique e Viaje! (Parktur): plano de edição

Escrito antes da construção dos gráficos. Os tempos estão em milissegundos da linha do tempo final,
com 60 qps. **END = 38 300 ms** (2 298 quadros).

## Tabela de trechos (0 → END)

| Trecho | Início | Fim | Duração | Layout | Fala (faixa final) | Conteúdo visual |
| --- | ---: | ---: | ---: | :---: | --- | --- |
| S1 | 0 | 4 500 | 4 500 | **B** dividido | E se eu te dissesse que indicar um amigo pode te auxiliar a pagar sua próxima viagem? | Gancho. A peça oficial "E se seus amigos ajudassem…" sobe como cartão de story sobre o fundo desfocado da própria peça. Capa no quadro 0. Riser termina em 4 500. |
| S2 | 4 500 | 8 267 | 3 767 | **C** visual | Chegou o Indique e Viaje, a nova campanha aqui da Parktur. | Primeira menção: o selo INDIQUE E VIAJE! surge grande e centralizado, recua para a posição fixa e revela a peça principal (story mockup), com logotipo e botão de seta. |
| S3a | 8 267 | 9 517 | 1 250 | **A** câmera | E é muito simples, | Fala direta ao espectador. |
| S3b | 9 517 | 15 000 | 5 483 | **C** visual | você indica um amigo, um familiar ou um colega. Se essa pessoa fechar uma viagem com a Parktur, | Mecânica: cartão de indicação genérico (contato → amigo/familiar/colega) sendo enviado; passagem para um cartão de reserva Parktur que recebe o carimbo verde VIAGEM FECHADA. |
| S3c | 15 000 | 19 367 | 4 367 | **B** dividido | você ganha R$ 100 de crédito para utilizar na sua próxima viagem | Valor isolado: box amarelo VOCÊ GANHA com contador R$ 0 → R$ 100 e "em crédito para sua próxima viagem", sobre foto de destino (peça 1). |
| S4a | 19 367 | 21 583 | 2 217 | **A** câmera | e quem você indicar também ganha [é] | Frase de impacto, contato visual. |
| S4b | 21 583 | 25 000 | 3 417 | **B** dividido | R$ 50 de benefício na contratação da viagem. | Valor isolado: box SEU INDICADO GANHA R$ 50 aplicado como desconto num cartão de contratação. |
| S5a | 25 000 | 27 783 | 2 783 | **A** câmera | e tem mais, o seu crédito é acumulativo. | Frase de impacto (legenda em destaque: ACUMULATIVO). |
| S5b | 27 783 | 32 250 | 4 467 | **C** visual | Então, quanto mais pessoas você indicar para viajar com a gente, mais você vai ganhar. | Tabela de acúmulo 1/3/5 indicações sincronizada com moedas empilhando e contador R$ 100 → R$ 300 → R$ 500. |
| S6a | 32 250 | 34 617 | 2 367 | **B** dividido | Já pensou em alguém que tá querendo viajar? | Frase de curiosidade, como na peça "JÁ TEM ALGUÉM EM MENTE? 👀", com selo, logotipo e foto do lago (peça 3). |
| S6b | 34 617 | 38 300 | 3 683 | **A** câmera | Então mande o nome pra gente e faça sua primeira indicação. | Encerramento/CTA: botão INDIQUE AGORA → com impacto, toque e pulsação. |

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
