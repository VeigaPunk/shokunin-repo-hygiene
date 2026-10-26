# C2 false-positive map (SwarmScout11) — base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc

Source of the 13: `python3 -B census/round-31/c2-counter.py --root <lane> --rev <base> --base <base> --fleet-root <fleet> --scratch /fast/scratch/hyaku/souji-r31/SwarmScout11/cnt` -> `SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same`.
Gate = `tools/souji-landing-gate.py` (line numbers at base, unchanged in the lane tree at read time).

## Gate emit path (all 13 go through it)
- `POINTER_PATH_RE` 142-147: root prefix then `[^\s`"'()\[\]]+` — takes any non-space run, including `...`, en dash `–`, `:text`, `%d`.
- `_pointer_paths` 848-892: skip filter 851-858 (`…` only, `<>*`, `round-N`, unbalanced braces); comma split 861-872; per-part `_trim_pointer_token` 874; template skip 877-881 (`TEMPLATE_POINTER_RE` line 156 = `%s|<[Nn]>|\{N\}` only); `_normalize_pointer_path` 882 (line 826-833, only `./` `../` normalisation, not involved in any FP); brace/round-range expansion 888-892 re-trims 890.
- `_trim_pointer_token` 820-823: only strips `:\d+(-\d+)?(,...)*$` with ASCII hyphen.
- `check_pointers` 997-1039: exists 1000, capture map 1002-1006 (`_capture_pointer_path` 906-916, no `.captured` twin), exemption 1007-1009, fleet 1012-1032, finding 1033-1039.

## Map (token = counter LANE-FP token; quote = lane line at base)
| # | round | token | source:line | quote (<=25 words) | emitting stage | cause |
|---|---|---|---|---|---|---|
| 1 | 19 | census/round-18/...seat-audit...json | corpus/lessons/round-19-verifier-spotcheck.md:49 | `json.loads(git show tip:census/round-{18,19}/...seat-audit...json)` | 853 filters only `…`; `...` passes; brace expand 888 | ASCII ellipsis placeholder |
| 2 | 19 | census/round-19/...seat-audit...json | same line | same | same | same (second brace member) |
| 3 | 19 | tools/souji-seat-audit.py:274–277 | corpus/lessons/round-19-verifier-spotcheck.md:66 | `final `tools/souji-seat-audit.py:274–277` unconditionally grants all five same-stem` | 822 regex has ASCII `-` only | en-dash line range |
| 4 | 19 | tools/tests/census/corpus | corpus/lessons/round-19-verifier-spotcheck.md:154 | `Preserve tools/tests/census/corpus refusals except exact OWN ONLY contracts` | no stage rejects; absent at 1000 | prose slash alternation, extensionless, unbackticked |
| 5 | 20 | corpus/authority | LOG.md:1106 | `Inherited r20 preregistration and corpus/authority drafts are retained only after` | same | prose, extensionless, unbackticked |
| 6 | 20 | corpus/helper | corpus/lessons/round-20.md:153 | `Bind targeted wrapper and corpus/helper inputs; F5 correction narrows` | same | prose, extensionless, unbackticked |
| 7 | 20 | corpus/knowledge/process-residue-observations.md:58–59 | corpus/lessons/round-20.md:370 | `(`corpus/knowledge/process-residue-observations.md:58–59`; `corpus/QUALITY.md:81`; ...` | 822 | en-dash line range |
| 8 | 20 | corpus/source/QUALITY | LOG.md:1436 | `Existing corpus/source/QUALITY rows and historical receipts remain intact;` | no stage | prose, extensionless, unbackticked |
| 9 | 20 | tests/fixtures/r18-proc-census.sh:395–396 | corpus/lessons/round-20.md:370 | `tests/fixtures/r18-proc-census.sh:395–396, ...` (same line, after `tools/souji-proc-census.sh:243,`) | 822 (comma split 869 works; dash does not) | en-dash line range |
| 10 | 20 | tools/kill/killpg | LOG.md:1123 | `the tools/kill/killpg controls. Carry fixture now requires both baseline` | no stage | prose, extensionless, unbackticked |
| 11 | 24 | corpus/census/tools | corpus/lessons/round-24.md:145 | `` `.ufo/waves/round-23/w2/`, so the corpus/census/tools line numbers are unchanged.`` | no stage | prose, extensionless, unbackticked |
| 12 | 28 | census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:fixture/ | corpus/lessons/round-28-verifier-spotcheck.md:71 | `ignore rules copied into the capture: `census/round-26/.../vadv-49/.gitignore:fixture/` (138),` (full path in lane) | 822 leaves `:fixture/`; 1000/1002 miss `.gitignore.captured` (capture writes `<name>.captured`, tools/souji-wave-evidence-capture.sh:219-223) | `:text` suffix + `.captured` twin not tried |
| 13 | 28 | corpus/knowledge/registry | corpus/lessons/round-28-verifier-spotcheck.md:36 | `git show fec846d:corpus/QUALITY.md | grep -c 'corpus/knowledge/registry'` | no stage (preceded by `'`, inside a code span) | grep literal, extensionless, inside quotes in a code span |

