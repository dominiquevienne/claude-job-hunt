#!/usr/bin/env python3
"""The parsing core, tested without touching the network.

**Sixty-five of the scripts open a socket on a third-party site; testing
those in CI would mean sweeping the web on every commit**, which is the thing this project
teaches people not to do. So the perimeter is the pure-parsing core, and every
case here is synthetic. Issue #108.

**Most of these cases already existed — written by hand, run once, and read
afterwards.** `_robots.py`'s group grammar was corrected twice in one day
(#101) against exactly these inputs, typed into a shell. **A case that is not
executed is a comment**, and a comment does not fail when someone changes the
function under it.

## The access layer owes two instruments, not one

**This is not a rule against reading source.** Several cases here read files
and are right to: `DocumentedInvocationsAreReal` reads board cards because
**a card is text**, and what it checks — that a documented subcommand exists —
is a property of that text. `SourceCompilesWithoutWarning`, the import ban and
the corpus scans are the same kind. **None of them is touched by what
follows.** Anyone "correcting" them has misread this section.

The rule is narrower:

> **For any guard in the access-and-identity layer whose conclusion is
> behavioural, an exercised case accompanies the corpus scan. The scan is not
> replaced.**

**Because the two instruments prove different things and neither implies the
other.**

  * A **corpus scan** proves an absence across every file — no adapter binds
    its own agent, none assembles the refused URL. **Breadth without depth**:
    it sees the token and never the intent.
  * An **exercised case** proves the mechanism on one file — this request
    carried a TLS context, this header held the declared agent. **Depth
    without breadth**: it says nothing about the other sixty-four.

**The demonstration, which is why the rule exists rather than the reasoning.**
`TlsHostsAreRoutedEverywhere` scanned every adapter for an `import _tls` and
was green while one of them passed `context=None` — the import present, the
context absent, #104 back. An exercised case was added on `oposiciones.py`.
**Twelve hours later `empleate.py` could do the same thing unnoticed** — the
scan saw the import, the exercised case was looking at the other file. And
`empleate.py` is the adapter #104 was opened for.

**The temptation, once the exercised case exists, is to call the scan
redundant.** It would have been, until somebody adds a third adapter. *A
redundancy that only justifies itself at the third case is one that gets
removed at the second.*

**What it costs.** About four lines per case: the exercised ones written for
this run run 19 lines to a source-reading case's 15, and none of them opens a
socket — the opener is replaced by a function that captures the request. The
cheapest two are 7 and 12 lines with no stub at all, because the code was made
testable first: **a condition extracted into a function that returns its
verdict is cheaper to test than the same condition read through text.**

**And the cost falls at scale.** 53 of the 65 network readers share two names
for their fetching function (`get`, `fetch`), so one generic harness covers
82% of the corpus; on eight adapters sampled, seven exercised cleanly under
fifteen lines. **A rule whose cost collapses at scale is not the rule it looks
like when priced file by file.**

Adopted 2026-09-04. **Nothing is owed retroactively**: all eleven cases in
scope were brought up at the time, and each was mutated on the mutation that
used to leave it green.

Run: `python3 -m unittest discover -s tests -v`
"""

import argparse
import io
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "job-scan", "scripts"))

import importlib.util     # noqa: E402

import _decode           # noqa: E402
import _language          # noqa: E402
import _ldjson            # noqa: E402
import _locations         # noqa: E402
import _match             # noqa: E402
import _robots            # noqa: E402
import _secrets           # noqa: E402
import _sitemap           # noqa: E402


class RobotsGroups(unittest.TestCase):
    """The grammar, and both directions it was got wrong in one day."""

    def test_consecutive_user_agents_form_one_group(self):
        # Read as an overwrite, the `*` rule is lost and the error goes
        # towards permitted. Issue #101, defect 2.
        dis, allow = _robots._star_group(
            "User-agent: *\nUser-agent: Googlebot\nDisallow: /x\n")
        self.assertEqual(dis, ["/x"])
        self.assertEqual(allow, [])

    def test_a_named_agents_rule_is_not_ours(self):
        dis, _ = _robots._star_group(
            "User-agent: Googlebot\nDisallow: /a\n\n"
            "User-agent: *\nDisallow: /b\n")
        self.assertEqual(dis, ["/b"])

    def test_repeated_star_records_merge(self):
        # RFC 9309, and measured on a file with eight consecutive `*` groups.
        dis, _ = _robots._star_group(
            "User-agent: *\nDisallow: /a\n\nUser-agent: *\nDisallow: /b\n")
        self.assertEqual(dis, ["/a", "/b"])

    def test_a_group_restarts_after_a_directive(self):
        # Not only the grammar: **21 of 54 files in this repository's corpus
        # carry more than one record**, so this is the shape of a real file
        # and not a reading of §2.2.1.
        dis, _ = _robots._star_group(
            "User-agent: *\nDisallow: /a\nUser-agent: Bing\nDisallow: /b\n")
        self.assertEqual(dis, ["/a"])

    def test_comments_and_blank_lines_are_not_directives(self):
        dis, _ = _robots._star_group(
            "# User-agent: *\n# Disallow: /trap\n\n"
            "User-agent: *\nDisallow: /real  # trailing\n")
        self.assertEqual(dis, ["/real"])


class RobotsGroupSelection(unittest.TestCase):
    """The group that binds **us**, which is not always `*`. Issue #116."""

    CLOUDFLARE = (
        "User-agent: *\n"
        "Content-Signal: search=yes,ai-train=no,use=reference\n"
        "Allow: /\n\n"
        "User-agent: CCBot\nDisallow: /\n\n"
        "User-agent: ClaudeBot\nDisallow: /\n\n"
        "User-agent: GPTBot\nDisallow: /\n")

    def test_a_named_refusal_is_found(self):
        # The measured shape: `*` open, our token closed. Before #116 this
        # answered *allowed*, on the one kind of file that names us.
        token, dis, allow, matched = _robots.group_for(self.CLOUDFLARE)
        self.assertEqual(token, "claudebot")
        self.assertEqual(dis, ["/"])
        self.assertEqual(matched, ["claudebot"])

    def test_the_star_group_still_reads_as_open(self):
        # Both are true of the same file, which is why the group has to be
        # selected before anything is evaluated.
        dis, allow = _robots._star_group(self.CLOUDFLARE)
        self.assertEqual(dis, [])
        self.assertEqual(allow, ["/"])

    def test_a_named_permission_is_found_too(self):
        # The other direction, and it is real: taleez.com allows our tokens
        # by name. Selection is not a refusal detector.
        token, dis, allow, _m = _robots.group_for(
            "User-agent: *\nDisallow: /x\n\n"
            "User-agent: ClaudeBot\nAllow: /\n")
        self.assertEqual(token, "claudebot")
        self.assertEqual(allow, ["/"])
        self.assertEqual(dis, [])

    def test_falls_back_to_star_when_we_are_not_named(self):
        token, dis, _a, matched = _robots.group_for(
            "User-agent: *\nDisallow: /a\n\n"
            "User-agent: GPTBot\nDisallow: /\n")
        self.assertEqual(matched, [])
        self.assertEqual(token, "*")
        self.assertEqual(dis, ["/a"])

    def test_every_record_that_names_us_binds_us(self):
        """**This test used to assert the opposite, and the opposite was
        wrong.** It read `test_the_longest_matching_token_wins` and pinned
        the rule that made `www.linkedin.com` readable: four records refusing
        this project and one permitting it, and the longest name was the
        permissive one. A case that pins the wrong behaviour defends it.
        Issue #117."""
        _t, dis, _a, matched = _robots.group_for(
            "User-agent: ClaudeBot\nDisallow: /a\n\n"
            "User-agent: Claude-Web\nDisallow: /b\n")
        self.assertEqual(sorted(dis), ["/a", "/b"])
        self.assertEqual(sorted(matched), ["claude-web", "claudebot"])

    def test_the_linkedin_shape_one_permission_among_four_refusals(self):
        _t, dis, allow, matched = _robots.group_for(
            "User-agent: ClaudeBot\nDisallow: /\n\n"
            "User-agent: Claude-Web\nDisallow: /\n\n"
            "User-agent: Claude-User\nDisallow: /\n\n"
            "User-agent: Claude-SearchBot\nDisallow: /search\nAllow: /\n")
        self.assertIn("/", dis)
        # **The permission is not common to all four**, so it is not ours.
        self.assertEqual(allow, [])
        self.assertEqual(len(matched), 4)

    def test_an_allow_survives_only_if_every_record_grants_it(self):
        _t, _d, allow, _m = _robots.group_for(
            "User-agent: ClaudeBot\nAllow: /jobs\nAllow: /x\n\n"
            "User-agent: Claude-Web\nAllow: /jobs\n")
        self.assertEqual(allow, ["/jobs"])

    def test_our_tokens_are_declared_not_derived(self):
        """A module that decides consent must not depend on a UA string built
        elsewhere: an adapter changing its `UA` would silently change which
        rules bind.

        **Provenance, checked 2026-09-03 rather than assumed.** Anthropic's
        own documentation names three — `ClaudeBot`, `Claude-User`,
        `Claude-SearchBot`. Five are published by hosts in this corpus: those
        three plus `Claude-Web` and `anthropic-ai`. `anthropicbot` is in
        neither, and stays because **the two directions do not cost the same**:
        a token we answer to needlessly only binds us to more refusals, while
        a token we are missing loses a refusal aimed at us.

        **That missing direction is the one to keep checking** — enumerate the
        `User-agent` names across the corpus containing `claude` or
        `anthropic` and compare with this tuple. Nothing was missing on
        2026-09-03.
        """
        self.assertIn("claudebot", _robots.OUR_AGENTS)
        self.assertIn("claude-user", _robots.OUR_AGENTS)
        self.assertIn("claude-searchbot", _robots.OUR_AGENTS)
        self.assertTrue(all(a == a.lower() for a in _robots.OUR_AGENTS))

    def test_repeated_named_records_merge(self):
        token, dis, _a, _m = _robots.group_for(
            "User-agent: ClaudeBot\nDisallow: /a\n\n"
            "User-agent: ClaudeBot\nDisallow: /b\n")
        self.assertEqual((token, dis), ("claudebot", ["/a", "/b"]))


class RobotsPaths(unittest.TestCase):
    """`_match_len`: prefix, `*`, `$`, and the empty `Disallow`.

    **These cases came from reading RFC 9309, not from watching a host**, and
    the audit that followed #117 asked what that is worth. One of them rests
    on a genuine ambiguity: §2.2.2 says the winner is *"the match that has the
    most octets"*, and its only worked example — `Allow: /example/page/`
    against `Disallow: /example/page/disallowed.gif` — cannot separate **the
    length of the rule** from **the length of the matched text**. This module
    compares matched text; Google's own documentation describes rule length.

    **So it was measured rather than argued.** 1 402 probe paths were derived
    from the corpus's own rules — for every pattern in the group binding us on
    70 hosts, a path that pattern matches — and the two readings picked the
    same rule **every time**. 25 of 55 files use a wildcard, so the territory
    is real; the disagreement is not, on this corpus.

    **That is not a licence to leave it unexamined.** It is a belief with no
    host behind it, recorded as such, and `/tmp` is the wrong place for the
    probe — re-derive it when a file appears that pits a wildcard `Allow`
    against a longer literal `Disallow`.
    """

    def test_prefix_match_returns_its_length(self):
        self.assertEqual(_robots._match_len("/p", "/pq"), 2)

    def test_no_match_is_minus_one(self):
        self.assertEqual(_robots._match_len("/z", "/pq"), -1)

    def test_star_is_a_wildcard(self):
        self.assertEqual(_robots._match_len("/a*b", "/axxb"), 5)

    def test_dollar_anchors_the_end(self):
        self.assertEqual(_robots._match_len("/x$", "/x"), 2)
        self.assertEqual(_robots._match_len("/x$", "/xy"), -1)

    def test_an_empty_disallow_is_not_a_refused_path_in_the_verdict(self):
        """`_match_len` knew this; `verdict()` did not, and counted it.

        **`employtt.gov.tt` publishes 26 bytes** — `User-agent: *` and a bare
        `Disallow:` — the most permissive file there is. The sentence came out
        *"this host refuses 1 path(s) to `*` ... :"* with nothing after the
        colon. **The permission was right and the account of it was wrong**,
        which is its own kind of wrong: a reader deciding whether to write an
        adapter reads the sentence.
        """
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda host: {
            "state": "read", "final": host, "attempts": 1,
            "body": "User-agent: *\nDisallow:\n"}
        try:
            v = _robots.verdict("employtt.gov.tt")
            self.assertIs(v["sweep"], True)
            self.assertEqual(v["disallow"], [])
            self.assertIsNone(v["reason"])
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_an_empty_disallow_matches_nothing(self):
        # It is how a file says *nothing is closed*. Matching everything at
        # length zero would close the site instead.
        self.assertEqual(_robots._match_len("", "/anything"), -1)


class RobotsLooksLikeRules(unittest.TestCase):
    """An absent `Content-Type` is not a declaration of HTML. Issue #96."""

    def test_markup_is_not_a_rules_file(self):
        self.assertFalse(_robots._looks_like_rules(
            "<!DOCTYPE html><html><body>Sitemap: /x</body></html>"))

    def test_a_directive_makes_it_one(self):
        self.assertTrue(_robots._looks_like_rules(
            "User-agent: *\nDisallow: /a\n"))

    def test_prose_is_neither(self):
        self.assertFalse(_robots._looks_like_rules("hello world"))


class Sitemap(unittest.TestCase):
    """The three ways a populated sitemap reads as empty. Issue #55."""

    def test_cdata_wrapped_loc(self):
        body = ("<urlset><url><loc><![CDATA[ https://a/1 ]]></loc></url>"
                "</urlset>")
        self.assertEqual(_sitemap.locs(body), ["https://a/1"])

    def test_namespace_prefixed_loc(self):
        self.assertEqual(_sitemap.locs("<x><ns:loc>https://b/1</ns:loc></x>"),
                         ["https://b/1"])

    def test_counts_elements_not_lines(self):
        one_line = "<urlset>" + "".join(
            f"<url><loc>https://c/{i}</loc></url>" for i in range(91)
        ) + "</urlset>"
        self.assertEqual(_sitemap.count(one_line)["locs"], 91)
        self.assertEqual(one_line.count("\n"), 0)

    def test_gzip_served_as_text_is_decompressed(self):
        import gzip
        raw = gzip.compress(b"<urlset><url><loc>https://d/1</loc></url></urlset>")
        self.assertEqual(_sitemap.locs(raw), ["https://d/1"])

    def test_zero_locs_never_says_the_sitemap_is_empty(self):
        says = _sitemap.count_says(
            "<urlset><url><lastmod>2026-01-01</lastmod></url></urlset>")
        self.assertIn("impossible", says.lower())

    def test_contains_filters(self):
        body = "<x><loc>https://a/keep/1</loc><loc>https://a/drop/2</loc></x>"
        self.assertEqual(_sitemap.locs(body, contains="/keep/"),
                         ["https://a/keep/1"])


class LdJson(unittest.TestCase):
    """Polymorphic schema.org fields. Issue #57."""

    def test_one_returns_a_dict_for_a_string(self):
        # Documented behaviour: `one(x).get(...)` must always be legal.
        self.assertEqual(_ldjson.one("a string"), {})

    def test_one_picks_the_first_object_of_a_list(self):
        self.assertEqual(_ldjson.one([{"a": 1}, {"b": 2}]), {"a": 1})

    def test_label_returns_the_string_a_string_carries(self):
        self.assertEqual(_ldjson.label("FULL_TIME"), "FULL_TIME")

    def test_label_reads_an_objects_name(self):
        self.assertEqual(_ldjson.label({"name": "CDI"}), "CDI")

    def test_label_joins_a_list(self):
        self.assertEqual(_ldjson.label(["a", "b"]), "a, b")

    def test_single_quoted_script_type_is_read(self):
        html = ("<script type='application/ld+json'>"
                '{"@type":"JobPosting","title":"x"}</script>')
        self.assertEqual([p.get("title") for p in _ldjson.postings(html)],
                         ["x"])

    def test_literal_newline_inside_a_string_still_parses(self):
        # Two boards of ten need `strict=False`, and you do not know which
        # board will be the third.
        html = ('<script type="application/ld+json">'
                '{"@type":"JobPosting","description":"a\nb"}</script>')
        self.assertEqual(len(_ldjson.postings(html)), 1)


class Secrets(unittest.TestCase):
    """Credentials from a file as well as the environment. Issue #110."""

    def _write(self, text):
        import tempfile
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "credentials.env"), "w",
                  encoding="utf-8") as f:
            f.write(text)
        return d

    def test_reads_key_equals_value(self):
        d = self._write("A_KEY=abc\n")
        old = os.environ.get("JOB_HUNT_HOME")
        os.environ["JOB_HUNT_HOME"] = d
        try:
            _secrets._CACHE.clear()
            self.assertEqual(_secrets.get("A_KEY"), "abc")
        finally:
            _secrets._CACHE.clear()
            if old is None:
                del os.environ["JOB_HUNT_HOME"]
            else:
                os.environ["JOB_HUNT_HOME"] = old

    def test_ignores_comments_strips_quotes_and_export(self):
        d = self._write('# c\nexport B_KEY="xy"\n\nC_KEY=\'z\'\n')
        old = os.environ.get("JOB_HUNT_HOME")
        os.environ["JOB_HUNT_HOME"] = d
        try:
            _secrets._CACHE.clear()
            got = _secrets.load()
            self.assertEqual(got.get("B_KEY"), "xy")
            self.assertEqual(got.get("C_KEY"), "z")
        finally:
            _secrets._CACHE.clear()
            if old is None:
                del os.environ["JOB_HUNT_HOME"]
            else:
                os.environ["JOB_HUNT_HOME"] = old

    def test_the_environment_wins(self):
        d = self._write("D_KEY=from-file\n")
        old_ws, old_d = os.environ.get("JOB_HUNT_HOME"), os.environ.get("D_KEY")
        os.environ["JOB_HUNT_HOME"] = d
        os.environ["D_KEY"] = "from-env"
        try:
            _secrets._CACHE.clear()
            self.assertEqual(_secrets.get("D_KEY"), "from-env")
        finally:
            _secrets._CACHE.clear()
            for k, v in (("JOB_HUNT_HOME", old_ws), ("D_KEY", old_d)):
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_printing_the_container_shows_no_value(self):
        # The accident a plain dict invites. Not a substitute for not printing
        # what `get()` returns — see the class docstring.
        m = _secrets.Masked({"K": "supersecret"})
        self.assertNotIn("supersecret", repr(m))
        self.assertNotIn("supersecret", f"{m}")
        self.assertIn("11 chars", repr(m))

    def test_the_message_gives_both_routes(self):
        note = _secrets.missing_note(["X_KEY"], "svc", "Service", "example.com")
        self.assertIn("credentials.env", note)
        self.assertIn("set -a", note)
        self.assertIn("config.yml", note)


def _stdlib_names():
    """The standard library's module names, on every version this runs on.

    **`sys.stdlib_module_names` is 3.10+, and this file is the only thing in
    the repository that needed it.** `core.yml` declares 3.9 as the floor and
    documents it as *measured* — but it was measured on `bin/`, not on
    `tests/`, so the three 3.9 cells were red by construction from the first
    run. **A conformance check set on the participants instead of the
    obligated**, which is the shape this suite catches elsewhere. #143.

    The floor is a promise in `README.md`. Raising it to fit a test would be
    changing a published promise to make a check pass, so the check changes
    instead.

    Derived from `sysconfig` when the attribute is absent: the names of the
    modules and packages in the stdlib directory, the frozen builtins, and the
    dynamically loaded extensions. Verified against `sys.stdlib_module_names`
    on 3.14 — the derivation misses eleven platform C modules
    (`_winapi`, `msvcrt`, `_tkinter` …) and **none of the 53 modules this
    repository imports.**
    """
    names = set(getattr(sys, "stdlib_module_names", ()))
    if names:
        return names
    import glob as _glob
    import sysconfig
    names = set(sys.builtin_module_names)
    std = sysconfig.get_path("stdlib")
    for path in _glob.glob(os.path.join(std, "*.py")):
        names.add(os.path.basename(path)[:-3])
    for path in _glob.glob(os.path.join(std, "*", "__init__.py")):
        names.add(os.path.basename(os.path.dirname(path)))
    # **C extensions live in two different places.** POSIX puts them in
    # `lib-dynload/*.so`; Windows puts them in `<base_prefix>/DLLs/*.pyd`.
    # Scanning only the first left `unicodedata` outside the set and turned
    # `windows-latest · python 3.9` red while the other eight cells were
    # green — the derivation was written and checked on one platform.
    for ext_dir in (os.path.join(sysconfig.get_path("platstdlib"),
                                 "lib-dynload"),
                    os.path.join(sys.base_prefix, "DLLs"),
                    os.path.join(sys.base_prefix, "lib", "lib-dynload")):
        for path in _glob.glob(os.path.join(ext_dir, "*")):
            names.add(os.path.basename(path).split(".")[0])
    return names


