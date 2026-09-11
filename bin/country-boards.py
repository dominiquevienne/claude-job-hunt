#!/usr/bin/env python3
"""What a country page must carry, generated from the repository alone — #195.

    bin/country-boards.py CH                    Markdown, the page's board table + the five numbers
    bin/country-boards.py FR --html             the same content as an HTML fragment, to paste into the artefact
    bin/country-boards.py --all --members FILE  one line per Atlas member: cards · adapters · none · to re-verify

**It reads `shared/boards/`, never the network** (#195, conduct 3: the campaign
puts in shape what is known; a fresh measurement is another issue). Every
figure it prints comes from a header line a card DECLARES — `countries:`,
`script:`, `content:`, `verified:`, `robots:`, `override:` — or from a refusal
the card records with its date. **What a card only says in prose is invisible to
this view, and the script says how many cards are invisible to it** (no
`countries:` line): the declaration of hosts as `hosts:` lines is #195 ⑤, the
owner's decision, not this script's.

THE FIVE NUMBERS, AND WHY NOT TWO — #195, 2026-09-08 14:08

    fait                a script exists (`script:` names a .py)
    faisable ÉTABLI     no script, a dated measurement, no refusal recorded
    INDÉTERMINÉS        no script, a refusal recorded WITH its date — named one by one
    à REVÉRIFIER        no script and no date, or a refusal with no date (#195 ①: an
                        undated «not feasible» is not a denominator, it is a re-check)
    écartés VALIDÉS     only what the owner validated (§2 sexies) — no card declares
                        such a validation today, so this is 0 and says so
    écartés NON validés a `Disallow: /` written to `*` (bound 1), or a name with no
                        delegation on two resolvers — a closure no route crosses,
                        counted apart, out of «faisable», in «total», named, and
                        still the owner's to validate
    total               every card declaring the country

    fait / faisable   = fait / (fait + faisable établi)   — routes licites exercées
    fait / total      = fait / total                        — indéterminés et à revérifier compris

**The denominator is our list, not the market** (#195 ②) — one fixed sentence,
printed on every page. And boards declared `countries: *` (worldwide meta-boards)
are listed apart and counted apart: they carry no country code, so «one row per
card whose `countries:` carries the country» does not include them, and folding
them into the ratio would add the same 25 rows to 186 pages.
"""

import argparse
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARDS = os.path.join(ROOT, "shared", "boards")

HEADER = re.compile(r"^<!--\s*([a-z-]+):\s*(.*?)\s*-->\s*$", re.M)
DATE = re.compile(r"(20\d\d-\d\d-\d\d)")
# a refusal the card records: an HTTP 403/401/429/451 with its date on the same
# line or in the same paragraph, and the tool when it is named
REFUSAL = re.compile(r"(?:HTTP\s*)?\b(403|429|451)\b")
TOOL = re.compile(r"(fetch-body\.py|_robots\.allowed|curl|browser|navigateur|a real browser)")

NOTICE = ("Le dénominateur est la liste de boards que ce relevé a établie, à sa "
          "date. Ce n'est pas le marché du pays.")

