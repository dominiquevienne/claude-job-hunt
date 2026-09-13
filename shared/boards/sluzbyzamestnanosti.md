# Board adapter — Služby zamestnanosti (Slovakia): the public employment service's board, read by the JSON search its own page calls — 12 126 advertisements of the state's own store, equal to the answer's own count, beside 13 437 republished from the private portals

<!-- verified: 2026-09-13 -->

<!-- hosts: www.sluzbyzamestnanosti.gov.sk, sluzbyzamestnanosti.gov.sk, www.upsvr.gov.sk, upsvr.gov.sk -->
<!-- script: sluzbyzamestnanosti.py -->
<!-- countries: SK -->
<!-- content: measured · rules read twice and certain on both hosts (`upsvr.gov.sk` 24 B, `Disallow:` empty; `sluzbyzamestnanosti.gov.sk` 52 B, one refusal `/pracovne-ponuky/*/reagovat`; no agent named; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: the ÚPSVaR's «Voľné pracovné miesta» links to `sluzbyzamestnanosti.gov.sk/pracovne-ponuky`, a server-rendered page whose script calls `GET /search/ponuky?pageNr=N&pageSize=100[&zdrojPonuky=VPM]` — JSON with the site's own `countVPM` beside the rows: **25 563** advertisements in all (8 955 employers, 150 248 positions), **12 126 the state's own** (`zdrojPonuky=VPM`, 122 pages walked 18:20–18:22 UTC — «12 126 emitted, site states 12 126 — equal»), the rest republished from profesia.sk, kariera.sk, worki.sk, eures.sk and the Fajn group with a link out to each; the state's advertisement page is a `<dl>` of forty fields ending in a «Kontaktná osoba» section, never read · 2026-09-13 18:22 UTC -->
<!-- witness: the search answer's own `countVPM` for the store asked (12 126 for `zdrojPonuky=VPM`, 25 563 for all sources, 2026-09-13 18:2x UTC) beside the rows walked — «12 126 emitted, site states 12 126 — equal», printed by `sluzbyzamestnanosti.py list`; the page's server-rendered «25 563 pracovných ponúk, 8 955 zamestnávateľov, 150 248 pracovných miest» says the same figures; positions are never compared to advertisements -->

**Shipped 2026-09-13 under #342 — Slovakia's public inventory, the one no
private board republishes (the reverse is true: the state republishes
theirs).** Every fetch under the declared identity, the guard on the exact
path first, on both hosts. *Page Slovaquie of 2026-09-01 read the
ÚPSVaR's 24-byte file and wrote «no sitemap declared, an adapter would
walk the search»; the search is on another host, and it is JSON.*

```
sluzbyzamestnanosti.py list                   # the state's own store — 12 126 on 2026-09-13, 122 pages of 100 at 1 s, ~2 min
sluzbyzamestnanosti.py list --source all      # + the republished private boards — 25 563; 256 pages
sluzbyzamestnanosti.py ad --url https://www.sluzbyzamestnanosti.gov.sk/pracovne-ponuky/<uuid>
```

## The rules — two hosts, seventy-six bytes, one refusal

```
www.upsvr.gov.sk/robots.txt                  24 B, md5 b6216d61c03e — `User-agent: *` / `Disallow:` (empty): everything allowed; no Sitemap line
www.sluzbyzamestnanosti.gov.sk/robots.txt    52 B, md5 4e33f915bd11 — `User-agent: *` / `Disallow: /pracovne-ponuky/*/reagovat` (the apply action); no Sitemap line
identity("/")   http, claude-user on both — no agent named
verdict()       sweep True, certain True, crawl_delay none  -> Pace(HOST, own=1.0), one second, ours
allowed()       True on `/pracovne-ponuky`, `/search/ponuky?…`, `/pracovne-ponuky/<uuid>` — **False on `/pracovne-ponuky/<uuid>/reagovat`**, never requested
/sitemap.xml    on the board host: a Keycloak login page («Prihlásenie do vpm-realm», 30 583 B, 200) — not an index
```

## The ÚPSVaR points, the board answers

| question | answer (2026-09-13, 18:13–18:22 UTC) |
| :-- | --: |
| `www.upsvr.gov.sk/volne-pracovne-miesta.html` | 200, 46 463 B — the office's own vacancies and one line, «Vyhľadávanie pracovných ponúk - Služby zamestnanosti (gov.sk)» → `https://www.sluzbyzamestnanosti.gov.sk/pracovne-ponuky` |
| `/pracovne-ponuky` | 200, 118 007 B — server-rendered: «25 563 pracovných ponúk, 8 955 zamestnávateľov, 150 248 pracovných miest», 12 cards (all profesia.sk that hour), and a script that calls the JSON search for every page and filter |
| `GET /search/ponuky?pageNr=N&pageSize=100` | JSON — `countVPM`, `countZamestnavatelia`, `countPocetVolnychMiest`, `pageNr`, `pageSize`, `pracovnePonuky[]`; `pageSize=100` honoured, `pageNr=200` served |
| `zdrojPonuky=VPM` — the state's own store | **12 126** (`countVPM`), 5 324 employers, 128 448 positions; `priznakZdroj` 1 «úrad PSVR» 11 950, 2 «Portál SZ» 176; 11 910 with a salary |
| the six sources the page filters on | Portál SZ (`VPM`), profesia.sk (3), Fajn skupina (5), kariera.sk (1), eures.sk (4), worki.sk (2) — the external rows carry `urlExternyPortal` (`https://www.profesia.sk/O5354102`) and **no page on this host** |
| a row | `uuid` (the key: `sz:<uuid>`), `nazovPracovnehoMiesta`, `zamestnavatelObchodneMeno`, `miestoVykonuPrace` («Skalica - Skalica»), `zakladnaMzda` 1200.0 + `MESIAC`, `naposledyZmenene`, `priznakZdroj`, `externyPortal`, `urlExternyPortal` |

**The state's store is the default, and it is the inventory that matters
here**: the 13 437 republished rows are read at their source by
`profesia.py` and the others; the adapter says how many of each it
emitted. **The witness comes with the rows** — the answer's own `countVPM`
for the store asked — and the adapter still prints both apart; a bounded
walk is a lower bound, not compared; the 150 248 «positions» are never
compared to advertisements.

## The advertisement page — forty `<dl>` fields, and a section that is cut before reading

`/pracovne-ponuky/7f97c15a-…` (45 214 B, server-rendered, no JSON-LD):
«Údaje o pracovnej pozícii» (Názov pracovnej pozície, Profesia SK ISCO-08
«2151001 - Špecialista elektrotechnik technológ», Pracovná oblasť, Počet
voľných miest, Náplň práce), «Pracovné podmienky» (Miesto výkonu práce —
the `location_on` / Google-maps tail stripped —, Pracovný a mimopracovný
pomer, Zmennosť, Základná zložka mzdy «4 500 € mesačne», Dátum nástupu),
«Požiadavky na zamestnanca», «Údaje o zamestnávateľovi» (Názov
spoločnosti, IČO, Internetová adresa, Počet zamestnancov), «Zabezpečenie
obsadenia» — and **«Kontaktná osoba»: the page is cut at that heading
before any field is read**, so a name, a phone or an address there never
reaches a field (tested with a contact «Internetová adresa» that would
otherwise fill `employer_site`). `Id VPM` and `Zdroj` («úrad PSVR») are
kept. No `mailto:`, no `tel:` in the served page.

## What the adapter does, and refuses to do

- **122 JSON requests at 1 s** for the state's store (256 for all); a
  non-200 or a non-JSON page is a partial walk (exit 6), no count printed.
- **Never requests `/reagovat`**, never reads past «Kontaktná osoba».
- **Never compares positions to advertisements**, nor a bounded walk.
- **Not a verdict that anything is closed** — the state opens its store to
  everyone in 52 bytes.

## Tests

`TheStatesOwnStoreByDefaultTheRepublishedOnRequestAndTheContactSectionNeverRead`
in `tests/test_core.py` — two cases (the state's store asked by default
and keyed by uuid, an external row linked to its portal, the answer's
count as the witness with positions never compared, `--source all` and a
bounded walk not compared; the `<dl>` read with the place's map tail
stripped and the contact section cut before reading, a portal URL
refused). Six mutations under `python3 -B` on a detached copy, six reds:
the `VPM` parameter dropped, the dedup removed, the external row linked
here, the positions figure compared, the contact cut dropped (*green on a
first fixture whose contact section carried no label of the adapter's —
the fixture, not the guard; it now carries an «Internetová adresa»*), the
`location_on` tail kept.

## Provenance

- `up/robots.txt`, `up/volne-pracovne-miesta_….html`, `up/sz-robots.txt`,
  `up/sz-root.html`, `up/sz-sitemap.xml` (the login page), `up/sz-list.html`,
  `up/sz-widgets.js`, `up/sz-p2.html` (the first JSON answer), `up/sz-q-*.json`,
  `up/sz-vpm.json`, `up/sz-ad.html` — 2026-09-13 18:13–18:19 UTC,
  `bin/fetch-body.py`, provenance beside each; scratchpad of `claude-job-hunt-ab`.
- `sluzbyzamestnanosti.py list` at 18:20:16 → 18:22:20 UTC: 12 126 lines,
  the two `[sluzbyzamestnanosti]` lines quoted above verbatim.
