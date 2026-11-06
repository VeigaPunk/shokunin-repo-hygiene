# S71Scribe — r71 lesson draft + pointer check (partial; D3 milestone unbuilt)
Draft `.ufo/waves/round-71/w1/S71Scribe/draft.md`. Revs read: 52e8c3fa (after-arms), then tip 1c2239cd (16:57:11 -0300: sizechange probe re-run + r70 D2 erratum).
| routed item (round-70.md:78) | verdict | evidence at 52e8c3fa unless noted |
|---|---|---|
| (a) F1 filter driver hides a modified file | closed | a1db6c85 scrubs GIT_ATTR_SOURCE (`tools/souji-receipt-write.py:124`), refuses RECEIPT-FILTER-DRIVER-SET; `c1-after.txt` FC1/FC2/FC3 `base=accept → new=refuse`; `writer-selftest.txt:43` |
| (b) F2 `core.fileMode=false` hides a mode flip | closed | `-c core.fileMode=true` pin; FM1/FM2; `writer-selftest.txt:44` |
| (c) F3/F4/F5 member names, harness labels | closed | `c1-counter.py:1262-1287` MEMBER_RE; `c2-harness.py:108-126` LABEL_RE + "label escapes --work"; `c2-CF1` EXIT=2 |
| (d) X7/X8: rc binds no base counts; no ambient-scrub selftest | **partial** | X7/X8 `fate=killed` and `clean_env: ambient pathspec variables are scrubbed` present, but `claim_upheld` (`c1-counter.py:1164-1169`) binds only new_*/class/echo/regress — no `base_forgeries`/`base_honest` |
| (e) regenerate the battery for the 59-row matrix | **open** | no `*battery*` file under census/round-71/ (`ls records probes controls \| grep -i battery` → none) |
| (f) NOGLOB row or named limit | **open** | `c1-after.txt:121,123` NGA/NGD identical base→new; prereg "Named limits" names attr.tree, core.attributesFile, process driver, in-run creation — not NOGLOB |
| (g) writer case 38 enumerate vars independently of PATHSPEC_ENV | **open** | `tools/souji-receipt-write.py:1558` still `for var in PATHSPEC_ENV:`; candidate diff adds only git(), filter fns, cases 39-40 |
| (h) r69 D5 ambient tuple, D06 row, `verify` subcommand | **open** | writer diff has no tuple write, no `add_parser("verify")` |
| (i) cross-lane pathspec reads (kaidoku, kumitate) | open, documented, out of lane | no r71 commit touches a sibling repo |
Spot-check: **D1 open** — `SCORECARD.md:181` still "(5 missing, EXIT=1)" vs `git show 52e8c3fa:census/round-70/records/pointer-check-r69.txt` → `missing=8`, `EXIT=1`; no r71 commit touches SCORECARD. **D2 closed at 1c2239cd** (`grep -c 'R70-D2 erratum'` → 1; 0 at 52e8c3fa, the rev the C1/C2 receipts bind). **D3 open** (finding). **D4** → table. **D5** operator-owned; no lane file carries the toplevel guard (`git ls-files .ufo/prompts` → empty).
Pointer check (item 4), run from the lane:
`python3 -B tools/souji-pointer-check.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 52e8c3faf678b0f3d2f18cc6d41a365dc91123f7 census/round-71/preregistration.txt corpus/knowledge/filter-filemode-witness.md`
→ `SUMMARY files=2 checked=37 missing=0 skipped=1 dead_declared=0`, `EXIT=0`; same at 1c2239cd. No missing pointer; the skip is `census/round-71/controls/c1-*.txt` (holds `*`, checker docstring :11).
Re-derived: matrix 70 rows (19 accept / 51 refuse); `grep -c '^CASE '` → 70; 7 base forgeries are exactly AS1 AS2 FC1 FC2 FC3 FM1 FM2, each refused with its frozen class; `comm -23` r70→r71 case names empty (59 carried); receipts' shas match the tree (counter 7e5a694a, matrix e1a3c00b, harness 6c7bf41d, mutants 3e4945bf, candidate writer 56b6be03 = `git show a1db6c85:…|sha256sum`, base control 118597e0 = prereg:5); `git diff --stat aa91d1ca 52e8c3fa` → 10 files, no SCORECARD/LOG; `--name-status 52e8c3fa 1c2239cd` → probe file + round-70.md.
**Findings.**
- **HIGH** — declared milestone "D3 pointer-check selftest build" unbuilt: no r71 commit touches `tools/souji-pointer-check.py`; `grep -n 'pointer-check' SKILL.md` → 0 hits (r71 rows only :928 C1, :929 C2); `--selftest` → argparse usage error, rc=2.
- **MEDIUM** — `matrix=70` counts inert rows as coverage: NGA/NGD identical in both slots (`c1-after.txt:121,123`); r70's "NOGLOB row *or* named limit" met by neither; lesson should say `inert=2`.
- **MEDIUM** — rc still does not bind the base slot (`claim_upheld`): the X8 shape the r70 lesson named ("`base_forgeries` 4 → 0 with `EXIT=0`") reproduces; `grep -nE 'BASE_(FORG|HONEST)' c1-counter.py` → 0.
- **LOW** — `rev=` has three referents: candidate writer (`c1-after.txt:1`, a1db6c85), instrument (`counter-selftest.txt:3`, aa91d1ca), `--base-rev` (`c2-after.txt:1`, 8b9345b1) where `census/round-71/{c1-counter,c2-harness}.py` are both absent (`git cat-file -e` fails).
- **LOW** — committed `attr-filemode-probe-sizechange.txt` is a `sed` re-run, not the overwritten original; prereg's "overwritten" holds, evidence now durable.
Draft Mistakes rows: M-a (receipt `rev=` three referents), M-b (routed-list amnesia: freeze carries 3 of 9, and the dropped ones are invisible to the round's own SUMMARY). Files written: `.ufo/waves/round-71/w1/S71Scribe/draft.md` and this file. No scratch dir, no installs, no lane edits.