# ISO 3166-1: alpha-3 -> alpha-2, for `--all` over an Atlas member file that
# speaks alpha-3 while the cards speak alpha-2. A member the table does not
# know is printed as UNMAPPED, never as zero cards.
ISO3_TO_2 = {
 "AFG":"AF","ALA":"AX","ALB":"AL","DZA":"DZ","ASM":"AS","AND":"AD","AGO":"AO","AIA":"AI","ATA":"AQ","ATG":"AG",
 "ARG":"AR","ARM":"AM","ABW":"AW","AUS":"AU","AUT":"AT","AZE":"AZ","BHS":"BS","BHR":"BH","BGD":"BD","BRB":"BB",
 "BLR":"BY","BEL":"BE","BLZ":"BZ","BEN":"BJ","BMU":"BM","BTN":"BT","BOL":"BO","BES":"BQ","BIH":"BA","BWA":"BW",
 "BVT":"BV","BRA":"BR","IOT":"IO","BRN":"BN","BGR":"BG","BFA":"BF","BDI":"BI","CPV":"CV","KHM":"KH","CMR":"CM",
 "CAN":"CA","CYM":"KY","CAF":"CF","TCD":"TD","CHL":"CL","CHN":"CN","CXR":"CX","CCK":"CC","COL":"CO","COM":"KM",
 "COG":"CG","COD":"CD","COK":"CK","CRI":"CR","CIV":"CI","HRV":"HR","CUB":"CU","CUW":"CW","CYP":"CY","CZE":"CZ",
 "DNK":"DK","DJI":"DJ","DMA":"DM","DOM":"DO","ECU":"EC","EGY":"EG","SLV":"SV","GNQ":"GQ","ERI":"ER","EST":"EE",
 "SWZ":"SZ","ETH":"ET","FLK":"FK","FRO":"FO","FJI":"FJ","FIN":"FI","FRA":"FR","GUF":"GF","PYF":"PF","ATF":"TF",
 "GAB":"GA","GMB":"GM","GEO":"GE","DEU":"DE","GHA":"GH","GIB":"GI","GRC":"GR","GRL":"GL","GRD":"GD","GLP":"GP",
 "GUM":"GU","GTM":"GT","GGY":"GG","GIN":"GN","GNB":"GW","GUY":"GY","HTI":"HT","HMD":"HM","VAT":"VA","HND":"HN",
 "HKG":"HK","HUN":"HU","ISL":"IS","IND":"IN","IDN":"ID","IRN":"IR","IRQ":"IQ","IRL":"IE","IMN":"IM","ISR":"IL",
 "ITA":"IT","JAM":"JM","JPN":"JP","JEY":"JE","JOR":"JO","KAZ":"KZ","KEN":"KE","KIR":"KI","PRK":"KP","KOR":"KR",
 "KWT":"KW","KGZ":"KG","LAO":"LA","LVA":"LV","LBN":"LB","LSO":"LS","LBR":"LR","LBY":"LY","LIE":"LI","LTU":"LT",
 "LUX":"LU","MAC":"MO","MDG":"MG","MWI":"MW","MYS":"MY","MDV":"MV","MLI":"ML","MLT":"MT","MHL":"MH","MTQ":"MQ",
 "MRT":"MR","MUS":"MU","MYT":"YT","MEX":"MX","FSM":"FM","MDA":"MD","MCO":"MC","MNG":"MN","MNE":"ME","MSR":"MS",
 "MAR":"MA","MOZ":"MZ","MMR":"MM","NAM":"NA","NRU":"NR","NPL":"NP","NLD":"NL","NCL":"NC","NZL":"NZ","NIC":"NI",
 "NER":"NE","NGA":"NG","NIU":"NU","NFK":"NF","MKD":"MK","MNP":"MP","NOR":"NO","OMN":"OM","PAK":"PK","PLW":"PW",
 "PSE":"PS","PAN":"PA","PNG":"PG","PRY":"PY","PER":"PE","PHL":"PH","PCN":"PN","POL":"PL","PRT":"PT","PRI":"PR",
 "QAT":"QA","REU":"RE","ROU":"RO","RUS":"RU","RWA":"RW","BLM":"BL","SHN":"SH","KNA":"KN","LCA":"LC","MAF":"MF",
 "SPM":"PM","VCT":"VC","WSM":"WS","SMR":"SM","STP":"ST","SAU":"SA","SEN":"SN","SRB":"RS","SYC":"SC","SLE":"SL",
 "SGP":"SG","SXM":"SX","SVK":"SK","SVN":"SI","SLB":"SB","SOM":"SO","ZAF":"ZA","SGS":"GS","SSD":"SS","ESP":"ES",
 "LKA":"LK","SDN":"SD","SUR":"SR","SJM":"SJ","SWE":"SE","CHE":"CH","SYR":"SY","TWN":"TW","TJK":"TJ","TZA":"TZ",
 "THA":"TH","TLS":"TL","TGO":"TG","TKL":"TK","TON":"TO","TTO":"TT","TUN":"TN","TUR":"TR","TKM":"TM","TCA":"TC",
 "TUV":"TV","UGA":"UG","UKR":"UA","ARE":"AE","GBR":"GB","USA":"US","UMI":"UM","URY":"UY","UZB":"UZ","VUT":"VU",
 "VEN":"VE","VNM":"VN","VGB":"VG","VIR":"VI","WLF":"WF","ESH":"EH","YEM":"YE","ZMB":"ZM","ZWE":"ZW",
 # Atlas members outside ISO 3166-1, with the codes the Atlas uses on the
 # alpha-3 side. Kosovo's cards declare `XK`; Northern Cyprus and Somaliland
 # have no alpha-2 any card declares — they map to their own alpha-3, so a
 # card that one day declares `CYN` or `SOL` is found, and until then they
 # count zero cards, which is a fact about the cards and not an UNMAPPED.
 "KOS":"XK", "XKX":"XK", "CYN":"CYN", "SOL":"SOL",
}


