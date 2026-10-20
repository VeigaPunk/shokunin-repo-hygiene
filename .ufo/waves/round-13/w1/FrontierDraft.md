# FrontierDraft — round-13 W1 report

Seat: `SoujiR13.FrontierDraft` (leaf executor). Axes: calibration, operability,
coverage. Assignment: draft the F2 coverage map, PROVINCE movement/retention
recommendation, and safe SKILL decision/error/checklist additions citing
S005/S006. No shared doc was edited, nothing was committed, no live deletion
occurred.

## Files changed

- `census/round-13/frontier-draft.md` — created (284 lines, sha256
  `fad9d25532ee3f595df4768c00b04079bbd559f569d6d2a0c0f179c5bf733ff3`): F2
  coverage map (10 sub-grounds), PROVINCE movement/retention recommendation
  with landing conditions, SKILL insert drafts (3 decision rows, 2 error
  patterns, a pre-census checklist), and exact L1 checks.
- `.ufo/waves/round-13/w1/FrontierDraft.md` — this report.

## What the draft decides

- **Coverage.** F2 decomposes into 10 sub-grounds. Only the bounded read-only
  `git repo structure` census is in round scope; `count-objects`/`rev-list
  --disk-usage` (unreachable-object accounting), reclaimable-disk attribution,
  reclamation authorization, and comparative tooling (git-sizer) remain
  uncovered or out of province.
- **PROVINCE.** Retain F2 as a frontier row; move only the bounded read-only
  census to Core, and only when the entry, probe, fixture and cited evidence
  land in the same commit (conditions C-a…C-e in the draft). If any condition
  fails, leave F2 unchanged. The draft supplies exact replacement text for
  `PROVINCE.md:72-80`, the F2 frontier bullet, and `corpus/README.md:47`.
- **SKILL.** Additions are append-only and fill gaps not covered by the
  in-flight § F2: a `count-objects` refusal row, a partial-clone/promisor
  refusal row, a bare/linked-worktree caution row, the
  "reachable-size-as-reclaimable" and "optional-locks overclaim" error
  patterns, and a four-item pre-census checklist.

## Retained evidence (observed by this seat)

- Host git `2.55.0`; installed man pages:
  `git-repo(1)` roff :44 "THIS COMMAND IS EXPERIMENTAL. THE BEHAVIOR MAY
  CHANGE."; :166 "This format may change and is not intended for machine
  parsing. This is the default format."; `git(1)` roff :288-291
  (`--no-optional-locks`) and :2195-2200 (`GIT_OPTIONAL_LOCKS`).
- Isolated run, git 2.55.0, two disposable repos under
  `/var/tmp/souji-r13-frontier.*` (mkdtemp, removed by the same process,
  absence verified): `--format=lines` rc 0 with a 28-key inventory;
  `--format=nul` rc 0 with 28 NUL pairs; default table rc 0; `.git` manifest
  (content sha256 + mtime + size) unchanged across all three plus
  `count-objects`; `git status` with `GIT_OPTIONAL_LOCKS=0` left `.git/index`
  mtime and bytes unchanged after a stat-stale touch, while `=1` rewrote the
  index; plain directory rc 128; bare rc 0; linked worktree rc 0.
- In-flight artifact hashes at drafting: entry `48ff065f…`; fixture
  `5968a460…` (moved from `6c94f7fc…`); probe `97b324a7…` (moved twice);
  `SKILL.md` `6561c948…`; `PROVINCE.md` `dad81c3d…`; `corpus/README.md`
  `ef9086c1…`. `census/round-13/verification.json` was absent.
- `corpus/SOURCES.md:42-45`: S035/S036 supersede S005/S006 and S037 opens
  `builtin/repo.c`@v2.55.0 (`:744`, `:798-801`, `:930`); all three name the
  entry in `used-by`.
- Defects/gaps recorded with exact commands: Q4's mechanical test fails on
  the fixture as authored (`grep -c 'TMPDIR:-/tmp'` → 1, a comment at line
  88, while Q4 demands 0); `source-draft.md:37` proposes a stale entry slug
  (`size-census-git-repo-structure.md`); the fixture does not exercise the
  probe's promisor/partial-clone refusal; `count-objects` has no opened row.
- Only non-read observation executed: the raw git commands above and one
  `bash -n tests/fixtures/r13-repo-structure.sh` syntax check (no execution of
  the fixture, no probe run). `bash -n` is not a substitute for `--selftest`.

## Checks L1 should run (not run here)

1. `bash tests/fixtures/r13-repo-structure.sh --selftest` → expect
   `selftest=PASS ids=4/4`; repeat with `--probe tools/souji-repo-structure.sh`.
2. Resolve the admitted entry and fixture from HEAD
   (`git cat-file -e HEAD:<path>`), not from the worktree (Q17).
3. Reword fixture line 88 so Q4's literal test passes, then re-run check 1.
4. Confirm S035/S036/S037 `used-by` equals the admitted filename
   (`awk -F'|' '$2 ~ /S03[567]/ {print $2 "|" $12}' corpus/SOURCES.md`).
5. Land `census/round-13/verification.json` or drop its citations from the
   entry/README (Q17).
6. Confirm the PROVINCE Core sentence and README F2 row name only committed
   artifacts; otherwise defer the movement to the next round.

## Risks / blockers

- Every F2 artifact was in flight; hashes moved during drafting. Integration
  must re-read, not trust the draft's §1 table.
- The observed no-delta result is bounded to one host, one filesystem, normal
  SHA-1 loose-object repositories; packs, promisor, alternates, submodules,
  hooks, bare/linked manifest diffs and concurrent writers are untested. It is
  not certification and not deletion authority; certification remains OFF.
- The probe's promisor refusal is a config-guard design claim until a fixture
  case exercises it; S037 is the reason it matters (object-info errors are
  skipped, zero exit is not complete accounting).
- `git repo structure` is EXPERIMENTAL on 2.55.0; the recheck is on-release.
- No live fleet repo was probed; `census/operator-sweep-20261019/` was not
  opened, scanned, staged or modified.

## Tooling record

No install or upgrade; nothing to report beyond the host's `git 2.55.0` and
the Python runtime used for the disposable fixture. No credentials read.
