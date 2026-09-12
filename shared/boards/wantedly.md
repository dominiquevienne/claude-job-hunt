# Not a board — Wantedly (`www.wantedly.com`, Japan): a business social network, by its own description, and why no adapter is built

<!-- verified: 2026-09-12 -->

<!-- hosts: www.wantedly.com -->
<!-- script: none -->
<!-- countries: JP -->
<!-- witness: none — this card reads the host's own words about itself (title, meta description, rules file) and builds nothing; no listing was walked and no count is claimed · 2026-09-12 -->

**Wantedly is not a job board, and it says so on its front page**: *«共感で
つながるビジネスSNS»* — a business social network that connects on
sympathy — *«450万人のユーザーと40,000社が利用»*, 4.5 million users and
40 000 companies. Read 2026-09-12 15:26 UTC with the declared client, the
guard on the exact path first. *In the Japan reserve since 2026-09-01 as
«open, no AI agent named, volume not established»; this card establishes
what it is instead of a volume.*

## What the host says, and what its rules say

```
robots.txt        200, 880 B — `User-Agent: *`, 28 Disallow lines, every one an account, message, edit or `.js` supplement path
                  (/users/*/edit, /messages, /bookmarked_projects, /projects/*/show_supplement.js …); no agent named; Sitemap: /sitemaps/sitemap.xml.gz
identity("/")     http, claude-user — nothing binds either token
GET /             200, 31 443 B — <title>Wantedly（ウォンテッドリー）共感でつながるビジネスSNS</title>
                  meta description: «Wantedlyは、450万人のユーザーと40,000社が利用するビジネスSNS。共感を軸にした新しい挑戦との出会いや、学びの発信など組織の枠を超えた「つながり」が広がっていきます。»
                  links: /signin_or_signup, /user/auth/facebook, /user/auth/google, the app stores, /projects.xml (a feed), sg. and en-jp. editions
```

*The rules are open and the transport answers 200 to the declared client —
nothing here is a refusal.* **The reason there is no adapter is the
object, not the door.**

## Why no adapter

**The unit Wantedly publishes is a company's «project» — a story and an
invitation to «visit» — inside a signed-in social graph, not a vacancy
with a title, a contract and a deadline.** Its own description names
users and companies, not jobs. What the plugin sweeps is a board: a list
of advertisements a candidate reads without an account and applies to
through the employer. Wantedly's surface for a candidate is a profile,
follows, messages and «visits», which its rules keep behind sign-in
(`/messages`, `/user/*`, `/bookmarked_projects`) — *reading them would be
reading a person's own account, which is `linkedin-profile`'s shape, not
`job-scan`'s.*

**So `/projects/` was not walked, on purpose**, and this card records the
decision with the site's own words as its evidence. *A count of projects
would be a count of stories, and it would enter the Atlas as if it were
vacancies.*

## What would change this

- Wantedly publishing vacancies as vacancies — a public listing with a
  count, titles and employers, outside the signed-in graph; the
  `/projects.xml` feed the front page links to is the first thing to read
  on that day;
- or a decision that the plugin reads recruiting social networks — a
  doctrine question, not a measurement.

## What this card does not establish

- **Anything about `/projects/`, `/projects.xml` or the sitemap** — not
  read, by the pilot's instruction and by the reasoning above.
- **The English and Singapore editions** (`en-jp.`, `sg.`) — the same
  product, not measured.
