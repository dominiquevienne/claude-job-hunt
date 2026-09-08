# Board adapter — PortalJob Madagascar (open, readable, and not enumerable)

<!-- verified: 2026-09-08 -->

<!-- hosts: www.portaljob-madagascar.com -->
<!-- script: none -->
<!-- countries: MG -->
<!-- content: indeterminate · the root serves 8 593 o carrying an Inertia.js `data-page` payload of 3 783 o — 32 sectors and 6 contract types, and zero advertisements, because the component is `Home`; `/sitemap.xml` is HTTP 404 and no route to a listing is declared anywhere read · 2026-09-07 -->
<!-- witness: none — the site publishes no total, and what the root serves is a menu rather than an inventory -->

**Madagascar stays at zero coverage — but not for the reason this card gave
when it was written earlier on 2026-09-07.**

## CORRECTION, same day: this host does not serve nothing

**It serves its whole page payload inline, and the control this card proposed
is the one that cannot see it.**

```
<body class="font-sans antialiased">
  <div id="app" data-page="{&quot;component&quot;:&quot;Home&quot;,
                            &quot;props&quot;:{ … 3 783 bytes … }}">
```

**This is Inertia.js.** The server renders a real response and puts the page's
data in a single HTML attribute; the client turns it into a page. So the count
that this card called *«the discriminator»* — **zero `<a>` on a body of several
kilobytes** — is exactly what a correctly working Inertia response looks like.
*The signature identified a real class and then named the wrong members: an
application shell that fetches its content later, and a server-rendered
response that already carries it, are indistinguishable by that count.*

**What the payload actually holds:** the site's own menu — 32 sectors with
their slugs (`agronomie-agriculture`, `biologie-chimie-sciences`, …), 6
contract types, a quote, an auth block. **Zero advertisements**, because the
component is `Home` and the home page is a menu.

*The earlier reading of this card is preserved below, because the counts in it
were correct and only their interpretation was wrong.*

## Why it is still not enumerable

**`/sitemap.xml` answers HTTP 404**, and no listing route is declared anywhere
that was read — not in the shell, not in the 264 kB runtime bundle, whose only
literal path is `/build/`. The page components are code-split and the sector
slugs travel without the prefix that would use them.

> **The remaining step would be to guess a route.** `/secteur/<slug>`,
> `/offres`, `/emploi/<slug>` — each plausible, none written down. **A path
> this repository composed is not a path the site declared**, and a 404 sweep
> to find the right one is probing.

**So the verdict stands and its reason changes**: not *«the page contains
nothing»*, but *«the page contains its menu and the inventory is behind a
route the site does not publish to a reader that cannot run its scripts»*.

## The rules file, which had not been recorded here

It is the **Cloudflare managed block**: `User-agent: *  Allow: /`, and a list
of named refusals that includes `ClaudeBot: Disallow: /`. **We read it as
`claude-user`**, which the file does not name — the decision of 2026-09-07.

It also carries a content signal, and this card is the first to record one:

```
Content-Signal: search=yes, ai-train=no, use=reference
```

declared as an **express reservation of rights under Article 4 of EU Directive
2019/790**. *`ai-train=no` is not our use — this repository reads advertisements
for a person who is job-hunting, and trains nothing.* `use=reference` covers
that. **It is written here so that the next reader does not have to decide it
again, and so that any future use of this corpus for training meets a refusal
already on record.**

The site's own `*` group additionally refuses `/rj-roundcube/`, `/admin/`,
`/prjmbdd.php` and `/pjmbo/`, none of which is an advertisement.

## The earlier reading, kept — the counts were right

**Do not read the status code as access.**

```
GET /   → 200, 8 598 o
          <div>      1
          <script>   6
          <a>        0        <- the discriminator
          <form>     0
          <title>    absent
          ld+json    absent
          the 5 hrefs point at /build/… assets and two icons
```

**It is an application shell.** The page is a mount point; a browser runs the
scripts and the content appears. **A plain HTTP client — ours, or any
enumerator — receives the shell and nothing else.**

## The control that distinguishes it, so the next reader does not rediscover it

> **The signature is zero content links on a body of several kilobytes — not
> the size.**

**AND THAT CONTROL IS WRONG, established above on this very host.** It cannot
tell an empty shell from a server-rendered Inertia or Turbo response that
carries its data in an attribute. *`rozeegpt.ai` and `recruit-ai.co` were
called by the same test on the same day — **whether they too carry a payload
was never checked**, and this card cannot say.* **The corrected control is to
look for `data-page`, `<script type="application/json">` and similar payload
carriers before concluding that a body of several kilobytes holds nothing.**

