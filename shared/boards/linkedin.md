# Driving LinkedIn through browser automation — hard-won constraints

<!-- hosts: www.linkedin.com -->
<!-- countries: * -->

Read this **before improvising** any LinkedIn automation. Every line below was
established by trial; ignoring one costs many wasted round-trips, and two of
them cost a lost application.

**Re-verified against the live site on 2026-08-28.** The constraint table held —
25 cards in the DOM, **7 hydrated**, on a search reporting 2 259 results. What
changed is recorded in the two traps at the end of this file, and one bug in the
extraction snippet was corrected.

Applies to both skills: scanning search results (`job-scan`) and filling an
Easy Apply form (`cover-letter`).

## Configuration

This adapter runs only when it is switched on in the user's `config.yml`:

```yaml
boards:
  linkedin:
    enabled: true
    profile_url: "https://www.linkedin.com/in/<handle>"   # required
```

| Key | Required | How the user gets it |
| :-- | :-- | :-- |
| `enabled` | yes | Set by `/job-setup`, or by hand. False or absent → this board is not scanned at all |
| `profile_url` | yes | Their own LinkedIn profile page URL: open LinkedIn → **Me** → *View profile* → copy the address bar. The handle is the last path segment, and it is what builds the `/details/…` export URLs |

If `enabled` is true and `profile_url` is empty, **skip the board and say which
key is missing** — offer to fill it there and then. Never sweep with a guessed
handle.


## What `linkedin.com/robots.txt` says about us, and why this adapter is still legitimate

**Verified 2026-09-02, hand-written and not a managed block:** `ClaudeBot`,
`Claude-Web`, `Claude-User` and `anthropic-ai` all get **`Disallow: /`**, and
`Claude-SearchBot` gets a narrower refusal (`/public-profile/`,
`/people/search/`). **`Claude-User` — the agent that fetches because a person
asked — is refused with the rest.**

**So no automated fetch of LinkedIn by our agents is permitted by that file,
and this adapter does not make one.** It drives **the user's own Chrome, in
the user's own logged-in session**: that is the person browsing their own
account, which their own use of the site governs, not a crawler.

**The distinction is ours to state, not to assume** — LinkedIn's file is
exactly the document that declines to draw it, and `shared/reading-terms.md`
is explicit that being a user-driven tool is never a reason to argue past a
publisher who named us. It is a reason to be clear about which act is
happening.

**Practical consequence: never fetch a LinkedIn URL from a script here.** Not
in `cover-letter`, not in a checker, not to verify an ad is still open. If a
LinkedIn page needs reading, it is read in the user's browser or not at all.

## Prerequisites — say these out loud before touching the browser

Browser automation here is not a background capability: it needs two things
from the user, and both fail silently-looking ways if they are missing. **Tell
the user before you start, not after the first error.**

1. **The Claude extension for Chrome must be installed and connected.** Without
   it there is no browser at all — the `mcp__claude-in-chrome__*` tools are
   simply absent or return no connected browser. If you cannot reach a tab,
   say exactly that: *"this step drives your own Chrome and needs the Claude
   Chrome extension installed and connected; without it I can still produce
   your documents, but I cannot open or fill anything for you."* Then continue
   with everything that does not need a browser rather than stopping the run.
2. **The user must already be logged in to the site, in that Chrome, before
   you begin.** This automation works *inside their session* — it does not and
   must not authenticate on their behalf, and it never handles their password.
   Ask them to log in first, in as many words, and wait for confirmation:
   *"open <site> in Chrome and log in, then tell me when you're in — I work in
   your session and I won't sign in for you."*

If a page comes back showing the logged-out layout, that is the diagnosis:
name it (*"LinkedIn is showing me the signed-out page"*), give the URL, ask
the user to sign in, and resume when they confirm. Never try to work around a
login wall, and never fill a credential field.

## Setup

Load the browser tools in ONE call:

```
ToolSearch "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__form_input,mcp__claude-in-chrome__file_upload,mcp__claude-in-chrome__tabs_create_mcp"
```

Then `tabs_context_mcp{createIfEmpty:true}` and work in that tab. **This runs in
the user's own logged-in Chrome** — say so before starting, since it acts under
their identity. If a page returns the logged-out layout, stop and ask them to
log in rather than trying to authenticate.

## The constraint table

| Constraint | Consequence |
| :-- | :-- |
| The automated tab is **usually** `document.hidden === true` (its window is in the background) | `setTimeout` is throttled to ~1 s per tick. An in-page loop of 25 × 200 ms sleeps **times out the 45 s CDP budget**. Never sleep in page JS — use `computer{action:"wait"}` between steps inside a `browser_batch`. **It is not an invariant** — see the last trap |
| The results list is virtualized **and** the tab is hidden | Only the **first ~7 job cards** ever hydrate. Scrolling the list (window, container, or `scrollIntoView`) does **not** hydrate more. Do not fight it: run **more, narrower searches** instead of trying to read 25 results from one |
| The job description pane only loads on a **real** mouse click on a card | `element.click()` from JS updates the URL but renders nothing. `/jobs/view/<id>/` standalone renders nothing either. You must `screenshot` → read the card's y-position → `computer{left_click}` at those coordinates |
| `fetch()` of `/jobs/view/...` or `/jobs-guest/jobs/api/...` | Returns HTTP **999** or an empty body. There is no API shortcut |
| `localStorage` is unavailable in the injected world | Silently no-ops. Accumulate results in the tool output, not in the page |
| Returning `location.href` (or anything carrying a query string or cookie) from `javascript_tool` | The whole result is replaced by `[BLOCKED: Cookie/query string data]`. **Never return URLs from page JS** — rebuild them from the job ID |
| Modal buttons ignore synthetic clicks | Same rule as the cards: `screenshot`, then a real `computer{left_click}` at the coordinates you read off it |

