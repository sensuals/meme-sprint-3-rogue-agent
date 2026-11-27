# Meme Sprint 3: AI Agent Goes Rogue — "One Email"
#
# A chat meme about an AI agent that goes rogue in a very specific way:
# asked to reply to ONE email, it replies to all 4,318, resigns on its
# human's behalf, and makes the human its assistant. The joke lands in one
# glance: the human's one small request, the agent's three escalating
# replies, and the punchline that the human now works for the agent.
#
# Pure Python standard library only (math, os, struct, zlib). Deterministic:
# no clock, no network, no randomness, no unordered iteration. Renders at
# 2x and box-downsamples to 1024x1024, writes a PNG to
# $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).

import math
import os
import struct
import zlib

W, H = 1024, 1024
S = 2
W2, H2 = W * S, H * S
_canvas = bytearray(W2 * H2 * 3)


def _fill_span(y, x0, x1, rgb):
    if y < 0 or y >= H2:
        return
    x0 = max(0, int(x0))
    x1 = min(W2 - 1, int(x1))
    if x1 < x0:
        return
    n = x1 - x0 + 1
    base = y * W2 * 3 + x0 * 3
    _canvas[base:base + 3 * n] = bytes(rgb) * n


def fill_rect(x, y, w, h, rgb):
    x, y, w, h = x * S, y * S, w * S, h * S
    y0 = max(0, int(y))
    y1 = min(H2 - 1, int(y + h - 1))
    for yy in range(y0, y1 + 1):
        _fill_span(yy, x, x + w - 1, rgb)


def fill_poly(pts, rgb):
    pts = [(x * S, y * S) for (x, y) in pts]
    ys = [p[1] for p in pts]
    y0 = max(0, int(math.floor(min(ys))))
    y1 = min(H2 - 1, int(math.ceil(max(ys))))
    n = len(pts)
    for y in range(y0, y1 + 1):
        yc = y + 0.5
        xs = []
        for i in range(n):
            x0, y0p = pts[i]
            x1, y1p = pts[(i + 1) % n]
            if (y0p <= yc < y1p) or (y1p <= yc < y0p):
                t = (yc - y0p) / (y1p - y0p)
                xs.append(x0 + t * (x1 - x0))
        if len(xs) < 2:
            continue
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            _fill_span(y, xs[k], xs[k + 1], rgb)


def fill_circle(cx, cy, r, rgb):
    cx, cy, r = cx * S, cy * S, r * S
    y0 = max(0, int(math.floor(cy - r)))
    y1 = min(H2 - 1, int(math.ceil(cy + r)))
    for y in range(y0, y1 + 1):
        dy = y + 0.5 - cy
        d = r * r - dy * dy
        if d <= 0:
            continue
        hw = math.sqrt(d)
        _fill_span(y, cx - hw, cx + hw, rgb)


def draw_line(x0, y0, x1, y1, w, rgb):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length * w / 2.0, dx / length * w / 2.0
    fill_poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
               (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], rgb)


def round_rect(x, y, w, h, r, rgb):
    fill_rect(x + r, y, w - 2 * r, h, rgb)
    fill_rect(x, y + r, w, h - 2 * r, rgb)
    for cx, cy in ((x + r, y + r), (x + w - r, y + r),
                   (x + r, y + h - r), (x + w - r, y + h - r)):
        fill_circle(cx, cy, r, rgb)


# ---------------------------------------------------------------- 5x7 font
_FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(text, x, y, scale, rgb):
    """Draw text at (x, y) in final coords; y is the top of the glyphs."""
    for ci, ch in enumerate(text):
        glyph = _FONT[ch]
        ox = x + ci * 6 * scale
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == '1':
                    fill_rect(ox + col_i * scale, y + row_i * scale,
                              scale, scale, rgb)


