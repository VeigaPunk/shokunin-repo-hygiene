# Round-29 landing checklist (ordered, executed at base)

Base: lane `691dd29211c53d0ef94fa072394cb9c8a69fe92e` (prompt base) / measured tip
`b8cb4b31ce80e2e3314b88e85d40ea9873180804` (preregistration commit, branch `master`,
ahead=0 behind=0). Every "observed" line below was produced by me this run; nothing here is
inferred. All commands are absolute and read-only except the two landing commits, which go
through the lane/fleet helpers only.

Run in this order. Steps 0–5 must all be green before step 7; step 6 is measured at the same
tip and read again after landing.

## 0. Lane worktree must be empty (input the pre-report gate needs)

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain=v1 --untracked-files=all
```

Observed at base (NOT empty):

```
 M .ufo/waves/round-26/w1/ScribeGateDraft.md
```

Expected at round end: no output (rc 0). `.ufo/waves/` is gitignored, so wave reports and
delivery files never appear here; only tracked-file edits do. Resolve the one above per prompt
§6.5 (commit it under the round-26 entry through `jj-lane.sh`, or restore it from the branch with
`git -C /home/vgpnk/Projects/shokunin/souji-shokunin show master:.ufo/waves/round-26/w1/ScribeGateDraft.md > /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/ScribeGateDraft.md`)
and name it in the report. Until then `check-clean` in step 5 is `FAIL` and the gate exits 1.

## 1. Authoritative lane tip, full 40 hex

```sh
/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin
```

Observed at base (rc 0, single line):

```
state branch=master local=b8cb4b31ce80e2e3314b88e85d40ea9873180804 remote=b8cb4b31ce80e2e3314b88e85d40ea9873180804 ahead=0 behind=0 head=detached tracked=1 untracked=0
```

Fields: `local=` is the branch tip to cite and to pass as `--rev`; `remote=` is the *local*
`refs/remotes/origin/master` and can be stale — step 2 is authoritative. Require `ahead=0
behind=0` and `tracked=0 untracked=0` at the end. `head=detached` is normal after the first
helper commit. `tracked=1` at base is the step-0 file.

```sh
TIP=$(/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin | sed -n 's/.* local=\([0-9a-f]\{40\}\).*/\1/p'); echo "$TIP"
```

## 2. The remote branch really carries that tip

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-remote origin refs/heads/master
```

Observed at base (rc 0, tab-separated, field 1 is the sha):

```
b8cb4b31ce80e2e3314b88e85d40ea9873180804	refs/heads/master
```

Expected: the byte-identical 40-hex of `$TIP`. Older hash = your commits are not on the branch;
land them through `jj-lane.sh commit` (never plain git, never force). This is the same check the
pre-report gate runs, but run standalone too: the gate swallows git's stderr.

## 3. Census exit 0, recorded before → after

```sh
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji > /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/records/census-end.txt 2>&1
echo "exit=$?" >> /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/records/census-end.txt
```

Observed at base (rc 0, 36 lines; the r29 start record has 37 — 36 + the `exit=` line, same
convention):

```
souji	W04	S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
exit=0
```

Required at round end: rc 0 and a last functional line `souji<TAB>ok<TAB>…/corpus/SOURCES.md`.
`W04` warnings are cross-scope duplicates and never change lane status. Exit meanings:
0 clean/warnings only, 1 `E`/overdue findings, 2 usage/missing registry, 3 selftest failure.
Cross-check the C3 row target with the census-mode command (prints counts, rc 0 at base with
`souji rows 139`; target 143):

```sh
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin souji
```

## 4. Report carries exactly one SHONEN heading

```sh
grep -c '^## SHONEN' /home/vgpnk/Projects/shokunin/.ufo/reports/round-29/souji.md
```