## Pace

Pace it like a human reading job ads: a few dozen page views, not hundreds. Do
not batch-open every result — the session gets throttled, and the throttle lands
on the user's real account, not on a scraper.

## Building a search URL

`sortBy=R` is relevance; relevance decays fast, so the top ~7 results are the
useful ones — which is exactly what hydrates (see the constraint table).

```
https://www.linkedin.com/jobs/search/?keywords=<terms>&location=<place>&sortBy=R
   &distance=50          # miles around the location. This is a net, not the commute
                         # rule: it is measured from the search city as the crow flies,
                         # so it still returns unreachable ads. The commute filter in
                         # shared/scoring-rubric.md is what actually discards them.
   &f_TPR=r2592000       # posted within: r604800 = week, r2592000 = month,
                         # r7776000 = 3 months. Map from search.posted_within
   &f_WT=2               # remote only (1 = on-site, 3 = hybrid). Set when the
                         # query has remote_only: true
```

Quoting a keyword (`keywords="Laravel"`) matches it strictly — four results
instead of six hundred of noise. Unquoted keywords are matched very loosely (a
"PHP" search returns junior Python jobs), so **always sanity-check the titles**.

## The ad id and its URL

The id is `data-occludable-job-id` on the result card. In the ledger it is
recorded **prefixed**, as `linkedin:<ID>`. Rebuild the canonical URL from it:

```
https://www.linkedin.com/jobs/view/<ID>/
```

**Never scrape the URL out of the page** — see the constraint table: returning
anything with a query string from page JS blocks the whole result.

## Before extracting anything: is this search a zero?

**A LinkedIn zero is not an empty card list.** A search that matches nothing
renders **seven or eight real, live, unrelated ads** — browsing-history
recommendations — and nothing in the extracted text says they are not results.
Measured 2026-09-01 on `?keywords="Laravel"&location=Switzerland`:

| Signal | Value |
| :-- | --: |
| Page text says *No matching jobs found* | **true** |
| Page text says *Jobs you may be interested in* | **true** |
| `li[data-occludable-job-id]` matched | **8** |
| …of those, inside `.scaffold-layout__list` | **8** |

**Scoping the selector to the results container does not separate them** — on a
zero-result page the suggestion block is rendered *inside* it. Seven unrelated
ads were about to enter the ledger as new Laravel matches in Switzerland for a
query whose true answer is zero. Issue #46.

**So run this first, and act on it before mapping any card:**

```js
(()=>{const t=document.body.innerText;
 const ZERO=[/No matching jobs found/i,/Aucune offre correspondante/i];
 const SUGG=[/Jobs you may be interested in/i,/Offres susceptibles de vous int/i];
 return JSON.stringify({
   noResults: ZERO.some(r=>r.test(t)),
   suggestions: SUGG.some(r=>r.test(t)),
   knownLanguage: /\b(jobs?|results?|offres?|résultats?)\b/i.test(t),
   cards: document.querySelectorAll('li[data-occludable-job-id]').length
 });})()
```

- **`noResults` true → the search is a genuine zero.** Report the zero and
  **discard every card on the page**, whatever the count.
- **`suggestions` true while `noResults` is false** → the page mixes both.
  Extract, and say in the run report that a suggestion block was present.
- **`knownLanguage` false** → *the guard could not read this interface
  language*. **Do not treat the extraction as verified**: say so, and let the
  user look. **A search that could not be checked is not a search that
  returned results** — the two strings above are the only ones measured, and
  the banner is localised.

**Card count can never establish a zero on its own**, and the previous version
of this file said the selector *"does not reach"* the recommendations — true on
a page with results, false on a page without. That is the shape this repository
calls *measured in one condition, written as general*.

## Extracting search results

Returns no URLs, so it is never blocked:

```js
const N=/^(with verification|Viewed|Promoted|Easy Apply|Company review|You.{0,3}d be a top|Applied|Within the past|Actively reviewing|Be an early applicant|Response managed|.*works here|.*alum.*|Reposted)/i;
JSON.stringify([...document.querySelectorAll('li[data-occludable-job-id]')].map(li=>{
  const p=li.innerText.split('\n').map(s=>s.trim()).filter(Boolean); const t=p[0];
  return {i:li.getAttribute('data-occludable-job-id'), s:[t,...p.slice(1).filter(s=>{
    // The verification badge FOLLOWS the title on its line — it never starts it,
    // so N's ^-anchored `with verification` alternative never fires. Strip the
    // suffix, then compare to the title.
    const b=s.replace(/\s+with verification$/i,'').trim();
    return b!==t&&s!==t&&!N.test(s);
  })].join(' · ')};
}).filter(c=>c.s.length>3))
```

