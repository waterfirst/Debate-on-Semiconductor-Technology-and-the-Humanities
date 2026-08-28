import { createRequire } from "node:module";
import { existsSync, readdirSync } from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
let sharp;
try {
  sharp = require("sharp");
} catch {
  const userHome = process.env.USERPROFILE ?? process.env.HOME;
  if (!userHome) {
    throw new Error("USERPROFILE or HOME is required to locate Sharp.");
  }
  const candidates = [
    process.env.SHARP_NODE_MODULES,
    path.join(userHome, ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "node", "node_modules"),
  ].filter(Boolean);
  const modules = candidates.find((candidate) => existsSync(path.join(candidate, "sharp", "package.json")));
  if (!modules) {
    throw new Error("Sharp was not found. Set SHARP_NODE_MODULES to a node_modules directory containing Sharp.");
  }
  sharp = createRequire(path.join(modules, "sharp", "package.json"))("sharp");
}

const root = path.resolve(import.meta.dirname, "..");
const locales = ["en", "ja"];

for (const locale of locales) {
  const translation = path.join(root, "translations", locale);
  const coverSource = path.join(translation, "cover", `front-cover-${locale}.svg`);
  const coverOutput = path.join(translation, "cover", `front-cover-${locale}.png`);
  await sharp(coverSource, { density: 300 })
    .resize(1748, 2480, { fit: "fill" })
    .png({ compressionLevel: 9 })
    .toFile(coverOutput);
  console.log(`rendered ${path.relative(root, coverOutput)}: 1748x2480`);

  const figures = path.join(translation, "figures");
  const sources = readdirSync(figures)
    .filter((name) => /^week\d{2}\.svg$/.test(name))
    .sort();
  for (const name of sources) {
    const source = path.join(figures, name);
    const output = path.join(figures, name.replace(/\.svg$/, "-print.png"));
    await sharp(source, { density: 300 })
      .resize({ width: 1840, withoutEnlargement: false })
      .png({ compressionLevel: 9 })
      .toFile(output);
    const metadata = await sharp(output).metadata();
    console.log(`rendered ${path.relative(root, output)}: ${metadata.width}x${metadata.height}`);
  }
}
