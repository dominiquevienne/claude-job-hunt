#!/usr/bin/env python3
"""Tala-Com (`www.tala-com.com`, DR Congo): the national directory's job section — `/offres-demploi/` paginated fifteen a page, the site stating no total, its pager the only bound; the advert page's labelled block (contract, posts, reference, expiry, region), its WebPage `datePublished`, its text scrubbed. Issue #339.

  talacom.py list [--no-sitemap]
  talacom.py ad --url https://www.tala-com.com/offres-emploi/<slug>/

THE RULES (1 583 B, read 2026-09-21 07:33 UTC): `User-agent: *` refuses the
WordPress internals (`/wp-admin/`, `/wp-includes/`, `/wp-content/plugins/`,
`/feed/`, `/*.php$`, `/*?*` — no query string is ever sent), and a group naming
sixteen AI agents — `ClaudeBot`, `Claude-Web`, `anthropic-ai` among them —
carries NO directive: nothing refused. `/offres-demploi/`, `/offres-demploi/page/N/`,
`/offres-emploi/<slug>/` and the sitemaps are open; no Crawl-delay; 2 s
between requests are ours.

THE ROUTE, MEASURED 2026-09-21 07:34 UTC, the declared client (served since
this morning — the provider's 25-byte 403 of 2026-09-07..14 is gone).
`/offres-demploi/` answers 200 with fifteen `article.emploi-item` cards —
employer (`h3.emploi-title`), region (`.emploi-adresse`), the post
(`.emploi-poste`), the contract (`.emploi-horaires`), the advert's address
`/offres-emploi/<slug>/` — and a pager `.talacom-pagination` whose numbered
links name the last page; `/page/2/` fourteen; **a page beyond the end
answers 200 with no card** (`/page/3/`, 224 KB of shell) — the walk ends on
the pager, not on a 404. **The site states no total**: the pager bounds it
(two pages of fifteen: 16–30), and the Yoast sitemap
`offre_emploi-sitemap.xml` (60 addresses on 2026-09-21, expired adverts
included) is read once so every emitted address is checked against it —
«29 emitted — the site states no total; the pager bounds 16–30; 29 of 29 in
the job sitemap (60 addresses, the archive)».

THE ADVERT (`/offres-emploi/<slug>/`, 200, ~237 KB of Divi): the title in
`.et_pb_text_0_tb_body`; `.acf-offre-infos` — «Type de contrat», «Nombre de
postes», «Référence», a «Document offre» PDF under `/wp-content/uploads/`;
the information column — `.offre-ville` (the region), a Cloudflare-protected
e-mail (never decoded, never emitted), «Date d'expiration : dd/mm/yyyy», the
«Postuler» link (never emitted); the description in `.et_pb_code_2_tb_body`;
JSON-LD WebPage / BreadcrumbList / WebSite / Organization — `datePublished`
read from the WebPage node, **no JobPosting**. The employer is NOT on the
advert page (the listing card carries it — `list` does). A slug the site
does not have answers 404 (exit 3). The REST collection
`/wp-json/wp/v2/offre_emploi` answers too (ten an answer, the archive with
its expired adverts, no expiry field) — not the route.

WITHHELD: the applicant's e-mail (protected by the host, and scrubbed
wherever it appears in text) and every telephone number; the «Postuler»
link; the employer's logo; `contacts_withheld` on every record. Country CD
on every row.
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD, HOST, COUNTRY = "talacom", "www.tala-com.com", "CD"
BASE = f"https://{HOST}"
LISTING = BASE + "/offres-demploi/"
SITEMAP = BASE + "/offre_emploi-sitemap.xml"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE = 15
MAX_PAGES = 200

CARD_RE = re.compile(r'<article class="emploi-item">(.*?)</article>', re.S)
LINK_RE = re.compile(r'<a class="emploi-link" href="(https://www\.tala-com\.com/offres-emploi/([^/"]+)/)"')
FIELD_RE = {
    "company": re.compile(r'<h3 class="emploi-title">(.*?)</h3>', re.S),
    "region": re.compile(r'<div class="emploi-adresse">(.*?)</div>', re.S),
    "title": re.compile(r'<div class="emploi-poste">(.*?)</div>', re.S),
    "contract": re.compile(r'<div class="emploi-horaires">(.*?)</div>', re.S),
}
PAGER_RE = re.compile(r'<div class="talacom-pagination">(.*?)</div>\s*</div>', re.S)
PAGE_NUM_RE = re.compile(r'class="page-numbers[^"]*"[^>]*>(\d+)<')
LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
AD_TITLE_RE = re.compile(r'et_pb_text_0_tb_body[^>]*>\s*<div class="et_pb_text_inner">(.*?)</div>', re.S)
INFOS_RE = re.compile(r'<div class="acf-offre-infos">(.*?)</div>', re.S)
INFO_RE = re.compile(r"<strong>\s*([^<:]+?)\s*:?\s*</strong>\s*:?\s*([^<]*)")
DOC_RE = re.compile(r"href='(https://www\.tala-com\.com/wp-content/uploads/[^']+)'[^>]*>\s*Document offre")
VILLE_RE = re.compile(r'<span class="offre-ville">\s*(?:<span class="marker-icon">\s*</span>)?\s*([^<]+)', re.S)
EXPIRY_RE = re.compile(r"Date d'expiration\s*:\s*(?:</[^>]+>\s*)*(\d{2}/\d{2}/\d{4})")
DESC_RE = re.compile(r'et_pb_code_2_tb_body[^>]*>\s*<div class="et_pb_code_inner">(.*?)</div>\s*</div>\s*</div>\s*</div>', re.S)
LDJSON_RE = re.compile(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
FORM_RE = re.compile(r"https?://(?:forms\.gle|docs\.google\.com/forms)/\S+")   # the application form is the apply link
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[talacom] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """(status, body) — this host only, no query string, the guard first, 2 s apart."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != HOST or parts.query:
        die(f"{url}: not {HOST}, or a query string (refused in writing: /*?*) — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml", "Accept-Language": "fr"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font)\b[^>]*>", "", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    s = FORM_RE.sub("[application link withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def status_of(st, url):
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def parse_listing(body):
    """(cards, last_page) — last_page None when the page shows no pager."""
    cards = []
    for seg in CARD_RE.findall(body or ""):
        link = LINK_RE.search(seg)
        if not link:
            continue
        c = {"url": link.group(1), "slug": link.group(2)}
        for k, rx in FIELD_RE.items():
            m = rx.search(seg)
            c[k] = text(m.group(1)) if m else None
        cards.append(c)
    pager = PAGER_RE.search(body or "")
    nums = [int(x) for x in PAGE_NUM_RE.findall(pager.group(1))] if pager else []
    return cards, (max(nums) if nums else None)


def row(c):
    return {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{c['slug']}", "id": c["slug"], "url": c["url"],
            "title": c["title"], "company": c["company"], "region": c["region"], "contract": c["contract"], "contacts_withheld": True}


def cmd_list(a):
    seen, out, last = set(), [], None
    page = 1
    while page <= MAX_PAGES:
        url = LISTING if page == 1 else f"{LISTING}page/{page}/"
        st, body = request(url)
        status_of(st, url)
        cards, pager_last = parse_listing(body)
        if page == 1:
            if not cards and "emploi" not in (body or ""):
                die(f"{url}: no card and no listing shell in the answer — not the job section, or the page changed shape.", EXIT_PARTIAL)
            last = pager_last if pager_last else 1
        new = 0
        for c in cards:
            if c["slug"] not in seen:
                seen.add(c["slug"])
                out.append(row(c))
                new += 1
        if not cards or (page > 1 and new == 0):
            if page <= last:
                note(f"page {page} of {last}: {'no card' if not cards else 'only repeats'} — the pager promised more; stopped.")
            break
        if page >= last:
            break
        page += 1
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    lo, hi = (max(1, (last - 1) * PAGE + 1), last * PAGE) if last else (None, None)
    bound = f"the pager bounds {th(lo)}–{th(hi)}" if last else "no pager on the page"
    if last and not (lo <= n <= hi):
        bound += f" — {th(n)} is OUTSIDE it"
    tail = ""
    if not a.no_sitemap:
        st, body = request(SITEMAP)
        status_of(st, SITEMAP)
        locs = set(LOC_RE.findall(body or ""))
        if not locs:
            die(f"{SITEMAP}: no <loc> in the answer — not a sitemap.", EXIT_PARTIAL)
        missing = [r["url"] for r in out if r["url"] not in locs]
        tail = f"; {th(n - len(missing))} of {th(n)} in the job sitemap ({th(len(locs))} addresses, the archive with its expired adverts)"
        if missing:
            tail += " — absent from it: " + ", ".join(missing[:5]) + ("…" if len(missing) > 5 else "")
    note(f"{th(n)} emitted — the site states no total; {bound}{tail}.")
    if last and not (lo <= n <= hi):
        sys.exit(EXIT_PARTIAL)


def webpage_date(body):
    for raw in LDJSON_RE.findall(body or ""):
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        for node in d.get("@graph", [d]) if isinstance(d, dict) else []:
            if isinstance(node, dict) and node.get("@type") == "WebPage" and node.get("datePublished"):
                return node["datePublished"]
    return None


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = re.fullmatch(r"/offres-emploi/([^/]+)/?", parts.path or "")
    if parts.netloc.lower() != HOST or not m or parts.query:
        die(f"{a.url!r}: not a Tala-Com advert address (https://{HOST}/offres-emploi/<slug>/)")
    slug = m.group(1)
    url = f"{BASE}/offres-emploi/{slug}/"
    st, body = request(url)
    status_of(st, url)
    t = AD_TITLE_RE.search(body)
    infos = INFOS_RE.search(body)
    if not t or not infos:
        die(f"{url}: no advert title or no «acf-offre-infos» block in the page — not an advert, or the page changed shape.", EXIT_PARTIAL)
    fields = {}
    for k, v in INFO_RE.findall(infos.group(1)):
        fields[k.strip().lower()] = text(v)
    doc = DOC_RE.search(infos.group(1))
    ville = VILLE_RE.search(body)
    exp = EXPIRY_RE.search(body)
    desc = DESC_RE.search(body)
    posts = fields.get("nombre de postes")
    rec = {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{slug}", "id": slug, "url": url,
           "title": text(t.group(1)), "contract": fields.get("type de contrat"),
           "positions": int(posts) if posts and posts.isdigit() else posts,
           "reference": scrub(fields.get("référence")), "document_url": doc.group(1) if doc else None,
           "region": text(ville.group(1)) if ville else None,
           "expires": "-".join(reversed(exp.group(1).split("/"))) if exp else None,
           "posted": webpage_date(body),
           "description": (scrub(text(desc.group(1))) or "")[:20000] or None,
           "contacts_withheld": True}
    print(json.dumps(rec, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Tala-Com (DR Congo) — the job section walked page by page to its pager; the advert's labelled block and text; no contact. Issue #339.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="/offres-demploi/ then /page/N/ to the pager's last page; «N emitted — the site states no total; the pager bounds a–b»")
    s.add_argument("--no-sitemap", action="store_true", help="do not read the job sitemap as the second witness")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advert by its address; the text scrubbed, the apply link and e-mail withheld")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
