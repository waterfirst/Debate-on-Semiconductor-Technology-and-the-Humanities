import fs from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const chapters = path.join(root, "book", "chapters");
let changed = 0;

for (const filename of fs.readdirSync(chapters).filter((name) => /^week\d\d\.qmd$/.test(name))) {
  const file = path.join(chapters, filename);
  const source = fs.readFileSync(file, "utf8");
  let updated = source
    .replace(/^title: "\d{2}\. /m, 'title: "')
    .replace(
      /## 오늘의 책문\r?\n\r?\n> \*\*(.+?)\*\*/,
      "::: {.book-question}\n[오늘의 책문]{.book-question-label}\n\n[$1]{.book-question-prompt}\n:::"
    )
    .replace(
      /\n\| 데이터 카드 \| 발언에 쓸 수 있는 검증 문장 \|/,
      "\n### 근거 데이터 표\n\n| 근거 번호 | 토론에 쓸 수 있는 검증 문장 |"
    )
    .replace(
      /\n## 면접장 직전 메모\r?\n[\s\S]*?(?=\r?\n## 출처)/,
      "\n"
    )
    .replace(
      /`결론 → 데이터 2개 → 강한 반론 → 전환 조건`/g,
      "**결론 → 데이터 2개 → 강한 반론 → 전환 조건**"
    )
    .replace(
      /!\[[^\]]+\]\((\.\.\/figures\/week\d{2}\.png)\)(\{[^}]*\})/g,
      "![]($1)$2"
    );

  const week = filename.slice(4, 6);
  const title = updated.match(/^title: "(.+)"$/m)?.[1] ?? `책문 ${week}`;
  if (!updated.includes("book-question-image")) {
    updated = updated.replace(
      "[오늘의 책문]{.book-question-label}",
      `[오늘의 책문]{.book-question-label}\n\n![](../figures/symbols/week${week}-symbol.png){.book-question-image width=30mm fig-alt="${title} 상징 삽화"}`
    );
  }
  updated = updated.replace(
    /```\{mermaid\}[\s\S]*?```/,
    `![${title} 판단 구조](../figures/week${week}.png){fig-alt="${title} 핵심 데이터와 판단 구조"}`
  );

  if (updated !== source) {
    fs.writeFileSync(file, updated, "utf8");
    changed += 1;
  }
}

console.log(`updated chapters: ${changed}`);
