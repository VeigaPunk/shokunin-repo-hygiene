# R42executor05 — C2 candidate (souji-freeze-check.py), regression-safety angle

Candidate: `.ufo/waves/round-42/w1/R42executor05/souji-freeze-check.py`
sha256 `d97ab2e252dbef43f35061ce0fe5d2b426f1d6b567d73d24438b86efd563a61c`, 21509 bytes.
Receipts in the same directory: `hidden-audit-new.txt` (candidate), `hidden-audit-r41-tool.txt` (r41 tool at base).

## Design
- r41 code kept (whitelisted git env, core.quotePath/mailmap off, CRLF/BOM, spaces in paths, first-wins key read).
- KEY-DUPLICATE: `parse_claims` records each key seen twice (one finding per key, detail = key).
- HEADING-MALFORMED: any column-0 `##` (not `###`) line that is not `## C<digits>( |$)` but matches `##(?!#) *[Cc] *[0-9]` is reported (C0, `line=<n>`); it opens no claim and closes the open one.
- COUNTER-/POPULATION-SYMLINK: `Repo.mode()` = `git ls-tree -z --full-tree FREEZE -- path` (checked from a subdirectory root: root-relative path works); mode 120000 gives that finding only (no digest/FROZEN-EDITED/EMPTY check).
- DISPATCH-BEFORE-FREEZE basename test: contains `-dispatch` or `.ready`, or ends `-spec.json` / `-results.json`.
- `--selftest`: builds 18 synthetic repos under `$TMPDIR` (`mkdtemp`, removed in `finally`; every git call `-C`, identity via env, no `git config`), runs the tool's own `main()` in-process (real `digest`, `git log --diff-filter=A`, `git merge-base --is-ancestor` through `subprocess.run`). Expected digests are literals, plus a known-answer check sha256(b"abc"), so a reversed-digest patch cannot cancel out between fixture and tool. No counter text read; no case names special-cased.

## Commands and output
```
TMPDIR=/fast/scratch/hyaku/souji-r42/R42executor05 python3 -B souji-freeze-check.py --selftest
SELFTEST cases=18 pass=18 fail=0        (exit 0)

bash census/round-42/score-candidate.sh c2 /fast/scratch/hyaku/souji-r42/R42executor05 tools/souji-freeze-check.py=<candidate>
case-* x37 = PASS
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=19 summary=(3, 19)
retro_clean ok rc=0 findings=0 summary=(3, 0)
selftest ok rc=0 summary=(18, 18, 0)
SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=d97ab2e252db
exit code 0
```
(Note: score-candidate.sh needs the scratch root to already exist; first try with a not-yet-created subdir gave exit 2 "not a directory", rerun with the existing seat dir.)

r41 hidden-case audit (`python3 -B .../R41w2executor01/hidden-audit.py --tool <file> --scratch .../audit`):
- r41 tool at base: `SUMMARY scenarios=92 strict=80/83 literal=0/4 ambig=4/5 seed=603641295` (strict fails: round-absent-early-dispatch-silent, no-claims-empty-file, no-claims-header-variants).
- candidate: `SUMMARY scenarios=92 strict=79/83 literal=0/4 ambig=4/5 seed=2053006971` exit 1 (the audit's fuzz seed differs per run; fuzz scenarios all PASS in both).
- Strict diff = the same 3 r41 fails plus ONE new, a legitimate r42 change:
  - `dispatch-lookalike-names-silent` (r41 expected clean for `x-dispatch.json.bak`, `x.readyy`, `a-dispatch.jsonl`, `...-dispatch.JSON`; also `dispatch.json`, `ready` which stay clean). The r42 spec says basename *contains* `-dispatch` / `.ready`, so 4 of those now read DISPATCH-BEFORE-FREEZE by design.
  - `no-claims-header-variants` was already a r41 fail (extra FIELD-MISSING Round); it now additionally carries 2 HEADING-MALFORMED (`##C1`, `## c2`) by design — still a fail by the r41 oracle, expected change.
- Ambiguous/literal rows unchanged except none; `ambig-sha256-uppercase-hex` and `literal-control-blank` fail as at r41.

## Limits
- First-wins value reading retained for duplicated keys (only KEY-DUPLICATE added); the counter case set passed with it.
- A tab-separated heading (`##\tC1`) is not flagged (spec says "spaces").
- Per-line `splitlines()` semantics inherited from r41.

## Verdict
Target met by this seat's score run (37/37, patches=3/3, selftest ok). Regression: 79/83 strict vs r41's 80/83, the single delta being the intended widening of DISPATCH names.
