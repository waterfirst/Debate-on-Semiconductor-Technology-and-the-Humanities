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
const root = path.resolve(import.meta.dirname, "..");
const cover = path.join(root, "book", "cover");

const assets = [
  ["front-cover-layout-final.svg", "front-cover-final.png", 1748, 2480],
  ["back-cover-layout-final.svg", "back-cover-final.png", 1748, 2480],
  ["full-wrap-layout-final.svg", "full-wrap-cover-final.png", 5717, 2551],
];

for (const [source, output, width, height] of assets) {
  await sharp(path.join(cover, source), { density: 300 })
    .resize(width, height, { fit: "fill" })
    .png()
    .toFile(path.join(cover, output));
  console.log(`rendered ${output}: ${width}x${height}`);
}