def read_cards(boards_dir):
    """Every card, README excluded — it carries three `countries:` lines of
    example and would enter its own count (memory:
    un-fichier-dexemples-entre-dans-son-propre-compte)."""
    out = []
    for path in sorted(glob.glob(os.path.join(boards_dir, "*.md"))):
        if os.path.basename(path).upper() == "README.MD":
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        h = {}
        for m in HEADER.finditer(text):
            h.setdefault(m.group(1), m.group(2))
        out.append({"name": os.path.basename(path)[:-3], "path": path,
                    "text": text, "h": h})
    return out


def date_of(value):
    m = DATE.findall(value or "")
    return m[-1] if m else None


def refusal_of(card):
    """The refusal a card records — status, date, tool — read from the lines
    that carry a 403/429/451, never from the header. `None` when the card
    records none."""
    best = None
    for line in card["text"].splitlines():
        m = REFUSAL.search(line)
        if not m or "robots.txt" in line and "200" in line:
            continue
        d = date_of(line)
        t = TOOL.search(line)
        cand = {"status": m.group(1), "date": d, "tool": t.group(1) if t else None,
                "line": line.strip()[:160]}
        # prefer a dated one, then one naming a tool
        if best is None or (cand["date"] and not best["date"]) or \
           (cand["date"] == best["date"] and cand["tool"] and not best["tool"]):
            best = cand
    if best and not best["date"]:
        # a refusal line without a date takes the card's verified: date, and
        # says so — the date is the card's, not the refusal's
        v = card["h"].get("verified")
        if v:
            best["date"] = date_of(v)
            best["date_is_cards"] = True
    return best


WRITTEN_REFUSAL = re.compile(r"User-agent:\s*\*\s*\n\s*Disallow:\s*/\s*(?:\n|$)")
NO_DELEGATION = re.compile(r"\bNXDOMAIN\b")


def excluded_of(card):
    """A closure the card records that no route crosses — and that the owner
    has NOT validated (§2 sexies): a `Disallow: /` written to `*` (bound 1),
    or a name with no delegation on two resolvers. Returns (label, date) or
    None. Neither is INDÉTERMINÉ (nothing is missing to decide) and neither
    is faisable; they are counted apart, as «écartés NON validés»."""
    text = card["text"]
    if WRITTEN_REFUSAL.search(text):
        return "refus écrit dans les règles — `User-agent: * / Disallow: /` (borne 1)", \
            date_of(card["h"].get("verified", ""))
    if NO_DELEGATION.search(text):
        return "le nom ne résout pas — NXDOMAIN sur deux résolveurs", \
            date_of(card["h"].get("verified", ""))
    return None


