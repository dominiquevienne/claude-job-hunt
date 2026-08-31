# Board adapter — Cegid Talentsoft

Talentsoft, now part of **Cegid**, runs the careers sites of large French
employers and public bodies — ministries, airports, energy, publishing,
agencies. It is the **fifth and last** of the French ATS family here, after
`taleez.md`, `flatchr.md`, `softy.md` and `digitalrecruiters.md`.

**Everything here was verified against the live site on 2026-08-31.**

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
any redesign. **Anchor on the ids and on the `<h2>` section names**
(`JobDescription`, `Location`, `ApplicantCriteria`), never on presentation
classes.

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

No login, no account, no API key. **No directory exists** — ask the user for the
careers URL, as for every ATS here.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/talentsoft.py" \
  jobs --tenant businessfrance-recrute --with-detail
```

`robots.txt` on the tenant sampled is **HTTP 200 with zero bytes** — an empty
file, which is a valid "everything allowed", and distinct from a 404.

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

**1. The location is not always an address, and a postcode rule silently drops
the overseas jobs.** The first parser here matched a French five-digit postcode
and filled `location` on 10 of 19 ads. The other nine were real and fine —
*Bureau Business France à Bombay*, *New Delhi* — postings abroad with no French
postcode. A public agency, an airport group or a ministry will all have some.
The row's fields are unlabelled fragments in a fixed order, so the parser
identifies the title, reference, date and contract by pattern and takes **what
is left** as the location. That fills 19/19.

**2. The listing row starts inside its own opening tag.** The block is cut at
`class="ts-offer-list-item offerlist-item`, so flattening it puts leftover
attribute text — `class=… title=… onclick=…` — where the title should be. Taken
positionally, every title on the board becomes a fragment of HTML that *looks
like data*. The title comes from `ts-offer-list-item__title-link` instead.

**3. A wrong tenant is a DNS failure, not a 404.** The host simply does not
exist, so the error arrives from the resolver. Passed through, it reads as a
network problem; it is a typo in the one value the user supplied. The script
says so.

**4. The ad page ends with other people's ads.** A *"Ces offres pourraient vous
intéresser"* block carries `ts-offer-card__title-link` links to unrelated
postings. Harvesting ad links from a detail page therefore pulls in ads that
are not related to it — collect links from the **listing** only.

**5. There is no expiry date**, as on all four other French ATS. Freshness comes
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
