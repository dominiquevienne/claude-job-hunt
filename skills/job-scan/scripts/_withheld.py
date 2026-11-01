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
})


def kinds(names):
    """`(contacts, others, unknown)`, each sorted and deduplicated."""
    seen = sorted(set(names or ()))
    return (
        tuple(n for n in seen if n in CONTACT),
        tuple(n for n in seen if n in OTHER),
        tuple(n for n in seen if n not in CONTACT and n not in OTHER),
    )


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
