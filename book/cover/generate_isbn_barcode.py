"""Generate the assigned ISBN EAN-13 barcode and Korean 5-digit add-on as SVG."""

from __future__ import annotations

from pathlib import Path


OUTPUT = Path(__file__).with_name("isbn-barcode.svg")
ISBN = "9791122089585"
ADDON = "03500"

L = ("0001101", "0011001", "0010011", "0111101", "0100011", "0110001", "0101111", "0111011", "0110111", "0001011")
G = ("0100111", "0110011", "0011011", "0100001", "0011101", "0111001", "0000101", "0010001", "0001001", "0010111")
R = ("1110010", "1100110", "1101100", "1000010", "1011100", "1001110", "1010000", "1000100", "1001000", "1110100")
EAN_PARITY = ("LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG", "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL")
ADDON_PARITY = ("GGLLL", "GLGLL", "GLLGL", "GLLLG", "LGGLL", "LLGGL", "LLLGG", "LGLGL", "LGLLG", "LLGLG")


def check_digit(first_twelve: str) -> int:
    total = sum(int(value) * (3 if index % 2 else 1) for index, value in enumerate(first_twelve))
    return (10 - total % 10) % 10


def ean_bits(code: str) -> str:
    parity = EAN_PARITY[int(code[0])]
    left = "".join((L if kind == "L" else G)[int(digit)] for digit, kind in zip(code[1:7], parity))
    right = "".join(R[int(digit)] for digit in code[7:])
    return "101" + left + "01010" + right + "101"


def addon_bits(code: str) -> str:
    checksum = (3 * sum(map(int, code[::2])) + 9 * sum(map(int, code[1::2]))) % 10
    parity = ADDON_PARITY[checksum]
    encoded = [(L if kind == "L" else G)[int(digit)] for digit, kind in zip(code, parity)]
    return "1011" + "01".join(encoded)


def bar_rects(bits: str, start_x: int, y: int, module: int, height: int, *, guards: set[int] | None = None) -> list[str]:
    guards = guards or set()
    rects: list[str] = []
    for index, bit in enumerate(bits):
        if bit == "1":
            extra = 16 if index in guards else 0
            rects.append(f'<rect x="{start_x + index * module}" y="{y}" width="{module}" height="{height + extra}"/>')
    return rects


def main() -> None:
    if len(ISBN) != 13 or check_digit(ISBN[:12]) != int(ISBN[-1]):
        raise ValueError("invalid ISBN-13 check digit")
    module = 3
    main_bits = ean_bits(ISBN)
    addon = addon_bits(ADDON)
    main_x = 28
    addon_x = main_x + len(main_bits) * module + 28
    guards = set(range(3)) | set(range(45, 50)) | set(range(92, 95))
    bars = bar_rects(main_bits, main_x, 46, module, 150, guards=guards)
    bars += bar_rects(addon, addon_x, 67, module, 129)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="260" viewBox="0 0 500 260">
<rect width="500" height="260" fill="#fff"/>
<g fill="#000">{''.join(bars)}</g>
<g font-family="Arial, sans-serif" fill="#000">
  <text x="28" y="28" font-size="22">ISBN 979-11-220895-8-5</text>
  <text x="{addon_x}" y="55" font-size="18">03500</text>
  <text x="18" y="228" font-size="20">9</text>
  <text x="55" y="228" font-size="20" letter-spacing="12">791122</text>
  <text x="205" y="228" font-size="20" letter-spacing="12">089585</text>
  <text x="28" y="252" font-size="18">정가 15,000원</text>
</g>
</svg>'''
    OUTPUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"barcode={OUTPUT} isbn={ISBN} addon={ADDON}")


if __name__ == "__main__":
    main()
