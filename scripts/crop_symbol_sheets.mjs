import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";

const require = createRequire(import.meta.url);
const sharp = require("sharp");

const root = path.resolve(import.meta.dirname, "..");
const symbols = path.join(root, "book", "figures", "symbols");
const sheets = path.join(symbols, "source-sheets");
fs.mkdirSync(symbols, { recursive: true });

for (let sheetIndex = 0; sheetIndex < 5; sheetIndex += 1) {
  const source = path.join(sheets, `sheet-${sheetIndex + 1}.png`);
  const metadata = await sharp(source).metadata();
  const cellWidth = Math.floor(metadata.width / 3);
  const cellHeight = Math.floor(metadata.height / 2);

  for (let cell = 0; cell < 6; cell += 1) {
    const week = sheetIndex * 6 + cell + 1;
    const column = cell % 3;
    const row = Math.floor(cell / 3);
    const left = column * cellWidth;
    const top = row * cellHeight;
    const width = column === 2 ? metadata.width - left : cellWidth;
    const height = row === 1 ? metadata.height - top : cellHeight;
    const output = path.join(symbols, `week${String(week).padStart(2, "0")}-symbol.png`);

    await sharp(source)
      .extract({ left, top, width, height })
      .resize(720, 720, { fit: "cover" })
      .png()
      .toFile(output);
  }
}

console.log("cropped symbolic illustrations: 30");
