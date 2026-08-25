import { createRequire } from "node:module";
import { existsSync } from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
let sharp;
try {
  sharp = require("sharp");
} catch {
  const home = process.env.USERPROFILE ?? process.env.HOME;
  if (!home) {
    throw new Error("USERPROFILE 또는 HOME 환경변수가 필요합니다.");
  }
  const candidates = [
    process.env.SHARP_NODE_MODULES,
    path.join(home, ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "node", "node_modules"),
    path.join(home, "apps", "hermes3d-scholarbridge", "node_modules"),
    path.join(home, ".npm-global", "lib", "node_modules", "openclaw", "node_modules"),
  ].filter(Boolean);
  const bundledModules = candidates.find((candidate) =>
    existsSync(path.join(candidate, "sharp", "package.json")),
  );
  if (!bundledModules) {
    throw new Error("Sharp를 찾지 못했습니다. SHARP_NODE_MODULES를 지정하십시오.");
  }
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
