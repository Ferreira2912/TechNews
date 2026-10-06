/* Marcas de tempo compartilhadas pela imagem (index.html) e pelo som (audio/score.js).
   80 BPM em 4/4: 1 tempo = 0,75 s = 45 quadros a 60 fps; 1 compasso = 3 s. */
(function (g) {
  var BPM = 80;
  var BEAT = 60 / BPM;
  var b = function (n) {
    return n * BEAT;
  };

  var T = {
    BPM: BPM,
    BEAT: BEAT,
    BAR: BEAT * 4,
    DURATION: 18,
    FPS: 60,
    W: 2560,
    H: 1440,
    SAMPLE_RATE: 48000,

    // Compasso 1: o gancho
    dotLand: b(0.5), // 0.375
    whip: 0.56, // o ponto dispara até o início da frase
    typeStart: b(1), // 0.75
    period: b(3), // 2.25 — o cursor vira ponto final
    swell2: b(3.5),
    // Compasso 2: código
    pullBack: b(4), // 3.00
    focus: 3.7, // foco sai do código
    h2In: 3.9,
    h2Out: 5.66,
    collapse: 5.68,
    // Compasso 3: som
    line: b(8), // 6.00
    h3In: b(9), // 6.75
    h3Out: 8.6,
    // Compasso 4: tensão
    tension: b(12), // 9.00
    h4In: b(12),
    h4Out: b(15), // 11.25
    vacuum: 11.85,
    // Compasso 5: clímax
    impact: b(16), // 12.00
    // Compasso 6: cartela final
    endCard: b(19), // 14.25
    endSettle: b(20), // 15.00
  };

  // Digitação: cada palavra começa numa colcheia, letras a cada 45 ms.
  var WORDS = ["Nada", "aqui", "foi", "filmado"];
  var CHAR_GAP = 0.045;
  var chars = [];
  WORDS.forEach(function (w, wi) {
    var t0 = T.typeStart + wi * (BEAT / 2);
    for (var i = 0; i < w.length; i++) {
      chars.push({ ch: w[i], t: t0 + i * CHAR_GAP, word: wi, first: i === 0 });
    }
  });
  T.WORDS = WORDS;
  T.TYPE = chars;

  // Motivo melódico (Hz): Lá–Ré–Mi–Fá, que resolve em Fá♯ na revelação.
  var hz = function (midi) {
    return 440 * Math.pow(2, (midi - 69) / 12);
  };
  T.hz = hz;
  T.MOTIF = [
    // compasso 2 (Rém)
    { t: b(5), m: 69, d: 0.75 },
    { t: b(6), m: 74, d: 0.375 },
    { t: b(6.5), m: 76, d: 0.375 },
    { t: b(7), m: 77, d: 1.4 },
    // compasso 3 (Si♭)
    { t: b(9), m: 69, d: 0.75 },
    { t: b(10), m: 74, d: 0.375 },
    { t: b(10.5), m: 76, d: 0.375 },
    { t: b(11), m: 77, d: 1.4 },
    // compasso 4 (Dó) — sobe para o Sol (sus4)
    { t: b(13), m: 69, d: 0.75 },
    { t: b(14), m: 74, d: 0.375 },
    { t: b(14.5), m: 76, d: 0.375 },
    { t: b(15), m: 79, d: 0.55 },
    // compasso 5 (Ré maior) — resolução
    { t: b(17), m: 69, d: 0.75 },
    { t: b(18), m: 74, d: 0.375 },
    { t: b(18.5), m: 76, d: 0.375 },
    { t: b(19), m: 78, d: 3.2 },
  ];

  g.FILM_T = T;
})(typeof window !== "undefined" ? window : globalThis);
