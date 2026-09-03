# Board adapter — Cegid Talentsoft

**Talentsoft and DigitalRecruiters are Cegid, and the old domains no longer
publish rules of their own.** Measured 2026-09-03:

```
talent-soft.com/robots.txt        → https://www.cegid.com/global/      (HTML)
digitalrecruiters.com/robots.txt  → https://www.cegid.com/fr/produits/… (HTML)
www.cegid.com/robots.txt          → 200, 1 006 bytes, text/plain
```

**A request for the old host's rules file lands on a marketing page**, so it
reads `unreadable` — and *"unreadable" reads as a server accident when it is an
acquisition.* **The rules that apply are Cegid's, they exist, and they are at
that platform's own root**, which nothing pointed at: the redirect goes to a
product page, not to the equivalent path.

Cegid's file is a WordPress default extended by hand — two `User-agent: *`
records, `/wp-admin`, `/*?s=`, feeds — and **refuses nothing this adapter
reads**. `<tenant>.talent-soft.com` answers for itself and is unaffected.

*(Two `User-agent: *` records in one file is the case `_robots.py` merges per
RFC 9309, rather than letting the first win.)*

<!-- verified: 2026-09-02 -->

<!-- hosts: talent-soft.com -->
**Re-verified 2026-09-02** on the tenant-directory question, with the search
recorded below rather than its conclusion.

Talentsoft, now part of **Cegid**, runs the careers sites of large French
employers and public bodies — ministries, airports, energy, publishing,
agencies. It is the **fifth and last** of the French ATS family here, after
`taleez.md`, `flatchr.md`, `softy.md` and `digitalrecruiters.md`.

**Everything here was verified against the live site on 2026-08-31, on two
tenants** — `businessfrance-recrute` (19 ads) and `place-ep-recrute`
(**51 708**). The second is where most of the traps below came from: one tenant
was not enough to write this file.

## Old-school, and better for it

Careers sites live at `https://<tenant>.talent-soft.com/`, where the tenant
label usually ends in **`-recrute`** or **`-career`**:
`businessfrance-recrute`, `groupeadp-recrute`, `ministereinterieur-career`.

Everything is **server-rendered ASP.NET** — `__VIEWSTATE` and all. There is no
JSON API, no `__NEXT_DATA__`, and **no JSON-LD anywhere**, on the listing or the
ad. So this adapter parses HTML, which is normally the fragile choice.

Here it is not, because the ad pages carry **Talentsoft's field model as
element `id`s**:

```
id="fldjobdescription_jobtitle"       id="fldapplicantcriteria_educationlevel"
id="fldjobdescription_contract"       id="fldapplicantcriteria_experiencelevel"
id="fldjobdescription_professionalcategory"
id="fldlocation_location_geographicalareacollection"
```

Those names come from the platform's data model, not from a theme, so they hold
across tenants and across restyling — the opposite of the Tailwind utility
classes on `softy.md` and `cadremploi.md`, which mean nothing and change with
any redesign.

**But stable as a *name* is not stable as a *meaning*.*
`fldjobdescription_professionalcategory` reads `Cadre` on Business France and
`Vacant` on the public-service tenant, which uses the field for the post's
vacancy status instead. Use the ids to find the values; never assume what a
value means across tenants.

**Anchor on the ids and on the `<h2>` section names**
(`JobDescription`, `Location`, `ApplicantCriteria`), never on presentation
classes.


## `other_fields` is the one field here that does not name its contents

**The card enumerates everything it emits — except this one, on purpose.**
`shared/boards/README.md` requires an adapter to name what it emits; this file
is the exception it allows, and the reason is measured: a row's fragments are
unlabelled and **what they are varies by tenant**. Business France puts an
address where `place-ep-recrute` puts a public-service status phrase, and
taking "whatever is left" as the location once produced *"Emploi ouvert aux
titulaires et aux contractuels"* in a location field — a well-formed, entirely
wrong answer.

