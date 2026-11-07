# S75Scribe — round-75 knowledge section (draft for `corpus/knowledge/filter-filemode-witness.md`)

Append after the r74 section. Draft only; nothing in the committed knowledge file is edited by this seat.

---

## r75: which ignore rule may hide an untracked path from the gate, and a second detector for the counter's witness (appended 2026-11-06)

**`git status` treats every exclude source alike.** An untracked path matched by any exclude source is
left out of status output, but the sources are not the same kind of rule. gitignore(5) sends patterns
meant to be version-controlled and distributed to `.gitignore` files, and sends patterns that are
"specific to a particular repository but which do not need to be shared with other related repositories"
to `$GIT_COMMON_DIR/info/exclude`, while `core.excludesFile` names a per-user file (S318). Only the
committed `.gitignore` files are the lane's declared policy for untracked artifacts (the lane's own
`__pycache__/` line). Measured with the frozen r75 counter (`census/round-75/c1-evade-counter.py`, 25
rows: the 20 r74 routes imported byte-bound from `census/round-74/records/wave-repair/probes/evade-probe.py`
plus the five r75 ignore-surface routes f3 f5 f6 f7 f8, each with a frozen expectation in
`census/round-75/c1-population.tsv`): the lane-base gate passed an untracked file hidden by
`$GIT_COMMON_DIR/info/exclude` and a whole directory hidden the same way
(`census/round-75/controls/c1-K-a-do-nothing.txt`, mismatches=2 [f-info-exclude f5-info-exclude-dir]
EXIT=1).

**What the gate now does.** Inside the same isolated interpreter, after the byte-truth check, the gate
lists the untracked ignored paths twice — under `--exclude-standard` and under
`--exclude-per-directory=.gitignore` alone — and subtracts the second from the first
(`tools/souji-pre-report-gate.sh` at rev `1ad737b4`, lines 85-101). git-ls-files(1) defines
`--exclude-standard` as the per-directory files plus the user's global exclusion file and
`$GIT_COMMON_DIR/info/exclude`, and tells a caller who gives only `--exclude-per-directory=.gitignore` to
add the other two sources by hand ("To emulate what `--exclude-standard` specifies, you can give
`--exclude-per-directory=.gitignore`, and then specify:", S319). The set difference is therefore the
untracked content hidden only by a local, unversioned source; a non-empty difference prints
`RECEIPT-UNTRACKED-LOCAL-EXCLUDE` and fails `clean` (count only, no path echoed). Measured:
`census/round-75/records/c1-after.txt` rows=25 mismatches=0 EXIT=0 with the gate blob `620ed97e…` of
rev `1ad737b4`; refusing every ignored path instead (`census/round-75/controls/c1-K-b-blanket-ignored.txt`)
fails three honest rows — a committed `.gitignore` rule, a committed `*.pyc` rule and a self-ignoring
tool directory — mismatches=3 [f2 f6 f7] EXIT=1. On the lane itself the two listings are equal (measured
during the wave 2026-11-06; the count moves as agents write ignored report files, the equality is what
the gate tests), the lane's only ignored paths coming from its committed `.gitignore` lines
(`.ufo/waves/`, `census/operator-sweep-*`, `__pycache__/`) and from the self-ignoring `.jj/` and
`.ruff_cache/` directories; a dirty lane still fails `clean` for its tracked modifications, not for this
check.

**Rulings the counter freezes.** The r74 evasion probe labelled a route by worktree bytes alone and got
two of them wrong (round-74 routed defects 2 and 4, `corpus/lessons/round-74-verifier-spotcheck.md`): an
executable-bit change under `core.fileMode=false` keeps the bytes equal but is a lane change git records
in the tree, so `n-filemode-config` is expected FAIL (r74 called the repaired gate's refusal an
over-refusal); an untracked file hidden by a committed `.gitignore` line is declared repository policy,
so `f2-gitignore` is expected PASS (r74 left it as a stated limit).

**Stated limit.** An untracked `.gitignore` that ignores itself (`*`) hides its whole directory as
per-directory policy — the shape jj and ruff write (`.jj/.gitignore` holds `/*`, `.ruff_cache/.gitignore`
holds `*`, both untracked), and a shape a forger could copy. The gate cannot tell the two apart; row
`f7-selfignore-dir` freezes the honest label PASS. The lane's own 13392 `.jj/` and 5 `.ruff_cache/`
ignored paths rest on exactly this limit.

**The witness counter's selftest has a second detector.** S74MutCounter's r74 survivors were X09 (the new
slot's divergences not narrowed to the row's forged paths) and X15 (the (9a) witness-run check without its
`new_unwitnessed` term); X15 also removes the only kill of M17 (a new slot that reads its pre-run
divergence only). The r75 successor (`census/round-75/c1-counter.py`, sha256 `90a3c7b2…`, a 33-line diff
from `census/round-74/c1-counter.py`: header and two selftest checks, no `evaluate()`/verdict change)
adds, at `census/round-75/c1-counter.py:2015-2053`: a witness read that reports only a set-up path no
`forge_paths()` names must leave both slots unwitnessed (the X09 detector), and the (9a) run's per-row
new-slot witness must be yes for every forging row (a second detector of M17). Kills: the r74 counter 4
of 6 — X09 and P1 survive — with its selftest 62/62 (`census/round-75/controls/c2-K-do-nothing-r74.txt`);
the r75 counter 6 of 6 (X09, P1, M08, M14, M15, M17) with its own selftest 64/64
(`census/round-75/records/c2-after.txt`, `census/round-75/records/c2-after-pristine-selftest.txt`). X15
alone still survives by design; its harm is the lost detector, which P1 measures.

Still not covered: the ignore-source check reads the two listings once, after the byte-truth check, so it
does not re-read them after the run; a forger who adds an untracked self-ignoring `.gitignore` is labelled
honest (f7); the check counts paths and does not name them; git 2.56.0 only.

---

## Re-derivation performed by this seat (not part of the corpus text)

- C1 W arm: copied `tools/souji-pre-report-gate.sh` + `tools/souji-receipt-write.py` from rev `1ad737b4`
  into a scratch dir (sha256 `620ed97ea464…`, `70bbf1c2a92e…`), ran
  `python3 -B census/round-75/c1-evade-counter.py --gate-dir D --work S/c1w` →
  `SUMMARY rows=25 mismatches=0 errors=0`, EXIT=0.
- C1 base arm: same with rev `52d3f07d` (gate `062b6d39c9d8…`) → mismatches=2
  [f-info-exclude f5-info-exclude-dir], EXIT=1.
- C1 K-b arm: blanket-ignored variant gate (`e0d2e149e19b…`) → mismatches=3 [f2 f6 f7], EXIT=1.
- C2 tally replay on the committed receipts → `SUMMARY mutants=6 killed=6 survived=0 unread=0
  pristine=PASS`, EXIT=0; the do-nothing replay on the r74 receipts → killed=4 survived=2, EXIT=1.
- C2 pristine selftest of `census/round-75/c1-counter.py` re-run → see `census-validate.txt` companion
  `run-c2-pristine.txt` in this seat directory.
- Lane listing equality: `git ls-files -o -i --exclude-standard` vs `… --exclude-per-directory=.gitignore`
  → 25996 paths each, zero difference (2026-11-06, live worktree); the same count was 25993 minutes
  earlier, which is why the corpus text names the predicate, not a frozen number.