class NoDependencies(unittest.TestCase):
    """The README promises a zero-install path. **This is what makes it true.**

    *"Every Python script in this plugin uses the standard library and nothing
    else"* is a claim about every file, so it is checked rather than asserted
    — and it is the kind of claim that rots on the first convenient `import`.
    Issue #113.
    """

    def test_nothing_outside_the_standard_library_is_imported(self):
        import ast
        import glob
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        std = _stdlib_names()
        local = {os.path.basename(f)[:-3] for f in
                 glob.glob(os.path.join(root, "skills", "job-scan",
                                        "scripts", "*.py"))}
        offenders = {}
        files = (glob.glob(os.path.join(root, "skills", "**", "*.py"),
                           recursive=True)
                 + glob.glob(os.path.join(root, "bin", "*.py"))
                 + glob.glob(os.path.join(root, "tests", "*.py")))
        for f in files:
            with open(f, encoding="utf-8") as fh:
                try:
                    tree = ast.parse(fh.read())
                except SyntaxError:
                    continue
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [a.name.split(".")[0] for a in node.names]
                elif (isinstance(node, ast.ImportFrom) and node.level == 0
                      and node.module):
                    mods = [node.module.split(".")[0]]
                for m in mods:
                    if m in std or m in local or m.startswith("_"):
                        continue
                    offenders.setdefault(m, set()).add(os.path.basename(f))
        self.assertEqual(
            offenders, {},
            f"a dependency would break the zero-install path: {offenders}")


class Locations(unittest.TestCase):
    """Folding. A regression here is invisible and falsifies every place."""

    def test_diacritics_fold(self):
        self.assertEqual(_locations.fold("Zürich"), _locations.fold("Zurich"))

    def test_case_folds(self):
        self.assertEqual(_locations.fold("GENÈVE"), _locations.fold("geneve"))

    def test_a_different_city_does_not_fold_together(self):
        self.assertNotEqual(_locations.fold("Bern"), _locations.fold("Bienne"))


class Language(unittest.TestCase):
    """It refuses to guess a translation, on purpose. Issue #70."""

    def test_an_unmeasured_market_says_nothing(self):
        self.assertIsNone(_language.language_note("developer", "ZZ", ("fr",)))


class Match(unittest.TestCase):
    """A board's reported count is not a match count. Issue #62."""

    def test_only_a_card_naming_both_is_an_assertion(self):
        # `literal` is the only verdict; the others are questions, and the
        # docstring says so. A test that treated them as booleans would have
        # asserted the opposite of what this module promises.
        verdict, reason = _match.classify("Senior PHP Developer", "Genève",
                                          "PHP", "Genève")
        self.assertEqual(verdict, "literal")
        self.assertIsNone(reason)

    def test_a_wrong_place_is_a_question_and_names_it(self):
        verdict, reason = _match.classify("Senior PHP Developer", "Lyon",
                                          "PHP", "Genève")
        self.assertEqual(verdict, "regional?")
        self.assertIn("Genève", reason)

    def test_a_wrong_trade_is_a_question_and_names_it(self):
        verdict, reason = _match.classify("Chef de rang", "Genève", "PHP",
                                          "Genève")
        self.assertEqual(verdict, "semantic?")
        self.assertIn("php", reason.lower())

    def test_flatten_pads_so_a_term_is_not_a_prefix(self):
        # ` php ` must not match `phpstorm`, or every card becomes a match.
        self.assertIn(" php ", _match.flatten("A PHP role"))
        self.assertNotIn(" php ", _match.flatten("phpstorm licences"))

    def test_matches_city_folds_diacritics(self):
        self.assertTrue(_match.matches_city("Genève, Suisse", "Geneve"))

    def test_share_reports_both_numbers(self):
        """**This test used to feed `share()` booleans.** `classify()` returns
        `literal` / `regional?` / `semantic?`, so `{"match": True}` is a row no
        adapter ever produces — and the sentence came out *"3 of 3 rows (100%)
        did not literally match — 2 True, 1 False"*, which the assertions
        `assertIn("3")` and `assertIn("2")` accepted. A loose assertion over
        the wrong vocabulary passes for the wrong reason."""
        said = _match.share([{"match": "literal"}, {"match": "regional?"},
                             {"match": "literal"}])
        self.assertIn("1 of 3 rows (33%)", said)
        self.assertIn("2 literal, 1 regional?", said)

    def test_share_says_nothing_when_every_row_matched(self):
        """**The behaviour that matters, and nothing covered it** — because
        the old row shape could never produce it: with booleans, `literal` is
        always 0 and the silent branch is unreachable."""
        self.assertIsNone(_match.share([{"match": "literal"},
                                        {"match": "literal"}]))

    def test_share_says_nothing_about_nothing(self):
        self.assertIsNone(_match.share([]))


def _load_render_plain():
    """The module's file name has a hyphen, so it cannot be imported by name."""
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "skills", "cover-letter", "render-plain.py")
    spec = importlib.util.spec_from_file_location("render_plain", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rp = _load_render_plain()


class RenderPlain(unittest.TestCase):
    """The no-LaTeX route: what it keeps, and what it must say it lost.

    **The point of these is the loss, not the rendering.** A PDF that came out
    beautiful and dropped the euro sign from a salary line is the failure; a
    PDF that says which characters it could not print is not.
    """

    def test_typographic_variants_are_substituted_not_dropped(self):
        text, dropped = rp.to_winansi("−15 % ≈ 40 k€ …")
        self.assertEqual(text, "-15 % ~ 40 k€ ...")
        self.assertEqual(dropped, {})

    def test_french_accents_and_guillemets_survive(self):
        text, dropped = rp.to_winansi("Élodie Müller — « à Genève », coût")
        self.assertEqual(text, "Élodie Müller — « à Genève », coût")
        self.assertEqual(dropped, {})

    def test_a_character_with_no_glyph_is_named_never_a_question_mark(self):
        text, dropped = rp.to_winansi("Ωmega")
        self.assertNotIn("?", text)
        self.assertEqual(text, "mega")
        self.assertIn("Ω", dropped)
        self.assertEqual(dropped["Ω"][0], "GREEK CAPITAL LETTER OMEGA")

    def test_the_count_is_per_occurrence(self):
        _text, dropped = rp.to_winansi("中中中")
        self.assertEqual(dropped["中"][1], 3)

    def test_the_pdf_declares_winansi_and_carries_no_image(self):
        pdf, pages, dropped = rp.build("# Title\n\n- Coût : 40 k€\n")
        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertEqual(pages, 1)
        self.assertEqual(dropped, {})
        self.assertIn(b"/WinAnsiEncoding", pdf)
        self.assertIn(b"/BaseFont /Helvetica", pdf)
        # The ATS properties, asserted rather than described: no image, no
        # form XObject, and a page tree of exactly one column of text.
        self.assertNotIn(b"/Image", pdf)
        self.assertNotIn(b"/XObject", pdf)
        self.assertIn(b"startxref", pdf)

    def test_headings_bullets_and_emphasis_reach_the_line_list(self):
        lines = rp.lines_of("# N\n\n## Sec\n\n### Role\n\n- **a** *b*\n",
                            "resume")
        self.assertIn(("t", "N"), lines)
        self.assertIn(("h", "SEC"), lines)
        self.assertIn(("sh", "Role"), lines)
        self.assertIn(("li", "• a b"), lines)

    def test_a_letter_keeps_its_heading_case(self):
        self.assertIn(("h", "Objet"), rp.lines_of("## Objet\n", "letter"))

    def test_wrap_never_exceeds_the_width_it_was_given(self):
        for line in rp.wrap("alpha beta gamma delta epsilon zeta", 12):
            self.assertLessEqual(len(line), 12)


class WhichStatusMeansWhat(unittest.TestCase):
    """**Nothing pinned the status tables, so either could shrink in
    silence.**

    Reducing `(401, 403, 429, 451)` to `(403,)` left the suite green, and so
    did reducing `(404, 410)` to `(404,)` — every case exercised 403 and 404
    and no other member of either set. **A table tested through one of its
    entries is a table with one entry, as far as the suite is concerned.**

    It matters because the two classes lead to opposite conduct. An `absent`
    is knowledge — no file, therefore no rules, therefore an open door. A
    `refused` stops this module cold. **A status sliding from one set to the
    other moves a host between those two**, and after the 2026-09-04 decision
    the door is genuinely open on the permissive side.
    """

    def _verdict(self, code):
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        back = _robots._BACKOFF
        _robots._BACKOFF = (0, 0)

        def fail(*a, **k):
            raise _robots.urllib.error.HTTPError(
                "https://h.example/robots.txt", code, "x", {},
                io.BytesIO(b""))

        _robots.urllib.request.urlopen = fail
        try:
            return _robots.verdict("h.example")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._BACKOFF = back
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_every_refusing_status_refuses(self):
        """401, 429 and 451 are not decoration: a host that rate-limits or
        answers *unavailable for legal reasons* **answered**, and it did not
        answer yes."""
        for code in (401, 403, 429, 451):
            with self.subTest(code=code):
                v = self._verdict(code)
                self.assertEqual(v["state"], "refused",
                                 f"HTTP {code} is no longer a refusal")
                self.assertIsNot(v["sweep"], True)

    def test_every_absent_status_is_an_absence(self):
        """**410 is a stronger 404**, not a weaker one — the host says the
        file was here and is deliberately gone."""
        for code in (404, 410):
            with self.subTest(code=code):
                v = self._verdict(code)
                self.assertEqual(v["state"], "absent",
                                 f"HTTP {code} is no longer an absence")

    def test_the_two_sets_do_not_overlap(self):
        """A status in both would make the verdict depend on branch order."""
        import re
        src = open(os.path.join(SCRIPTS, "_robots.py"), encoding="utf-8").read()
        got = re.findall(r"e\.code in \(([0-9, ]+)\)", src)
        self.assertGreaterEqual(len(got), 2, "the status tables moved")
        sets = [set(int(x) for x in g.replace(" ", "").split(",") if x)
                for g in got[:2]]
        self.assertEqual(sets[0] & sets[1], set(),
                         "a status is in both the absent and refusing sets")


class RobotsThirdState(unittest.TestCase):
    """A failure to read must never come back as a permission. Issue #118.

    **This is the case the module got wrong for its whole life**, so every
    branch of it is pinned here: `nea.gov.kh` closes everything to `ClaudeBot`
    by name, and a timed-out request used to return `allowed: True`.
    """

    def setUp(self):
        self._real = _robots._fetch
        _robots._CACHE.clear()
        _robots._ALIAS.clear()

    def tearDown(self):
        _robots._fetch = self._real
        _robots._CACHE.clear()
        _robots._ALIAS.clear()

    def _serve(self, result):
        _robots._fetch = lambda host: dict(result, final=host, attempts=1)

    def test_a_failed_fetch_is_never_a_permission(self):
        self._serve({"state": "unreachable", "why": "timed out"})
        v = _robots.verdict("nea.gov.kh")
        self.assertIsNone(v["sweep"])
        self.assertFalse(v["certain"])
        self.assertIsNone(_robots.allowed("nea.gov.kh", "/jobs")["allowed"])

    def test_the_unknown_is_falsy_so_a_naive_caller_fails_closed(self):
        """**The whole design rests on this.** Thirty-six adapters write
        `if not v["sweep"]: die(...)` and none of them had heard of a third
        state; `None` makes both naive readings the safe one."""
        self._serve({"state": "unreachable", "why": "timed out"})
        v = _robots.verdict("example.invalid")
        self.assertFalse(v["sweep"])          # `if not v["sweep"]` refuses
        self.assertFalse(bool(v["sweep"]))    # `if v["sweep"]` does not fetch

    def test_a_403_is_a_refusal_not_an_absence(self):
        self._serve({"state": "refused",
                     "why": "HTTP 403 — the host refuses to serve its rules "
                            "file"})
        v = _robots.verdict("barbadosjobregister.gov.bb")
        self.assertIs(v["sweep"], False)
        self.assertIn("the reply was no", v["reason"])
        self.assertIs(
            _robots.allowed("barbadosjobregister.gov.bb", "/x")["allowed"],
            False)

    def test_a_404_is_still_a_permission_because_it_is_knowledge(self):
        """**The one silence that really is one.** Confusing the two
        directions is how this defect started: the fix must not invent a
        refusal out of a host that published nothing."""
        self._serve({"state": "absent", "why": "HTTP 404"})
        v = _robots.verdict("philjobnet.gov.ph")
        self.assertIs(v["sweep"], True)
        self.assertTrue(v["certain"])
        self.assertIs(_robots.allowed("philjobnet.gov.ph", "/x")["allowed"],
                      True)

    def test_a_body_that_is_not_a_rules_file_permits_but_is_not_certain(self):
        self._serve({"state": "unreadable", "why": "Content-Type 'text/html'"})
        v = _robots.verdict("my.indeed.com")
        self.assertIs(v["sweep"], True)
        self.assertFalse(v["certain"])

    def test_an_unknown_is_not_cached_a_transient_must_not_poison_a_run(self):
        self._serve({"state": "unreachable", "why": "timed out"})
        _robots.verdict("flaky.example")
        self.assertNotIn("flaky.example", _robots._CACHE)
        self._serve({"state": "read", "body": "User-agent: *\nAllow: /\n"})
        self.assertIs(_robots.verdict("flaky.example")["sweep"], True)

    def test_a_named_refusal_still_wins_when_the_file_arrives(self):
        """`nea.gov.kh`'s actual file, trimmed. The verdict it should always
        have given, and does whenever the fetch succeeds."""
        self._serve({"state": "read", "body":
                     "User-agent: *\nAllow: /\n\n"
                     "User-agent: ClaudeBot\nDisallow: /\n"})
        v = _robots.verdict("nea.gov.kh")
        self.assertIs(v["sweep"], False)
        self.assertEqual(v["group"], "claudebot")


class RobotsRetry(unittest.TestCase):
    """**Only an unknown is worth asking twice.** A slow host used to be a
    permissive host; a host that has already answered is not asked again."""

    def test_the_ladder_keeps_more_than_one_rung(self):
        """**The population this class stands on, which nothing asserted.**
        Cutting `_TIMEOUTS` from three rungs to one left every case here green
        — they pin *that* a retry happens and *when*, never *how many times*.

        It matters in one direction only, and that direction is the module's
        whole subject: **fewer attempts means more hosts filed `unreachable`**,
        which stops the sweep. That errs safe and it errs silently, and on this
        module every silent change has cost something.
        """
        self.assertGreaterEqual(len(_robots._TIMEOUTS), 3,
                                "the retry ladder lost a rung without any "
                                "case noticing")
        self.assertEqual(len(_robots._BACKOFF), len(_robots._TIMEOUTS) - 1,
                         "there must be one wait between each pair of "
                         "attempts, no more and no fewer")
        self.assertEqual(sorted(_robots._TIMEOUTS), list(_robots._TIMEOUTS),
                         "the timeouts no longer increase — a retry that "
                         "waits less than the attempt before it is not a "
                         "second chance")

    def setUp(self):
        self._real = _robots._fetch_once
        # The backoff is real seconds on a real sweep and nothing here is
        # testing the clock; a suite that sleeps five seconds gets run less.
        self._sleep = _robots.time.sleep
        _robots.time.sleep = lambda _s: None
        self.calls = []

    def tearDown(self):
        _robots._fetch_once = self._real
        _robots.time.sleep = self._sleep

    def _answer(self, state):
        def fake(url, host, timeout):
            self.calls.append(timeout)
            return {"state": state, "why": "x", "final": host}
        _robots._fetch_once = fake

    def test_an_unreachable_host_is_retried_with_widening_timeouts(self):
        self._answer("unreachable")
        got = _robots._fetch("slow.example")
        self.assertEqual(self.calls, list(_robots._TIMEOUTS))
        self.assertEqual(got["attempts"], len(_robots._TIMEOUTS))

    def test_an_answer_is_not_repeated(self):
        for state in ("read", "absent", "refused", "unreadable"):
            with self.subTest(state=state):
                self.calls = []
                self._answer(state)
                got = _robots._fetch("x.example")
                self.assertEqual(len(self.calls), 1)
                self.assertEqual(got["attempts"], 1)


class RobotsThreeFormulations(unittest.TestCase):
    """Named and refused, named and permitted, not named. Issue #117.

    **The middle one had no words at all** — `reason` stayed `None`, which is
    what a file that says nothing about us also produces. They are different
    facts and the sentence has to say which one this is.
    """

    def setUp(self):
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        self._real = _robots._fetch

    def tearDown(self):
        _robots._fetch = self._real
        _robots._CACHE.clear()
        _robots._ALIAS.clear()

    def _body(self, body):
        _robots._fetch = lambda host: {"state": "read", "body": body,
                                       "final": host, "attempts": 1}

    def test_named_and_permitted_says_so_and_says_why_star_does_not_bind(self):
        # taleez.com's shape: `*` refuses a dozen paths, our token is granted
        # everything by name.
        self._body("User-agent: *\nDisallow: /api/\nDisallow: /u/\n\n"
                   "User-agent: ClaudeBot\nAllow: /\n")
        v = _robots.verdict("taleez.com")
        self.assertIs(v["sweep"], True)
        self.assertIn("names this project and permits it", v["reason"])
        self.assertIn("do not bind us", v["reason"])

    def test_named_and_refused_says_the_refusal_is_aimed_at_us(self):
        self._body("User-agent: *\nAllow: /\n\n"
                   "User-agent: ClaudeBot\nDisallow: /\n")
        v = _robots.verdict("nea.gov.kh")
        self.assertIs(v["sweep"], False)
        self.assertIn("names this project", v["reason"])

    def test_not_named_says_the_policy_is_general(self):
        self._body("User-agent: *\nDisallow: /\n")
        v = _robots.verdict("plain.example")
        self.assertIs(v["sweep"], False)
        self.assertIn("evenly", v["reason"])
        self.assertEqual(v["groups"], [])

    def test_records_that_disagree_are_reported_not_smoothed_over(self):
        self._body("User-agent: ClaudeBot\nDisallow: /\n\n"
                   "User-agent: Claude-SearchBot\nAllow: /\n")
        v = _robots.verdict("www.linkedin.com")
        self.assertIs(v["sweep"], False)
        self.assertTrue(v["group_conflict"])
        self.assertIn("does not answer them alike", v["reason"])

    def test_records_that_agree_say_so_without_alarm(self):
        self._body("User-agent: ClaudeBot\nAllow: /\n\n"
                   "User-agent: Claude-Web\nAllow: /\n")
        v = _robots.verdict("taleez.com")
        self.assertFalse(v["group_conflict"])
        self.assertIn("says the same thing to each", v["reason"])

    def test_a_path_with_no_matching_rule_names_the_group_it_checked(self):
        self._body("User-agent: *\nDisallow: /api/\n\n"
                   "User-agent: ClaudeBot\nAllow: /\n")
        a = _robots.allowed("taleez.com", "/api/x")
        # Correct per RFC 9309 — a record naming us replaces `*` — and the
        # reason has to say that, because it looks wrong at a glance.
        self.assertIs(a["allowed"], True)
        self.assertIn("names this project", a["reason"])


class Decode(unittest.TestCase):
    """Read the declared charset. Issue #115.

    **`decode("utf-8", "replace")` cannot fail**, which is the whole problem:
    it returns plausible text with holes in it and nothing raises.
    """

    class _Headers(dict):
        def get_content_charset(self):
            ct = self.get("Content-Type", "")
            import re as _re
            m = _re.search(r"charset=([\w\-]+)", ct)
            return m.group(1).lower() if m else None

    def test_the_header_is_believed_first(self):
        h = self._Headers({"Content-Type": "text/html;charset=ISO-8859-1"})
        text, enc = _decode.decode_body(b"Pudahuel \xa1Comisiones", h)
        self.assertEqual(text, "Pudahuel ¡Comisiones")
        self.assertEqual(enc, "iso-8859-1")

    def test_utf8_replace_is_what_this_replaces(self):
        """The `bne.gob.cl` bytes, and the two readings side by side."""
        raw = b"Pudahuel \xa1Comisiones"
        self.assertIn("\ufffd", raw.decode("utf-8", "replace"))
        self.assertNotIn("\ufffd", raw.decode("cp1252"))

    def test_a_meta_charset_is_read_when_the_header_is_silent(self):
        raw = b'<html><head><meta charset="windows-1252"><body>caf\xe9'
        name, where = _decode.charset_of(None, raw)
        self.assertEqual((name, where), ("windows-1252", "meta"))

    def test_an_xml_prolog_counts_as_a_declaration(self):
        """**Sitemaps declare here and nowhere else**, and this repository
        reads a sitemap on nearly every board. Issue #115."""
        raw = b'<?xml version="1.0" encoding="ISO-8859-1"?><loc>caf\xe9</loc>'
        self.assertEqual(_decode.charset_of(None, raw), ("iso-8859-1", "xml"))
        self.assertTrue(_decode.decode_body(raw)[0].endswith(
            "<loc>café</loc>"))

    def test_a_prolog_must_be_first_a_mention_later_is_not_a_declaration(self):
        raw = b'<urlset><note><?xml encoding="ISO-8859-1"?></note></urlset>'
        self.assertEqual(_decode.charset_of(None, raw), (None, None))

    def test_strict_first_then_a_total_fallback_and_it_says_which(self):
        # Not valid UTF-8 and nothing declared: cp1252 maps every byte, so it
        # is chosen for being total rather than for being right — and the
        # second value is how the caller learns that.
        text, enc = _decode.decode_body(b"caf\xe9 \x93x\x94")
        self.assertEqual(enc, "cp1252")
        self.assertNotIn("\ufffd", text)

    def test_valid_utf8_stays_utf8_when_nothing_is_declared(self):
        text, enc = _decode.decode_body("café €".encode("utf-8"))
        self.assertEqual((text, enc), ("café €", "utf-8"))

    def test_a_string_passes_through_and_says_so(self):
        self.assertEqual(_decode.decode_body("already text"),
                         ("already text", "str"))

    def test_an_unknown_charset_name_falls_through_instead_of_raising(self):
        h = self._Headers({"Content-Type": "text/html;charset=x-nonesuch"})
        text, enc = _decode.decode_body("café".encode("utf-8"), h)
        self.assertEqual((text, enc), ("café", "utf-8"))


class RobotsStorage403(unittest.TestCase):
    """A 403 that carries an object-storage error document. Issue #118.

    **The hint is allowed; the conclusion is not.** On S3 a missing key
    answers 403 because listing is not granted, so a static site with no
    robots.txt can answer 403 where the identical site with a custom error
    page answers 200 — measured on two Chilean government portals.
    """

    class _Err:
        def __init__(self, body):
            self._body = body

        def read(self, n=None):
            return self._body[:n] if n else self._body

    def test_an_s3_error_document_is_named_as_a_hint(self):
        note = _robots._storage_note(self._Err(
            b'<?xml version="1.0"?><Error><Code>AccessDenied</Code></Error>'))
        self.assertIn("object-storage error document", note)
        self.assertIn("hint, not a finding", note)

    def test_a_firewall_page_gets_no_such_note(self):
        note = _robots._storage_note(
            self._Err(b"Request is Blocked by Firewall"))
        self.assertEqual(note, "")

    def test_a_body_that_cannot_be_read_tells_us_nothing(self):
        class Broken:
            def read(self, n=None):
                raise OSError("connection reset")
        self.assertEqual(_robots._storage_note(Broken()), "")

    def test_the_hint_never_turns_the_refusal_into_a_permission(self):
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda host: {
            "state": "refused", "final": host, "attempts": 1,
            "why": "HTTP 403 — the host refuses to serve its rules file. "
                   "**The body is an object-storage error document**"}
        try:
            v = _robots.verdict("www.trabajaenelestado.cl")
            self.assertIs(v["sweep"], False)
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()


def guard_is_last(source):
    """`(ok, classes_after)` — is the `__main__` guard the last statement?

    **A free function so it can be tested on sources other than this file.**
    The first attempt asserted the property only about `test_core.py` itself,
    and the negative check — appending a class to a copy in a temp directory —
    came back red for an import error rather than for the defect. **A check
    whose failure is indistinguishable from an unrelated failure has not been
    verified**, and it nearly went in as verified.
    """
    import ast
    tree = ast.parse(source)
    if not tree.body:
        return False, []
    last = tree.body[-1]
    is_guard = (isinstance(last, ast.If) and any(
        isinstance(n, ast.Name) and n.id == "__name__"
        for n in ast.walk(last.test)))
    idx = next((i for i, n in enumerate(tree.body)
                if isinstance(n, ast.If) and any(
                    isinstance(x, ast.Name) and x.id == "__name__"
                    for x in ast.walk(n.test))), None)
    after = ([n.name for n in tree.body[idx + 1:] if isinstance(n, ast.ClassDef)]
             if idx is not None else [])
    return is_guard, after


class SuiteRuns(unittest.TestCase):
    """**A green run that covered 59% of the suite.** Found by the test audit.

    `python3 tests/test_core.py` ran **51 of 87** cases and printed OK: the
    `if __name__ == "__main__"` block had drifted into the middle of the file,
    so every class appended after it was defined only *after*
    `unittest.main()` had already run and exited. The documented invocation
    (`python3 -m unittest discover`) was unaffected, which is exactly why
    nothing showed. **A clean run is not a clean state.**
    """

    GOOD = ('import unittest\n\n\nclass A(unittest.TestCase):\n'
            '    def test_x(self):\n        pass\n\n\n'
            'if __name__ == "__main__":\n    unittest.main()\n')
    BROKEN = GOOD + '\n\nclass B(unittest.TestCase):\n    pass\n'

    def test_the_check_accepts_a_well_formed_file(self):
        self.assertEqual(guard_is_last(self.GOOD), (True, []))

    def test_the_check_rejects_a_class_appended_after_the_guard(self):
        """**The negative case, on a source built for it** — not on a copy of
        this file in a temp directory, where a red result means the imports
        failed."""
        ok, after = guard_is_last(self.BROKEN)
        self.assertFalse(ok)
        self.assertEqual(after, ["B"])

    def test_this_file_puts_its_guard_last(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "test_core.py")
        ok, after = guard_is_last(open(path, encoding="utf-8").read())
        self.assertTrue(ok, "the `__main__` guard is not the last statement: "
                             "anything after it is invisible to `python3 "
                             "tests/test_core.py`, which will still print OK")
        self.assertEqual(after, [])


SCRIPTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "job-scan", "scripts")


