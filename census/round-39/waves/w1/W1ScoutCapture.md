# W1ScoutCapture — wave-evidence capture and `.ufo` ignore

Seat: W1ScoutCapture (scout). Axis: operability.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
HEAD observed this run: `2201778e7736af82e7d8a42dec2494f115bf3923`.
No capture was run against the live lane (it would write `census/round-39/waves/`). No git/jj mutation. No scratch left on disk. No tool install.

## Verdicts

| Check | Verdict |
|---|---|
| What hides `.ufo/waves/` | PASS — root `.gitignore:1` pattern `.ufo/waves/` only. Line 2 does not match. Line 3 matches `__pycache__/` under a census receipt, not under `.ufo/waves/` (parent exclusion wins). `info/exclude` and `core.excludesFile` add nothing. |
| What the capture tool accepts and writes | PASS — usage and writers read; usage, `--rev` without `--verify`, missing source, and `--verify --rev` exercised. Fixture source read (15 cases). Fixture not executed this run. |
| How round 26 and round 29 were captured | PASS — introducing and recapture commits named from `git log`; receipt roots listed from `git ls-tree`. |
| Exact command for a verifiable round-39 record | PASS — command stated below. `--verify --rev` at current HEAD exits 4 because `census/round-39/waves` is not committed. Capture itself not run. |
| Files required before capture | PASS — tool requires only the source directory. Spec, dispatch, results, and seat reports are the wave set both historical receipts contain; round 39 is missing results and is mid-wave. |

## 1. Ignore rules that hide `.ufo/waves/`

`.gitignore` is three lines:

```
.ufo/waves/
census/operator-sweep-*/
__pycache__/
```

Command:

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
git -C /home/vgpnk/Projects/shokunin/souji-shokunin check-ignore -v -- \
  .ufo/waves/ .ufo/waves/round-39/ .ufo/waves/round-39/w1-spec.json \
  .ufo/waves/round-39/w1-dispatch.json .ufo/waves/round-39/w1/W1ScoutCapture.md \
  .ufo/waves/round-39/w1/__pycache__/x.pyc \
  census/round-39/waves/manifest.sha256 census/round-39/waves/__pycache__/x.pyc
git -C /home/vgpnk/Projects/shokunin/souji-shokunin check-ignore --no-index -v -- \
  .ufo/waves/round-39/w1-spec.json .ufo/waves/round-39/w1/__pycache__/x.pyc \
  census/round-39/waves/w1/seat.md census/round-39/waves/__pycache__/x.pyc \
  census/operator-sweep-probe/x
git -C /home/vgpnk/Projects/shokunin/souji-shokunin config --show-origin --get core.excludesFile
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain=v1 -- .ufo/waves/round-39
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain=v1 --ignored -- \
  .ufo/waves/round-39/w1-spec.json .ufo/waves/round-39/w1-dispatch.json
```

Observed:

```
/home/vgpnk/Projects/shokunin/souji-shokunin
2201778e7736af82e7d8a42dec2494f115bf3923
.gitignore:1:.ufo/waves/	.ufo/waves/round-39/
.gitignore:1:.ufo/waves/	.ufo/waves/round-39/w1-spec.json
.gitignore:1:.ufo/waves/	.ufo/waves/round-39/w1-dispatch.json
.gitignore:1:.ufo/waves/	.ufo/waves/round-39/w1/W1ScoutCapture.md
.gitignore:1:.ufo/waves/	.ufo/waves/round-39/w1/__pycache__/x.pyc
.gitignore:3:__pycache__/	census/round-39/waves/__pycache__/x.pyc
check-ignore-rc=0
.gitignore:1:.ufo/waves/	.ufo/waves/round-39/w1-spec.json
.gitignore:1:.ufo/waves/	.ufo/waves/round-39/w1/__pycache__/x.pyc
.gitignore:3:__pycache__/	census/round-39/waves/__pycache__/x.pyc
.gitignore:2:census/operator-sweep-*/	census/operator-sweep-probe/x
no-index-rc=0
core.excludesFile=(unset)
0
!! .ufo/waves/round-39/
```

`.git/info/exclude` is the stock comment template (6 lines). Non-comment patterns: none.

Index-aware `check-ignore` on already-tracked `.ufo/waves/round-26/w1-spec.json` and the nested `vadv-49/.gitignore` printed nothing (`tracked-check-rc=1`). `--no-index` still attributes both to `.gitignore:1:.ufo/waves/`. The rule hides untracked wave bytes from `status`; it does not hide modifications of paths that were tracked before the rule. `census/round-N/waves/` is not matched by line 1, so a receipt is committable. Line 3 does hide `__pycache__/` inside that receipt; the capture tool accounts those in `excluded.tsv` instead of copying them.

Tracked nested `.gitignore` files under `.ufo/waves/round-26/assimilation/...` are source content inside the ignored tree, not additional rules that hide `.ufo/waves/`.

## 2. What `tools/souji-wave-evidence-capture.sh` accepts and writes

Usage (header lines 8-10 and `usage()`, confirmed by running it):

```
bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N>
bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> --verify
bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> --verify --rev <full40>
```

`<lane-abs>` must be absolute and must not contain `..`. `<round-N>` must be an integer. `--rev` is refused unless `--verify` is also set, and must be 40 hex digits.

Command:

```
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh \
  /home/vgpnk/Projects/shokunin/souji-shokunin 39 --rev ed30b7f5b77939c9073348d810730bc4f355708d
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh \
  /home/vgpnk/Projects/shokunin/souji-shokunin 99
