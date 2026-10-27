# AttackE18 — adversarial falsification of W1's C1 item E18 finding

Seat: SwarmReviewer16 · Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · Read-only; no frozen artifact altered.

## Status

**W1's finding CONFIRMED — reproduced independently; the proposed blockage/correction is valid and is the unique rule-conforming route.** The base do-nothing MISMATCH, the cause bracket, and the restatement acceptance were all re-executed by this seat. Two report-level defects found in W1's deliverable (a false exit-code claim and an env/trace inconsistency); neither changes the verdict. During this probe the builder landed adac8bb implementing exactly W1's row; the frozen counter reads **AGREE, exit 0** at the new tip.

## Evidence

All revisions full-40: base `9c76c7222a8abff027af42e37f0d160d52526bba`, list-rev/prereg-repair `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`, cause `728b2ce71acbe574ae3036b456724d0a3d6f8f08`, cause parent `679e2d02f46ec06447d679d9395d6592c5e35f5c`, r24 receipt rev `778747eb671f8e85ef5387bc3d7023337b30467c`, W1-time tip `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`, new tip `adac8bbc79a7ed77b632b309e70fd2a91b45dbd9`.

1. **Base do-nothing arm (REPRODUCED).** Frozen item row (`census/round-34/c1-items.tsv:62`, byte-identical at list-rev): `E18 / SCORECARD.md:71 / exit 0 / pred "selftest=PASS ids=5/5" / files tests/fixtures/r13-repo-structure.sh,tools/souji-repo-structure.sh / argv bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh`.
   ```
   python3 -B census/round-34/c1-counter.py --root <lane> --rev 9c76c7222a8a… \
     --list-rev 2b0171e2071f… --scratch /fast/scratch/hyaku/souji-r34/E18/cnt --only E18
   → ITEM  E18  MISMATCH  original  rc=0 expect_exit=0 predicate fails last=selftest=PASS ids=7/7 load=1.15
   → SUMMARY items=1 agree=0 mismatches=1 restated=0 partial=1 rev=9c76c7222a8a… ; exit=1
   ```
   Exit matches, predicate does not — W1's verdict line reproduces verbatim. (Note `exit=1`, see Finding 2.)

2. **Cause bracket (REPRODUCED)** — one `--no-local --no-checkout` scratch clone, `env -i PATH=/usr/bin:/bin TMPDIR=<fresh> GIT_CONFIG_NOSYSTEM=1 HOME LANG=C.UTF-8`:
   - parent `679e2d02f46e`: rc=0, fixture sha256 `b6bf52056d037b22…` — byte-identical to the pin in the cell's own receipt `census/round-24/records/r13-recheck-receipt.tsv` (`tool_sha256=b6bf5205…`, `selftest=PASS ids=5/5`) — last line `selftest=PASS ids=5/5`, **0 digit-bearing lines after it**;
   - cause `728b2ce71acb`: rc=0, fixture sha `eabc5f0ac56ea3db…`, adds `id=SOUJI-R13-STRUCT-linked-common-dir` and `id=SOUJI-R13-STRUCT-colocated-vs-plain`, last line `selftest=PASS ids=7/7`, **0 digit-bearing lines after it**;
   - tool `tools/souji-repo-structure.sh` sha `80025137b20d5a61…` unchanged across the bracket — the drift vector is the fixture alone;
   - `git merge-base --is-ancestor 778747eb… 679e2d02…` → true: the r24 receipt (5/5) predates the growth, so the cell was true when written and stale only after `728b2ce`.
   The fixture's commit diff at `728b2ce` renumbers the header comment `ids=5/5` → `ids=7/7` (`--probe` mode) exactly as W1 described.

3. **Cause-commit gates (REPRODUCED).** `git show --name-only 728b2ce` = 181 paths, includes `tests/fixtures/r13-repo-structure.sh` (satisfies the run=same gate at `census/round-34/c1-counter.py:287`); full-40; `git merge-base --is-ancestor 728b2ce… 2b0171e2071f…` → true. File history of the item's two files at base is exactly `{6ed10a7, 728b2ce, 98e5203}` (git log --reverse), so W1's enumeration was complete.

4. **Q76 — no carry (REPRODUCED).** `git grep -n -F "SCORECARD.md:71"` over the whole base tree: only `.ufo/waves/round-16/w2/ConnScorecard2.md:48` (unrelated r16 note) and `census/round-33/waves/w1/deliver-c1-enumeration-misses.md:31` (an r33 *exclusion* row, see Finding 5). No correction row binds `:71`; `### Round 34 registry restatements` is absent at base; SCORECARD.md is byte-identical base..list-rev (diff empty). Structurally, the frozen counter implements no runtime Q76 carry for in-list items: `judge` reads restatements keyed by item id under SECTION only (`c1-counter.py:93-107`, `:245-247`), and `:155`/`:42` are Capabilities/measurement rows outside the r34 surface per the prereg surface clause — so K04 (SCORECARD.md:502) and R30-CORRECTION (SCORECARD.md:325) cannot make E18 AGREE. The counter's own base MISMATCH (item 1) is the machine proof.

5. **Corroborating history (READ, not executed).** `census/round-33/waves/w1/deliver-c1-enumeration-misses.md:31` excluded this very cell under r33's binding clause ("outcome in a different cell … NO (superseded by E13/r25; K04 is the same stale 5/5)"), and its line 92 records the same drift observed at 2d9bca5 (E18: ids=5/5 vs 7/7). That exclusion rode r33's "immediately followed" clause, which round-34 replaced with the hardened LAST-digit-bearing-line semantics; it is non-binding context for the frozen r34 list and independently corroborates the defect.

