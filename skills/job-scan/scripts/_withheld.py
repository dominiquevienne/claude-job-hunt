#!/usr/bin/env python3
"""A name in `withheld_fields` does not carry its CLASS — #1238, item 3.

    from _withheld import withheld_a_contact

    r = {..., "withheld_fields": noms}
    if withheld_a_contact(noms):
        r["contacts_withheld"] = True

**WHY THIS IS NOT A PREDICATE EACH ADAPTER CAN WRITE FOR ITSELF.** `withheld_fields`
answers "what did the document carry that this record does not", and that mixes two
unrelated things: something that **reaches a person** (an e-mail, a number, an address
to write to) and something dropped for a reason that has nothing to do with a contact
(a criterion #183 refuses to propagate, the vacancy's own latitude, a link nobody can
follow). `contacts_withheld` answers only the first. **Deriving it from the whole list
declares that a contact was withheld for a record where only the applicant's gender
was dropped** — which is #1007's defect, "declaring you withheld what nobody filed",
one class further along.

Three of the seven sites #1238 names mix the two classes, and one of them mixes them
*in a way no list can show*: `govtlc` puts `coordinates` in every record, because
every item carries Latitude/Longitude. **So a truthiness test on that list is True for
every record forever** — the derivation would look done and measure nothing.

WHAT WAS MEASURED, AND IT IS NOT A DENOMINATOR OF THREE

`#1238` opened on three Adecco Italy pages where `scrub` removed nothing while the
record said `True`. Item 1 closed that: of **N = 665** records emitted by the nine
boards whose bodies this repository holds, **K = 16** carried a redaction marker —
and on the **200** `acbar` records held with their provenance, the declaration is
`True` with an **empty** witness on **200 of 200**. That is the population, and it
is exact rather than a bound: `withheld_fields` is emitted on every one of them.

A LOCUS PREFIX IS NOT A CLASS

Five adapters namespace their witness — `description:e-mail`, `body:telephone`,
`company.phone`, `description.email`, `advertiser:phone`. The prefix records WHERE the
value sat in the document and the suffix records WHAT it was, so `classe()` judges the
suffix when the whole name is unknown. **Listing the prefixed spellings instead would
grow this vocabulary by one entry per adapter per field, forever**, and each entry
would have to be kept in step with a file nobody opens while editing this one.

THE DEFAULT CASE FAILS VISIBLY, ON PURPOSE

A name this module does not classify raises. The other two designs both lie: an
unknown name read as a contact **over**-declares (the #1236 lie), read as a
non-contact it **under**-declares — a contact removed and not said. Neither is safe,
so the sort has no default (`CLAUDE.md` §4: when a sort has a default case, choose the
one that fails visibly). The names are literals in our own source, never values off
the network, so the raise can only fire while a developer is adding one — and
`tests/test_core.py` asserts the vocabulary covers every name the carriers emit.
"""

# reaches a person
CONTACT = frozenset({
    "email",
    "telephone",
    "phone",
    "postal_address",
    "employer_email",
    "employer_phone",
    "application_email",
    "submission_email",
    # SYNONYMS, not finer classes. A witness names what ITS OWN adapter removed, so
    # this vocabulary records the names our source emits instead of imposing one —
    # `telephone`, `phone` and `employer_phone` already coexist here for that reason.
    # `mailto` is an address inside an href and `contact_email` one in prose: the FORM
    # differs, the class does not, and the description's own marker says which. Added
    # on 2026-11-11 for `jobsdz` and `dadlijobs`, after MEASURING that adding them
    # brings NO further file into the guard's derived scope and leaves no site
    # unguarded — 20 carriers and 28 sites before as after, on a bench armed by
    # emptying CONTACT, which collapses that scope to 0.
    "mailto",
    "contact_email",
    "contact_phone",
    # **A LOCUS PREFIX SAYS *WHERE* THE DATUM SAT; THE SUFFIX SAYS *WHAT* IT IS.** Five
    # adapters spell their witness `description:e-mail`, `body:telephone`,
    # `company.phone`, `description.email`, `advertiser:phone` — the same classes under
    # a namespace. `classe()` below strips the locus and judges the SUFFIX, which is the
    # line this file already takes for `mailto` against `contact_email`: the FORM
    # differs, the class does not. These five entries are the suffixes those spellings
    # leave behind; the prefixed spellings themselves are deliberately NOT listed, or
    # the vocabulary would grow by one entry per adapter per field forever.
    "e-mail",
    "messaging",
    "street",
    "address",
    "contactPhones",
    # **`ntchito`'s company handle, #1337.** A handle is a channel one can WRITE to,
    # which is `messaging` under its WP Job Manager name. Measured EMPTY on 100 of 100
    # records on 2026-11-26, so this classification is a JUDGEMENT on the field's form
    # and not a measurement of its content — declared as such, and inert today.
    "_company_twitter",
})

