# R40w2mutationtester05 — C3 fixture mutation coverage

**Verdict: FALSIFIED (coverage).** The landed r40 fixture leaves two plausible defect mutants alive: removing the duplicate REPO-name rejection and ignoring the TOTAL prunable sum. It does kill strict rejection of an identical second TOTAL and an ignored `--skip-unrecorded` guard. A `surrogateescape` mutant crashes the fixture driver itself; that is inconclusive as a detector result, not a kill. No installed tools.

## Frozen target and attack points

Frozen claims: `census/round-40/preregistration.txt:10-11`; landed instrument commit `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Attack target is only the committed r40 fixture (`tests/fixtures/r40-drift-record-branches.py`) against the committed detector `tools/souji-worktree-drift.py`; no lane files were changed besides this report.

Fixture scenarios: `tests/fixtures/r40-drift-record-branches.py:99-120` tests `--skip-unrecorded`, identical/conflicting TOTAL rows, totals repo count mismatch, and invalid UTF-8 in a repo name/comment. Tool behavior sites: `tools/souji-worktree-drift.py:157-160` duplicate-name guard; `:162-165` TOTAL assignment; `:169-178` TOTAL sums; `:370-371` skip guard; `:147` UTF-8 decoding.

## Reproduction commands and actual output

All fixtures were run from isolated scratch `/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester05`, with `TMPDIR` explicitly set there. Sources were extracted from the landed commit with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show <rev>:<path>`. Common invocation (each mutant was run against both fixture versions):

```sh
python3 -B "$S/fixture.py" --tool "$S/$mutant.py" --work "$S"
python3 -B "$S/base.py" --tool "$S/$mutant.py" --work "$S"
```

Pristine r40 output:
```
case-good=PASS
case-total-duplicate-identical=PASS
case-total-conflicting-second=PASS
case-total-repos-disagrees=PASS
case-skip-unrecorded-suppresses=PASS
case-unrecorded-without-flag=PASS
case-invalid-utf8-in-repo-name=PASS
case-invalid-utf8-in-comment=PASS
SUMMARY cases=8 pass=8 fail=0
```
Exit status 0.

Mutants were single edits in the scratch copy of the detector: `strict_duplicate` rejects a second TOTAL instead of overwriting it; `skip_flag_ignored` replaces `if not args.skip_unrecorded:` with `if True:`; `surrogateescape` changes the decoder error handler; `duplicate_repo_check_removed` removes lines 158-159; `ignore_total_prunable` disables the condition at line 174.

### strict_duplicate
r40:
```
case-good=PASS
case-total-duplicate-identical=FAIL rc=2 want=0 missing=['SUMMARY', 'record_repos=2'] out='REFUSAL RECORD-MALFORMED: duplicate TOTAL '
case-total-conflicting-second=PASS
case-total-repos-disagrees=PASS
case-skip-unrecorded-suppresses=PASS
case-unrecorded-without-flag=PASS
case-invalid-utf8-in-repo-name=PASS
case-invalid-utf8-in-comment=PASS
SUMMARY cases=8 pass=7 fail=1
```
rc=1. r39 base: `case-good=PASS`, `case-trailing-space=PASS`, `case-total-before-rows=PASS`, `case-crlf=PASS`, `case-outside-root=PASS`, `case-indented-comment=PASS`, `case-comments-total-only=PASS`, `SUMMARY cases=7 pass=7 fail=0`; rc=0. **KILLED by r40; survives r39.**

### skip_flag_ignored
r40:
```
case-good=FAIL rc=1 want=0 missing=[] out='DRIFT\tUNRECORDED\tgamma\tlive regs=1 prunable=0 SUMMARY record=/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester05/souji-r40-branches.xkbhxwk9/fleet-root/record-zdpzr_6j.tsv record_repos=2 record_reg'
case-total-duplicate-identical=FAIL rc=1 want=0 missing=[] out='DRIFT\tUNRECORDED\tgamma\tlive regs=1 prunable=0 SUMMARY record=/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester05/souji-r40-branches.xkbhxwk9/fleet-root/record-we7w2q4_.tsv record_repos=2 record_reg'
case-total-conflicting-second=PASS
case-total-repos-disagrees=PASS
case-skip-unrecorded-suppresses=FAIL rc=1 want=0 missing=[] out='DRIFT\tUNRECORDED\tgamma\tlive regs=1 prunable=0 SUMMARY record=/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester05/souji-r40-branches.xkbhxwk9/fleet-root/record-p837eq2s.tsv record_repos=2 record_reg'
case-unrecorded-without-flag=PASS
case-invalid-utf8-in-repo-name=PASS
case-invalid-utf8-in-comment=FAIL rc=1 want=0 missing=[] out='DRIFT\tUNRECORDED\tgamma\tlive regs=1 prunable=0 SUMMARY record=/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester05/souji-r40-branches.xkbhxwk9/fleet-root/record-_3j0ijb4.tsv record_repos=2 record_reg'
SUMMARY cases=8 pass=4 fail=4
```
rc=1. r39 base: seven PASS cases, `SUMMARY cases=7 pass=7 fail=0`; rc=0. **KILLED by r40; survives r39.**

### surrogateescape
r40 output:
```
Traceback (most recent call last):
  File "/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester05/fixture.py", line 150, in <module>
    sys.exit(main(sys.argv[1:]))
  File "/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester05/fixture.py", line 140, in main
    results = run_cases(tool, work)
  File "/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester05/fixture.py", line 114, in run_cases
    run_record(tool, root, path,
  File "/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester05/fixture.py", line 82, in run_record
    proc = subprocess.run(
  File "/usr/lib/python3.14/subprocess.py", line 557, in run
    stdout, stderr = process.communicate(input, timeout=timeout)
  File "/usr/lib/python3.14/subprocess.py", line 1221, in communicate
    stdout, stderr = self._communicate(input, endtime, timeout)
  File "/usr/lib/python3.14/subprocess.py", line 2194, in _communicate
    self.stdout.encoding,
    self.stdout.errors)
  File "/usr/lib/python3.14/subprocess.py", line 1099, in _translate_newlines
    data = data.decode(encoding, errors)
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 15: invalid start byte
```
rc=1. r39 base: seven PASS cases, `SUMMARY cases=7 pass=7 fail=0`; rc=0. **INCONCLUSIVE**: fixture process fails while decoding child output before it emits its own `SUMMARY`, so the detector does not report a fixture-level kill.

### duplicate_repo_check_removed
r40: all eight cases PASS; `SUMMARY cases=8 pass=8 fail=0`; rc=0. r39 base: all seven PASS; `SUMMARY cases=7 pass=7 fail=0`; rc=0. **SURVIVED by r40 and r39.**

### ignore_total_prunable
r40: all eight cases PASS; `SUMMARY cases=8 pass=8 fail=0`; rc=0. r39 base: all seven PASS; `SUMMARY cases=7 pass=7 fail=0`; rc=0. **SURVIVED by r40 and r39.**

The fixture has no duplicate REPO-name record and no mismatched TOTAL prunable sum case, explaining the two uncovered behaviors. The identical duplicate TOTAL case does constrain a different contract (accepting identical duplicate totals), but does not test the prunable aggregate.

Scratch cleanup: removed via `trap 'rm -rf -- "$S"' EXIT`; no scratch artifacts retained. No pacman/tool installs performed.
