# Board measurement — Bakeca (`bakeca.it`, Italy): the classifieds board's employment section — the rules open the path and the infrastructure returns 403

<!-- verified: 2026-10-06 -->

<!-- hosts: www.bakeca.it, bakeca.it -->
<!-- script: none -->
<!-- countries: IT -->
<!-- content: measured · **read 2026-10-06: the rules OPEN this path and the transport REFUSES it** — `/offerte-lavoro/` answers **HTTP 403 with 15 568 B** under the declared identity, while both host forms serve a rules file (`state: read`, `certain: True`) with no refusal naming us and **no `Crawl-delay`**. *That is the 2026-09-07 configuration exactly: the host has written that it opens our path, and the firewall does not contradict it — it does not know who we are.* **So this is a browser-route CANDIDATE and not a closed board — but borne 0 is NOT yet satisfied: the refusal body must be fetched TWICE to see whether its fingerprint moves, and compared against an unrelated host's refusal, before anything is concluded about who the 403 aims at.** Until that is done the route is undetermined, and an undetermined is never a renunciation · 2026-10-06 -->
<!-- witness: none — a 403 states nothing about the board's size · 2026-10-06 -->

## Measured 2026-10-06 under the declared identity, one guard per host form

Opened under **#949**, tranche 2 — the six Italian generalists and classifieds.
*The owner opened the campaign by tranches on 2026-10-06, verbatim « oui, ouvre
#949 par tranches, commence par l'Italie ».*

**The guard was taken on EVERY host form separately, in a turn distinct from the
retrieval, because `robots.txt` binds a HOST and not a brand.** *Thirteen forms
were guarded across this tranche and they returned THREE different states —
`read`, `no-rules` and `unrecognised` — all open, which is why `state` and not
the verdict is what each card records.*

**No adapter is declared here, and that is the finding rather than an
omission.**
