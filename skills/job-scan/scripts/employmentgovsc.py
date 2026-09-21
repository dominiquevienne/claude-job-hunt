#!/usr/bin/env python3
"""Ministry of Employment — National Vacancies (Seychelles, `www.employment.gov.sc`): the public employment service publishes **one PDF a week**, and the vacancies exist nowhere else on the site — so the adapter follows the link the page itself publishes and reads the document's own text layer, in memory. Issue #714.

  employmentgovsc.py jobs [--country-code SC] [--max-documents N]     the page, then each document it lists

WHAT IT IS. The Employment Promotion Division of Seychelles' **Department of Employment and Human
Resource Planning** files every employer's vacancy and publishes the week's list as a single PDF
(«Weekly Vacancy List - 15th to 21st September 2026», its Creole masthead «Departman Lanplwa ek
Planifikasyon Resours Imen»). **The page carries no HTML list and no count**: it is a download
category with one item, whose address changes every week — *so the link is READ FROM THE PAGE, never
composed from a date.*

THE RULES. `www.employment.gov.sc` answers its rules file: open, `certain: True`, no Crawl-delay; 2 s
is ours. The guard is taken on the exact path, the document's included.

THE DOCUMENT. `GET /job-opportunities/national-vacancies` (200; 34 169 B) lists the week's item and
its `/download`; that address answers 200 `application/pdf` (387 382 B on 2026-09-21, filename and
`modification-date` in `Content-Disposition`, «Tue, 15 Sep 2026»). **The PDF is read in memory and
never written to disk.** Its text layer is extracted with the standard library alone — the content
streams inflated, the `Tm`/`Td` positions kept, the `ToUnicode` CMaps applied to the four CID fonts —
because the layout IS the structure:

```
x = left        ADMINISTRATIVE AND OTHER RELATED SERVICES:     <- the sector, at the left margin
x = centred              PROPERTY MANAGEMENT CORPORATION       <- the employer, centred
x = left        • Financial Controller                         <- a vacancy, bulleted
x = left+18       Administrator                                <- a vacancy's second line
x = right col                        Email: … / Contact: …     <- NEVER EMITTED
x = right col                        Closing Date: 18th September 2026
```

**WITHHELD:** every employer's e-mail address and telephone number — the document is a contact sheet
as much as a vacancy list, and **it is served, they are not carried** (#183's form: the record NAMES
what was dropped in `withheld_fields`, so a silent drop cannot look like a clean board). The closing
date IS emitted: it is the vacancy's, not a person's.

**The ministry publishes no identifier**, so the key is ours and it says so: the document's own slug
plus the employer and the title, folded. Two identical lines under one employer are one vacancy.

`--max-documents` stops after N documents (the page lists one today; it has listed more). 
`--country-code` STAMPS (the document states no country — every vacancy is Seychelles' by the
ministry's own scope, and a stamp is still the user's) and the run says so.

Measured 2026-09-21 14:2x–14:3x UTC by the declared client, the guard on the exact path, two reads of
the page and one of the document: page 200 ×2 (34 169 / 34 240 B, md5 2be626f4ed64 / 8d3959a869db —
a rendered element moves), one item listed; the PDF 200, 387 382 B, md5 9d0146be3c05,
`application/pdf`, 13 pages of text, **the week of 15–21 September 2026**. The page states no count,
so the run prints what it read: the entries, the employers, the sectors and the pages.
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zlib

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "www.employment.gov.sc"
PAGE = f"https://{HOST}/job-opportunities/national-vacancies"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

LINK_RE = re.compile(r'<a[^>]+href="([^"]*/download)"[^>]*>(.*?)</a>', re.S | re.I)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{5,}\d(?!\w)")
CONTACT_RE = re.compile(r"^\s*(e-?mail|contact|tel|telephone|phone|mobile)\b\s*:?", re.I)
CLOSING_RE = re.compile(r"closing\s*date\s*:?\s*(\d{1,2})\s*(?:st|nd|rd|th)?\s*([A-Za-z]+)\s*(\d{4})", re.I)
BULLET = "•"
# WinAnsi differs from Latin-1 exactly on 0x80-0x9F, and that is where a document keeps its bullet
# (0x95), its curly quotes (0x91-0x94) and its dashes (0x96-0x97) — decoding those as Latin-1 turns
# a vacancy's bullet into a control character, and the line stops being a vacancy
WINANSI = {0x80: "\u20ac", 0x82: "\u201a", 0x83: "\u0192", 0x84: "\u201e", 0x85: "\u2026", 0x86: "\u2020",
           0x87: "\u2021", 0x88: "\u02c6", 0x89: "\u2030", 0x8a: "\u0160", 0x8b: "\u2039", 0x8c: "\u0152",
           0x8e: "\u017d", 0x91: "\u2018", 0x92: "\u2019", 0x93: "\u201c", 0x94: "\u201d", 0x95: "\u2022",
           0x96: "\u2013", 0x97: "\u2014", 0x98: "\u02dc", 0x99: "\u2122", 0x9a: "\u0161", 0x9b: "\u203a",
           0x9c: "\u0153", 0x9e: "\u017e", 0x9f: "\u0178"}
UNMAPPED = "\ufffd"          # a glyph the document's own CMap does not name: shown, so a loss cannot pass for text
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[employmentgovsc] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, binary=False):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    accept = "application/pdf,*/*;q=0.8" if binary else "text/html,application/xhtml+xml,*/*;q=0.8"
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read()
            if binary:
                return r.getcode(), raw, dict(r.headers)
            return r.getcode(), decode_body(raw, r.headers)[0], dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, b"" if binary else "", {}
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", markup or "")).replace("\xa0", " ")
    return " ".join(t.split()) or None


def scrub(s):
    """A vacancy's title never needs an address or a number; if one is there, it does not travel."""
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


