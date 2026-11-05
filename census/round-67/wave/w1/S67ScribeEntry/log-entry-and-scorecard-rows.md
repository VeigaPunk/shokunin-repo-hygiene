# LOG.md `## Round 67` entry shape and SCORECARD Round-67 measurements table shape

**STATUS: both were landed by the L1 before this seat delivered** — `LOG.md` §Round 67 and the SCORECARD
`### Round 67 measurements` table, both in `e41f022f0dd018390fa68c7edab1dff734fcfc4f` (2026-11-05
13:48:45 -0300; `LOG.md` +14 lines, `SCORECARD.md` +11 lines).

What this file delivers is: (a) the **entry/table shape** the seat was asked for, shown against the landed
text so the L1 can see the shape is satisfied and where it is thin; (b) the **placeholders the seat was asked to
leave** (measured commit, counting command) filled in from the committed receipts, with the commands this seat
re-ran; and (c) the **two additions** the landed bookkeeping still owes, both grounded in this seat's
measurements.

---

## 1. LOG.md `## Round 67` entry — shape and the landed text

### 1.1 The shape (from the r66 entry, the immediately preceding round)

`LOG.md` is append-only; each round adds one `## Round <n> (<date>, <host>; attempt <n>) — <title>` section
whose bullets run in a fixed order:

```
## Round 67 (2026-11-05, Linux; attempt 1) — <title>

- **Claims (two; frozen at census/round-67/preregistration-attempt4.txt, freeze 4c61efcb…):**
  C1 operability … ; C2 calibration …
- **Freeze chronology (all on this Linux host):** instruments 05eb2cee… ; controls d544e75a… / 832a4d43… ;
  freeze attempts 1–3 superseded; freeze attempt 4 4c61efcb… (`--substance` `claims=2 findings=0`).
- **Wave w1 (10 seats, policy v1 band 8–16; attack share N/10):** …
- **Landed:** candidate tools/souji-receipt-write.py at f70da577… (sha256 b811ee2a…); records … ;
  knowledge entry … ; lesson … .
- **Sources:** S300 … ; registry 222 → 223 rows; census rc 0.
- **Measured residual routes / probes:** …
- **Mistakes (lesson corpus/lessons/round-67.md § Mistakes M1–M10):** …
- **Frontier:** … ; Assimilation: none …
- **Tools:** none installed or upgraded. No pacman transaction. …
- **Scratch:** …
```

### 1.2 The landed entry, checked bullet by bullet

The landed entry's actual bullets (at `e41f022f`; the file has since grown — the current tip is `36200ad8`):

| landed bullet | shape element it carries | present? |
|---|---|---|
| **Claims** (two; frozen at the named prereg + freeze hash) | claims | yes |
| **Freeze chronology (all Linux)** | instruments / controls / attempts 1–4 | yes |
| **Wave w1** (10 seats, policy v1 band 8–16, attack share 5/10, seats named) | wave | yes |
| **Landed** (candidate path, revision, sha256, records, knowledge entry, lesson) | landing | yes |
| **Measured** (C1 after receipt with its rev/instrument digest; C2 after + mutant receipts) | measurements | yes |
| **Named trade (C1, operator ruling needed)** | the trade, named and not folded into the verdict | yes |
| **Corrections (append-only; the frozen files are not edited)** | corrections | yes |
| **Sources** (S300, URL, access date, quote verification method) | sources | yes |
| **Assimilation: none** | assimilation | yes |
| **Tools** (none installed; no pacman transaction; no sysctl/sudo change) | tools | yes |
| **Scratch** (`/fast/scratch/hyaku/souji-r67/`) | scratch | yes |

The r66 entry's bullet set differs slightly (it carries a "Mistakes" and a "Frontier" bullet; the r67 entry
carries "Measured", "Named trade" and "Corrections" instead). Both satisfy the same shape: every element the
r66 shape names is present, with the round's own additions. **The shape is satisfied.**

The landed entry has a **"Corrections (append-only; the frozen files are not edited)"** bullet. That is exactly
where the S298 `used-by` old→new log belongs — the bullet's own convention (a correction logged, frozen files
not edited) is the contract's rule-2 idiom. See §3.1.

---

## 2. SCORECARD Round-67 measurements table — the shape

The shape, copied from the r66 table (`SCORECARD.md`, `### Round 66 measurements (2026-11-05, Linux; base …;
instruments …; controls …; freeze …; prereg …; measured revision …)`) and the r64/r65 tables:

