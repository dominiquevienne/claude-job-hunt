# The page-JS output channel stops at 1 000 characters, and the cut is silent

**#1241.** A board card tells a session to run a snippet in the user's browser
and read what it returns. **The channel that carries that return —
`javascript_tool`, alone or inside `browser_batch` — stops at exactly 1 000
characters and appends a literal `[TRUNCATED]`.** What the page computed is
intact; only the way back is short.

## Measured, 2026-11-01, on a bench of our own

A page served on `127.0.0.1` carrying a payload of 10-character blocks, each
block printing its own index, so the surviving length is read off the last
block rather than counted. No third-party host took part, and no site content
was needed: the object under test is the channel.

| call | asked | came back |
| :-- | --: | :-- |
| `javascript_tool`, standalone | 6 000 char. | 1 000 then `[TRUNCATED]` |
| `javascript_tool`, inside `browser_batch` | 1 010 char. | 1 000 then `[TRUNCATED]` |
| `javascript_tool` | **1 000 char.** | **1 000, whole, no marker** |
| `javascript_tool`, 700 accented char. (1 400 bytes) | 700 char. | **whole** — the ceiling counts CHARACTERS, not bytes |
| `get_page_text` on the same page | 6 000 char. in an `<article>` | **6 000, whole** |

**The positive control is the line that makes the rest mean something:** the
same call shape returning 100 characters came back entire, and
`document.querySelector('article').innerText.length` returned **6 000** — so
the page held the whole text while the channel delivered a fifth of it. The
loss is at the output, not at the read.

## The number a caller actually gets is SMALLER, and that is the trap

The ceiling applies to the **whole result**, framing included. A snippet that
returns three fields spends its budget on the first two:

```
JSON.stringify({t: 90 char., m: 140 char., d: <long>})
  -> the `d` field comes back at 750 characters, and the JSON is left UNTERMINATED
JSON.stringify({d: <long>})
  -> 994 characters of `d`, same unterminated end
```

> **So «1 000» and the «roughly 600 to 700» first reported on LinkedIn are the
> same measurement from two ends, not a disagreement.** *1 000 is the channel;
> 750 is what a description gets once a title and a metadata line are in the
> same object; and a real description escapes to more characters than it has
> — every newline becomes `\n`, two characters — which lands it in the 600s.*

**And the result is not merely short: it is invalid JSON.** The cut falls
inside a string, so a consumer that parses raises, and a consumer that reads
the text keeps the fields it can see and never learns the last one was
amputated.

## Who this hits — derived, not listed

The exposed cards are those carrying a fenced `js` block that returns a
description. Two motifs of different forms agree on the same four, and their
difference is empty either way: a `d:` key inside a `js` fence, and a file
carrying both `innerText` and `JSON.stringify`.

| card | what its block returns for `d` | what comes back |
| :-- | :-- | :-- |
| `shared/boards/linkedin.md` | `.slice(0,1500)` | **750 char.**, with `t` and `m` filled |
| `shared/boards/indeed.md` | **unbounded** | cut wherever 1 000 falls |
| `shared/boards/jobs-ch.md` | **unbounded** | idem — and it also ships `jobup.py`, so the browser is its second route |
| `shared/boards/jobup.md` | **unbounded** | idem |

**A declared bound of 1 500 is nearer to honest than no bound at all**: it at
least says what was asked for. The three unbounded blocks promise the whole
description and return a prefix, with nothing in the snippet to compare
against.

## Conduct

1. **A description is read with `get_page_text`, never returned from page JS.**
   It returned 6 000 of 6 000 on the bench, it names its source element, and it
   has no framing to pay for.
2. **Page JS returns what is SHORT and STRUCTURAL** — ids, counts, booleans,
   a title, which is what it is good at and what no other tool gives.
3. **If long text must come back through page JS, it is paged in slices under
   1 000 characters INCLUDING the framing**, and each slice says its offset so
   a missing one is visible.
4. **`[TRUNCATED]` in a result is read, never skimmed.** It is the only signal,
   it is a literal in the text, and everything before it looks complete.

## What is NOT established

- **The extension's version.** `list_connected_browsers` exposes
  `deviceId`, `name`, `osPlatform`, `connectedAt`, `isLocal` and `inUse`, and
  no version; two scans of the Chrome profile on disk returned **zero
  manifests**, which is a zero that says «I did not look in the right place»,
  not «absent». So the 1 000 is dated and attached to this machine, and it is
  not attached to a build.
- **Whether the ceiling moves with the extension version or the host.** One
  machine, one day. A reading that disagrees is a second measurement, not a
  refutation of this one — and it should carry its own date.
- **Whether `read_page` and `find` have ceilings of their own.** Not measured.
