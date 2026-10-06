// Renderiza a trilha (audio/score.js) com OfflineAudioContext no Chrome headless
// usado pelo HyperFrames e grava:
//   assets/score.wav       PCM 24 bits, 48 kHz, estéreo, pico normalizado
//   assets/score-wave.js   envelope da trilha, usado para desenhar a onda real
//
// Uso: node scripts/render-audio.mjs   (ou npm run audio)
import { execFileSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import puppeteer from "puppeteer-core";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const TARGET_PEAK_DB = -1.5;
const WAVE_BINS_PER_SECOND = 400;

function chromePath() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const out = execFileSync("npx", ["hyperframes", "browser", "path"], { cwd: root, encoding: "utf8" });
  const line = out
    .split("\n")
    .map((l) => l.trim())
    .find((l) => l.startsWith("/") || /^[A-Z]:\\/.test(l));
  if (!line) throw new Error("Chrome não encontrado; rode `npx hyperframes browser ensure`.");
  return line;
}

const browser = await puppeteer.launch({
  executablePath: chromePath(),
  headless: true,
  args: ["--allow-file-access-from-files", "--no-sandbox", "--autoplay-policy=no-user-gesture-required"],
});
let result;
try {
  const page = await browser.newPage();
  page.on("console", (m) => console.log("[page]", m.text()));
  page.on("pageerror", (e) => {
    throw e;
  });
  await page.goto(pathToFileURL(resolve(root, "audio/render.html")).href, { waitUntil: "load" });
  const t0 = Date.now();
  result = await page.evaluate(() => window.renderScore());
  console.log(`OfflineAudioContext: ${((Date.now() - t0) / 1000).toFixed(1)} s`);
} finally {
  await browser.close();
}

const { sampleRate, length } = result;
const ch = result.channels.map((b64) => {
  const buf = Buffer.from(b64, "base64");
  return new Float32Array(buf.buffer, buf.byteOffset, buf.byteLength / 4);
});

// Masterização mínima: um limitador de pico transparente (lookahead de 5 ms,
// liberação suave de 180 ms), limitado a MAX_GR_DB de redução, só nos picos
// mais altos. Depois, ganho linear único até o teto de TARGET_PEAK_DB.
const MAX_GR_DB = 3;
const link = new Float32Array(length);
for (let i = 0; i < length; i++) link[i] = Math.max(Math.abs(ch[0][i]), Math.abs(ch[1][i]));
let peak = 0;
for (let i = 0; i < length; i++) peak = Math.max(peak, link[i]);
const ceiling = peak * Math.pow(10, -MAX_GR_DB / 20);
const look = Math.round(0.005 * sampleRate);
const relCoef = Math.exp(-1 / (0.18 * sampleRate));
// ganho mínimo exigido em cada amostra, olhando 'look' amostras adiante
const need = new Float32Array(length).fill(1);
for (let i = 0; i < length; i++) if (link[i] > ceiling) need[i] = ceiling / link[i];
const gr = new Float32Array(length);
let g = 1;
// janela deslizante de mínimo (ingênua, mas só nas regiões com redução)
for (let i = 0; i < length; i++) {
  let target = 1;
  for (let k = i; k < Math.min(length, i + look); k++) if (need[k] < target) target = need[k];
  if (target < g) {
    // ataque: rampa linear até o alvo antes do pico chegar
    g = g - (g - target) / Math.max(1, look / 4);
    if (g < target) g = target;
  } else {
    g = target + (g - target) * relCoef;
  }
  gr[i] = g;
}
let grMax = 0;
let grSamples = 0;
for (let i = 0; i < length; i++) {
  const db = -20 * Math.log10(gr[i]);
  grMax = Math.max(grMax, db);
  if (db > 0.5) grSamples++;
  ch[0][i] *= gr[i];
  ch[1][i] *= gr[i];
}
let peak2 = 0;
for (const c of ch) for (let i = 0; i < c.length; i++) peak2 = Math.max(peak2, Math.abs(c[i]));
const gain = Math.pow(10, TARGET_PEAK_DB / 20) / peak2;
console.log(
  `pico bruto ${(20 * Math.log10(peak)).toFixed(2)} dBFS · limitador: máx ${grMax.toFixed(2)} dB, ` +
    `>0,5 dB em ${((grSamples / sampleRate) * 1000).toFixed(0)} ms · ganho final ${(20 * Math.log10(gain)).toFixed(2)} dB`
);

// WAV PCM 24 bits
const nCh = ch.length;
const dataBytes = length * nCh * 3;
const wav = Buffer.alloc(44 + dataBytes);
wav.write("RIFF", 0);
wav.writeUInt32LE(36 + dataBytes, 4);
wav.write("WAVE", 8);
wav.write("fmt ", 12);
wav.writeUInt32LE(16, 16);
wav.writeUInt16LE(1, 20);
wav.writeUInt16LE(nCh, 22);
wav.writeUInt32LE(sampleRate, 24);
wav.writeUInt32LE(sampleRate * nCh * 3, 28);
wav.writeUInt16LE(nCh * 3, 32);
wav.writeUInt16LE(24, 34);
wav.write("data", 36);
wav.writeUInt32LE(dataBytes, 40);
let o = 44;
for (let i = 0; i < length; i++) {
  for (let c = 0; c < nCh; c++) {
    const v = Math.max(-1, Math.min(1, ch[c][i] * gain));
    wav.writeIntLE(Math.round(v * 8388607), o, 3);
    o += 3;
  }
}
mkdirSync(resolve(root, "assets"), { recursive: true });
writeFileSync(resolve(root, "assets/score.wav"), wav);

// Envelope (pico e RMS por janela) da mixagem mono, para a onda na tela.
const per = sampleRate / WAVE_BINS_PER_SECOND;
const bins = Math.floor(length / per);
const pk = new Float32Array(bins);
const rms = new Float32Array(bins);
for (let b = 0; b < bins; b++) {
  let m = 0;
  let s = 0;
  const a = Math.floor(b * per);
  const z = Math.floor((b + 1) * per);
  for (let i = a; i < z; i++) {
    const v = ((ch[0][i] + ch[1][i]) / 2) * gain;
    m = Math.max(m, Math.abs(v));
    s += v * v;
  }
  pk[b] = m;
  rms[b] = Math.sqrt(s / (z - a));
}
const q = (arr) => Array.from(arr, (v) => Math.round(Math.min(1, v) * 1000)).join(",");
writeFileSync(
  resolve(root, "assets/score-wave.js"),
  `/* Gerado por scripts/render-audio.mjs a partir de assets/score.wav. Não editar. */\n` +
    `window.SCORE_WAVE={binsPerSecond:${WAVE_BINS_PER_SECOND},scale:1000,` +
    `peak:[${q(pk)}],rms:[${q(rms)}]};\n`
);
console.log(`assets/score.wav (${(wav.length / 1e6).toFixed(1)} MB, ${(length / sampleRate).toFixed(3)} s) e assets/score-wave.js gravados`);
