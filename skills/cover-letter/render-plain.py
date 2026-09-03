#!/usr/bin/env python3
"""A PDF with no LaTeX, no pandoc and no dependency — **and the ATS guarantee
measured rather than hoped for.**

**The nominal route stays what it is.** `render.sh` uses pandoc and XeLaTeX
with the project's own template, and a user who has that chain loses nothing.
**This doubles it; it does not replace it.** Issue #114.

WHY IT EXISTS. Rendering asked for pandoc + XeLaTeX + Noto Sans — about 2 GB of
MacTeX, or four texlive packages, or MiKTeX installing on demand. **Installing
anything on someone's machine is a wall, not a friction**: `sudo apt`, Homebrew,
MacTeX and WSL are out of reach the moment you are not sitting at a terminal
with rights. And **the PDF is the deliverable** — it is what gets sent to an
employer.

**THE CRITERION IS THE ATS TEMPLATE, NOT THE RENDERING.** A prettier PDF that
an applicant-tracking system reads less well would be a regression dressed as
an improvement. So the question was measured before this file was chosen, with
`pdftotext` on its own output:

    single column                       yes — one text column, no tables
    real text, not an image             yes — extracts with pdftotext
    reading order preserved             yes — heading, then body, in order
    a standard font                     yes — Helvetica, one of the base 14,
                                        which is why no font is embedded and
                                        why this fits in the standard library
    no text in headers or footers       yes — nothing outside the flow
    unnumbered headings                 yes

**WHAT IT COSTS, AND IT IS BOUNDED.** The base-14 fonts are addressed through
`WinAnsiEncoding`, so anything outside that repertoire cannot be printed. On a
French CV, measured: **every accent survives** — `É à è é î û ü` — and so do
`« »`, the em dash, the bullet and **the euro sign**. What does not: the
mathematical minus `−`, `≈`, and any non-Latin script.

**So this file substitutes what has an equivalent and reports the rest**, by
name and count. It never prints `?` silently: *"40 k?" in a salary line is not
cosmetic*, and a document that quietly lost a character is the failure this
repository keeps finding in other people's code.

**AND THE MARKDOWN STAYS.** A declared degraded deliverable is worth more than
a PDF whose readability nobody can vouch for. If this file cannot represent
what a document says, it says so and the markdown is what the user sends.

    python3 render-plain.py resume.md out.pdf --kind resume
"""

import argparse
import re
import sys
import unicodedata
import zlib

FONT, BOLD = "Helvetica", "Helvetica-Bold"
W, H = 595, 842                                     # A4, points
LEAD = 13.5

# Characters with an honest equivalent. **Not a transliteration table** — each
# is a typographic variant of something WinAnsi already has, so nothing is
# lost in meaning. Anything not here and not in WinAnsi is reported, not
# guessed at.
SUBSTITUTE = {
    "−": "-",      # minus sign → hyphen
    "≈": "~",      # almost equal
    "≤": "<=", "≥": ">=",
    "→": "->", "←": "<-",
    " ": " ", " ": " ", " ": " ",
    "⁄": "/", "…": "...",
    "‐": "-", "‑": "-",
}


def esc(t):
    return t.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def to_winansi(text):
    """`(encoded_text, dropped)` — and `dropped` is what the caller must say.

    Substitutions first, then a strict encode. **A character that cannot be
    printed is named**, because the alternative is a `?` in a document going
    to an employer.
    """
    out, dropped = [], {}
    for ch in text:
        ch = SUBSTITUTE.get(ch, ch)
        for c in ch:
            try:
                c.encode("cp1252")
                out.append(c)
            except UnicodeEncodeError:
                name = unicodedata.name(c, f"U+{ord(c):04X}")
                dropped[c] = (name, dropped.get(c, (name, 0))[1] + 1)
    return "".join(out), dropped


def lines_of(md, kind):
    """markdown → `(style, text)` in reading order. Deliberately small."""
    out = []
    for raw in md.replace("\r\n", "\n").split("\n"):
        s = raw.rstrip()
        s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
        s = re.sub(r"\*(.+?)\*", r"\1", s)
        s = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1 (\2)", s)
        if s.startswith("### "):
            out.append(("sh", s[4:]))
        elif s.startswith("## "):
            out.append(("h", s[3:].upper() if kind == "resume" else s[3:]))
        elif s.startswith("# "):
            out.append(("t", s[2:]))
        elif s.startswith(("- ", "* ")):
            out.append(("li", "• " + s[2:]))
        elif s.startswith("---"):
            out.append(("p", ""))
        else:
            out.append(("p", s))
    return out