So the card labels only what it can identify with confidence and hands the rest
back **unnamed rather than mislabelled**. Two things keep that honest: the
carry-over is **capped at `MAX_FIELDS`**, and it holds only text a visitor sees
on the card. **A field this adapter cannot name is better as an unnamed string
than as a wrong label** — but it is the only one, and it is listed as such in
`bin/emit-audit.py`. Issue #75.

## Configuration

```yaml
boards:
  talentsoft:
    enabled: true
    tenants: ["businessfrance-recrute"]
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `tenants` | yes | The careers host's **first label**. One employer each |
| `lcid` | no | Locale id; `1036` is French, and the default |

No login, no account, no API key.

**No tenant directory was found. Searched 2026-09-02:**

| Looked at | Answer |
| :-- | :-- |
| `talentsoft.com/robots.txt`, `www.talentsoft.com/robots.txt` | **200 but 379 KB of `text/html`** — Cegid's product page, not a rules file |
| `talent-soft.com/robots.txt` | 200, 268 KB of `text/html` — the same shape |
| `www.talent-soft.com` | does not resolve |
| `www.cegid.com/robots.txt` | a real file, 1 006 bytes — WordPress paths only, **no customer index, no sitemap of tenants** |
| `<tenant>.talent-soft.com/robots.txt` | **200 `text/plain`, 0 bytes** — an empty file, so nothing is disallowed and nothing is advertised |
| `<tenant>.talent-soft.com/sitemap.xml` | **404** |

**Three of those are the trap this repository keeps meeting**: a `200` in
`text/html` where `text/plain` was expected is not a `robots.txt`, and a
vendor domain that redirects everything into a marketing page answers every
question with the same page. Read the `Content-Type`.

Nothing found is not the same as nothing existing — **this records the search,
not a proof**. Ask the user for the careers URL, as for every ATS here.

*(The vendor is Cegid, and `digitalrecruiters.md` is the other half of the
same acquisition. Its own search turned up a `403` on a plausible listing
endpoint, so if a directory ever surfaces it will probably be a Cegid one
covering both products.)*

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/talentsoft.py" \
  jobs --tenant businessfrance-recrute --with-detail
```

`robots.txt` on the tenant sampled is **HTTP 200 with zero bytes** — an empty
file, which is a valid "everything allowed", and distinct from a 404.

### choisirleservicepublic.gouv.fr is this adapter

The French state's public-service job portal — ex-Place de l'emploi public — is
a Talentsoft tenant: **`place-ep-recrute`**. Nothing on the portal says so; the
giveaway was an RSS link in its page source. **It needs no separate adapter.**

Three things specific to it:

- **51 708 ads at 50 per page**, so a full sweep is over a thousand requests.
  It is not a board to read whole — screen or filter first. `--max-pages`
  defaults to 50, and the script reports how many of the announced total it
  actually collected rather than implying it got them all.
- **The canonical public URL is the portal's, not Talentsoft's**:
  `https://choisirleservicepublic.gouv.fr/offre-emploi/<reference>/`, built from
  the ad's `reference` (`2026-2395447`). Hand the user that one — it is the
  address the employer publishes.
- **A freshness feed exists**: `/handlers/offerRss.ashx?LCID=1036` returns the
  **20 most recent** ads, with per-contract and per-domain variants. Twenty, not
  the board: useful for *what is new since yesterday*, useless for enumeration.

## The ad id and its URL

The id is the numeric suffix of the ad's path — `…_1563.aspx` → `1563`. It is
**per tenant**, not global, so the ledger key carries the tenant:

```
talentsoft:<tenant>:<id>
```

The employer's own `reference` (`2026-1563`) is carried too, but it is theirs,
not a key.

## What the listing gives — which is unusually much

Measured across Business France's 19 ads, **every field on every ad**:

| Field | Example |
| :-- | :-- |
| `title` | Chef(fe) de projets IT - solutions low code & IA H/F |
| `reference` | 2026-1563 |
| `published` | 25/08/2026 |
| `contract` | CDI |
| `location` | **77 boulevard Saint-Jacques 75014 Paris** |