```
### Round 67 measurements (<date>, <host>; base <40-hex>; instruments <40-hex>; controls <40-hex> (C1), <40-hex> (C2);
freeze <40-hex> (attempt 4; attempts 1-3 superseded); prereg census/round-67/preregistration-attempt4.txt;
measured revision <40-hex>)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 <one-line claim> | operability <n> (receipt-binding; Q59 neutral) | <before: the do-nothing/base arm, with its receipt path> | <after: the SUMMARY literal, EXIT, and the receipt path> | <the exact executed counter argv> | <short commit> |
| C2 <one-line claim> | calibration 7 (bookkeeping file) | <before: the r66 counter at the pinned state> | <after: the FINDING + SUMMARY + EXIT> | <the exact executed counter argv, plus the mutant recipe> | <short commit> |

Trend-visible score changes: none (calibration 7, coverage 8, operability 8). <the trade/limit sentence that
must not be folded into the verdict.>
```

The two house rules the shape carries: **every number in the prose appears in the table row** (QUALITY Q10), and
**a trade is named, not counted as an improvement** (the r66 precedent: the honest-run refusal cost was named and
routed to the operator rather than folded into the verdict).

### 2.1 The landed table

The landed `### Round 67 measurements` table (`SCORECARD.md:1678`–`1685` at `e41f022f`) has the required six
columns and two rows (C1, C2), plus the closing sentence:

> "Trend-visible score changes: none (calibration 7, coverage 8, operability 8). C1 and C2 both verify on their
> frozen predicates; C1's named relative-value trade is routed to the operator and not counted as an improvement
> without that ruling."

### 2.2 The placeholders the seat was asked to fill, filled from committed receipts

The seat's item asked for the table shape with "measured commit placeholders". The landed table already carries
the measured revisions; this seat re-derived each number independently and confirms them:

| row | cell | landed value | this seat's independent re-measurement |
|---|---|---|---|
| C1 | before | do-nothing `new_forgeries=2`, `EXIT=1` (`census/round-67/controls/c1-do-nothing.txt`) | re-read from the committed control receipt: `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=2 new_honest=6 class_mismatches=2 regress=PASS`, `EXIT=1`; W1/W2 `base=accept`, W3 `base=accept` ✔ |
| C1 | after | `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0 regress=PASS`, `EXIT=0` | **re-ran the frozen counter against the landed candidate in a scratch clone**: the same literal, `EXIT=0` ✔ |
| C2 | before | r66 counter at `c13fbb4e`: `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0` (`census/round-67/controls/c2-do-nothing-r66.txt`) | re-read from the committed receipt: the same literal ✔ |
| C2 | after | `FINDING SCOPE-OVERREACH s5`; `SUMMARY rows=5 findings=1 verdict=FAIL`, `EXIT=1` | **re-ran the r67 counter at the pinned state in the scratch clone**: `FINDING SCOPE-OVERREACH s5: … needs writer markers cdred; writer blob lacks them`; `MARKERS … envcfg=1 envred=1 cdred=0`; `SUMMARY rows=5 findings=1 verdict=FAIL`; `EXIT=1` ✔ |
| C1 | counting command | the frozen counter argv with `--base-rev 36390879…` | the argv re-run verbatim in the scratch clone; the counter refuses a `--work` under `/tmp`, `/var/tmp`, `$TMPDIR` or inside `--root`, so this seat's work dir was under its own scratch ✔ |
| C2 | kill power | the reverted-rule and enum-weakened mutants | **both re-built by the frozen recipe and re-run**: reverted-rule `--selftest` → `m10-s5-assertion-line-not-live: findings=0 want=1 MISMATCH`, `cases=17 fail=1`, `EXIT=1`; enum-weakened at the pinned state → `findings=0 verdict=PASS`, `EXIT=0` ✔ |

Every number the landed table prints is reproduced by this seat from committed bytes or by re-running the frozen
instruments in a scratch clone. The "before" column's `base_forgeries=2` and `base_honest=6` match the frozen
predicate and the committed do-nothing control.

---

## 3. What the landed bookkeeping still owes

### 3.1 The SCORECARD/LOG do not record the new registry finding

The r67 landing introduced one new K1 registry finding that no gate that ran at landing could see (full
measurement in `sources-rows.md` §3):

