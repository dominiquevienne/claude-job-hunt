# Chile — the public-sector portals, and why none of them has an adapter

<!-- verified: 2026-09-03 -->
<!-- hosts: sence.gob.cl, www.trabajaenelestado.cl, www.practicasparachile.cl, directoresparachile.cl, adp.serviciocivil.cl, www.empleospublicos.cl -->

Five Chilean portals were assessed for an adapter on 2026-09-03. **None of
them yields one, and each fails for a different reason.** This card exists so
the next person does not spend the day finding that out again — and so that
"no adapter" is never read as "nobody looked".

**Chile is covered**: `bne-cl.md` reads 7 928 advertisements from the Bolsa
Nacional de Empleo, which is the national board and the one every portal below
points people at.

## The five, and the layer each one stops at

| portal | what stops it |
|---|---|
| `sence.gob.cl` | **not a job board** |
| `directoresparachile.cl` | `User-agent: * / Disallow: /` |
| `adp.serviciocivil.cl` | `User-agent: * / Disallow: /` |
| `www.trabajaenelestado.cl` | 403 on its own rules file |
| `www.practicasparachile.cl` | its data belongs to a host that refuses |

### `sence.gob.cl` — the training service, not a board

SENCE is the *Servicio Nacional de Capacitación y Empleo*, and the
capacitación half is what it publishes: courses, subsidies, benefits. Its
robots.txt is an ordinary Drupal one — 36 path refusals to `*`, nothing
blanket, `Crawl-delay: 10`.

**But `/personas/buscaempleo`, its page for jobseekers, links out**: to
`bne.cl` — already covered — and to `empleospublicos.cl`. **There is nothing
here to adapt.** Writing one anyway would have produced a "board" returning
training courses, which is worse than none: it would look like ads and count
like ads.

### `directoresparachile.cl` and `adp.serviciocivil.cl` — closed, evenly

Both publish `User-agent: * / Disallow: /`. **A refusal aimed at everyone, not
at a named crawler**, and the intention behind it does not change its effect.
Not swept. Nothing further was requested from either.

### `www.trabajaenelestado.cl` — 403, and the apex does not exist

`trabajaenelestado.cl` does not resolve at all; only the `www.` form does, as
a CloudFront alias. Its `/robots.txt` answers **403 with 111 bytes of S3
`AccessDenied`** — with browser headers, so this is not header sniffing.

Under this repository's rule a 403 is a refusal, **which departs from RFC 9309
§2.3.1.3 on purpose** (`_robots.py` says why). The guard reports that this
particular 403 carries an object-storage error document, so the file may
simply be absent from the bucket — **a hint, not a finding.** It stays refused.

**And the pair below it is the argument for reading these one host at a time**:
`www.practicasparachile.cl` is the *same* stack with the *same* missing file,
and answers 200 with its own SPA shell because its distribution has a custom
error page. Same absence, opposite HTTP status.

### `www.practicasparachile.cl` — open, readable, and still not ours

The one of the five that passes the guard. Its `/robots.txt` returns the site's
own 16 kB HTML shell, so no rules were read; **an unreadable file is not a
refusal**, and the verdict permits.

`convocatorias.html` carries no offers. The listing is fetched by the page
from **`apisqa.empleospublicos.cl`**, an Elasticsearch `_search` endpoint, and
that host publishes no robots.txt either.

**That is where it stops.** `www.empleospublicos.cl` and `empleospublicos.cl`
— the operator of that data — publish **`User-agent: * / Disallow: /`**.
Reading the same records through an API host that merely omits a rules file
would be **choosing the host that says yes**, which this repository already
refuses to do: `icims.py` warns aloud when an employer's two hosts disagree,
precisely so that the convenient one is never picked quietly.

**The refusal is the operator's, and it is the whole reason.** The endpoint's
own state is a separate matter and is not a licence — see below.

## One thing to report to the operator, not to build on

The `_search` endpoint is reached with a header the page hardcodes as
`X-API-KEY: cambia-este-token` — *"change this token"* — and the page sends a
Painless `_script` sort in its query body, so the proxy forwards arbitrary
query DSL from the public internet.

**Nothing here was probed beyond reading the page's own source.** No request
was sent to that endpoint. It is recorded because a site's own placeholder,
visible in its published HTML, is worth telling its owner about — and because
an adapter built on it would rest on something that is going to change.

**It is not the reason there is no adapter.** The reason is one line above:
the operator says `Disallow: /`.
