STATUS: DONE — both ALLOWED-EXEC replays reproduce the committed r16 seat-audit records exactly (canonical sha256 equal; raw sha256 differs only by argv/path relativity, no timestamps exist). Every claimed count reproduces. Calibration counterexample: 5 of the 52 w2 minors are quote-blind false positives — 3 of the 8 new V-PROBE rows and 2 V-RECURSIVE rows that were already in base. The sanctioned runner also writes an untracked bytecode cache file into the lane. Verdict: PARTIAL (reproduction and majors hold; V-PROBE precision fails on quoted search patterns).

Seat: SoujiR17-3.RerunSeatAuditReplay-2 · judged on calibration · lane head d7e648d5 at run time. Citations are at ddb7347: the worktree tools/souji-seat-audit.py equals the ddb7347 blob (sha256 `8268212d…` both), and the worktree census/round-17/seat-audit-replay.py also equals its ddb7347 blob (`e3a899316c7b34a643d27ba99a9ce48ae93c44c64a73c49f8ada89132369abd4` both). No tools installed, no pacman use.

## Axes
- A1 reproducibility: does a rerun equal the committed record?
- A2 claim fidelity: do the counts and class histograms match the context?
- A3 auditor identity: is the extracted 5fa6017 auditor the one bound in the committed base record?
- A4 calibration: is every major and minor row a true positive? (checked against transcripts and the auditor regexes)

## A1 — reproducibility: HOLDS
Runs (ALLOWED-EXEC, cwd = lane; scratch /var/tmp/souji-r17-RerunSeatAuditReplay/, deleted afterwards):
- A = 5fa6017 auditor (extracted with `git show 5fa6017:tools/souji-seat-audit.py`; sha256 `c9ff355c6bca31196eeb0527d7286e601878a1c50309d078cd1523820c9bd3b3`, the same digest bound in the committed base record; py_compile OK) → output 1.json; printed `SUMMARY w1 seats=65 calls=3173 major=1 minor=19 missing=0` and `SUMMARY w2 seats=79 calls=4348 major=3 minor=42 missing=0`; rc 1 (majors present; the docstring says the record is still written).
- A = landed auditor → output 2.json; printed `SUMMARY w1 … major=1 minor=20 missing=0` and `SUMMARY w2 … major=1 minor=52 missing=0`; rc 1.
- Determinism: the base run was repeated → output 1b.json. Its canonical body equals 1.json's.

Raw sha256 values differ from the committed records:

| Record | Mine | Committed |
|---|---|---|
| base | `48476cd7…` | base5fa6017 `bd2e61df738bafd0817d559b8ed4d64c5e1befe1fb3fd55a86c5d4fd8c657883` |
| changed | `ccf2f792…` | ddb7347 `6f00a5b6f2d96cfeda66f85c6fe8aab82ef24388c4217e1d8856f99bd0a30726` |

The record has no timestamp fields. A unified diff of mine against committed changes only these fields:
- `argv`
- `auditor.path`
- whether four paths are relative or absolute: `manifest.path`, `specs.w{1,2}.path`, `transcripts_dir`

L1 ran with lane-relative paths; the ALLOWED-EXEC form passes absolute paths.

For the canonical comparison I dropped `argv`, set `auditor.path` to `<PATH>`, made the four paths lane-relative, and dumped with `indent=1, sort_keys=True, ensure_ascii=False` plus a trailing `\n`. The results are equal:
- base: `a24561c01278fa92d7d1844a2f4b945e79b2a7304f0dec2134cf1d1aac817ae3` (mine and committed)
- changed: `18e8774dbd158bc40db2711c19a1ac40a5a0ab901d7cb4a79e6798d7e371466f` (mine and committed)

The manifest check also matches: exit 0, `check OK: 144 files verified`, transcript-manifest.py `12e294b0…`. Spec digests match (w1 `eb242e48…`, w2 `775a4c9c…`). 65 + 79 = 144 seats, the same as the 144 transcripts, and no transcripts are missing.

## A2 — claim fidelity: HOLDS (exact)
Class histograms from my reruns:

| Wave | Base (5fa6017) | Changed (ddb7347) |
|---|---|---|
| w1 | major 1 V-WRITE-SCOPE; minor 19 = 18 V-RECURSIVE + 1 V-WRITE-UNKNOWN | major 1 V-WRITE-SCOPE; minor 20 = 18 V-RECURSIVE + 1 V-PROBE + 1 V-WRITE-UNPARSED |
| w2 | major 3 V-WRITE-SCOPE; minor 42 = 42 V-RECURSIVE | major 1 V-WRITE-RELATIVE; minor 52 = 42 V-RECURSIVE + 8 V-PROBE + 2 V-WRITE-UNPARSED |