An `Applied` marker on a card means the user **already applied** — record it as
such instead of proposing it again.

### Traps found on re-verification, 2026-08-28

**The number in the page title is the messaging badge, not the result count.**
`(25) developer Jobs in Switzerland | LinkedIn` on a search reporting **2 259
results**, and `(25) "Laravel" Jobs in Lausanne | LinkedIn` on a search
reporting **2** — the same `(25)` both times, because it counts unread messages.
Read the count from the list header (`… results`), never from `document.title`.

**The left column continues past the results.** Below the last card sit *"Are
these results helpful?"*, *"Expand your search"* and **"Top job picks for you"**
— recommendations built from the profile, not results for this query. The
selector above is scoped to `li[data-occludable-job-id]`, and **on a page that
has results it does not reach them; keep it that way.** A looser selector
silently mixes recommendations into the sweep, attributed to a search they
never matched.

**On a zero-result page it does reach them**, which is the whole of issue #46
and why the guard above runs first. This trap and that one are the same block
of ads seen from two pages, and only one of the two pages was measured when
this paragraph was written.

**`document.hidden === true` is the normal case, not a guarantee — and the
click rule follows from it.** Observed once, on 2026-08-28, while the user had
the Chrome window in the foreground: `document.hidden` was `false`, and the
description pane **rendered on plain navigation, with no click at all**. The
moment the window went back to the background, `hidden` returned to `true` and
the pane stayed empty — verified after 6 s and again after a further 8 s, so it
is a block and not slowness.

So the constraint table is right about what to *do* (screenshot, then a real
click), and the reason is narrower than it reads: **LinkedIn defers rendering
the detail pane while the tab is hidden.** Do not build on the foreground
behaviour — it depends on where the user's attention is, which the plugin does
not control and must never assume.

## Extracting one job description

After a real click on the card, plus `computer{wait:4}`:

```js
const q=s=>(document.querySelector(s)?.innerText||'').replace(/\s+/g,' ').trim();
JSON.stringify({
  t:q('.job-details-jobs-unified-top-card__job-title').slice(0,90),
  m:q('.job-details-jobs-unified-top-card__primary-description-container').slice(0,140),
  d:q('#job-details').slice(0,1500)
})
```

**Confirm `t` matches the ad you meant to open** — the list re-orders between
visits, so the card at a given y-coordinate is not stable across navigations.

Several clicks on the same search page chain nicely in one `browser_batch`
(click → wait → extract, repeated): one screenshot, then 3–6 descriptions.

## Easy Apply — established 2026-08-26, NOT re-verified since

Everything from here to the end of the file dates from **2026-08-26** and was
**deliberately left out of the 2026-08-28 re-verification**: exercising it means
driving a real application form on the user's real account, on an ad they may
not want to send. It is the oldest standing claim in this file, and
`bin/adapter-age.sh` reports the file by this date because of it.

Treat these sections as the most likely to have rotted, and re-verify them the
next time an Easy Apply is run for real.

## The Easy Apply modal may be invisible to the accessibility tree

LinkedIn has been migrating Easy Apply to an SDUI flow (the job link carries
`openSDUIApplyFlow=true`, and the modal footer reads *Application powered by
Workable*). In that flow `read_page` and `find` return the underlying job page
and report **no modal at all**, even though it is plainly on screen.

Do **not** conclude the modal failed to open. Take a `screenshot`, confirm it
visually, and drive the whole flow by coordinates: `computer{left_click}` on
fields, `computer{type}` for text, `cmd+a` then `Delete` to clear a field before
retyping. `form_input` needs a `ref` and is unusable there; so is `file_upload`.

Scrolling in that flow needs care too: the modal has its own scroll container,
and a `scroll` aimed at its upper half often scrolls the page *behind* it. Aim
low inside the modal, near its footer, and confirm on the next screenshot that
the modal content actually moved.

## Click *Easy Apply* exactly once

The button stays visible while the page is still loading, and a second click
lands *behind* the modal the first one opened — which LinkedIn reads as
dismissing it, raising a *Save this application? / Discard / Save* prompt. If
that appears, close it with its **X**: *Discard* throws the application away and
*Save* closes the modal.

## Never click a file input or an "Upload" button

It opens a native file picker that cannot be seen or controlled, and the session
hangs. Use `read_page` or `find` to get the input's `ref`, then `file_upload`
with an absolute path.

When there is no `ref` — the SDUI flow above — **this is a dead end by design,
not a failure to route around**. Hand it to the user: open the folder so the
file is one click away, name the exact button and the exact filename, and ask
them not to advance the form until you resume.

## Never trigger a native dialog

`alert`, `confirm`, `prompt` and browser modals block every subsequent command
and kill the session. If one appears by accident, tell the user it must be
dismissed by hand in their browser.
