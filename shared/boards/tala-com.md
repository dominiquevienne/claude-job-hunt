# Assessed, adapter not built — Tala-Com (DR Congo)

<!-- verified: 2026-09-08 -->

<!-- hosts: www.tala-com.com -->
<!-- script: none -->
<!-- countries: CD -->
<!-- content: measured · 31 live advertisements under `/offres-demploi/`, read in a browser across the three pages the site paginates — 15 + 15 + 1, no address repeated between pages · 2026-09-08 -->
<!-- witness: none — the site publishes no total anywhere on the listing; the pagination `1 2 3` is the only external anchor, and it bounds the count without stating it · 2026-09-08 -->

**A national board in a country of a hundred million people, and it refused our
client at the transport for three days.**

## The refusal targets our client, not every visitor

*This is the question the 2026-09-07 decision calls borne zero, and a browser
answers it in one request.*

```
python3 bin/fetch-body.py https://www.tala-com.com/...
   -> HTTP 403, 25 bytes, md5 9ccabba20b9f4ec7d18bd6644579e5bf
      body: b'Your request was blocked.'   (a shared provider default —
      www.hays.fr and three others serve the same 25 bytes)

a real browser, same path, 2026-09-08
   -> the page renders, 15 advertisements, no challenge of any kind
```

**The rules permit and the firewall refuses**, so under the 2026-09-07 decision
this was a browser candidate. **The browser answers the question the fingerprint
could not: the refusal is aimed at the simple client, not at every visitor.**

*Borne 2 is not strained here — **no antirobot control was presented and none
was defeated.** The page simply loaded.*

**And access is per session.** *One session was refused navigation to this
domain outright; two others reached it.* **A refusal in one session is not a
property of the host**, and it is not borrowed from another session either.

## This host is NOT a job board, and that is the first thing to know

`www.tala-com.com` is a **hub**: a company directory, brand promotions, public
**tenders**, events, and classified ads — *and its classifieds carry outright
scam listings.* **An adapter that swept this host would emit those as
vacancies.**

> **Only `/offres-demploi/` is the employment section.** *Anything built here
> targets that path and nothing else* — this is `appels-doffres-melanges-aux-annonces`
> on a host where nobody had looked for it.

## What the employment section holds

```
page 1   15 advertisements
page 2   15
page 3    1
         --
         31   no address repeated between pages
```

**Each card carries employer, city and contract type** — `CDD`, `CDI`, or
`autres`, in the board's own doubled form `CDD|CONTRAT A DUREE DETERMINEE (CDD)`.

**The employers are real and mostly humanitarian**: ACTED, Action contre la
Faim, Mercy Corps, INTERSOS, Handicap International, Médecins du Monde, COOPI,
ADRA, Fondation Mérieux — beside commercial ones (HSD Solutions, D-Pro
Services, Multi Task Company, Prodimpex, Pullman Kinshasa).

## The site declares no total, and that is a gap worth naming

**Nothing on the listing states how many advertisements exist.** The pagination
`1 2 3` bounds the count without stating it, and 31 is *our* count of *our*
extraction.

> **So an adapter here would have no anchor outside its own reader** — issue
> #181's exact shape. *A broken extractor would report zero, and the only thing
> contradicting it would be the pagination still showing three pages.*

**That is a weaker anchor than a declared total, and it is the one available.**
*Naming the gap is what this card can do; inventing a total is not.*

## What this card does not establish

- **no advertisement page was opened** — the fields above are the listing's;
- **no dates**: neither posting nor deadline appears on the listing, and
  whether the advertisement pages carry them was not checked;
- **nothing about the rest of the host**, beyond that it exists and must not be
  swept;
- **no adapter is built.** *Reading this board needs the browser, and whether
  that is a shape this repository wants is a decision, not a measurement.*