```

Observed:

```
Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]
  <lane-abs> absolute path to the lane repo root
  <round-N>  integer round number
  --verify   re-verify an existing receipt (no copy)
  --rev H    with --verify: verify against the tree committed at H
usage-rc=1
error: --rev requires --verify
rev-without-verify-rc=1
error: source directory not found: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-99
missing-src-rc=2
```

Source is `<lane>/.ufo/waves/round-<N>/`. Destination is `<lane>/census/round-<N>/waves/`. Capture clears the destination, copies regular files byte-exact, renames `.gitignore` / `.gitattributes` / any `.git` component to `.captured` (`renames.tsv`), copies symlinks verbatim (`symlinks.tsv`, not in the manifest), and records destination paths that `git check-ignore --no-index` would ignore in `excluded.tsv` (reason `ignored`). A fifo/socket/device is exit 3. Then it writes:

- `manifest.sha256` — GNU sha256 records, `LC_ALL=C` byte-sorted, every regular receipt file except the manifest itself. Newline or backslash in a name is a backslash-escaped record.
- `summary.tsv` — header `name agent id status final_output_available`, plus one row per seat in every top-level `*-results.json`. No results file means header only.
- `renames.tsv` / `excluded.tsv` / `symlinks.tsv` — only when they have rows.

Success lines in the tool: `captured+verified: <src> -> <dst>` plus `records= renames= excluded= symlinks=`; disk `--verify` prints `verified: <dst>`; `--verify --rev` prints `verify-rev rev=<H> records=<n> failed=<n> uncovered=<n>` and exits 0 only when both counters are 0. Exit map: 0 verified, 1 usage/unknown revision, 2 source missing, 3 refusal, 4 verification failed, 5 copy/write failure.

Fixture `tests/fixtures/r28-wave-evidence-capture.sh` (read, not run) declares 15 cases and the summary line `cases=15 pass=<n> control=TAMPER-REJECTED`. Cases: (1) two files including `w1-results.json`, (2) missing source rc 2, (3) tampered manifest, (4) fifo rc 3, (5) `..` in the lane rc 1, (6) empty directory rc 0, (7) nested `.gitignore` stored as `.captured` and `--verify --rev`, (8) `__pycache__` excluded, (9) symlink in `symlinks.tsv`, (10) newline name GNU-escaped, (11) post-commit blob tamper rc 4, (12) `.git` stored as `.git.captured`, (13) disk payload tamper rc 4, (14) non-numeric round rc 1, (15) absolute and relative symlink targets kept verbatim. Scratch repos are created with `git -C` and root-checked before the first commit. This seat did not execute the fixture, so no `cases=15 pass=15` claim is made from this run.

## 3. How round 26 and round 29 were captured

Command:

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%H %ad %s' --date=short -- \
  census/round-26/waves/manifest.sha256
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%H %ad %s' --date=short -- \
  census/round-29/waves/manifest.sha256
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --format='%H%n%s' --name-status \
  b86200714069022954a3b498cf697d894119b45e -- \
  tools/souji-wave-evidence-capture.sh tests/fixtures/r28-wave-evidence-capture.sh \
  census/round-26/waves/manifest.sha256 census/round-26/waves/renames.tsv \
  census/round-26/waves/excluded.tsv census/round-26/waves/symlinks.tsv
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only \
  765fe8bd602ac679d01e7a0790711485209ab8bd:census/round-26/waves
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only HEAD:census/round-26/waves
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only HEAD:census/round-29/waves
```

Round 26, first capture — commit `765fe8bd602ac679d01e7a0790711485209ab8bd` (2026-10-25, `round-28: repair pointers, curate F4 primitives, capture wave evidence`). Tree root at that commit:

```
assimilation  census-before.txt  make-spec.py  manifest.sha256
preregistration.txt  preregistration-amendment-1.txt  preregistration-amendment-2.txt
summary.tsv  w1  w1-dispatch.json  w1-results.json  w1-spec.json
w1-validate.err  w1-validate.out  w1.ready  w1.ready.dispatched
```

`renames.tsv`, `excluded.tsv`, and `symlinks.tsv` are absent there (`git cat-file -e` ABSENT). That is the v1 disk capture: the tool copied `.ufo/waves/round-26/` into `census/round-26/waves/` and wrote `manifest.sha256` plus `summary.tsv`. The committed r28 seat report quotes the invocation `bash tools/souji-wave-evidence-capture.sh /home/vgpnk/Projects/shokunin/souji-shokunin 26`. Markdown files in that tree: 492.

