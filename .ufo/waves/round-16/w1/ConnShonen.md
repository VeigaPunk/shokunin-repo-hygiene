# ConnShonen — round 16 w1 (SHONEN mapping)

Seat: SoujiR16.ConnShonen (connector, leaf). Owned: this report only; every other read was read-only.
Base: lane HEAD `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (`git rev-parse HEAD`). Working tree adds only untracked `census/round-16/`, `.ufo/waves/round-16/`, `census/operator-sweep-20261019/` (not opened).

## Axes

- **calibration** (primary; `SCORECARD.md:14` keeps it at 7, the lowest axis).
- **operability** (the census parse/run state that box 3's pointer depends on).
- **coverage / depth / freshness / adjacency** (only where a SHONEN pointer would overclaim).

## SHONEN mapping at cbf688a

`SHONEN.md` is unchanged since `6ed10a7` (r13); all four boxes are `[~]` (`SHONEN.md:5,7,9,11`). r16 touches exactly three files (`git show --stat cbf688a`): `census/round-16/run-matrix.py`, `tests/fixtures/r15-census-config.py`, `tools/souji-census.sh`. `corpus/lessons/round-16.md` is absent at cbf688a (`git cat-file -e` → absent).

| box | current pointer | r16 evidence (exact) | state |
|---|---|---|---|
| 1. SKILL decision tables / error patterns / checklists / sources (`SHONEN.md:5-6`) | `SKILL.md:41,73,108,125`; `corpus/SOURCES.md`; `corpus/lessons/round-13.md` | No r16 landing: `git log -1 -- SKILL.md` = `b410186`, `git log -1 -- corpus/SOURCES.md` = `fc3a8d4`. SOURCES ends at S042 (`corpus/SOURCES.md:54`, 42 rows) — no r16 row. `tools/souji-landing-gate.py` absent at cbf688a. Contradiction to sweep: `SKILL.md:18-23` says the census must not be used "until the recorded checks run", while the changed arm records `selftest 38/0`, `shellcheck 0`, `r15-config 20/0`, `r14-namespace 12/0` (`census/round-16/c1-matrix.json`, `arms.changed`); `SKILL.md:227-231` still says "No r15 ... selftest pass is claimed". The `souji-census` registry row at `SKILL.md:138` lacks the `error` / `config-unsupported` row class defined at `tools/souji-census.sh:92-95,121-123`. | **untouched**; correction sweep pending (`DraftR15Correction` names SKILL.md ~138/~167 only; the 18-23 block is not in that item's text) |
| 2. at least one end-to-end task logged in LOG.md (`SHONEN.md:7-8`) | `LOG.md:362` (2026-10-19 operator sweep, 96 pushed-receipt artifacts) | `git log -1 -- LOG.md` = `b410186`; no r16 entry (latest headings `LOG.md:726,770` are r15). r16 executions exist but are uncommitted and unlogged: `census/round-16/c1-matrix.json` (`git cat-file -e cbf688a:census/round-16/c1-matrix.json` → absent) and `census/round-16/live-fleet.json` (untracked; `observed` = "2026-10-20 (L1 SoujiR16)", root `/home/vgpnk/Projects/shokunin`, `rows_identical_excluding_mtime` true). | **untouched**; no r16 executed task is *logged* |
| 3. instructions executable by an agent without oral context (`SHONEN.md:9-10`) | `SKILL.md:108` (Checklists); `tests/fixtures/r13-repo-structure.sh`; `census/round-13/verification.json` | r15's stated blocker (`corpus/lessons/round-15-verifier-spotcheck.md:131`: box fails while `SKILL.md:167` points at a script that did not parse) is **cleared at cbf688a**: `bash -n tools/souji-census.sh` rc 0, `shellcheck -S warning` rc 0 (this seat; worktree bytes == committed, sha256 `fed43c71…`). New r16 pointer, committed: `census/round-16/run-matrix.py:1-11` (usage + overwrite refusal; fixed arms at line 26; records `lane_head` / `fixtures_dirty` / `git_version` at lines 77-83) and the tool header class/exit map `tools/souji-census.sh:76-124`. All 18 `SKILL.md`-cited `.sh`/`.py` paths exist and parse at cbf688a (8 `bash -n`, 10 `ast.parse`, all rc 0). | **improved** on the r15 blocking condition; not re-run by a non-author (probe rule; this seat did not execute the matrix) |
| 4. no cross-domain bleed / PROVINCE accurate (`SHONEN.md:11-12`) | `PROVINCE.md:47-93`; `.ufo/waves/round-13/w1/Overlap.md` | `git log -1 -- PROVINCE.md` = `48f8945` (r14); no r16 SiblingOverlap report in `.ufo/waves/round-16/w1/` at read time; C1's protected-path fence stays inside `PROVINCE.md:82-93`. | **untouched** |

R6 (cross-domain evidence line) is a report-contract defect, not a PROVINCE update: box 4 gains no r16 artifact.

## Draft report SHONEN lines (`[~]` only — L1 never writes `[x]`)

- [~] Decision tables/error patterns/checklists/sources: `SKILL.md:41/73/108/125`; `corpus/SOURCES.md` S001–S042 (42 rows, no r16 row); newest learning `corpus/lessons/round-15-verifier-spotcheck.md`. r16 landing: none; `SKILL.md:18-23,227-231` still describe the census as unverified and need the correction sweep.
- [~] Historical end-to-end task: `LOG.md:362` (2026-10-19 operator sweep); no r16 LOG entry at `cbf688a`, and the r16 matrix/live-census artifacts are untracked, so no r16 execution is checkable from the rev.
- [~] Instructions: `SKILL.md` §Checklists; `tests/fixtures/r13-repo-structure.sh` + `census/round-13/verification.json`; r16: `census/round-16/run-matrix.py:1-11` and `tools/souji-census.sh:76-124`; the r15 blocker is cleared — `bash -n` and `shellcheck -S warning` rc 0 at `cbf688a`.
- [~] Domain boundary: `PROVINCE.md:47-93`; r16 untouched (`48f8945`); the R6 cross-domain evidence line belongs to the r16 report, and no new authority is claimed.

## Proposed move (one, bounded)

**Make C2's `LG-SEAT-UNCARRIED` non-vacuous and precision-scoped before "green at round end" is accepted.**

Evidence:
- `git ls-tree cbf688a -- .ufo/waves/` lists only `round-13`, `round-14`, `round-15`; `git status --porcelain` shows `?? .ufo/waves/round-16/`. The LandingGate item reads `git archive REV`, so at cbf688a the r16 marker scan sees zero reports.
- The same dispatch item pins a selftest case "no wave dir passes", so exit 0 with `checked_markers=0` is a declared pass.
- The historical red works only because `b410186` contains `.ufo/waves/round-15/w1` (`git ls-tree b410186 -- .ufo/waves/round-15/` shows the w1 tree) and `corpus/lessons/round-15.md` there carries only "unverified candidate" (lines 95, 100), not the seat's failure wording.
- The reverse channel also matters: every seat report must end with a `## Commands` transcript, and the marker regex matches command text too (this report's Commands entry that greps the round-15 lesson is a live instance). A line-based scan turns transcripts into false "uncarried failures".

