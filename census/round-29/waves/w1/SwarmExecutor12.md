# SwarmExecutor12 — r29 w1 baseline of the lane's existing gates

## Status
STATUS: PASS — all eight assigned baseline commands ran at base `691dd29211c53d0ef94fa072394cb9c8a69fe92e` from a detached scratch clone; seven exited 0 with their controls rejected, and the landing gate exited 2 through its documented could-not-evaluate path (`.ufo/waves/` is gitignored), so that gate's comparable baseline is its finding count (3), not its rc. No gate failed at base for a wave-caused reason. Delivery: `deliver-baseline-gates.tsv`.

## Evidence

Base and clone: `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r29-BaselineGates/c`, then `git -C … checkout -q --detach 691dd29211c53d0ef94fa072394cb9c8a69fe92e`; `git -C <clone> rev-parse HEAD` → `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, `rev-parse --show-toplevel` → `/var/tmp/souji-r29-BaselineGates/c`, `git status --porcelain` → 0 lines after the full command set. Every command ran with cwd = clone root, `python3 -B`.

1. Landing gate — exit 2 (stdout):
```
LG-DANGLING-PTR	.ufo/waves/round-28/	corpus/lessons/round-28-verifier-spotcheck.md:34 cites path absent at 691dd29211c5
LG-DANGLING-PTR	census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:fixture/	corpus/lessons/round-28-verifier-spotcheck.md:71 cites path absent at 691dd29211c5
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/lessons/round-28-verifier-spotcheck.md:36 cites path absent at 691dd29211c5
SUMMARY	findings=3	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
```
   same run, stderr: `COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-28/ at 691dd29211c53d0ef94fa072394cb9c8a69fe92e`

2. `python3 -B tools/souji-record-agreement.py --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e` — exit 0 — `keys=4 records=4 occurrences=17 mismatches=0` (CLI checked with `--help` first: `--root --rev --json --no-worktree`).

3. `python3 -B tools/souji-coverage-agreement.py --root . --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e` — exit 0 — `grounded=13 mapped=13 dangling=0 mismatches=0` (equals the prereg C3 base line).

4. `bash tests/fixtures/r28-wave-evidence-capture.sh` — exit 0 — `cases=6 pass=6 control=TAMPER-REJECTED`.

5. `bash tests/fixtures/r27-pre-report-gate.sh` — exit 0 — `cases=4 pass=4 control=FALSE-GREEN-REJECTED`.

6. `python3 -B tests/fixtures/r25-coverage-agreement.py --tool tools/souji-coverage-agreement.py` — exit 0 — `cases=16 pass=16 control=FALSE-GREEN-REJECTED`.

7. `python3 -B tools/souji-axis-check.py --prereg /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/records/preregistration.txt --scorecard SCORECARD.md` — exit 0 — `claims=3 flags=0`.

8. `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` — exit 0, 35 `W04` rows, no `E` code — final line verbatim:
```
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```
   `diff -u` of this run's 36 output lines against `census/round-29/records/census-start.txt` yields one hunk that adds only the record's own `exit=0` trailer; `grep -c W04` is 35 on both sides.

Delivery fidelity: each of the 8 `summary_verbatim` cells was byte-compared to its capture file — 8/8 equal (`ALL_MATCH=True`); `awk -F'\t'` confirms the five fixed fields of every row are tab-free, with the summary as the last column.

## Findings

1. **The landing gate's exit code is structurally 2 at this revision.** `.gitignore:1` is `.ufo/waves/`, so `git cat-file -t 691dd292…:.ufo/waves/round-28` → error at every rev; the tool's exit contract (`tools/souji-landing-gate.py` docstring: "2 could-not-evaluate … missing .ufo/waves/round-N/ at REV") turns that into rc 2 with `checked_reports=0`. The round's no-regression comparison at this gate must therefore use `findings=` (base 3), never rc. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.gitignore:1`, `tools/souji-landing-gate.py` exit block.

2. **All three base findings are backticked tokens inside quotations in the routed r28 lesson, not broken scripts or pins.** `corpus/lessons/round-28-verifier-spotcheck.md:34` quotes the gate message "…no .md reports under .ufo/waves/round-28/" (that tree is gitignored, so absent at REV); `:36` is a negative re-measure "git show fec846d:corpus/QUALITY.md | grep -c 'corpus/knowledge/registry'" whose needle `corpus/knowledge/registry` is genuinely absent at REV (`cat-file -t` → error); `:71` is an ignore-provenance token `…/vadv-49/.gitignore:fixture/` whose `.gitignore` blob does exist at REV (`cat-file -t` → blob) — the gate takes the whole `path:rule` token as a path. Classification: one truly dangling citation, one ignored-path/environmental, one citation-shape artifact `[INFERENCE]` on intent (the parse behaviour is observed in the output's path column).

3. **`record-agreement`'s exit 0 holds only over a clean worktree, and the lane disk is not clean.** In `/home/vgpnk/Projects/shokunin/souji-shokunin`, `git status --porcelain` → ` M .ufo/waves/round-26/w1/ScribeGateDraft.md`; `census/round-23/records/uncommitted-exemptions.tsv` names only `census/operator-sweep-20261019/` and `grep -c ScribeGateDraft` there is 0. K4 flags each non-exempt `git status --porcelain` path (`tools/souji-record-agreement.py` docstring, K4). An in-lane rerun will therefore report one pre-existing K4 mismatch that is not a wave regression; only the committed-bytes/clone run is comparable. I neither modified nor staged that path (observed at first inspection, before any command).

4. **The C1 and C2 instruments do not exist at base.** `tools/souji-registry-agreement.py` and `census/round-29/c2-counter.py` are `ABSENT` at `691dd292…` and `blob` at `b8cb4b31…`; `tests/fixtures/r29-registry-agreement.py` is absent at both. Their frozen before values (`k1=6 k2=4 mismatches=10`; `manifests=3 failed=152 uncovered=14 floor_violations=0`) come from `census/round-29/records/controls.tsv` and are reproducible only with the b8cb4b31 tool binary, never from a base-tree execution.

5. **Baseline floors a later "no drop" comparison must hold.** Case counts: r28 capture fixture 6 (`tests/fixtures/r28-wave-evidence-capture.sh:6`, "six isolated cases"), r27 4, r25 16, each with its control rejected (`TAMPER-REJECTED`, `FALSE-GREEN-REJECTED`, `FALSE-GREEN-REJECTED`); coverage-agreement `mismatches=0` with `grounded=13 mapped=13`; axis-check `claims=3 flags=0`; sources-census rc 0 with 35 W04 / 0 E.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-baseline-gates.tsv` — 8 rows, columns `id / command / exit / class / notes / summary_verbatim`; the summary is the last column and is raw capture bytes (the landing-gate and sources-census summaries are tab-separated internally), fields 1-5 are tab-free.
- `.ufo/waves/round-29/w1/SwarmExecutor12.md` — this report.

No tool installs or upgrades this seat. No writes outside the two delivery paths; the scratch clone and captures under `/var/tmp/souji-r29-BaselineGates/` were removed after the delivery bytes were verified.