# withheld for a reason that is NOT a contact
OTHER = frozenset({
    # criteria an advert states about a person and #183 refuses to propagate
    "gender",
    "nationality",
    "age",
    "age_range",
    # the vacancy's own geography, never a person's
    "coordinates",
    # a form, a careers page, or an address nobody can follow. When the link WAS a
    # way to reach someone — `mailto:`, `tel:`, a messaging host — the adapter says
    # so through `reached_a_person`, because this one name covers three causes and
    # only two of them are contacts.
    "application_link",
    # Suffixes left by a locus prefix, same rule as above. **A NAME IS NOT A CHANNEL**:
    # `advertiser:name` identifies, it does not reach, so it sits here beside `gender` —
    # withheld, and not a contact. `image` and `lastOnline` are a hiring manager's photo
    # and presence; `ghash`, `itemId` and `display` are the vacancy's own geohash and its
    # rendered address block, which is `coordinates` one notch further. **`display` was
    # first written `fullName` here, from a COMMENT that names the leaf rather than the
    # path `jobtoday.DROP` actually declares — `("addressInfo", "display")`. The raise
    # said so on the first run: a vocabulary read off prose instead of off the emitting
    # code is the `_travel` defect of #1316, one file further along.**
    "name",
    "display",
    "image",
    "lastOnline",
    "ghash",
    "itemId",
    # **WP Job Manager's meta keys as `ntchito` names them, #1337 — MEASURED on 100
    # records of `/wp-json/wp/v2/job-listings` on 2026-11-26, never classed on their
    # spelling.** `_company_website` was filled on 22 of 100 and all 22 were a company
    # URL: a site reaches no person. `_application` was filled on 46: **39 a URL and 7
    # an e-mail address** — ONE name, two causes, exactly `application_link`'s shape, so
    # it sits here and the adapter says through `reached_a_person` when the value it
    # withheld was an address. `_company_name` was EMPTY on 100 of 100: it is classed by
    # this file's own rule that A NAME IS NOT A CHANNEL, a judgement on its form.
    "_application",
    "_company_website",
    "_company_name",
})


def classe(nom):
    """`"contact"`, `"other"` or `None` — the class of ONE name.

    The literal is tried first, so an adapter that spells a field exactly as this
    vocabulary does is judged on it. Only then is a LOCUS prefix stripped — the part
    before the last `.` or `:` — and the suffix judged instead.

    **Stripping can only ever REACH a verdict, never change one**: a name already in
    either set returns before the strip, so adding a prefixed spelling to the
    vocabulary tomorrow still wins over its suffix. And a suffix nobody classifies
    returns `None`, which `kinds` turns into the raise: the default case stays the one
    that fails visibly.
    """
    if nom in CONTACT:
        return "contact"
    if nom in OTHER:
        return "other"
    court = nom
    for sep in (".", ":"):
        court = court.rsplit(sep, 1)[-1]
    if court != nom:
        if court in CONTACT:
            return "contact"
        if court in OTHER:
            return "other"
    return None


