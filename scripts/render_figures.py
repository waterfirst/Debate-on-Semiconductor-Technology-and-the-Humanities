"""Regenerate chart SVG files without overwriting chapter manuscripts."""

from enrich_content import EVIDENCE, FIGURES, TOPICS, svg_chart, svg_matrix


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    written = 0
    for topic in TOPICS:
        week, title = topic[0], topic[1]
        evidence = EVIDENCE[week]
        output = FIGURES / f"week{week:02d}.svg"
        output.write_text(
            svg_chart(week, title, evidence["unit"], evidence["chart"])
            if evidence["chart"]
            else svg_matrix(title),
            encoding="utf-8",
        )
        written += 1
    print(f"rendered figure SVGs: {written}")


if __name__ == "__main__":
    main()
