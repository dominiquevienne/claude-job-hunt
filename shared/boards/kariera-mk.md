# Board adapter — Kariera.mk (North Macedonia): rules silent, transport closed

<!-- verified: 2026-09-07 -->

<!-- hosts: kariera.mk -->
<!-- script: none -->
<!-- countries: MK -->
<!-- content: indeterminate · the root and `/sitemap.xml` both answer HTTP 403 with 25 bytes, `Your request was blocked.`, md5 9ccabba20b9f4ec7d18bd6644579e5bf — the same body byte for byte as `jobstore` and `hays`, so nothing of this board was read · 2026-09-07 -->
<!-- witness: none — nothing was served, and the count this card does not give is the one a reader would want -->

**Only the apex was fetched.** `www.kariera.mk` serves the apex's rules and
the guard reports it as such; this card claims nothing about that form, and
declares no `host-forms:` because it declares no script to reach them.

**North Macedonia's named board, and the first card for it.** It has been
mentioned in this repository since 2026-09-05 with no status established;
this card establishes one and it is not coverage.

## The rules are silent about us — which is not the same as open

```
User-agent: Googlebot-Image
Disallow: /uploads/articles
Disallow: /uploads/files

Sitemap: https://kariera.mk/sitemap.xml
```

**One group, and it names a crawler that is not us.** No `*` group, no record
for either of this project's tokens. So nothing here binds us, and nothing
here was written for us: *silence towards us, not a permission.*

**This is the second shape of the groupless file found on 2026-09-07**, and it
is not the shape that opened #180. `ihararejobs.com` carries seven `Disallow:`
lines **above any `User-agent:`**; this one carries a group addressed to
somebody else. They reach the same place — `group_for()` returns `None`,
`_star_group()` returns `[]` — and they are different facts, which the guard
said in one identical and partly false sentence until it was corrected the
same day.

*The file also declares its sitemap, which is a coordinate, and the coordinate
is refused at the transport.*

## The transport refuses, at the root and not only at a path

```
GET /               403   25 bytes   md5 9ccabba20b9f4ec7d18bd6644579e5bf
GET /sitemap.xml    403   25 bytes   md5 9ccabba20b9f4ec7d18bd6644579e5bf   (twice)
body                "Your request was blocked."
```

**Taken at the root, because a 403 on a sitemap is not a closed board** — a
site can shut its sitemap to robots and serve its pages. Here the root is shut
too, so the scope of the refusal is the host.

**And the body is a vendor default, not this operator's words.** It is
identical, byte for byte, to `jobstore` and `hays` — two other countries, two
other operators. *`shared/robots-policy.md` now lists three.* The sitemap was
fetched twice first: the body does not change between reads, so the
fingerprint is comparable across hosts rather than carrying a per-request
element.

## What follows, and what does not

**Rules open a path and infrastructure refuses that same path.** Under the
decision of 2026-09-07 that makes this host a **candidate for a browser
adapter** — the shared refusal body is precisely the signal that says the
browser is worth its cost here, because nobody wrote this page about us.

**It is a candidate and not a plan.** Driving the browser is not this
session's to start, and this card does not claim the board would be readable
that way — only that the reason it is unreadable now is infrastructure rather
than an editor's decision.

**North Macedonia stays at zero coverage.** *That is a statement about this
host and this date, not about the country:* a second Macedonian board is named
in the coverage queue and has not been measured here.
