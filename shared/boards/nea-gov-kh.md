# Board measurement — nea.gov.kh (Cambodia): rules open to us, the vendor default at the door — the only host of its country

<!-- verified: 2026-09-11 -->

<!-- hosts: nea.gov.kh, www.nea.gov.kh -->
<!-- script: none -->
<!-- countries: KH -->
<!-- witness: none — nothing was read past the refusal; the rules file is the only body this card holds, 1 836 bytes, Cloudflare's managed template · 2026-09-11 -->

**This card is a measurement and not an adapter.** *No card declared `KH`
before it. The host is Cambodia's National Employment Agency — the public
employment service — and the repository knew it only as the example of «access
without intention» in `shared/robots-policy.md` (2026-09-08).* **This card
sorts the refusal, and the sort puts it on #222.**

## Step 1 — the rules, twice, on both hosts (2026-09-11 13:40 UTC)

```
https://nea.gov.kh/robots.txt        200   1 836 o   md5 c6370d4bc02563e4b1e1af4540d1e670   twice
https://www.nea.gov.kh/robots.txt    200   1 836 o   md5 c6370d4bc02563e4b1e1af4540d1e670   twice — the same file
```

**Cloudflare's managed content-signals template, identical on both forms**:
`User-agent: *` → `Content-Signal: search=yes,ai-train=no,use=reference`,
`Allow: /`; then named refusals — `Amazonbot`, `Applebot-Extended`,
`Bytespider`, `CCBot`, **`ClaudeBot`**, `CloudflareBrowserRenderingCrawler`,
`Google-Extended`, `GPTBot`, `meta-externalagent`, each `Disallow: /`.
**`Claude-User` is not named.**

**The guard's verdict, on the exact path `/`, both hosts:** `allowed: True,
rule: None, certain: True` — *«no `Disallow` matches this path in `*`»*.
**That is the 07.09 decision applied: a refusal that names `ClaudeBot` does not
bind `Claude-User`, the token this plugin declares.** *The policy's own
paragraph on this host — that the template is identical on three continents
and nobody here decided anything — still holds: the file is the vendor's, the
`ClaudeBot` line included.*

## Step 2 — the transport, twice per host, and the fingerprint

```
https://nea.gov.kh/         403   25 o   md5 9ccabba20b9f4ec7d18bd6644579e5bf   ×2, identical   "Your request was blocked."
https://www.nea.gov.kh/     403   25 o   md5 9ccabba20b9f4ec7d18bd6644579e5bf   ×2, identical
```

**That is the vendor default of family (1) — the twelfth host on that
fingerprint**, after `hiringcafe.com`, `www.jobstore.com`, `www.hays.fr`,
`iqjscout.com`, `eshjob.com`, `www.iraqhire.com`, `www.tala-com.com`,
`kariera.mk`, `sptojobslink.com`, `northcyprus.cv`, `jobs.af`. *Stable across
two reads on each of two hosts: not a challenge, a static refusal to a client
the infrastructure does not recognise.*

> **Rules open, transport refuses, fingerprint stable → the browser route is
> the candidate (doctrine of 07.09), and the route is an adapter in the sense
> of the 08.09 decision.** *Bound 0 is settled by the shared fingerprint:
> eleven unrelated operators do not write the same 25 bytes.*

**So this host goes to #222** — the objects waiting for the Chrome extension —
**with the priority `shared/false-zero-cost.md` gives the only host of a
country**: Cambodia has no other card, and the National Employment Agency is
the one public listing the country publishes.

## What this card does not say

Nothing about what the site serves — its size, its fields, whether the
listing is server-rendered — because nothing past the door was read. **The
08.09 sentence «blocks access while expressing no intention at all» is
confirmed on the transport and refined on the rules: the `*` group grants,
and the only refusal that names us names the other token.**