Per-rule groups: ellipsis 1-2; dash 3,7,9; extensionless-prose 4,5,6,8,10,11,13; captured+suffix 12. Total 13.
Not in the 13 (zero base lane hits) but required by fixture G7: `%d`/`%02d` templates -> `TEMPLATE_POINTER_RE` line 156.

## Minimal rules (implemented on scratch copies of the base gate, not in the lane)
- R1 ellipsis: add to the skip filter at 851-858 `or "..." in raw.rstrip(".,;:!?")` (interior `...` only; a trailing `x.py...` still resolves `x.py`). Fixes 1,2 (G4).
- R2 dash: `_trim_pointer_token` line 822 range separator `[-\u2013]` (both occurrences). Fixes 3,7,9 (G5).
- R3 suffix+capture: in `_trim_pointer_token` also `re.sub(r":[A-Za-z][^:/]*/?$", "", token)` after the digit strip; in `check_pointers` after 1002-1006 accept `<path>.captured` and `<capture_path>.captured` present in tree. Only reduces a token to a path that is still resolved, so it cannot hide a missing path with no twin. Fixes 12 (G6).
- R4 template: line 156 `%[0-9]*[sd]|<[Nn]>|\{N\}` (G7 only).
- R5 extensionless prose (G8; fixes 4,5,6,8,10,11,13): placed in `check_pointers` AFTER the exemption block (1007-1009, so exemptions and `checked_ptrs`/`ptr_exempt` counts are unchanged) and before the fleet/finding block: skip when last component has no `.`, path does not end `/`, and the token is not a whole backtick code span (char before and after the match are both a backtick). `_pointer_paths` must yield that flag.
  - REAL pointers unaffected: `census/round-3/garbage-census.out` (has `.`), `tools/__pycache__/` (trailing `/`).
  - Alternative R5-lexical (E0): drop the whole-span condition (extensionless + no trailing `/` + absent = skip). It also passes G8 when the fixture backticks the tokens, but FAILS two existing selftest cases (below) and drops pass count 65 -> 63.

