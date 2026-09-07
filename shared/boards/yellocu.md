# Board adapter — Yellocu (Cuba): not a job board

<!-- verified: 2026-09-07 -->

<!-- hosts: www.yellocu.com -->
<!-- script: none -->
<!-- countries: CU -->
<!-- content: out-of-domain · the site describes itself as `Local Business Network in Cuba | Online Business Directory`, and its homepage carries 0 occurrences of `empleo`, `trabajo`, `oferta`, `vacante`, `curriculum` or `contratar` · 2026-09-07 -->
<!-- witness: not applicable — nothing here is counted, because the object is not advertisements -->

**Cuba's country page listed this host among its job sources, ranked 5, «ouvert
— à construire». It is a business directory.**

## What it says it is, in its own words

```
<title>       Local Business Network in Cuba | Online Business Directory
description   Business Network in Cuba, Find Companies Near Me, Read Reviews
              and Write Reviews. List Your Business and Expand Your Reach.
```

## What its homepage contains

```
empleo 0 · trabajo 0 · oferta 0 · vacante 0 · curriculum 0 · contratar 0
/company/<n>   12 links
/category/…     Restaurants · Vehicle_services · Doctors_and_Clinics
                Department_stores · Legal_services · Real_estate_agents
                Construction · Hotels · Universities
```

**Not one employment category, and not one of the six Spanish words a Cuban
job site could not avoid.** The rules file opens (`Allow: /` under `*`, with
`/admin/`, `/user/*`, `/sign-in/*` and eleven more refused), so this is not a
refusal and not an access problem: **the object is not advertisements.**

## Why this is a delivery and not a gap

*The guard was open, the host answered, and a reader working from the country
page would have built an adapter and found nothing — or worse, counted company
pages as vacancies.* **`bestzambiajobs.com` is the precedent**: a domain
classified three times in one day from correct measurements taken on the wrong
object.

**The verdict of «is this a board» is taken by fetching, not by guarding.** A
`robots.txt` says nothing about what a host serves today.

*This card does not say Cuba is worse covered than it was.* It says one of
three named hosts was never a source, which makes `cubisima.md` the country's
coverage rather than one third of it.
