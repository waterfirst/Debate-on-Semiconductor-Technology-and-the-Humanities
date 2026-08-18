from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FONT_DIRS = [
    Path(r"C:\Windows\Fonts"),
    Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts",
]
FONT_NAMES = [
    "HANBatangExt.ttf",
    "HANBatangExtB.ttf",
    "HANBatangExtBB.ttf",
    "NotoSerifKR-VF.ttf",
    "NotoSerifKR-Regular.otf",
    "SimsunExtG.ttf",
    "KoPubBatangMedium.ttf",
]


FC_QUERY = Path(r"C:\Program Files\MiKTeX\miktex\bin\x64\fc-query.exe")


def cmap(path: Path) -> set[int]:
    result = subprocess.run(
        [str(FC_QUERY), "--format=%{charset}", str(path)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    points: set[int] = set()
    for token in result.stdout.split():
        if "-" in token:
            try:
                start, end = (int(value, 16) for value in token.split("-", 1))
            except ValueError:
                continue
            points.update(range(start, end + 1))
        else:
            try:
                points.add(int(token, 16))
            except ValueError:
                pass
    return points


def is_hanja(codepoint: int) -> bool:
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0x20000 <= codepoint <= 0x2FA1F
    )


source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "book").rglob("*.qmd"))
hanja = sorted({ord(char) for char in source if is_hanja(ord(char))})

print(f"hanja_codepoints={len(hanja)}")
full_coverage = []
for name in FONT_NAMES:
    path = next((directory / name for directory in FONT_DIRS if (directory / name).exists()), None)
    if path is None:
        continue
    supported = cmap(path)
    missing = [cp for cp in hanja if cp not in supported]
    sample = ",".join(f"U+{cp:04X}" for cp in missing[:12])
    print(f"{path.name}: missing={len(missing)} {sample}")
    if not missing:
        full_coverage.append(path.name)

assert full_coverage, "No installed font covers every Hanja code point in the manuscript"
print(f"full_coverage={','.join(full_coverage)}")
print("hanja_font_audit=PASS")