class SalaryCarriesItsUnit(unittest.TestCase):
    """**A number in an unknown unit is worse than a number absent, because it
    compares.** `shared/plausible-and-false.md`, mechanism 1.

    Found by auditing the fields adapters trust, after `mihnati.com` published
    `baseSalary.currency: "PKR"` on Saudi jobs. Two ways of losing the unit
    turned up, neither of which involves a board lying:

    **Descending past it.** In schema.org's `MonetaryAmount`, `currency` is a
    **sibling** of `value`, not a child — so `one(jp["baseSalary"])["value"]`,
    the shape eight adapters use to reach `minValue`, walks straight past it.
    `batiactu.py` did, and a ledger got `42000.00` with no unit while the page
    published `{"currency": "EUR", "value": {"minValue": "42000.00", ...}}`.

    **Knowing it too well to write it down.** Three single-country boards
    omitted the currency because it was obvious to whoever wrote the adapter,
    and absent from the row a ledger keeps. `adzuna.py` was the sharp case:
    **nineteen country indexes through one code path, and no currency field
    anywhere in the API's response**, so `salary_min: 90000` was CHF, GBP,
    BRL or ZAR depending on a flag.
    """

    def _emitters(self):
        import glob
        out = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            src = open(path, encoding="utf-8").read()
            if re.search(r'"salary_(?:min|max)[a-z_]*"', src):
                out.append((name, src))
        return out

    def test_there_are_numeric_salary_emitters_to_check(self):
        """**A guard that checks nothing passes.** If these field names ever
        change, this fails first and says so, instead of the check below
        quietly succeeding over an empty list."""
        self.assertGreater(len(self._emitters()), 10)

    def test_every_numeric_salary_emitter_names_its_currency(self):
        missing = [name for name, src in self._emitters()
                   if not re.search(r'"[a-z_]*currency[a-z_]*"', src)]
        self.assertEqual(
            missing, [],
            "these emit a salary figure with no field naming its unit: "
            + ", ".join(missing))

    def test_adzunas_table_covers_every_index_it_serves(self):
        """Nineteen countries, one code path. **A country added without a
        currency would emit bare numbers again**, which is how this started."""
        sys.path.insert(0, SCRIPTS)
        import adzuna
        self.assertEqual(sorted(adzuna.INDEX_CURRENCY),
                         sorted(adzuna.COUNTRIES))
        self.assertTrue(all(len(v) == 3 and v.isupper()
                            for v in adzuna.INDEX_CURRENCY.values()))


class UrlWithoutAScheme(unittest.TestCase):
    """`urlparse("www.jobs.ch/x").netloc` is `""`. Found on job-room.

    **A general trap, not a job-room quirk**, which is why it is pinned here
    rather than described in a card. job-room sends `externalUrl` in two
    shapes — measured on 300 Vaud cards, 2026-09-03: **100 with a scheme, 193
    without** — and two fields read the host off it. Both went quiet rather
    than wrong:

    - `external_host` was `""` on 193 of 300, so a count of origins made on it
      reported `www.jobs.ch` **once** where the sample holds **194**. Three
      published figures came from that.
    - `duplicate_of` was `None` on all 193 — **the advertisement already swept
      under a jobs.ch id was recorded again as new.** Filled on 90 of 300
      before, 283 of 300 after.

    **The empty string did not say "I do not know", it said "no external
    host"** — the third missing third value in this repository in one day,
    after `allowed` and the three HTTP outcomes.
    """

    def setUp(self):
        sys.path.insert(0, SCRIPTS)
        import jobroom
        self.jobroom = jobroom

    def test_a_bare_host_gets_the_scheme_it_needs(self):
        self.assertEqual(
            self.jobroom.with_scheme("www.jobs.ch/de/stellenangebote/detail/x/"),
            "https://www.jobs.ch/de/stellenangebote/detail/x/")

    def test_a_url_that_has_one_is_untouched(self):
        for url in ("https://www.jobup.ch/fr/emplois/detail/x/",
                    "http://example.com/a"):
            self.assertEqual(self.jobroom.with_scheme(url), url)

    def test_a_path_is_not_a_host(self):
        """**A leading slash or a dotless first segment is a path.** Turning
        `/jobs/1` into `https:///jobs/1` would invent a host."""
        self.assertEqual(self.jobroom.with_scheme("/jobs/1"), "/jobs/1")
        self.assertEqual(self.jobroom.with_scheme("jobs/1"), "jobs/1")
        self.assertIsNone(self.jobroom.with_scheme(""))
        self.assertIsNone(self.jobroom.with_scheme(None))

    def test_the_host_is_readable_from_a_scheme_less_url(self):
        """The assertion that fails without the fix, on the exact shape the
        board sends."""
        import urllib.parse
        bare = "www.jobs.ch/de/stellenangebote/detail/fdb4a6bd/"
        self.assertEqual(urllib.parse.urlparse(bare).netloc, "",
                         "if this ever stops being empty the trap is gone")
        self.assertEqual(
            urllib.parse.urlparse(self.jobroom.with_scheme(bare)).netloc,
            "www.jobs.ch")

    def test_duplicate_of_sees_a_scheme_less_advertisement(self):
        """The consequence that costs a ledger row, not a statistic."""
        # A **whole** UUID: `UUID_RE` wants all five groups, and the first
        # draft of this case truncated it — the test failed for its own
        # fixture rather than for the defect, which is the shape of vacuous
        # negative this suite already carries a lesson about.
        bare = ("www.jobs.ch/de/stellenangebote/detail/"
                "fdb4a6bd-97c7-4ff0-97d3-0d2cb63f9153/")
        self.assertEqual(self.jobroom.duplicate_of(bare),
                         "jobs.ch:fdb4a6bd-97c7-4ff0-97d3-0d2cb63f9153")
        self.assertEqual(self.jobroom.duplicate_of(bare),
                         self.jobroom.duplicate_of("https://" + bare))

    def test_clean_url_and_the_host_agree_about_the_same_url(self):
        """**Two functions normalising the same thing differently is how this
        survived.** They share one normaliser now."""
        bare = "www.jobs.ch/de/x/?utm_source=jobroom"
        import urllib.parse
        cleaned = self.jobroom.clean_url(bare)
        self.assertEqual(cleaned, "https://www.jobs.ch/de/x/")
        self.assertEqual(urllib.parse.urlparse(cleaned).netloc,
                         urllib.parse.urlparse(
                             self.jobroom.with_scheme(bare)).netloc)


class ChildProcessesAreChecked(unittest.TestCase):
    """`subprocess.run` does not raise on a non-zero exit. Issue #123.

    **Two adapters shelled out to `hiringcafe.py`; one checked and one did
    not.** The one that did carried the reason in its own message — *an empty
    tenant list from a failed sweep would read exactly like a provider nobody
    uses* — and `recruitee.py` did not have it. On 2026-09-03, the day
    `hiringcafe.py search` began refusing by design, it printed **"0 tenants
    seen in HiringCafe's GB cards"** and exited 0: **a refusal presented as a
    measurement.**

    `capture_output=True` and then reading only `.stdout` is the whole
    defect. The child's diagnosis goes to `.stderr`, which nobody read, and an
    empty `.stdout` parses to an empty result perfectly well.

    **This is not a third point fix.** A fourth caller written next month
    would repeat it, so the check is here rather than in a card.
    """

    def _callers(self):
        import glob
        out = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))
                           + glob.glob(os.path.join(
                               os.path.dirname(SCRIPTS.rstrip("/")), "*.py"))):
            src = open(path, encoding="utf-8").read()
            if "subprocess.run(" in src:
                out.append((os.path.basename(path), src))
        return out

    def test_there_are_callers_to_check(self):
        """**A guard over an empty list passes.** If the shape ever changes
        this fails first instead of the check below succeeding vacuously."""
        self.assertGreater(len(self._callers()), 0)

    def test_every_subprocess_caller_reads_the_exit_code(self):
        missing = [name for name, src in self._callers()
                   if "returncode" not in src]
        self.assertEqual(
            missing, [],
            "these run a child process and never look at its exit code, so a "
            "child that refused or crashed yields an empty result that reads "
            "like a real absence: " + ", ".join(missing))

    def test_the_helper_passes_a_refusal_upward_unchanged(self):
        """7 and 8 mean something to a caller. **Flattening them into a
        generic failure loses the one distinction the guard draws.**"""
        sys.path.insert(0, SCRIPTS)
        import _child
        self.assertIn(7, _child.MEANINGFUL)
        self.assertIn(8, _child.MEANINGFUL)

        seen = {}

        def fake_die(msg, code=2):
            seen["msg"], seen["code"] = msg, code
            raise SystemExit(code)

        for child_code, expected in ((7, 7), (8, 8), (3, 2), (1, 2)):
            seen.clear()
            real = _child.subprocess.run
            _child.subprocess.run = lambda *a, **k: type(
                "R", (), {"returncode": child_code, "stdout": "",
                          "stderr": "the child's own words"})()
            try:
                with self.assertRaises(SystemExit):
                    _child.run(["x"], fake_die, "child.py")
            finally:
                _child.subprocess.run = real
            self.assertEqual(seen["code"], expected,
                             f"child exited {child_code}")
            self.assertIn("the child's own words", seen["msg"])


class HiringCafeIsBuiltInOnePlace(unittest.TestCase):
    """Three commands built the same refused URL, each with its own client.

    `hiringcafe.com/robots.txt` refuses `/*?searchState=*` to `User-agent: *`.
    **#123 named `hiringcafe.py:119`; `ats.py` and `workday.py` were building
    it too**, found by grepping for the URL rather than for the file — and two
    further adapters inherit it by running `hiringcafe.py search`.

    **The same shape as `jobroom.py`'s three URL parsers, fixed the same
    evening**: several places doing one thing slightly differently, one of
    them right by accident.
    """

    def test_no_adapter_assembles_the_refused_url_itself(self):
        import glob
        offenders = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
            name = os.path.basename(path)
            if name == "_hiringcafe.py":
                continue
            src = open(path, encoding="utf-8").read()
            if re.search(r'"https://hiringcafe\.com/\?"', src):
                offenders.append(name)
        self.assertEqual(
            offenders, [],
            "these build the refused `?searchState=` URL by hand instead of "
            "going through `_hiringcafe.py`: " + ", ".join(offenders))

    def test_the_refusal_names_the_rule_and_the_open_route(self):
        sys.path.insert(0, SCRIPTS)
        import _hiringcafe
        text = _hiringcafe.refusal("test")
        self.assertIn("/*?searchState=*", text)
        self.assertIn("/job/", text)
        self.assertIn("No request was made", text)


class WhatTheStatusMeans(unittest.TestCase):
    """One case per shape, because they had been sharing a verdict. #125.

    `algerie.tanqeeb.com` answers **HTTP 202 with a zero-byte body**, and the
    guard returned `allowed: True` giving the reason *"a 404 is an absence"* —
    **a status that never occurred, quoted as the justification.**

    **A 404 says there are no rules. A 202 with an empty body says nothing.**
    Melting both into `unreadable`, and reading `unreadable` as an absence,
    gave a host that did not answer the same verdict as a host that has no
    file. The three-valued output added in #118 was right; **this branch was
    not using it.**

    And the reason mattered as much as the verdict: **a silent verdict invites
    suspicion, a falsely-motivated one reads like a verification.** Every
    reason now quotes the status and the byte count actually observed.
    """

    class _Resp:
        def __init__(self, status, body, ctype="text/plain"):
            self._s, self._b, self._c = status, body, ctype

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def getcode(self):
            return self._s

        def geturl(self):
            return "https://h.example/robots.txt"

        def read(self):
            return self._b.encode()

        @property
        def headers(self):
            return {"Content-Type": self._c}

    def _fetch_with(self, response=None, error=None):
        sys.path.insert(0, SCRIPTS)
        import _robots
        real = _robots.urllib.request.urlopen

        def fake(req, timeout=None, **kw):
            # `**kw` because `_fetch_once` now passes `context=` for the two
            # hosts that need a supplied intermediate (#104). A stub with a
            # narrower signature than the real call fails for its own shape.
            if error:
                raise error
            return response
        _robots.urllib.request.urlopen = fake
        try:
            return _robots._fetch_once("https://h.example/robots.txt",
                                       "h.example", 5)
        finally:
            _robots.urllib.request.urlopen = real

    def test_404_is_an_absence_and_an_absence_permits(self):
        import urllib.error
        got = self._fetch_with(error=urllib.error.HTTPError(
            "u", 404, "Not Found", {}, None))
        self.assertEqual(got["state"], "absent")
        self.assertIn("404", got["why"])

    def test_202_with_an_empty_body_is_an_unknown(self):
        """**The case that started this.** Not an absence: nothing was said."""
        got = self._fetch_with(self._Resp(202, "", "text/html; charset=UTF-8"))
        self.assertEqual(got["state"], "unreachable")
        self.assertEqual(got["bytes"], 0)
        self.assertIn("202", got["why"])
        self.assertIn("not an absence", got["why"])

    def test_a_500_is_an_unknown(self):
        import urllib.error
        got = self._fetch_with(error=urllib.error.HTTPError(
            "u", 500, "Server Error", {}, None))
        self.assertEqual(got["state"], "unreachable")

    def test_a_403_is_a_refusal(self):
        import urllib.error
        got = self._fetch_with(error=urllib.error.HTTPError(
            "u", 403, "Forbidden", {}, None))
        self.assertEqual(got["state"], "refused")

    def test_200_with_a_rules_file_is_read(self):
        got = self._fetch_with(self._Resp(
            200, "User-agent: *\nDisallow: /x\n"))
        self.assertEqual(got["state"], "read")
        self.assertEqual(got["status"], 200)

    def test_no_reason_cites_a_status_that_did_not_happen(self):
        """The defect in one assertion: the word `404` may appear only where
        a 404 actually occurred."""
        sys.path.insert(0, SCRIPTS)
        import _robots
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda host: {
            "state": "unreachable", "final": host, "attempts": 1,
            "status": 202, "bytes": 0,
            "why": "HTTP 202 with a 0-byte body"}
        try:
            a = _robots.allowed("algerie.tanqeeb.com", "/jobs")
            self.assertIsNone(a["allowed"])
            self.assertNotIn("404", a["reason"])
            self.assertIn("202", a["reason"])
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()


