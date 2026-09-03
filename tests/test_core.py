#!/usr/bin/env python3
"""The parsing core, tested without touching the network.

**Sixty-one adapters depend on third-party sites; testing those in CI would
mean sweeping the web on every commit**, which is the thing this project
teaches people not to do. So the perimeter is the pure-parsing core, and every
case here is synthetic. Issue #108.

**Most of these cases already existed — written by hand, run once, and read
afterwards.** `_robots.py`'s group grammar was corrected twice in one day
(#101) against exactly these inputs, typed into a shell. **A case that is not
executed is a comment**, and a comment does not fail when someone changes the
function under it.

Run: `python3 -m unittest discover -s tests -v`
"""

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
        std = set(sys.stdlib_module_names)
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
        self.assertIn("does not answer with structured data", window)


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
        "adzuna.py": "keyed API under the user's own credentials — and "
                     "api.adzuna.com publishes `Disallow: /`. OPEN QUESTION",
        "francetravail.py": "keyed API — api.francetravail.io publishes "
                            "`Disallow: /`. OPEN QUESTION",
        "labonnealternance.py": "keyed API; its host permits. OPEN QUESTION",
        "platsbanken.py": "keyed API; its host publishes no robots.txt "
                          "(404 — absent). OPEN QUESTION",
        "arbeitsagentur.py": "keyed API; the docstring carries a human's "
                             "reading of the file, not a call. OPEN QUESTION",
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

    def test_every_network_reader_asks_the_guard_or_is_listed_with_a_reason(self):
        silent = [name for name, src in self._network_readers()
                  if "_robots" not in src and name not in self.NOT_ASKING]
        self.assertEqual(
            silent, [],
            "these touch the network, never ask the guard, and give no "
            "reason — an absent call reads the same as a decision not to "
            "call: " + ", ".join(silent))

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
    """One case per specimen, each named with the site it came from. #127.

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
        looked at it."""
        v, a = self._verdict(self.APACHE, "text/plain")
        self.assertEqual(v["state"], "unrecognised")
        self.assertIsNone(a["allowed"])
        self.assertFalse(v["certain"])

    def test_a_long_spa_shell_is_not_rules_either(self):
        """Same verdict for the case that was already caught — **the two must
        not depend on which header they carried.**"""
        v, a = self._verdict(self.SPA, "text/html")
        self.assertEqual(v["state"], "unrecognised")
        self.assertIsNone(a["allowed"])

    def test_an_empty_body_establishes_nothing(self):
        """A zero-byte body carries no directive either. RFC 9309 would read
        it as *no rules*; **we cannot tell it from a broken response**, and
        after #125 the empty answer is an unknown."""
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
