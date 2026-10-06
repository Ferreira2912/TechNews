// Extrai as linhas de index.html marcadas com "// ◆" e grava assets/code-lines.js.
// O painel de código do trailer exibe essas linhas: são trechos reais do
// próprio filme, copiados do arquivo-fonte (o compilador do HyperFrames
// reformata scripts e remove comentários, por isso a extração é feita antes).
//
// Uso: node scripts/extract-code.mjs   (ou npm run code)
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const MARK = "// ◆";
const lines = readFileSync(resolve(root, "index.html"), "utf8")
  .split("\n")
  .filter((l) => l.includes(MARK))
  .map((l) => l.replace(MARK, "").replace(/\s+$/, ""));
const indent = Math.min(...lines.map((l) => l.match(/^ */)[0].length));
const out = lines.map((l) => l.slice(indent));
writeFileSync(
  resolve(root, "assets/code-lines.js"),
  "/* Gerado por scripts/extract-code.mjs a partir de index.html. Não editar. */\n" +
    "window.CODE_LINES = " +
    JSON.stringify(out, null, 2) +
    ";\n"
);
console.log(`${out.length} linhas reais de index.html → assets/code-lines.js`);
out.forEach((l) => console.log("  " + l));
