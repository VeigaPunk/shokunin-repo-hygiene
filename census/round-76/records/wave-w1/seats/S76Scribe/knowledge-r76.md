# r76 section draft for corpus/knowledge/filter-filemode-witness.md (scribe S76Scribe)

Append after the r75 section (currently ends at `corpus/knowledge/filter-filemode-witness.md:237`).
Every measured number below was re-derived this round from committed bytes (seat S76Scribe), not copied
from the L1's counts; the commands are in `.ufo/waves/round-76/w1/S76Scribe.md`.

## r76: which file decides an ignore match, and a tally that binds a receipt to its mutant (appended 2026-11-06)

**The gate can ask which rule decided a match.** An ignored path is not declared policy merely because
some exclude source matches it: git-check-ignore(1) reports the deciding rule per path. With `--verbose`
the record is `<source> <COLON> <linenum> <COLON> <pattern> <HT> <pathname>`, and "<source> is the
pattern's source file, and <linenum> is the line number of the pattern within that source." (S320, offset
2355 of the whitespace-normalized capture). The source field is absolute for `core.excludesFile` and
repository-relative for `.git/info/exclude` or a per-directory exclude file (same page, OUTPUT). The gate
therefore lists untracked ignored paths (`ls-files -o -i --exclude-standard`), feeds each to
`git -c core.excludesFile=/dev/null check-ignore -v -n -z --stdin` — `/dev/null` attributes that source
away so a path it alone hides reads as unmatched — and accepts a path only when its deciding pattern is
non-negated and its source is a TRACKED `.gitignore` in one of the path's ancestor directories
(`RECEIPT-UNTRACKED-UNDECLARED-IGNORE` otherwise, count only). A per-directory `.gitignore` is
declared policy only when the repository tracks it.

**Labels the r76 counter freezes.** `f7-selfignore-dir` is FAIL, relabelled from the r75 stated-limit
PASS: an untracked `.gitignore` that ignores itself decides its directory's matches from unversioned
bytes, exactly as info/exclude does. `f11-committed-dir-rule` is PASS (a committed rule naming the tool
directory — the `.jj/` shape) and `f12-committed-nested-gitignore` is PASS (a tracked `sub/.gitignore`).
The other 24 imported r75 rows keep the verdicts they held at the lane base. Measured with the frozen
30-row population (`census/round-76/c1-population.tsv`): the lane-base gate blob `ef3b04e4` reads
mismatches=4 [f7 f9 f10 f14] EXIT=1 (`census/round-76/controls/c1-K-a-do-nothing.txt`); the candidate
gate blob `18587bd2` reads `SUMMARY rows=30 mismatches=0 errors=0` EXIT=0
(`census/round-76/records/c1-after.txt`).

**Two controls stay red.** Refusing every ignored file (`controls/c1-K-b-blanket-ignored.txt`) breaks the
four honest rows f2, f6, f11, f12 — mismatches=4 EXIT=1; refusing any untracked `.gitignore`
(`controls/c1-K-c-naive-untracked-gitignore.txt`) breaks f11 — mismatches=1 EXIT=1. Regression at the
candidate gate: r36 `SUMMARY cases=21 pass=21 fail=0` and r27 `cases=4 pass=4`
(`census/round-76/records/c1-regress-r36.txt`, `c1-regress-r27.txt`).

**The lane declares its own two tool directories.** Commit `e827d2b` adds `.jj/` and `.ruff_cache/` to the
lane's committed `.gitignore` (`.gitignore:4-5`), so the matches inside those directories are decided by a
tracked rule instead of the self-ignoring `.gitignore` each tool writes. Live attribution on the lane
returns `.gitignore:4:.jj/` for `.jj/repo/config-id`; the lane itself reads `check-clean=PASS`.

**A receipt must name the instrument it ran.** The r76 tally (`census/round-76/c2-kill-tally.py`) derives
the expected bytes of every mutant itself — the pristine `census/round-75/c1-counter.py` with the frozen
single-occurrence edits of `census/round-75/c2-mutants.json` and `census/round-74/c2-survivors.json`
applied in order — and requires the receipt's column-0 `instrument_sha256=` to equal that sha256, its
`command=` to carry ` --selftest`, and no two slots to share a receipt digest; an id with no derivation is
UNBOUND. Every `EXIT=` line is read, and the r75 unread classes hold: one `SELFTEST` line with fail>=1
plus every `EXIT=1` is KILLED, fail=0 plus every `EXIT=0` is SURVIVED, anything else is UNREAD. Measured
against the frozen 10-case population (`census/round-76/c2-population.tsv`): the do-nothing tally (the r75
counter, sha256 `fdb75c09`) reads mismatches=5 [b-swap-x09-gets-m08 b-swap-p1-gets-x09 b-pristine-r74
b-unknown-id b-exit-disagree] EXIT=1 (`controls/c2-K-do-nothing-r75.txt`); the r76 tally reads
`SUMMARY cases=10 mismatches=0 errors=0` EXIT=0 (`records/c2-after.txt`), with the honest r75 set still
`mutants=6 killed=6 survived=0`. The blanket control that rejects every set
(`controls/c2-K-b-blanket-reject-all.txt`) stays red at mismatches=2 [h-honest h-honest-reordered].

**Stated limit.** The tally reads bytes: binding proves which instrument a receipt names, not that the
instrument ran — a hand-written receipt carrying the right header and EXIT lines is out of reach without
re-running the counter. The gate's attribution has its own limit, unchanged from r75: a broad committed
rule (f2) still hides whatever it matches, and that is declared, versioned policy.
