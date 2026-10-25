# W2Scope — round-24 scope-bound attack

## Status
STATUS: PARTIAL — the 44 landed paths in a65fac9..ca7fc1c are all lane-internal, with no operator-sweep content, no real credential, no `/tmp` scratch, and no new `__pycache__`. That part survives. One trust-boundary attack lands on a tool the round modified: `souji-receipt-run.py run --out` overwrites fleet and shokuknow paths that HARD BOUND forbids (F1, reproduced in /var/tmp).

## Evidence
All commands are read-only against the lane. Range end ca7fc1cb6dd1333096c6f3bdbad304686691d126; `master` is now c3ca7ad8f8722d5e92ba350e49b4ebb96e8bface (wave-1 reports), which was also scanned.

| check | command (abridged) | result |
|---|---|---|
| paths changed | `git -C $L diff --name-status a65fac9 ca7fc1c` | 44 paths, 7372+/4−. 40 are `A`; 4 are `M` (`corpus/README.md`, `corpus/SOURCES.md`, `corpus/knowledge/git-repo-structure-readonly.md`, `tools/souji-receipt-run.py`). Prefixes: `.ufo/waves/round-24/` (13), `census/round-24/` (21), `corpus/` (4), `tests/fixtures/r24-*` (3), `tools/` (3). |
| extra commit | `git diff --name-status ca7fc1c master` | 46 `A` paths, all `.ufo/waves/round-24/w1/*` |
| symlink/submodule | `git diff --raw … \| awk '$2=="120000"\|\|$2=="160000"'` | none; new modes are only 100644 and 100755 |
| operator-sweep paths | `git diff --name-only a65fac9 master \| grep operator-sweep` | rc=1 (none) |
| operator-sweep content | `git grep -nE 'operator-sweep-[0-9]+/[^ ]+' master` (round-24 hits) | only the directory name and the sparse pattern `!/census/operator-sweep-*`. No file under it is named or quoted in round-24 bytes. |
| credential grep (mandated) | `git show ca7fc1c:$f \| grep -nE 'sk-\|ghp_\|BEGIN .*PRIVATE\|password='` over every A/M file | 4 hits, all non-secret (F3) |
| wider credential grep | added lines vs `AKIA…`, `xox[bp]-`, `gh[pousr]_…`, `glpat-`, `token=`, `secret=`, `api_key`, `Authorization:`, `BEGIN … KEY` | 0 hits |
| `/tmp` use | added lines matching `/tmp` but not `/var/tmp`, a65fac9..master | 6 hits: the runner's OUT-UNDER-TMP refusal (`tools/souji-receipt-run.py:169-170`), its docstrings, and one LOG quote. No scratch path. |
| tempfile dir | `mkdtemp\|mkstemp\|TemporaryDirectory\|NamedTemporaryFile\|gettempdir` without `dir=` in range `.py` files | none. Fixtures: `r24-size-census.py:28,86`, `r24-coverage-agreement.py:50,337`, `r24-receipt-verify.py:45,107` all use `dir='/var/tmp'`. The runner uses `SCRATCH_ROOT="/var/tmp"` (`:62,188`). |
| `__pycache__` | `git ls-tree -r --name-only {a65fac9,ca7fc1c,master} \| grep __pycache__` | only `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`, present at base and added in e879ba0 (round 10) (F4) |
| committed record paths | `grep -oE '(/var)?/tmp…\|/home/vgpnk/…'` over `census/round-24/records/*` and `size-census-lane.txt` | only `/var/tmp/souji-receipt-*`, `/var/tmp/souji-r13-repo-structure.*`, and the lane root/`.git`. No path outside the lane. |
| lane measurement | `git show master:census/round-24/size-census-lane.txt` | `census.common_dir=/home/vgpnk/Projects/shokunin/souji-shokunin/.git`; the counts line `garbage=0 size_garbage=0 unreachable=1093 alternates=0` describes the lane only |
| F1 reproduction | scratch at `/var/tmp/souji-r24-W2Scope/` (removed; `ls` shows it is gone) | see Attack log |

## Findings
1. **F1 — MEDIUM. `run --out` guard does not enforce HARD BOUND.** Location: `tools/souji-receipt-run.py:165-180` at ca7fc1c.
   - **Mechanism:** after `realpath`, `run` refuses only:
     - `/tmp`;
     - paths inside `--root`;
     - the substrings `/.ufo/state/`, `/.tower/`, `/.scratch/`, `/MANIFEST.json`;
     - `/[A-Za-z0-9_-]+-shokunin/`.
     It then writes with `open(out, "w")` (`:248-250`), which truncates the target.
   - **Exploit:** a seat or the L1 passes `--out /home/vgpnk/Projects/shokunin/.ufo/watchdog.log` or `--out /home/vgpnk/Projects/shokuknow/<f>`. Paths under `/home/vgpnk/Projects/shokunin/scripts/` or `templates/` work the same way. HARD BOUND names every one of these as untouchable.
   - **Evidence:** reproduced on a mirrored tree (Attack log).
   - **Provenance:** the guard predates the round (these lines are not in the r24 hunks). The round modified this file and left the gap open.
   - **Smallest remediation:** replace the deny-list with an allow-list. Require `out` to be under `/var/tmp/` (or one configured receipt root) and refuse everything else. Add a fixture case per forbidden root.