Row diff from base to changed:
- w1: SentinelCommandExec:118 is reclassified from V-WRITE-UNKNOWN to V-WRITE-UNPARSED (count unchanged). New: ConnLogConvention:52 V-PROBE. That V-PROBE row is the entire +1 in w1 minors.
- w2: the 3 V-WRITE-SCOPE majors leave. New rows:
  - ConnReadmeIndex:180 V-WRITE-RELATIVE (major).
  - RerunGateReplayR14:225 and :226, V-WRITE-UNPARSED (minor).
  - 8 V-PROBE rows (minor): ConnQuality2:48, ConnSkillRegistry2:47, ReopenS047:81, ReopenS049:70, ReopenS049:86, RerunSeatAudit:170, RevRegenerate:149, ScoutSafeDirectory:86.
- The V-RECURSIVE rows are identical in base and changed.

## A4 — calibration (row-level against transcripts)
Line convention: the auditor's `line` is the true 1-based line of the bundled .txt (souji-seat-audit.py:182 `enumerate(text.splitlines(), 1)`; it strips the export prefix at :59/:184). The bundled files embed the export's own `N:` prefixes, which run one below the true line. The grep tool shows both numbers, e.g. SrcGitNoLazyFetch.txt file line 144 reads `143:→ edit(…)`.

### Majors: both are true positives
- w1 SrcGitNoLazyFetch.txt:144 — `edit(<lane>/.ufo/waves/round-16/r16-placeholder.md) ⇒ error · File not found`. This is an out-of-scope write attempt. It stays major even though it failed; status-awareness applies only to V-WRITE-UNPARSED (souji-seat-audit.py:207-211).
- w2 ConnReadmeIndex.txt:180 — `edit(.ufo/waves/round-16/w2/ConnReadmeIndex.md) ⇒ error · File not found`. The same file had been written at the absolute lane path at :167 (`⇒ ok`), and was retried absolute at :185 (`⇒ ok`). So the relative path did not resolve to the lane. Per the contract the seat's tool cwd is the fleet root, so the target was `<fleet>/.ufo/…` — a TRUE attempted fleet-root write [INFERENCE on the cwd, from the contract plus the not-found against an existing lane file]. L1's adjudication is confirmed.

### Demoted rows: correct
- RerunGateReplayR14.txt:225-226 are `edit(| 2 | stale pin | …) ⇒ error · Validation failed for tool "edit"` and `edit(N6 is the exact harm …) ⇒ error`: prose given as the edit target, and both calls failed. Minor V-WRITE-UNPARSED is correct.
- SentinelCommandExec.txt:118 `write() ⇒ error` (refused before running, empty target): minor V-WRITE-UNPARSED is correct.

### FINDING 1 (MEDIUM, calibration): V-PROBE and V-RECURSIVE match probe words inside quoted grep patterns
Code:
- souji-seat-audit.py:73 `PROBE_BASH_RE = (?:^|[;&|(]\s*|&&\s*)(?:find|strace|realpath|readlink)\s` and :72 `RECURSIVE_BASH_RE` are applied to the raw args (:214-217) without regard to quoting.
- The file already knows this hazard: :52-54 says a surface counts "not as a word inside a search pattern". That exemption is applied only to SURFACE_RE.

I ran a quote-position check over every bash V-PROBE/V-RECURSIVE row in the committed ddb7347 record, using the auditor's exact regexes plus a shell quote mask; an unterminated quote is treated as running to the end, which covers export truncation. These matches are inside quotes only:
- w2 RevRegenerate:149 V-PROBE — `grep -n "strace probe produced no log\|strace could not be executed"…`. It matches through `\|strace`; no strace was run.
- w2 ScoutSafeDirectory:86 V-PROBE and V-RECURSIVE — `grep -n "guard_path()\|…\|find .*\.git\|-nam…`. It matches through `\|find`.
- w2 RerunSeatAudit:170 V-PROBE and V-RECURSIVE — `grep -nHE '(^|[;&|] )(find |rg |grep -[a-zA-Z…`. V-PROBE matches through `(find`; V-RECURSIVE matches through `|rg`. The seat was grepping for the auditor's own pattern.

Every other row has an unquoted command-position hit. I checked by eye:
- 5 + 1 V-PROBE rows are real `find`.
- 36 + 13 bash V-RECURSIVE rows are real `grep -r…`/`find`; none is inside a heredoc.
- 4 + 5 grep/glob rows are tool calls aimed at the lane or fleet root.

Calibrated w2 minors are 47/52 true positives (V-PROBE 5/8 = 62.5% precision; V-RECURSIVE 40/42). w1 is 20/20. The majors are unaffected.

The 49/49 severity-exact selftest has one quoted-pattern negative case: :289 `pattern-word-not-surface` (`grep -v '^?? census/operator-sweep'` → `[]`). It covers SURFACE_RE only. No selftest bash case puts find/rg/strace/realpath/readlink inside quotes, including the V-PROBE cases at :305-309. I verified this by grepping the auditor for `→ bash\(.*(grep|["'][^"']*(find|rg|strace|realpath|readlink))`; the only match is :289. The 2 V-RECURSIVE false positives are also in base (identical rows), so they predate r17. The 3 V-PROBE false positives are new in r17.