Round 26, v2 recapture — commit `b86200714069022954a3b498cf697d894119b45e` (2026-10-25, `round-29: C2 capture tool v2 (committed-bytes receipts), fixture 15 cases, r26 recapture`). Name-status:

```
A  census/round-26/waves/excluded.tsv
M  census/round-26/waves/manifest.sha256
A  census/round-26/waves/renames.tsv
A  census/round-26/waves/symlinks.tsv
M  tests/fixtures/r28-wave-evidence-capture.sh
M  tools/souji-wave-evidence-capture.sh
```

Those three added ledgers are exactly what the v2 tool writes and the v1 tool did not. The only capture form the tool accepts for that round is:

```
bash tools/souji-wave-evidence-capture.sh /home/vgpnk/Projects/shokunin/souji-shokunin 26
```

HEAD `excluded.tsv` starts `# path	sha256	reason` and its first data rows are `__pycache__` `.pyc` files with reason `ignored`. `renames.tsv` starts `# original	stored` and stores nested `.gitignore` as `.gitignore.captured`. `symlinks.tsv` starts `# path	target`. Markdown count at HEAD: 494. This seat did not re-run the recapture.

Round 29 — commit `de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b` (2026-10-25, `round-29: lesson, scorecard, log, wave evidence capture, end census`) is the only commit that adds `census/round-29/waves/manifest.sha256`. Tree root:

```
make-spec.py  manifest.sha256  summary.tsv
w1  w1-dispatch.json  w1-results.json  w1-run.err  w1-spec.json
w1.ready  w1.ready.dispatched
```

No `renames.tsv` / `excluded.tsv` / `symlinks.tsv` (the tool writes those only when non-empty). `summary.tsv` is 69 lines (header plus 68 seats). Markdown count: 86. Same capture form, round number 29:

```
bash tools/souji-wave-evidence-capture.sh /home/vgpnk/Projects/shokunin/souji-shokunin 29
```

Committed-bytes check, run this seat:

```
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh \
  /home/vgpnk/Projects/shokunin/souji-shokunin 29 \
  --verify --rev 2201778e7736af82e7d8a42dec2494f115bf3923
```

Observed: `verify-rev rev=2201778e7736af82e7d8a42dec2494f115bf3923 records=131 failed=0 uncovered=0`, exit 0.

## 4. Command that captures round 39 with a verifiable record

Do not run the first command until the wave directory is the set to preserve. Capture writes `census/round-39/waves/` and is an L1 landing step; this seat did not run it. After that receipt is committed, verify the committed tree (read-only):

```
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh \
  /home/vgpnk/Projects/shokunin/souji-shokunin 39
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh \
  /home/vgpnk/Projects/shokunin/souji-shokunin 39 --verify --rev <full-40-hex-of-the-commit-that-contains-census/round-39/waves>
```

A passing verify prints `verify-rev rev=<H> records=<n> failed=0 uncovered=0` and exits 0. The same verify against current HEAD, run this seat:

```
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh \
  /home/vgpnk/Projects/shokunin/souji-shokunin 39 \
  --verify --rev 2201778e7736af82e7d8a42dec2494f115bf3923
```

Observed: `error: manifest.sha256 missing at 2201778e7736af82e7d8a42dec2494f115bf3923:census/round-39/waves`, exit 4. `census/round-39/waves` is also absent on disk.

## 5. Files that must exist before capture

Tool precondition (`capture()`): `<lane>/.ufo/waves/round-<N>/` must be a real directory, not a symlink. An empty directory is accepted (fixture case 6, rc 0). A missing directory is exit 2 (observed for round 99). Spec, dispatch, results, and seat reports are not checked by the tool.

What both committed receipts actually contain, and what `summary.tsv` is built from:

| File | Role | Round 26 @ 765fe8b and @ HEAD | Round 29 @ de874ee | Round 39 live tree |
|---|---|---|---|---|
| `w1-spec.json` | wave spec (`reportDir` `.ufo/waves/round-39/w1`, wave `souji-r39-w1`) | present | present | present |
| `w1-dispatch.json` | rendered dispatch | present | present | present |
| `w1-results.json` | seat rows; the only input to `summary.tsv` | present | present | absent (no other `*-results.json`) |
| `w1/<Seat>.md` | seat reports | 492 md @ 765fe8b, 494 @ HEAD | 86 md | 30 of 71 spec names, 41 missing, 0 extra |
| `w1.ready` / `w1.ready.dispatched` | dispatch markers | both present | both present | `w1.ready` present; `w1.ready.dispatched` absent; `w1.ready.partial` present |

The 30-of-71 count is from `json.load` of `w1-spec.json` compared with `w1/*.md` during this run. An earlier `find` in the same run saw 25 markdown files, so the directory is still being written. `W1ScoutCapture.md` itself was in the missing set at the count. Capturing now would succeed (source directory exists) and would write a header-only `summary.tsv`, but it would not be a finished wave record: no results file, dispatch marker still partial, 41 seat reports not on disk yet.