class VerificationIsNeverDisabled(unittest.TestCase):
    """Issue #104. **The boundary, pinned rather than promised.**

    `empleate.gob.es` sends its leaf and no intermediate, so every verifying
    client refuses it while browsers do not notice — they cache intermediates
    and fetch the missing one from the AIA extension. **The operator therefore
    has no symptom to fix.**

    The rule: a third party's infrastructure problem is not the plugin's to
    fix. **The exception is narrow** — when the fault is masked for web users
    and an alternative exists *that keeps verification intact*, take it.
    Supplying the missing intermediate keeps it intact entirely.

    **`verify=False` is never that alternative.** It does not fix the
    connection, it removes the check from every connection the plugin makes.
    So it is a test, not a sentence in a document.
    """

    @staticmethod
    def _code_only(src, path):
        """Source with comments and string literals removed.

        **The first draft of this scan matched `_tls.py`'s own docstring**,
        which exists to forbid the thing — a checker that reads prose about a
        ban as the ban itself. `tokenize` gives the code and nothing else.
        """
        import io
        import tokenize
        if not path.endswith(".py"):
            return "\n".join(l.split("#", 1)[0] for l in src.splitlines())
        out = []
        try:
            for tok in tokenize.generate_tokens(io.StringIO(src).readline):
                if tok.type in (tokenize.COMMENT, tokenize.STRING):
                    continue
                out.append(tok.string)
        except (tokenize.TokenError, IndentationError):
            return src
        return " ".join(out)

    def _sources(self):
        import glob
        here = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(here)
        out = []
        for pattern in ("skills/**/*.py", "bin/**/*.py", "bin/*.sh"):
            for path in glob.glob(os.path.join(root, pattern), recursive=True):
                rel = os.path.relpath(path, root)
                src = open(path, encoding="utf-8").read()
                out.append((rel, self._code_only(src, path)))
        return out

    def test_there_are_sources_to_scan(self):
        self.assertGreater(len(self._sources()), 30)

    def test_nothing_turns_certificate_verification_off(self):
        banned = ("CERT_NONE", "_create_unverified_context", "--insecure")
        hits = []
        for name, src in self._sources():
            for token in banned:
                if token in src:
                    hits.append(f"{name}: {token}")
            # `verify=False` and `check_hostname=False` survive tokenising as
            # three tokens, so they are matched on the token stream.
            flat = src.replace(" ", "")
            for token in ("verify=False", "check_hostname=False"):
                if token in flat:
                    hits.append(f"{name}: {token}")
        self.assertEqual(hits, [], "verification is disabled here: "
                                   + "; ".join(hits))


class EmbeddedIntermediate(unittest.TestCase):
    """It is narrow, it is read from itself, and it names its own expiry."""

    def setUp(self):
        sys.path.insert(0, SCRIPTS)
        import _tls
        self._tls = _tls

    def test_it_applies_to_two_hosts_and_no_others(self):
        """**A set, not a suffix match.** `notempleate.gob.es` must not pick
        this up, and neither must anything else."""
        self.assertIsNotNone(self._tls.context_for("empleate.gob.es"))
        self.assertIsNotNone(self._tls.context_for("www.empleate.gob.es"))
        for other in ("example.com", "notempleate.gob.es",
                      "empleate.gob.es.evil.test", "gob.es"):
            self.assertIsNone(self._tls.context_for(other), other)

    def test_the_expiry_is_read_from_the_certificate(self):
        """**Not from a constant beside it.** A second source of truth is how
        a field drifts away from what it describes."""
        end = self._tls.expires()
        self.assertGreater(end.year, 2024)
        self.assertEqual(self._tls.check()["expires"], f"{end:%Y-%m-%d}")

    def test_expiry_fails_by_name_and_never_suggests_disabling(self):
        """The day it lapses, the failure must say so — not come back as an
        opaque `CERTIFICATE_VERIFY_FAILED` and make somebody repeat the whole
        investigation. `never-fail-silently.md`."""
        import datetime
        later = self._tls.expires() + datetime.timedelta(days=1)
        with self.assertRaises(self._tls.Expired) as caught:
            self._tls.context_for("empleate.gob.es", now=later)
        text = str(caught.exception)
        self.assertIn("expired on", text)
        self.assertIn(self._tls.AIA_URL, text)
        self.assertIn("Do not disable", text)

    def test_it_is_still_valid_today(self):
        """A reminder with a date on it, rather than a surprise."""
        import datetime
        left = (self._tls.expires()
                - datetime.datetime.now(datetime.timezone.utc)).days
        self.assertGreater(left, 0, "the embedded intermediate has expired — "
                                    "see `_tls.check()` for what to do")


class AnInvocationThatCannotSucceed(unittest.TestCase):
    """`jobup.py search` accepted a call that could only return zero. #126.

    **Measured 2026-09-03**, and the numbers are the whole argument:

        /fr/emplois/                    275 kB    0 JobPosting
        /fr/emplois/?term=developpeur   534 kB   22 JobPosting
        /fr/emplois/?location=Lausanne  517 kB   22 JobPosting

    The bare listing renders client-side and carries no structured data. **A
    filterless run therefore returned zero, reliably** — and a zero from a
    board reads as a board with no jobs. It was reported as one, and an Atlas
    page was published saying the board had broken.

    Two further faults in the same command made it worse: **`--location` never
    entered the URL** (it was applied afterwards, to rows fetched from the
    *unfiltered* listing), and `drop_report` returns three values where the
    call site unpacked two — so `--location` alone raised `ValueError` after
    paying for the sweep.

    **A tool that accepts an invocation which cannot succeed manufactures
    false results.**
    """

    def setUp(self):
        sys.path.insert(0, SCRIPTS)
        import jobup
        self.jobup = jobup

    def _args(self, **kw):
        import argparse
        base = dict(site="jobup", term=None, location=None, pages=1,
                    limit=None, delay=0.0)
        base.update(kw)
        return argparse.Namespace(**base)

    def test_a_filterless_search_is_refused_before_any_request(self):
        with self.assertRaises(SystemExit) as caught:
            self.jobup.cmd_search(self._args())
        self.assertEqual(caught.exception.code, 2)

    def test_drop_report_returns_three_values(self):
        """The contract the call site got wrong. `(kept, dropped, labels)`."""
        import _locations
        got = _locations.drop_report(
            [{"location_text": "Lausanne"}, {"location_text": "Bern"}],
            "Lausanne")
        self.assertEqual(len(got), 3)
        kept, dropped, labels = got
        self.assertEqual(len(kept), 1)
        self.assertEqual(dropped, 1)
        self.assertEqual(labels, {"Bern": 1})

    def test_location_reaches_the_query_string(self):
        """It was filtered after the fetch, so the fetch was unfiltered."""
        src = open(os.path.join(SCRIPTS, "jobup.py"), encoding="utf-8").read()
        self.assertIn('q["location"] = a.location', src)

    def test_the_empty_message_names_three_causes(self):
        """Naming two of three is not a false statement, and it had the same
        effect as one: it pointed at *the board is broken*."""
        src = open(os.path.join(SCRIPTS, "jobup.py"), encoding="utf-8").read()
        i = src.index("carried no JobPosting")
        window = src[i:i + 1200]
        self.assertIn("(1)", window)
        self.assertIn("(2)", window)
        self.assertIn("(3)", window)
        # **The substance, not the tense — and not the line wrapping.**
        # This asserted the exact phrase "does not answer with structured
        # data"; it broke on "did not", which is the more accurate claim,
        # and then broke again because the phrase spans an f-string
        # continuation in the source. **A case that reads source text is
        # matching the author's line breaks, not the program's behaviour**,
        # so the continuations are stitched before matching.
        flat = re.sub(r'"\s*\n\s*f?"', "", window)
        self.assertIn("answer with structured data", flat)
        self.assertIn("measured both ways within a day", flat)


class OneDeclaredIdentity(unittest.TestCase):
    """One user-agent, in one module, imported by all of them. #120, #124.

    The repository **obeyed `Claude-User`'s rules and announced Chrome** — 63
    files carried a browser string while `_robots.OUR_AGENTS` already bound
    the guard to `claude-user`, and `job-room.md` argued its position in the
    language of that very class. Three files declared themselves honestly and
    sixty-three did not; the split is how a project comes to plead one thing
    and send another.
    """

    def setUp(self):
        sys.path.insert(0, SCRIPTS)
        import _ua
        self._ua = _ua

    def test_the_declaration_carries_the_token_and_says_what_it_is(self):
        """**Both readings must be true.** An operator matching the token in a
        robots group gets the intended behaviour; an operator reading the
        string sees a personal tool, not Anthropic's fleet — which matters,
        because `claude.com/crawling/bots.json` publishes IP prefixes for
        verification and this runs from the user's own address."""
        ua = self._ua.UA
        self.assertIn("Claude-User", ua)
        self.assertIn("claude-job-hunt", ua)
        self.assertIn("github.com/dominiquevienne/claude-job-hunt", ua)

    def test_no_adapter_declares_its_own_agent(self):
        import glob
        offenders = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))
                           + glob.glob(os.path.join(
                               os.path.dirname(SCRIPTS.rstrip("/")),
                               "..", "..", "bin", "*.py"))):
            name = os.path.basename(path)
            if name in ("_ua.py", "adzuna.py"):
                continue          # adzuna is keyed API access, not a crawl
            src = open(path, encoding="utf-8").read()
            if "Mozilla/5.0 (Macintosh" in src:
                offenders.append(name)
        self.assertEqual(offenders, [],
                         "these still announce a browser: "
                         + ", ".join(offenders))

    def test_the_browser_is_never_the_answer_to_a_refusal(self):
        """**The whole worth of declaring rests on this.** Declaring the token
        and then reaching for a browser at every refusal is worse than not
        declaring: it hands operators a way to recognise us and makes it
        ineffective. #124."""
        msg, code = self._ua.browser_fallback("h.example", True, 403)
        self.assertEqual(code, self._ua.EXIT_NEEDS_BROWSER)
        self.assertIn("permit", msg)
        for refused_or_unknown in (False, None):
            with self.assertRaises(ValueError):
                self._ua.browser_fallback("h.example", refused_or_unknown, 403)

    def test_a_block_says_the_declaration_might_be_why(self):
        """Measured the day it shipped: `emploi.batiactu.com` serves 289 bytes
        of `robots.txt` to a browser string and 403s ours. **A declaration can
        manufacture a refusal**, and a run that quietly returned less would
        hide it."""
        note = self._ua.blocked_note("emploi.batiactu.com", 403)
        self.assertIn("Claude-User", note)
        self.assertIn("cannot tell them apart", note)


class EveryNetworkReaderAsksOrSaysWhyNot(unittest.TestCase):
    """#100's last hole, and the answer written down rather than deduced.

    **An absent guard call is indistinguishable from a decision not to call**,
    which is exactly what went wrong with SmartRecruiters in `ats.py`: the
    exception existed nowhere, it was a silence. So the scripts that do not
    ask are listed here **with the reason**, and a script that stops asking
    without being added fails this case.

    **#100 counted ten by grepping for `robots`. That measure passes prose.**
    `arbeitsagentur.py` and `hiringcafe.py` mention the word in a docstring —
    one of them carrying *a human's one-time reading of the file*, which is
    the very practice `_robots.py` was written to replace — and neither calls
    the guard. Six network readers do not ask, not four.
    """

    # Each entry is a decision, not an oversight, and the text is the reason.
    NOT_ASKING = {
        "adzuna.py": "documented public API — and api.adzuna.com publishes "
                     "`Disallow: /`. HELD: arbitration with the user",
        "francetravail.py": "documented public API — api.francetravail.io "
                            "publishes `Disallow: /`. HELD: same arbitration",
        "labonnealternance.py": "documented public API — and "
                                "api.apprentissage.beta.gouv.fr serves 145 kB "
                                "of its own SPA as robots.txt, so the guard "
                                "reads `unrecognised`. HELD: same class",

        "arbeitsagentur.py": "documented public API — and "
                             "rest.arbeitsagentur.de answers its robots.txt "
                             "with a 1-byte 403. The docstring's human "
                             "reading was of www.arbeitsagentur.de, a "
                             "different host. HELD: same class",
        "hiringcafe.py": "refuses from the record by design (#123): a guard "
                         "call is itself a request, and collection from this "
                         "host is suspended",
    }

    def _network_readers(self):
        import glob
        out = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            src = open(path, encoding="utf-8").read()
            if any(t in src for t in ("urllib.request", "urlopen",
                                      "http.client")):
                out.append((name, src))
        return out

    def test_there_are_network_readers_to_check(self):
        self.assertGreater(len(self._network_readers()), 50)

    @staticmethod
    def _calls_the_guard(src):
        """**Imported is not called.** #100 worried that adapters might carry
        the import and never use it — *the appearance of control*. Measured
        2026-09-03: none did, 63 of 63. But a substring test could not have
        told the difference, so this reads the syntax tree: a name bound from
        `_robots` must appear as the function of an actual call."""
        import ast
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return False
        bound = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and (n.module or "") == "_robots":
                bound.update(a.asname or a.name for a in n.names)
            if isinstance(n, ast.Import):
                bound.update(a.asname or a.name for a in n.names
                             if a.name == "_robots")
        if not bound:
            return False
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            if isinstance(f, ast.Name) and f.id in bound:
                return True
            if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                    and f.value.id in bound):
                return True
        return False

    def test_every_network_reader_asks_the_guard_or_is_listed_with_a_reason(self):
        silent = [name for name, src in self._network_readers()
                  if not self._calls_the_guard(src)
                  and name not in self.NOT_ASKING]
        self.assertEqual(
            silent, [],
            "these touch the network, never call the guard, and give no "
            "reason — an absent call reads the same as a decision not to "
            "call: " + ", ".join(silent))

    def test_the_count_is_what_it_is_said_to_be(self):
        """**The denominator #100 was written on was wrong**, so the real one
        is pinned here. 74 scripts, 69 touching the network, 63 calling the
        guard, 6 listed with a reason. *45* was never the number that did not
        call — it is the number that call `allowed()`, the **per-path** check,
        which is stronger than the per-host one the issue counted."""
        readers = self._network_readers()
        calling = [n for n, src in readers if self._calls_the_guard(src)]
        self.assertEqual(len(readers) - len(calling), len(self.NOT_ASKING))
        self.assertGreater(len(calling), 55)

    def test_the_list_carries_no_script_that_now_asks(self):
        """**A reason that has stopped applying is worse than none.** If one
        of these starts calling the guard, the entry must go, or the file
        will explain an exception that no longer exists."""
        asking = {name for name, src in self._network_readers()
                  if "_robots" in src}
        stale = sorted(asking & set(self.NOT_ASKING))
        self.assertEqual(stale, [], "these now ask the guard and should be "
                                    "removed from NOT_ASKING: "
                                    + ", ".join(stale))

    def test_the_tooling_scripts_really_do_not_touch_the_network(self):
        """Verified rather than assumed — **and the assumption was wrong
        once.** `tenant_offer.py` was grouped with the ledger tools and sends
        HEAD requests through up to eight redirects; it asks the guard now."""
        import glob
        names = {os.path.basename(p) for p, _ in
                 [(x, None) for x in glob.glob(os.path.join(SCRIPTS, "*.py"))]}
        for tool in ("achievements.py", "board_offer.py", "dormant.py",
                     "employers.py", "ledger.py"):
            self.assertIn(tool, names)
            src = open(os.path.join(SCRIPTS, tool), encoding="utf-8").read()
            for token in ("urllib.request", "urlopen", "http.client",
                          "socket."):
                self.assertNotIn(token, src, f"{tool} touches the network")


class SmartRecruitersIsAnOverrideNotASilence(unittest.TestCase):
    """#121, decided by the repository's owner: treat it as AMS.

    **`api.smartrecruiters.com` publishes 72 bytes** — `LinkedInBot` allowed on
    `/v1/companies/`, `*` closed entirely — which is the AMS shape exactly.
    Before this, `ats.py` gated teamtailor at line 418 and **did not ask about
    this host at all**, so the adapter read a host that refuses it and **the
    exception existed nowhere**: not as a decision, not as a note, not as a
    silence anybody could see. That was the defect, more than the reading.

    The first ground offered was wrong and is retracted in
    `shared/boards/smartrecruiters.md`: the `llms.txt` cited sits on other
    hosts, one copy is generated by an SEO plugin, and it indexes marketing
    and documentation pages. **The most specific declaration for the API host
    is its own file.**
    """

    def test_the_key_is_required_and_absent_means_skipped(self):
        src = open(os.path.join(SCRIPTS, "ats.py"), encoding="utf-8").read()
        self.assertIn("override_robots", src)
        self.assertIn("skipped, not silently obeyed", src)

    def test_the_gate_sits_where_every_request_passes(self):
        """**Gating `list` alone left `ad` and the description fetch open** —
        three call sites, which is how `hiringcafe.com` came to be built in
        three places. A new call site cannot miss a check inside `fetch`."""
        src = open(os.path.join(SCRIPTS, "ats.py"), encoding="utf-8").read()
        i = src.index("def fetch(url):")
        self.assertIn("smartrecruiters_gate()", src[i:i + 500])

    def test_the_gate_actually_runs_and_not_merely_appears(self):
        """**The case above reads a position and calls it a guarantee.**

        `None and smartrecruiters_gate()` leaves the call text exactly where
        that check looks, never runs it, and the whole suite stayed green —
        while `fetch` would then reach `api.smartrecruiters.com`, which
        publishes `User-agent: * / Disallow: /`. **A gate that is present and
        inert is worse than one that is absent**, because the check that
        should find it reports success.

        So this one calls `fetch` and asserts the gate *fired*, rather than
        asserting where it is written. No request is made: the gate refuses
        first, which is the whole point.
        """
        import ats
        calls = []
        real_gate = ats.smartrecruiters_gate
        real_open = ats.urllib.request.urlopen
        ats.smartrecruiters_gate = lambda *a, **k: calls.append(1)

        def offline(*a, **k):
            # the gate has already decided by the time this could run; the
            # request itself is not what this case is about.
            raise ats.urllib.error.URLError("offline for this case")

        ats.urllib.request.urlopen = offline
        try:
            ats.fetch("https://api.smartrecruiters.com/v1/companies/x")
        except BaseException:      # SystemExit included — fetch dies loudly
            pass
        finally:
            ats.smartrecruiters_gate = real_gate
            ats.urllib.request.urlopen = real_open
        self.assertEqual(len(calls), 1,
                         "fetch() did not call the gate — it may still be "
                         "written in the file and never reached")

    def test_the_run_says_it_out_loud_once(self):
        src = open(os.path.join(SCRIPTS, "ats.py"), encoding="utf-8").read()
        self.assertIn("override ACTIVE", src)
        self.assertIn("_SR_ANNOUNCED", src)

    def test_no_document_still_calls_it_the_only_override(self):
        """**A sentence that says "the only one" while a second exists tells
        the user something false about the plugin.** There are two."""
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for rel in ("shared/robots-policy.md", "shared/setup.md"):
            text = open(os.path.join(root, rel), encoding="utf-8").read()
            for stale in ("the only override in the plugin",
                          "this is the only one",
                          "That this is the only one"):
                self.assertNotIn(stale, text, f"{rel} still says {stale!r}")

    def test_the_permitting_providers_are_not_swept_into_it(self):
        """It does not generalise: Greenhouse, Workable and Lever permit."""
        src = open(os.path.join(SCRIPTS, "ats.py"), encoding="utf-8").read()
        i = src.index("def smartrecruiters_gate")
        self.assertIn("does not generalise", src[i:i + 3000])


