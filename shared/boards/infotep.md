# Board measurement — INFOTEP (`www.infotep.gob.do`, Dominican Republic): served to a tab — and it is the national training institute, not a board

<!-- verified: 2026-09-13 -->

<!-- hosts: www.infotep.gob.do, infotep.gob.do -->
<!-- script: none -->
<!-- countries: DO -->
<!-- content: out-of-domain · **not a board** — the tab on `/` is served (200, 90 654 B, Joomla, «Instituto Nacional de Formación Técnico Profesional | INFOTEP - Inicio»): a vocational-training institute whose «oferta» is its *oferta formativa* (courses, by regional directorate), whose «Plazas Vacantes» page is the institute's own hiring (served, 46 038 B, a menu page), and whose `/empleo` — the listing path the 12th guessed — is the server's own 404 (nginx, 1 690 B); no advertisement, no listing, no count anywhere read; the declared client met a challenge on the 11th, the tab did not on the 13th; the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: none — nothing to count: the host publishes training offers and its own vacancies page, not employers' advertisements; read from a tab 16:55 UTC · 2026-09-13 -->
<!-- route: none · not a board — the Dominican national training institute (INFOTEP); its «oferta» is courses; the country's board question is not answered by this host · 2026-09-13 -->

**Measured 2026-09-12 at 11:00:36Z UTC for #233, lot 3 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first, by `bin/fetch-body.py
--allow-refusal` — the four records carry the status, the bytes, the md5 and
the `cf-ray` that answered.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 1836 B, md5 c6370d4bc025 both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*The file is Cloudflare's managed content block, byte for byte — the
`Content-Signal` preamble and nine named crawlers refused, `ClaudeBot` among
them — with not one line of the operator's own.* Before the decision this
host was read as closed by name; the decision reopened it on paper, and this
card is the first time its transport was asked under the permitted token.

## The transport — a Cloudflare challenge

```
GET https://www.infotep.gob.do/            403, 6160 B, md5 6a38c5509346    (11:00:36Z)
GET https://www.infotep.gob.do/            403, 6160 B, md5 e24276e5e6c2    (second fetch)
GET https://www.infotep.gob.do/empleo     403, 6160 B, md5 784f808d7ead    (11:02:06Z)
GET https://www.infotep.gob.do/empleo     403, 6160 B, md5 823d4681ec85    (second fetch)
```

**Same size, different md5 on two fetches of the same URL, «Attention
Required! | Cloudflare» — a challenge**, the `revolico` / `mabumbe` /
`sudancareers` family. *Masking the 16-hex `cf-ray` in the two bodies leaves
ten differing lines, and every one is an edge stamp: the Rocket Loader nonce
on four `<script type>` attributes, a beacon `<script>` present in one body
only, and the base64 timestamp in `__CF$cv$params` — nothing of the site.* *The comparison across hosts is void (the
`cf-ray` is in the body); the comparison of one URL with itself is what says
«challenge».* **A challenge is where the browser branch stops** (borne 2): the
plugin neither defeats one nor asks the user to. Whether a real browser passes
it without a person is not measured, and this card claims nothing either way.

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a challenge.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **Not an AfricaWork host** — the state's technical-training institute, under the same 1 836-byte managed block as the franchise; its challenge page is 6 160 B where the franchise ones are 5 508–5 515 B (Rocket Loader nonces in this one), and the `revolico` reading holds: a challenge is a challenge whatever the operator.

## 2026-09-13 16:55 UTC — the browser route, MEASURED (#222): served, and the wrong kind of site

```
tab: /empleo                                    404 Not Found (nginx, 1 690 B) — the path this card guessed on the 12th is nothing on the site
tab: fetch /                                    200, 90 654 B, Joomla — «INFOTEP - Inicio»; no challenge; links: /index.php/oferta-formativa/<direction-régionale>…, /index.php/sobre-nosotros/plazas-vacantes, programa-rd-trabaja, becas
tab: fetch /index.php/sobre-nosotros/plazas-vacantes   200, 46 038 B — «Plazas Vacantes», the institute's own hiring: a menu page, no listing read
```

**INFOTEP is the Dominican Republic's national vocational-training
institute** — its «oferta» is an *oferta formativa*, courses by regional
directorate; «Plazas Vacantes» is the institute recruiting for itself.
Nothing on it is an employer's advertisement. *The 12th read a challenge
on the transport and never saw the site; the 13th saw it, and it is not
a board.* The country's question — a public employment service with a
listing — is not answered here (the `empleateya` / `mt.gob.do` family is
where a Dominican public listing would live, not measured in this pass).
