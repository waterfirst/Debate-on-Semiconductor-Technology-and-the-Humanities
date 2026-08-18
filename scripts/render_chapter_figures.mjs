import { createRequire } from "node:module";
import path from "node:path";

const require = createRequire(import.meta.url);
const sharp = require("sharp");
const figures = path.resolve(import.meta.dirname, "..", "book", "figures");

for (let index = 1; index <= 30; index += 1) {
  const week = String(index).padStart(2, "0");
  const source = path.join(figures, `week${week}.svg`);
  const output = path.join(figures, `week${week}.png`);
  await sharp(source, { density: 192 })
    .resize(1840, 880, { fit: "fill" })
    .png()
    .toFile(output);
  console.log(`rendered week${week}.png: 1840x880`);
}