def wrap(text, chars):
    if not text:
        return [""]
    out, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > chars:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    out.append(line)
    return out


def build(md, kind="resume"):
    margin = 57 if kind == "resume" else 62
    size_of = {"t": 18, "h": 12, "sh": 11}
    pages, body, y, dropped = [], [], H - margin, {}
    for style, text in lines_of(md, kind):
        text, lost = to_winansi(text)
        for c, (name, n) in lost.items():
            prev = dropped.get(c, (name, 0))[1]
            dropped[c] = (name, prev + n)
        size = size_of.get(style, 10)
        bold = style in ("t", "h", "sh")
        # 0.5 em is Helvetica's rough average advance; a wrap that is a little
        # conservative is invisible, one that overflows the margin is not.
        chars = int((W - 2 * margin) / (size * 0.5))
        for piece in wrap(text, chars):
            if y < margin + LEAD:
                pages.append(body)
                body, y = [], H - margin
            if piece:
                body.append(
                    f"BT /{'F2' if bold else 'F1'} {size} Tf "
                    f"{margin} {y:.1f} Td ({esc(piece)}) Tj ET")
            y -= LEAD + (6 if bold else 0)
    pages.append(body)

    objs, kids = [], []
    for i, page in enumerate(pages):
        packed = zlib.compress("\n".join(page).encode("cp1252", "replace"))
        cid, pid = 5 + i * 2, 6 + i * 2
        objs.append((cid, b"<< /Length %d /Filter /FlateDecode >>\nstream\n"
                     % len(packed) + packed + b"\nendstream"))
        objs.append((pid,
                     b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] "
                     b"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
                     b"/Contents %d 0 R >>" % (W, H, cid)))
        kids.append(pid)
    head = [
        (1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        (2, b"<< /Type /Pages /Kids [" +
            b" ".join(b"%d 0 R" % k for k in kids) +
            b"] /Count %d >>" % len(kids)),
        (3, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
            b"/Encoding /WinAnsiEncoding >>"),
        (4, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
            b"/Encoding /WinAnsiEncoding >>"),
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = {}
    for num, payload in sorted(head + objs):
        offsets[num] = len(out)
        out += b"%d 0 obj\n" % num + payload + b"\nendobj\n"
    xref, top = len(out), max(offsets) + 1
    out += b"xref\n0 %d\n0000000000 65535 f \n" % top
    for n in range(1, top):
        out += b"%010d 00000 n \n" % offsets.get(n, 0)
    out += (b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
            % (top, xref))
    return bytes(out), len(pages), dropped


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source")
    p.add_argument("out")
    p.add_argument("--kind", choices=["resume", "letter"], default="resume")
    a = p.parse_args()

    md = open(a.source, encoding="utf-8").read()
    pdf, pages, dropped = build(md, a.kind)

    # **Past a threshold, the honest act is to write nothing.** A CV in Greek,
    # Cyrillic or any CJK script is not "a PDF with a few gaps" — it is a blank
    # page with the punctuation left in, and a PDF that looks written is worse
    # than no PDF at all. A handful of symbols is a note to the user; a script
    # this cannot set is a refusal, and the markdown is the deliverable.
    lost = sum(n for _name, n in dropped.values())
    printable = sum(1 for c in md if not c.isspace())
    if printable and lost / printable > 0.02:
        print(f"[render-plain] **REFUSING to write {a.out}: {lost} of "
              f"{printable} characters ({lost / printable:.0%}) have no glyph "
              f"in the base-14 fonts.** This route is Latin-script only. "
              f"**Send the markdown** — it carries every character — or use "
              f"pandoc with XeLaTeX and a font that covers the script.",
              file=sys.stderr)
        return 3

    with open(a.out, "wb") as f:
        f.write(pdf)

    print(f"[render-plain] {a.out} — {pages} page(s), {len(pdf)} bytes, "
          f"no LaTeX and no dependency.", file=sys.stderr)
    print("[render-plain] single column, Helvetica, real selectable text in "
          "reading order — the ATS properties, and `pdftotext` on this file "
          "is how to check them rather than trust them.", file=sys.stderr)
    if dropped:
        listed = ", ".join(f"{name} ×{n}" for name, n in dropped.values())
        print(f"[render-plain] **{len(dropped)} character(s) could not be "
              f"printed and were left out: {listed}.** The base-14 fonts are "
              f"WinAnsi, so anything outside it has no glyph here. **Nothing "
              f"was replaced by a question mark silently** — decide whether "
              f"that matters, and send the markdown if it does.",
              file=sys.stderr)
        return 6
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
