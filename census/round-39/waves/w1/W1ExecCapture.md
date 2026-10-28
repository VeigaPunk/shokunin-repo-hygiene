# W1ExecCapture — wave-evidence capture path (R4)

Role: executor (leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
(lane HEAD at run time `094e53131098aff1d9b8a12f2001a1d599d84252`; frozen base
`ed30b7f5b77939c9073348d810730bc4f355708d`).
Scratch: `/fast/scratch/hyaku/souji-r39/W1ExecCapture` — created, used, and **removed**
(`rm -rf -- "$S"`; `ls` confirms `No such file or directory`).

I ran no mutating git/jj command in the lane or the fleet root. Two `mktemp -d` scratch git
repos were created and committed in (root-asserted with
`git -C "$D" rev-parse --show-toplevel` == `$D` before the first commit), which is the
fixture protocol of the hard rules; no lane/ fleet bytes were touched by them.

## Subject

- tool: `tools/souji-wave-evidence-capture.sh` (614 lines)
- fixture: `tests/fixtures/r28-wave-evidence-capture.sh` (15 cases, v2 layout)

## Bottom line

| check | verdict |
|---|---|
| C0 guessed CLI `--out <dir>` exists | **FAIL (no such flag)** — usage banner + rc 1 |
| C1 real CLI accepted | **PASS** — `<lane-abs> <round-N> [--verify [--rev <full40>]]` |
| C2 capture of round 39 into a scratch lane target | **PASS** — `records=13`, rc 0 |
| C3 `--verify` (disk) | **PASS** — rc 0, `records=13` |
| C4 `--verify --rev <full40>` over a commit | **PASS** — `failed=0 uncovered=0`, rc 0 |
| C5 first-falsification: tampered committed blob | **PASS** — `failed=1`, rc 4 |
| C6 non-commit revision (`--rev <blob>`) | **PASS (refused)** — `error: unknown revision`, rc 1 |
| C7 round-38 waves capturable by the same command | **PASS** — `records=93`, rc 0 in scratch |
| C8 tool's own 15-case fixture | **PASS** — `cases=15 pass=15 control=TAMPER-REJECTED`, rc 0 |
| C9 does a receipt already exist for r38/r39 at lane HEAD | **NO** — `manifest.sha256 missing at ...` rc 4 (R4 reproduced) |

R4's operability precondition is therefore **sound and exercisable**: the capture command works,
its own fixture is green, and committed-bytes verification genuinely discriminates. What is
missing is not tool capability but the act — no receipt exists at HEAD for either round, and the
source `.ufo/waves/` is git-ignored, so only the L1's landing can close R4 (see "For the L1").

## C0 — the guessed CLI in the ticket does not exist

```
$ bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh \
    /home/vgpnk/Projects/shokunin/souji-shokunin 39 --out /fast/scratch/hyaku/souji-r39/W1ExecCapture/capture
Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]
  <lane-abs> absolute path to the lane repo root
  <round-N>  integer round number
  --verify   re-verify an existing receipt (no copy)
  --rev H    with --verify: verify against the tree committed at H
rc=1
```

Verdict: the ticket's `--out` guess is wrong; the banner is the real contract. **There is no
output redirection flag at all.** `tools/souji-wave-evidence-capture.sh:597` hard-codes
`waves_rel = 'census/round-%s/waves' % round_s`, so the only way to capture into a scratch target
is to give the tool a scratch *lane root*. I did exactly that: a `mktemp -d` git repo seeded
with a `cp -a` copy of the real `.ufo/waves/round-39` plus the lane's `.gitignore`.

## C1/C2 — real CLI; round-39 capture into a scratch lane

Setup (exact):

```
S=/fast/scratch/hyaku/souji-r39/W1ExecCapture
D=$(mktemp -d "$S/lane39.XXXXXX") && git -C "$D" init -q           # D=lane39.rhVFsx
test "$(git -C "$D" rev-parse --show-toplevel)" = "$D" && echo "ROOT-OK $D"
ROOT-OK /fast/scratch/hyaku/souji-r39/W1ExecCapture/lane39.rhVFsx
cp -a "$LANE/.gitignore" "$D/.gitignore"; mkdir -p "$D/.ufo/waves"
cp -a "$LANE/.ufo/waves/round-39" "$D/.ufo/waves/round-39"         # 12 files at 14:47
```

Capture:

```
$ bash "$LANE/tools/souji-wave-evidence-capture.sh" "$D" 39
captured+verified: /fast/scratch/.../lane39.rhVFsx/.ufo/waves/round-39 -> /fast/scratch/.../lane39.rhVFsx/census/round-39/waves
records=13 renames=0 excluded=0 symlinks=0
rc=0
```

Receipt on disk: 14 files = the 12 source files + `summary.tsv` + `manifest.sha256`; the manifest
carries 13 records (the 13 in `expected`, manifest itself excluded). `summary.tsv` was header-only
(`name	agent	id	status	final_output_available`) because round 39 has no `w1-results.json` yet —
`write_summary()` (`:347`) reads only `<*-results.json>` in the source root.

Verdict: **PASS.** `records=13` is arithmetically the source file count plus the summary file; the
`captured+verified` line means capture re-verified its own manifest *and* the receipt/source
set identity before exiting 0.

## C3/C4 — `--verify` and `--verify --rev`

```
$ bash "$LANE/tools/souji-wave-evidence-capture.sh" "$D" 39 --verify
verified: /fast/scratch/.../lane39.rhVFsx/census/round-39/waves
records=13
rc=0

$ git -C "$D" add -A
$ git -C "$D" -c user.name=fixture -c user.email=fixture@example.invalid commit -q -m 'r39 receipt'
$ rev=$(git -C "$D" rev-parse HEAD); echo "rev=$rev"
rev=cd4580be294251b174882e37a6c63c4865982bfa

$ bash "$LANE/tools/souji-wave-evidence-capture.sh" "$D" 39 --verify --rev "$rev"
verify-rev rev=cd4580be294251b174882e37a6c63c4865982bfa records=13 failed=0 uncovered=0
rc=0
```

Because the scratch repo carried the lane's `.gitignore` (`.ufo/waves/`), the commit contains
**no** `.ufo/` path — `git -C "$D" ls-tree -r --name-only HEAD | grep -c '^\.ufo/'` printed `0`.
That is the R4 property proven on scratch bytes: the receipt verifies by revision while the wave
source was never tracked.

Argument-guard probes (same run):

```
$ bash "$T" "$D" 39 --rev cd4580be...      -> error: --rev requires --verify          rc=1
$ bash "$T" "$D" 39 --verify --rev HEAD    -> Usage: ... (full 40-hex required)       rc=1
```

Verdict: **PASS.** `--verify` works over a revision, and refuses shorthand revisions loudly.

## C5/C6 — first falsification (the check only counts if it can fail)

```
$ printf 'tampered\n' >> "$D/census/round-39/waves/w1-dispatch.json"
$ git -C "$D" add -A && git -C "$D" … commit -q -m tamper
rev2=01357f0850e86ea7604775d70870da4882b720bb

$ bash "$T" "$D" 39 --verify --rev "$rev2"
verify-rev rev=01357f0850e86ea7604775d70870da4882b720bb records=13 failed=1 uncovered=0
rc=4

$ blob=$(git -C "$D" rev-parse "$rev2:census/round-39/waves/w1-spec.json")
blob=20915543029dccfb6d3c88c7a9e06334a85ace78
$ bash "$T" "$D" 39 --verify --rev "$blob"
error: unknown revision: 20915543029dccfb6d3c88c7a9e06334a85ace78
rc=1
```

The same tamper also broke plain `--verify` on that discriminator (`verification failed: manifest
does not match the receipt bytes`, rc 4 when re-run later), so disk verify hashes payload bytes,
not just the manifest — consistent with fixture case 13.

Verdict: **PASS, non-vacuous.** A one-line payload edit flips `failed=0`→`failed=1` and rc 0→4.

## C7 — can round 38's waves be captured by the same command? Yes; 93 records

```
$ D38=$(mktemp -d "$S/lane38.XXXXXX") && git -C "$D38" init -q   # lane38.QDgjb9
$ test "$(git -C "$D38" rev-parse --show-toplevel)" = "$D38" && echo ROOT-OK   -> ROOT-OK
$ cp -a "$LANE/.gitignore" "$D38/.gitignore"; mkdir -p "$D38/.ufo/waves"
$ cp -a "$LANE/.ufo/waves/round-38" "$D38/.ufo/waves/round-38"    # 92 files, 2.0M
$ bash "$LANE/tools/souji-wave-evidence-capture.sh" "$D38" 38
captured+verified: /fast/scratch/.../lane38.QDgjb9/.ufo/waves/round-38 -> /fast/scratch/.../lane38.QDgjb9/census/round-38/waves
records=93 renames=0 excluded=0 symlinks=0
rc=0
```

Contents actually captured (94 files on disk = 92 source files + `summary.tsv` + `manifest.sha256`;
93 manifest records):

- specs: `w1-spec.json`, `w2-spec.json`
- dispatches: `w1-dispatch.json`, `w2-dispatch.json`
- results: `w1-results.json`, `w2-results.json`
- seat reports: `w1/*.md` (43) + `w2/*.md` (32), plus `w1/swarm-registry.json`, `w2/swarm-registry.json`
- wave plumbing: `gen-w1-spec.py`, `gen-w2-spec.py`, `report-draft.md`,
  `w1.ready`, `w1.ready.dispatched`, `w2.ready`, `w2.ready.dispatched`,
  `w1-validation.err`, `w2-validation.err` (both empty)
- `summary.tsv`: 74 seat rows (42 from w1 + 32 from w2), all with `final_output_available=1`

So round 38 is capturable by one command and would add **94 new git paths** under
`census/round-38/waves` (93 records + manifest). Those 94 paths are all new: at lane HEAD
`git ls-tree -r --name-only HEAD -- census/round-38/waves census/round-39/waves` printed nothing
(`wc -l` → `0`), and `census/round-38/` on disk holds only `cells.tsv`, `preregistration.txt`,
`records/`.

## C8 — the tool's own fixture, green on current bytes

```
$ SOUJI_CAPTURE_TOOL="$LANE/tools/souji-wave-evidence-capture.sh" \
  SOUJI_R29_C2FIXTURE_BASE="$S/fixture" TMPDIR="$S/fixture" \
  bash "$LANE/tests/fixtures/r28-wave-evidence-capture.sh"
tool=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh
… case-1..case-15: PASS …
cases=15 pass=15 control=TAMPER-REJECTED
rc=0
```

All 15 cases pass, including cases 7/8/9/10/12/15 which each end in `verify-rev … failed=0
uncovered=0`, case 11 (`verify-rev … failed=1` → rc 4 tamper control) and case 14 (usage rc 1).
`control=TAMPER-REJECTED` fired, so the suite itself is non-vacuous. Warnings
`lane is not a git work tree; ignore rules not evaluated` appear only for the non-git cases
(1/3/6/13) — expected by design.

## C9 — no receipt exists at the lane's real HEAD (R4 reproduced)

```
$ R=$(git -C "$LANE" rev-parse HEAD); echo "HEAD=$R"
HEAD=094e53131098aff1d9b8a12f2001a1d599d84252
$ bash "$LANE/tools/souji-wave-evidence-capture.sh" "$LANE" 38 --verify --rev "$R"
error: manifest.sha256 missing at 094e53131098aff1d9b8a12f2001a1d599d84252:census/round-38/waves
rc=4
$ bash "$LANE/tools/souji-wave-evidence-capture.sh" "$LANE" 39 --verify --rev "$R"
error: manifest.sha256 missing at 094e53131098aff1d9b8a12f2001a1d599d84252:census/round-39/waves
rc=4
```

Both calls are read-only (`rev-parse`/`ls-tree`/`cat-file`); `census/round-39/` on disk was
unchanged afterwards (`__pycache__ c1-counter.py c1-items.tsv c2-counter.py c3-counter.py
preregistration.txt records`).

Ignore map on the real lane:

```
$ git check-ignore -v .ufo/waves/round-39/w1-spec.json
.gitignore:1:.ufo/waves/	.ufo/waves/round-39/w1-spec.json      rc=0   -> source is ignored
$ git check-ignore -v census/round-39/waves/x.tsv census/round-38/waves/x.tsv
rc=1                                                                  -> receipts are committable
```

## For the L1 (what the R4 close needs, precisely)

1. Run, at a quiescent moment after w1 seat reports have landed:
   `bash tools/souji-wave-evidence-capture.sh /home/vgpnk/Projects/shokunin/souji-shokunin 39`
   from the lane root. It writes `<lane>/census/round-39/waves/` (13 records today: 12 source
   files + `summary.tsv`; 14 files with the manifest). My report file is one more source file, so
   the number will read 14 records / 15 files if captured after it lands. Do **not** expect a
   `--out` flag; there is none.
2. Land the receipt dir (it is not git-ignored), then the closing evidence is
   `bash tools/souji-wave-evidence-capture.sh <lane> 39 --verify --rev <landing-40hex>`
   printing `verify-rev … failed=0 uncovered=0`, rc 0.
3. Optional, and cheap: round 38 can be backfilled with the same command on the same bytes —
   `records=93`, 94 new paths, 74 summary rows. It costs no new tooling.

## Operability findings the round should know (observed, not fixed — outside my write scope)

1. **No output redirection.** Destination is `<lane>/census/round-<N>/waves` unconditionally
   (`:597`). Any "capture without touching the lane" run must fabricate a scratch lane root; the
   ticket's `--out <scratch>` is not implementable against these bytes.
2. **Snapshot, not freshness.** Verification never consults the source directory. After adding
   `w1/ZzLateSeat.md` to a pristine round-38 source, `--verify` still printed
   `verified: … records=93` rc 0, and `--verify --rev` on the earlier commit also stayed rc 0.
   A stale receipt is indistinguishable from a fresh one by the tool's own checks; capture must
   therefore be the last write before landing, and freshness has to be argued from timing, not
   from a receipt field. (Recommended, if the round wants it: an r39 item.)
3. **`summary.tsv` is schema-dependent and silently degrades.** For round 38's results files the
   `output` field is a flat report object (`files_changed`, `assigned_commands`, …), not the
   `{'text': '<json>'}` envelope `write_summary()` (`:347`) expects, so all 74 rows carry
   `status` empty and `id` empty (`with-id 0/42` and `0/32` in the results JSONs) while
   `final_output_available=1` on every row. The receipt is byte-faithful; the summary columns are
   just not informative for this schema. Any consumer that reads `status` from `summary.tsv` for
   r38 would read blanks.
4. **Non-commit revision class differs from C2's subject.** `--rev <blob>` gives
   `error: unknown revision: …` rc 1, not the `REFUSAL REV-UNRESOLVED` / rc 2 class that C2's L1/L2
   legs require of `tools/souji-citation-reconcile.py`. That is this tool's own exit-code contract
   (`1 usage error / unrepresentable revision`) and is not a C2 leg; recorded so the round does not
   conflate the two revisions contracts.
5. **Concurrent write during capture is caught per file, not globally.** `h_src`/`h_dst` are
   compared after each `copyfile` (`die(5, 'copy mismatch for %s')`, `:477`), so a file mutated
   mid-copy fails the run; a file mutated *after* its copy is simply not in the snapshot. No lock,
   by design.

## Tooling

None installed or upgraded; no package channel used. `bash`, `git` (read-only in the lane),
`python3` and `mktemp` were sufficient.

## Evidence honesty

Every line quoted above was produced by the command shown in the same session. Two numbers are
scenario-dependent and labelled as such: the round-39 record count (13 at 14:47, grows with each
landing seat report) and the round-38 backfill count (93 records, stable — the round is closed).
The scratch tree `/fast/scratch/hyaku/souji-r39/W1ExecCapture` was removed; nothing of this seat
remains on disk except this report and the lane's untouched state.
