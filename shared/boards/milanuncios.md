# Board measurement — Milanuncios (`www.milanuncios.com`, Spain): the generalist classifieds with an employment section — **its rules NAME this project three times and permit the token we send, closing six paths that are exactly the ones we would withhold anyway; and its infrastructure answers a «Pardon Our Interruption» captcha under HTTP 200, to the declared client and to a connected tab alike**. Borne 2 stops here: the captcha is never answered and never asked of anyone. Nothing is declared closed

<!-- verified: 2026-10-05 -->

<!-- hosts: www.milanuncios.com, milanuncios.com -->
<!-- script: none -->
<!-- countries: ES -->
<!-- route: none · a «Pardon Our Interruption» captcha served under HTTP 200 on 2026-10-05 19:31–19:47 UTC, to the declared client and to a connected tab alike; borne 2 forbids answering it or asking a candidate to — a DATED statement about the route and not a verdict on the board (§2 sexies) · 2026-10-05 -->
<!-- host-forms-basis: read — `www.milanuncios.com` and `milanuncios.com` both serve the SAME 4 033 B rules file (md5 b6b66259e583, `state: read`, `certain: True`), fetched at 19:29:35 UTC and verified to be genuine rules and not a challenge wearing a 200: 51 `User-agent` lines, 134 `Disallow`, 11 `Allow`, no HTML, no captcha string · 2026-10-05 -->
<!-- content: indeterminate · **the rules permit us by name and the transport serves a captcha, and nothing of the board was read: `robots.txt` (4 033 B, md5 b6b66259e583, read at 19:29:35 UTC) addresses THREE of this project's tokens with deliberately different rules — `claudebot` gets `Disallow: /`, while `claude-searchbot` and `claude-user` each get `Allow: /` plus six refusals: `/api/`, `/publicar`, `/datos-contacto/`, `/contacta/`, `/email/`, `/anuncios-usuario/`. `identity()` returns `token: claude-user`, `state: http`, «claude-user may fetch this path (claudebot may not)», which is the 2026-09-07 decision applied; and the six refused paths are the contact, identity and publishing paths, so the operator granted reading and closed exactly what this project withholds anyway. AND THE RATE, WHICH THIS HOST MAKES A POINT OF: the 4 033 B write NO `Crawl-delay` at all — not for `*`, not for any of our three tokens — so the 2 s of our own pace are the ones that would apply; and the host enforces a rate anyway through the control described next, which is why an absent `Crawl-delay` must never be read as an absent rate limit. THEN THE TRANSPORT: by 19:31:58 UTC — about nine requests and two and a half minutes after the rules were served — `/ofertas-empleo` and `/empleo` answered HTTP 405 at 97 958 B each with a MOVING md5 across two reads, and the root answered HTTP 200 carrying «Pardon Our Interruption / ¡Ups! Algo se detuvo / Para continuar, completa el captcha», md5 e077048f9461 STABLE across two reads. A single request after a 120 s pause returned the same interstitial at the same md5, and a connected tab on `/ofertas-empleo/` rendered the same captcha. SO THE EMPLOYMENT LISTING PATH WAS NEVER ESTABLISHED: no served page of this board was read, by any route, and the card claims no count, no advert shape and no inventory. The host's own interstitial offers «estés navegando fuera de España» among its possible causes — recorded as the host's words and NOT as a measured cause, since this reading has one vantage point and no identity was forged to vary it. WHAT WOULD LIFT THIS is a later reading in which the interstitial is not served — which is exactly what happened to `revolico` and `emploi-cm`, both challenged on one day and served to a tab on another. METHOD: guard on both host forms and each exact path in turns distinct from the retrievals, exercised in BOTH directions (`/` and a listing permitted; `/datos-contacto/`, `/contacta/`, `/email/`, `/anuncios-usuario/`, `/publicar`, `/api/` refused); every body fetched twice before any fingerprint was compared; the refusals kept only under `--allow-refusal` so their status travels in their records** · 2026-10-05 -->

<!-- witness: none — nothing of the board was read, so there is nothing to count and no count is claimed; the only figures here are the sizes of the rules file and of the interstitial · 2026-10-05 -->

