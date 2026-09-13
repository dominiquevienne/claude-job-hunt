# Board measurement — Kazibongo (`kazibongo.com`, Tanzania): 403 to the declared client and to a real browser alike — a refusal to everyone, nothing read

<!-- verified: 2026-09-13 -->

<!-- hosts: kazibongo.com, www.kazibongo.com -->
<!-- script: none -->
<!-- countries: TZ -->
<!-- content: measured · **403 «Forbidden», 9 bytes, to a real browser as well** — the tab on `/jobs` and `fetch()` of `/` and `/jobs` from it, 16:25 UTC, the same nine bytes the declared client got; `www.` does not connect from the tab either; a refusal rendered to everyone is the operator's (borne 0), so no route is open by any legitimate means and nothing of the board was read · 2026-09-13 -->
<!-- witness: none — nothing served to any client; the 9-byte «Forbidden» is the only body, from the declared client (15:29 UTC, twice) and from a browser tab (16:25 UTC) · 2026-09-13 -->
<!-- route: none · 403 to a real browser too — the operator's refusal, not a client filter (borne 0); the guard opens on `certain: False` since #283 and the transport closes to everyone · 2026-09-13 -->

**Tanzania's named board, in the #222 candidate list as a single-host
country.** *This card is a measurement and not an adapter, and it is a
short one, because the guard closed the question before any page was
asked for.* Measured 2026-09-12 12:19–12:20 UTC with the declared client.

## The rules file is refused — twice, and that is the verdict

```
GET https://kazibongo.com/robots.txt        403 · server: openresty · 12:20:02 UTC   (bin/fetch-body.py, body not kept by the tool)
GET https://kazibongo.com/robots.txt        403 · server: openresty · 2 s later      — the same
_robots.allowed('kazibongo.com', '/')       allowed False · certain True · rule "/" · rule_kind host-closed
_robots.allowed('www.kazibongo.com', '/')   the same
```

**A `403` on the rules file is a refusal, and the doctrine keeps it one**:
the 2026-09-09 decision reopened `401` as an absence of rules and left
`403` exactly where it was. *`robots-policy.md` records one host —
`grabjobs.co` — whose 403 on `robots.txt` cleared by itself between two
reads; this one did not, two seconds apart.* So no path is open, the
browser branch has no open path to run on (it starts from «the rules open,
the transport refuses», and here the rules never answered), and **nothing
was fetched beyond the rules file — no root, no listing, no tab.**

*A refusal at the rules is the one refusal that does not say what it
refuses:* it may be an `openresty` front rule on `/robots.txt` alone, a
firewall keyed on our identity, or a host that serves no rules to anyone.
From here those look the same, and the card says so rather than choosing.

## What reopens it

- `robots.txt` answering `200` (or `404`/`401` — an absence) to the
  declared client: then the rules are read and the ordinary order applies;
- a **later** pair of reads minutes apart, not seconds — the `grabjobs.co`
  case cleared «within seconds», and two seconds may be inside that window;
- the pilot's or the owner's decision to treat a 403 *on the rules file*
  differently from a 403 on a page — a doctrine question, not a
  measurement, and this card does not decide it.

## What this card does not say

Nothing about what the site serves, its size, its fields, or whether a
browser is served — **because a browser was not opened.** *A tab would
have been the doctrine's route only after the rules opened a path.*

## 2026-09-13 — #283: an unread rules file is an absence of rules, and the transport measured

**Owner's decision of 2026-09-13, verbatim: «toutes incapacité d'ouvrir robots.txt
doit aboutir à l'absence de règles et donc à l'ouverture».** This card read
«host-closed, certain (12.09)» — a verdict taken on the rules file alone. Since #283 the 403 on
`/robots.txt` is `no-rules-403`, `allowed: True, certain: False`: nothing
was read, nothing forbids, and **the transport decides**. Measured with
`bin/fetch-body.py --allow-refusal` under the new guard, the root (and a
listing path where one was known) twice:

```
GET https://kazibongo.com/                               403, 9 B, md5 722969577a96   (15:29:16Z)
GET https://kazibongo.com/                               403, 9 B, md5 722969577a96   (15:29:19Z)
GET https://kazibongo.com/jobs                           403, 9 B, md5 722969577a96   (15:29:21Z)
GET https://kazibongo.com/jobs                           403, 9 B, md5 722969577a96   (15:29:23Z)
```

**The transport answers a **static 403** — the same bytes on every fetch: a refusal at the transport aimed at the client, family (1) of #222, where a browser is legitimate and is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*

## 2026-09-13 16:25 UTC — the browser route, MEASURED (#222): 403 to the tab as well

```
tab: https://kazibongo.com/jobs        403, «Forbidden», 9 B — the page itself
tab: fetch('https://kazibongo.com/')    403, 9 B, «Forbidden»
tab: fetch('https://kazibongo.com/jobs') 403, 9 B
tab: fetch('https://www.kazibongo.com/') TypeError: Failed to fetch (the apex with `www.` does not connect)
```

**The same nine bytes to a browser and to the declared client** — this is
the shape `cadremploi` is closed for: a 403 rendered to everyone is the
operator's refusal, not an infrastructure that cannot tell who we are
(borne 0 of the 2026-09-07 doctrine). Nothing of the board was read by any
route. **Not a verdict that the host is closed for good** — the owner's, on
his express validation; recorded: two clients, one day, nine bytes.
