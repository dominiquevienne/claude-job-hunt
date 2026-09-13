# Board adapter — HeadHunter (`api.hh.ru`: hh.ru, hh.kz, hh.uz, rabota.by, zarplata.ru): one file for the network's five fronts, the user's own contact address on every request — and a 403 to that address on the day, on all four areas

<!-- verified: 2026-09-13 -->

<!-- hosts: api.hh.ru, hh.ru, hh.kz, hh.uz, rabota.by, zarplata.ru -->
<!-- script: hh.py -->
<!-- host-forms: api.hh.ru -->
<!-- host-forms-basis: read — `hh.py:HOST`, a single literal for the API; the fronts are named in `hosts:` because their pages are what the API's `alternate_url` points to, and `rabota-by.md` measured one of them · 2026-09-13 -->
<!-- countries: RU KZ BY UZ -->
<!-- content: measured · **HTTP 403 `{"errors":[{"type":"forbidden"}]}` on `/vacancies?area=<id>` for all four areas (16 BY, 40 KZ, 97 UZ, 113 RU), with the owner's own contact sent in `HH-User-Agent` beside our UA AND, in a second probe, as the whole `User-Agent: claude-job-hunt/<v> (<contact>)` — the two forms the API's specification names; 18:52 UTC, one request per area plus two probes; no `robots.txt` on the API host (404, an absence)**; the fronts' figures are `rabota-by.md`'s (30 406 for `area=16`, 1 025 175 for the network, 12.09) and are not this adapter's; the adapter is exercised on a stub of the documented envelope · 2026-09-13 -->
<!-- witness: the API's `found` per area — the witness the adapter prints beside every walk when the API answers; on the day it answered 403 to the address, and the adapter stopped without a retry; nothing else is compared · 2026-09-13 -->
<!-- route: http · under the user's own `boards.hh.contact` ONLY — the API requires a contact address and the plugin never fabricates one; without the key nothing is requested (exit 7); with the owner's key the API refused this address on 2026-09-13 (403 on four areas) — a dated fact, not a verdict · 2026-09-13 -->

**Four countries of #233 behind one API — and the API asks who is
calling.** Issue #337 (the owner's decision of 2026-09-13 on the form of
the key: `boards.hh.contact`, the user's own address, sent to `api.hh.ru`
and printed nowhere). Measured 2026-09-13 18:52 UTC with the owner's key
in the owner's config, the guard on the exact path first (no rules file →
open, an absence).

## The key, and where the address goes — and does not go

```yaml
boards:
  hh:
    enabled: true
    contact: "claude-job-hunt (you@example.org)"   # YOUR address; sent to api.hh.ru on every request as HH-User-Agent, and to nothing else
```

`api.hh.ru`'s OpenAPI specification requires `User-Agent: MyApp/1.0
(contact address)` or `HH-User-Agent` on every request, and answers 403
without one. **The plugin never fabricates an address**: the value is
read from `boards.hh.contact` by `_override.py` — the one function that
opens the config, one more key — sent as `HH-User-Agent:
claude-job-hunt/<version> (<contact>)` beside our own `User-Agent`, and
**appears in no text this adapter produces**: not in the refusal that
says what to write, not in a row, not in a note, not in a 403 message
(the guard in `tests/` asserts it against a private address). `setup.md`
tells the user, before they set it, that their address is sent to
`api.hh.ru` in this form. Without the key: nothing is requested, not
even the guard's rules fetch, exit 7 with the sentence to write.

## What the API answered on the day

```
GET https://api.hh.ru/robots.txt                        404 — an absence of rules (a knowledge)
GET https://api.hh.ru/vacancies?area=16&per_page=100&page=0   HH-User-Agent: claude-job-hunt/1.231.0 (<contact>) + our UA   →  403 {"errors":[{"type":"forbidden"}]}   (BY)
GET …?area=40 · ?area=97 · ?area=113                    the same 403, the same 34-byte body                                             (KZ · UZ · RU)
probe A: our UA + HH-User-Agent (<contact>)             403 {"errors":[{"type":"forbidden"}],"request_id":"1789325559954d…"}
probe B: User-Agent: claude-job-hunt/1.231.0 (<contact>) alone   403, the same body, another request_id
```

**The API refuses this address in both forms its specification names.**
`{"type":"forbidden"}` is the API's generic refusal — a block on the
caller's network address (the fronts have refused non-CIS addresses
before), an unregistered application, or a policy the specification does
not state; **which is not decided by six requests from one machine, and
the adapter does not guess**: a 403 stops the run without a retry, and
the message says «a contact it does not accept, or a block». `rabota.by`
itself served its listing to the declared client on 2026-09-12
(`rabota-by.md`, 30 406 for `area=16`); the API behind it did not, on the
13th, with a contact.

## What the adapter does when the API answers

`search --area <id>`: `/vacancies?area=&per_page=100&page=N`, 1 s apart;
`found` printed beside every walk («n emitted over p page(s), site states
found — equal / k short»); the API's own window of 2 000 results per
query named when reached, with `--text` as the way to narrow. The item, in
the API's own names: id, name, employer {id, name}, area.name, salary
{from, to, currency, gross — **no period stated**, `salary_unit_stated:
false`}, published_at, schedule, experience, employment,
professional_roles, snippet {requirement, responsibility} with the
`<highlighttext>` stripped, alternate_url (the front's page). `ad --id`:
description (HTML → text), key_skills — **and `contacts` dropped whole
and listed as dropped**, with any key named like one. Areas: 16 BY, 40
KZ, 97 UZ, 113 RU — the network's ids; `--area` refuses any other.

## Configuration

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `contact` | **yes** | the user's own address; absent → nothing requested, exit 7 |

No browser. `search` is one request per 100 at 1 s; `ad` is one.

## What is not established

- **Why the API answers 403 to this address** — the network address,
  the application, or a policy; one machine, one day, six requests.
- **The five fronts' own counts** — `rabota-by.md` has one; the others
  were not read.
- **Whether `zarplata.ru` is a sixth area or the Russian one** — the
  network lists it as a front; the adapter has no area for it.
- **The salary period** — monthly by the network's convention, stated
  nowhere in the item.

## 2026-09-13 — shipped on a stub, exercised once per area

One request per area with the owner's key: 403 × 4. Two probes on the
header form: 403 × 2. Three tests; six mutations on a detached worktree
(`python3 -B`), six red — the contact check moved after the guard (inert
until the no-key case counted the guard as a request), the contact echoed
in the 403 message, the header renamed, the «equal» branch made
unconditional (inert on an equal-only fixture until a 3-against-2 run was
added), `contacts` kept, the window check dropped.
