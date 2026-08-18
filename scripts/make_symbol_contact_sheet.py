"""Build a numbered contact sheet for visual QA of the 30 chapter symbols."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "book" / "figures" / "symbols"
OUTPUT = ROOT / "tmp" / "proof" / "symbol-contact-sheet-v2.png"


def main() -> None:
    thumb = 220
    label_height = 30
    cols, rows = 5, 6
    sheet = Image.new("RGB", (cols * thumb, rows * (thumb + label_height)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=18)
    for index in range(30):
        week = index + 1
        path = SOURCE / f"week{week:02d}-symbol-v2.png"
        with Image.open(path) as source:
            image = source.convert("RGB")
            image.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
        x = (index % cols) * thumb
        y = (index // cols) * (thumb + label_height)
        sheet.paste(image, (x + (thumb - image.width) // 2, y))
        draw.text((x + 8, y + thumb + 4), f"{week:02d}", fill="#10283F", font=font)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