class LdJsonMalformations(unittest.TestCase):
    r"""One case per specimen, each named with the site it came from. #127.

    **Two occurrences on two continents suggest a class, not an accident**: a
    publisher that escapes one layer too many. Michael Page and Chile's
    service put a **literal newline** inside a string, which is why
    `strict=False` is passed at all; `jobivoire.ci` puts an **HTML entity
    behind a backslash** — `d\&#039;Atelier`, an apostrophe HTML-escaped after
    being JSON-escaped. `\&` is not an escape sequence and `strict=False` does
    not forgive it.

    **The repair does not silence the guard.** `absent_reason()` caught this
    on two independent sessions the same evening and reported it
    `our_fault=True`; a fix that recovered the twelve advertisements by
    turning that warning off would be a regression, not a repair.
    """

    NEWLINE = ('<script type="application/ld+json">'
               '{"@type":"JobPosting","description":"a\nb"}</script>')
    BAD_ESCAPE = ('<script type="application/ld+json">'
                  '{"@type":"JobPosting","title":"d\\&#039;Atelier"}</script>')
    NESTED = ('<script type="application/ld+json">'
              '{"@type":"CollectionPage","mainEntity":{"@type":"ItemList",'
              '"itemListElement":[{"@type":"ListItem","position":1,'
              '"item":{"@type":"JobPosting","title":"one"}},'
              '{"@type":"ListItem","position":2,'
              '"item":{"@type":"JobPosting","title":"two"}}]}}</script>')
    BEYOND_REPAIR = ('<script type="application/ld+json">'
                     '{"@type":"JobPosting", "title": }</script>')

    def test_a_literal_newline_still_parses(self):
        """Michael Page and `bne.gob.cl`. The reason `strict=False` is there."""
        self.assertEqual(len(_ldjson.postings(self.NEWLINE)), 1)

    def test_a_backslash_before_an_html_entity_is_repaired(self):
        """`jobivoire.ci`. `strict=False` does not cover this one."""
        import json
        blk = _ldjson.blocks(self.BAD_ESCAPE)[0]
        with self.assertRaises(ValueError):
            json.loads(blk, strict=False)
        got = _ldjson.postings(self.BAD_ESCAPE)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["title"], "d\\&#039;Atelier")

    def test_the_repair_is_counted_and_can_be_reported(self):
        """**A page whose structured data needs mending is a page to watch**,
        and the number belongs in a run's output, not in this module's
        silence."""
        self.assertEqual(_ldjson.repairs(self.BAD_ESCAPE), 1)
        self.assertEqual(_ldjson.repairs(self.NEWLINE), 0)

    def test_mainentity_nests_an_itemlist(self):
        """`jobivoire.ci` again: a `CollectionPage` whose `mainEntity` is an
        `ItemList` of twelve. A reader unwrapping `itemListElement` only at
        the top level saw **one** object on a page holding twelve."""
        got = _ldjson.postings(self.NESTED)
        self.assertEqual([p["title"] for p in got], ["one", "two"])

    def test_what_the_repair_cannot_fix_is_still_reported(self):
        """**The guard is not turned off by the fix.**"""
        self.assertEqual(_ldjson.postings(self.BEYOND_REPAIR), [])
        why = _ldjson.absent_reason(self.BEYOND_REPAIR)
        self.assertEqual(why.kind, "unparseable")
        self.assertTrue(why.our_fault)

    def test_the_diagnosis_parses_the_same_way_the_reader_does(self):
        """A diagnosis that parsed differently would report a page unreadable
        while the reader was reading it."""
        why = _ldjson.absent_reason(self.BAD_ESCAPE)
        self.assertNotEqual(why.kind, "unparseable")

    def test_the_repair_leaves_valid_json_untouched(self):
        """**It must not be a general attempt to fix JSON.** A valid escape
        is not a malformation."""
        good = ('<script type="application/ld+json">'
                '{"@type":"JobPosting","title":"a \\"quoted\\" word",'
                '"description":"line\\nbreak"}</script>')
        got = _ldjson.postings(good)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["title"], 'a "quoted" word')
        self.assertIn("\n", got[0]["description"])


class ABodyNobodyRecognisedIsNotAnAbsence(unittest.TestCase):
    """#128, the seventh defect in this guard and the seventh towards
    *allowed* — but the first that **asserts** rather than merely permits.

    `maliemploi.org` served an Apache *"Access forbidden! / Error 403"* page
    as its `robots.txt`, and the guard answered:

        allowed: True   group: *   sweep: True   certain: True

    **A `*` group invented out of an error page, and then certified.**

    **The issue read it as the verdict depending on body size** — 976 bytes
    accepted, a 5 132-byte React shell rejected. **It is not the size.** The
    short one was labelled `text/plain` and **its body was never examined**;
    the long one was labelled `text/html` and was. Same defect, one branch
    earlier: the header decided, and the body never got a look.

    `certain` exists to say *this is an established absence of rules*. **A
    guard that errs by doubting is repairable; a guard that errs by asserting
    gets itself believed.**
    """

    class _Resp:
        def __init__(self, body, ctype):
            self._b, self._c = body, ctype

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def getcode(self):
            return 200

        def geturl(self):
            return "https://h.example/robots.txt"

        def read(self):
            return self._b.encode()

        @property
        def headers(self):
            return {"Content-Type": self._c}

    def _verdict(self, body, ctype):
        sys.path.insert(0, SCRIPTS)
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = (
            lambda r, timeout=None, **k: self._Resp(body, ctype))
        try:
            return _robots.verdict("h.example"), _robots.allowed(
                "h.example", "/jobs")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    APACHE = ('<!DOCTYPE HTML><html><head><title>403 Forbidden</title></head>'
              '<body><h1>Access forbidden!</h1><p>Error 403</p></body></html>')
    SPA = ('<!doctype html><html><body>You need to enable JavaScript to run '
           'this app.</body></html>')

    def test_a_short_error_page_labelled_text_plain_is_not_rules(self):
        """**The specimen.** Labelled `text/plain`, so the old code never
        looked at it.

        **What #128 fixed is still fixed**, and that is what this asserts: the
        page is not parsed into an empty `*` group, and it is not certified.
        The conduct applied to that absence changed on 2026-09-04 — see
        `AnEmptyBodyIsAnOpenDoor` — but the epistemics did not, and the two
        were merged once already.
        """
        v, a = self._verdict(self.APACHE, "text/plain")
        self.assertEqual(v["state"], "unrecognised")
        self.assertFalse(v["certain"])
        self.assertFalse(a["certain"])
        self.assertIsNone(v.get("group"),
                          "a group was invented out of an error page — this "
                          "is #128 itself, and no policy change licenses it")

    def test_a_long_spa_shell_is_not_rules_either(self):
        """Same verdict for the case that was already caught — **the two must
        not depend on which header they carried.**"""
        v, a = self._verdict(self.SPA, "text/html")
        self.assertEqual(v["state"], "unrecognised")
        self.assertFalse(a["certain"])

    def test_an_empty_body_establishes_nothing(self):
        """A zero-byte body carries no directive either. RFC 9309 would read
        it as *no rules*; **we cannot tell it from a broken response**, so the
        state stays `unrecognised` and `certain` stays false — even though the
        door now opens on it."""
        v, _a = self._verdict("", "text/plain")
        self.assertEqual(v["state"], "unrecognised")
        self.assertFalse(v["certain"])

    def test_a_real_rules_file_still_permits_and_is_certain(self):
        """**The other half.** A file with no `Disallow` is a real absence of
        restriction, and `certain` is exactly what it is for."""
        v, a = self._verdict("User-agent: *\nAllow: /\n", "text/plain")
        self.assertEqual(v["state"], "read")
        self.assertIs(a["allowed"], True)
        self.assertTrue(v["certain"])

    def test_certain_is_never_true_on_a_body_we_did_not_recognise(self):
        """The requirement that separates this from #125, as one assertion."""
        for body, ctype in ((self.APACHE, "text/plain"),
                            (self.SPA, "text/html"), ("", "text/plain")):
            v, _a = self._verdict(body, ctype)
            self.assertFalse(v["certain"], f"{ctype}: {body[:30]!r}")

    def test_the_reason_quotes_what_was_seen_not_an_invented_group(self):
        v, a = self._verdict(self.APACHE, "text/plain")
        self.assertIn("not a rules file", v["reason"])
        self.assertIn("200", v["reason"])
        self.assertNotIn("the group that applies to everyone",
                         a["reason"] or "")


class RulesNothingHadEverTested(unittest.TestCase):
    """Four rules `_robots.py` implements and the suite never checked. #119.

    **Found by mutation, not by reading.** Each of this guard's seven defects
    was put back one at a time and the suite asked; six were caught. Then the
    same battery was run against rules that had never failed in production —
    and four of them nothing noticed.

    **Three of the four err towards `allowed` when broken**, which is the
    direction all seven real defects took. A suite that tests only the
    defects that have already happened describes a history; these pin the
    rules.

    **Two of the eight mutations proved nothing and were discarded**: one
    changed only which token name is quoted, one added an unused constant.
    **A mutation that does not change behaviour is not evidence about the
    tests**, and the first was very nearly reported as a hole.
    """

    def _with_body(self, body, host="h.example"):
        sys.path.insert(0, SCRIPTS)
        import _robots
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda h: {"state": "read", "body": body,
                                    "final": h, "attempts": 1}
        try:
            return _robots.verdict(host), _robots.allowed(host, "/a/b/c/d")
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_a_tie_between_allow_and_disallow_goes_to_allow(self):
        """RFC 9309: *if an allow and a disallow are equivalent, the allow
        SHOULD be used.* **Nothing paired them on one path**, so `>=` could
        have been `>` for ever."""
        sys.path.insert(0, SCRIPTS)
        import _robots
        self.assertEqual(_robots._match_len("/a/b", "/a/b/c/d"),
                         _robots._match_len("/a/b", "/a/b/c/d"))
        _v, a = self._with_body(
            "User-agent: *\nDisallow: /a/b\nAllow: /a/b\n")
        self.assertIs(a["allowed"], True)
        self.assertEqual(a["kind"], "allow")

    def test_the_longest_match_decides_not_the_first(self):
        """**Breaking this permits a path the file refuses.** With
        `Disallow: /a`, `Disallow: /a/b/c` and `Allow: /a/b`, a first-match
        reader compares `/a` (2) against `/a/b` (4) and **allows**; the
        longest match is `/a/b/c` (6) and refuses."""
        _v, a = self._with_body(
            "User-agent: *\nDisallow: /a\nDisallow: /a/b/c\nAllow: /a/b\n")
        self.assertIs(a["allowed"], False)
        self.assertEqual(a["rule"], "/a/b/c")

    def test_content_signal_ai_input_no_is_a_refusal(self):
        """**The most consent-critical rule in the module, and `ai-input`
        appeared nowhere in the suite.** Disabling the check flips `sweep`
        from False to True and nothing failed. Issue #98."""
        v, _a = self._with_body(
            "User-agent: *\nContent-Signal: search=yes,ai-input=no\n"
            "Allow: /\n")
        self.assertIs(v["sweep"], False)
        self.assertIn("ai-input", v["reason"])

    def test_every_content_signal_is_read_not_only_the_first(self):
        """A refusal in the second line is still a refusal — the CDN's copy
        and the origin's can disagree, and no convention says which wins."""
        v, _a = self._with_body(
            "User-agent: *\nContent-Signal: search=yes\n"
            "Content-Signal: ai-input=no\nAllow: /\n")
        self.assertIs(v["sweep"], False)
        self.assertTrue(v["content_signal_conflict"])

    def test_the_verdict_is_cached_on_the_host_that_answered(self):
        """#99: `ss.ge` redirects to `jobs.ss.ge`, which publishes a different
        file. **Caching on the name that was typed would hand one host's
        rules to another**, and nothing asserted `requested_host`."""
        sys.path.insert(0, SCRIPTS)
        import _robots
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda h: {
            "state": "read", "body": "User-agent: *\nDisallow: /x\n",
            "final": "answered.example", "attempts": 1}
        try:
            v = _robots.verdict("asked.example")
            self.assertEqual(v["host"], "answered.example")
            self.assertEqual(v["requested_host"], "asked.example")
            self.assertIn("answered.example", _robots._CACHE)
            self.assertNotIn("asked.example", _robots._CACHE)
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()


class TheLossyFallbackSpeaks(unittest.TestCase):
    """`errors="replace"` is the probe that cannot go red. #115.

    A half-replaced title reads as ordinary text to the program and to this
    suite. `_decode` was written to report **which** encoding it used so a
    caller could tell — and measured 2026-09-03, **60 of 61 call sites
    discard it with `[0]`**, and nothing anywhere tests for
    `"utf-8/replace"`.

    **A signal that exists and is never read** is the shape this repository
    met four times in one day: `absent_reason()` parsing differently from the
    reader, an empty `external_host` asserting *no host*, `certain` on a body
    nobody recognised. So the module speaks now, rather than returning a
    value nobody looks at.

    **And it speaks only on a real loss.** Measured across five live boards —
    4 663 rows, 18 089 accented characters — **zero replacements**. On these
    boards the guard is a precaution, and that was measured before the
    severity was chosen.
    """

    def test_it_warns_when_characters_are_actually_replaced(self):
        import io
        import contextlib
        _decode._WARNED.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            text, enc = _decode.decode_body(b"ok \x81\x8d text")
        self.assertEqual(enc, "utf-8/replace")
        self.assertEqual(text.count("\ufffd"), 2)
        self.assertIn("could not be decoded", err.getvalue())
        self.assertIn("U+FFFD", err.getvalue())

    def test_it_says_nothing_when_nothing_was_lost(self):
        """**A warning that fires on clean input is noise**, and noise is how
        a real one gets missed."""
        import io
        import contextlib
        _decode._WARNED.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            _decode.decode_body("café €".encode("utf-8"))
            _decode.decode_body("caf\xe9".encode("cp1252"))
        self.assertEqual(err.getvalue(), "")

    def test_it_speaks_once_per_process(self):
        """A sweep of four thousand advertisements on a broken host would
        otherwise print four thousand lines, **and a warning that scrolls is
        a warning nobody reads.**"""
        import io
        import contextlib
        _decode._WARNED.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            for _ in range(5):
                _decode.decode_body(b"ok \x81\x8d text")
        self.assertEqual(err.getvalue().count("[decode]"), 1)

    def test_no_adapter_still_decodes_utf8_by_hand(self):
        """The first migration matched `decode("utf-8", …)` and **missed
        `decode("utf8", …)` without the hyphen** — eight adapters. The
        pattern defined its own result."""
        import glob
        offenders = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
            name = os.path.basename(path)
            if name in ("_decode.py", "_robots.py", "hiringcafe.py"):
                continue          # deliberate, and each says why
            src = open(path, encoding="utf-8").read()
            if re.search(r'\.decode\(\s*["\']utf-?8["\']\s*,', src):
                offenders.append(name)
        self.assertEqual(offenders, [],
                         "these decode a body without reading the "
                         "declaration: " + ", ".join(offenders))


class NoSignalIsOrphaned(unittest.TestCase):
    """#129: a signal that exists and nobody reads. **The scan overcounted.**

    A first pass reported **11 of 16 keys in the guard's result read by
    nobody** — and it was wrong, because it looked only at adapter files. A
    signal reaches its reader by **three** routes, not one:

    - the field, read by a caller (`allowed`, `sweep`, `reason`, `kind`);
    - the field, read by the module's own CLI (`sweep_disagrees`, `differ`)
      or by this suite (`certain`, `group`, `groups`, `rule`, `disallow`);
    - **the sentence** — `content_signal`'s value is quoted verbatim in the
      `reason` that every `die()` prints, and so are the status and the byte
      count.

    **A scan that counts only the first route reports the other two as
    absences** — the same shape as `45 of 61`, where the complement of a
    stronger check was read as a gap. It is the eighth time in two days that
    a probe defined its own population, **and the first where the wrong
    answer was the alarming one**, which is why it nearly shipped.

    The one real orphan was `decode_body`'s second value — 60 of 61 callers
    discarding it with `[0]` — and that module speaks now.
    """

    def _verdict(self, body):
        sys.path.insert(0, SCRIPTS)
        import _robots
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda h: {"state": "read", "body": body,
                                    "final": h, "attempts": 1}
        try:
            return _robots.verdict("h.example")
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_the_reason_carries_what_the_orphan_keys_hold(self):
        """**The sentence is the route that reaches a caller.** No adapter
        reads `content_signal`; every one of them prints `reason`."""
        v = self._verdict("User-agent: *\n"
                          "Content-Signal: search=yes,ai-input=no\nAllow: /\n")
        self.assertEqual(v["content_signal"], ["search=yes,ai-input=no"])
        self.assertIn("ai-input=no", v["reason"])

    def test_the_status_and_size_reach_the_caller_through_the_reason(self):
        """#125's requirement, restated as a route: an adapter that prints
        only `reason` still learns what was observed."""
        sys.path.insert(0, SCRIPTS)
        import _robots
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda h: {
            "state": "unrecognised", "final": h, "attempts": 1,
            "status": 200, "bytes": 976,
            "why": "HTTP 200, Content-Type 'text/plain', 976 bytes, and no "
                   "`User-agent` line anywhere in it"}
        try:
            v = _robots.verdict("h.example")
            self.assertIn("200", v["reason"])
            self.assertIn("976", v["reason"])
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_decode_body_is_the_one_signal_that_had_no_route(self):
        """It reported its method in a return value that 60 of 61 callers
        threw away, and no route replaced it. **So the source speaks.**"""
        import io
        import contextlib
        _decode._WARNED.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            _decode.decode_body(b"ok \x81\x8d text")
        self.assertIn("[decode]", err.getvalue())