# ---------------------------------------------------------------- the PDF, with the standard library

def _objects(raw):
    return {int(m.group(1)): m.group(2) for m in re.finditer(rb"(\d+)\s+\d+\s+obj\b(.*?)\bendobj", raw, re.S)}


def _stream(body):
    m = re.search(rb"stream\r?\n(.*?)\r?\nendstream", body or b"", re.S)
    if not m:
        return None
    data = m.group(1)
    if b"FlateDecode" not in body.split(b"stream", 1)[0]:
        return data
    try:
        return zlib.decompressobj().decompress(data)
    except zlib.error:
        return None


def _cmap(data):
    """A `ToUnicode` CMap → {code: text}. Without it a CID font's bytes are not characters."""
    out = {}
    for blk in re.findall(rb"beginbfchar(.*?)endbfchar", data, re.S):
        for a, b in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            out[int(a, 16)] = bytes.fromhex(b.decode()).decode("utf-16-be", "replace")
    for blk in re.findall(rb"beginbfrange(.*?)endbfrange", data, re.S):
        # a range maps to a FIRST destination, or to an ARRAY of them, one per code — and the array
        # form is not a curiosity: `<0003> <0004> [<0020> <0041>]` is where this document keeps its
        # space and its «A», and a parser that reads only the first form loses both without a word
        for lo, hi, one, many in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(?:<([0-9A-Fa-f]+)>|\[([^\]]*)\])", blk):
            lo, hi = int(lo, 16), int(hi, 16)
            if one:
                base = int(one, 16)
                for i in range(lo, min(hi, lo + 65535) + 1):
                    out[i] = chr(base + (i - lo))
            else:
                for i, dst in enumerate(re.findall(rb"<([0-9A-Fa-f]+)>", many)):
                    if lo + i <= hi:
                        out[lo + i] = bytes.fromhex(dst.decode()).decode("utf-16-be", "replace")
    return out