def access_of(card):
    """What the card DECLARES about the route. Returns (label, basis)."""
    h = card["h"]
    if h.get("robots", "").strip() == "keyed-api":
        return "API à clé", "`robots: keyed-api`"
    if "override" in h:
        return "HTTP, dérogation robots", "`override:` — " + (date_of(h["override"]) or "sans date")
    x = excluded_of(card)
    if x and not (h.get("script", "").strip() not in ("", "none")):
        return x[0], "the card's own quotation of the rule, or of the DNS answer"
    if h.get("content", "").strip().lower().startswith("indeterminate"):
        # the card's declared word outranks any status its prose mentions
        return "indéterminé — " + re.sub(r"^indeterminate\s*·\s*", "",
                                         h["content"]).split(" · ")[0][:120], "`content: indeterminate`"
    r = refusal_of(card)
    script = h.get("script", "").strip()
    if r:
        tool = ("mention : " + r["tool"]) if r["tool"] else "outil non nommé"
        when = r["date"] or "sans date"
        if script and script != "none":
            return (f"HTTP ordinaire — et un {r['status']} consigné ({when}, {tool})",
                    r["line"])
        return f"refusé au client HTTP — {r['status']}, {when}, {tool}", r["line"]
    if script and script != "none":
        return "HTTP ordinaire (adaptateur)", "`script:` sans refus consigné"
    if re.search(r"\b(browser|navigateur)\b", card["text"], re.I):
        return "route navigateur (déclarée en prose)", "le mot dans la fiche"
    return "non déclaré", "aucune ligne de refus, aucun script"


def classify(card):
    """One of: fait · faisable · indetermine · reverifier."""
    h = card["h"]
    script = h.get("script", "").strip()
    measured = date_of(h.get("content", "")) or date_of(h.get("verified", ""))
    if script and script != "none":
        return "fait", measured
    if excluded_of(card):
        return "ecarte", measured
    if h.get("content", "").strip().lower().startswith("indeterminate"):
        # the card's own first word — `content: indeterminate · …` — is a
        # declaration, and it outranks any refusal line the prose carries
        return "indetermine", measured
    r = refusal_of(card)
    if r:
        if r.get("date") and not r.get("date_is_cards"):
            return "indetermine", measured or r["date"]
        if r.get("date"):
            return "indetermine", measured
        return "reverifier", measured
    if measured:
        return "faisable", measured
    return "reverifier", None


def covers(card):
    c = card["h"].get("countries", "").strip()
    if not c:
        return None
    return [x.strip() for x in re.split(r"[,\s]+", c) if x.strip()]


def rows_for(cards, iso2):
    own, world, undeclared = [], [], 0
    for c in cards:
        cs = covers(c)
        if cs is None:
            undeclared += 1
            continue
        if iso2 in cs:
            own.append(c)
        elif cs == ["*"]:
            world.append(c)
    return own, world, undeclared


def status_of(card, cls, measured):
    h = card["h"]
    script = h.get("script", "").strip()
    if cls == "fait":
        return f"adaptateur `{script}`"
    label = {"faisable": "mesuré sans adaptateur — faisable établi",
             "indetermine": "mesuré sans adaptateur — INDÉTERMINÉ",
             "ecarte": "écarté — NON validé par le propriétaire",
             "reverifier": "à REVÉRIFIER"}[cls]
    return label


def covers_text(card):
    c = card["h"].get("content", "")
    if not c:
        return "*(pas de ligne `content:`)*"
    c = re.sub(r"\s*·\s*20\d\d-\d\d-\d\d(?:T[\d:]+Z?)?\s*$", "", c)
    c = c.replace("|", "\\|")
    if len(c) > 220:
        c = c[:220].rsplit(" ", 1)[0] + "…"
        if c.count("`") % 2:          # never cut inside a code span
            c += "`"
    return c


def table(cards, iso2):
    own, world, undeclared = rows_for(cards, iso2)
    n = {"fait": 0, "faisable": 0, "indetermine": 0, "reverifier": 0, "ecarte": 0}
    lines = ["| Board | Ce qu'il couvre | Accès | Statut | Mesuré |",
             "| :-- | :-- | :-- | :-- | :-- |"]
    named_ind, named_rev, named_exc = [], [], []
    for c in own:
        cls, measured = classify(c)
        n[cls] += 1
        acc, _basis = access_of(c)
        lines.append(f"| `{c['name']}` | {covers_text(c)} | {acc} | "
                     f"{status_of(c, cls, measured)} | {measured or '—'} |")
        if cls == "indetermine":
            named_ind.append(c["name"])
        if cls == "reverifier":
            named_rev.append(c["name"])
        if cls == "ecarte":
            named_exc.append(c["name"])
    total = len(own)
    faisable = n["fait"] + n["faisable"]
    return {"lines": lines, "n": n, "total": total, "faisable": faisable,
            "world": world, "undeclared": undeclared,
            "named_ind": named_ind, "named_rev": named_rev,
            "named_exc": named_exc}