**A full street address on the listing** is rare — most boards make you open the
ad to learn where the job is, and many never say. Only `digitalrecruiters.md`
does the same among the French ATS.

Pagination is `?page=N&LCID=1036`, ten ads a page, and the header states the
total: 10 + 9 = 19, with no overlap.

`--with-detail` adds, from the ad page: `description` (3 311 characters on the
one measured), `professional_category` (Cadre / Non Cadre), `job_family`,
`geographical_area` (*Europe, France, Ile-de-France*), `education_level` and
`experience_level` — **19/19 on all of them**.

## Traps

**1. The row's fields are unlabelled, and what they *are* varies by tenant.**
Business France: title, reference, date, contract (`CDI`), address.
`place-ep-recrute`: title, reference, date, a **status** phrase — *"Emploi
ouvert aux titulaires et aux contractuels"* — an address, **and the employing
body**. Same markup, different meanings, different count.

Two parsers failed here in the same well-formed way before this one held:

- Matching a French postcode filled `location` on 10 of 19 Business France ads
  and left nine blank. Those nine were *Bombay*, *New Delhi*, *Montréal*,
  *Houston* — real ads with no French postcode.
- Taking **whatever was left** fixed that, and then put *"Emploi ouvert aux
  titulaires et aux contractuels"* into the location field of the entire public
  service board. Fifty-one thousand ads, a location that is not a location, and
  nothing anywhere reporting a problem.

So the parser now **labels only what it can identify** — the reference, the
date, a contract matching known vocabulary, an address carrying a French
postcode — and hands everything else back in **`other_fields`**, in order,
uninterpreted. An unnamed string is better than a wrong label. On the
public-service tenant that means `contract` is empty on all 50 and `location`
on 19; the rest are foreign postings (*Ambassade de France au Japon*) sitting
in `other_fields` rather than invented.

**1b. `Vacant (45823)` is not a postcode.** That tenant's status field carries a
bracketed id, and a bare five-digit rule made it the job's location. The rule
now rejects digits in brackets. Three variants of one mistake in a single
adapter is why the design is now *refuse to guess*.

**2. The last row on every page swallows the footer.** Blocks are cut at the
next row marker, so the final one runs to the end of the document and collects
the sidebar filters, the pagination and the legal links — thirty extra fields on
the last ad of every page, all `<li>` elements indistinguishable from the row's
own. They cannot be cut by structure, so the parser takes a **bounded number of
fields** (`MAX_FIELDS`): the real ones come first, the furniture does not.

**3. The listing row starts inside its own opening tag.** The block is cut at
`class="ts-offer-list-item offerlist-item`, so flattening it puts leftover
attribute text — `class=… title=… onclick=…` — where the title should be. Taken
positionally, every title on the board becomes a fragment of HTML that *looks
like data*. The title comes from `ts-offer-list-item__title-link` instead.

**4. A wrong tenant is a DNS failure, not a 404.** The host simply does not
exist, so the error arrives from the resolver. Passed through, it reads as a
network problem; it is a typo in the one value the user supplied. The script
says so.

**5. The ad page ends with other people's ads.** A *"Ces offres pourraient vous
intéresser"* block carries `ts-offer-card__title-link` links to unrelated
postings. Harvesting ad links from a detail page therefore pulls in ads that
are not related to it — collect links from the **listing** only.

**6. There is no expiry date**, as on all four other French ATS. Freshness comes
from the listing's own publication date, which — unlike
`digitalrecruiters.md` — is there without opening the ad.

## Applying

The apply flow is on the tenant's own site and requires a candidate account.
**The plugin does not create accounts and does not fill credential fields.**
Hand the user the ad URL with their documents.

## Pace, and the note on access

Two requests for a 19-ad employer, plus one per ad with `--with-detail`, spaced
by `--delay` (default 1s). These are public careers pages served as HTML, read
unauthenticated, for one person's job search.