_STR = re.compile(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>", re.S)
_OPS = re.compile(rb"/(\w+)\s+[\d.]+\s+Tf|([\d.-]+)\s+([\d.-]+)\s+Td|[\d.-]+\s+[\d.-]+\s+[\d.-]+\s+[\d.-]+\s+([\d.-]+)\s+([\d.-]+)\s+Tm"
                  rb"|\[((?:[^\[\]\\]|\\.)*)\]\s*TJ|((?:\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>))\s*Tj", re.S)
_ESC = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f", b"(": b"(", b")": b")", b"\\": b"\\"}


def _literal(tok):
    if tok.startswith(b"<"):
        return "hex", re.sub(rb"\s", b"", tok[1:-1])
    s, out, i = tok[1:-1], bytearray(), 0
    while i < len(s):
        c = s[i:i + 1]
        if c != b"\\":
            out += c
            i += 1
            continue
        n = s[i + 1:i + 2]
        if n in _ESC:
            out += _ESC[n]
            i += 2
            continue
        oc = re.match(rb"[0-7]{1,3}", s[i + 1:i + 4])
        if oc:
            out.append(int(oc.group(0), 8))
            i += 1 + len(oc.group(0))
            continue
        i += 2
    return "lit", bytes(out)


def _num_array(body):
    """`[ 226 498 ... ]` → [226.0, 498.0, …] — the array of an object, or the object itself."""
    m = re.search(rb"\[(.*?)\]", body or b"", re.S)
    return [float(n) for n in re.findall(rb"-?[\d.]+", m.group(1))] if m else []


def _cid_widths(body):
    """A CID font's `/W`: `c [w …]` and `cfirst clast w` both, in one pass, as the format allows both."""
    out = {}
    m = re.search(rb"\[(.*?)\]\s*$|\[(.*)\]", body or b"", re.S)
    src = (m.group(1) or m.group(2)) if m else b""
    for hit in re.finditer(rb"(\d+)\s*\[([^\]]*)\]|(\d+)\s+(\d+)\s+(-?[\d.]+)(?![\d.\s]*\[)", src):
        if hit.group(1):
            first = int(hit.group(1))
            for i, w in enumerate(re.findall(rb"-?[\d.]+", hit.group(2))):
                out[first + i] = float(w)
        else:
            lo, hi, w = int(hit.group(3)), int(hit.group(4)), float(hit.group(5))
            for c in range(lo, min(hi, lo + 65535) + 1):
                out[c] = w
    return out


def _metrics(objs):
    """{font object: (widths by code, default width, is_cid)} — the glyph widths the document ships.

    Without them a run's width is a guess, and the guess decides whether two runs typeset apart are
    one word or two: «Food and» + «Beverage Attendant» came out «Food andBeverage» on an estimate,
    and «SERVIC» + «ES:» came out «SERVIC ES:» on a laxer one. The document states the widths.
    """
    out = {}
    for num, body in objs.items():
        if b"/Type0" in body:
            df = re.search(rb"/DescendantFonts\s+(?:(\d+)\s+0\s+R|\[\s*(\d+)\s+0\s+R)", body)
            desc = objs.get(int(df.group(1) or df.group(2)), b"") if df else b""
            w = re.search(rb"/W\s+(\d+)\s+0\s+R", desc)
            dw = re.search(rb"/DW\s+(-?[\d.]+)", desc)
            table = _cid_widths(objs.get(int(w.group(1)), b"")) if w else _cid_widths(desc)
            out[num] = (table, float(dw.group(1)) if dw else 1000.0, True)
        elif b"/BaseFont" in body and b"/FirstChar" in body:
            fc = re.search(rb"/FirstChar\s+(\d+)", body)
            w = re.search(rb"/Widths\s+(\d+)\s+0\s+R", body)
            arr = _num_array(objs.get(int(w.group(1)), b"")) if w else _num_array(body)
            first = int(fc.group(1)) if fc else 0
            out[num] = ({first + i: v for i, v in enumerate(arr)}, 500.0, False)
    return out


def _runs(stream, cmaps, font_map, metrics):
    """A content stream → [(y, x, text, size, width)]: the positions ARE the structure of this document."""
    out, font, x, y, size = [], None, 0.0, 0.0, 11.0
    for m in _OPS.finditer(stream):
        if m.group(1):
            font = m.group(1).decode()
            sz = re.search(rb"[\d.]+(?=\s+Tf$)", m.group(0))
            size = float(sz.group(0)) if sz else size
        elif m.group(2) is not None:
            x += float(m.group(2))
            y += float(m.group(3))
        elif m.group(4) is not None:
            x, y = float(m.group(4)), float(m.group(5))
        else:
            ref = font_map.get(font)
            cm = cmaps.get(ref)
            table, default, is_cid = metrics.get(ref, ({}, 500.0, False))
            payload = m.group(6) if m.group(6) is not None else m.group(7)
            got, units = "", 0.0
            for piece in re.finditer(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>|(-?[\d.]+)", payload, re.S):
                if piece.group(1):
                    units -= float(piece.group(1))          # a TJ kern: the number MOVES the pen
                    continue
                kind, val = _literal(piece.group(0))
                if kind == "hex":
                    codes = [int(val[i:i + 4], 16) for i in range(0, len(val) - 3, 4)]
                    if cm:
                        got += "".join(cm.get(c, UNMAPPED) for c in codes)   # a code the CMap does not name is SHOWN, never dropped
                else:
                    codes = list(val)
                    got += "".join(cm.get(b, WINANSI.get(b, chr(b))) for b in val) if cm else \
                        "".join(WINANSI.get(b, chr(b)) for b in val)
                units += sum(table.get(c, default) for c in codes)
            if got.strip():
                out.append((round(y, 1), round(x, 1), got, size, units / 1000.0 * size))
    return out


def _columns(cells):
    """One baseline → its columns.

    A vacancy and a telephone number are typeset on the SAME baseline («• Guest Service Agent» at
    x=87, «Contact: 2522265» at x=293), and a baseline read as one line carries the number into the
    title. The cut is made where a run ITSELF starts the contact block — never at a fixed
    x, because an employer's name is centred and can run past the contact column
    («OCEANICA RESORT » + «-» + «GLACIS» ends at x=337).
    """
    for i in range(1, len(cells)):
        if CONTACT_RE.match(cells[i][1]) or CLOSING_RE.match(cells[i][1]):
            return [cells[:i], cells[i:]]
    return [cells]


def _page_objects(objs):
    """The document's pages, in order, each with ITS OWN font resources.

    A font NAME is per page: `/F3` is Calibri on one page and the symbol font on another. Resolving
    the names globally silently dropped every character its CMap did not know — «REBA'S MOTOR
    MECHANIC» came out «REB'S MOTOR MECHNIC», and nothing in the output said a letter was missing.
    """
    out = []
    for num, body in objs.items():
        if b"/Type" not in body or not re.search(rb"/Type\s*/Page\b", body):
            continue
        res = body
        rr = re.search(rb"/Resources\s+(\d+)\s+0\s+R", body)
        if rr:
            res = objs.get(int(rr.group(1)), b"")
        fonts = {}
        fm = re.search(rb"/Font\s*(?:(\d+)\s+0\s+R|<<(.*?)>>)", res, re.S)
        if fm:
            block = objs.get(int(fm.group(1)), b"") if fm.group(1) else fm.group(2)
            for name, ref in re.findall(rb"/(\w+)\s+(\d+)\s+0\s+R", block):
                fonts[name.decode()] = int(ref)
        contents = [int(n) for n in re.findall(rb"(\d+)\s+0\s+R", (re.search(rb"/Contents\s+(\[[^\]]*\]|\d+\s+0\s+R)", body) or [b"", b""])[1])]
        out.append((num, contents, fonts))
    return out


def pdf_lines(raw):
    """The document → [[(x, y, line)] per page], the runs of one baseline joined left to right."""
    objs = _objects(raw)
    cmaps = {}
    for num, body in objs.items():
        tu = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", body)
        if tu:
            d = _stream(objs.get(int(tu.group(1)), b""))
            if d:
                cmaps[num] = _cmap(d)
    metrics = _metrics(objs)
    pages = []
    for _num, contents, fonts in _page_objects(objs):
        data = b"\n".join(d for d in (_stream(objs.get(c, b"")) for c in contents) if d)
        if not data or (b"Tj" not in data and b"TJ" not in data):
            continue
        runs = _runs(data, cmaps, fonts, metrics)
        rows = {}
        for y, x, t, size, width in runs:
            rows.setdefault(y, []).append((x, t, size, width))
        page = []
        for y in sorted(rows, reverse=True):
            cells = sorted(rows[y])
            for seg in _columns(cells):
                # runs are concatenated; a space goes back ONLY where the document typeset one —
                # the pen's gap, measured with the font's own widths, wider than a sixth of the size
                line, pen = "", None
                for cx, t, size, width in seg:
                    if pen is not None and cx - pen > size / 6.0 and not line.endswith(" ") and not t.startswith(" "):
                        line += " "
                    line += t
                    pen = cx + width
                page.append((seg[0][0], round(y, 1), " ".join(line.split())))
        pages.append(page)
    return pages


# ---------------------------------------------------------------- the ministry's layout

def is_caps(s):
    letters = [c for c in s if c.isalpha()]
    return bool(letters) and sum(1 for c in letters if c.isupper()) >= len(letters) - 1


def closing_of(line):
    m = CLOSING_RE.search(line or "")
    if not m or not MONTHS.get(m.group(2).lower()):
        return None
    return f"{m.group(3)}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"


def entries_of(pages):
    """The document's own layout → [entry]; the right column is read to be WITHHELD, never emitted.

    An employer's contact block can be typeset ABOVE its own first bullet (the e-mail sits at
    y=609.7 and the vacancy at y=609.1), so the block is collected first and applied to its
    vacancies afterwards — reading it forward would attach the closing date to the employer before.
    """
    blocks, sector, ignored = [], None, 0
    for page in pages:
        left = min((x for x, _y, _l in page), default=0.0)
        last_y = None
        for x, y, line in page:
            if not line:
                continue
            if line.startswith(BULLET):
                title = line.lstrip(BULLET).strip()
                if title:
                    if not blocks:
                        blocks.append({"sector": sector, "employer": None, "titles": [],
                                       "had_email": False, "had_phone": False, "closing": None})
                    # a vacancy line can run into the employer's address when the columns touch;
                    # the title is scrubbed, and the record declares it like any other withholding
                    blocks[-1]["titles"].append({"text": title, "had_email": bool(MAIL_RE.search(title)),
                                                 "had_phone": bool(PHONE_RE.search(title))})
                    last_y = y
                continue
            if CONTACT_RE.match(line) or MAIL_RE.search(line) or CLOSING_RE.search(line):
                if blocks:
                    b = blocks[-1]
                    b["closing"] = b["closing"] or closing_of(line)
                    b["had_email"] = b["had_email"] or bool(MAIL_RE.search(line))
                    b["had_phone"] = b["had_phone"] or bool(PHONE_RE.search(line) and not CLOSING_RE.search(line))
                continue        # the contact column is beside the vacancy, not between it and its second line
            if (blocks and blocks[-1]["titles"] and last_y is not None
                    and left + 8 < x < left + 60 and abs(last_y - y) < 25 and not is_caps(line)):
                t = blocks[-1]["titles"][-1]
                t["text"] = " ".join((t["text"] + " " + line).split())               # a wrapped title
                t["had_email"] = t["had_email"] or bool(MAIL_RE.search(line))
                t["had_phone"] = t["had_phone"] or bool(PHONE_RE.search(line))
                last_y = y
                continue
            if is_caps(line):
                last_y = None
                if abs(x - left) <= 5:
                    sector = line.rstrip(":").strip()
                else:
                    blocks.append({"sector": sector, "employer": line, "titles": [],
                                   "had_email": False, "had_phone": False, "closing": None})
                continue
            last_y = None
            ignored += 1
    out = []
    for b in blocks:
        for t in b["titles"]:
            out.append({"sector": b["sector"], "employer": b["employer"], "title": t["text"],
                        "closing_date": b["closing"],
                        "had_email": b["had_email"] or t["had_email"],
                        "had_phone": b["had_phone"] or t["had_phone"]})
    return out, ignored


def record(doc, e, stamp):
    withheld = ["employer_email"] if e["had_email"] else []
    if e["had_phone"]:
        withheld.append("employer_phone")
    # the KEY is built from what is emitted, never from what was read: a vacancy line that ran into
    # the employer's address would otherwise carry it into the identifier, where nobody looks for one
    title, employer = scrub(e["title"]), scrub(e["employer"])
    key = f"{doc['slug']}:{slug(employer)}:{slug(title)}"
    return {
        "source": "employmentgovsc", "country": stamp,
        "ledger_id": f"employmentgovsc:{key}", "id": key,
        "title": title, "employer": employer, "sector": e["sector"],
        "closing_date": e["closing_date"],
        "document": doc["title"], "document_url": doc["url"],
        "document_published": doc.get("modified"),
        "key_is_ours": True,                 # the ministry publishes no identifier, and the record says so
        "withheld_fields": withheld,         # what the document carried and the record does not
        "contacts_withheld": True,
    }


def documents_of(markup):
    """The page → [(url, title)] for each item it links; the address changes every week and is never composed."""
    out, seen = [], set()
    for href, label in LINK_RE.findall(markup or ""):
        url = urllib.parse.urljoin(PAGE + "/", htmlmod.unescape(href))
        name = text(label)
        if url in seen or not name or name.lower() == "download":
            if url not in seen:
                out.append((url, None))
                seen.add(url)
            continue
        seen.add(url)
        out.append((url, name))
    return [(u, t) for u, t in out if t] or out


def cmd_jobs(a):
    code, body, _h = request(PAGE)
    if code == 404:
        die(f"{PAGE}: HTTP 404 — the category is gone", EXIT_GONE)
    if code != 200:
        die(f"{PAGE}: HTTP {code}", EXIT_PARTIAL)
    docs = documents_of(body)
    if not docs:
        die(f"{PAGE}: 200 but no document is linked — the page changed, or the week's list is not up; not an empty board", EXIT_PARTIAL)
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, read = [], set(), []
    for url, title in docs[: a.max_documents or len(docs)]:
        code, raw, headers = request(url, binary=True)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        ctype = (headers.get("Content-Type") or "").lower()
        if "pdf" not in ctype and not raw.startswith(b"%PDF"):
            die(f"{url}: {ctype or 'no content type'} and no %PDF header — the week's list is not a PDF any more", EXIT_PARTIAL)
        disp = headers.get("Content-Disposition") or ""
        mod = re.search(r'modification-date="([^"]+)"', disp)
        doc = {"url": url, "title": title or (re.search(r'filename="([^"]+)"', disp) or [None, None])[1],
               "slug": slug(url.rsplit("/download", 1)[0].rsplit("/", 1)[-1]),
               "modified": mod.group(1) if mod else None}
        pages = pdf_lines(raw)                      # read in memory; the document is never written to disk
        if not pages:
            die(f"{url}: {th(len(raw))} B of PDF with no text layer — a scan, not a list we can read", EXIT_PARTIAL)
        entries, ignored = entries_of(pages)
        read.append((doc["title"], len(pages), len(entries), ignored))
        for e in entries:
            r = record(doc, e, stamp)
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    for title, pages, entries, ignored in read:
        note(f"«{title}»: {th(pages)} page(s) of text, {th(entries)} bulleted vacancy line(s), {th(ignored)} line(s) neither sector, employer, vacancy nor contact.")
    employers = len({r["employer"] for r in rows})
    sectors = len({r["sector"] for r in rows if r["sector"]})
    withheld = sum(1 for r in rows if r["withheld_fields"])
    note(f"{th(len(rows))} vacancies emitted, {th(employers)} employer(s), {th(sectors)} sector(s) — **the page and the document state no count**: what the week's list carries is the board.")
    note(f"employer e-mails and telephone numbers never emitted — {th(withheld)} record(s) name what was dropped in `withheld_fields`; the closing date is the vacancy's and is emitted.")
    note("the key is OURS (document slug + employer + title): the ministry publishes no identifier, and `key_is_ours` says so on every record.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the document states no country.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Ministry of Employment — National Vacancies (Seychelles): the week's PDF, followed from the page that publishes it and read in memory. Issue #714.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the page, then each document it lists (1 request each)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the document states none)")
    j.add_argument("--max-documents", dest="max_documents", type=int, default=0, help="stop after N documents (0 = every one the page lists)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
