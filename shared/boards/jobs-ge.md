# Board adapter — jobs.ge (Georgia, independent)

<!-- verified: 2026-09-03 -->

<!-- hosts: www.jobs.ge -->
<!-- script: jobsge.py -->
Georgia's independent generalist, unrelated to the HR.ge platform. **No key, no
cookie, no browser — and no pagination.**

**The home page carries every live vacancy**: **308** distinct ad ids on
2026-09-03, identical on both language versions, with no `page` parameter
anywhere on it. **A complete sweep costs one request.**

## `robots.txt`, and a rate limit that is read rather than chosen

**54 bytes:**

```
User-agent: *
Disallow: /data/clients/
Crawl-delay: 5
```

No sitemap, **no AI agent named**, and one directory closed. **`Crawl-delay: 5`
is the first explicit rate limit in this repository's adapters**, and
`jobsge.py` uses it as its default. **It is a value read from the site, not a
number this project picked** — nobody should later "optimise" it downward.

## The site declares its own stub, and it goes both ways

The same advertisement, in two languages:

```
/en/?view=jobs&id=749603     581 visible characters
                             "See full text of this announcement in Georgian"
/ge/?view=jobs&id=749603   3 910 visible characters — the whole posting
```

**Measured on twelve advertisements sampled across the board:**

| | |
| :-- | --: |
| English pages that are stubs | **11 of 12** |
| **English pages that are the complete text** | **1 of 12** |

**And the twelfth is the mirror, not an exception to be waved away.** For
`749690` the **Georgian** page is 772 characters and says *"იხილეთ ამ
განცხადების სრული ტექსტი ინგლისურ ენაზე"* — *see the full text of this
announcement in English* — while the English page carries the advertisement.

**So "Georgian is the complete one" is false**, and the adapter does not
believe it. It reads the language asked for, and **when the page says it is a
stub it follows the pointer to the other language and says it did.** The site
declared the switch; nothing here guessed it.

### Length is not the test, and the sample says so

English stubs ran **623 to 767** visible characters. That looks like a clean
threshold — until one sampled advertisement's **complete** Georgian page came
in at **767 characters**, shorter than several stubs.

> **A string the site prints needs no threshold. A ratio needs one, and the
> threshold is where it fails.**

A length rule would have called that complete page a stub, and a mean ratio
would have measured how long Georgian advertisements are as much as how much
English is missing.

## A string that describes the feature you want, and is an advertisement

The ad page contains the words **"All Job Ads on a Single Page"** — which is
exactly the full-board view an adapter looks for. **It is the caption of a
banner ad for one employer.**

It belongs with `encuentra24.md`'s `jobs-job-offers`, the guessed URL that
*answers*: both qualify themselves to us by plausibility alone, and neither is
what it says. **A name that answers and a string that describes are the two
ways a search finds something that is not there.**

## What a card yields

`<title>` is `JOBS.GE - <role> - <employer>` in both languages, and it is the
only place either appears as a clean field. Dates come as *"Published: 02
September / Deadline: 02 October"*.

**The dates are emitted as printed — a day and a month name, no year.** Not
normalised: guessing the year across a December/January boundary is exactly the
quiet error this repository keeps finding.

## Configuration

```yaml
boards:
  jobsge:
    enabled: true
    lang: ge          # `en` is a stub on 11 ads in 12
    delay: 5          # published in robots.txt — do not lower it
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `lang` | no | `ge` by default. Either way the adapter follows the stub pointer |
| `delay` | no | **5 seconds, and that is the site's own figure** |

No credentials, no login, no browser.

## Zero-shaped answers

**1. An English page answering `200` with one sentence.** Eleven in twelve.

**2. And the reverse**, once in twelve — so a rule that fixes the first by
hardcoding a language breaks the second.

**3. A complete page shorter than a stub.** 767 characters against stubs of up
to 767.

**4. A banner captioned like the feature you were looking for.**

**5. A date field that swallows the advertisement.** Reading
`Deadline:\s*([^\n<]+)` off flattened text has no newline to stop at: 3 400
characters of body arrived as a deadline. Bounded to a day and a month.

## Applying

Through the ad URL, in the user's own browser. Most advertisements print an
application e-mail address in their body; **the plugin does not send it for
them.**

## Pace

**5 seconds between requests, from `robots.txt`.** The home page is ~394 kB and
an ad ~14–24 kB, so a full enumeration is one request and reading everything is
308 more — at the published pace, that is a deliberate, slow sweep and should
be run against a filtered list rather than the board.

## Verification

```bash
S=skills/job-scan/scripts/jobsge.py
python3 $S search --limit 5                 # 308 in one request
python3 $S --lang en ad --id 749603         # follows the stub to `ge`
python3 $S --lang ge ad --id 749690         # follows the stub to `en`
python3 $S compare --sample 12              # 11 of 12, and the mirror
```