## Measured 2026-10-05 — rules that name us and permit us, and a captcha under 200 on 6 paths of 9

```
robots.txt            4 033 o   md5 b6b66259e583, read, certain, 19:29:35 UTC
                                51 User-agent · 134 Disallow · 11 Allow
                                aucun HTML, aucune chaine de captcha -> de VRAIES regles
                                AUCUN Crawl-delay nulle part -> 2 s a nous…
                                …et un taux impose quand meme, voir plus bas
  User-agent: claudebot         Disallow: /                      <- ferme a CE nom
  User-agent: claude-searchbot  Allow: /  + 6 refus
  User-agent: claude-user       Allow: /  + 6 refus
      /api/ · /publicar · /datos-contacto/ · /contacta/ · /email/ · /anuncios-usuario/
  identity()                    token=claude-user, state=http
                                « claude-user may fetch this path (claudebot may not) »
la garde, eprouvee dans les DEUX sens
  /  ·  /ofertas-empleo  ·  /empleo                     allowed=True
  /datos-contacto/ · /contacta/ · /email/               allowed=False
  /anuncios-usuario/ · /publicar · /api/                allowed=False
puis le TRANSPORT, 19:31:58 UTC — ~9 requetes, ~2 min 30 apres les regles
  /ofertas-empleo       405      97 958 o   md5 MOUVANT entre deux lectures
  /empleo               405      97 958 o   md5 MOUVANT
  /                     200      95 999 o   « Pardon Our Interruption »
                                            md5 e077048f9461  STABLE x2
  apres 120 s d'attente, UNE requete        le MEME md5, le MEME defi
  onglet connecte sur /ofertas-empleo/      le MEME captcha
server: bon  ·  via CloudFront (x-amz-cf-pop ZRH52-P1)
```

**Found by the Spain pass of #949, and taken LAST and with care** — *the note I carried all session
said «&nbsp;same group as InfoJobs, which refuses our agents in writing, so read its `robots.txt`
before anything else&nbsp;».* **Reading it first was right, and it says the opposite of what the
caution expected.**

### The rules name us three times, and they are not careless

| token | what the file says |
| :-- | :-- |
| `claudebot` | `Disallow: /` — closed to that name |
| `claude-searchbot` | `Allow: /` + six refusals |
| **`claude-user`** | **`Allow: /`** + the same six refusals |

**And the six are `/api/`, `/publicar`, `/datos-contacto/`, `/contacta/`, `/email/` and
`/anuncios-usuario/`** — *the contact paths, a user's own adverts, and publishing.*

> **The operator granted reading and closed exactly the paths this project withholds anyway.**
> *That is not a boilerplate file: it was written token by token, and the refusals it chose are the
> ones our own doctrine would have chosen.* **A host that thinks about us this precisely deserves
> to have its six refusals honoured without argument, and they are.**

*`identity()` makes the applicable decision explicit — `token: claude-user`, `state: http`,
«&nbsp;`claude-user` may fetch this path (`claudebot` may not). Ordinary HTTP, no browser&nbsp;» —
which is the owner's 2026-09-07 decision doing its work: a named refusal of `ClaudeBot` does not
bind `Claude-User`.* **The guard was exercised in both directions and refuses the six while
permitting the root and a listing path.**

### No `Crawl-delay` is written, and a rate is enforced regardless

**The 4 033 bytes write no `Crawl-delay`** — not under `*`, not under any of the three tokens that
name us. *So the 2 s of our own courtesy are what would apply, and nothing in the file asks for
more.*

> **And then the host enforces a rate anyway.** *About nine requests in two and a half minutes was
> enough to replace every answer with a captcha.* **So an absent `Crawl-delay` is not an absent
> rate limit — it is a rate that is never stated and still has a threshold**, and the only way to
> learn where the threshold is, is to cross it.

*The one host of this pass that DID write a delay — Hosco, `Crawl-delay: 10`, naming ClaudeBot as
respecting it — is the opposite case and the kinder one: it says the rate out loud and does not
need to enforce it.*

### Then the transport, and it does not agree with the rules

**The rules were served at 19:29:35 UTC. By 19:31:58 — about nine requests and two and a half
minutes later — every path answered a control.**

