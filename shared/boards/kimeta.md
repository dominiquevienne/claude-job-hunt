# Board measurement — kimeta (`kimeta.de`, Germany): a blanket `Disallow: /` to every agent, read on `www.kimeta.de` for both queries

<!-- verified: 2026-10-07 -->

<!-- hosts: www.kimeta.de, kimeta.de -->
<!-- script: none -->
<!-- countries: DE -->
<!-- content: measured · read 2026-10-06 — the rules refuse our path IN WRITING and the refusal is a blanket one: `User-agent: * / Disallow: /`, so `allowed=False`, `rule=/`, `kind=host-closed`, `group=*`, `certain=True`, and NO `Crawl-delay` is written because the file closes everything instead of pacing it. Borne 1 blocks every route including the browser, so nothing was retrieved. BOTH host forms were queried separately and BOTH were answered by `www.kimeta.de`, which the tool says itself, so the bare form's own file is UNREAD and this verdict is about `www.kimeta.de` · 2026-10-07 -->
<!-- witness: none, and none possible by any route we may take — no body was fetched, so nothing is known of what this board publishes; and no rate was read, there being no `Crawl-delay` in a file that closes everything · 2026-10-07 -->

## Measured 2026-10-06 — a written refusal, the only one in this tranche

Opened under **#949**, first German tranche.

```
kimeta.de      -> allowed=False  rule=/  kind=host-closed  group=*  certain=True
www.kimeta.de  -> allowed=False  rule=/  kind=host-closed  group=*  certain=True
requested_host kimeta.de     host (qui a REPONDU) www.kimeta.de    <- pour les DEUX
Crawl-delay : AUCUN — le fichier ferme tout, il ne cadence rien
```

**THE REFUSAL DOES NOT NAME US, AND THAT IS WORTH WRITING DOWN.** *It is
`User-agent: * / Disallow: /` — the publisher closing the door to every agent
evenly, not an intention about this repository.* **Borne 1 honours it the same
way either: a `Disallow` aimed at our path blocks every route, the browser
included.** So this card carries no count, no shape and no verdict on the board.

**AND THE TOOL CORRECTED ME IN ITS OWN `reason` FIELD, WHICH THIS CARD REPEATS
RATHER THAN HIDES:** *« These rules were read from `www.kimeta.de`, not from
`kimeta.de` — the request was redirected, and the two hosts do not necessarily
publish the same file. »* **So «both forms refuse» would overstate it: one file
was read, twice, and the bare host's own file is UNREAD.** *Querying each form
separately is still right — it is what surfaced the redirection — but what it
bought here is knowing WHICH host answered, not two independent verdicts.*

## What this card is, and is not

- **Not a verdict that the host is closed**, and not a renouncement: the owner's
  decision of 2026-09-08 reserves that to him, and nothing here asks for it.
- **There is a lawful door and it is NOT ours to open.** Since 2026-09-13 the
  `boards.<board>.override_robots` key is available on ANY board whose rules
  refuse in writing, **and it is the USER who sets it, in full knowledge, never
  `job-setup` in his place and never by default** — it costs him his own address.
  *The tool reports it absent from the current configuration; the issue carrying
  this card says so and does not ask for it.*
- What would reopen it without that key: a change in this host's own rules — or
  a reading of `kimeta.de`'s own file, which a redirect has so far prevented.
