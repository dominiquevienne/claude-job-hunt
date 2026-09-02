# Which language to ask a market in

<!-- verified: 2026-09-02 -->

**A search term carries a language, and a market answers in its own.** On
Adzuna's Swiss index, 2026-09-02:

| `what=` | Matches |
| :-- | --: |
| `Entwickler` | **12 691** |
| `developer` | 3 162 |
| `informaticien` | 129 |
| **`développeur`** | **0** |

Same board, same market, same hour. `job-scan` builds its search terms from
the user's own profile, so **a French-speaking user searching in French is
handed an empty market that has twelve thousand jobs in it** — HTTP 200, an
empty list, no error, and the natural reading is that nobody is hiring.

`shared/never-fail-silently.md` (point 3c) says why that is the worst shape of
failure here. `skills/job-scan/scripts/_zero.py` makes the zero speak. **This
page is what it can say next**, and `_language.py` is where the data lives.

## 1. The market's languages come from a map, the person's from the person

The obvious fallback — *look at the language of the ads already read* — is
**circular exactly where it is needed**: the search returned nothing, so there
is nothing to look at. The map has to be primary.

`MARKET_LANGUAGES` in `_language.py` is deliberately short: `be`, `ca`, `ch`,
`es`, `fi`, `lu`. **A country absent from it is not a monolingual country — it
is a country nobody has measured here.** Adding a row is cheap; inventing one
is the guess this whole page refuses.

**But the market's languages are not the answer on their own.** A German search
on a Swiss board returns German ads, and German ads mostly require German.
Pouring 12 691 of them onto somebody who does not speak the language replaces
a misleading zero with a misleading flood, and they sort it by hand.

**So the third source is the user**, and setup already collects it:
`languages.working` in `config.yml`.

> **The rule: search the market's languages *that the person works in*, and
> say what the others return.**

On this case that is one sentence — *your French search returns 0; the same
index returns 12 691 in German, a language you have not declared* — and the
person decides. Not hiding the German market, not dumping it. That is issue #48
applied properly: **give the person what they need to steer, do not steer for
them.**

## 2. The table records measurements, not translations

`MEASURED` holds entries of the shape *this term, on this market, returned this
many, on this date, on this board*. It never holds *this word means that word*.

- **A measurement is checkable and refutable.** Re-run it.
- **A translation is neither, and it ages without saying so** (issue #72).

### How to read an entry: its order of magnitude and its zero, nothing finer

The index moves during a day. Measured hours apart on 2026-09-02:
`informaticien` **138 → 129**; `Entwickler` **12 666 → 12 691**. Those are the
same measurement twice. **12 691 and 0 are not.**

**Do not refresh an entry for a 7% drift.** Refresh it when a term that
returned thousands returns none, or the reverse. An entry that gets rewritten
every time somebody looks stops being a record and becomes noise.

## 3. A term that is not in the table produces silence

Not a guessed translation. **A guessed term that also returns zero manufactures
a second zero, and two zeros read as a certainty** — one invented here, in the
one place the user has no way to check.

**Finding no equivalent is information. Inventing one is not.**

## 4. The extra pass fires on zero, and only on zero

Issue #70 is about **not lying**, not about recall. Repairing it does not
require finding more ads; a systematic multilingual pass is a different feature
with a different cost — three languages is three times the requests on boards
that already back off — and it must not arrive under this justification.

## What this does not cover, with the numbers

**1. A thin result misleads as much as an empty one, and nothing fires on it.**
`informaticien` returns **129 of the Swiss index's 81 516 ads** — 1% of the
market. It is not zero, so `_zero.py` stays quiet and none of this is reached.
The trigger is strict on purpose; **this paragraph is where the step is, for
whoever comes next.**

**2. The category route does not rescue it.** Adzuna's 30 category tags are
identical across countries and genuinely language-independent — a sample of
`category=it-jobs` on `ch` with no keyword returns French, German and English
titles together. **But the classification is mostly empty:**

| Index | Ads | `category=unknown` | `it-jobs` |
| :-- | --: | --: | --: |
| **ch** | 81 516 | **57 663 — 70.7%** | 1 150 |
| fr | 965 545 | 477 585 — 49.5% | 13 293 |
| de | 1 211 402 | 822 462 — 67.9% | 23 034 |

`category=it-jobs` returns **1 150** where `what=Entwickler` alone returns
**12 691**. A category sweep would announce 1 150 IT jobs in Switzerland where
there are twelve thousand — issue #70 again, in better manners. `adzuna.py`
warns on `--category` for that reason, and the flag stays: **it narrows a
keyword search, it does not sweep a market.**

*(The classification is not clean either: a `Lehrstelle Küchenangestellte/r` —
a kitchen apprenticeship — sat in `it-jobs` in the sample.)*

**3. The language detector that is not here.** A stopword scorer written to
measure the language mix inside a category called 26 of 50 plainly French ads
Italian. The distributions quoted above are **read off the titles by eye**, and
no language detector ships in this repository. If one ever does, it needs to
report its own confidence — a wrong language label is a plausible false field,
which is issue #67.

## Using it

The adapters do not read `config.yml` — none here does. **The skill passes the
languages down**, and only the boards that can take them:

```bash
python3 skills/job-scan/scripts/adzuna.py search --country ch \
    --what "développeur" --speaks "French, English"
```

`--speaks` is used **only when a search returns zero**. A name it cannot read
is named and ignored, never guessed at.
