# Board adapter — Tanqeeb (per-country, Arabic-speaking markets)

<!-- verified: 2026-09-05 -->

<!-- hosts: per-country -->
<!-- script: none -->
<!-- countries: DZ EG PS SY YE -->
<!-- content: indeterminate · rules unreadable on 6 of 6 hosts queried, HTTP 202 with a 0-byte body · 2026-09-05 -->
<!-- witness: none — nothing was fetched beyond robots.txt, and nothing could be -->

**No adapter exists and none can be written until this changes.** The state is
**indeterminate**, not closed: nothing here says the operator refuses us.

## The measurement, dated

**Six hosts of the same operator**, each with the date it was measured and by
whom — because two independent readings of this same set both said *five* and
they were not the same five:

    tanqeeb.com              2026-09-05   this session      HTTP 202   0 bytes
    algerie.tanqeeb.com      2026-09-05   this session      HTTP 202   0 bytes
    syria.tanqeeb.com        2026-09-05   this session      HTTP 202   0 bytes
    egypt.tanqeeb.com        2026-09-04   issue #155 body   HTTP 202   0 bytes
    yemen.tanqeeb.com        2026-09-04   issue #155 body   HTTP 202   0 bytes
    palestine.tanqeeb.com    2026-09-04   issue #155 comment, 21:15   HTTP 202   0 bytes

`d41d8cd98f00b204e9800998ecf8427e` is the md5 of the empty string, on all six.

**The apex is not a country and adds none**; `countries:` carries the five
country subdomains.

> **Why the provenance column is here.** The first version of this sheet listed
> five hosts — four country subdomains and the apex — while the record published
> on 2026-09-04 listed five country subdomains including `palestine`. **Same
> cardinal, different members.** No count signalled it, no sum collapsed, and two
> readers would both have said *five*. It was found by reading the names.
>
> The cause is worth naming: **the issue body listed four, and `palestine` was
> added in a comment.** Reading the body and treating it as the issue is how a
> measurement that exists goes missing.

The guard's own words, which are the finding:

> *HTTP 202 with a 0-byte body — a 2xx that is not 200 is not the document, and
> an empty body states nothing. **This is not an absence**: a 404 would say there
> are no rules, and this says only that something answered.*

**This is a dated observation, not a property of the site.** Nothing in an empty
body distinguishes a deployment from an intermittence, and the same hosts may
answer differently tomorrow.

## It is the operator, not Algeria

`_robots.py` documents `algerie.tanqeeb.com` as the host that answers 202 with
zero bytes, and the shape of the note invites the reader to look for what is
particular about Algeria. **Nothing is.** Four country subdomains answer
identically, **and so does the bare apex `tanqeeb.com`** — which is not a country
at all, so a per-country explanation is ruled out at the operator level.

The Algerian host is the one that produced the fix in #125; it is not the one
that has the behaviour.

## Why the host list stops at six, and why that is not laziness

The issue asks for **every `tanqeeb` subdomain the repository can name**. It can
name one — `algerie.tanqeeb.com` — and this sheet adds the five measured beside
it, four of them from #155 and its comment, one measured here.

**The obvious way to extend the list is to read the apex and let the operator
name its own countries.** That is the method that closed a thirty-two-host
network on 2026-09-05, without composing a single hostname.

**It cannot be used here. The apex is itself indeterminate, and an indeterminate
is not probed** — that is the standing rule, and it binds hardest exactly when
the result would be useful. The alternative, composing `<country>.tanqeeb.com`
for countries the operator plausibly serves, is inventing hostnames.

**So the list is six, it is short for a reason that is written down, and it is
not a claim that the operator serves five markets.**

## What this blocks

`syria.tanqeeb.com` is the only known intermediary for the Syrian market. The
country is therefore neither *empty category* nor *access refused* but
**indeterminate**, and the same lock sits on Algeria, Yemen and Egypt.

**Writing "closed" here would be the error the state exists to prevent** —
`robots.txt` was never read, so no refusal was ever expressed. See
`shared/never-fail-silently.md` on the three states, and `shared/robots-policy.md`
for how `None` propagates.

## What would change this

- The hosts answering **200 with a body**, at which point the rules can be read
  and the ordinary guard applies.
- A source outside the operator naming further subdomains — a listing, a press
  page, a link from a site we may read. **Not a guess.**

Until then: **no adapter, no country page claiming a closed market, and no
figure.**
