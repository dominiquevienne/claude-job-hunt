# Board measurement — Maliemploi (`maliemploi.org`, Mali): served to our client today, and every path is the front page — seven posts, no addresses, a one-item feed

<!-- verified: 2026-09-12 -->

<!-- hosts: maliemploi.org, www.maliemploi.org -->
<!-- script: none -->
<!-- countries: ML -->
<!-- content: measured · **7 job posts on the front page** (6 «Publié il y a 1–2 jours», 1 «18 heures»; 5 CDI, 2 Stage; all Bamako), and no other page exists to read — `/robots.txt`, `/wp-json/wp/v2/types` and `/` answer the same 193 913-byte document (md5 `9978fa37…`), the RSS feed holds one item, «Hello world!»; four requests with the declared client, all HTTP 200 · 2026-09-12 -->
<!-- witness: none — the site states no count and links every post to `/`; the seven were counted by the «Publié il y a» stamps on the one page the site serves · 2026-09-12 -->

**Mali's named board, in the #222 candidate list as «403 Apache
intermittent» from the country page** — *four requests with the declared
client on 2026-09-12 12:17 UTC, four HTTP 200; no refusal was met, so no
browser was opened.* What was met instead decides the rest of this card.

## What the host serves — the same page on every path

```
GET /                       200, 193 913 B, md5 9978fa37a742a4f71d599513206d8fc2 — WordPress 7.1, «Job» theme, French
GET /robots.txt             200, 193 913 B, the same md5 — the guard reads it as `unrecognised` and permits by absence (certain: False)
GET /wp-json/wp/v2/types    200, 193 913 B, the same md5
GET /?feed=rss2             200, 1 794 B — one <item>: «Hello world!», the WordPress default post, link /?p=1
```

**Every path is the front page.** *A catch-all this complete means there
is no listing page, no post page and no API to find: the seven cards on
the front page link to `/` (42 of 42 internal links), and the feed knows
one post that is not a job.* The «403 intermittent» of the country page was
not reproduced in four requests; the failure this host actually has is
that it serves nothing but one document.

## The seven posts

```
AVIS DE RECRUTEMENT – BAMAKO               CDI     Bamako   il y a 18 heures   (20 places, 2 500 FCFA/jour, apply by WhatsApp)
Stagiaire Santé – Sécurité au Travail      Stage   Bamako   il y a 1 jour
Stagiaire Comptable                        Stage   Bamako   il y a 1 jour
Comptable clients et fournisseurs          CDI     Bamako   il y a 1 jour
Agent de Gardiennage et de Surveillance    CDI     Bamako   il y a 1 jour
Ingénieur Génie Civil                      CDI     Bamako   il y a 1 jour
APPEL A CANDIDATURE                        CDI     Bamako   il y a 2 jours
```

Each card carries title, contract type, city, a relative date and the
body; three carry an employer's e-mail in the body (`sandvik.com`,
`neutron-mali`, `sa-i.com`). **No stable id exists**: no URL, no post id in
the markup read, and the relative date moves. A row here would be keyed on
the title alone, which is not an identifier.

## What an adapter would be, and why none is built

*Reading the front page and cutting it into cards is a two-request
adapter; keying its rows is the problem.* **Without an address per post
the ledger cannot say «seen before», and without a second page the count
is whatever fits on one front page** — 7 today, all posted within two days,
which is either the whole board or its newest slice, and the site cannot
say which. **The finding is the catch-all, and it is dated**: a WordPress
whose permalinks resolve to the front page is a configuration, and the day
it is fixed the addresses appear and this card is re-measured — the first
line to run is `GET /wp-json/wp/v2/types` and whether it returns JSON.

## What this card does not establish

- **Whether the 403 of the country page ever occurs** — not in four
  requests; «intermittent» is the country page's word.
- **Whether the seven are the whole board** — no second page, no count.
- **The browser route** — not opened: nothing refused the client, and a
  tab would be served the same single document.