class LineEndingsAreDeclared(unittest.TestCase):
    """#107: `bin/doctor.sh` is the first thing `README.md` asks a user to run.

    **Git for Windows sets `core.autocrlf=true` by default**, converting line
    endings on the way *out* of the repository. A shell script checked out
    that way fails under Git Bash with

        /usr/bin/env: 'bash\r': No such file or directory

    — which names an interpreter that exists, with an invisible character on
    the end. **The first gesture the project asks for is the one that
    breaks**, and it looks like the user's fault.

    **No Windows machine was available to reproduce it**, and this suite does
    not pretend otherwise. What it checks is what is checkable anywhere: that
    the rule is declared, that Git agrees it applies, and that nothing in the
    index already carries a carriage return.
    """

    def _root(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_the_rule_exists(self):
        self.assertTrue(os.path.exists(os.path.join(self._root(),
                                                    ".gitattributes")))

    def test_git_applies_lf_to_the_script_the_readme_names_first(self):
        """**Declared is not applied.** `git check-attr` is the one that
        answers, and it answers on this machine as it would on any other —
        the attribute is in the repository, not in the checkout."""
        import subprocess
        r = subprocess.run(["git", "check-attr", "eol", "--", "bin/doctor.sh"],
                           capture_output=True, text=True, cwd=self._root())
        self.assertIn("eol: lf", r.stdout)

    def test_every_shell_script_is_covered(self):
        import glob
        import subprocess
        root = self._root()
        scripts = [os.path.relpath(p, root)
                   for p in glob.glob(os.path.join(root, "bin", "*.sh"))]
        self.assertGreater(len(scripts), 0)
        for rel in scripts:
            r = subprocess.run(["git", "check-attr", "eol", "--", rel],
                               capture_output=True, text=True, cwd=root)
            self.assertIn("eol: lf", r.stdout, rel)

    def test_nothing_in_the_index_already_carries_a_carriage_return(self):
        """The declaration fixes the boundary; it does not rewrite history.
        **If a CRLF file were already committed, the rule would not undo it**
        — somebody would need `git add --renormalize .` `git ls-files --eol`
        reports the index (`i/`) and working-tree (`w/`) endings of every
        tracked file in one pass; anything but `i/lf` on a text file is a
        carriage return already in the repository."""
        import subprocess
        root = self._root()
        out = subprocess.run(["git", "ls-files", "--eol"], capture_output=True,
                             text=True, cwd=root).stdout.splitlines()
        self.assertGreater(len(out), 50)
        bad = []
        for line in out:
            fields = line.split("\t", 1)
            if len(fields) != 2:
                continue
            index_eol = fields[0].split()[0]
            # i/-text marks a binary blob, which has no line endings to get
            # wrong; i/mixed and i/crlf are the two that break Git Bash.
            if index_eol not in ("i/lf", "i/-text", "i/none"):
                bad.append(f"{fields[1].strip()} ({index_eol})")
        self.assertEqual(bad, [], "stored with a carriage return: "
                                  + ", ".join(bad[:5]))


class SourceCompilesWithoutWarning(unittest.TestCase):
    """`\\&` sat in a docstring in this file until #107's work compiled the
    tree and Python said so.

    **An invalid escape sequence is not a style complaint.** `"\\&"` is
    currently `"\\\\&"` by accident — Python leaves an unrecognised escape
    alone and warns — and that behaviour is scheduled to become a
    `SyntaxError`. The specimens this suite quotes are *made of* backslashes:
    `d\\&#039;Atelier` from jobivoire, the JSON escapes in `_ldjson`, the
    `\\r` this class's neighbour is about. **A file that documents escaping
    is the likeliest place to escape something wrongly**, and the warning
    goes to stderr where a green `OK` hides it.

    Compiling is not importing: this reads every tracked `.py` without
    running any of it.
    """

    def test_no_invalid_escapes_or_other_syntax_warnings(self):
        import glob
        import warnings
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        found = []
        seen = 0
        for path in glob.glob(os.path.join(root, "**", "*.py"),
                              recursive=True):
            if os.sep + ".git" + os.sep in path:
                continue
            seen += 1
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                try:
                    compile(src, path, "exec")
                except SyntaxWarning as exc:      # raised, not warned
                    found.append(f"{os.path.relpath(path, root)}: {exc}")
                for item in caught:
                    if issubclass(item.category, SyntaxWarning):
                        found.append(f"{os.path.relpath(path, root)}: "
                                     f"{item.message}")
        self.assertGreater(seen, 50, "found almost no python to compile")
        self.assertEqual(found, [], "; ".join(found[:3]))


class TlsHostsAreRoutedEverywhere(unittest.TestCase):
    """#104 was fixed in one of the two adapters that read the host.

    `_tls.py` exists because **`empleate.gob.es` serves its leaf certificate
    and no intermediate**. Python's stdlib does not chase the AIA extension,
    so verification fails with `unable to get local issuer certificate` —
    while `curl` succeeds, because it does chase it. That is why the defect
    survived a `curl` check.

    `empleate.py` was given the context. **`oposiciones.py` was not**, and it
    reads the same host through the same `urlopen`. Nothing failed loudly:
    the robots guard refuses both adapters earlier, so the broken TLS path
    was never reached and never reported.

    **The fix is per-adapter and the host list is central**, which is the
    shape that loses one call site. This binds them: a file naming a host in
    `_tls.HOSTS` must route through `_tls`.
    """

    def test_every_adapter_reading_a_tls_host_imports_tls(self):
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        sys.path.insert(0, scripts)
        import _tls
        hosts = {h for h in _tls.HOSTS if not h.startswith("www.")}
        self.assertTrue(hosts, "_tls declares no hosts to check")

        offenders = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            # only a file that actually opens a socket on the host counts
            if not re.search(r"urlopen|http\.client", src):
                continue
            if not any(h in src for h in hosts):
                continue
            if not re.search(r"(^|\n)\s*import\s+_tls", src):
                offenders.append(name)
        self.assertEqual(offenders, [],
                         "these read a host in _tls.HOSTS over a raw stdlib "
                         "context and will fail verification: "
                         + ", ".join(offenders))


class GuardReportsBytesNotCharacters(unittest.TestCase):
    """#130: `len()` of a decoded string counts characters; every message
    called the number `bytes`.

    **An all-ASCII body cannot catch this** — the two counts coincide there,
    and `robots.txt` is usually ASCII, which is why it survived. It shows on
    anything else: `empleate.gob.es` answered with an 8 456-byte error page
    carrying six multi-byte sequences, and the guard announced *"8 450
    bytes"*.

    **A wrong unit is worse than a missing one.** A missing unit stops the
    reader; a wrong one invites them to compare two numbers that are not the
    same quantity. That is exactly what happened: a direct read (8 456) and
    this message (8 450) were set beside each other and the difference was
    published as the site changing size between reads — **a property of our
    counter, reported as a property of the host.**

    So the specimen here is deliberately multi-byte, and the assertion is
    against the count on the wire.
    """

    def _serve(self, body_bytes, ctype="text/html"):
        """One request, on a real socket, then the server dies."""
        import http.server
        import threading
        holder = {}

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(inner):                      # noqa: N805
                inner.send_response(200)
                inner.send_header("Content-Type", ctype)
                inner.send_header("Content-Length", str(len(body_bytes)))
                inner.end_headers()
                inner.wfile.write(body_bytes)

            def log_message(inner, *a):             # noqa: N805
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        holder["port"] = srv.server_address[1]
        t = threading.Thread(target=srv.handle_request, daemon=True)
        t.start()
        self.addCleanup(srv.server_close)
        return holder["port"]

    def test_a_multibyte_body_is_reported_by_its_byte_length(self):
        import _robots
        # six two-byte sequences, exactly the shape of the page that exposed
        # this: an error document with accented Spanish.
        text = ("<html><title>SEPE</title>"
                "<p>Si el problema persiste, p\u00f3ngase en contacto "
                "con nosotros a trav\u00e9s de la sede electr\u00f3nica. "
                "Disculpe las molestias, gracias por su comprensi\u00f3n. "
                "M\u00e1s informaci\u00f3n.</p></html>")
        raw = text.encode("utf-8")
        self.assertGreater(len(raw), len(text),
                           "specimen is not multi-byte — this test would "
                           "pass on the defect it exists to catch")

        port = self._serve(raw)
        got = _robots._fetch_once(
            f"http://127.0.0.1:{port}/robots.txt", "127.0.0.1", 10)

        self.assertEqual(got["state"], "unrecognised", got.get("why"))
        self.assertEqual(
            got["bytes"], len(raw),
            f"reported {got['bytes']}, on the wire {len(raw)}, decoded "
            f"{len(text)} characters — the report is following the decode")
        self.assertIn(f"{len(raw)} bytes", got["why"],
                      "the printed sentence still carries the wrong number "
                      "even if the field is right — the user reads the "
                      "sentence")

    def test_an_ascii_body_agrees_and_proves_nothing_alone(self):
        """Kept as the control, and labelled as such: it passes on the defect
        too, which is why the case above exists."""
        import _robots
        raw = b"<html>plain ascii error page, no rules here</html>"
        port = self._serve(raw)
        got = _robots._fetch_once(
            f"http://127.0.0.1:{port}/robots.txt", "127.0.0.1", 10)
        self.assertEqual(got["bytes"], len(raw))


class DeclaredAgentIsSentEverywhere(unittest.TestCase):
    """#120 settled what this project calls itself. **The declaration was
    central and its application was per adapter**, so two files never got it.

    Found on 2026-09-04 by looking for the shape that lost `oposiciones.py` a
    day earlier — a value a helper hands back that the caller must remember to
    use. `_tls.context_for()` returns a context you have to pass to `urlopen`;
    `_ua.UA` is a string you have to put in a header. **Neither does anything
    on its own.**

    What was found:

      * `adzuna.py` defined its **own** `UA`, naming no agent token, carrying
        no version and no contact URL, and describing the tool as *"personal
        job search; one user"* — which this repository stopped being.
      * `labonnealternance.py` sent **no `User-Agent` at all**, so urllib
        announced `Python-urllib/3.x`.

    Both are in the four keyed-API boards, which carry a documented exemption
    from the **robots guard**. That is a different obligation, and it does not
    extend here: a key says which account is calling, not who is calling.

    **Declaring a token and then not sending it is worse than not declaring
    one** — the operators who could have recognised us cannot, and the
    declaration in `_ua.py` becomes a claim the traffic does not support.
    """

    def test_every_network_reader_sends_the_declared_agent(self):
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        offenders = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            if not re.search(r"urlopen|http\.client", src):
                continue
            imported = re.search(r"(^|\n)\s*(from _ua import|import _ua)", src)
            header = re.search(r"""["']User-Agent["']\s*:""", src)
            if not imported:
                offenders.append(f"{name} (no _ua import)")
            elif not header:
                offenders.append(f"{name} (imports _ua, sends no header)")
        self.assertEqual(offenders, [],
                         "these open sockets without the declared agent: "
                         + ", ".join(offenders))

    def test_no_adapter_defines_a_user_agent_of_its_own(self):
        """The defect was not a missing header — `adzuna.py` had one. It was a
        **second declaration**, which is why a header check alone would have
        stayed green."""
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        offenders = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            if re.search(r"^UA\s*=\s*[\"']", src, re.M):
                offenders.append(name)
        self.assertEqual(offenders, [],
                         "these bind their own UA string, shadowing the one "
                         "declaration: " + ", ".join(offenders))


class AnEmptyBodyIsAnOpenDoor(unittest.TestCase):
    """Decided by the owner on 2026-09-04, on #104.

    > *"l'absence de regle est une porte ouverte. Rappel : le fichier
    > robots.txt est un souhait de l'hote (qui bien souvent est autogenere et
    > non verifie)"*

    **It is the counterpart of a rule this repository already applies in the
    other direction.** `robots-policy.md` holds that a vendor default binds
    even though nobody meant it — Honduras publishes a file copied out of
    Google's documentation and we obey it. **If an unmeant refusal binds, an
    unwritten one cannot.**

    **The fragile thing is the boundary, not the state that moved.** *"A body
    that says nothing does not say no"* sits one sentence away from *"we
    proceed when we do not know"*, and the second would undo #118 — where a
    host that closes everything to this project by name was swept whenever
    the request timed out. So the neighbours are pinned as hard as the change.
    """

    def setUp(self):
        """**The real ladder is three attempts with 1.5s and 4s of backoff.**
        Two cases here end in `unreachable` on purpose, and paying the real
        wait for them put twenty-five seconds on the suite. The retry
        behaviour is pinned elsewhere; what these cases are about is the
        verdict."""
        import _robots
        real = _robots._BACKOFF
        _robots._BACKOFF = (0, 0)
        self.addCleanup(setattr, _robots, "_BACKOFF", real)

    class _Resp:
        def __init__(self, body, ctype, code=200):
            self._b = body.encode("utf-8") if isinstance(body, str) else body
            self._c, self._code = ctype, code

        def read(self):
            return self._b

        def geturl(self):
            return "https://h.example/robots.txt"

        def getcode(self):
            return self._code

        @property
        def headers(self):
            return {"Content-Type": self._c}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _verdict(self, body, ctype="text/html", code=200):
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = (
            lambda r, timeout=None, **k: self._Resp(body, ctype, code))
        try:
            return (_robots.verdict("h.example"),
                    _robots.allowed("h.example", "/jobs"))
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    # ---- the state that moved -------------------------------------------

    def test_a_body_with_no_directive_line_opens_the_door(self):
        v, a = self._verdict("<html><title>SEPE</title>error</html>")
        self.assertEqual(v["state"], "unrecognised")
        self.assertTrue(v["sweep"])
        self.assertTrue(a["allowed"])

    def test_it_opens_the_door_without_claiming_to_know(self):
        """**`allowed: True` with `certain: False` is the honest shape.** We
        proceed on a policy, not on a finding, and anything reading this
        module must be able to tell those apart — #128 exists because they
        were merged once."""
        v, a = self._verdict("<html><title>SEPE</title>error</html>")
        self.assertTrue(a["allowed"])
        self.assertFalse(v["certain"])
        self.assertFalse(a["certain"])

    def test_the_reason_says_why(self):
        """A verdict that gives no reason invites suspicion; one that gives a
        false reason reads like a verification. The sentence carries the
        status, the type, the size and the absence of directive lines."""
        body = "<html><title>SEPE</title>no rules here</html>"
        v, _a = self._verdict(body, "text/html")
        why = v["reason"]
        self.assertIn("200", why)
        self.assertIn("text/html", why)
        self.assertIn(str(len(body.encode("utf-8"))), why)
        self.assertIn("User-agent", why)
        self.assertIn("open door", why)

    # ---- the two neighbours, which must not move -------------------------

    def test_a_2xx_that_is_not_200_still_stops_us(self):
        """`algerie.tanqeeb.com` answers **202 with zero bytes**. That is not
        a body without rules — it is not a document at all. #125."""
        v, a = self._verdict("", "text/plain", code=202)
        self.assertEqual(v["state"], "unreachable")
        self.assertIsNone(v["sweep"])
        self.assertIsNone(a["allowed"])

    def test_the_open_door_did_not_reach_the_unreachable_state(self):
        """**The one that would undo #118.** A host we could not reach is a
        host we know nothing about, and it looks exactly like a host that
        closes everything to us by name — `nea.gov.kh` did."""
        import _robots
        real = _robots.urllib.request.urlopen

        def boom(*a, **k):
            raise _robots.urllib.error.URLError("timed out")

        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = boom
        try:
            v = _robots.verdict("h.example")
            a = _robots.allowed("h.example", "/jobs")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()
        self.assertEqual(v["state"], "unreachable")
        self.assertIsNone(v["sweep"], "a fetch failure became a permission — "
                                      "this is #118, the worst defect this "
                                      "module has had")
        self.assertIsNone(a["allowed"])

    def test_a_403_on_robots_txt_is_still_a_refusal(self):
        """**The host answered, and it answered no.** Nothing about an
        absence of rules reaches this row."""
        import _robots
        real = _robots.urllib.request.urlopen

        def refuse(*a, **k):
            raise _robots.urllib.error.HTTPError(
                "https://h.example/robots.txt", 403, "Forbidden", {},
                io.BytesIO(b"nope"))

        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = refuse
        try:
            v = _robots.verdict("h.example")
            a = _robots.allowed("h.example", "/jobs")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()
        self.assertEqual(v["state"], "refused")
        self.assertIsNot(v["sweep"], True)
        self.assertIsNot(a["allowed"], True)


class EveryCardDeclaresItsScript(unittest.TestCase):
    """The card-to-script link was never written down, so every check had to
    guess it — and guessing was wrong about one time in seven.

    **Three audits in two days tripped on a guessed correspondence.** A
    `decode("utf-8")` pattern that defined its own population and missed nine
    adapters. A `sweep()` in `francetravail.py` — the adapter's own function,
    nothing to do with the guard — counted as a guard call. And
    `jobivoire.md`, which names **no** script of its own: the only `.py` it
    mentions is `employtt.py`, in a cross-reference about entity escaping, so
    a name-matching check paired the card with the wrong adapter entirely.

    **Those are not three slips. They are three instances of one missing
    fact.** `<!-- script: -->` states it, beside the `<!-- hosts: -->` line
    that was already there, and this reads it without heuristics.

    **The guard runs both ways**, because each direction catches a different
    accident:

      * a declaration naming a file that does not exist — a rename, a typo;
      * an adapter no card declares — a board shipped without its card
        pointing at it, which is exactly what `jobivoire` was.

    Tooling is named here rather than pattern-matched: a rule that excluded
    "anything not looking like a board" would quietly excuse a real adapter
    the day one is named like a utility.
    """

    TOOLING = frozenset({
        "ledger.py", "employers.py", "dormant.py", "achievements.py",
        "board_offer.py", "tenant_offer.py",
    })

    def _paths(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return (os.path.join(root, "shared", "boards"),
                os.path.join(root, "skills", "job-scan", "scripts"))

    def _declared(self):
        import glob
        import re
        cards, _ = self._paths()
        out = {}
        for path in sorted(glob.glob(os.path.join(cards, "*.md"))):
            name = os.path.basename(path)
            if name.lower() == "readme.md":
                continue
            with open(path, encoding="utf-8") as fh:
                head = fh.read(4000)
            m = re.search(r"<!--\s*script:\s*([a-z0-9_]+\.py)\s*-->", head)
            if m:
                out.setdefault(m.group(1), []).append(name)
        return out

    def _adapters(self):
        import glob
        _, scripts = self._paths()
        return {os.path.basename(p)
                for p in glob.glob(os.path.join(scripts, "*.py"))
                if not os.path.basename(p).startswith("_")} - self.TOOLING

    def test_every_declaration_names_a_file_that_exists(self):
        import glob
        _, scripts = self._paths()
        present = {os.path.basename(p)
                   for p in glob.glob(os.path.join(scripts, "*.py"))}
        missing = sorted(s for s in self._declared() if s not in present)
        self.assertEqual(missing, [],
                         "cards declare scripts that are not there: "
                         + ", ".join(missing))

    def test_every_adapter_is_declared_by_some_card(self):
        """**The direction that would have caught `jobivoire`.** Its adapter
        existed and shipped; no card pointed at it, so nothing could find the
        pair except by guessing the name."""
        declared = set(self._declared())
        orphans = sorted(self._adapters() - declared)
        self.assertEqual(orphans, [],
                         "these adapters are declared by no card, so any "
                         "check must guess the link: " + ", ".join(orphans))

    def test_the_declarations_are_enough_to_pair_without_guessing(self):
        """A shared adapter may be declared by several cards — `ats.py` serves
        seven — and that is the point: **the fact is written, so nothing has
        to infer it.**"""
        declared = self._declared()
        self.assertGreater(len(declared), 50)
        shared = {k: v for k, v in declared.items() if len(v) > 1}
        self.assertIn("ats.py", shared,
                      "ats.py serves several boards; if no card pairs with "
                      "it more than once the declarations have drifted")


class TheCredentialNoteKeepsItsBlock(unittest.TestCase):
    """`missing_note()` indented only the first credential it listed.

    The variable names were joined with a bare newline and then interpolated
    after eight spaces, so **the f-string indented the first line and every
    later one started at column 0**, falling out of the block a reader is
    meant to copy.

    **A single credential cannot show this** — there is no second line. The
    two that can are `ADZUNA_APP_ID`/`ADZUNA_APP_KEY` and France Travail's
    pair: **the two messages whose entire point is that both values are
    needed.** So the specimen here has two, and one with a single name is
    kept beside it to say why it proves nothing alone.

    It matters more than a layout slip because of where it sits. The same
    measurement established that `missing_note()` goes to **stderr with exit
    2 and an empty stdout**, and that no documented invocation redirects
    stderr — so **there is no silent failure here**: a wrong key gives a named
    401, not an empty board. **This message is the user's only recovery, and
    half its content was leaving the block.**
    """

    def _indents(self, names):
        import _secrets
        note = _secrets.missing_note(names, "x", "X Service", "see the card")
        return [len(ln) - len(ln.lstrip())
                for ln in note.split("\n")
                if "=" in ln and ln.strip().endswith("\u2026")]

    def test_two_credentials_are_both_inside_the_block(self):
        got = self._indents(["ADZUNA_APP_ID", "ADZUNA_APP_KEY"])
        self.assertEqual(len(got), 2, "the specimen must list two names or "
                                      "it cannot catch this")
        self.assertEqual(got, [got[0]] * 2,
                         f"the credentials are indented {got} — a later line "
                         f"left the block the reader is told to copy")
        self.assertGreater(got[0], 0, "the block is not indented at all")

    def test_a_single_credential_agrees_and_proves_nothing_alone(self):
        """Kept and labelled: this passes on the defect."""
        self.assertEqual(len(self._indents(["LBA_API_KEY"])), 1)

    def test_it_still_gives_both_routes(self):
        """**Prescribing a shell command to somebody without a shell is not
        help**, so the note carries a file route and a terminal route. A fix
        to the layout must not cost one of them."""
        import _secrets
        note = _secrets.missing_note(["A_KEY"], "svc", "X", "y")
        self.assertIn("credentials.env", note)
        self.assertIn("set -a", note)
        self.assertIn("config.yml", note)


class DocumentedInvocationsAreReal(unittest.TestCase):
    """Every board card documents how to run its adapter. Nothing compared
    that with what the script accepts.

    **Re-verifying a board means running its adapter**, and seventy adapters
    cannot be run for an internal check. **But half of it needs no request at
    all**: `argparse` states what a script accepts and the card asserts what
    to type.

    Read from the **AST**, never by importing or by `--help` — importing an
    adapter executes its module-level code, and a check should not have to run
    the thing it checks.

    **This guard shipped in v1.210.0 seeing less than half of what it claimed
    to check**, and the correction is the point:

      * **Invocations through a shell variable were invisible.** 29 cards
        write `S=…/board.py` and then `python3 $S search …`, which never
        contains the filename. **109 command lines, unchecked, reported as
        checked.** Aliases assigned in the same block are resolved now.
      * **Options can be built in a loop too, not only subcommands.**
        `computrabajo.py` adds one per entry of `FORBIDDEN`, so `--sal` is
        real and the AST cannot see it. It was reported as a defect in a card
        whose command works verbatim.
      * **A pipe is not an argument.** `python3 $S provincias | head -5` was
        read as passing `-5`.

    **Prose is not an invocation either.** The first pass produced four
    findings and all four were its own. Only lines beginning as a command,
    with any `#` tail and any pipe removed, are read.

    What cannot be checked is counted rather than hidden — the count is
    asserted below, so this cannot go quiet by drifting to zero.
    """

    LOOSE = ("--help", "-h")

    def _shape(self, path):
        """Subcommands, options, and whether either is built in a loop."""
        import ast
        tree = ast.parse(open(path, encoding="utf-8").read())
        subs, opts = set(), set()
        dyn_sub = dyn_opt = False
        for n in ast.walk(tree):
            if not (isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)):
                continue
            if n.func.attr == "add_parser" and n.args:
                if isinstance(n.args[0], ast.Constant):
                    subs.add(n.args[0].value)
                else:
                    dyn_sub = True
            elif n.func.attr == "add_argument":
                lits = [a.value for a in n.args
                        if isinstance(a, ast.Constant)
                        and isinstance(a.value, str)]
                if n.args and not lits:
                    dyn_opt = True
                for v in lits:
                    if v.startswith("-"):
                        opts.add(v)
        return subs, opts, dyn_sub, dyn_opt

    def _commands(self, text, script):
        """Command lines naming the script, or a shell variable assigned to
        it earlier in the same fenced block."""
        import re as _re
        out = []
        for m in _re.finditer(r"```[a-z]*\n(.*?)```", text, _re.S):
            block = m.group(1).replace("\\\n", " ")
            aliases = {a.group(1) for a in _re.finditer(
                r"^\s*([A-Za-z_][A-Za-z0-9_]*)=\S*?" + _re.escape(script)
                + r"\s*$", block, _re.M)}
            for line in block.split("\n"):
                line = line.split("#", 1)[0]
                line = line.split("|", 1)[0].strip()   # a pipe is not an arg
                tail = None
                if script in line and _re.match(
                        r"^(python3?|\$|)\s*[\"']?\S*" + _re.escape(script),
                        line):
                    tail = line.split(script, 1)[1]
                else:
                    for v in aliases:
                        mm = _re.match(
                            r"^python3?\s+[\"']?\$\{?" + v + r"\}?[\"']?(.*)$",
                            line)
                        if mm:
                            tail = mm.group(1)
                            break
                if tail is None:
                    continue
                sub, opts = None, []
                for tok in tail.replace('"', " ").split():
                    if tok.startswith("-"):
                        opts.append(tok.split("=")[0])
                    elif sub is None and not opts and _re.fullmatch(
                            r"[a-z][a-z0-9-]*", tok):
                        sub = tok
                if sub or opts:
                    out.append((sub, opts, line[:74]))
        return out

    def _walk(self):
        import glob
        import re as _re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cards = os.path.join(root, "shared", "boards")
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        bad, checked, skipped, with_cmd = [], 0, 0, 0
        for path in sorted(glob.glob(os.path.join(cards, "*.md"))):
            if os.path.basename(path).lower() == "readme.md":
                continue
            text = open(path, encoding="utf-8").read()
            m = _re.search(r"<!--\s*script:\s*([a-z0-9_]+\.py)\s*-->", text)
            if not m:
                continue
            sp = os.path.join(scripts, m.group(1))
            if not os.path.exists(sp):
                continue          # the declaration guard owns that failure
            subs, opts, dyn_sub, dyn_opt = self._shape(sp)
            card = os.path.basename(path)[:-3]
            cmds = self._commands(text, m.group(1))
            if cmds:
                with_cmd += 1
            for sub, used, raw in cmds:
                if sub is not None:
                    if dyn_sub:
                        skipped += 1
                    else:
                        checked += 1
                        if sub not in subs:
                            bad.append(f"{card}: {m.group(1)} has no "
                                       f"subcommand `{sub}` "
                                       f"(has {sorted(subs)}) — {raw}")
                for o in used:
                    if o in self.LOOSE:
                        continue
                    if dyn_opt:
                        skipped += 1
                        continue
                    checked += 1
                    if o not in opts:
                        bad.append(f"{card}: {m.group(1)} has no option "
                                   f"`{o}` — {raw}")
        return bad, checked, skipped, with_cmd

    def test_every_documented_subcommand_and_option_exists(self):
        bad, checked, _skipped, _n = self._walk()
        self.assertGreater(checked, 350,
                           f"only {checked} checks ran — the card format "
                           f"changed and this went quiet")
        self.assertEqual(bad, [], "\n".join(bad[:6]))

    def test_the_shell_variable_form_is_read(self):
        """**The hole that shipped.** 29 cards invoke through `$S`; if this
        stops resolving, a third of the corpus goes unchecked in silence and
        the count above still looks healthy."""
        _bad, _checked, _skipped, with_cmd = self._walk()
        self.assertGreater(with_cmd, 55,
                           f"only {with_cmd} cards were seen to carry an "
                           f"invocation — the `$S` form is not resolving")


class TheSharedBoardSaysWhichOneItRead(unittest.TestCase):
    """`jobup.py` serves two boards and defaulted to one of them in silence.

    `--site` carried `default="jobup"`, so somebody who had enabled **jobs.ch**
    and typed the general form got twenty **jobup.ch** advertisements, HTTP
    200, no warning. The `ledger_id` prefix was the only tell, **and it is in
    the JSON, not in the message** — the reader of a sweep reads the message.

    **And the tag lied in the other direction too.** `note()` printed
    `[jobup]` unconditionally, so `--site jobs-ch` announced its twenty
    advertisements under the other board's name while the records themselves
    carried `jobs-ch:` ids and `www.jobs.ch` URLs. **The data was right and
    every sentence about it was wrong.**

    **The default is kept and no longer silent.** Making `--site` required
    would have been the other repair, and it would have invalidated the
    invocations `jobup.md` documents — two days after establishing that the
    documented invocations are all valid.

    **The announcement fires only when nobody chose.** A warning on correct
    use is noise, so the quiet case is asserted too: without it this cannot
    tell *"announces"* from *"announces when it should"*.
    """

    def _parser(self):
        import jobup
        return jobup

    def test_the_flag_does_not_carry_its_own_default(self):
        """`argparse` cannot distinguish a chosen `jobup` from an unchosen one
        if the default is the value. It has to arrive as `None`."""
        jobup = self._parser()
        p = jobup.build() if hasattr(jobup, "build") else None
        if p is None:
            import re
            src = open(jobup.__file__, encoding="utf-8").read()
            i = src.index('add_argument("--site"')
            call = src[i:src.index("\n\n", i)]
            self.assertIn("default=None", call)
            self.assertNotIn('default="jobup"', call)

    def test_the_default_is_named_once(self):
        jobup = self._parser()
        self.assertEqual(jobup.DEFAULT_SITE, "jobup")
        self.assertIn(jobup.DEFAULT_SITE, jobup.SITES)

    def test_the_tag_follows_the_site(self):
        """`[jobup]` over twenty jobs.ch advertisements is the defect this
        catches — the records were always right."""
        import io
        import contextlib
        jobup = self._parser()
        before = jobup._TAG
        try:
            for name in sorted(jobup.SITES):
                jobup._TAG = name
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    jobup.note("x")
                self.assertEqual(err.getvalue().strip(), f"[{name}] x")
        finally:
            jobup._TAG = before

    def test_the_default_announces_itself(self):
        """`resolve_site(None)` is somebody who typed the general form."""
        jobup = self._parser()
        site, said = jobup.resolve_site(None)
        self.assertEqual(site, jobup.DEFAULT_SITE)
        self.assertIsNotNone(said, "the default no longer announces itself")
        self.assertIn(jobup.SITES[jobup.DEFAULT_SITE]["host"], said)
        self.assertIn("--site", said)
        for name in jobup.SITES:
            self.assertIn(name, said,
                          "the line does not name the board the reader might "
                          "have meant — a warning that does not say what to "
                          "do instead is half a warning")

    def test_a_chosen_site_is_not_announced(self):
        """**The witness, and its first version could not fail.**

        It asserted that the `note(` call sat between two markers in the
        source. Nesting `if True:` inside that span fires the announcement on
        every run and **leaves the text exactly where the check looked** — the
        suite stayed green while every correct invocation was warned at. It
        was reading position, not condition.

        `resolve_site` returns the message instead of printing it, so the
        condition is the value and both cases can be compared.
        """
        jobup = self._parser()
        for name in sorted(jobup.SITES):
            site, said = jobup.resolve_site(name)
            self.assertEqual(site, name)
            self.assertIsNone(said,
                              f"--site {name} was chosen explicitly and still "
                              f"drew a warning — a warning on correct use is "
                              f"the noise this was avoiding")


class TheRefusedSearchIsRefusedInFact(unittest.TestCase):
    """`_hiringcafe` centralises the refusal so three commands cannot say
    three different things. **Nothing exercised it** — the module was never
    named in this suite, and renaming `search_url` away left the suite green.

    The corpus scan next door asserts that no adapter assembles the refused
    URL itself, which is a statement about **text across 65 files** and is
    right to be. It says nothing about whether the one place that may build
    it actually refuses to fetch it.

    **Collection is suspended by decision, not by accident** — no request to
    that host in any form, even on the paths its own file allows. So this
    exercises the refusal with an opener that fails the case if it is ever
    reached.
    """

    def test_the_search_mode_refuses_and_makes_no_request(self):
        import hiringcafe

        def forbidden(*a, **k):
            raise AssertionError(
                "hiringcafe.py opened a socket — collection is suspended and "
                "no request to that host is permitted in any form")

        real = hiringcafe.urllib.request.urlopen
        hiringcafe.urllib.request.urlopen = forbidden
        code, said = None, ""
        try:
            import subprocess
            import sys as _sys
            out = subprocess.run(
                [_sys.executable, os.path.join(SCRIPTS, "hiringcafe.py"),
                 "search", "--query", "x", "--country", "CH"],
                capture_output=True, text=True, timeout=60)
            code, said = out.returncode, out.stderr
        except AssertionError:
            raise
        finally:
            hiringcafe.urllib.request.urlopen = real
        self.assertEqual(code, 7,
                         f"the refused search did not exit 7 (got {code!r} "
                         f"{said[:60]})")

    def test_the_refusal_quotes_the_rule_and_the_date(self):
        """**A refusal that does not say what refused it invites a retry.**"""
        import _hiringcafe
        said = _hiringcafe.refusal("x", "this search")
        self.assertIn("robots.txt", said)
        self.assertIn(_hiringcafe.MEASURED_ON, said)
        self.assertIn("No request was made", said)

    def test_the_constructor_is_the_only_place_that_builds_it(self):
        """Kept as the corpus half, beside the exercised one — **the scan
        covers 65 files, the case above covers one command.**"""
        import _hiringcafe
        url = _hiringcafe.search_url({"searchState": "{}"})
        self.assertTrue(url.startswith(_hiringcafe.BASE))
        self.assertIn("searchState", url)


class PresenceIsNotBehaviour(unittest.TestCase):
    """Four guards asserted that a token appeared in a file and reported a
    behaviour. **Each could be neutralised without moving the text it looked
    for**, and each reinstates a defect this repository had already shipped a
    fix for.

    | guard | how it stayed green |
    | :-- | :-- |
    | `_tls` is routed | import kept, `context=None` passed to `urlopen` |
    | the declared agent is sent | `_ua` imported, a Chrome string in the header |
    | the SmartRecruiters gate exists | the gate's body replaced by `return True` |
    | that gate refuses | `if not allowed:` replaced by `if False:` |

    **A guard that reads presence cannot see intent.** The import is there,
    the header key is there, the call is there — and none of them does
    anything. These cases exercise the code instead, on stubbed sockets, so no
    request leaves the machine.
    """

    def _capture(self, module):
        """Run the module's fetch against a stubbed opener and hand back the
        `Request` and the keyword arguments it was called with."""
        seen = {}

        def fake(req, *a, **kw):
            seen["req"] = req
            seen["kw"] = kw
            raise module.urllib.error.URLError("stubbed")

        return seen, fake

    def test_every_adapter_that_uses_tls_actually_passes_the_context(self):
        """**One specimen does not cover a corpus, and this is the proof.**

        The case below exercises `oposiciones.py` and says nothing about the
        other reader of the same host. `empleate.py` could be given
        `context=None` — reinstating #104 on the adapter #104 was *opened*
        for — and the suite stayed green: the corpus scan sees the import, the
        exercised case sees the wrong file.

        Three files use `_tls`; two of them are adapters. Exercising both
        costs a loop.
        """
        import glob
        import re
        import importlib
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        users = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            src = open(path, encoding="utf-8").read()
            if re.search(r"(^|\n)\s*import _tls", src):
                users.append(name[:-3])
        self.assertGreaterEqual(len(users), 2,
                                "the adapters using _tls have vanished — "
                                "either a real change or this went quiet")

        for mod_name in users:
            with self.subTest(adapter=mod_name):
                mod = importlib.import_module(mod_name)
                seen, fake = self._capture(mod)
                real = mod.urllib.request.urlopen
                gate = getattr(mod, "_robots_gate", None)
                mod.urllib.request.urlopen = fake
                real_sleep = getattr(mod, "time", None)
                if real_sleep is not None:
                    slept = mod.time.sleep
                    mod.time.sleep = lambda *_a, **_k: None
                if gate:
                    setattr(mod, "_robots_gate", lambda *a, **k: None)
                try:
                    fn = getattr(mod, "fetch", None) or getattr(mod, "get")
                    try:
                        fn("https://empleate.gob.es/x")
                    except BaseException:
                        pass
                finally:
                    mod.urllib.request.urlopen = real
                    if real_sleep is not None:
                        mod.time.sleep = slept
                    if gate:
                        setattr(mod, "_robots_gate", gate)
                self.assertIn("kw", seen,
                              f"{mod_name}: never reached the opener")
                self.assertIsNotNone(
                    seen["kw"].get("context"),
                    f"{mod_name} sent the request with no TLS context — "
                    f"`_tls` is imported and not applied, which is #104")

    def test_a_tls_host_is_fetched_with_the_tls_context(self):
        """#104 again: `context=None` restores the failure `_tls` exists to
        remove, and the import stays in place while it does."""
        import oposiciones
        import _tls
        seen, fake = self._capture(oposiciones)
        real = oposiciones.urllib.request.urlopen
        real_gate = getattr(oposiciones, "_robots_gate", None)
        oposiciones.urllib.request.urlopen = fake
        if real_gate:
            oposiciones._robots_gate = lambda *a, **k: None
        try:
            try:
                oposiciones.fetch(
                    "https://empleate.gob.es/empleate/open/x", retries=0)
            except BaseException:
                pass
        finally:
            oposiciones.urllib.request.urlopen = real
            if real_gate:
                oposiciones._robots_gate = real_gate
        self.assertIn("kw", seen, "fetch() never reached the opener")
        ctx = seen["kw"].get("context")
        self.assertIsNotNone(
            ctx, "the request went out with no TLS context — `_tls` is "
                 "imported and not applied, which is #104 exactly")
        self.assertIsNotNone(_tls.context_for("empleate.gob.es"))

    def test_the_declared_agent_is_the_one_on_the_wire(self):
        """#120 again: the header key is what the old guard checked, and the
        value is what the operator reads."""
        import adecco
        import _ua
        seen, fake = self._capture(adecco)
        real = adecco.urllib.request.urlopen
        real_gate = adecco._robots_gate
        adecco.urllib.request.urlopen = fake
        adecco._robots_gate = lambda *a, **k: None   # the guard is elsewhere
        try:
            try:
                adecco.get("https://www.adecco.fr/", retries=0)
            except BaseException:
                pass
        finally:
            adecco.urllib.request.urlopen = real
            adecco._robots_gate = real_gate
        self.assertIn("req", seen, "fetch() never reached the opener")
        sent = seen["req"].get_header("User-agent")
        self.assertEqual(sent, _ua.UA,
                         f"the wire carries {sent!r}, not the declared "
                         f"agent — a token declared and not sent is worse "
                         f"than one never declared")

    def test_the_smartrecruiters_gate_refuses_when_it_should(self):
        """#121 again. The gate may be called, may exist, and may do nothing:
        `return True` in its body, or `if False:` where it decides, both left
        the suite green."""
        import ats
        calls = {"died": 0}
        real_verdict = ats.robots_verdict
        real_die = ats.die
        real_cfg = getattr(ats, "override_enabled", None)

        def refused(host):
            return {"sweep": False, "certain": True,
                    "reason": "User-agent: * / Disallow: /"}

        def die(msg, code=2):
            calls["died"] += 1
            raise SystemExit(code)

        ats.robots_verdict = refused
        ats.die = die
        if real_cfg is not None:
            ats.override_enabled = lambda *a, **k: False
        try:
            try:
                ats.smartrecruiters_gate()
            except SystemExit:
                pass
        finally:
            ats.robots_verdict = real_verdict
            ats.die = real_die
            if real_cfg is not None:
                ats.override_enabled = real_cfg
        self.assertEqual(calls["died"], 1,
                         "the host refuses and no override is enabled, and "
                         "the gate let the run continue")


class PartialStillWritesWhatItKept(unittest.TestCase):
    """`jobup.py search` announced rows on stderr and put none on stdout.

    When page 2 repeats page 1 entirely the sweep stops rather than looping —
    a good guard, and the diagnosis was right. But it stopped with
    `sys.exit(EXIT_PARTIAL)` **inside the page loop**, above the print stage,
    so the run said *"6 row(s) so far and they are good"* and wrote nothing.
    **Total and silent for anything reading stdout**, which is the whole
    chain. Reproduced twice on 2026-09-04, exit 6, `wc -l` 0. Issue #134.

    **Two exits left the same loop and only one of them worked.** The other,
    for a page with no postings, uses `break` and reaches the print. The
    difference was invisible because both printed a correct sentence first.

    **It was the only one.** Thirteen functions in the corpus exit inside a
    loop before their last `print`; eight of those claim to hold rows; two
    carry this very sentence — `philjobnet.py` and `jobivoire.py` — and both
    **print inside the loop**, so their rows are already out when they leave.
    A `die()` on a bad department code or a 404 is not this defect either.
    Same shape, different case, four times over.
    """

    class _Page:
        """One posting, returned for every page — which is what a board that
        has stopped paginating looks like."""

        BODY = ('<html><script type="application/ld+json">'
                '{"@type":"JobPosting","identifier":{"value":"abc-1"},'
                '"title":"X","hiringOrganization":{"name":"Y"},'
                '"datePosted":"2026-09-01",'
                '"url":"https://www.jobup.ch/fr/emplois/detail/abc-1/"}'
                '</script></html>')

    def _run(self, pages):
        import io
        import contextlib
        import jobup
        real_get = jobup.get
        real_gate = jobup.robots_verdict
        real_sleep = jobup.time.sleep
        jobup.get = lambda url: (200, self._Page.BODY, url)
        jobup.robots_verdict = lambda h: {"sweep": True, "certain": True,
                                          "reason": ""}
        jobup.time.sleep = lambda *a, **k: None
        args = argparse.Namespace(
            site="jobup", term="x", location=None, pages=pages, limit=None,
            delay=0)
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(out), \
                    contextlib.redirect_stderr(err):
                jobup.cmd_search(args)
        except SystemExit as exc:
            code = exc.code
        finally:
            jobup.get = real_get
            jobup.robots_verdict = real_gate
            jobup.time.sleep = real_sleep
        return code, out.getvalue(), err.getvalue()

    def test_the_repeated_page_still_writes_its_rows(self):
        code, out, err = self._run(pages=2)
        self.assertIn("pagination did not advance", err,
                      "the fixture did not reach the partial branch")
        rows = [l for l in out.splitlines() if l.strip()]
        self.assertEqual(
            len(rows), 1,
            f"stderr announced rows and stdout carried {len(rows)} — this is "
            f"#134: the exit skipped the print stage")
        self.assertEqual(code, 6, "the partial status was lost with the fix")

    def test_the_row_on_stdout_is_the_row_it_counted(self):
        """**A count on stderr and a row on stdout must be the same thing.**
        Writing *some* row would satisfy the case above."""
        import json
        _code, out, err = self._run(pages=2)
        row = json.loads(out.splitlines()[0])
        self.assertEqual(row["id"], "abc-1")
        self.assertIn("1 row(s) so far", err)

    def test_a_normal_run_is_unchanged(self):
        """The witness: one page, no repetition, no partial status."""
        code, out, _err = self._run(pages=1)
        self.assertIsNone(code, "a complete run must not exit 6")
        self.assertEqual(len([l for l in out.splitlines() if l.strip()]), 1)


class EveryCardDeclaresItsCountries(unittest.TestCase):
    """Nothing in this repository said which country a board serves.

    The Atlas publishes a coverage figure per country and was **held by
    hand**, because there was no source to read: a card declared `verified`,
    `hosts` and `script`, and never a country. Two countries were published at
    0% while their adapter sat in `scripts/` — not a typo, an **absent link**.
    Only 29 of 85 cards named a country in their opening, in prose.

    **The pairing is the point, not the country.**

      * `script` **and** `countries` — a board that is covered, and where.
      * `countries` **without** `script` — assessed, no adapter. Ten cards,
        and `chile-public-sector.md` is the model: *"Five Chilean portals were
        assessed… none of them yields one."* **`CL` with no adapter is a fact
        the Atlas needs**, and publishing Chile as uncovered is then correct
        rather than an oversight.
      * `script` **without** `countries` — the hole this guard closes.

    **`*` is not a country and not a blank.** It says the adapter is not
    country-scoped: an ATS where the tenant decides, or a global board.
    Twenty-three cards carry it, and inventing a country for them would be
    exactly the error this replaces.

    **Every value was read off its own card**, one by one — a title or an
    opening sentence. A first pass tried to extract them from the first 1200
    characters and produced seven countries for Singapore's national portal
    and eight for the Philippines', because a card's opening compares it to
    other boards. **A map written by hand is not evidence either**; that is
    how `<!-- script: icims.py -->` came to sit on a card with no adapter.
    Both failures are why this is card-by-card and paired with a check.
    """

    # ISO 3166-1 alpha-2, the codes this corpus actually uses. Listed rather
    # than pattern-matched: `ZZ` matches a two-letter pattern and is not a
    # country, and the Atlas would carry it silently.
    ISO = frozenset("""
        AD AE AR AT AU AW BE BH BO BQ BR CA CH CI CL CM CO CR CU CW CY CZ DE
        DK DO DZ EC EE EG ES FI FR GB GE GH GN GR GT HN HR HU ID IE IL IN IT
        JM JO JP KE KW LB LT LU LV MA MG MT MU MX MY NG NI NL NO NZ OM PA PE
        PH PK PL PT PY QA RO RS SA SE SG SI SK SN SV TH TN TR TT UA US UY VE
        VN ZA
    """.split())

    def _cards(self):
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out = {}
        for path in sorted(glob.glob(os.path.join(root, "shared", "boards",
                                                  "*.md"))):
            name = os.path.basename(path)
            if name.lower() == "readme.md":
                continue
            with open(path, encoding="utf-8") as fh:
                head = fh.read(4000)
            co = re.search(r"<!--\s*countries:\s*(.+?)\s*-->", head)
            sc = re.search(r"<!--\s*script:\s*([a-z0-9_]+\.py)\s*-->", head)
            out[name[:-3]] = (co.group(1) if co else None,
                              sc.group(1) if sc else None)
        return out

    def test_every_declared_code_is_a_real_one(self):
        bad = []
        for card, (countries, _sc) in self._cards().items():
            if countries is None:
                continue
            for code in countries.split():
                if code == "*":
                    continue
                if code not in self.ISO:
                    bad.append(f"{card}: {code}")
        self.assertEqual(bad, [], "not ISO 3166-1 alpha-2: " + ", ".join(bad))

    def test_a_card_with_an_adapter_says_where_it_reaches(self):
        """**The direction that closes the Atlas hole.** A board shipped
        without this is a country published as uncovered while its adapter
        sits in `scripts/`."""
        silent = sorted(c for c, (co, sc) in self._cards().items()
                        if sc and not co)
        self.assertEqual(silent, [],
                         "these declare an adapter and no countries, so "
                         "nothing can tell what they cover: "
                         + ", ".join(silent))

    def test_the_star_is_not_mixed_with_countries(self):
        """`* FR` would mean both *"not country-scoped"* and *"France"*. A
        reader would take one and the Atlas the other."""
        mixed = []
        for card, (countries, _sc) in self._cards().items():
            if countries and "*" in countries.split() \
                    and len(countries.split()) > 1:
                mixed.append(card)
        self.assertEqual(mixed, [], "`*` mixed with codes: " + ", ".join(mixed))

    def test_the_declarations_cover_the_corpus(self):
        """**The floor**, so the population cannot empty in silence — the
        defect found in two of this suite's own guards on 2026-09-04."""
        cards = self._cards()
        self.assertGreater(len(cards), 80)
        declared = [c for c, (co, _s) in cards.items() if co]
        self.assertEqual(len(declared), len(cards),
                         f"only {len(declared)} of {len(cards)} cards declare "
                         f"countries — declared everywhere or an absence is "
                         f"not a signal")


class TheDeclaredDuplicateIsALedgerId(unittest.TestCase):
    """Three adapters publish the other board's own id, and the skill read
    none of them.

    `job-room`, `France Travail` and `La Bonne Alternance` syndicate ads from
    boards this plugin already sweeps, and each emits `duplicate_of` **in the
    ledger's namespace** — `jobup:<uuid>` beside its own `job-room:<uuid>`.
    `francetravail.py` states the intended conduct in its source: *"When it is
    set and the ledger already holds that row, this is the same posting —
    record it discarded naming the row."*

    **`SKILL.md` said the employer's name was the only signal available at
    scan time.** On one sweep of 497 job-room rows, **20 offered duplicates
    went through**, one of them already at status `applied`. Nothing stopped
    it until the ledger refused an id it already held — *after* it had been
    scored and listed as a find. #136.

    **And the employer fallback cannot cover those rows.** For a syndicated
    ad job-room writes the *syndicating board* as the employer — `Jobup` —
    while the ledger holds the real employer's legal name. No common
    substring in either direction: the two checks fail on different things.

    The value is only useful if it really is a ledger id, so that is what
    this exercises.
    """

    def test_the_value_is_a_ledger_id_not_a_url(self):
        import jobroom
        got = jobroom.duplicate_of(
            "https://www.jobup.ch/fr/emplois/detail/"
            "3fa85f64-5717-4562-b3fc-2c963f66afa6/")
        self.assertEqual(got, "jobup:3fa85f64-5717-4562-b3fc-2c963f66afa6")
        self.assertNotIn("/", got, "a URL cannot be looked up in the ledger")
        self.assertEqual(got.count(":"), 1)

    def test_a_host_this_plugin_does_not_sweep_yields_nothing(self):
        """**A duplicate of an ad we never held is not a duplicate.** Naming
        a board outside the ledger would produce a key that can never match,
        which reads like a working check and is not one."""
        import jobroom
        # **With a real UUID on it**, so the None can only come from the host
        # being unknown. The first version of this case used a URL with no
        # UUID and passed for that reason instead — it could not have failed
        # on its own subject.
        with_uuid = ("https://www.example.invalid/offer/"
                     "3fa85f64-5717-4562-b3fc-2c963f66afa6")
        self.assertTrue(jobroom.UUID_RE.search(with_uuid),
                        "the specimen must carry a UUID or this proves "
                        "nothing about the host lookup")
        self.assertIsNone(jobroom.duplicate_of(with_uuid))
        self.assertIsNone(jobroom.duplicate_of(None))

    def test_a_scheme_less_url_still_resolves(self):
        """The field is built from whatever the feed carries, and the feed
        does not always carry a scheme."""
        import jobroom
        self.assertEqual(
            jobroom.duplicate_of(
                "www.jobup.ch/fr/emplois/detail/"
                "3fa85f64-5717-4562-b3fc-2c963f66afa6/"),
            "jobup:3fa85f64-5717-4562-b3fc-2c963f66afa6")

    def test_the_skill_reads_the_field_at_the_exclusion_step(self):
        """**The object here is the text of `SKILL.md`**, which is what a run
        follows — so reading it is the check, not a proxy for one. What it
        must say is that a row whose `duplicate_of` is in the exclusion set is
        excluded, *at step 3*, before scoring."""
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        skill = open(os.path.join(root, "skills", "job-scan", "SKILL.md"),
                     encoding="utf-8").read()
        self.assertIn("duplicate_of", skill,
                      "the skill does not mention the field three adapters "
                      "publish")
        i = skill.index("- Anything already in the exclusion set from step 0.")
        # **the bullet list only.** A 400-character window reached into the
        # section below, whose heading also names the field, so deleting the
        # bullet left this green — the window was the test's own blind spot.
        bullets = skill[i:skill.index("\n\n", i)]
        self.assertIn("duplicate_of", bullets,
                      "step 3 does not exclude on `duplicate_of` — the field "
                      "may be described further down and never acted on")

    def test_every_adapter_that_publishes_it_is_named_in_the_skill(self):
        """A fourth adapter emitting it and going unnamed is the same defect
        again, one board later."""
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        whole = open(os.path.join(root, "skills", "job-scan", "SKILL.md"),
                     encoding="utf-8").read()
        # **The section, not the file.** 58 of 74 adapter names appear
        # somewhere in this skill, so "named anywhere" is true by accident
        # about four times in five — the first version of this case could not
        # have failed.
        start = whole.index("### Cross-board duplicates")
        end = whole.index("\n## ", start)
        skill = whole[start:end].lower()
        emitters = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            if '"duplicate_of"' in open(path, encoding="utf-8").read():
                emitters.append(name[:-3])
        self.assertGreaterEqual(len(emitters), 3,
                                "the emitters have vanished — either a real "
                                "change or this went quiet")
        # the skill names boards in prose, so match on the board's own words
        WORDS = {"jobroom": "job-room", "francetravail": "france travail",
                 "labonnealternance": "la bonne alternance"}
        missing = [e for e in emitters
                   if WORDS.get(e, e.replace("_", " ")) not in skill]
        self.assertEqual(missing, [],
                         "these publish `duplicate_of` and the skill does "
                         "not name them: " + ", ".join(missing))


class ATestNamespaceMatchesTheRealParser(unittest.TestCase):
    """A case that builds `argparse.Namespace` by hand bypasses argparse.

    **Most of that is already caught, and measuring it was the point.**
    A field the code reads under a *wrong* name raises `AttributeError` —
    renaming `term` to `keyword` turns three cases red. And a drift in the CLI
    itself is caught elsewhere: renaming `--term` to `--query` breaks the
    invocations `jobup.md` documents, which
    `DocumentedInvocationsAreReal` sees. The subprocess-driven case is
    validated by argparse directly — driving `--what` where the CLI wants
    `--query --country` failed loudly while this suite was being written.

    A field *missing* from the namespace is caught too, for the same reason:
    dropping `delay` turns those three cases red.

    **One shape escapes all of it: an option the CLI gains that the fixture
    does not supply.** Measured on v1.221.0 — adding `--since` to the parser
    produced **zero failures**, while every real invocation would now carry a
    field the case never sets. So the case drifts from the CLI it stands for,
    quietly, in the one direction nothing was watching.

    *Establishing that took two bad mutations of my own.* The first `delay`
    mutation matched nothing — the fixture wraps across lines, so
    `", delay=0)"` is not in the file — and its green was read as a finding.
    The second comparison ran with the new guard already in the working tree,
    because `git checkout` carries uncommitted changes across branches. **Both
    readings were void, and the gap is the one that survived redoing them.**
    """

    def _dests(self, script, subcommand):
        """Every `dest` the parser defines, read from the AST."""
        import ast
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, "skills", "job-scan", "scripts", script)
        tree = ast.parse(open(path, encoding="utf-8").read())
        var = None
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) \
                    and isinstance(n.value.func, ast.Attribute) \
                    and n.value.func.attr == "add_parser" \
                    and n.value.args \
                    and isinstance(n.value.args[0], ast.Constant) \
                    and n.value.args[0].value == subcommand:
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        var = t.id
        self.assertIsNotNone(var, f"no `{subcommand}` subparser in {script}")
        out = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr == "add_argument" \
                    and isinstance(n.func.value, ast.Name) \
                    and n.func.value.id == var:
                named = [a.value for a in n.args
                         if isinstance(a, ast.Constant)
                         and isinstance(a.value, str)]
                dest = next((kw.value.value for kw in n.keywords
                             if kw.arg == "dest"
                             and isinstance(kw.value, ast.Constant)), None)
                if dest:
                    out.add(dest)
                elif named:
                    out.add(named[0].lstrip("-").replace("-", "_"))
        return out

    def test_the_jobup_namespace_carries_every_option_the_cli_defines(self):
        dests = self._dests("jobup.py", "search")
        self.assertIn("term", dests, "the parser no longer defines --term, "
                                     "and the fixture below still passes it")
        built = {"site", "term", "location", "pages", "limit", "delay"}
        missing = sorted(dests - built)
        self.assertEqual(
            missing, [],
            f"PartialStillWritesWhatItKept builds a namespace without "
            f"{missing} — the CLI always supplies those, so the case is "
            f"exercising a shape no invocation can produce")

    def test_the_fixture_and_this_list_are_the_same_list(self):
        """**Two copies of one fact, and the case above compares the wrong
        one if they drift.** This reads the fixture's own namespace rather
        than trusting the literal repeated here."""
        import re
        src = open(os.path.abspath(__file__), encoding="utf-8").read()
        m = re.search(r"args = argparse\.Namespace\(\s*(.*?)\)", src, re.S)
        self.assertIsNotNone(m, "the fixture no longer builds a namespace")
        fields = set(re.findall(r"(\w+)=", m.group(1)))
        self.assertEqual(
            fields, {"site", "term", "location", "pages", "limit", "delay"},
            "the fixture's namespace changed and the list above did not")


