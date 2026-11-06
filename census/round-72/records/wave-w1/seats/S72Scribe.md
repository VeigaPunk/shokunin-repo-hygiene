S72Scribe — souji round 72 (scribe: lesson draft + pointer check). Base 0bf098dd; freeze 23372f36; candidate 06df4f97; after-arms 2ec8b63. All evidence read at 2ec8b63; no lane file edited (<40 lines).

Routed items (verdict | deciding bytes)
- D1 report wording: PARTLY — preregistration.txt:22-23 freezes the candidate's non-existence; `.ufo/reports/round-72/` absent (report pending); the four controls read the r71 harness/counter or its committed variant, none reads an r72 counter/matrix byte (controls/*.txt:1-3).
- D2 / (a) base slot: CLOSED — c1-counter.py:1238-1239,1291-1299; records/c1-Y6-main-arm.txt:164-165 (`base_mismatches=10`, `EXIT=1`), re-executed variant reproduces it; honest arm c2-honest-writer.txt:164-165 (`0`, `EXIT=0`), re-executed.
- D3 measurement gap: PARTIAL — FW rows matrix:72-76 + battery 5/5 (c2-after-battery.txt:159,312,465,618,771,772); ident/working-tree-encoding and checkStat/trustctime have no row/member (`grep -in 'ident|encoding|checkStat|trustctime'` on both matrices → 0) and are not in the limits (preregistration.txt:115-121); over-refusal open.
- D4 clean_env: CLOSED — c1-after.txt:19 (`Z1 … fate=killed`); c1-counter.py:1792; counter-selftest.txt:48-49.
- D5 / (h) cross-lane: OPEN — no r72 artifact (grep → 0 files).
- (b) CLOSED as a survivor — c1-after.txt:15 (Y4 killed), counter-selftest.txt:44; (c) CLOSED — c1-after.txt:14,17, counter-selftest.txt:46-47; (d) W3/W4/W5/W6/W8 CLOSED, W7 OPEN (preregistration.txt:36); WM7 reachability not probed in r72 (no WM7 member; matrix row `W7` at :48 is the unrelated `git-dir-redirect-hides-mode` row); (e) OPEN; (f) OPEN — harness frozen, and `rev=` has three referents (c1-after.txt:1=8b9345b1, c1-Y6-main-arm.txt:1=0bf098dd, counter-selftest.txt:1=06df4f97); (g) not addressed.
- Brief says (a)-(e); round-71.md:85 carries (a)-(h) — LOW.

Byte re-derivations: mk-counter replay reproduces counter+matrix identically (`cmp` clean); make-battery replay reproduces 5 members+SHA256SUMS+manifest; 6/6 r71-seat mutants reproduce byte-for-byte; matrix 75 rows (19 accept/56 refuse; base_expect 31/44; 70/70 carried base_expect = r71 receipt `base=`); probe 35 lines/10 accept; every receipt's instrument/matrix/mutant/member sha matches committed bytes; frozen inputs unchanged freeze→after-arms. NOT re-executed by this seat: the 9-min C1 harness and 4-min battery runs.

Commands (from lane root; scratch /fast/scratch/hyaku/souji-r72/S72Scribe, now removed)
- `python3 -B tools/souji-pointer-check.py --root … --rev 2ec8b63d… census/round-72/preregistration.txt corpus/knowledge/filter-filemode-witness.md corpus/README.md` → `SUMMARY files=3 checked=134 missing=4 skipped=9 dead_declared=0`, `EXIT=1`. Missing: README.md:81 `census/operator-sweep-20261019`; :764 `.ufo/waves/round-32/a2w1/SwarmCritic20.md`; :770 `…/SwarmReviewer27.md`; :985 `.ufo/waves/round-62/w1/S62ConnectorOverlap`. Same four at 0bf098dd (files=1 checked=88 missing=4, EXIT=1) → pre-existing; no r72 pointer receipt.
- Replay of c1-Y6-main-arm.txt's recorded command minus `--receipt` → `SUMMARY matrix=75 … base_mismatches=0 … EXIT=0` (does NOT reproduce the receipt). Variant `census/round-72/records/variants/r72-Y6-counter.py` → `SUMMARY matrix=75 base_forgeries=2 base_honest=19 base_mismatches=10 … EXIT=1` (matches receipt:164-165).
- Replay of counter-selftest.txt's recorded command verbatim → `C1-COUNTER-FATAL: work directory does not exist: …/<scratch>`, `EXIT=2`.

Findings
- MEDIUM: D3 half-closed and undeclared — ident conversion + stat pins are matrix-less and not named in the limits.
- LOW/MEDIUM: receipt provenance — `instrument=`/`command=` are the `COUNTER_REL` constant (c1-counter.py:191,1481,1935,1976), so the Y6 receipt's own command runs the unmutated counter; two committed receipts are not replayable.
- LOW: pointer gate red at the round's revision with four pre-existing dead pointers, no r72 receipt.
- LOW: seat brief's (a)-(e) is stale against round-71.md:85 (a)-(h).
- LOW: id collision — matrix row `W7` (:48, git-dir-redirect-hides-mode) vs battery mutant WM7 (prereg:36); WM7 reachability has no r72 artifact.

Files written: `.ufo/waves/round-72/w1/S72Scribe/draft.md`, `.ufo/waves/round-72/w1/S72Scribe/replay-honest-arm.txt`, `…/replay-Y6-variant.txt`, `…/mk-counter-replay.txt`, `…/pointer-check-r72.txt`, and this report `.ufo/waves/round-72/w1/S72Scribe.md`.
