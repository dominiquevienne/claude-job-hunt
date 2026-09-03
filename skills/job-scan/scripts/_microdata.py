#!/usr/bin/env python3
"""Read schema.org **microdata** — the other way a page carries a `JobPosting`.

**Every structured-data reader in this repository parses JSON-LD**, and until
Applifly no board needed anything else. That adapter's ad carries a complete
`JobPosting` and **not one byte of `ld+json` describes it**: it is
`itemscope itemtype="http://schema.org/JobPosting"` with twenty `itemprop`
attributes, coordinates included.

**THE TRAP THAT MAKES THIS WORTH A FILE.** On that page, two reasonable checks
give opposite answers:

    grep -c JobPosting page.html          → 1     "the ad is there"
    json.loads(each ld+json block)        → none  "no structured data"

A string search says yes, a JSON-LD parse says no, **and both are looking at a
real, complete `JobPosting`.** `shared/boards/successfactors.md` established
the first half — *the tell is the block, not the string*. This is the other
half: **the block is not always JSON.**

**IT USES A REAL TAG STACK, NOT REGEX, AND THAT IS NOT A STYLE CHOICE.** The
first version paired properties with items by document order and got two
things wrong on the very first page: the job's `title` came back empty because
the `<h1>` opens with a hidden `<span>`, and the JobPosting's `name` came back
as *"Meanquest SA"* — the nested `Organization`'s name, leaking one level up.
**Microdata nests, so the reader must too**: `html.parser` gives the stack for
free.

WHAT IT STILL DOES NOT DO: `itemref` (which points at content elsewhere in the
document) is ignored, and an item's value is the attribute schema.org names
for that element — `content`, `datetime`, `href`, `src` — or its text. Enough
for a `JobPosting`; said out loud rather than discovered.

    from _microdata import items, first
    posts = items(html, "JobPosting")
    title = first(posts, "title", "name")
"""

import html as html_mod
import re
from html.parser import HTMLParser

__all__ = ["items", "first"]

# schema.org: for these elements the value is an attribute, not the text.
# Getting it wrong returns a logo's alt text where a company name was wanted.
VALUE_ATTR = {
    "meta": "content", "audio": "src", "embed": "src", "iframe": "src",
    "img": "src", "source": "src", "track": "src", "video": "src",
    "a": "href", "area": "href", "link": "href", "object": "data",
    "data": "value", "meter": "value", "time": "datetime",
    # **`input` is not in schema.org's list**, and it is here because a real
    # page put coordinates in one: `<input itemprop="latitude" type="hidden"
    # value="46.5258">`. A spec-pure reader returns a `GeoCoordinates` block
    # with **no properties** — a block that is present and empty, which is the
    # shape this repository keeps catching in board payloads. Reading the
    # attribute costs nothing and turns 0 of 8 into the real number.
    "input": "value",
}

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class _Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []          # every item, in document order
        self._stack = []         # open elements: (tag, item_or_None, prop)
        self._open_items = []    # items whose element is still open

    # -- helpers ---------------------------------------------------------
    def _current_item(self):
        return self._open_items[-1] if self._open_items else None

    def _finish(self, entry):
        tag, item, prop = entry
        if prop is not None:
            name, owner, buf, attrval, nested, own = prop
            if nested is not None:
                # A property that is itself an item: the value is the item,
                # and the parent records its type rather than its text.
                value = direct = nested.get("type")
            else:
                value = attrval if attrval is not None else \
                    re.sub(r"\s+", " ", "".join(buf)).strip()
                direct = attrval if attrval is not None else \
                    re.sub(r"\s+", " ", "".join(own)).strip()
            # **First one wins.** A page repeats `name` for the employer, the
            # location and the breadcrumb; last-wins returns the breadcrumb.
            if value and name not in owner["props"]:
                owner["props"][name] = value
            if direct and name not in owner["props_direct"]:
                owner["props_direct"][name] = direct
        if item is not None and self._open_items and self._open_items[-1] is item:
            self._open_items.pop()

    # -- parser ----------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        item = None
        if "itemscope" in a:
            itype = (a.get("itemtype") or "").strip()
            item = {"type": itype.rstrip("/").rsplit("/", 1)[-1] or None,
                    "itemtype": itype or None, "props": {},
                    "props_direct": {}}
            self.items.append(item)

        prop = None
        if "itemprop" in a:
            owner = self._current_item()
            if owner is not None:
                attrval = None
                wanted = VALUE_ATTR.get(tag)
                if wanted and wanted in a:
                    attrval = html_mod.unescape(a[wanted])
                elif "content" in a:
                    attrval = html_mod.unescape(a["content"])
                prop = (a["itemprop"].strip(), owner, [], attrval,
                        item, [])

        if item is not None:
            self._open_items.append(item)

        entry = (tag, item, prop)
        if tag in VOID or tag.endswith("/"):
            self._finish(entry)
        else:
            self._stack.append(entry)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self._stack and self._stack[-1][0] == tag:
            self._finish(self._stack.pop())

    def handle_endtag(self, tag):
        # Unwind to the matching open tag. Unclosed elements are the norm in
        # real pages; refusing to cope with them would make this useless.
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                while len(self._stack) > i:
                    self._finish(self._stack.pop())
                return

    def handle_data(self, data):
        innermost = self._open_items[-1] if self._open_items else None
        for entry in self._stack:
            prop = entry[2]
            if prop is None or prop[4] is not None:
                continue
            prop[2].append(data)
            # `props` is the spec's value: all the element's text, nested
            # items included. `props_direct` excludes them, and it exists
            # because this page's `<h1 itemprop="title">` wraps a hidden
            # Organization block — so the spec-correct title reads
            # *"Meanquest SA Cheffe / Chef de projet IT Envoyer"*.
            # **Both are right answers to different questions**, and a reader
            # that only had the first would have to guess.
            if prop[1] is innermost:
                prop[5].append(data)

    def close(self):
        super().close()
        while self._stack:
            self._finish(self._stack.pop())


def items(doc, type_name=None):
    """Every microdata item, or only those of `type_name` (bare, no URL)."""
    r = _Reader()
    try:
        r.feed(doc or "")
        r.close()
    except Exception:                      # a malformed page is not a crash
        pass
    out = r.items
    if type_name:
        out = [i for i in out
               if (i.get("type") or "").lower() == type_name.lower()]
    return out


def first(blocks, *names):
    """The first non-empty value among `names`, across `blocks`."""
    for b in blocks or ():
        for n in names:
            v = (b.get("props") or {}).get(n)
            if v:
                return v
    return None


def _main():
    import argparse
    import json
    import sys
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True)
    p.add_argument("--type", default=None)
    a = p.parse_args()
    doc = open(a.file, encoding="utf-8", errors="replace").read()
    blocks = items(doc, a.type)
    if not blocks:
        print("[microdata] no itemscope block"
              + (f" of type {a.type}" if a.type else "")
              + " — an absence of microdata is not an absence of an ad: the "
                "page may carry JSON-LD instead.", file=sys.stderr)
    print(json.dumps(blocks, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