def kinds(names):
    """`(contacts, others, unknown)`, each sorted and deduplicated."""
    seen = sorted(set(names or ()))
    par = {n: classe(n) for n in seen}
    return (
        tuple(n for n in seen if par[n] == "contact"),
        tuple(n for n in seen if par[n] == "other"),
        tuple(n for n in seen if par[n] is None),
    )


# **WHAT A `scrub` WROTE, READ BACK ON THE RECORD IT EMITTED — #1321.** The dominant
# `scrub` of this directory substitutes these markers and returns the text ALONE, so it
# cannot say what it took. Reading the markers on the emitted record is the one form that
# cannot diverge from it: a second detector would be a second judgement, and the two would
# drift. The names are suffixes `CONTACT` already holds.
MARKERS = (("e-mail", "[e-mail withheld]"),
           ("telephone", "[telephone withheld]"))


def taken(record, markers=MARKERS):
    """The contact names whose marker sits in any string of `record`, nested included.

    Returns a sorted list, empty when nothing was taken — an empty list, not `None`, so
    the caller decides how to emit the witness.
    """
    found = set()

    def walk(v):
        if isinstance(v, str):
            for nom, marque in markers:
                if marque in v:
                    found.add(nom)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x)

    walk(record)
    return sorted(found)


# **WHAT A `scrub` CANNOT MARK, READ ON THE SOURCE — #1321.** Eight adapters drop a
# STRUCTURED contact — a consultant object, a `ContactPoint`, an application address in its
# own field — that never reaches a text, so `taken()` cannot see it. For them the constant
# `contacts_withheld: True` was TRUE on most records; reading the markers alone would have
# silenced it, which is the silent direction. `present()` names the field when the SOURCE
# filled it, and stays silent when it did not, so the declaration follows the document.
_SENTINELS = frozenset({"undefined", "null", "none", "nan"})


def filled(v):
    """A POSITIVE floor: a value is filled only if it passes, never because it misses a list.

    A string needs a letter or a digit, and is refused when it is a flight-data reference
    (`$undefined`, `$3e`) or a literal sentinel; a number or a `True` counts; a container
    counts when one of its members does.
    """
    if v is None or v is False:
        return False
    if isinstance(v, str):
        t = v.strip()
        return (any(c.isalnum() for c in t) and not t.startswith("$")
                and t.lower() not in _SENTINELS)
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, dict):
        return any(filled(x) for x in v.values())
    if isinstance(v, (list, tuple)):
        return any(filled(x) for x in v)
    return False


def present(source, spec):
    """The names of `spec` — `{witness name: [path, ...]}` — whose value `source` filled.

    A path is a tuple of keys; a list met on the way is walked member by member, so
    `("Locations", "Address", "Line1")` reaches every location. Returns a sorted list.
    """
    def reach(v, path):
        if not path:
            return filled(v)
        if isinstance(v, (list, tuple)):
            return any(reach(x, path) for x in v)
        if isinstance(v, dict):
            return reach(v.get(path[0]), path[1:])
        return False

    return sorted(n for n, paths in spec.items() if any(reach(source, tuple(p)) for p in paths))


def withheld_a_contact(names, reached_a_person=False):
    """Did something that reaches a person leave this record?

    `reached_a_person` is for the case a name cannot express: `wazefnisy` drops an
    `application_link` either because it opens a conversation with someone or because
    it is not an address at all, and it names both the same way.
    """
    contacts, _others, unknown = kinds(names)
    if unknown:
        raise ValueError(
            "withheld_fields names %s, which _withheld classifies neither as a "
            "contact nor as anything else. Classify it here rather than letting "
            "`contacts_withheld` guess: read as a contact the record over-declares, "
            "read as anything else it hides a removal." % (", ".join(unknown),))
    return bool(contacts) or bool(reached_a_person)