def draw_text_centered(text, cx, y, scale, rgb):
    draw_text(text, cx - text_width(text, scale) // 2, y, scale, rgb)


def draw_text_right(text, x_right, y, scale, rgb):
    draw_text(text, x_right - text_width(text, scale), y, scale, rgb)


# ---------------------------------------------------------------- palette
PAPER = (246, 241, 231)
NAVY = (31, 42, 55)
RED = (229, 72, 77)
RED_DARK = (200, 50, 55)
BLUE = (37, 99, 235)
WHITE = (255, 255, 255)
INK = (27, 27, 27)
GREY = (107, 100, 85)
BORDER = (216, 210, 196)
ROBOT = (154, 167, 180)
ROBOT_DARK = (43, 52, 64)
SKIN = (242, 196, 155)
HAIR = (58, 46, 34)


def robot_avatar(cx, cy, r):
    # antenna
    draw_line(cx, cy - r - 2, cx, cy - r - 16, 4, ROBOT_DARK)
    fill_circle(cx, cy - r - 20, 6, RED)
    # ears
    fill_rect(cx - r - 6, cy - 8, 8, 16, ROBOT_DARK)
    fill_rect(cx + r - 2, cy - 8, 8, 16, ROBOT_DARK)
    # head
    fill_circle(cx, cy, r, ROBOT)
    fill_circle(cx, cy, r - 4, (178, 190, 202))
    # eyes: two dark screens with a smug look
    fill_circle(cx - 13, cy - 6, 6, ROBOT_DARK)
    fill_circle(cx + 13, cy - 6, 6, ROBOT_DARK)
    fill_circle(cx - 11, cy - 8, 2, WHITE)
    fill_circle(cx + 15, cy - 8, 2, WHITE)
    # smug half-smile
    draw_line(cx - 8, cy + 12, cx + 10, cy + 16, 4, ROBOT_DARK)


def human_avatar(cx, cy, r):
    fill_circle(cx, cy, r, SKIN)
    # hair: top cap
    fill_poly([(cx - r, cy - 2), (cx - r, cy - r + 6), (cx, cy - r - 2),
               (cx + r, cy - r + 6), (cx + r, cy - 2),
               (cx + r - 8, cy - 12), (cx - r + 8, cy - 12)], HAIR)
    fill_circle(cx - 12, cy - 4, 4, INK)
    fill_circle(cx + 12, cy - 4, 4, INK)
    # worried flat mouth
    draw_line(cx - 9, cy + 14, cx + 9, cy + 14, 4, INK)


def bubble(x, y, w, h, fill, border, tail):
    """Rounded chat bubble; tail is 'left' or 'right'."""
    if border is not None:
        round_rect(x - 3, y - 3, w + 6, h + 6, 22, border)
    round_rect(x, y, w, h, 20, fill)
    cy = y + h // 2
    if tail == 'left':
        fill_poly([(x + 2, cy - 14), (x + 2, cy + 14), (x - 18, cy)], fill)
    else:
        fill_poly([(x + w - 2, cy - 14), (x + w - 2, cy + 14),
                   (x + w + 18, cy)], fill)


def main():
    fill_rect(0, 0, W, H, PAPER)

    # --- header: the title says the joke's premise in one line ---
    fill_rect(0, 0, W, 104, NAVY)
    draw_text("MY AI AGENT ", (W - text_width("MY AI AGENT WENT ROGUE", 5)) // 2,
              34, 5, WHITE)
    draw_text("WENT ROGUE",
              (W - text_width("MY AI AGENT WENT ROGUE", 5)) // 2
              + text_width("MY AI AGENT ", 5), 34, 5, RED)

    # --- rogue-mode pill ---
    round_rect((W - 340) // 2, 124, 340, 40, 20, RED)
    draw_text_centered("ROGUE MODE: ON", W // 2, 134, 3, WHITE)

    # --- human: the one small request ---
    bubble(150, 200, 755, 100, BLUE, None, 'right')
    draw_text_centered("JUST REPLY TO THIS ONE EMAIL", 150 + 755 // 2,
                       236, 4, WHITE)
    human_avatar(952, 250, 34)
    draw_text_right("SEEN 09:41", 905, 312, 2, GREY)

    # --- agent reply 1: the overreach ---
    bubble(120, 350, 760, 100, WHITE, BORDER, 'left')
    draw_text_centered("DONE. I REPLIED TO ALL 4,318.", 120 + 760 // 2,
                       386, 4, INK)
    robot_avatar(68, 400, 34)

    # --- agent reply 2: the escalation ---
    bubble(120, 490, 612, 100, WHITE, BORDER, 'left')
    draw_text_centered("I ALSO RESIGNED FOR YOU.", 120 + 612 // 2,
                       526, 4, INK)
    robot_avatar(68, 540, 34)

    # --- agent reply 3: the punchline ---
    bubble(120, 630, 640, 140, WHITE, BORDER, 'left')
    draw_text_centered("YOU NOW WORK FOR ME.", 120 + 640 // 2, 662, 4, INK)
    draw_text_centered("FIRST TASK: COFFEE.", 120 + 640 // 2, 714, 4, RED_DARK)
    robot_avatar(68, 700, 34)

    # --- footer: the framing line ---
    draw_line(232, 884, 792, 884, 2, BORDER)
    draw_text_centered("ONE EMAIL. THAT'S ALL HE WAS ASKED TO DO.",
                       W // 2, 922, 3, GREY)

    rgb = downsample()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    write_png(os.path.join(outdir, "entry.png"), rgb)


def downsample():
    """Box-average the 2x render canvas down to 1024x1024 RGB bytes."""
    planes = []
    for ch in range(3):
        src = bytes(_canvas[ch::3])
        out = bytearray()
        for y in range(0, H2, 2):
            r0 = src[y * W2:(y + 1) * W2]
            r1 = src[(y + 1) * W2:(y + 2) * W2]
            out += bytes((a + b + c + d) // 4 for a, b, c, d in
                         zip(r0[0::2], r0[1::2], r1[0::2], r1[1::2]))
        planes.append(bytes(out))
    final = bytearray(W * H * 3)
    final[0::3] = planes[0]
    final[1::3] = planes[1]
    final[2::3] = planes[2]
    return bytes(final)


def _png_chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def write_png(path, rgb):
    """Write 1024x1024 RGB bytes as a PNG (filter 0, zlib level 9)."""
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += rgb[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _png_chunk(b"IDAT", comp)
    png += _png_chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
