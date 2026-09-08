# Where a false zero would cost most — the 80 nude adapters, ranked

**Ranked 2026-09-08 by `claude-job-hunt-82`, from the 80 class-C adapters of
`adapter-count-discriminant.md`** — those that print no quantity a broken
extraction could contradict. *No new measurement: every input is a card's own
`countries:`, `script:` and `content:`.*

## The criterion, written so someone else can continue the list

```
GATE   is this adapter the ONLY live route to at least one country?
       live = some card declares that country with a script that is not `none`
       -> 21 of the 80 pass the gate; the other 59 fail it and are not ranked

ORDER  what a silent zero would erase:
       (a) the number of countries erased
       (b) the volume erased, from the card's own `content:`
```

**(a) and (b) do not collapse into one number, and this file does not pretend
they do.** *A silent zero on `jobrapide` makes SEVEN countries look empty and
hides 11 advertisements. One on `ihararejobs` makes ONE country look empty and
hides 6 295.* **Both orderings are given; the headline uses volume, because a
country that a board covers with one or two advertisements is barely covered
whether the adapter works or not.**

## The ten where it would cost most

| # | adapter | sole route for | volume hidden | why |
| --: | :-- | :-- | --: | :-- |
| 1 | `ihararejobs.py` | ZW | **6 295** | Zimbabwe has no other declared route |
| 2 | `cubisima.py` | CU | **6 068** | Cuba likewise, and `revolico` is a challenge page |
| 3 | `emploitic.py` | DZ | **4 237** | Algeria's largest private board, exercised today |
| 4 | `ergodotisi.py` | CY | **2 644** | Cyprus |
| 5 | `careerical_sl.py` | SL | **2 344** | Sierra Leone |
| 6 | `todasvagas.py` | MZ | **855** | Mozambique |
| 7 | `keejob.py` | TN | **808** | Tunisia |
| 8 | `jobwebrwanda.py` | RW | **558** | Rwanda |
| 9 | `emploiscongo.py` | CD | **446** | DR Congo — *and its own card calls the corpus a closed archive* |
| 10 | `computrabajo.py` | **BO · CO · PY · UY** | *unknown* | **four countries at once**, and no `content:` line to size it |

**`computrabajo` is placed tenth by the volume rule and FIRST by the country
rule.** *That disagreement is the point of writing both.*

## By countries erased instead

```
jobrapide.py     7   BJ · CG · CM · ML · MR · SD · SN     volume 11
computrabajo.py  4   BO · CO · PY · UY                    volume unknown
every other      1
```

**`jobrapide` heads that ordering and is 12th by volume**, holding 11
advertisements across seven countries. *Which of the two matters is a judgement
about what coverage means, and it is the owner's to make rather than mine.*

## Nine of the 21 cannot be ordered at all — declared as tied

**They carry no `content:` line, so dimension (b) has no value.** *They are not
ranked below the ten above; they are unranked.*

```
computrabajo · glmis · jobam · jobbkk · jobsbotswana
jobsgovpk · mihnati · mycareer · vieclam24h
```

*Sizing them costs one exercise each and would change this order — `jobbkk`
(Thailand), `vieclam24h` (Vietnam) and `mihnati` (Saudi Arabia) are large
markets whose volume is simply not written down.*

## What this ranking does not establish

**A volume is the BOARD's, not the country's.** *`myjobsfiji.py` is the sole
declared route to the Solomon Islands and its 190 is a Fiji count; how much of
it is Solomon Islands is not written anywhere.* **It is excluded from the ten
for that reason**, not for being small.

**"Sole route" is read from `countries:` declarations, not from the world.** *A
country with no card at all — Afghanistan until today — has zero routes and does
not appear here.* **This ranks the risk inside our coverage, not the gaps in
it.**

**The gate was checked both ways.** *`ihararejobs`/ZW is the only card declaring
Zimbabwe; France has 15 class-C adapters and none is flagged sole.* *And one
check of mine was wrong before the data was: a `grep -l 'SB'` matched the
substring in two cards that declare `DE` and `DE AT CH`, which would have
removed a true sole route had it not been read.*
