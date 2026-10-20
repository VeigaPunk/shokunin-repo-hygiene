# CriticRoundAdmission — souji r18 W1

Attack on the round as a whole: lowest-axis fit, sourced claim, causal separability,
no-harm, mined mistake, SHONEN. Scope: plan-level falsification, not seat output
(wave 1 is in flight).

## Verdict

**Admission-blocking defect found in C1's fix contract (B1).** The per-repo bound as
specified wraps `census_one` only (`emit_census` :1394-1416), but the identical
stat-then-open TOCTOU the claim cites also lives in `list_repos` /
`guard_git_pointer` / `guard_git_config`, which run *before* the bounded loop. The
claim's falsifiable wording — "no single repository can hang the fleet census" —
still fails, deterministically, on the unbounded path. B2/B3 are smaller premise
gaps in C2; everything else is watch-list.

## Blockers

### B1 — C1 bound does not cover `list_repos`/`guard_git_pointer`/`guard_git_config` opens (claim falsified as contracted)

- `tools/souji-census.sh:1343-1391` `list_repos` calls `guard_git_surface "$d"`
  (:1352, :1355, :1385) and `guard_git_pointer "$d" "$g"` (:1381) per candidate,
  in the main shell, before `emit_census`'s per-repo child exists.
- `guard_git_pointer` → `gitfile_admin` :818-820 does `IFS= read -r line < "$file"`
  — a blocking `open(2)` on `.git` after only a `-f` test.
- `guard_git_surface` :902+ → `guard_git_config` (:913, :915, :933, :957, :975)
  → `tr -d '\000' < "$cfg" | cmp -s` (:696) and `git config --file "$cfg"` (:698, :702)
  — blocking opens on `.git/config`, plus `read < "$common"` on `commondir` (:922)
  and `read < "$reg"` on `worktrees/*/gitdir` (:854). `guard_git_files`'s `stat -L`
  (:555) is exactly the "guard passes, then swap" window L1 reproduced for
  `status` — the same window precedes every one of these opens.