```
K1 cited-not-in-used-by S298 corpus/knowledge/common-dir-route-receipt-writer.md
```

At the freeze the K1 arm printed 4 findings (all pre-existing); at the landing and at the current tip it prints
**5** — the fifth is the round's own entry, because the entry's front matter cites S298 while S298's `used-by`
cell was not extended to name it. QUALITY Q62 requires the binding in both directions.

**Recommended addition to the LOG's round-67 entry.** The landed entry already has a
**"Corrections (append-only; the frozen files are not edited)"** bullet — that is the natural home for the
old→new log the SOURCES-CONTRACT-v1 rule 2 requires:

> S298 `used-by`: `corpus/knowledge/caller-env-routes-receipt-writer.md` →
> `corpus/knowledge/caller-env-routes-receipt-writer.md, corpus/knowledge/common-dir-route-receipt-writer.md`
> (the r67 entry cites S298; the correction is a `used-by` cell edit, the only in-place change the contract
> permits). The r67 frontier section's sources bullet in `corpus/README.md:990` ("S298/S299 unchanged") is
> superseded by this line and must be updated too.

**Recommended addition to the SCORECARD round-67 table:** a third measurement row, or an appended line under the
table, recording the registry-agreement arm's before/after at the round's own revisions — the house rule is that
a count carries its command, and the K1 count (4 → 5, and back to 4 after the correction) is a count this round
produced:

```
| C3 registry/entry citation agreement (S298 used-by) | calibration 7 | `K1` findings 4 at freeze 4c61efcb… | 5 at e41f022f… (`K1 cited-not-in-used-by S298 corpus/knowledge/common-dir-route-receipt-writer.md`) | `python3 -B tools/souji-registry-agreement.py --root . --rev REV --list-rev LIST_REV` | 11a96e07 |
```

**Note on the axis:** this is a bookkeeping/registry defect on the calibration surface, not a claim failure —
C1 and C2 keep their frozen predicates and their landed measurements. The correction is one cell.

### 3.2 The M1 "65 hex" narrative mismatch (detail in `lesson-round-67.md` §2)

The landed M1 row's lengths (63 / 62 hex) are correct and this seat confirms them; the frozen attempt-3 and
attempt-4 headers say "65 hex" for attempt 2. The lesson does not record the difference. One addendum sentence
closes it. Not a prereg edit — the prereg is frozen.

### 3.3 The one located-quote row whose raw byte offset differs by 100

`environment.html` @ 189753 matches at 189853 raw; the other 24 rows are EXACT. The Gate's whitespace-normalization
sentence is true; naming the one row closes the disclosure.

---

## 4. Placeholders deliberately left open for the L1

| placeholder | where it belongs | what the L1 must put there |
|---|---|---|
| registry-agreement measurement | SCORECARD round-67 table (or an appended line) | the K1 before/after counts with the command (§3.1) |
| S298 `used-by` old→new log | LOG round-67 (or lesson Gate) | the exact old and new cell values (§3.1) |
| M1 addendum sentence | lesson `## Mistakes` M1 | the "65 hex vs 63 hex" reconciliation (§3.2) |
| quote-offset disclosure | lesson `## Gate` sources bullet | the `environment.html` row and its +100-byte raw delta (§3.3) |
| chronology sweep note | lesson sweep paragraph | the dangling pre-landing commit `5b571380` |

---

## 5. Provenance

| what | how |
|---|---|
| landed LOG/SCORECARD text | `git show e41f022f… -- LOG.md SCORECARD.md` (read-only) |
| r66 shape reference | `git show HEAD:LOG.md`, `git show HEAD:SCORECARD.md`, the `### Round 66 measurements` table (read-only) |
| C1 after | frozen counter re-run against the landed candidate in this seat's scratch clone (`--no-hardlinks` clone; the lane tree was never written) |
| C2 after + both mutants | frozen counter and frozen recipe re-run in the scratch clone; mutants written to this seat's scratch |
| do-nothing / before-arm receipts | re-read from the committed receipts `census/round-67/controls/c1-do-nothing.txt`, `c2-do-nothing-r66.txt` |
| K1 counts | `tools/souji-registry-agreement.py`'s `k1()` called at the freeze revision, the landing revision and the current tip; the correction measured in a fixture repo under this seat's scratch |

**No lane file was edited by this seat.** All lane reads were read-only git plumbing.
