# Board adapter — Mihnati (Saudi Arabia)

<!-- verified: 2026-09-03 -->
<!-- hosts: www.mihnati.com -->
<!-- script: mihnati.py -->

A Saudi job board running on Rozee's platform, **and the platform shows
through in ways that change the data.**

```
GET /EN/                   → 17 advertisements, server-rendered
GET /EN/<slug>-jobs-<id>   → one advertisement, with a JobPosting
```

## The rules refuse families, not the site — so the check is per path

`robots.txt` closes 17 path families. **The Arabic board is refused while the
English one is open**: `Disallow: /ar/` and `/EN/ar/`, alongside `/hiring/`,
`/people/`, `/UR/` and `/ZH/`. A host-level check passes and misses every one
of them, which is why the adapter calls `allowed(host, path)` before each
request and exits **7** naming the rule.

## 17 advertisements, and that is not the board

`/EN/category/<x>`, `/EN/channel/<x>`, `/EN/search/<x>` and `/EN/job/jsearch/`
all answer **200 with 200–460 kB and zero advertisement links** — the results
are drawn by script. So `latest` returns the seventeen the home page carries
and **says they are seventeen**. Reading the rest needs a browser, and the
adapter does not pretend otherwise.

## Three things the `JobPosting` gets wrong — ten of ten ads, 2026-09-03

**The currency is `PKR` on Saudi jobs.** Ten of ten — Jeddah, Riyadh, Sharurah,
`addressCountry: SA` — publish `baseSalary.currency: "PKR"`. Pakistani rupees,
from the platform underneath, the same one this host's own `robots.txt` names
in `/rozee-a/` and `/rozee-b/`. **A row copying that field would price a Saudi
salary in the wrong currency by roughly a factor of seventy.**

`salary_currency_disagrees_with_country` travels beside the value and **no
figure is converted**: guessing the intended currency would be a second
invention on top of the first.

**`identifier` holds the employer's name.** Ten of ten:

```json
"identifier": {"@type": "PropertyValue", "name": "Ansaaj"}
```

The schema.org field for the posting's id carries the company. **An adapter
reading it as an id would key every advertisement by its employer**, and two
jobs at one company would collide in a ledger. The id is the number at the end
of the URL; nothing else is used, and the field is emitted under a name that
says what it actually contains.

**Every page carries the `JobPosting` twice.** Ten of ten, byte-identical.
`_ldjson.postings()` returns both — correctly, it reports what is there — so
the adapter takes the first and **counts the duplication rather than letting
it double a total**.

## Salary, counted on the figure

`baseSalary.value.value` is populated on every advertisement and reads
`Confidential` when nothing was published — **the same shape as EmployTT's
`Concealed`**. Counting keys would report 100% disclosure. Counted on whether
a digit is present.

## The 404 announces itself in the query string

`/jobs` and `/sitemap.xml` answer **200** after redirecting to
`/site/error?e=cnf_jobs` and `?e=cnf_sitemap.xml`. Another *200 with the wrong
body* — but this one needs no guessing at body shapes, because the final URL
names the missing controller.