- Deterministic repro (same technique as L1's PATH `git` shim): a PATH `stat`
  shim — `stat` is a coreutils call at :555 — swaps repo B's `.git/config` for a
  FIFO immediately after B's guard stat; B's `guard_git_config` then blocks in
  `tr < cfg` inside `list_repos`, before any watchdog exists. Whole run hangs,
  zero rows, outer `timeout` → 124. Identical observable signature to the defect
  being claimed fixed.
- **Smallest fix:** make the bound cover each repo-touch, not each measurement:
  `list_repos` reduces to pure lstat classification (`[ -d/-f/-L ]` never open —
  already true), and *every* repo-local open (`guard_git_surface`,
  `guard_git_pointer`, `census_one`) moves inside the same per-repo
  process-group child with the same watchdog. `.git`-file pointer children need
  a bounded guard pass too (row or skip). The shim fixture must attack the list
  phase, not only `status`.

### B2 — C2 scan list omits SHONEN.md, a file the calibration axis itself names

- `AXES.md:15` calibration signal: "**SHONEN.md**/SCORECARD entries match
  observed repo state". C2 scans SCORECARD, SKILL, PROVINCE, QUALITY, README,
  knowledge, round-N lesson, LOG section — not `SHONEN.md`. Its premise
  ("the lane's authority files must not cite evidence that does not exist")
  then goes unverified for one of the two files the axis definition cites.
- Checked today: all `SHONEN.md` pointers resolve
  (`corpus/lessons/round-13.md`, `tests/fixtures/r13-repo-structure.sh`,
  `census/round-13/verification.json`, `PROVINCE.md`,
  `.ufo/waves/round-13/w1/Overlap.md` all exist), so no live finding — but a
  stale SHONEN cite would sail past the new gate. A calibration claim shipping
  a scope hole on the calibration-evidence file is self-undermining.
- **Smallest fix:** add `SHONEN.md` to the scanned set; state in the claim that
  historical lessons stay out of scope by design (else LG-DANGLING-PTR would
  churn frozen history).

### B3 — LG-FROZEN-MEASURED spec keeps a silent-skip lane

- `tools/souji-landing-gate.py:544-572`: `measured` fails the hex regex →
  `measured_ok=False` → loop skipped, *no finding*. A record pinning
  `measured_commit: "master"` (non-hex, resolves to a commit, unverifiable as a
  pin) contributes zero checks and zero findings — the same "dangling → silent"
  defect class Q25(b) names, one shape over.
- **Smallest fix:** emit LG-FROZEN-MEASURED whenever `measured` is a non-empty
  string and `measured_ok` is False (covers unresolvable *and* non-hash
  values), still gated on `--round ≥ 18`.

## Watch-list (fix in the same diff, not blockers)

- **Watchdog lifetime:** contract says "the watchdog never outlives its repo".
  If `census_one` exits 2 the run `exit 2`s while the watchdog's `sleep` still
  runs — and the same on `exit 1` and on signal exits. Kill the watchdog
  unconditionally after `wait`, on every path including the protected-refusal
  and failure branches; a trap should reap live repo groups on INT/TERM.
- **Monitor-mode signal semantics:** `set -m` children ignore SIGINT/SIGQUIT
  (verified: child pgid ≠ parent pgid, `bash script.sh` no-tty, wait rc 143 on
  group TERM — mechanism itself is sound). Operator Ctrl-C on the script leaves
  the blocked repo running until the watchdog fires (≤ N s of residue). Parent
  INT trap → group kill removes even that.
- **Timeout/exit-2 collision:** a repo that would `protected_fail` (exit 2)
  *after* N s is instead TERMed by the watchdog and reported as a timed-out
  `error` row with run exit 0 — today that case hangs forever, so this is a
  strict improvement, but the semantics ("timeout suppresses a would-be
  refusal") should be stated in the row/lesson so the count isn't misread.
- **Precedence:** specify `--repo-timeout` beats `SOUJI_CENSUS_REPO_TIMEOUT`
  beats default 600; invalid *env* value should also usage-exit 2 (script
  already uses exit 2 for usage — `usage_err` :209, header doc :156 — so this
  is convention-consistent, not a conflict).
- **Exemption file trust:** `corpus/pointer-exemptions.tsv` (does not exist
  yet — `MISSING` today) must be shape-validated (two fields, non-empty reason)
  or the gate trusts an unchecked self-declared exemption list — a calibration
  hole inside a calibration gate.
- **Token-rule ambiguity:** `{a,b}` braces vs `round-6..11` ranges overlap —
  is `round-{6..11}` expanded twice? Pick one expansion order in the spec.
  Pinned-replay safety: existing selftests invoke `--round 16` (:940, :1318);
  gate the *finding* on round≥18 so `census/round-17/gate-replays-expected.json`
  (exists) byte-compares equal.
- **R1 recipe:** `tools/souji-quarantine.sh:246-251` — deriving the owner id via
  `jj config get user.name` minus `-shokunin` fails on non-jj/plain repos; the
  recipe must degrade to a placeholder + note, not fail. Fixture assertion
  should cover a souji-named repo and a non-souji jj repo.
- **C3 residue:** the tool lists but never reaps. Live count right now
  (independent, `/proc/*/cwd` readlink): **60 deleted-cwd processes** = the 58
  in `census/round-18/leaked-procs-before-1631.txt` plus 2 foreign
  (`/opt/1Password` zygotes 1911/1929). The census's "reason" column must split
  souji-fixture residue from foreign residue or the "census vs independent
  counter" comparison is apples/oranges. The 58 stay alive after the round —
  name their disposition in the report (they are evidence for C1 but they are
  still residue).

## Separability

- C1 verifiable alone (script + fixtures, no doc dependency). C3 verifiable
  alone (new tool). **C2 must be counted last**: its `findings → 0` needs every
  cited artifact (C1 matrix, C3 tool, wave reports, the r18 lesson) committed
  first. C2 verifies *without* C1/C3 passing — only their artifacts existing —
  so separability holds weakly; record the ordering constraint in the lesson.

## Lowest-axis rule (calibration 7)

C2 genuinely works calibration: "authority files must not cite evidence that
does not exist" = "SHONEN.md/SCORECARD entries match observed repo state"
(AXES.md:15), and it extends the existing landing-gate calibration capability
(Q25(b) open item is in scope). Verified today: `gate-replays-ddb7347.json` is
absent (only `-4f48343` and `-expected` exist) and `jj-receipts-ddb7347.txt` is
absent — real dangling pointers, real calibration defect. **But B2 leaves the
axis's own named file out of the sweep.**

## Sourced claim

"C1 rests on new rows" — §2b.4 requires the landed knowledge entry *or evidence*
to cite the S###. A script comment is weak; the citation should live in the
fixture matrix header / committed census record / a knowledge entry
(`setpgid`/`killpg` semantics, `bash(1)` job control — fifo(7) is already S062).
`used-by` on the new rows must name the landing path. Specify the carrier file
up front or the rule degenerates to a citation-shim.

## Mined mistake

The natural entry is the r17 F3 TOCTOU (residual, `round-17-verifier-spotcheck.md:68,
:153`). "Fix shown able to fail" needs the fixture red arm — and **with B1, a fix
per the current contract does not fail the list-phase variant**, so either the
bound widens (B1 fix) or the mistake entry honestly reads `fix: partial,
list-phase variant open`. Do not let the mistake entry claim a fix that the
strongest counterexample already beats.

## SHONEN

All four boxes `[~]` with resolvable pointers (verified above). Report may keep
`[~]`; `[x]` requires a named non-author verifier the lane cannot self-name —
the r18 closure is that verifier, post-landing. Promotion remains
operator-owned; nothing this round lands changes a box verdict by itself.
Report-installs line: none.

## Probes run (all in lane repo / read-only)

- `grep -n census_one tools/souji-census.sh` → callers only :1244 (worktree
  path, inside `census_one`) and :1403 (bounded-to-be).
- `stat -e` existence sweep of SHONEN-cited paths → all exist;
  `corpus/pointer-exemptions.tsv` and `tools/souji-proc-census.sh` absent (new
  files, as planned).
- `ps`/`/proc/*/cwd` readlink sweep → 60 deleted-cwd processes, matching +
  extending `census/round-18/leaked-procs-before-1631.txt` (58 fixture leaks,
  pids enumerated there, still alive).
- `bash` no-tty `set -m` test → background child got its own pgid (≠ shell
  pgid), `kill -- -pgid` + `wait` → rc 143; mechanism viable non-interactively.
- `tools/souji-landing-gate.py:538-586` → dangling-measured skip confirmed;
  `EXPECTED_JSON_RE`/`check_frozen_pins`/`--round` plumb-through confirmed.
- `tools/souji-census.sh:204-209` → usage exit is already 2; no collision.
- `ls census/round-17` → `gate-replays-{4f48343,expected}.json`,
  `jj-receipts-{4f48343,base5fa6017}.txt` exist; the `ddb7347` names cited by
  SKILL/LOG/knowledge do not.