*A small body can be a real page. A large body can be a shell. **What separates
them is that a shell links only to its own assets.*** `rozeegpt.ai` and
`recruit-ai.co` gave the same reading — `<div id="root">`, a bundle, no
content — and so did two advertisement URLs on `rozee.pk` that were answered by
someone else's shell.

**A card that wrote "open" on this host would manufacture coverage that does
not exist**, and every aggregate counting open hosts would carry Madagascar.
*That is `bestzambiajobs.com` on a different object: there the rules were
impeccable and the domain had changed hands; here the object is genuinely a
board and its content is not served.*

## What would change this

**A listing route, published by the site or found without guessing.** With one
real listing URL, this board becomes readable today: its response would carry
that page's advertisements in `data-page`, and no browser would be needed.

*The rest of this section was written before the payload was found, and its
premise — «its content is not served» — is retired.* *Reading it needs a browser to run
its scripts — the branch the owner opened on 2026-09-07 for hosts whose rules
open and whose transport refuses.* **This host's transport does not refuse: it
answers `200`.** So it is not that branch either, and it belongs to no route we
have.

**It is not disqualified. It is not qualifiable.** *The distinction matters:
`jobstore.md` is refused, `tanqeeb.md` is unreadable at the rules layer, and
this one serves a page that contains nothing — three different facts that a
single "no" would flatten.*

## Re-measured 2026-09-08 — still indeterminate, and better bounded

**Guard re-taken and it opens**: `/`, `/robots.txt` and every candidate below
answer `read`, `allowed=True`, `certain=True`.

**Six routes tried, six HTTP 404 — and they are real negatives**, because the
application answers a miss with an Inertia payload whose `component` is `404`:

```
/offres  /offre  /emplois  /emploi  /secteur/<slug>  /<slug>      all 404
```

*So «&nbsp;no listing found&nbsp;» here is not «&nbsp;the page was silent&nbsp;»
— the app distinguishes a route from a miss, and said miss six times.*

**The JS bundle names the page components** — `pages/emploi/Index.vue`,
`pages/front/secteur/Liste.vue`, `pages/front/secteur/Show.vue` — **and a
component name is not a route.** *There is no route table in the bundle read
(264 432 o): no Ziggy object, and no string of the shape `/x/y` at all.*

> **What remains is exactly one thing: the route table.** *It is server-side or
> in a chunk not loaded on the home page, and finding it by trying paths cost
> six requests for six 404s — which is the measurement that says to stop
> trying.*

## Its `robots.txt` carries a Content-Signal, and we do not act on it

```
User-agent: *
Content-Signal: search=yes,ai-train=no,use=reference
Allow: /

User-agent: ClaudeBot
Disallow: /
```

**The guard opens because of the 2026-09-07 decision** — a group naming
`ClaudeBot` does not bind `Claude-User` — *and that decision is about
`User-agent` groups, not about content signals.*

**`ai-input` is absent from this signal**, and the file's own preamble says an
absent signal «&nbsp;neither grants nor restricts&nbsp;». *`ai-train=no` does not
describe what this plugin does.* **So nothing here forbids the reading — on
this host.**

### A correction, made before this card was an hour old

**This card first said `_robots.py` recognises `Content-Signal` and never acts
on it. That is false**, and it was published here and reported to the pilot
before being checked.

```
verdict()   collects every Content-Signal line
            flags content_signal_conflict when they disagree
            searches for ai-input=no  ->  sweep = False, with a reason
            "a refusal in any of them is a refusal, because no convention
             says which wins"
ignored_for()  excludes content-signal deliberately — because verdict() reads it
```

**The module handles the directive, and handles it conservatively.** *So there
is no gap here to name, and no tension between the docstring and the code: the
docstring says `ai-input=no` is an operator asking not to be read into an AI
system, and the module refuses on exactly that.*

**How the false claim was made:** *a `grep` for `content-signal` returned the
`_DIRECTIVE` regex and the module docstring, and I read that list as the whole
treatment.* **A grep finds where a name appears, not what a program does with
it** — `verdict()` is 344 lines and the handling is inside it.

*What remains true of this host: `ai-input` is absent from its signal, so
nothing in it forbids the reading.*