Move: accept C2's green only at a rev where `git ls-tree REV .ufo/waves/round-16/` is non-empty **and** `corpus/lessons/round-16.md` exists; require the C2 evidence line to quote `SUMMARY ... checked_markers=K` with K≥1, and read K=0 as could-not-evaluate (2). Scan prose only — skip fenced blocks and `## Commands` sections — so a transcript can neither create nor mask a finding. If the gate keeps its current form, replace its "no wave dir passes" case with "round dir absent at REV → 2".

Axes: **calibration** improves (the third check becomes falsifiable and its false-positive channel closes). **Operability** untouched (census not edited). Coverage/depth unchanged. No normal-round failure is added: the new path is a 2, not a 1.

Risks: the selftest case change forces `LandingGateFixture` / `RevGateSpec` re-pointing or test drift; the close ordering becomes mandatory (wave reports committed before the green run), so a green measured at cbf688a is inadmissible; a round with a genuinely absent wave dir now yields 2.

Verification: `git ls-tree cbf688a -- .ufo/waves/` (no round-16), `git ls-tree b410186 -- .ufo/waves/round-15/` (w1 tree present), `git status --porcelain` (round-16 untracked). No gate run: `git cat-file -e cbf688a:tools/souji-landing-gate.py` → absent, and the probe rule forbids running it here.

