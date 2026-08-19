import { createRequire } from "node:module";
import path from "node:path";

const require = createRequire(import.meta.url);
let sharp;
try {
  sharp = require("sharp");
} catch {
  const bundledModules = path.join(
    process.env.USERPROFILE,
    ".cache",
    "codex-runtimes",
    "codex-primary-runtime",
    "dependencies",
    "node",
    "node_modules",
  );
  sharp = createRequire(path.join(bundledModules, "sharp", "package.json"))("sharp");
}
const figures = path.resolve(import.meta.dirname, "..", "book", "figures");
const requested = new Set(
  process.argv.slice(2).map((value) => Number.parseInt(value, 10)).filter(Number.isFinite),
);

for (let index = 1; index <= 30; index += 1) {
  if (requested.size > 0 && !requested.has(index)) continue;
  const week = String(index).padStart(2, "0");
  const source = path.join(figures, `week${week}.svg`);
  const output = path.join(figures, `week${week}.png`);
  await sharp(source, { density: 192 })
    .resize(1840, 880, { fit: "fill" })
    .png()
    .toFile(output);
  console.log(`rendered week${week}.png: 1840x880`);
}
