#!/usr/bin/env python3
"""Read a board card's declarations — **once, and the same way everywhere.**

    from _cards import declarations, card_script, shares_platform

A card in `shared/boards/` opens with HTML comments that declare facts about
the board: which hosts it covers, which script drives it, what was measured,
which other card shares its platform. **Those declarations had no reader.**
Every consumer wrote its own regular expression, and they disagreed.

WHY THIS MODULE EXISTS RATHER THAN A NEW KEY — #159

The issue proposed adding a `driver:` key to say what `script:` was being asked
to say. **The measurement pointed the other way.** Seven cards declare
`script: none`; six places read the key, in **two different shapes**:

    re.search(r"<!--\\s*script:\\s*([a-z0-9_]+\\.py)\\s*-->", …)   skips `none`
    re.search(r"<!--\\s*script:\\s*([^\\s>]+)", …)                 captures "none"

The first is **right by accident** — `none` has no `.py`, so it fails to match
and the caller sees nothing, which happens to be correct. The second carries
the string `"none"` onward as if it were a filename. *A second key would have
to be kept in step with a first key that is already read six ways.*

**So: no new key. One reader, and the existing guard becomes the rule instead
of an exception repaired afterwards.**

WHAT `shares-platform:` IS FOR, AND WHY IT WAS INERT — #170

`jobup.md` and `jobs-ch.md` both declare:

    <!-- shares-platform: … · the same posting UUID appears on both -->

**Nothing consumed it.** One test checked the line was well formed; no code
ever asked it a question. So `job-scan` step 3 compared **whole ledger ids** —
`jobup:<uuid>` against `jobs-ch:<uuid>` — found them different, and let the
advertisement through. Seven passed in one morning, **one of them the twin of a
row already at status `applied`**.

The declaration was written, guarded for shape, and never read: a step wired
end to end that nobody walks. This module is the reader.
"""

import os
import re

# **A card's declarations, whatever the key.** One pattern, so a new key is
# readable the day it is written rather than the day somebody adds a regex.
_DECL = re.compile(r"<!--\s*([a-z][a-z0-9-]*)\s*:\s*(.*?)\s*-->", re.S)

# The words a card uses to say *there is no script, and that is the finding*.
# `chile-public-sector.md`: "This card declares no adapter, and that is the
# finding, not an omission."
NO_SCRIPT = ("none", "-", "—", "n/a")


def declarations(src):
    """Every `<!-- key: value -->` in the card, first occurrence wins.

    First wins because a card's declarations sit in its head; a later comment
    in prose is illustration, not declaration.
    """
    out = {}
    for key, value in _DECL.findall(src or ""):
        out.setdefault(key, " ".join(value.split()))
    return out


def card_script(src):
    """The script that drives this card, or `None` when it declares none.

    **`None` and `"none"` are different answers and one of them is a bug.**
    Returns the bare filename — `jobup.py` — never a path, and never the word.
    """
    value = declarations(src).get("script", "").strip()
    if not value or value.lower() in NO_SCRIPT:
        return None
    return value


def shares_platform(src):
    """The card names that share this board's posting identifiers.

    Returns bare card names without the `.md` — `["jobs-ch"]` — because that
    name is also the ledger prefix the adapter writes. **That correspondence is
    a convention, so it is asserted in the suite rather than assumed here.**
    """
    value = declarations(src).get("shares-platform", "")
    names = []
    for chunk in re.split(r"[·,]", value):
        m = re.match(r"\s*([a-z0-9][a-z0-9._-]*\.md)\b", chunk)
        if m:
            names.append(m.group(1)[:-3])
    return names


def platform_siblings(boards_dir):
    """`{prefix: [sibling prefixes]}` for every card that declares a sharing.

    Read from the cards rather than hard-coded: a third brand joining the
    platform is covered by its card, not by remembering to edit a list.
    """
    out = {}
    for name in sorted(os.listdir(boards_dir)):
        if not name.endswith(".md") or name == "README.md":
            continue
        with open(os.path.join(boards_dir, name), encoding="utf-8") as fh:
            sibs = shares_platform(fh.read())
        if sibs:
            out[name[:-3]] = sibs
    return out


def same_posting_ids(ledger_id, siblings):
    """Every ledger id that would name **this same advertisement**.

    `siblings` is what `platform_siblings()` returned.

        same_posting_ids("jobup:abc", sibs) -> ["jobs-ch:abc", "jobup:abc"]

    **This is the check step 3 was missing.** Comparing whole ledger ids finds
    `jobup:abc` and `jobs-ch:abc` different, because they are — as strings.
    They are the same posting.

    An id with no `:` is returned alone: it is not a namespaced ledger id, and
    guessing a prefix for it would invent an identity.
    """
    if ":" not in (ledger_id or ""):
        return [ledger_id] if ledger_id else []
    prefix, ident = ledger_id.split(":", 1)
    out = {ledger_id}
    for sib in siblings.get(prefix, ()):
        out.add(f"{sib}:{ident}")
    return sorted(out)