Expected `1`. Verified: with the heading the command prints `1` rc 0; with none it prints `0`
rc 1 (grep's rc is the count test, so do not chain it with `&&`). The round-28 filed report has
exactly this shape. Then one `[~]`/`[ ]` line per SHONEN box — `SHONEN.md` currently has 4
(`grep -c '^- \[[~ ]\]' /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md` → `4`).

## 5. Pre-report gate (5 checks, one rc)

Inputs, all required, all absolute: `--lane` lane repo root, `--branch` branch name without
`/`, `..` or a leading `-` (`master`), `--report` the fleet report file (must already exist and
be non-empty; it lives outside the lane so it never dirties `--lane`), `--prereg` the frozen
preregistration file (must exist and be non-empty). Internally it needs: `refs/heads/<branch>`
resolvable to 40–64 hex, a queryable `origin` for `ls-remote --exit-code origin
refs/heads/<branch>`, whose first line is `<sha>\t<ref>` and whose field 1 must equal the local
sha; exactly one `^## SHONEN` in the report; empty `git status --porcelain=v1
--untracked-files=all` in the lane.

```sh
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-pre-report-gate.sh \
  --lane /home/vgpnk/Projects/shokunin/souji-shokunin \
  --branch master \
  --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-29/souji.md \
  --prereg /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/records/preregistration.txt
```

Green shape (verified, rc 0): five lines `check-tip=PASS`, `check-report=PASS`,
`check-shonen=PASS`, `check-clean=PASS`, `check-prereg=PASS`.

Exit codes, each verified in a scratch clone at base:

| rc | meaning | verified output |
|---|---|---|
| 0 | all five PASS | the five `=PASS` lines |
| 1 | ≥1 check FAIL (a finding) | `check-*` lines with at least one `FAIL`; detail on stderr (`detail-tip:`, `detail-shonen: found 0 headings, expected 1`, `detail-clean: ?? stray.txt`) |
| 2 | usage only, no check ran | `Usage: bash tools/souji-pre-report-gate.sh --lane ABS --branch NAME --report ABS --prereg ABS` on stderr |

A tip failure prints `detail-tip: local=<sha> remote=<none>` when `ls-remote` itself failed
(unreachable/unauthorised) and `remote=<other sha>` when the branch is behind; rerun step 2 to
see git's own error. `rc 2` never means "clean" — it means the invocation was rejected.

## 6. Landing gate at the same tip

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev b8cb4b31ce80e2e3314b88e85d40ea9873180804 \
  --round 29 \
  --base 691dd29211c53d0ef94fa072394cb9c8a69fe92e \
  --fleet-root /home/vgpnk/Projects/shokunin
echo "rc=$?"
```

Expected at round end with the reports as filed (measured at base, rc 2):

```
SUMMARY	findings=0	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-29/ at b8cb4b31ce80e2e3314b88e85d40ea9873180804
```

(the summary line on stdout, the `COULD-NOT-EVALUATE` line on stderr).

**What rc 2 means here.** `.ufo/waves/` is gitignored, so the gate's carry check enumerates
`tree(.ufo/waves/round-29/**.md)` at `--rev` and finds none; `check_carry` raises
could-not-evaluate, the error wins the exit code over any findings, and the summary prints with
`checked_reports=0`. This is the r28-closure routing (defect 3): for rounds ≥27 the report check
can never evaluate committed reports. rc 2 is **neither a pass nor a finding**:

| tell | rc 2 could-not-evaluate | rc 1 findings |
|---|---|---|
| stderr | `COULD-NOT-EVALUATE<TAB><reason>` | empty |
| `checked_reports` | `0` (carry never ran) | `>0` once reports are enumerable |
| stdout | `SUMMARY` only, plus any independent `LG-*` lines | one `LG-<ID><TAB>path<TAB>detail` per finding |

Findings are retained even when the exit is 2, so **any `LG-*` line is real** and must be fixed;
only the absent `COULD-NOT-EVALUATE` line distinguishes a fully evaluated clean run.

Two base facts you need to read the summary: (a) without `--fleet-root` the gate reports three
pre-existing `LG-DANGLING-PTR` (`corpus/README.md:217` ×2 and
`corpus/knowledge/jj-colocation-receipts.md:148`, citing `../.ufo/waves/hyaku/jj-w1/reports/…`
paths that live in the fleet repo); with `--fleet-root /home/vgpnk/Projects/shokunin` they are
classified `fleet` and `findings=0`, so keep the flag. (b) `rc 2` from a bad `--rev` also prints
`SUMMARY findings=0` with every counter 0 and `COULD-NOT-EVALUATE cannot resolve revision …
git rev-parse --verify failed` — that shape means the revision never resolved; do not confuse it
with the no-reports shape above.

**To actually evaluate the carry check**, force the reports into a scratch clone (never do this
in the lane). Verified mechanics: with one committed report and a `corpus/lessons/round-29.md`
present the gate prints `SUMMARY … carry_heading=1 checked_reports=1` and returns rc 0 with
`--fleet-root`; without `--fleet-root` the same synthetic run returned rc 1 with the three
pointer findings above.

```sh
# TRAP: `git clone --no-local <lane> <dir>` leaves origin pointing AT the lane. Repoint it at a
# throwaway bare repo before running anything that pushes, or just never push here.
D=$(mktemp -d /var/tmp/souji-r29-landing.XXXXXX)
git -C "$D" init -q --bare origin.git
git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin "$D/c"
git -C "$D/c" remote set-url origin "$D/origin.git"
mkdir -p "$D/c/.ufo/waves/round-29"
cp -a /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1 "$D/c/.ufo/waves/round-29/"
git -C "$D/c" add -f .ufo/waves/round-29
git -C "$D/c" -c user.name=labrat -c user.email=labrat@example.invalid commit -qm scratch
python3 -B "$D/c/tools/souji-landing-gate.py" --root "$D/c" \
  --rev "$(git -C "$D/c" rev-parse refs/heads/master)" --round 29 \
  --fleet-root /home/vgpnk/Projects/shokunin; echo "rc=$?"
rm -rf "$D"
```

Expected there: rc 0 and `findings=0 … carry_heading=1 checked_reports=<number of .md in w1>`
only if every failing `STATUS:` in those reports is carried into `corpus/lessons/round-29.md`
`## Seat-reported failures`; otherwise rc 1 with `LG-SEAT-UNCARRIED` per uncarried marker.

## 7. Land the report last (fleet repo, helper only)

```sh
/home/vgpnk/Projects/shokunin/scripts/hyaku/fleet-commit.sh --as souji -m "round-29: souji report" \
  -- .ufo/reports/round-29/souji.md
git -C /home/vgpnk/Projects/shokunin status --porcelain -- .ufo/reports/round-29/souji.md
```

Cite only the helper's final `landed <hash>` after its remote verification. rc 0 = committed and
pushed (or nothing to commit); rc 1 = commit failed; rc 3 = committed locally, push failed —
resolve and retry, never force; rc 64 = usage. The second command must print nothing. The report
must cite the step-1 `local=` tip.

## 8. Final state re-read

```sh
/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-remote origin refs/heads/master
```

Expected: `local=` unchanged, `ahead=0 behind=0`, `tracked=0 untracked=0`, and step 8's
`ls-remote` line identical to `local=`.

## Inputs the two gates demand, in one place

| gate | inputs | green |
|---|---|---|
| pre-report | lane abs path; branch name (`master`); existing non-empty report abs path; existing non-empty prereg abs path; local branch sha resolvable; `origin` reachable and its `refs/heads/master` first-line field 1 == local sha; exactly one `^## SHONEN`; empty `status --porcelain --untracked-files=all` | rc 0, five `=PASS` |
| landing | lane abs path; full-40 rev; `--round 29`; `--base 691dd29…`; `--fleet-root /home/vgpnk/Projects/shokunin`; (report .md committed under `.ufo/waves/round-29/` only ever true in scratch) | rc 0, `SUMMARY findings=0`, no `COULD-NOT-EVALUATE`; in the lane the expected terminal shape is rc 2 with that line and `checked_reports=0` |