def render_md(iso2, t, all_cards):
    n = t["n"]
    out = [f"## Boards — {iso2}", "", *t["lines"], ""]
    if not t["total"]:
        out.append(f"*Aucune fiche de `shared/boards/` ne déclare `{iso2}` dans sa "
                   f"ligne `countries:`.*")
        out.append("")
    out += [
        "### Les cinq nombres, et les deux ratios",
        "",
        "```",
        f"fait              {n['fait']}     route livrée (`script:` nomme un .py)",
        f"faisable ÉTABLI   {n['faisable']}     mesuré, daté, aucun refus consigné",
        f"INDÉTERMINÉS      {n['indetermine']}     refus consigné avec sa date"
        + (f" — {', '.join(t['named_ind'])}" if t["named_ind"] else ""),
        f"à REVÉRIFIER      {n['reverifier']}     sans date, ou refus sans date"
        + (f" — {', '.join(t['named_rev'])}" if t["named_rev"] else ""),
        f"écartés VALIDÉS   0     aucune fiche ne déclare une exclusion validée par le propriétaire",
        f"écartés NON validés {n['ecarte']}   refus écrit à `*` (borne 1) ou nom sans délégation — hors de «faisable», dans «total», à valider (§2 sexies)"
        + (f" — {', '.join(t['named_exc'])}" if t["named_exc"] else ""),
        f"total             {t['total']}",
        "",
        f"fait / faisable   {n['fait']} / {t['faisable']}    (faisable = fait + faisable établi : routes licites exercées)",
        f"fait / total      {n['fait']} / {t['total']}    (total = toutes les fiches déclarant {iso2}, indéterminés, à revérifier et écartés compris)",
        "```",
        "",
        f"*{NOTICE}*",
        "",
    ]
    if t["world"]:
        out += [f"### Boards mondiaux (`countries: *`) — {len(t['world'])}, listés à part, "
                f"hors des deux ratios", "",
                ", ".join(f"`{c['name']}`" for c in t["world"]), ""]
    out.append(f"*Généré depuis `shared/boards/` — {len(all_cards)} fiches, README exclu ; "
               f"{t['undeclared']} sans ligne `countries:` sont invisibles à cette vue.*")
    return "\n".join(out)


