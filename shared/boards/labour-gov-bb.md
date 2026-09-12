# Board measurement — Ministry of Labour (Barbados): open, served, and NOT a board — its «Online Job Centre» page points to `barbadosjobregister.gov.bb`

<!-- verified: 2026-09-12 -->

<!-- hosts: labour.gov.bb, www.labour.gov.bb -->
<!-- script: none -->
<!-- countries: BB -->
<!-- content: measured · rules read twice and certain — 187 bytes, `*` refused nothing, `Crawl-delay: 10`, a WordPress sitemap index; `identity()` answers `claude-user`, `verdict()` sweeps — and the transport answers 200 at the root (the ministry's site) and at `/employment-services/online-job-centre/`, whose title is «Barbados Job Register» and whose only job link goes out to `https://barbadosjobregister.gov.bb/`: 0 advertisements on this host · 2026-09-12 11:21 UTC -->
<!-- witness: the page text and its outbound links — the register is another host, on #222's list (a 403 to the plain client, browser not measured); nothing to enumerate here -->

**Measured 2026-09-12 at 11:19:05Z UTC for #233, lot 4 — a measurement of
the transport, and a finding about the object.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`,
the host's `Crawl-delay: 10` honoured.

## The rules — nothing refused

```
robots.txt      read twice, certain: True, 187 B, md5 3e6823cb1af8 both times — `Crawl-delay: 10`, `User-agent: * / Disallow:` (empty), `Sitemap: /sitemap_index.xml`
identity("/")   http, claude-user
verdict()       sweep True
allowed("/employment-services/online-job-centre/") True
```

*#233 listed this host under «another managed block naming ClaudeBot»; the
file read today names nobody and refuses nothing — a 187-byte WordPress
default. Whatever was read on 2026-09-11 is not what the host serves on
2026-09-12, and the card records what it read.*

## The transport — 200, and the object is a ministry, not a board

```
GET https://labour.gov.bb/                                        200, 287 221 B, md5 1124d8b692ee   (11:19:05Z)  «Home - Government of Barbados Ministry of Labour», WordPress
GET https://labour.gov.bb/                                        200, 287 221 B, md5 76a8a3cfc470   (11:19:06Z)
GET https://labour.gov.bb/employment-services/online-job-centre/  200, 136 547 B, md5 66583e56c6ce   (11:21:18Z)  «Barbados Job Register - Government of Barbados Ministry of Labour»
GET https://labour.gov.bb/employment-services/online-job-centre/  200, 136 547 B, md5 1376d4f606b3   (11:21:20Z)
```

**The «Online Job Centre» page is a description of the Barbados Job
Register with one outbound link — `https://barbadosjobregister.gov.bb/` —
and no advertisement of its own.** The root links the same register and a
FAQ about it (`/barbados-job-register-faq-page/`). *This host is the
ministry's site: legislation, tribunals, grants, press. The board it
describes lives on another host — one that #222 already lists as a 403 to
the plain client, browser route not measured.*

## What this card is, and is not

- **A finding, not a renunciation**: 0 advertisements on this host because
  it publishes none, not because it refuses. *«Not a board» is the class
  `bestzambiajobs` opened (2026-09-05): a host whose rules and transport are
  fine and whose object is something else.*
- **The board is `barbadosjobregister.gov.bb`** — #222's list, «+0» at lot
  16 of #195; its measurement is that host's, not this card's.
- **No script, no configuration**, and nothing for `cover-letter` here.
