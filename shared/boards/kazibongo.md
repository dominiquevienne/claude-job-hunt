# Board measurement — Kazibongo (`kazibongo.com`, Tanzania): the rules file itself answers 403, so no path is open and nothing was read

<!-- verified: 2026-09-12 -->

<!-- hosts: kazibongo.com, www.kazibongo.com -->
<!-- script: none -->
<!-- countries: TZ -->
<!-- witness: none — nothing past the rules file was requested; the guard's verdict (`allowed False, certain True, rule_kind host-closed`) is the only body this card holds, taken twice two seconds apart · 2026-09-12 -->

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