6. **Landed bytes (REPRODUCED).** Tip moved `51acb5f` → `adac8bb` ("round-34: append executed C1 restatements") during this probe; it appends the section and `| E18 | SCORECARD.md:71 | restated | 0 | same | `selftest=PASS ids=7/7` | 728b2ce71acb… | r25 added two passing repo-structure probes… |` — substance-identical to W1's proposed row. Counter at tip:
   ```
   ITEM  E18  AGREE  restated  rc=0 expect_exit=0 statement is the run's last digit-bearing line last=selftest=PASS ids=7/7 load=1.81
   SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=adac8bbc79a7… ; exit=0
   ```
   AGREE also machine-proves the row is unique under the section (a duplicate is BAD-ROW at `c1-counter.py:246`).

## Findings

1. **[CONFIRMED — reproduced]** The base defect is real: `SCORECARD.md:71` states `selftest=PASS ids=5/5`; the row's own argv at base exits 0 and prints `selftest=PASS ids=7/7` as its collapsed LAST digit-bearing line. Cause `728b2ce` is valid under the frozen executed-cause rule (holds at parent, fails at cause, touches an item file, ancestor of list-rev). The restated statement is forced, not chosen: A1(c) requires equality with the run's collapsed last digit-bearing line (`c1-counter.py:312`), leaving exactly `selftest=PASS ids=7/7`. W1's correction is the unique rule-conforming fix.

2. **[W1 REPORT DEFECT — reproduced]** W1's deliverable claims "Exit 0 (the counter exits 0 because every listed run completed; the item verdict is MISMATCH)". False for the frozen bytes: `c1-counter.py:397` `return 0 if mism == 0 else 1` — any MISMATCH forces exit 1. Measured exit on the same invocation: **1**. Verdict-irrelevant (the ITEM/SUMMARY lines are the claim), but the stated observation does not match the frozen instrument.

3. **[W1 REPORT DEFECT — cosmetic, source-level]** W1 quotes exec env `env -i … TMPDIR=<fresh> …` yet its captured lines show `fixture_repo=/var/tmp/souji-r13-repo-structure.AA8fuu/repo`. The fixture honors TMPDIR when set (`tests/fixtures/r13-repo-structure.sh:189`, `mktemp -d "${TMPDIR:-/var/tmp}/…"`; `/var/tmp` is only the unset fallback), so those lines came from a run with TMPDIR unset — the quoted env and quoted output are mutually inconsistent. Transcription-level; the counter's own env is hermetic either way.

4. **[NO MISSED ROUTE]** Every alternative under the frozen rules is machine-refused or vacuous:
   - Q76 carry via K04/R30-CORRECTION: refuted by the counter itself (base MISMATCH; no runtime carry — Finding/Evidence 4).
   - Cause `6ed10a7`: fixture absent at its parent → run fails → `holds` False → BAD-CAUSE. Cause `98e5203`: W1's negative control printed BAD-CAUSE(parent=False, cause=False); this seat adds that the frozen rule requires only the executed bracket, so W1's extra "first failing commit" proof exceeds the rule rather than missing anything.
   - RESULTS:-form restatement: the fixture emits no `RESULT ` lines (observed full stdout), `:0` is the frozen junk construct (prereg junk controls / A4), so no valid RESULTS row exists.
   - Argv correction: pointless (frozen argv already runs the row's own script) and A1(b)-risky; `same` is the only sound run cell.
   - Exit cell: run rc is 0 at base; `0` is the honest and accepted value (`re.fullmatch(r"-?\d+|\*")`, `c1-counter.py:258`).

5. **[TIMING NOTE]** W1's L1 note ("heading does not yet exist in SCORECARD.md … no match at tip") was accurate at its read time (tip `51acb5f`, section absent) and is now superseded: `adac8bb` appended section + E18 row during this probe; counter reads AGREE exit 0 at tip. W1's L1 instruction ("append together with the row") was correctly followed by the landed bytes.

## Attack log

1. Read frozen prereg (`census/round-34/preregistration.txt`), frozen row (`c1-items.tsv:62`), W1 deliverable (`.ufo/waves/round-34/w1/deliver-c1-E18.md`), base SCORECARD rows :42/:71/:155/:325/:371/:502.
2. Pinned counter identity: working-tree `c1-counter.py` sha256 `1ad8c86c9d78b79f…` == `git show 2b0171e:…` (prereg A6 re-pin); read `judge`/`run_item`/`load_restatements`/`main` for the exact A1(b)/(c), cause, and Q76 semantics.
3. Probe A (counter, base, --only E18) → MISMATCH, exit 1. Probe B (Q76 sweep, whole base tree) → no `:71` binding; SECTION absent; r33 exclusion note found.
4. Probe C (cause bracket, one scratch clone, parent+cause) → 5/5 vs 7/7, rc 0 both, zero trailing digit lines, fixture/tool shas as above; receipt-rev ancestry and SCORECARD base..list-rev identity verified.
5. Discovered tip movement mid-probe (`adac8bb`); re-ran counter at new tip → AGREE, exit 0.
6. Scratch hygiene: transient 148M clone trimmed; remaining probe artifacts 12K (`/fast/scratch/hyaku/souji-r34/E18/out.<rev>`, `err.<rev>`); no lane file written; no frozen artifact altered.

Residual gaps: the bracket probe ran without the counter's optional jj symlink dir (the fixture invokes `git` only — inference from source inspection; the two counter runs exercised the real env and are authoritative). Fixture executed 4× total, hermetic (trap cleanup, `r13-repo-structure.sh:192-193`); no residue left outside scratch.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE18.md` — this report.
- `.ufo/waves/round-34/w2/SwarmReviewer16.md` — scoped seat findings (same verdicts, condensed).
