# Board measurement — goafricaonline.com (Gabon): the name answers, and what it serves is a business directory

<!-- verified: 2026-10-27 -->

<!-- hosts: goafricaonline.com, www.goafricaonline.com -->
<!-- script: none -->
<!-- countries: GA -->
<!-- route: none · non faisable — « sort du faisable », décision du propriétaire du 26.10.2026, par OBJET et non par classe (§2 sexies) — measured 2026-10-27: unlike the two hosts closed by the SAME decision, this name RESOLVES (NOERROR on both 1.1.1.1 and 8.8.8.8, apex AND `www.`), its `robots.txt` reads 200 with no `Disallow` on our path, and the sitemap index it declares enumerates 739 `<loc>` over 137 countries under EXACTLY FIVE file names — `companies.xml` 321, `categories.xml` 138, `pages.xml` 138, `shoppings.xml` 137, `cms.xml` 5 — and not one of them is a job file; Gabon's five are categories, shoppings, pages and companies ×2. A business directory, not a board · 2026-10-27 -->
<!-- witness: 2 HTTP requests, both 200, as Claude-User — `https://www.goafricaonline.com/robots.txt` 343 o md5 a2266f99d536 at 06:10:20Z, and `https://goafricaonline.com/sitemap.xml` 90 678 o md5 e25e36e9fc2c at 06:10:44Z; the sitemap lives on the APEX and the rules on `www.`, so the guard was taken twice, on each exact host · 2026-10-27 -->

**This card closes a host that answers.** *Its two companions under the same
owner decision — `bestjobs.mg` and `emploimali.com` — are NXDOMAIN, so nothing
could be asked of them. Here everything could be asked, it was, and the answer
is that this is not a job board.*

## Step 1 — the rules were READ, and they do not refuse us (2026-10-27 06:10:20 UTC)

```
www.goafricaonline.com/robots.txt   HTTP 200, 343 o   state: read, certain: True
user-agent: *   disallow: /api/*  /graphql*  /ajax/*  /event-stats/*  /switch_to_mobile*
Sitemap: https://goafricaonline.com/sitemap.xml      <- the APEX, not the `www.` host
```

**Nothing in those rules touches a listing path**, so this card is not a
refusal of any kind: neither borne 1 (`Disallow` on our path), nor borne 0
(a transport refusal), nor a challenge. *And the declared sitemap lives on a
DIFFERENT host from the rules that declare it, so the guard was taken again on
the apex — `robots.txt` binds a HOST, not a brand.*

**And there is no `Crawl-delay` anywhere in those 343 bytes, which is a fact
about US and not about the host.** *A file that writes its delay tells us how
to respect it; a silent file does not tell us there is none — and the only way
to learn where an unwritten threshold sits is to cross it, so we do not learn
it.* **The cadence here would therefore be ours to set, and nothing was
marched: two requests, forty-four seconds apart, and no listing was walked.**

## Step 2 — the sitemap index enumerates what the site is, and it is not employment

```
739 <loc>, raw count and extracted count AGREE (so no CDATA, nothing dropped)
137 countries, and FIVE file names cover all 739 :
     321  companies.xml      138  categories.xml      138  pages.xml
     137  shoppings.xml        5  cms.xml
Gabon (/ga/) : categories · shoppings · pages · companies?page=1 · companies?page=2
```

**This is an ENUMERATION and not a search for an absence, and the difference is
the whole measurement.** *Asking «&nbsp;does it say `job`, `emploi`,
`recrutement`&nbsp;?&nbsp;» returns zero for six retyped patterns, and a zero
obtained that way cannot tell «&nbsp;there is none&nbsp;» from «&nbsp;I asked
badly&nbsp;».* **Listing every file name the index carries answers without
asking anything: five names, all of them businesses, categories, pages, shops
and CMS content.** *A first attempt to classify them returned `(index)` for all
739 — the pattern captured nothing — and it is not published here.*

## What this card does not say

**It does not say the operator declared anything.** *The third form of refusal
validated in class on 06.10.2026 is «&nbsp;an operator who declares its own
platform closed or unavailable&nbsp;», and this operator declares nothing: the
platform is alive and serving. What closes this host is the owner's decision of
26.10.2026 on this OBJECT, and the measurement above is its reason, not its
authority.*

**And it does not say anything about the 136 other countries the index
declares.** *`countries:` carries GA alone, because GA is what was asked and
what the Gabon page names; the index covering 137 countries is recorded here
and claimed nowhere.* **A card that claimed 137 would add this host to 137
denominators on the strength of one page's question.**