class OneResolverForFilesAndKeys(unittest.TestCase):
    """`_secrets` resolved the workspace by a copy of `bin/workspace-path.py`
    with both of its guards left out.

    That file was written for #109 against one trap: **`$HOME` is not the
    person's folder outside a terminal — in CoWork it is a container's.** Its
    cascade takes a folder the user *named* first, then `JOB_HUNT_HOME`, then
    `<home>/Documents/job_applications` **only if `Documents` is writable**,
    and then refuses, with a question to put to the person.

    `_secrets._workspace()` had neither the first step nor the writability
    test. It took `JOB_HUNT_HOME`, else `Documents` **the moment it merely
    existed** — and a container has a `Documents`. So the credentials were
    read from a path the person will never see, and nothing failed. **A silent
    success, which is the failure #109 exists against.**

    It also mattered for a reason that had not been connected to it: of the
    three places a key may live, **the environment does not survive CoWork's
    shell reset (#110) and `~/.<name>.env` is inside the container (#109)**.
    The workspace file is the only one left, so the resolver that finds it is
    the whole path.

    **The hardening can stop finding a file that was being found**, and that
    is the case the last two cases here are about.
    """

    def _home(self, writable_docs=True, with_keys=False):
        """A throwaway home, so nothing here depends on this machine's."""
        import tempfile
        home = tempfile.mkdtemp()
        docs = os.path.join(home, "Documents")
        os.makedirs(os.path.join(docs, "job_applications"))
        if with_keys:
            with open(os.path.join(docs, "job_applications",
                                   "credentials.env"), "w") as fh:
                fh.write("ADZUNA_APP_ID=x\nADZUNA_APP_KEY=y\n")
        if not writable_docs:
            os.chmod(docs, 0o500)
            self.addCleanup(os.chmod, docs, 0o700)
        return home

    def _with_home(self, home):
        import importlib
        import _secrets
        keep = {k: os.environ.get(k) for k in
                ("HOME", "USERPROFILE", "JOB_HUNT_HOME",
                 "ADZUNA_APP_ID", "ADZUNA_APP_KEY")}

        def restore():
            for k, v in keep.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            importlib.reload(_secrets)

        self.addCleanup(restore)
        # **`~` is not resolved from `HOME` on Windows.** `expanduser` reads
        # `USERPROFILE` there, so setting only `HOME` left these cases looking
        # at the runner's real profile instead of the sandbox — two of the
        # three CI failures on this class. #143.
        os.environ["HOME"] = home
        os.environ["USERPROFILE"] = home
        for k in ("JOB_HUNT_HOME", "ADZUNA_APP_ID", "ADZUNA_APP_KEY"):
            os.environ.pop(k, None)
        importlib.reload(_secrets)
        return _secrets

    def test_the_two_resolvers_agree(self):
        """**The convergence itself.** Not that `_secrets` has a cascade — that
        it has *the* cascade, the one the files use."""
        import importlib.util
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        wp = os.path.join(root, "bin", "workspace-path.py")
        spec = importlib.util.spec_from_file_location("_wp_check", wp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        home = self._home(writable_docs=True)
        sec = self._with_home(home)
        self.assertEqual(sec._workspace(), mod.resolve()[0])

    def _needs_posix_permissions(self):
        """**`chmod 500` does not make a directory unwritable on Windows, and
        `os.access(dir, W_OK)` does not report the truth about directories
        there.** So the fixture cannot produce the state these cases are
        about, and a version of them that passed on Windows would be a guard
        that never exercises — the defect this suite found three times on
        2026-09-04, committed deliberately the fourth time.

        **Skipped with the reason rather than made green.** What #109's guard
        does under Windows is *not established*, and that is a question about
        the product, not about the test: it is #145, and this skip is where a
        reader meets it.
        """
        if os.name != "posix":
            self.skipTest(
                "chmod cannot create an unwritable directory here, and "
                "os.access is not authoritative on directories — see #145: "
                "whether #109's guard protects anything on Windows is "
                "unestablished, and this case cannot establish it")

    def test_an_unwritable_documents_settles_nothing(self):
        """**The guard `_secrets` was missing.** A container has a `Documents`
        too, so its existence proves nothing; not being able to write there is
        the evidence that this home is not the person's."""
        self._needs_posix_permissions()
        home = self._home(writable_docs=False)
        sec = self._with_home(home)
        self.assertIsNone(sec._workspace(),
                          "the workspace was guessed from a Documents this "
                          "process cannot write to — that is #109")

    def test_a_named_folder_wins(self):
        """Step 1, which `_secrets` could not receive at all — and the only
        step that works in a container."""
        import tempfile
        # **Not skipped off posix.** This asserts that a named folder wins
        # whatever the cascade would otherwise have chosen, which holds
        # wherever `expanduser` finds the sandbox — and it is the step that
        # matters in a container, so it should run on every runner.
        home = self._home(writable_docs=True)
        sec = self._with_home(home)
        named = tempfile.mkdtemp()
        self.assertEqual(sec._workspace(prefer=named), named)

    # ---- the hardening must not take a key away in silence -------------

    def test_a_stranded_credentials_file_is_named_out_loud(self):
        """**The regression this hardening can cause.** Somebody whose keys
        sit in `~/Documents/job_applications/credentials.env` on a Documents
        that is not writable was served before and is not served now: their
        setup works this evening and not after the release, without their
        having touched anything.

        The refusal stands — guessing is what #109 removed — **but it does not
        stand quietly**, and the sentence names the file."""
        self._needs_posix_permissions()
        home = self._home(writable_docs=False, with_keys=True)
        sec = self._with_home(home)
        note = sec.missing_note(["ADZUNA_APP_ID", "ADZUNA_APP_KEY"],
                                "adzuna", "Adzuna", "developer.adzuna.com")
        expected = os.path.join(home, "Documents", "job_applications",
                                "credentials.env")
        self.assertIn(expected, note,
                      "the file that stopped being read is not named — the "
                      "user cannot tell a lost key from a missing one")
        self.assertIn("no longer being read", note)
        self.assertIn("not lost", note)

    def test_it_says_nothing_when_nothing_is_stranded(self):
        """**The witness.** Without it the case above passes on a note that
        cries stranded on every run, which is the noise this avoids."""
        # **A workspace that resolves, and a file sitting in it.** The first
        # version used an unwritable Documents with no file, so the note came
        # back None whether or not the workspace was consulted — it could not
        # tell "checks first" from "does not check".
        home = self._home(writable_docs=True, with_keys=True)
        sec = self._with_home(home)
        self.assertIsNotNone(sec._workspace(),
                             "the fixture must resolve or this proves "
                             "nothing")
        self.assertIsNone(sec.stranded_note("adzuna"),
                          "nothing is stranded — the workspace resolved and "
                          "that file is the one being read")
        note = sec.missing_note(["NOT_A_REAL_KEY"], "adzuna", "X", "y")
        self.assertNotIn("no longer being read", note,
                         "a warning on a healthy install is the noise this "
                         "avoids")

    def test_the_ordinary_guidance_survives(self):
        """A stranded key must not cost the reader the two routes: **telling
        somebody without a shell to run `export` is not help.**"""
        self._needs_posix_permissions()
        home = self._home(writable_docs=False, with_keys=True)
        sec = self._with_home(home)
        note = sec.missing_note(["A_KEY"], "svc", "X", "y")
        for owed in ("credentials.env", "set -a", "config.yml"):
            self.assertIn(owed, note)


if __name__ == "__main__":
    unittest.main(verbosity=2)
