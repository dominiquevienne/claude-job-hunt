#!/usr/bin/env python3
"""events_sheet — the two-tab events sheet: read, rebuilt, and derived. #1322.

**THE PARAGRAPH BELOW IS THE STATE OF TRANCHE 1 AND IT IS CITED, NOT REWRITTEN
(§4): `export` IS SHIPPED AS OF #1322, so do not read its "deliberately
absent" as current.** What it got right does not move — the premise WAS the
ledger's shape plus the two optional bullets, and it has now been measured:

    the ledger      read through the ONE reader, `_ledger_table` (#1182),
                    resolved from here by `_ledger_reader`
    the bullets     BOTH optional, and absent from the shipped template —
                    so the two alias columns leave EMPTY, which the contract
                    already allows, and `--employers` is what fills them

> *the paragraph of tranche 1, kept for what it measured:* **THIS SHIPS THE
> TABS WE READ AND REBUILD, AND NOT THE ONE WE DERIVE FROM THE LEDGER.**
> `export` is deliberately absent: its premise is the ledger's own shape plus
> the two optional bullets of `employers.md`, and neither was measured when
> this was written. *A chain left open on a DECLARED dependency is a debt, not
> an error — what would be false is reading «tranche 1 shipped» as «the sheet
> round-trips».*

**AND THE EGRESS EXISTS NOW, which is why the README's Privacy section is
rewritten in the SAME pull request as this.** `export` prints to STDOUT and
writes nothing else: a CSV import REPLACES a tab, so the user's own act is the
only thing that can change the sheet, and the order is export → union →
import because the union is the only shape that cannot delete a row.

**WHY CSV AT ALL, measured twice by two sessions on 2026-11-12 and recorded in
the issue's thread.** No Google Sheets connector exists in a Claude Code session
here: a tool search returned eight tools — Drive `update_file`, `create_file`,
`read_file_content`, `share_file`, `search_files`, two Calendar, one Gmail — and
**none writes a cell**. The instrument answered, so that zero is readable and
not a search failure.

> **Writing `candidatures` cannot be automated at all today.** A CSV import
> *replaces* a tab, so rebuilding the FULL union with the tab's current content
> is not an optimisation: it is the only shape that cannot delete a row.

**THE ASYMMETRY WAS A PROPERTY OF `text/csv`, NEVER OF THE TRANSPORT — and
the paragraph that follows is cited and bounded, not rewritten.** Measured:
`exportMimeType: text/csv` returns ONE tab, the one we WRITE; the xlsx mime
type returns **ALL** of them in one file, and this reader resolves the wanted
one by its **NAME** through `xl/_rels/workbook.xml.rels`. *So the question
«does the export follow tab ORDER or the ACTIVE tab?», which needed a human
minute and belonged to the owner, is SANS OBJET: it was asked only because the
CSV rendered one tab.*

> *cited:* **AND THE EXPORT IS ASYMMETRIC IN THE WORST DIRECTION.**
> `download_file_content` with `text/csv` works and returns **one** tab — the
> one we WRITE — and its schema carries no tab selector, so that is not a
> parameter anybody failed to pass. The tab we READ is the one it cannot
> reach.

**AND THE TAB IS RESOLVED BY NAME AND NEVER BY THE INDEX OF
`xl/worksheets/sheetN.xml`.** On the workbook this was measured against the two
COINCIDED — which is exactly why a reader that assumes the index returns green
today and reads the WRONG TAB on the first workbook whose author reordered or
deleted a sheet. *A workbook may also carry a THIRD tab that belongs to the
producer — a scan journal. We neither write it nor read it, and the refusal for
an absent tab NAMES the tabs the workbook does carry, which is how a reader
learns of it without reading it.*

**THE EXPORTED CSV HAS NO TRAILING NEWLINE** — 111 bytes, `wc -l` returns 0. A
`while read` loop drops the last line of such a file in silence, and here that
line is a real event. `csv.reader` is used for that reason, and the bench
carries a fixture with no final newline so the choice is exercised rather than
asserted.

**AN UNREADABLE OR HEADER-MISMATCHED CSV IS REFUSED BY AN EXIT CODE, NEVER READ
AS «no events».** The two failures are distinct codes, because «the file is not
there» and «the file is not this tab» send a reader to different places. *And a
code is taken WITHOUT A PIPE: the exit of a pipeline is the exit of the pipe.*

**«Pas de donnée» IS NOT THE ONLY SENTINEL A SHEET WRITES, so the floor is
POSITIVE**: a cell is a value when it passes a test, never because it is missing
from a list of refusals. A list of refusals bets that the problem has been
enumerated, and the next sentinel arrives spelled differently.

**AND AN UNKNOWN `type` OR `confiance` IS NAMED AND NEVER COERCED.** When a sort
has a default case, the default is the one that fails VISIBLY: mapping an
unknown type onto `autre` would make a producer's new event kind look like a
deliberate «other», and nothing in the output would say otherwise.

    events_sheet.py events --csv evenements.csv        # or the .xlsx
    events_sheet.py export --pipeline job-pipeline.md [--employers e.md] \
                           [--rejected-from YYYY-MM-DD]  > rows.csv
    events_sheet.py merge  --current candidatures.csv --new rows.csv

*The contract itself lives in `shared/integrations/events-sheet.md`; each tab
has one owner, and this module never writes the tab it reads.*
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _ledger_reader  # noqa: E402  (after the path insert, by design)
import _sheets  # noqa: E402  (same directory, same reason)

EXIT_BROKEN = 2
EXIT_UNREADABLE = 4      # the file is not there, or not readable text
EXIT_HEADER = 5          # the file is readable and is NOT this tab

#  The two contracts, in the order the sheet carries them. They are LITERALS
#  here so that a header check compares against the agreement and never against
#  whatever the file happens to hold.
CANDIDATURES = ("id", "entreprise", "alias_entreprise", "domaines_expediteurs",
                "poste", "canal", "statut_ledger", "date_envoi", "date_statut",
                "statut_pre")
EVENEMENTS = ("date_evenement", "message_id", "candidature_id",
              "candidats_possibles", "entreprise", "poste", "type",
              "motif_refus", "action_requise", "echeance", "thread_url",
              "archive", "confiance", "traite_le")

TYPES = ("accuse_reception", "refus", "entretien", "demande_action", "autre")
CONFIANCES = ("haute", "moyenne", "basse")

#  A POSITIVE floor. The first alternative is the one measured on a real sheet
#  export; the others are DECLARED inert on that corpus and exist because the
#  next sentinel arrives spelled differently, not because they protected
#  anything we saw.
SENTINEL = re.compile(
    r"^\s*(?:pas\s+de\s+donn[ée]es?|n/?a|aucune?|-{1,3}|null|none|undefined"
    r"|\$undefined)\s*$", re.I)

#  An ISO date, optionally followed by a time. A cell that does not match is not
#  ordered against the others: it is reported under its own name.
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:[ T].*)?$")


class SheetRefused(Exception):
    """The file is not the tab this reader was given."""

    def __init__(self, message, code=EXIT_HEADER):
        super().__init__(message)
        self.code = code


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[events_sheet] {msg}", file=sys.stderr)


def declared(value):
    """`(value, state)` — a POSITIVE floor, run on the RAW cell.

    Three states and not two: `if x` conflates «absent», «present but empty»
    and «the sheet wrote a sentinel there», and the one that costs is the third
    — a column holding «Pas de donnée» has deposited nothing, and reading it as
    a value is how a record comes to claim something nobody wrote.
    """
    if value is None:
        return None, "absent"
    if isinstance(value, str):
        if not value.strip():
            return None, "present but empty"
        if SENTINEL.match(value):
            return None, "sentinel"
        return value.strip(), "declared"
    return value, "declared"


# ---------------------------------------------------------------- xlsx

#  **A zip is detected on its MAGIC BYTES and never on its extension.** An
#  extension is a guess a user can get wrong in either direction, and both
#  directions cost: a `.csv` that is really a workbook would be parsed as one
#  enormous single-column row, and a `.xlsx` that is really text would be
#  refused as a corrupt archive.
_ZIP_MAGIC = b"PK\x03\x04"

_NS_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def is_workbook(path):
    """Whether this file is a zip container, read on its first four bytes."""
    try:
        with io.open(path, "rb") as fh:
            return fh.read(4) == _ZIP_MAGIC
    except OSError as e:
        raise SheetRefused(f"{path}: {type(e).__name__}: {e}", EXIT_UNREADABLE)


def _local(tag):
    """The local name of an XML tag, namespace dropped."""
    return tag.rsplit("}", 1)[-1]


def _col(ref):
    """`A1` -> 0, `AB7` -> 27. The letters only; the row number is ignored."""
    n = 0
    for ch in ref:
        if not ch.isalpha():
            break
        n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1 if n else 0


def _shared_strings(zf):
    """`xl/sharedStrings.xml` as a list, or an empty one when absent.

    Absent is normal: a workbook whose cells are all numbers carries no such
    part. A cell of type `s` indexes into this list, so an absent part and an
    out-of-range index are different failures and the second one refuses.
    """
    try:
        raw = zf.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    out = []
    for si in ET.fromstring(raw):
        #  The runs matter: a cell the user has part-bolded is split into
        #  several `<r><t>` and joining them is the only way to read the
        #  value the sheet SHOWS.
        out.append("".join(t.text or "" for t in si.iter()
                           if _local(t.tag) == "t"))
    return out


def workbook_tabs(zf, path):
    """`[(name, part)]` in workbook order — the tab resolved by its NAME.

    **The part is reached through `xl/_rels/workbook.xml.rels`, never through
    the index of `xl/worksheets/sheetN.xml`.** On the workbook this was
    measured against the two coincided, and that is exactly why a reader that
    assumes the index returns green today and reads the WRONG TAB on the first
    workbook whose author has reordered or deleted a sheet.
    """
    try:
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    except KeyError as e:
        raise SheetRefused(
            f"{path}: a zip container without {e}. It is not a workbook this "
            f"reader can resolve by tab name", EXIT_UNREADABLE)
    target = {}
    for r in rels:
        rid = r.get("Id")
        tgt = r.get("Target") or ""
        if rid:
            target[rid] = tgt.lstrip("/")
    out = []
    for sheet in wb.iter():
        if _local(sheet.tag) != "sheet":
            continue
        rid = sheet.get(_NS_REL + "id") or sheet.get("id")
        name = sheet.get("name")
        part = target.get(rid)
        if name is None or part is None:
            continue
        out.append((name, part if part.startswith("xl/") else "xl/" + part))
    return out


def read_workbook_tab(path, tab):
    """The rows of ONE named tab of a workbook, as lists of strings.

    The refusal when the name is absent NAMES the tabs the workbook does
    carry — which is also how a reader learns, without reading it, that a
    producer keeps a third tab of its own.
    """
    try:
        zf = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as e:
        raise SheetRefused(f"{path}: {type(e).__name__}: {e}", EXIT_UNREADABLE)
    with zf:
        tabs = workbook_tabs(zf, path)
        part = None
        for name, p in tabs:
            if name == tab:
                part = p
                break
        if part is None:
            raise SheetRefused(
                f"{path}: this workbook carries no tab named `{tab}` — it "
                f"carries {', '.join('`%s`' % n for n, _ in tabs) or 'none'}. "
                f"Refused rather than reading whichever tab came first")
        try:
            raw = zf.read(part)
        except KeyError:
            raise SheetRefused(
                f"{path}: tab `{tab}` points at {part}, which the container "
                f"does not hold", EXIT_UNREADABLE)
        strings = _shared_strings(zf)
    try:
        sheet = ET.fromstring(raw)
    except ET.ParseError as e:
        raise SheetRefused(f"{path}: tab `{tab}` is not readable XML: {e}",
                           EXIT_UNREADABLE)
    rows = []
    for row in sheet.iter():
        if _local(row.tag) != "row":
            continue
        cells = {}
        for c in row:
            if _local(c.tag) != "c":
                continue
            i = _col(c.get("r") or "A")
            kind = c.get("t")
            text = ""
            if kind == "s":
                v = next((e.text for e in c if _local(e.tag) == "v"), None)
                if v is not None:
                    try:
                        text = strings[int(v)]
                    except (ValueError, IndexError):
                        raise SheetRefused(
                            f"{path}: tab `{tab}` cell {c.get('r')} indexes "
                            f"shared string {v}, which is not there")
            elif kind == "inlineStr":
                text = "".join(t.text or "" for t in c.iter()
                               if _local(t.tag) == "t")
            else:
                v = next((e.text for e in c if _local(e.tag) == "v"), None)
                text = v if v is not None else ""
            cells[i] = text or ""
        rows.append([cells.get(i, "") for i in range(max(cells) + 1)]
                    if cells else [])
    return rows


#  The tab each contract lives on, by NAME. The names are the sheet's, not
#  ours, and they are what a workbook is resolved by.
TAB_OF = {CANDIDATURES: "candidatures", EVENEMENTS: "evenements"}


def read_tab(path, header, tab=None):
    """Rows of one tab, in SHEET ORDER, or a refusal with its own exit code.

    The header is compared to the contract and the complaint NAMES what it got:
    «not this tab» and «this tab with a column renamed» are different repairs.

    **A CSV export carries ONE tab and an xlsx export carries them ALL**, so
    the same call reads either: a zip container is resolved by the tab's NAME,
    a text file is read as the single tab it is. *That is the fact that
    retires an impossibility the contract recorded — `text/csv` cannot reach
    the tab we READ, and the workbook export can, so the open question about
    tab ORDER was a property of the CSV and never of the transport.*
    """
    if tab is None:
        tab = TAB_OF.get(tuple(header))
    if is_workbook(path):
        if not tab:
            raise SheetRefused(
                f"{path}: a workbook carries several tabs, so it cannot be "
                f"read without the NAME of the one wanted. Refused rather "
                f"than reading whichever tab came first")
        rows = read_workbook_tab(path, tab)
    else:
        try:
            with io.open(path, encoding="utf-8-sig", newline="") as fh:
                rows = list(csv.reader(fh))
        except OSError as e:
            raise SheetRefused(f"{path}: {type(e).__name__}: {e}",
                               EXIT_UNREADABLE)
        except UnicodeDecodeError as e:
            raise SheetRefused(f"{path}: not readable as UTF-8 text: {e}",
                               EXIT_UNREADABLE)
    if not rows:
        raise SheetRefused(
            f"{path}: zero lines. An empty FILE is not an empty TAB — a tab "
            f"carries its header row even with no data, so this is a refusal "
            f"and never «no rows»")
    got = tuple(c.strip() for c in rows[0])
    if got != tuple(header):
        missing = [c for c in header if c not in got]
        extra = [c for c in got if c not in header]
        detail = []
        if missing:
            detail.append("missing " + ", ".join(missing))
        if extra:
            detail.append("unexpected " + ", ".join(extra))
        if not detail:
            detail.append("same columns in a different ORDER")
        raise SheetRefused(
            f"{path}: header is not the contract — {'; '.join(detail)}. "
            f"Refused rather than read as «no rows»")
    out = []
    for n, raw in enumerate(rows[1:], start=2):
        if len(raw) != len(header):
            raise SheetRefused(
                f"{path}: line {n} carries {len(raw)} cell(s) for "
                f"{len(header)} column(s). A short row would silently shift "
                f"every field after it")
        out.append({k: raw[i] for i, k in enumerate(header)})
    return out


def date_of(row):
    """The ISO date prefix of `date_evenement`, or `None` — never a guess."""
    value, _state = declared(row.get("date_evenement"))
    if value is None:
        return None
    m = DATE_RE.match(value)
    return m.group(1) if m else None


def events(path):
    """Latest event per application, plus everything that has no single one.

    Three things are measured rather than assumed. **Deduplication is by
    `message_id`** — a replayed scan is idempotent on the producer's side and
    must be on ours. **«Latest» is by `date_evenement`, and ties keep the order
    in the sheet**, which is why the rows are never sorted: a stable scan of the
    sheet order cannot reorder a tie. **And a row whose date does not parse is
    not ordered against the others**: it leaves under its own name, because
    comparing it would put an unknown instant somewhere precise.
    """
    rows = read_tab(path, EVENEMENTS)
    seen, twice = set(), 0
    latest, sans_date, sans_candidature, inconnus = {}, [], [], []
    for row in rows:
        mid, _s = declared(row.get("message_id"))
        if mid is not None:
            if mid in seen:
                twice += 1
                continue
            seen.add(mid)
        kind, _s = declared(row.get("type"))
        if kind is not None and kind not in TYPES:
            inconnus.append({"type": kind, "message_id": mid})
        conf, _s = declared(row.get("confiance"))
        if conf is not None and conf not in CONFIANCES:
            inconnus.append({"confiance": conf, "message_id": mid})
        when = date_of(row)
        cid, _s = declared(row.get("candidature_id"))
        record = {
            "date_evenement": when,
            "message_id": mid,
            "candidature_id": cid,
            "type": kind,
            "confiance": conf,
            "a_confirmer": conf != "haute",
            "thread_url": declared(row.get("thread_url"))[0],
            "motif_refus": declared(row.get("motif_refus"))[0],
            "motif_refus_non_fiable": declared(row.get("motif_refus"))[0] is not None,
            "action_requise": declared(row.get("action_requise"))[0],
            "echeance": declared(row.get("echeance"))[0],
        }
        if when is None:
            sans_date.append(record)
            continue
        if cid is None:
            possibles, _s = declared(row.get("candidats_possibles"))
            record["candidats_possibles"] = (
                [p.strip() for p in possibles.split("|") if p.strip()]
                if possibles else [])
            sans_candidature.append(record)
            continue
        held = latest.get(cid)
        #  STRICTLY greater: on a tie the row already held wins, which is the
        #  sheet's own order, and the scan never sorts.
        if held is None or when > held["date_evenement"]:
            latest[cid] = record
    return {
        "dernier_par_candidature": latest,
        "sans_candidature": sans_candidature,
        "sans_date_lisible": sans_date,
        "valeurs_inconnues": inconnus,
        "lus": len(rows),
        "doublons_message_id": twice,
    }


def merge(current, new):
    """The union of the tab's current content with our rows — by `id`.

    A CSV import REPLACES the tab, so this is the only shape that cannot delete
    a row: anything the sheet holds and we do not know about is carried through
    untouched. **And `date_envoi` is never rewritten**: the owner's decision 1
    says a send date must survive `applied → rejected`, which is exactly the
    update that would overwrite it.
    """
    held = read_tab(current, CANDIDATURES)
    mine = read_tab(new, CANDIDATURES)
    order, rows = [], {}
    for row in held:
        rid, _s = declared(row.get("id"))
        if rid is None:
            raise SheetRefused(
                f"{current}: a row carries no `id`. The union keys on it, so a "
                f"row without one would be dropped or duplicated in silence")
        if rid not in rows:
            order.append(rid)
        rows[rid] = dict(row)
    kept_dates, added, updated = 0, 0, 0
    for row in mine:
        rid, _s = declared(row.get("id"))
        if rid is None:
            raise SheetRefused(f"{new}: a row carries no `id`")
        if rid not in rows:
            order.append(rid)
            rows[rid] = dict(row)
            added += 1
            continue
        before = rows[rid]
        merged = dict(row)
        envoi, _s = declared(before.get("date_envoi"))
        if envoi is not None:
            merged["date_envoi"] = before["date_envoi"]
            if declared(row.get("date_envoi"))[0] != envoi:
                kept_dates += 1
        rows[rid] = merged
        updated += 1
    return ([rows[r] for r in order],
            {"tenues": len(held), "miennes": len(mine), "ajoutees": added,
             "mises_a_jour": updated, "dates_envoi_conservees": kept_dates,
             "supprimees": 0})


# ---------------------------------------------------------------- export

#  The ledger's vocabulary mapped onto the contract's two values. **The French
#  forms are here because the ledger still accepts them**, and a sort with a
#  default case gets the one that fails VISIBLY: a kind the ledger counts as
#  SENT and this table does not name is reported under its own name and never
#  folded onto `applied`, because a row we cannot classify would leave for the
#  sheet carrying a status nobody wrote.
LEDGER_TO_SHEET = {
    "applied": "applied", "postulé": "applied", "postule": "applied",
    "rejected": "rejected", "refusé": "rejected", "refuse": "rejected",
}

#  `- **aliases** — Acme AG | Acme Group`. The LABELS the contract names, and
#  nothing else: `employers.md`'s own template carries «Also trades as», and
#  reading that as an alias would put into an egress a value the user never
#  declared for it. A declaration is not an interpretation.
_BULLET = re.compile(
    r"^\**(?P<label>aliases|domains)\**\s*[—:-]\s*(?P<rest>.*)$", re.I)


def board_of(rid):
    """The board prefix of a ledger `ID` — `linkedin:448…` -> `linkedin`.

    Empty when the id carries no prefix, and the caller COUNTS that: the
    column says **where the ad was FOUND**, so inventing a board for a row
    whose id does not name one would assert a provenance.
    """
    value, _state = declared(rid)
    if value is None or ":" not in value:
        return ""
    return value.split(":", 1)[0].strip()


def employer_facts(path, mod):
    """`{folded name: {"aliases": [...], "domains": [...]}}`, both optional.

    The reading is the employers reader's own — sections bounded by the first
    `---` rule, bullets joined across their wrapped lines — because this file
    must not acquire a second one. The value is what follows the dash, with
    the dated italic note after ` · ` dropped and the `|` separators split.
    """
    try:
        with io.open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        raise SheetRefused(
            f"{path}: {type(e).__name__}: {e}. An employers file that is NAMED "
            f"and cannot be read leaves by a refusal — reading it as «this "
            f"employer declares no alias» is the one thing it must not do",
            EXIT_UNREADABLE)
    out = {}
    for name, body in mod.sections(text):
        facts = {}
        for bullet in mod.bullets(body):
            m = _BULLET.match(bullet)
            if not m:
                continue
            rest = m.group("rest").split(" · ")[0]
            vals = [v.strip().strip("`").strip() for v in rest.split("|")]
            vals = [v for v in vals if declared(v)[0] is not None]
            if vals:
                facts[m.group("label").lower()] = vals
        if facts:
            out[mod.fold(name)] = facts
    return out


def candidatures(rows, sent, fold=None, facts=None, rejected_from=None):
    """The `candidatures` rows derived from the ledger, plus what was NOT.

    `sent` and `fold` are passed IN rather than resolved here: they belong to
    the two readers this file does not own, and taking them as arguments is
    what makes this function exercisable on a row nobody had to write a
    ledger for.

    Three things leave EMPTY rather than guessed, and each is counted so the
    output can say so:

    **`date_envoi` on a `rejected` row.** The contract's own reason for never
    rewriting that column is that `applied → rejected` OVERWRITES the send
    date in `Status` — so for a row the ledger already carries as `rejected`,
    **the send date is not in the ledger at all**. It leaves empty and `merge`
    then keeps whatever the sheet already holds. *A date taken from the
    rejection would be a send date nobody recorded.*

    **`statut_pre` with no `JR:` marker in the Note.** The contract lists
    three values and the ledger has a fourth state — nothing recorded at all.
    Folding it onto `non_declare` would claim a declaration state nobody
    wrote, on the column an unemployment-office declaration reads.

    **`canal` on an id with no board prefix** — see `board_of`.

    Scope is the contract's: every `applied` row whatever its date, because an
    `applied` row is waiting for an answer and leaving it out means its
    refusal is never matched; `rejected` rows only from `rejected_from`.
    **With no cut-off given, NO `rejected` row leaves** — the least-egress
    default, and the count says how many were held and what releases them.
    """
    facts = facts or {}
    if facts and fold is None:
        raise SheetRefused(
            "employer facts were given without the folding that keyed them. "
            "A lookup with the wrong folding finds NOTHING and says nothing, "
            "so this refuses instead of emitting empty alias columns")
    out = []
    counts = {"lues": len(rows), "jamais_envoyees": 0, "inconnues": [],
              "retenues_rejected": 0, "sans_date_envoi": 0,
              "sans_statut_pre": 0, "sans_canal": 0, "alias": 0,
              "domaines": 0}
    for row in rows:
        if not sent(row):
            counts["jamais_envoyees"] += 1
            continue
        kind = row.get("kind")
        if kind not in LEDGER_TO_SHEET:
            #  The ledger counts it as sent and this table does not name it.
            #  NAMED, never coerced: see the comment on `LEDGER_TO_SHEET`.
            counts["inconnues"].append(kind)
            continue
        statut = LEDGER_TO_SHEET[kind]
        date_statut = row["date"]
        if statut == "rejected":
            if not rejected_from or date_statut < rejected_from:
                counts["retenues_rejected"] += 1
                continue
            date_envoi = ""
            counts["sans_date_envoi"] += 1
        else:
            date_envoi = date_statut
        if row.get("jr_waived"):
            pre = "renonce"
        elif row.get("jr_declared"):
            pre = "declare"
        elif row.get("jr_missing"):
            pre = "non_declare"
        else:
            pre = ""
            counts["sans_statut_pre"] += 1
        canal = board_of(row.get("id"))
        if not canal:
            counts["sans_canal"] += 1
        f = facts.get(fold(row.get("societe", "")), {}) if facts else {}
        if f.get("aliases"):
            counts["alias"] += 1
        if f.get("domains"):
            counts["domaines"] += 1
        out.append({
            "id": (declared(row.get("id"))[0] or ""),
            "entreprise": (declared(row.get("societe"))[0] or ""),
            "alias_entreprise": "|".join(f.get("aliases", [])),
            "domaines_expediteurs": "|".join(f.get("domains", [])),
            "poste": (declared(row.get("poste"))[0] or ""),
            "canal": canal,
            "statut_ledger": statut,
            "date_envoi": date_envoi,
            "date_statut": date_statut,
            "statut_pre": pre,
        })
    return out, counts


# ---------------------------------------------------------------- commands

def cmd_events(a):
    state = events(a.csv)
    json.dump(state, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    note(f"{state['lus']} row(s) read, {state['doublons_message_id']} dropped "
         f"as a replayed `message_id`")
    note(f"{len(state['dernier_par_candidature'])} application(s) carry an "
         f"event, {len(state['sans_candidature'])} event(s) name no single "
         f"application, {len(state['sans_date_lisible'])} carry no readable "
         f"date")
    bas = sum(1 for r in state["dernier_par_candidature"].values()
              if r["a_confirmer"])
    note(f"{bas} of them below `haute`: they are SUGGESTIONS and nothing is "
         f"applied without a yes")
    if state["valeurs_inconnues"]:
        note(f"{len(state['valeurs_inconnues'])} cell(s) carry a value this "
             f"contract does not list — NAMED and never coerced onto `autre`")


def cmd_merge(a):
    rows, counts = merge(a.current, a.new)
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(CANDIDATURES)
    for row in rows:
        w.writerow([row.get(c, "") for c in CANDIDATURES])
    note(f"{counts['tenues']} held + {counts['miennes']} mine -> {len(rows)} "
         f"row(s): {counts['ajoutees']} added, {counts['mises_a_jour']} "
         f"updated, {counts['supprimees']} deleted")
    if counts["dates_envoi_conservees"]:
        note(f"{counts['dates_envoi_conservees']} `date_envoi` kept as the "
             f"sheet already had it — a send date is written once")


def cmd_export(a):
    """Write the `candidatures` rows to STDOUT. **Nothing else is written.**

    An import REPLACES a tab, so the user's own act is the only thing that
    can change the sheet: this prints, `merge` unions, and the order is
    export → union → import because the union is the only shape that cannot
    delete a row.
    """
    if a.rejected_from and not DATE_RE.match(a.rejected_from):
        die(f"--rejected-from {a.rejected_from!r} is not an ISO date. A "
            f"cut-off nobody can parse would either release every rejected "
            f"row or hold them all, and the two are opposite mistakes",
            EXIT_BROKEN)
    lt = _ledger_reader.ledger("--pipeline")
    rows, skipped = lt.load(a.pipeline, lt.HEADER_ALIASES)
    rows = [lt.annotate(r) for r in rows]
    facts, fold = {}, None
    if a.employers:
        em = _ledger_reader.employers("--employers")
        facts, fold = employer_facts(a.employers, em), em.fold
    out, counts = candidatures(rows, lt.sent, fold, facts, a.rejected_from)
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(CANDIDATURES)
    for row in out:
        w.writerow([row.get(c, "") for c in CANDIDATURES])
    for line in lt.skipped_lines(skipped):
        print(line.replace("  !", "[events_sheet] !", 1), file=sys.stderr)
    note(f"{counts['lues']} ledger row(s) read -> {len(out)} row(s) for "
         f"`candidatures`; {counts['jamais_envoyees']} never left")
    if counts["retenues_rejected"]:
        note(f"{counts['retenues_rejected']} `rejected` row(s) HELD BACK: "
             f"{'no cut-off given' if not a.rejected_from else 'older than ' + a.rejected_from}"
             f" — `--rejected-from <YYYY-MM-DD>` is what releases them")
    if counts["sans_date_envoi"]:
        note(f"{counts['sans_date_envoi']} row(s) leave with an EMPTY "
             f"`date_envoi`: they are already `rejected`, and the ledger's "
             f"`Status` then carries the REFUSAL date, not the send date. "
             f"`merge` keeps whatever the sheet already holds")
    if counts["sans_statut_pre"]:
        note(f"{counts['sans_statut_pre']} row(s) carry NO `JR:` marker, so "
             f"`statut_pre` is empty — nothing recorded is not `non_declare`")
    if counts["sans_canal"]:
        note(f"{counts['sans_canal']} id(s) carry no board prefix, so `canal` "
             f"is empty rather than guessed")
    if counts["inconnues"]:
        note(f"{len(counts['inconnues'])} row(s) the ledger counts as SENT "
             f"under a kind this table does not name — NAMED and never folded "
             f"onto `applied`: {', '.join(sorted(set(counts['inconnues'])))}")
    if a.employers:
        note(f"employers.md: {counts['alias']} row(s) carry an alias, "
             f"{counts['domaines']} carry sender domains — both optional, and "
             f"an absent bullet is empty and not an error")
    else:
        note("no --employers given: `alias_entreprise` and "
             "`domaines_expediteurs` leave EMPTY, which the contract allows")


def cmd_push(a):
    """Read the tab, derive our rows, UNION them, and write the union IN PLACE.

    This is the whole loop with no manual step, and it exists because the
    owner refused the export-then-import cycle on 2026-11-15: *« il n'est pas
    envisageable d'exporter... puis potentiellement importer la feuille »*.

    **It reuses `merge` rather than re-deriving the union**, by writing both
    sides to temporary CSVs: that function is the one the suite covers, and a
    second implementation of "the only shape that cannot delete a row" is the
    last thing this file needs. The cost is two temporary files; the gain is
    that the union keeps being the union the tests assert.

    **And nothing is written without `--apply`.** The skills already tell the
    user that `/job-sync` "proposes it and applies nothing without a yes", so
    a default that writes would make that sentence false.
    """
    try:
        cred = _sheets.credential(a.key)
        access = _sheets.token(cred)
        held = _sheets.fetch_values(a.sheet, a.tab, access=access)
    except _sheets.SheetsRefused as exc:
        die(str(exc), exc.code)

    if not held:
        die(f"`{a.tab}` came back EMPTY — not even a header row. A union "
            f"against nothing would write our rows over a tab whose shape we "
            f"never saw", EXIT_HEADER)
    if tuple(held[0]) != CANDIDATURES:
        die(f"`{a.tab}` row 1 is not this contract's header. Read it, do not "
            f"assume it: {held[0]}", EXIT_HEADER)

    with tempfile.TemporaryDirectory() as tmp:
        cur = os.path.join(tmp, "current.csv")
        new = os.path.join(tmp, "new.csv")
        width = len(CANDIDATURES)
        with io.open(cur, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            for row in held:
                #  The API omits trailing empty cells, so a short row is the
                #  NORMAL shape and not a malformed one. Padding here keeps the
                #  CSV rectangular, which is what the reader expects.
                w.writerow(list(row) + [""] * (width - len(row)))
        lt = _ledger_reader.ledger("--pipeline")
        rows, skipped = lt.load(a.pipeline, lt.HEADER_ALIASES)
        rows = [lt.annotate(r) for r in rows]
        facts, fold = {}, None
        if a.employers:
            em = _ledger_reader.employers("--employers")
            facts, fold = employer_facts(a.employers, em), em.fold
        out, counts = candidatures(rows, lt.sent, fold, facts, a.rejected_from)
        with io.open(new, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(CANDIDATURES)
            for row in out:
                w.writerow([row.get(c, "") for c in CANDIDATURES])
        union, mc = merge(cur, new)
        for line in lt.skipped_lines(skipped):
            print(line.replace("  !", "[events_sheet] !", 1), file=sys.stderr)

    values = [list(CANDIDATURES)] + [[row.get(c, "") for c in CANDIDATURES]
                                     for row in union]
    note(f"`{a.tab}` holds {len(held) - 1} row(s); the ledger gives "
         f"{len(out)}; the UNION is {len(union)}")
    note(f"{mc['ajoutees']} would be added, {mc['mises_a_jour']} updated, "
         f"{mc['supprimees']} deleted — and a union cannot delete, so a "
         f"non-zero deletion count is a defect and not a plan")
    if mc["dates_envoi_conservees"]:
        note(f"{mc['dates_envoi_conservees']} `date_envoi` kept as the sheet "
             f"already had it — a send date is written once")
    if counts["retenues_rejected"]:
        note(f"{counts['retenues_rejected']} `rejected` row(s) HELD BACK: "
             f"`--rejected-from <YYYY-MM-DD>` is what releases them")

    if not a.apply:
        w = csv.writer(sys.stdout, lineterminator="\n")
        for row in values:
            w.writerow(row)
        note("DRY RUN — nothing was written. Add `--apply` to write it.")
        return

    last = chr(ord("A") + len(CANDIDATURES) - 1)
    a1 = f"{a.tab}!A1:{last}{len(values)}"
    try:
        cells, rng = _sheets.write_values(a.sheet, a1, values, access=access)
    except _sheets.SheetsRefused as exc:
        die(str(exc), exc.code)
    note(f"WRITTEN IN PLACE: {cells} cell(s) over {rng}. Nothing was cleared, "
         f"so no row this sheet held can have been dropped")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    s = p.add_subparsers(dest="cmd", required=True)

    pe = s.add_parser("events", help="latest event per application")
    pe.add_argument("--csv", required=True)
    pe.set_defaults(fn=cmd_events)

    pm = s.add_parser("merge", help="union with the tab's current content")
    pm.add_argument("--current", required=True)
    pm.add_argument("--new", required=True)
    pm.set_defaults(fn=cmd_merge)

    px = s.add_parser("export", help="derive `candidatures` from the ledger")
    px.add_argument("--pipeline", required=True,
                    help="job-pipeline.md — NAMED and never defaulted: this "
                         "is the egress, and what leaves is said out loud")
    px.add_argument("--employers", default=None,
                    help="employers.md, optional; without it the two alias "
                         "columns leave empty, which the contract allows")
    px.add_argument("--rejected-from", default=None, dest="rejected_from",
                    help="ISO date. `applied` rows leave whatever their date; "
                         "`rejected` rows leave only from this one, and with "
                         "no cut-off NONE of them leaves")
    px.set_defaults(fn=cmd_export)

    pp = s.add_parser("push", help="the whole loop: read the tab, union, write")
    pp.add_argument("--sheet", required=True,
                    help="the spreadsheet id — NAMED and never defaulted: this "
                         "is the egress, and which document it reaches is not "
                         "something this file gets to assume")
    pp.add_argument("--pipeline", required=True, help="job-pipeline.md")
    pp.add_argument("--tab", default="candidatures")
    pp.add_argument("--employers", default=None)
    pp.add_argument("--key", default=None,
                    help="the service-account key; the default and the "
                         "environment variable are documented in `_sheets`")
    pp.add_argument("--rejected-from", default=None, dest="rejected_from")
    pp.add_argument("--apply", action="store_true",
                    help="WRITE. Without it this prints the union and writes "
                         "nothing, which is what the skills promise")
    pp.set_defaults(fn=cmd_push)

    a = p.parse_args()
    try:
        a.fn(a)
    except SheetRefused as e:
        die(str(e), e.code)


if __name__ == "__main__":
    main()
