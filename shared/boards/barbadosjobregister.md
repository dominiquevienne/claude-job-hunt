# Board measurement — Barbados Job Register (`barbadosjobregister.gov.bb`): the rules file answers 403 on `www.` and the apex fails its TLS certificate — no path open, nothing read, no browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.barbadosjobregister.gov.bb, barbadosjobregister.gov.bb -->
<!-- script: none -->
<!-- countries: BB -->
<!-- witness: none — nothing past the rules file was requested; the guard's two verdicts (`host-closed, certain` on `www.`, INDETERMINATE by TLS on the apex) are the only bodies this card holds · 2026-09-13 -->
<!-- route: none · the rules file is refused (403 ×2, x-cache CONFIG_NOCACHE) and the apex's certificate does not verify — no open path for any client, browser included · 2026-09-13 -->

**The register the Ministry of Labour's site points to as its «Online Job
Centre» (`labour-gov-bb.md`), and the only board of its country in this
repository.** *A measurement and not an adapter, and a short one, because
the guard closed the question at the rules file.* Measured 2026-09-13
10:38 UTC with the declared client.

## Two host forms, two verdicts, neither an open path

```
GET https://www.barbadosjobregister.gov.bb/robots.txt   403 · x-cache: CONFIG_NOCACHE · 10:38:24 UTC   (bin/fetch-body.py, twice, 3 s apart — the same)
_robots.allowed('www.barbadosjobregister.gov.bb', '/')  allowed False · certain True · rule "/" · rule_kind host-closed
_robots.allowed('barbadosjobregister.gov.bb', '/')      allowed None — «[SSL: CERTIFICATE_VERIFY_FAILED]»: INDETERMINATE, and an INDETERMINATE is not probed
```

**A `403` on the rules file is a refusal, and the doctrine keeps it one**
(the 2026-09-09 table reopened `401` alone); **a certificate that does not
verify is a non-answer**, not a door (`robots-policy.md`, «a non-answer is
not a refusal»). Between the two forms there is no path the rules open,
so the browser branch — which starts from «the rules open, the transport
refuses» — has nothing to start from. *Nothing beyond the rules file was
requested; no tab was opened.* Same shape as `kazibongo.md` the day
before, on a government host.

## What reopens it

- `www.…/robots.txt` answering anything but 403 — then the rules are
  read and the ordinary order applies;
- the apex presenting a certificate that verifies (or the TLS failure
  being isolated to this resolver/machine — a second machine's read would
  say);
- a doctrine decision on a 403 *at the rules file* — a question the card
  poses and does not decide.

## What this card does not say

Nothing about what the register serves — size, fields, whether a browser
is served — **because a browser was not opened**. *The country's page on
the Atlas keeps its ministry as «not a board» and its register as «rules
refused, dated».*