- **`/ofertas-empleo` and `/empleo`: HTTP 405** at 97 958 B each, *with a **moving** md5 across two
  reads* — so the body carries a per-request element and no fingerprint comparison across hosts
  would be valid. **I fetched twice before comparing**, which is what made that visible.
- **The root: HTTP 200** carrying «&nbsp;Pardon Our Interruption / ¡Ups! Algo se detuvo / Para
  continuar, completa el captcha&nbsp;», *md5 `e077048f9461`, **stable** across two reads.*

> **The 200 is the trap, and I walked into it before I read the body.** *I wrote «&nbsp;the root
> answers 200, so the host serves us&nbsp;» and that was wrong: a readable body is not an answer, and
> here even the STATUS lies.* **A challenge served under 200 escapes every check that looks at the
> code** — the defect this repository already records, met again.

**A single request after a 120 s pause returned the same interstitial at the same md5**, and **a
connected tab on `/ofertas-empleo/` rendered the same captcha.** *So the control is not a momentary
rate trip that a pause clears, on this date.*

**This is the same vendor page as `epreselec.md`** — another property of the same group, where it
was measured as arriving «&nbsp;from about the twelfth request in two minutes, every path&nbsp;» and
where the adapter dies with exit 9, *«&nbsp;the CAPTCHA never answered, never asked of anyone (borne
2)&nbsp;»*. **The same conduct applies here.**

### What is NOT established, and what the host says about it

**The employment listing path was never established.** *No served page of this board was read by
any route, so this card claims no count, no advert shape, and no inventory.* **`/ofertas-empleo`
and `/empleo` are the paths the guard was asked about; whether either is the real listing is
unknown, because neither ever answered with content.**

**The interstitial offers its own possible causes**, among them «&nbsp;estés navegando fuera de
España&nbsp;» — *you are browsing from outside Spain.* **Recorded as the host's words and not as a
measured cause:** *this reading has a single vantage point, varying it is not something we do, and
a correlation visible from the network is not a cause.*

### Why this is a route statement and not a verdict on the board

**§2 sexies lists an anti-robot control among the things that are limits of ROUTE and never verdicts
on a board** — *«&nbsp;ils disent pas par ce chemin-là&nbsp;»* — and **an indeterminate is never a
renunciation: it is a measurement to redo.**

**So `route: none` here is dated and motivated, and it is expected to be replaced.** *The two
precedents both did exactly that:* **`revolico` recorded `content: indeterminate` on a Cloudflare
interstitial and later carried `route: browser · 2200` when a tab was served; `emploi-cm` was
challenged to a tab on 2026-09-14 and served on the same day's second reading, ending at
`route: browser · 405`.** *What would lift this is one later reading in which the interstitial is
not served.*

**Nothing is declared closed, and no closure is proposed.** *Writing a host off belongs to the
owner, and this measurement does not ask for it.*

**Measured 2026-10-05 by the declared client, the guard taken on both host forms and each exact
path in a turn distinct from the retrieval and exercised in BOTH directions, `bin/fetch-body.py`
throughout, every body fetched twice before any fingerprint comparison, the refusals kept only
under `--allow-refusal` so their status travels in their records, and one connected tab.** *A
measurement, not an adapter.*

```
_robots.verdict('www.milanuncios.com')   state: read, certain: True, 4 033 B, 19:29:35 UTC
  named: claudebot (Disallow /), claude-searchbot (Allow / + 6), claude-user (Allow / + 6)
identity('www.milanuncios.com')          token: claude-user, state: http
allowed(…, '/') · '/ofertas-empleo' · '/empleo'                 True
allowed(…, '/datos-contacto/x') · '/contacta/x' · '/email/x'    False
allowed(…, '/anuncios-usuario/x') · '/publicar' · '/api/v1/x'   False
GET /ofertas-empleo · /empleo    405 x2, 97 958 B, md5 MOVING between two reads
GET /                            200, 95 999 B, md5 e077048f9461 stable, «Pardon Our Interruption»
GET / after a 120 s pause        200, same md5, same interstitial
tab on /ofertas-empleo/          the same captcha, nothing of the board rendered
```