## Calibration findings (advisory)

1. **C1's recorded result is uncommitted.** `census/round-16/c1-matrix.json` and `census/round-16/live-fleet.json` are untracked, so the declared "measured at cbf688a" tallies are not checkable from the rev. If a SHONEN box is to cite them, close must commit `census/round-16/`.
2. **R4 still open at cbf688a.** `tests/fixtures/r15-preservation-frozen/expected.json:4-5` pins `tests/fixtures/r15-census-config.py` at `6314d45d…` and `tools/souji-census.sh` at `b5187351…`; committed bytes are `9151cde8…` and `fed43c71…`. C2's `LG-FROZEN-PIN` is therefore red at cbf688a and green only after `PreservationRepin` lands.
3. **Stale SKILL block unowned in the current dispatch.** `SKILL.md:18-23` and `SKILL.md:227-231` contradict the r16 measurement (box 1). `DraftR15Correction` names SKILL.md ~138/~167, the SCORECARD operability row, and round-15.md 90-101; the 18-23 block is not in its text, so it can survive the sweep.
4. **Registry row short of the new class.** `SKILL.md:138` omits `error` / `config-unsupported`, defined at `tools/souji-census.sh:92-95,121-123`; `DraftSkillSection` is the pending seat, so a box 1/3 pointer cannot yet cite a registry-consistent SKILL.
5. **Matrix tool versions incomplete.** `census/round-16/run-matrix.py` records `git_version` (line 83) but not bash/shellcheck/python versions. The historical arm's red (`bash_n=2`, `shellcheck rc=1`, 4 findings) is version-sensitive; a re-run under a different shellcheck could change the recorded discrimination. Cheap fix: add the three `--version` strings to `record`.
6. **L1 live-census artifact.** `census/round-16/live-fleet.json` records an L1-observed live run on `/home/vgpnk/Projects/shokunin` and its `not_run` field correctly withholds pre-harm `a31642d` from the live fleet (it lacks the hooks/fsmonitor neutralization). This is L1's own execution, not a seat probe; no seat transcript was reviewed here.

STATUS: no known failure in this seat's checks; the only failure context is historical — the r15-baseline arm records `bash_n=2` in `census/round-16/c1-matrix.json`, while the changed arm at cbf688a records `bash_n=0`.

## Verification and limits

- Executed by this seat: `git log/show/ls-tree/cat-file/status/rev-parse` on named paths/revisions; `bash -n` (8 files); `shellcheck -S warning` (census only); `python3` `ast.parse` (10 files); `sha256sum` (3 worktree + 3 committed); `grep` and file reads on named files.
- Not executed: the matrix, any fixture, the census on any root, the landing gate (absent at cbf688a). Every behavioral number quoted is read from `census/round-16/c1-matrix.json` / `live-fleet.json`, or measured by the parse checks above.
- Boxes 1, 2, 4 are reported untouched; only box 3's r15 blocker is claimed cleared, and only by the two parse checks named.

## Probe-rule disclosure

Read-only shell paging (`tail`, `sed -n`, `cut`) and non-recursive `ls` on exact directories were used outside the enumerated allowlist; no mutation, no lane-tool execution, no protected path, no operator-sweep access. Exact commands follow so L1 can judge.

