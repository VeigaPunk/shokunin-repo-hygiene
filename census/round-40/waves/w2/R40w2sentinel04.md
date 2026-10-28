# R40w2sentinel04 — fixture filesystem safety

## Verdict: SAFE (for the exercised fixture run)

**Attack surface:** `tests/fixtures/r40-drift-record-branches.py`, specifically `make_repo` (lines 53–59), `fleet` (62–69), `run_record` (72–91), `run_cases` (94–123), and `main` (126–147). The fixture's temporary repositories and record files are created beneath the `--work` directory; `run_cases` removes its temporary tree in `finally`.

Frozen claim context: `census/round-40/preregistration.txt`, lines 10–12, states the C3 behavior under test. Landed commit: `128e412b0ced3c243dc27c3dd3332054a611bc2e`; fixture blob at that revision: `2ed78104eac7417d0b2f0c8024ad03ad56491db6`.

### Exact commands and output

Command 1:
```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat 128e412b0ced3c243dc27c3dd3332054a611bc2e
```
Output (relevant fixture entry):
```text
 tests/fixtures/r40-drift-record-branches.py        |  150 ++
```

Command 2 (set `TMPDIR` explicitly and use the same in-scratch `--work`):
```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel04; mkdir -p "$S" && export TMPDIR="$S" && python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r40-drift-record-branches.py --work "$S"; rc=$?; printf 'fixture_exit=%s\\n' "$rc"; printf 'work_contents_after='; find "$S" -mindepth 1 -maxdepth 3 -printf '%y %p\\n' | sort; exit 0
```
Output:
```text
case-good=PASS
case-total-duplicate-identical=PASS
case-total-conflicting-second=PASS
case-total-repos-disagrees=PASS
case-skip-unrecorded-suppresses=PASS
case-unrecorded-without-flag=PASS
case-invalid-utf8-in-repo-name=PASS
case-invalid-utf8-in-comment=PASS
SUMMARY cases=8 pass=8 fail=0
fixture_exit=0
work_contents_after=
```

Command 3 (post-run external-path check and revision-bound source identification):
```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel04; printf 'scratch=%s\\n' "$S"; printf 'work_after='; find "$S" -mindepth 1 -maxdepth 4 -printf '%y %p\\n' | sort; printf 'outside_tmp_candidates='; find /var/tmp -maxdepth 1 -name 'souji-r40-branches.*' -printf '%p\\n' 2>/dev/null | sort; printf 'fixture_source_revision='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 128e412b0ced3c243dc27c3dd3332054a611bc2e:tests/fixtures/r40-drift-record-branches.py
```
Output:
```text
scratch=/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel04
work_after=outside_tmp_candidates=fixture_source_revision=2ed78104eac7417d0b2f0c8024ad03ad56491db6
```

### Findings

- Created paths observed: none remaining. During execution, by code path (lines 62–69, 74–75, 94–98), paths are under the supplied work directory: `souji-r40-branches.<random>/fleet-root/fleet/{alpha,beta,gamma}` (three Git repos) and `souji-r40-branches.<random>/fleet-root/record-<random>.tsv` (one per case). The post-run work tree was empty.
- Outside `--work`: no paths observed from the run; the fixture's `mkdtemp` and `mkstemp` both receive explicit directory arguments (`run_cases` line 95; `run_record` line 74). The post-run check found no matching `souji-r40-branches.*` under `/var/tmp`.
- Symlink traversal: no symlink creation or following mechanism is present in the inspected fixture logic; it constructs fresh random descendants under `work` and uses ordinary `os.makedirs`/file creation. This is a code-path review, not a hostile prepopulated-work-dir symlink test.
- FIFO/blocking: no FIFO creation or FIFO read is present. The fixture creates regular record files and Git working trees, then executes the named tool synchronously with captured stdout/stderr and `--timeout 30` (lines 82–86). No FIFO was left behind; the work directory was empty after run.

**Conclusion:** No concrete filesystem-safety falsifier found for the specified run. The scratch directory `/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel04` was removed before report completion; its work contents were empty after fixture execution and the directory itself was then cleaned up. No tools were installed or updated.