def render_html(iso2, t, all_cards):
    n = t["n"]
    e = html.escape
    def md_cell(s):
        s = e(s).replace("\\|", "|")
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
        return s
    out = [f"<h2>Boards — {e(iso2)}</h2>", "<table>",
           "<thead><tr><th>Board</th><th>Ce qu'il couvre</th><th>Accès</th>"
           "<th>Statut</th><th>Mesuré</th></tr></thead><tbody>"]
    for line in t["lines"][2:]:
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        out.append("<tr>" + "".join(f"<td>{md_cell(c)}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table>")
    out.append("<h3>Les cinq nombres, et les deux ratios</h3><pre>")
    out.append(e(
        f"fait              {n['fait']}\nfaisable ÉTABLI   {n['faisable']}\n"
        f"INDÉTERMINÉS      {n['indetermine']}"
        + (f" — {', '.join(t['named_ind'])}" if t["named_ind"] else "") + "\n"
        f"à REVÉRIFIER      {n['reverifier']}"
        + (f" — {', '.join(t['named_rev'])}" if t["named_rev"] else "") + "\n"
        f"écartés VALIDÉS   0\nécartés NON validés {n['ecarte']}"
        + (f" — {', '.join(t['named_exc'])}" if t["named_exc"] else "") + "\n"
        f"total             {t['total']}\n\n"
        f"fait / faisable   {n['fait']} / {t['faisable']}    (faisable = fait + faisable établi)\n"
        f"fait / total      {n['fait']} / {t['total']}    (total = toutes les fiches déclarant {iso2})"))
    out.append("</pre>")
    out.append(f"<p><em>{e(NOTICE)}</em></p>")
    if t["world"]:
        out.append(f"<p>Boards mondiaux (<code>countries: *</code>) — {len(t['world'])}, "
                   f"listés à part, hors des deux ratios : "
                   + ", ".join(f"<code>{e(c['name'])}</code>" for c in t["world"]) + "</p>")
    out.append(f"<p><em>Généré depuis shared/boards/ — {len(all_cards)} fiches, README exclu ; "
               f"{t['undeclared']} sans ligne countries: sont invisibles à cette vue.</em></p>")
    return "\n".join(out)


def cmd_all(cards, members_path):
    """One line per member: cards · adapters · none · to re-verify — the
    denominator of the #195 campaign (conduct 1)."""
    per = {}
    undeclared = 0
    for c in cards:
        cs = covers(c)
        if cs is None:
            undeclared += 1
            continue
        if cs == ["*"]:
            continue
        cls, _m = classify(c)
        for iso2 in cs:
            d = per.setdefault(iso2, {"cards": 0, "fait": 0, "faisable": 0,
                                      "indetermine": 0, "reverifier": 0, "ecarte": 0})
            d["cards"] += 1
            d[cls] += 1
    if not members_path:
        print("# no --members FILE: the repository alone knows no list of Atlas "
              "members. Below, every ISO2 a card declares — the 186 denominator "
              "needs the members file (atlas-pages.txt shape: ISO3<TAB>name…).",
              file=sys.stderr)
        keys = sorted(per)
        print("iso2\tcards\tadapters\tnone\tindeterminate\tto_reverify\texcluded_unvalidated")
        for k in keys:
            d = per[k]
            print(f"{k}\t{d['cards']}\t{d['fait']}\t{d['faisable']}\t{d['indetermine']}\t{d['reverifier']}\t{d['ecarte']}")
        print(f"# {len(keys)} ISO2 declared · {undeclared} card(s) without countries: are invisible here",
              file=sys.stderr)
        return 0
    members = []
    with open(members_path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            members.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""))
    print("iso3\tiso2\tname\tcards\tadapters\tnone\tindeterminate\tto_reverify\texcluded_unvalidated")
    with_cards = with_adapter = unmapped = 0
    seen2 = set()
    for iso3, name in members:
        iso2 = ISO3_TO_2.get(iso3)
        if iso2 is None:
            unmapped += 1
            print(f"{iso3}\tUNMAPPED\t{name}\t?\t?\t?\t?\t?\t?")
            continue
        seen2.add(iso2)
        d = per.get(iso2, {"cards": 0, "fait": 0, "faisable": 0, "indetermine": 0, "reverifier": 0, "ecarte": 0})
        with_cards += d["cards"] > 0
        with_adapter += d["fait"] > 0
        print(f"{iso3}\t{iso2}\t{name}\t{d['cards']}\t{d['fait']}\t{d['faisable']}\t{d['indetermine']}\t{d['reverifier']}\t{d['ecarte']}")
    orphans = sorted(set(per) - seen2)
    print(f"# {len(members)} members · {with_cards} with at least one card · "
          f"{with_adapter} with at least one adapter · {unmapped} UNMAPPED (not zero: unknown) · "
          f"{undeclared} card(s) without countries: invisible · "
          f"{len(orphans)} ISO2 declared by cards and absent from the members file: "
          f"{', '.join(orphans) or 'none'}", file=sys.stderr)
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog=__doc__)
    p.add_argument("iso2", nargs="?", help="the country, ISO 3166-1 alpha-2 (CH, FR…)")
    p.add_argument("--html", action="store_true", help="an HTML fragment instead of Markdown")
    p.add_argument("--all", action="store_true", help="per-member counts over the Atlas members")
    p.add_argument("--members", help="members file for --all, atlas-pages.txt shape (ISO3<TAB>name…)")
    p.add_argument("--boards", default=BOARDS, help="the cards directory (default: shared/boards)")
    a = p.parse_args()
    cards = read_cards(a.boards)
    if a.all:
        return cmd_all(cards, a.members)
    if not a.iso2:
        p.error("give an ISO2 code, or --all")
    iso2 = a.iso2.strip().upper()
    t = table(cards, iso2)
    print(render_html(iso2, t, cards) if a.html else render_md(iso2, t, cards))
    return 0


if __name__ == "__main__":
    sys.exit(main())
