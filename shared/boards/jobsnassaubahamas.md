# Board measurement — Jobs in Bahamas (`jobsnassaubahamas.com`, Bahamas): served on 13.09, and on 16.09 the origin is down behind Cloudflare — HTTP 522 on the rules file and the root, three readings; no script yet, a control decides

<!-- verified: 2026-09-16 -->

<!-- hosts: jobsnassaubahamas.com -->
<!-- script: none -->
<!-- countries: BS -->
<!-- content: indeterminate · **the root was served to the declared client on 2026-09-13 20:27 UTC (200, 93 191 / 93 185 B — a WordPress board with `/submit-job/` and `wp-json` exposed, per #448); on 2026-09-16 21:49–21:51 UTC every reading is Cloudflare's 522 «error code: 522» (16 B, md5 2c2dae9e9cdd) — `/robots.txt` under the declared identity (after ~90 s), `/` under the declared identity, `/robots.txt` and `/` under a bare `curl` (21 s): the edge answers, the origin does not; the name resolves on 1.1.1.1 (188.114.96.12 / 97.12, Cloudflare); no rules could be read (absence of rules, `certain: False`, #283) and nothing of the board was read; the browser was not connected for a fourth reading** · 2026-09-16 -->
<!-- witness: none — nothing was served on the day; the 13.09 reading is the only body known, and it was not kept -->

**Issue #448 (opened under #410, the Bahamas searched on 2026-09-13).
Measured 2026-09-16 21:49–21:51 UTC — the declared client by
`bin/fetch-body.py --allow-refusal`, the guard on the exact path (the rules
file itself unreadable: no rules, `certain: False`), and a bare `curl` as
the control.** Rank: the pilot's risk order of 2026-09-14 10:4x, after
Suriname Vacatures (#446).

## What was read, dated — a 522 is the edge saying the origin did not answer

```
2026-09-13 20:27Z  GET /            200, 93 191 B then 93 185 B                     fetch-body, Claude-User   (the reading that opened #448)
2026-09-16 21:49Z  GET /robots.txt  522, 16 B «error code: 522», md5 2c2dae9e9cdd   fetch-body, Claude-User   (after ~90 s of waiting)
2026-09-16 21:50Z  GET /            522, same body                                   fetch-body, Claude-User
2026-09-16 21:51Z  GET /robots.txt  522, same body, 21.7 s                           curl, its own identity   (the control: not the identity)
2026-09-16 21:51Z  GET /            522, same body                                   curl
```

**Cloudflare 522 is «Connection timed out» between the edge and the
origin: the site's server did not answer the CDN, whoever asked.** *Not a
refusal (the edge would say 403 or 1020), not a challenge (no
«Just a moment»), not a DNS failure (the name resolves to Cloudflare):
the board is unreachable on the day, for everyone.* Under #283 the
unreadable rules file is an absence of rules; under the 07.09 doctrine a
transport failure is a transport failure — **INDÉTERMINÉ, a measurement to
redo, never a verdict on the board** (§2 sexies).

## What a session does next

One `bin/fetch-body.py https://jobsnassaubahamas.com/` under the declared
identity, dated. Served → the adapter as #448 describes: the WordPress job
listing (the plugin's post type through `wp-json` or the pages, «we list
jobs across every industry», Nassau, Freeport, Grand Bahama, Abaco,
Exuma…), the stated count beside the emitted, contacts withheld. 522 again
→ the card's date moves and the issue stays open; a host down for a week
is a question for the owner, not a verdict of this card.

*Control deposited in the sessions' deferred-tasks file for 2026-09-18 — the next session
day after the derogation window.*
