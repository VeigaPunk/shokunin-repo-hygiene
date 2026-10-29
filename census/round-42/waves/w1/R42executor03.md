# R42executor03 — C2 candidate: tools/souji-freeze-check.py (robustness angle)

Candidate: `.ufo/waves/round-42/w1/R42executor03/souji-freeze-check.py` — 32697 bytes,
sha256 `b15f0f69b55e233703f0263f1465175283fbae95e8dfe0bb61e61196cb36669c`.

## Evidence (commands actually run, scored in a scratch clone)
    bash census/round-42/score-candidate.sh c2 /fast/scratch/hyaku/souji-r42/R42executor03 tools/souji-freeze-check.py=<candidate>
    selftest ok rc=0 summary=(94, 94, 0)
    SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=b15f0f69b55e
    exit=0
Self-test directly: `python3 -B <candidate> --selftest` -> `SELFTEST cases=94 pass=94 fail=0` (exit 0), also under
`LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0` (non-ASCII fixtures use bytes paths) -> same line.
Candidate over committed lane bytes at afe17f4: r42 prereg `SUMMARY claims=3 findings=0` exit 0; r41 prereg the same.

## What changed vs r41
- KEY-DUPLICATE (one per duplicated key per claim; value of a duplicated key is not read by any other check),
  HEADING-MALFORMED (`line=<n>`, C0, closes the interrupted block), COUNTER-/POPULATION-SYMLINK (alone, no digest),
  widened DISPATCH-BEFORE-FREEZE (basename contains `-dispatch`/`.ready`, ends `-spec.json`/`-results.json`, any depth).
- `--selftest`: 94 hermetic cases over synthetic repos under $TMPDIR (every git call `-C`, identity via env, own HOME,
  toplevel asserted, rmtree in finally). Cases run the tool's own `digest` (against hard-coded SHA-256 constants),
  `freeze_rev` (`git log --diff-filter=A`) and `is_ancestor` (`git merge-base`) in-process via subprocess.run.
- Hardening beyond r41: ls-tree -z exact-name lookup (directory, submodule, glob, `./x`, NUL path read as missing;
  symlink detected by mode 120000; objects read by sha), `--literal-pathspecs`, `log -z` parsing (quotes, backslash,
  spaces, non-ASCII dispatch names), git failure in dispatch log / merge-base (rc>1) is COULD-NOT-EVALUATE not clean.
  No-regression claim: r41 plain-path behaviour unchanged; changed edge: `./`-prefixed path now reads missing.

## Edges covered by the self-test (all pass)
CRLF, BOM, BOM+CRLF, trailing space/tab on keys and headings, invalid UTF-8 bytes in prereg, `###`/`####`/prose `##` headings
clean, tab/colon/double-space/`C 2`/`C2x`/`c2`/`##C2` headings malformed (also CRLF, with keys following, only-bad -> +NO-CLAIMS),
multi-digit and trailing-space valid headings, duplicate keys (identical, differing, bad second, empty-then-value, two keys,
only in second claim), symlink counter/population (dangling, to dir, digest-of-link-text), counter becoming symlink or deleted
after freeze (FROZEN-EDITED), directory-valued counter, `./` counter, glob char (literal), NUL in path, spaces / non-ASCII /
quote+backslash paths, dispatch names (spaces, quotes, non-ASCII, nested depth, same commit as freeze, two files, other
round, `round-70` vs round-7, near-miss names), hostile GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE env, unresolved/short rev,
absent prereg, directory prereg, non-directory root.

## Limits / judgement calls
- Heading followed by a TAB (`## C2<TAB>x`) is HEADING-MALFORMED (spec: space or end of line only).
- `splitlines()` kept (r41 parity): U+2028/\x0b/\x0c inside a line split it.
- Free-standing --selftest cannot assert P1-P3 itself; it fails under them because its clean/dispatch/ancestry cases go red.
- Scratch dir /fast/scratch/hyaku/souji-r42/R42executor03 to be removed at yield.

Verdict: target SUMMARY met (exit 0). No tools installed.
