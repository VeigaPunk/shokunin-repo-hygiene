# R42executor04 — C2 candidate (tools/souji-freeze-check.py)

Verdict: PASS (seat score, advice only). Counter reached the target on the first scored run.

Candidate: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42executor04/souji-freeze-check.py
sha256 ed35b51f48dd99ffab1f5332b6d2cda5753355bd493e5b650048e1bc1c23e9a1, 32767 bytes.

## Commands and output
1. `TMPDIR=<scratch>/tmp python3 -B souji-freeze-check.py --selftest` -> `SELFTEST cases=61 pass=61 fail=0`, exit 0 (1.9 s).
2. `bash census/round-42/score-candidate.sh c2 /fast/scratch/hyaku/souji-r42/R42executor04 tools/souji-freeze-check.py=<candidate>` -> exit 0. 37 case-* lines all PASS, then:
   `real ok rc=0 findings=0 summary=(3, 0)`
   `retro red rc=1 findings=19 summary=(3, 19)`
   `retro_clean ok rc=0 findings=0 summary=(3, 0)`
   `selftest ok rc=0 summary=(61, 61, 0)`
   `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=ed35b51f48dd`
   Final SUMMARY exit code: 0.

## Design
- r41 behaviour kept: whitelisted git env, no GIT_DIR, `core.quotePath=false`, `log.mailmap=false`, CRLF/BOM, spaces in paths, `FIELD-MISSING C0 Round`.
- KEY-DUPLICATE: one finding per duplicated key; no value of a duplicated key is read (no first-wins), so the dependent checks for that key are skipped.
- HEADING-MALFORMED: `^##(?!#) *[Cc] *[0-9]` that is not `^## C[0-9]+( |$)`; detail `line=<n>`; it closes the claim before it and opens none.
- COUNTER-SYMLINK / POPULATION-SYMLINK: `git ls-tree -z --full-tree` mode 120000 at the freeze commit; that finding alone, no digest, FROZEN-EDITED or EMPTY check.
- DISPATCH-BEFORE-FREEZE: basename contains `-dispatch` or `.ready`, or ends `-spec.json` or `-results.json`, at any depth under `.ufo/waves/round-N/`. It reads `git log -z --name-only` so tab or newline names are exact. It flags a path if ANY adding commit is the freeze commit or an ancestor, which is stricter than r41's single-oldest.
- `--selftest`: runs `run_check`, `freeze_rev`, `Repo.is_ancestor`, `Repo.mode` and `sha256_hex` in-process over fresh repos under `$TMPDIR`.
  - Directory, commit-message, file-name and salt values are random per run (`secrets`). Every git call names `-C`, identity is passed through env, and the toplevel is asserted before the first commit.
  - Expected digests come from an independent pure-Python SHA-256 (`ref_sha256`, constants derived from primes, no hashlib). The tool's own digest therefore cannot grade itself, and a reversed `sha256` fails the clean cases and the known-answer cases.
  - 61 cases: known-answer digests, 51 grammar and git cases, ambient GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE ignored, 4 refusals (exit 2), direct freeze-rev/ancestry/mode checks, 2 CLI child runs. Scratch is removed in `finally`.
- I did not read the counter's CASES, SITECUSTOMIZE or env var names, and nothing special-cases fixture names.
- The `patches=3/3` leg passed in the scored run. I did not run the patches by hand, since that needs the sitecustomize text.

## Risks
- Case 61 count rests on the tool's own cases; a hidden counter case with an unusual duplicate shape, for example one where a duplicated key is also empty, could differ. The scored 37/37 shows none of the 37 do.
- Needs `os.symlink` (Linux); on a platform without symlink support the two symlink cases would fail loudly, not silently.
- Scratch dir deleted; no tools installed.