## Measured (scratch copies; commands below)
- `--selftest`: base `SELFTEST pass=65 fail=0`; R1-R5 whole-span: `pass=65 fail=0`; R5-lexical: `pass=63 fail=2` (FAIL `quarantine-path-absent`, FAIL `pointer-exemption-prefix`).
- Lane rounds 18-30 at base content, patched (whole-span) vs base: exactly the 13 LG-DANGLING-PTR lines removed, 0 added, every other finding and `checked_ptrs` unchanged; per-round `findings=` 7->3 (r19), 6->0 (r20), 18->17 (r24), 21->19 (r28); remaining pointer lines = the two REAL (r23).
- Fixtures with patched tool: r16 `total=15 failed=0`; r30 `cases=7 pass=7 control=FALSE-GREEN-REJECTED`; r19 `total=4 failed=0 base_discriminating=2`; r18-landing-pointers `total=11 failed=0` (REGRESS leg stays `same`).
- Synthetic G4-G9 lane (scratch git repo, N=18; G6 twins `.gitignore.captured` `.gitattributes.captured` committed): base emits 16 DANGLING lines (every G4-G8 path plus the six G9 ones); patched emits exactly the six G9 paths — `tools/missing.py`, `census/round-18/waves/w1/missing.md`, `.ufo/waves/round-18/w1/missing.md`, `corpus/knowledge/missing.md` (line spec removed), `census/round-3/garbage-census.out`, `tools/__pycache__/`. G8 with backticked tokens: whole-span rule emits `corpus/authority`, `tools/kill/killpg`, `tools/tests/census/corpus` extra (G8 FAIL; prose-form G8 passes); lexical rule passes both forms.
- Prereg wording `census/round-N/...` in G6/G9: the gate skips any token matching `round-N` (line 149, 855), so N in the fixture must be a concrete number or G9 could not emit its lines.

## Selftest / fixture cases whose output could change per rule (gate selftest table, lines 1309-2316)
- R1 `...`: none. `pointer-placeholder-skip` (1533-1542) uses `…`, `*`, `<script>`, `round-N`, `{seat-01..64.json,` (two dots only) — all already skipped; unchanged.
- R2 dash: none (no en-dash pointer in the table). `pointer-line-suffix` (1505-1511), `pointer-comma-line-suffix` (1515-1517), `pointer-brace-line-suffix` (1521-1523) use ASCII digits and stay identical.
- R3 `:text` strip / `.captured` twin: none (grep of table finds no root path followed by `:letter`; no `.captured` fixture). `pointer-line-suffix` input `corpus/missing.md:42:` still ends with expect_paths `corpus/missing.md`.
- R4 `%d`: none (no `%d`/`%02d` pointer token in the table; `%`-formats in the table are Python-side).
- R5 extensionless — the only risky rule. Extensionless pointers in the table (4 sites): `pointer-exemption` 1568-1582 (`corpus/intentional-runtime-state`, exempt, counts 6/1/0 — protected because the skip sits after the exemption check), `quarantine-path-exemption` 1584-1594 (`.ufo/quarantine/round-18/empty-stub`, exempt, counts 5/1/0 — protected), `quarantine-path-absent` 1596-1604 (`.ufo/quarantine/round-18/absent-stub`, expects 1 LG-DANGLING-PTR — BREAKS under the lexical rule), `pointer-exemption-prefix` 1745-1755 (`corpus/runtime-extra`, expects 1 dangling, counts 6/1 — BREAKS under the lexical rule). Both stay green under the whole-span rule because those tokens are whole backtick spans.
- Lane exemptions (`corpus/pointer-exemptions.tsv`): `.ufo/quarantine/round-17/.../dot-git-empty-stub` is extensionless; a skip placed before the exemption check (in `_pointer_paths`) would turn it into LG-DANGLING-PTR-EXEMPT-STALE — keep R5 after 1007-1009.
- External fixtures that run the gate: `tests/fixtures/r16-landing-gate.py`, `r18-landing-pointers.py`, `r19-carry-wrap.py`, `r30-landing-gate-discovery.py` — all unchanged (above).
- Pass-count constraint: C2's REGRESS leg and C1 bindings compare `SELFTEST pass=65 fail=0`; adding selftest cases to the gate changes the last line, so G1-G10 belong in the new standalone fixture, not the selftest table. Editing the two broken cases (e.g. `absent-stub.md`) would keep 65 but weakens extensionless coverage; not needed with the whole-span rule.

## Decision needed from the L1/fixture author
G8 text form: prose (whole-span rule, selftest untouched) vs backticked (needs lexical rule plus editing `quarantine-path-absent` and `pointer-exemption-prefix` inputs, count stays 65). The preregistration line says "(no extension, no trailing slash, absent)", which reads lexical; lexical alone cannot keep the selftest table unedited.
