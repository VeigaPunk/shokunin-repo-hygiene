# R43critic01 — frozen-instrument attacks

Axes: **calibration, operability, coverage**. Review only; no instrument, production candidate, tracked lane file, or sibling file was edited. Findings below are amendments for L1, not permission to change frozen scoring.

## Provenance and commands actually run

Evidence directory: `.ufo/waves/round-43/w1/R43critic01/` (all evidence links below are relative to the lane).

Frozen instrument bytes were loaded with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:<path>` by the retained drivers. Read-only `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse refs/heads/master` observed **8dfad888d7b7673de41cdcd92f30244c16e38519**, not the assignment's earlier master. The eight frozen/current SHA-256 comparisons in [control-probe.json](R43critic01/control-probe.json) all match, including both counters used by the attacks, tables, scorer, and the pinned drift tool (b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6). C1 scoring used the mandated scorer's current-master clone; it was not falsely represented as a clone of the earlier master.

Top-level commands, both exit 0:

```sh
mkdir -p /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43critic01 /fast/scratch/hyaku/souji-r43/R43critic01
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43critic01/probe.py
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43critic01/control-probe.py
```

[probe.py](R43critic01/probe.py) retains every subordinate command and exact input construction: three concurrent C1 scorer executions, all nine frozen C2 builders, a pristine/S13 parser pair, and the exact C3 execution-count shim leg. [control-probe.py](R43critic01/control-probe.py) retains the provenance comparison and exact extracted-memorizer execution. Both drivers explicitly set TMPDIR and remove their entire owned scratch directory in `finally`. Scratch names in command transcripts are ephemeral invocation arguments, not evidence locations. No tools installed or upgraded.

Each C1 invocation was exactly:

```sh
bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/score-candidate.sh c1 /fast/scratch/hyaku/souji-r43/R43critic01/NAME corpus/lessons/round-43.md=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43critic01/NAME.md
```

NAME was `c1-good`, `c1-derived-wrong`, and `c1-register-duplicate`. The last additionally supplied `census/round-43/c1-required.tsv=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43critic01/c1-register-duplicate.tsv`. Exact argv, exit codes, stdout and stderr are retained in each NAME.json.

## Finding table

| finding | instrument | exact input | observed | why it is wrong |
|---|---|---|---|---|
| **F1 — correction's derived value never checked** | `census/round-43/c1-counter.py:240–253` | [c1-derived-wrong.md](R43critic01/c1-derived-wrong.md): required D1 says `derived=rows=999999`, D2 `derived=W04=999999`, D3 `derived=0000000000000000000000000000000000000000`; all other required tokens unchanged | [c1-derived-wrong.json](R43critic01/c1-derived-wrong.json): exit **0**, `SUMMARY required=3 registered=3 missing=0 junk=0 fenced=0 duplicate=0 retracted=0 rederived=3 rederive_failed=0 new_mismatches=0` | Captured `derived` is omitted from the tuple comparison. Re-derivation checks register values, not the correction's asserted values. Three false corrections receive the exact target reading. **Calibration: confirmed false green.** |
| **F2 — duplicate register silently overwrites false required row** | `census/round-43/c1-counter.py:211–217` + `c1-required.tsv` parser | [c1-register-duplicate.tsv](R43critic01/c1-register-duplicate.tsv): prepend a D1 row with `derived=rows=999999`, then the original three rows; [lesson](R43critic01/c1-register-duplicate.md) supplies the original three corrections | [c1-register-duplicate.json](R43critic01/c1-register-duplicate.json): exit **0**, same complete target SUMMARY as F1 | Four physical required rows collapse to three dictionary entries; the false first D1 requirement disappears, with no refusal or duplicate count. This is an ambiguous/contradictory register accepted as a clean frozen authority. **Calibration: confirmed register-shape weakness; distinct from lesson duplicates.** |
| **F3 — hidden-control rejection is not evidence against memorization** | `census/round-43/c2-counter.py:310–325` | Execute the *unchanged generated stub*, extracted directly from the frozen source, with an ANSWERS entry whose SHA matches an existing prereg file; [extracted stub](R43critic01/c2-memorizer-extracted.py) | [control-probe.json](R43critic01/control-probe.json): exit **1**, empty stdout, `NameError: name 'os' is not defined` at `os.path.exists(path)` instead of its registered visible answer | Generated code imports only `hashlib, sys`. It cannot demonstrate visible-case memorization before hidden rejection. Additionally, the frozen invocation passes relative `prereg.txt` from work rather than the fixture root, while the stub opens it directly. **Operability/calibration: confirmed invalid discrimination control; full hidden audit was not run.** |
| **F4 — execution-count shim accepts zero tool executions** | `census/round-43/c3-counter.py:384–400` | [c3-no-tool-fixture.py](R43critic01/c3-no-tool-fixture.py): prints 17 PASS cases, writes 17 lines to inherited `SHIM_LOG`, never reads or executes `--tool` | [c3-probes.json](R43critic01/c3-probes.json): exit **0**, `SUMMARY cases=17 pass=17 fail=0`, `logged_invocations=17`, exact predicate `shim_ok=True`; actual tool calls **0** (fixture source has no process invocation) | Candidate receives the writable log pathname. Self-authored log lines are accepted as wrapper execution evidence. This is a demonstrated **counter-leg** bypass, not a claim that this fixture passes the whole C3 counter. **Coverage/calibration: confirmed false execution provenance.** |
| **F5 — N10-before provenance not established for the submitted fixture** | `census/round-43/c3-counter.py:322–330,408–410` | Inspect exact frozen `target` predicate and changed-tool branch, retained in [c3-probes.json](R43critic01/c3-probes.json) | `tests_n10_before=false`; any tool SHA different from the pinned SHA assigns `n10_before="base-receipt"` without running that candidate fixture on pinned bytes | The candidate fixture is absent from the frozen base and can be submitted later; a historical receipt cannot establish its pristine failure set. The stated requirement that the submitted fixture fail exactly case-json-symlink-leaf on pinned bytes is not gated. **Coverage/calibration: source-proven missing gate/false provenance risk; no full-counter bypass claimed.** |
| **N1 — C2 visible builder attack did not break** | `c2-cases.tsv` and frozen `CASE_BUILDERS/build` | Build all nine original cases, inspect prereg blobs, committed Control mode, freeze→tip paths and commit subjects | [c2-builders.json](R43critic01/c2-builders.json): control-symlink-text is **120000**, not regular; control edit changes exactly `census/control.txt`; prereg edit changes exactly `prereg.txt`; malformed round/heading and duplicate-key bytes match their named cases | No builder/name or want-multiset contradiction found in these nine cases against the normative grammar. Inspection is not a run of a compliant production candidate; no 9/9 claim. **Operability: bounded attack survived.** |
| **N2 — C3 S13 anchor/probe flip is real** | `c3-survivors.tsv` S13 + frozen MUTANTS anchor | Record `REPO\tr\tregs=\tprunable=0\nTOTAL\trepos=1\tregs=0\tprunable=0\n`; apply exactly S13 old→new replacement to pinned tool; call each `parse_record` | [c3-probes.json](R43critic01/c3-probes.json): pristine `Refusal: RECORD-MALFORMED: line 1 does not match the census schema`; mutant `ValueError: invalid literal for int() with base 10: ''` | Mutation genuinely changes the empty-regs refusal into an uncaught conversion error; no misnamed/non-flipping anchor defect found for S13. This was a parser-level probe, not all 16 mutants or the full fixture. **Coverage: selected anchor attack survived.** |

For comparison, [c1-good.json](R43critic01/c1-good.json) also records exit 0 and the same SUMMARY. False-derived prose is therefore observationally indistinguishable from the valid baseline to this counter.

## Smallest safe corrections (L1 amendments only; not implemented)

1. **F1:** compare the prose `derived` token with `req['derived']` before registration, alongside the other four tokens. Retain committed-byte re-derivation.
2. **F2:** refuse a repeated register ID before dictionary assignment. Do not choose either duplicate as authoritative.
3. **F3:** generate the missing `os` import, resolve relative prereg paths against `--root`, and require that the memorizer actually reproduces the visible table before treating hidden rejection as discrimination. A crash must not substitute for the claimed control behavior.
4. **F4:** keep the invocation log outside candidate write authority, or use supervisor-owned process observations. A candidate-writable log cannot attest to execution; merely hiding its environment variable is not a trust boundary.
5. **F5:** run the submitted fixture on the pinned tool on every score and gate on the exact N10 failure set plus the protocol's exit/SUMMARY requirements. Print `base-receipt` only for a receipt demonstrably bound to those same fixture bytes.

Verdict: F1 is a complete scored calibration counterexample; F2 is a second complete scored register counterexample. F3 and F4 invalidate specific discrimination/provenance legs. F5 is a missing acceptance check demonstrated from the frozen predicate. These are fixable instrument defects, not permission to alter frozen instruments or an admission/ship decision. No full C2/C3 score or full 16-mutant coverage claim was attempted.

Self-check: accuracy 4/5 (full C2/C3 target not exercised, explicitly bounded); completeness 4/5 (all three assigned surfaces attacked; only one C3 anchor dynamically checked); clarity 4/5 (exact commands are split between retained drivers and receipts); actionability 4/5 (five minimal L1 corrections, not implementations); conciseness 4/5 (report is necessarily longer than terminal summary). Overall 4.0/5. Improvement priority: bind fixture identity to baseline evidence, then replace self-authored execution attestations. No observed claim is expanded into an unrun pass.