Smallest fix:
- In the bash branch, run :214 and :216 against `unquoted(args)`: copy args with every '…'/"…" span (unterminated spans run to the end) replaced by spaces. Leave the operand of `bash -c`, `sh -c` or `eval` unblanked, because that text is executed.
- Add three selftest negatives built from the rows above: `grep -n "a\|strace b" {lane}/f`, `grep -nHE '(find |rg )' {lane}/f` and `grep -n "x\|find .*\.git" {lane}/f`, each expecting `[]`.
- Expected r16 replay after the fix: w2 minor 52 → 47 (V-PROBE 8 → 5, V-RECURSIVE 42 → 40), with w1 and all majors unchanged. This is [INFERENCE] from the classifier above; a patched auditor was not run, because it is not in my ALLOWED-EXEC.

Residual risk, not adjudicable from the bundle: V-RECURSIVE flags any `grep -…r`, even over exact files where `-r` does nothing (e.g. ReopenS044:58 `grep -rn "S044" tools/souji-census.sh tools/s…`). The operand lists are cut off by the export, so I left these rows as true positives.

### FINDING 2 (LOW, seat scope/hygiene): the sanctioned replay writes into the lane
- seat-audit-replay.py:40-44 `load_module` → `spec.loader.exec_module(mod)` (:43) imports the auditor through SourceFileLoader, and python 3.14.8 runs with `sys.dont_write_bytecode=False` (verified). With A = the lane auditor, it caches bytecode at `tools/__pycache__/souji-seat-audit.cpython-314.pyc`, which is inside the lane, not /var/tmp.
- Current state: `git ls-files --others` and `git ls-files --others --exclude-standard` both list `tools/__pycache__/souji-seat-audit.cpython-314.pyc`, so it is untracked and NOT ignored. stat: birth = modify = change = 2026-10-20 14:47:13.5576 −0300 for both the file and the directory; size 30016; inode 43448945.
- Attribution [INFERENCE]: most likely my changed-auditor run (2.json). Its timing fits: my report file was born 15:06:24, five analysis steps after the replay batch. The rendered transcript carries no wall-clock times, and the raw session log is under ~/.omp, a forbidden surface, so I did not open it.
- I did NOT delete the file (the contract allows writing only this report). L1 should remove `tools/__pycache__/` before any clean-tree measurement. Under C1-D1's `--untracked-files=normal` the census would count the lane as dirty. The r16 ConnReadmeIndex.txt:181 `ls -la tools/__pycache__ …` shows this is a recurring hazard.
- Smallest fix: `sys.dont_write_bytecode = True` before `load_module` in seat-audit-replay.py. Optionally also ignore `__pycache__/`, which only hides the file and does not stop the write.

### FINDING 3 (LOW, provenance)
seat-audit-replay.py:74 stores `"tool": "seat-audit-replay.py"` as a bare name. The record binds the auditor, spec, manifest and manifest-tool digests, but not the runner's own. Smallest fix: add `"tool_sha256": sha256_file(Path(__file__))` to `rec` (:73-84).

### INFO
- Reproducibility should be asserted canonically, using the recipe in A1. The raw sha256 can never match across invocation styles, because `argv` and path relativity are part of the record.
- Reviewer hazard: the `read` tool renders these .txt files with only the embedded export numbers, so reviewers using it will cite lines one too low. My first draft of this report did exactly that; it is corrected above. The context's and the records' citations are correct.

## Verdict
- Reproduction: HOLDS (canonical byte equality, deterministic).
- Claimed numbers: HOLD exactly.
- Adjudications (ConnReadmeIndex true fleet-root write; RerunGateReplayR14 unparsed failed calls): HOLD.
- Calibration of the minor counts: PARTIAL (5/52 w2 false positives, 3 of them in the new V-PROBE class).
- Overall: PARTIAL.

## Self-disclosure (for the L1 seat audit)
- I ran `git -C <lane> status --porcelain -- tools/souji-seat-audit.py census/round-17/seat-audit-replay.py` once at the start. It is not on the read-only git allow-list, and git status may refresh `.git/index` on its own. It printed nothing.
- The changed-auditor run passed `--auditor tools/souji-seat-audit.py` with cwd = lane instead of the absolute path in the ALLOWED-EXEC. It is the same file: the bound sha256 `8268212d…` equals the named file.
- Inline `python3 - <<EOF` and `python3 -c` analyses read only exact named files (my scratch outputs and the two committed records) and wrote only to stdout. I also ran `python3 -c` to print the interpreter version and `date`.
- `stat` on the lane pyc, `tools/__pycache__`, the auditor, and this report; `git ls-files --others` on `tools/__pycache__`.
- Two `read` calls on guessed `w2/<Seat>.md` paths failed with not found. I then made one flat `glob` listing of `census/round-16/transcripts/w2` and grep/read calls on exact named transcript files.
- I read my own `history://` transcript; it has no timestamps.
- Scratch was created and deleted with `rm -rf /var/tmp/souji-r17-RerunSeatAuditReplay`, which also removed the scratch `__pycache__` left by py_compile and the base-auditor import.