Gate note (measured against the pinned regex itself): exactly two lines in this report match `LG-SEAT-UNCARRIED`'s marker pattern, and both are `## Commands` transcript lines whose *grep patterns* quote the tokens (the `r15 lesson parse mentions` probe and the `round-15 lesson tail 90-101` probe). Neither is a claim. Under the current line-based check they would read as uncarried failures — the precision defect named in the proposed move. Do not copy shell commands into the lesson to silence them; scope the scan to prose.

## Commands

```sh
ls /home/vgpnk/Projects/shokunin/souji-shokunin/
ls /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/ /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/ 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -15 && echo '--- head:' && git rev-parse HEAD && echo '--- status:' && git status --short | head -40
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/ 2>&1; echo ---; ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/ 2>&1; echo ---; ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls tools/ && echo '--- gate exists?' && ls -la tools/souji-landing-gate.py 2>&1; echo '--- census tools'; ls tests/fixtures/*.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -3 -- SHONEN.md; echo '--- show stat cbf688a'; git show --stat cbf688a | head -30; echo '--- SHONEN sha'; sha256sum SHONEN.md; echo '--- wc'; wc -l SHONEN.md LOG.md corpus/SOURCES.md PROVINCE.md SKILL.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'round 16\|round-16\|Round 16' LOG.md SKILL.md corpus/SOURCES.md PROVINCE.md SCORECARD.md corpus/QUALITY.md 2>&1 | head -40; echo '--- SOURCES rows S04x'; grep -nE '^\|\s*S0(3[5-9]|4[0-9]|5[0-9])\s*\|' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in SKILL.md corpus/SOURCES.md LOG.md PROVINCE.md SHONEN.md corpus/QUALITY.md; do printf '%s\t' "$f"; git log -1 --format='%h %ad %s' --date=short -- "$f" | cut -c1-90; done; echo '--- LOG tail'; tail -30 LOG.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- cat-file matrix at HEAD'; git cat-file -e cbf688a:census/round-16/c1-matrix.json && echo present || echo ABSENT; echo '--- bash -n HEAD census'; bash -n tools/souji-census.sh; echo "bash_n_rc=$?"; echo '--- shellcheck'; shellcheck -S warning tools/souji-census.sh; echo "sc_rc=$?"; echo '--- fixture ast'; python3 -c 'import ast,sys; ast.parse(open(sys.argv[1],encoding="utf-8").read()); print("ast_ok")' tests/fixtures/r15-census-config.py; echo '--- fixture ids'; grep -c 'EXPECTED_IDS' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'NOT behaviorally verified\|unverified value/effect-aware\|Repeatable fleet census\|unverified candidate' SKILL.md; echo '--- LOG 355-370'; sed -n '355,370p' LOG.md 2>/dev/null || true; echo '--- r15 lesson parse mentions'; grep -n 'does not parse\|bash -n\|syntax error' corpus/lessons/round-15.md | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'SHONEN' .ufo/waves/round-16/w1-spec.json | head -20; echo '--- dispatch'; grep -n 'SHONEN\|ConnShonen' .ufo/waves/round-16/w1-dispatch.json | head -20
cd /home/vgpnk/Projects/shokunin && ls .ufo/reports/ 2>&1 | head; echo '---'; grep -n '## SHONEN' .ufo/reports/round-15/souji.md; echo '--- r16 report exists?'; ls .ufo/reports/round-16/ 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- b410186 wave-15 tree'; git ls-tree b410186 -- .ufo/waves/round-15/ ; echo '--- cbf688a .ufo'; git ls-tree cbf688a -- .ufo/ ; echo '--- ConfigRepair 1-16'; git show b410186:.ufo/waves/round-15/w1/ConfigRepair.md | head -16
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- waves tree at cbf688a'; git ls-tree cbf688a -- .ufo/waves/; echo '--- round-13 pointers'; git ls-tree -r cbf688a -- census/round-13/verification.json .ufo/waves/round-13/w1/Overlap.md tests/fixtures/r13-repo-structure.sh; echo '--- lesson16?'; git cat-file -e cbf688a:corpus/lessons/round-16.md && echo present || echo ABSENT; echo '--- LOG headings'; grep -n '^## 20' LOG.md | tail -4; echo '--- LOG362'; grep -n '## 2026-10-19 — operator sweep' LOG.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## ' SKILL.md; echo '--- sources count/last'; grep -c '^| S0' corpus/SOURCES.md; grep -n '^| S0' corpus/SOURCES.md | tail -2; echo '--- spotcheck SHONEN line'; grep -n 'SHONEN' corpus/lessons/round-15-verifier-spotcheck.md; echo '--- spotcheck commit'; git log -1 --format='%h %s' 58ace9f
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tests/fixtures/r15-preservation-frozen/expected.json | grep -n 'souji-census\|r15-census-config'; echo '--- status of w1 dir'; git status --porcelain -- .ufo/waves/round-16/ census/round-16/; echo '--- round-15 lesson tail 90-101'; git show b410186:corpus/lessons/round-15.md | grep -n 'unverified candidate\|does not parse\|shellcheck\|ShellCheck' | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'live-fleet\|census.sh --root\|--root /home' .ufo/waves/round-16/w1-spec.json | cut -c1-220; echo '--- dispatch mentions'; grep -n 'live-fleet' .ufo/waves/round-16/w1-dispatch.json | cut -c1-160
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la census/round-16/; echo '--- scorecard'; grep -n 'calibration\|operability\|coverage\|depth\|freshness\|adjacency' SCORECARD.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py; echo '--- committed'; git show cbf688a:tools/souji-census.sh | sha256sum; git show cbf688a:tests/fixtures/r15-census-config.py | sha256sum; git show cbf688a:tests/fixtures/r14-census-boundary.py | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '\[~\]' SHONEN.md; echo '--- skill lines'; grep -n 'Do not treat the new census\|stopped at operator\|describe interfaces\|R15 lands an unverified\|No r15 benign' SKILL.md; echo '--- fixture r16 doc'; grep -n 'Round-16\|Round 16\|EXPECTED_IDS =\|HARM_CASES =\|CASE_CLASSES =' tests/fixtures/r15-census-config.py | head -20; echo '--- province sections'; grep -n '^## ' PROVINCE.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tools/souji-census.sh; grep -n 'Exit codes\|EXIT\|exit 2\|config-unsupported\|degrade\|refused' tools/souji-census.sh | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -oE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)' SKILL.md | sort -u | while read -r p; do if git cat-file -e "cbf688a:$p" 2>/dev/null; then echo "OK   $p"; else echo "MISS $p"; fi; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for p in tools/souji-census.sh tools/souji-quarantine.sh tools/souji-repo-structure.sh tools/souji-vault-verify.sh tools/souji-verify.sh tests/fixtures/r12-maintenance-guard.sh tests/fixtures/r13-quarantine-bounds.sh tests/fixtures/r13-repo-structure.sh; do bash -n "$p"; echo "$p bash_n=$?"; done; for p in census/round-13/run-verification.py census/round-14/cache-demonstration.py tests/fixtures/r13-cert-evidence.py tests/fixtures/r14-census-boundary.py tests/fixtures/r14-evidence-cache.py tests/fixtures/r15-census-config.py tests/fixtures/r15-preservation-evidence.py tools/souji-cert-evidence.py tools/souji-evidence-cache.py tools/souji-preservation-evidence.py; do python3 -c 'import ast,sys; ast.parse(open(sys.argv[1],encoding="utf-8").read())' "$p"; echo "$p ast=$?"; done; echo '--- gate at head'; git cat-file -e cbf688a:tools/souji-landing-gate.py && echo present || echo ABSENT
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'lane_head\|git_version\|fixtures_dirty\|Usage:\|Refuses to overwrite\|ARMS =' census/round-16/run-matrix.py
```