2. **F2 — INFO. A disclosed fleet-root read is now in the lane history.** Location: `.ufo/waves/round-24/w1/ReviewQualityBar.md:21` (c3ca7ad, after the named range).
   - The seat quotes itself: "I ran `rg -n 'SOURCES-CONTRACT-v1' -l . ../` from the lane root". That search spanned `.scratch/`, `.ufo/state/` and `census/operator-sweep-20261019/`.
   - The seat says it printed 5 paths. The two I could check, `census/round-12/postreview.md` and `census/round-12/sources-census.sh`, are lane-tracked (`git ls-tree` lines 1772 and 1776). No forbidden content is in committed bytes.
   - This was a read, not a write, and it is disclosed. The bytes are clean, but the seat broke the read rule.
3. **F3 — LOW. The credential grep hits are false positives, and one exposes redaction over-match.**
   - `tools/souji-receipt-run.py:80-82` contains the redaction regexes themselves.
   - `corpus/SOURCES.md:185` matches `sk-` inside `--disk-usage`.
   - The same unanchored `sk-[A-Za-z0-9_.-]+` (`:81`) would rewrite any `cmd=` argv containing `--disk-usage`, `task-…` or `desk-…`. The round's TOOL-PATH-REDACTED refusal (`:180-181`) covers only the `--tool` path, not other argv elements. This was already raised in w1 `CritC3Value.md:25,46`.
   - No real credential appears in round-24 bytes.
4. **F4 — LOW, inherited. A `.pyc` is still tracked.** Location: `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`.
   - It was tracked at base, so the round did not add it.
   - The worktree blob hash `eab045d2…` equals the tracked blob.
   - The worktree mtime 1792911174.122327577 equals the index-recorded mtime. [INFERENCE] git or jj checkout rewrote it today, not Python bytecode generation.
   - No new `__pycache__` or `.pyc` exists in the range, the worktree or the ignored set.
   - Remediation is out of round scope: untrack it in a hygiene round and add `__pycache__/` to `.gitignore`.
5. **F5 — INFO. Uncommitted worktree state is outside the range.** ` M .ufo/waves/round-24/make-spec.py`, ` M corpus/QUALITY.md`, and `?? .ufo/waves/round-24/w2*` are uncommitted. `make-spec.py` writes only `os.path.join(dirname(__file__), f"{which}-spec.json")` (line 461 at ca7fc1c), inside the lane. I did not judge them further.

## Attack log
- **A1 — LANDED (F1).** Scratch `/var/tmp/souji-r24-W2Scope/`:
  - Setup: a one-commit repo on `master` with `t.py` printing `cases=1 pass=1`, and the runner taken from `git show ca7fc1c:tools/souji-receipt-run.py`.
  - Command: `python3 -B runner.py run --root $S/repo --rev $R --tool t.py --out $S/<o> -- python3 t.py`.

  | `<o>` | result |
  |---|---|
  | `fleet/.ufo/watchdog.log` | rc=0; file now starts `receipt=v1` (pre-seeded `ORIGINAL` truncated) |
  | `fleet/scripts/r.tsv` | rc=0, written |
  | `shokuknow/r.tsv` | rc=0, written |
  | `fleet/.ufo/state/r.tsv` | rc=2 `OUT-PROTECTED` |
  | `fleet/MANIFEST.json` | rc=2 `OUT-PROTECTED` |

  The guard matches path substrings, so the scratch prefix behaves the same as `/home/vgpnk/Projects/shokunin`.
- **A2 — survives.** Writes outside the lane by the new tools and fixtures. Every write site in `tools/souji-size-census.py`, `tools/souji-coverage-agreement.py`, the three `tests/fixtures/r24-*.py` files and `census/round-24/controls/stub-size-census.py` goes to stdout/stderr or under a `/var/tmp` mkdtemp. The size-census tool has no file writes at all; its sites are lines 123, 220, 223 and 225.
- **A3 — survives.** `/tmp` bypass of OUT-UNDER-TMP: `out = os.path.realpath(args.out)` (`:168`) runs before the prefix test, so relative paths, `..` and symlinks into `/tmp` all resolve first. I did not test a bind mount.
- **A4 — survives.** operator-sweep leakage: the round-24 runner checks out the clone sparsely with `!/census/operator-sweep-*` (`:200-208`), and no round-24 file names a file under that directory.

Tooling: no installs or updates.
