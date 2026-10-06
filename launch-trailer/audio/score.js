/* Trilha sonora do trailer, 100% sintetizada com a Web Audio API.
   Sem samples e sem arquivos externos: osciladores, ruído gerado por PRNG
   com semente, filtros, envelopes, delay e um reverb de convolução cuja
   resposta ao impulso também é calculada aqui.

   buildScore(ctx, T) agenda tudo num OfflineAudioContext.
   T = window.FILM_T (timing.js), as mesmas marcas usadas pela imagem. */
(function (g) {
  function mulberry32(seed) {
    return function () {
      seed |= 0;
      seed = (seed + 0x6d2b79f5) | 0;
      var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function buildScore(ctx, T) {
    var SR = ctx.sampleRate;
    var rng = mulberry32(5505);
    var hz = T.hz;
    var END = T.DURATION;

    // ---------- barramentos ----------
    var bus = ctx.createGain();
    var master = ctx.createGain();
    bus.connect(master);
    master.connect(ctx.destination);
    master.gain.setValueAtTime(1, 0);
    master.gain.setValueAtTime(1, 17.3);
    master.gain.setTargetAtTime(0, 17.3, 0.2);

    // Reverb: resposta ao impulso estéreo calculada (ruído com decaimento e
    // perda de agudos ao longo do tempo).
    function makeIR(seconds, decay) {
      var len = Math.floor(seconds * SR);
      var ir = ctx.createBuffer(2, len, SR);
      for (var c = 0; c < 2; c++) {
        var d = ir.getChannelData(c);
        var r = mulberry32(900 + c * 77);
        var lp = 0;
        for (var i = 0; i < len; i++) {
          var t = i / SR;
          var n = r() * 2 - 1;
          var k = 0.55 - 0.45 * Math.min(1, t / seconds); // escurece com o tempo
          lp += k * (n - lp);
          var pre = t < 0.012 ? t / 0.012 : 1;
          d[i] = lp * Math.exp(-t / decay) * pre;
        }
      }
      return ir;
    }
    var verb = ctx.createConvolver();
    verb.buffer = makeIR(4.2, 0.62);
    var verbReturn = ctx.createGain();
    verbReturn.gain.value = 0.55;
    verb.connect(verbReturn);
    verbReturn.connect(bus);

    // Delay pingue-pongue em colcheia pontuada (0,5625 s) para os sinos.
    var dly = ctx.createGain();
    var dL = ctx.createDelay(2);
    var dR = ctx.createDelay(2);
    dL.delayTime.value = T.BEAT * 0.75;
    dR.delayTime.value = T.BEAT * 0.75;
    var fbL = ctx.createGain();
    var fbR = ctx.createGain();
    fbL.gain.value = 0.34;
    fbR.gain.value = 0.34;
    var dTone = ctx.createBiquadFilter();
    dTone.type = "lowpass";
    dTone.frequency.value = 3200;
    var pL = ctx.createStereoPanner();
    var pR = ctx.createStereoPanner();
    pL.pan.value = -0.7;
    pR.pan.value = 0.7;
    var dlyReturn = ctx.createGain();
    dlyReturn.gain.value = 0.5;
    dly.connect(dTone);
    dTone.connect(dL);
    dL.connect(pL);
    pL.connect(dlyReturn);
    dL.connect(fbL);
    fbL.connect(dR);
    dR.connect(pR);
    pR.connect(dlyReturn);
    dR.connect(fbR);
    fbR.connect(dL);
    dlyReturn.connect(bus);
    dlyReturn.connect(verb);

    // Tudo o que soa antes do clímax passa por "pre", que se cala no vácuo.
    // Dinâmica por seção: o gancho, o corpo (compassos 2–3) e o crescendo
    // do compasso 4, terminando no corte do vácuo.
    function sectionGain(param) {
      param.setValueAtTime(1.4, 0);
      param.setValueAtTime(1.4, T.pullBack - 0.4);
      param.linearRampToValueAtTime(1.6, T.pullBack);
      param.setValueAtTime(1.6, T.tension);
      param.linearRampToValueAtTime(2.6, T.vacuum - 0.012);
      param.linearRampToValueAtTime(0, T.vacuum + 0.02);
    }
    var pre = ctx.createGain();
    pre.connect(bus);
    sectionGain(pre.gain);
    var OUT = pre;

    // O vácuo antes do clímax corta até as caudas de reverb e delay.
    [verbReturn, dlyReturn].forEach(function (gn) {
      var v = gn.gain.value;
      gn.gain.setValueAtTime(v, T.vacuum - 0.01);
      gn.gain.linearRampToValueAtTime(0, T.vacuum + 0.03);
      gn.gain.setValueAtTime(0, T.impact - 0.005);
      gn.gain.linearRampToValueAtTime(v * 1.25, T.impact + 0.01);
    });

    // ---------- utilitários ----------
    var noiseBuf = (function () {
      var len = SR * 6;
      var b = ctx.createBuffer(2, len, SR);
      for (var c = 0; c < 2; c++) {
        var d = b.getChannelData(c);
        for (var i = 0; i < len; i++) d[i] = rng() * 2 - 1;
      }
      return b;
    })();

    function noise(t, dur) {
      var s = ctx.createBufferSource();
      s.buffer = noiseBuf;
      var off = rng() * (noiseBuf.duration - dur - 0.1);
      s.start(t, Math.max(0, off), dur + 0.05);
      return s;
    }
    function filt(type, f, q) {
      var x = ctx.createBiquadFilter();
      x.type = type;
      x.frequency.value = f;
      if (q != null) x.Q.value = q;
      return x;
    }
    function gainNode(v) {
      var x = ctx.createGain();
      x.gain.value = v == null ? 1 : v;
      return x;
    }
    function panner(p) {
      var x = ctx.createStereoPanner();
      x.pan.value = p || 0;
      return x;
    }
    function chain() {
      for (var i = 0; i < arguments.length - 1; i++) arguments[i].connect(arguments[i + 1]);
      return arguments[arguments.length - 1];
    }
    // Envios pré-clímax passam por portões que também se fecham no vácuo.
    function gate(dest) {
      var gt = gainNode(1);
      sectionGain(gt.gain);
      gt.connect(dest);
      return gt;
    }
    var preVerb = gate(verb);
    var preDly = gate(dly);
    function send(node, amtVerb, amtDly) {
      var early = OUT === pre;
      if (amtVerb) chain(node, gainNode(amtVerb), early ? preVerb : verb);
      if (amtDly) chain(node, gainNode(amtDly), early ? preDly : dly);
    }
    // Envelope percussivo: ataque linear, queda exponencial.
    function perc(param, t, peak, attack, decay) {
      param.setValueAtTime(0, t);
      param.linearRampToValueAtTime(peak, t + attack);
      param.exponentialRampToValueAtTime(0.0001, t + attack + decay);
      param.setValueAtTime(0, t + attack + decay + 0.001);
    }

    // ---------- instrumentos ----------
    function sub(t, f0, f1, glide, dur, peak) {
      var o = ctx.createOscillator();
      o.type = "sine";
      o.frequency.setValueAtTime(f0, t);
      o.frequency.exponentialRampToValueAtTime(f1, t + glide);
      var a = gainNode(0);
      perc(a.gain, t, peak, 0.004, dur);
      chain(o, a, OUT);
      o.start(t);
      o.stop(t + dur + 0.1);
      // harmônico (oitava acima) para alto-falantes pequenos
      var o2 = ctx.createOscillator();
      o2.type = "sine";
      o2.frequency.setValueAtTime(f0 * 2, t);
      o2.frequency.exponentialRampToValueAtTime(f1 * 2, t + glide);
      var a2 = gainNode(0);
      perc(a2.gain, t, peak * 0.32, 0.004, dur * 0.35);
      chain(o2, a2, OUT);
      o2.start(t);
      o2.stop(t + dur + 0.1);
    }

    function boom(t, peak, cutoff, dur) {
      var n = noise(t, dur + 0.1);
      var f = filt("lowpass", cutoff, 0.7);
      var a = gainNode(0);
      perc(a.gain, t, peak, 0.006, dur);
      chain(n, f, a, OUT);
      send(a, 0.35);
    }

    function click(t, opt) {
      var n = noise(t, 0.08);
      var f = filt("bandpass", opt.freq, opt.q || 1.4);
      var a = gainNode(0);
      perc(a.gain, t, opt.gain, 0.0015, opt.decay || 0.02);
      var p = panner(opt.pan || 0);
      chain(n, f, a, p, OUT);
      if (opt.verb) send(p, opt.verb);
      if (opt.body) {
        var o = ctx.createOscillator();
        o.frequency.setValueAtTime(opt.body, t);
        o.frequency.exponentialRampToValueAtTime(opt.body * 0.6, t + 0.04);
        var ab = gainNode(0);
        perc(ab.gain, t, opt.gain * 0.45, 0.002, 0.035);
        chain(o, ab, p);
        o.start(t);
        o.stop(t + 0.1);
      }
    }

    function whoosh(t, dur, f0, f1, peak, pan0, pan1) {
      var n = noise(t, dur);
      var f = filt("bandpass", f0, 1.1);
      f.frequency.setValueAtTime(f0, t);
      f.frequency.exponentialRampToValueAtTime(f1, t + dur);
      var a = gainNode(0);
      a.gain.setValueAtTime(0, t);
      a.gain.linearRampToValueAtTime(peak, t + dur * 0.62);
      a.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      var p = panner(pan0 || 0);
      p.pan.setValueAtTime(pan0 || 0, t);
      p.pan.linearRampToValueAtTime(pan1 || 0, t + dur);
      chain(n, f, a, p, OUT);
      send(p, 0.3);
    }

    // "Prato invertido": cresce exponencialmente e corta seco em tEnd.
    function reverseSwell(tEnd, dur, peak, tonal) {
      var t = tEnd - dur;
      var n = noise(t, dur);
      var hp = filt("highpass", 300, 0.7);
      hp.frequency.setValueAtTime(300, t);
      hp.frequency.exponentialRampToValueAtTime(1800, tEnd);
      var lp = filt("lowpass", 2000, 0.7);
      lp.frequency.setValueAtTime(2000, t);
      lp.frequency.exponentialRampToValueAtTime(14000, tEnd);
      var a = gainNode(0);
      a.gain.setValueAtTime(0.0001, t);
      a.gain.exponentialRampToValueAtTime(peak, tEnd - 0.012);
      a.gain.linearRampToValueAtTime(0, tEnd);
      chain(n, hp, lp, a, OUT);
      if (tonal) {
        tonal.forEach(function (m) {
          var o = ctx.createOscillator();
          o.type = "triangle";
          o.frequency.value = hz(m);
          var ao = gainNode(0);
          ao.gain.setValueAtTime(0.0001, t);
          ao.gain.exponentialRampToValueAtTime(peak * 0.35, tEnd - 0.012);
          ao.gain.linearRampToValueAtTime(0, tEnd);
          chain(o, ao, OUT);
          o.start(t);
          o.stop(tEnd + 0.02);
        });
      }
    }

    // Sino FM suave (portadora + moduladora harmônica com índice decaindo).
    function bell(t, freq, ring, peak, pan, verbAmt, dlyAmt) {
      var car = ctx.createOscillator();
      car.frequency.value = freq;
      var mod = ctx.createOscillator();
      mod.frequency.value = freq * 2;
      var idx = gainNode(0);
      idx.gain.setValueAtTime(freq * 2.0, t);
      idx.gain.exponentialRampToValueAtTime(freq * 0.12, t + 0.9);
      chain(mod, idx, car.frequency);
      var a = gainNode(0);
      perc(a.gain, t, peak, 0.003, ring);
      var p = panner(pan || 0);
      chain(car, a, p, OUT);
      // brilho: parciais 3x e 4.01x com queda rápida
      [
        [3, 0.16, 0.5],
        [4.01, 0.07, 0.3],
      ].forEach(function (h) {
        var o = ctx.createOscillator();
        o.frequency.value = freq * h[0];
        var ah = gainNode(0);
        perc(ah.gain, t, peak * h[1], 0.002, h[2]);
        chain(o, ah, p);
        o.start(t);
        o.stop(t + h[2] + 0.1);
      });
      send(p, verbAmt == null ? 0.45 : verbAmt, dlyAmt == null ? 0.3 : dlyAmt);
      car.start(t);
      mod.start(t);
      car.stop(t + ring + 0.1);
      mod.stop(t + ring + 0.1);
    }

    // Voz de cordas/metais: serras desafinadas num passa-baixa.
    function lead(t, freq, dur, peak, cutoff) {
      var f = filt("lowpass", cutoff, 0.9);
      var a = gainNode(0);
      a.gain.setValueAtTime(0, t);
      a.gain.linearRampToValueAtTime(peak, t + 0.09);
      a.gain.setValueAtTime(peak, t + dur);
      a.gain.exponentialRampToValueAtTime(0.0001, t + dur + 0.9);
      [-7, 7].forEach(function (cents, i) {
        var o = ctx.createOscillator();
        o.type = "sawtooth";
        o.frequency.value = freq;
        o.detune.value = cents;
        var p = panner(i ? 0.25 : -0.25);
        chain(o, p, f);
        o.start(t);
        o.stop(t + dur + 1.0);
      });
      chain(f, a, OUT);
      send(a, 0.5);
    }

    function bass(t, midi, dur, peak) {
      var f = filt("lowpass", 1200, 5);
      f.frequency.setValueAtTime(1300, t);
      f.frequency.exponentialRampToValueAtTime(150, t + 0.2);
      var a = gainNode(0);
      a.gain.setValueAtTime(0, t);
      a.gain.linearRampToValueAtTime(peak, t + 0.006);
      a.gain.exponentialRampToValueAtTime(peak * 0.3, t + dur * 0.55);
      a.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      var o = ctx.createOscillator();
      o.type = "sawtooth";
      o.frequency.value = hz(midi);
      var s = ctx.createOscillator();
      s.type = "sine";
      s.frequency.value = hz(midi - 12);
      var sg = gainNode(0.9);
      chain(o, f, a, OUT);
      chain(s, sg, a);
      o.start(t);
      s.start(t);
      o.stop(t + dur + 0.05);
      s.stop(t + dur + 0.05);
    }

    // Pad de acordes: 3 serras desafinadas por nota, filtro comum.
    function pad(t0, t1, midis, peak, attack, release, cutPts, trem) {
      var f = filt("lowpass", cutPts[0][1], 0.6);
      cutPts.forEach(function (c, i) {
        if (i === 0) f.frequency.setValueAtTime(c[1], c[0]);
        else f.frequency.exponentialRampToValueAtTime(c[1], c[0]);
      });
      var a = gainNode(0);
      a.gain.setValueAtTime(0, t0);
      a.gain.linearRampToValueAtTime(peak, t0 + attack);
      a.gain.setValueAtTime(peak, t1);
      if (release > 0.02) a.gain.exponentialRampToValueAtTime(0.0001, t1 + release);
      else a.gain.linearRampToValueAtTime(0, t1 + release);
      var out = a;
      if (trem) {
        // tremolo cuja velocidade acelera (tensão)
        var tg = gainNode(1 - trem.depth / 2);
        var lfo = ctx.createOscillator();
        lfo.frequency.setValueAtTime(trem.from, t0);
        lfo.frequency.exponentialRampToValueAtTime(trem.to, t1);
        var lg = gainNode(trem.depth / 2);
        chain(lfo, lg, tg.gain);
        lfo.start(t0);
        lfo.stop(t1 + release + 0.1);
        chain(a, tg);
        out = tg;
      }
      midis.forEach(function (m, i) {
        [-9, 0, 9].forEach(function (cents) {
          var o = ctx.createOscillator();
          o.type = "sawtooth";
          o.frequency.value = hz(m);
          o.detune.value = cents + (rng() - 0.5) * 3;
          var pv = panner(((i % 2 ? 1 : -1) * (0.15 + 0.5 * (i / midis.length))) + cents / 60);
          var vg = gainNode(1 / Math.sqrt(midis.length * 3));
          chain(o, vg, pv, f);
          o.start(t0);
          o.stop(t1 + release + 0.05);
        });
      });
      chain(f, a);
      out.connect(OUT);
      send(out, 0.6);
    }

    // ================= a partitura =================

    // Compasso 1 — ar e drone
    (function () {
      var n = noise(0, 12.2);
      var lp = filt("lowpass", 700, 0.5);
      var hp = filt("highpass", 90, 0.5);
      var a = gainNode(0);
      a.gain.setValueAtTime(0, 0);
      a.gain.linearRampToValueAtTime(0.03, 0.4);
      a.gain.linearRampToValueAtTime(0.022, 3);
      a.gain.linearRampToValueAtTime(0.04, 11.6);
      a.gain.linearRampToValueAtTime(0, T.vacuum);
      chain(n, lp, hp, a, OUT);
    })();
    [38, 45].forEach(function (m, i) {
      var o = ctx.createOscillator();
      o.type = i ? "triangle" : "sine";
      o.frequency.value = hz(m);
      var a = gainNode(0);
      a.gain.setValueAtTime(0, T.dotLand);
      a.gain.linearRampToValueAtTime(i ? 0.035 : 0.09, 1.6);
      a.gain.setValueAtTime(i ? 0.035 : 0.09, 3.2);
      a.gain.linearRampToValueAtTime(0, 4.6);
      chain(o, a, OUT);
      o.start(T.dotLand);
      o.stop(4.7);
    });

    // A queda do ponto: sopro subindo, depois o primeiro impacto
    whoosh(0.0, T.dotLand + 0.02, 500, 7000, 0.16, 0, 0);
    // o ponto dispara para a esquerda e vira cursor
    whoosh(T.whip - 0.02, 0.24, 1500, 5200, 0.09, 0.1, -0.55);
    sub(T.dotLand, 75, 38, 0.28, 2.0, 0.4);
    click(T.dotLand, { freq: 4200, q: 0.9, gain: 0.32, decay: 0.05, verb: 0.5, body: 220 });
    boom(T.dotLand, 0.16, 220, 0.6);

    // Digitação: um clique por letra
    T.TYPE.forEach(function (c) {
      click(c.t, {
        freq: 2600 + rng() * 2400,
        q: 1.6,
        gain: c.first ? 0.16 : 0.1,
        decay: 0.016,
        pan: (rng() - 0.5) * 0.35,
        body: 160 + rng() * 60,
        verb: 0.12,
      });
    });
    // O cursor vira ponto final: o ponto soa
    bell(T.period, hz(74), 2.6, 0.2, 0, 0.55, 0.35);

    // Para o compasso 2
    reverseSwell(T.pullBack, 0.75, 0.11, [50, 57]);
    whoosh(T.pullBack - 0.05, 1.05, 5200, 280, 0.13, -0.35, 0.35);

    // Impactos estruturais
    sub(T.pullBack, 82, 36, 0.32, 2.4, 0.27);
    boom(T.pullBack, 0.14, 180, 1.0);
    sub(T.line, 82, 36, 0.3, 2.2, 0.25);
    boom(T.line, 0.12, 200, 0.9);
    sub(T.tension, 86, 36, 0.3, 2.0, 0.26);
    boom(T.tension, 0.13, 200, 0.9);

    // Baixo pulsante em colcheias (Ré, Si♭, Dó) e semicolcheias na tensão
    var roots = [
      [T.pullBack, T.line, 38],
      [T.line, T.tension, 34],
      [T.tension, T.h4Out, 36],
    ];
    roots.forEach(function (r, ri) {
      var step = ri === 2 ? T.BEAT / 4 : T.BEAT / 2;
      for (var t = r[0]; t < r[1] - 0.001; t += step) {
        var beatPos = Math.round((t - r[0]) / step);
        var accent = beatPos % (ri === 2 ? 4 : 2) === 0;
        var lvl = ri === 2 ? 0.12 + 0.06 * ((t - r[0]) / (r[1] - r[0])) : 0.2;
        bass(t, r[2], step * 0.92, accent ? lvl * 1.15 : lvl * 0.8);
      }
    });

    // Tique de relógio
    (function () {
      var k = 0;
      for (var t = T.pullBack; t < T.h4Out - 0.001; t += T.tension <= t + 1e-6 ? T.BEAT / 4 : T.BEAT / 2) {
        var inTension = t >= T.tension - 1e-6;
        var prog = inTension ? (t - T.tension) / (T.h4Out - T.tension) : 0;
        click(t, {
          freq: 7600,
          q: 0.8,
          gain: (inTension ? 0.045 + 0.06 * prog : 0.045) * (k % 2 ? 0.7 : 1),
          decay: 0.022,
          pan: k % 2 ? 0.28 : -0.28,
        });
        k++;
      }
    })();

    // Pads: Rém → Si♭ → Dó (tremolo acelerando) → corte no vácuo
    pad(T.pullBack, T.line, [50, 53, 57, 62], 0.1, 0.5, 0.35, [
      [T.pullBack, 420],
      [T.line, 900],
    ]);
    pad(T.line - 0.05, T.tension, [46, 50, 53, 58, 62], 0.11, 0.25, 0.35, [
      [T.line, 800],
      [T.tension, 1500],
    ]);
    pad(
      T.tension - 0.05,
      T.vacuum - 0.02,
      [48, 52, 55, 60, 64, 67],
      0.13,
      0.2,
      0.02,
      [
        [T.tension, 1300],
        [T.vacuum, 4200],
      ],
      { from: 3, to: 15, depth: 0.55 }
    );

    // Motivo nos sinos (e, na revelação, dobrado por cordas uma oitava abaixo)
    T.MOTIF.forEach(function (n, i) {
      var reveal = n.t >= T.impact;
      var tense = n.t >= T.tension && !reveal;
      var ring = reveal ? n.d + 2.4 : Math.min(n.d + 1.3, tense && n.m === 79 ? 0.58 : 9);
      bell(n.t, hz(n.m), ring, reveal ? 0.26 : tense ? 0.11 : 0.15, (i % 2 ? 0.18 : -0.18), 0.45, reveal ? 0.22 : 0.3);
      if (reveal) lead(n.t, hz(n.m - 12), n.d * 0.95, 0.1, 2400);
    });

    // Tensão: riser de ruído em banda e um tom subindo
    (function () {
      var t0 = T.tension;
      var t1 = T.vacuum;
      var n = noise(t0, t1 - t0);
      var f = filt("bandpass", 200, 3);
      f.frequency.setValueAtTime(200, t0);
      f.frequency.exponentialRampToValueAtTime(9000, t1);
      var a = gainNode(0);
      a.gain.setValueAtTime(0.0001, t0);
      a.gain.exponentialRampToValueAtTime(0.26, t1 - 0.01);
      a.gain.linearRampToValueAtTime(0, t1);
      chain(n, f, a, OUT);
      send(a, 0.25);
      var o = ctx.createOscillator();
      o.type = "triangle";
      o.frequency.setValueAtTime(hz(50), t0);
      o.frequency.exponentialRampToValueAtTime(hz(62), t1);
      var lp = filt("lowpass", 1800, 0.7);
      var ao = gainNode(0);
      ao.gain.setValueAtTime(0.0001, t0);
      ao.gain.exponentialRampToValueAtTime(0.06, t1 - 0.01);
      ao.gain.linearRampToValueAtTime(0, t1);
      chain(o, lp, ao, OUT);
      o.start(t0);
      o.stop(t1 + 0.02);
    })();

    // Transições
    whoosh(T.h2Out - 0.05, 0.45, 500, 5200, 0.14, 0.3, -0.3);
    reverseSwell(T.line, 0.55, 0.15, [46, 53]);
    whoosh(T.h3Out - 0.05, 0.45, 450, 6000, 0.14, -0.3, 0.3);
    reverseSwell(T.vacuum, 0.62, 0.22, [50, 57, 62]);

    // ======== CLÍMAX (12,0 s) ========
    OUT = bus;
    var I = T.impact;
    sub(I, 118, 30, 1.5, 5.2, 0.72);
    sub(I, 62, 44, 0.6, 1.4, 0.3);
    boom(I, 0.4, 170, 1.4);
    // estalo + ar brilhante
    (function () {
      var n = noise(I, 0.4);
      var f = filt("lowpass", 7500, 0.6);
      var a = gainNode(0);
      perc(a.gain, I, 0.75, 0.002, 0.24);
      chain(n, f, a, OUT);
      send(a, 0.6);
      var n2 = noise(I, 3.4);
      var f2 = filt("highpass", 3200, 0.6);
      var a2 = gainNode(0);
      perc(a2.gain, I, 0.12, 0.01, 3.2);
      var p2 = panner(0);
      chain(n2, f2, a2, p2, OUT);
      send(a2, 0.8);
    })();
    // Acorde de Ré maior abrindo o filtro, cauda longa
    pad(I, 16.6, [38, 45, 50, 54, 57, 62, 64, 66, 69], 0.3, 0.03, 1.35, [
      [I, 260],
      [I + 0.28, 4200],
      [15.0, 2300],
      [17.8, 900],
    ]);
    // Golpe de metais sintéticos: o acorde ataca forte e assenta.
    [50, 54, 57, 62, 66].forEach(function (m, i) {
      var f = filt("lowpass", 300, 1.2);
      f.frequency.setValueAtTime(300, I);
      f.frequency.exponentialRampToValueAtTime(3800, I + 0.06);
      f.frequency.exponentialRampToValueAtTime(1100, I + 1.8);
      var a = gainNode(0);
      perc(a.gain, I, 0.17, 0.012, 2.6);
      [-6, 6].forEach(function (c) {
        var o = ctx.createOscillator();
        o.type = "sawtooth";
        o.frequency.value = hz(m);
        o.detune.value = c;
        chain(o, f);
        o.start(I);
        o.stop(I + 2.8);
      });
      var p = panner((i - 2) * 0.22);
      chain(f, a, p, OUT);
      send(p, 0.6);
    });
    // corpo grave sustentado
    (function () {
      var o = ctx.createOscillator();
      o.type = "sine";
      o.frequency.value = hz(26);
      var a = gainNode(0);
      a.gain.setValueAtTime(0, I);
      a.gain.linearRampToValueAtTime(0.1, I + 0.05);
      a.gain.exponentialRampToValueAtTime(0.0001, I + 5.8);
      chain(o, a, OUT);
      o.start(I);
      o.stop(I + 6);
    })();

    // Cartela final
    whoosh(T.endCard - 0.1, 0.85, 3200, 520, 0.07, 0.2, -0.2);
    bell(T.endSettle, hz(81), 2.9, 0.1, 0.25, 0.6, 0.25);
    bell(T.endSettle, hz(50), 2.9, 0.16, -0.1, 0.4, 0.1);
    sub(T.endSettle, 60, 37, 0.4, 2.6, 0.28);

    return { end: END };
  }

  g.buildScore = buildScore;
})(typeof window !== "undefined" ? window : globalThis);
