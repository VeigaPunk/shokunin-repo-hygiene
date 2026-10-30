# R43scout01 — held-out C2 coverage matrix

Axes: source fidelity, explicit grammar, independently enforced coverage. Read-only source investigation; no candidate execution, installation, fixture, clone, or scratch directory was needed. Verdict: named input/dispatch/heading holes are mostly represented; D4/D5 remain GAPs. Timeout handling is bounded but does not implement the promised refusal diagnostic. Frozen instruments were not changed.

## Evidence binding and method

The three r43 instruments read here match frozen commit `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373`: the read-only diff command below emitted no diff. Observed lane HEAD was `8dfad888d7b7673de41cdcd92f30244c16e38519`, not the supplied historical master tip. Findings concern the frozen instrument bytes, not that newer tip.

The three requested unsuffixed reports do **not** exist under `census/round-42/waves/w2/`; glob found their committed copies under `waves/w1/`. The three `R42w2*` reports exist under `waves/w2/`. Pointers below deliberately correct this location error.

`read xd://lsp` returned `No such tool: xd://lsp`. No semantic server was available; definitions/callers were inspected as literal source text, not represented as LSP proof. Confidence is high for quotations/table membership; coverage conclusions are static source inferences, not observed candidate passes.

Abbreviations: W1 = `census/round-42/waves/w1/`; W2 = `census/round-42/waves/w2/`; T = `census/round-43/c2-cases.tsv`; H = `census/round-43/c2-hidden-audit.py`; C = `census/round-43/c2-counter.py`. Every quotation below is at most 25 words.

## Coverage matrix

| Finding (exact quotation) | Source pointer | Already forced? Covered by case id or GAP |
|---|---|---|
| D1: “`dup-base-differs` expectation is not entailed by the grammar.” | W1/R42critic03.md:48 | **Yes.** `dup-key-first-bad` and `dup-key-first-good` (T:6–7) distinguish skipping/all/last from first-wins; C:13–14 explicitly selects first-wins. |
| D2: “no case for the any-depth clause of the DISPATCH widening.” | W1/R42critic03.md:50 | **Yes.** `h9-dispatch-depth-three` (H:121) places `w9/w8/deep-spec.json` before freeze; `h7-dispatch-notes-ready` (H:119) covers `.ready` substring. C:43 makes the audit a required leg. |
| D3: “no case for a missing `Round:`.” | W1/R42critic03.md:52 | **Yes.** `round-missing` (T:11; C:158–159,184) requires `C0:FIELD-MISSING`. This is inherited behaviour; unlike malformed Round, the short r43 grammar does not separately restate it. |
| D4: “the patches leg probes call spelling, so honest code is rejected.” | W1/R42critic03.md:54 | **No — GAP D4.** No new/hidden case covers spelling-independent selftest fault injection. C:39–42,351–371 explicitly retains the r42 counter and requires `patches=3/3`. Thus this remains a restriction, not a closed hole. |
| D5: “the patches leg counts any nonzero exit as "rejected".” | W1/R42critic03.md:56 | **No — GAP D5.** No new/hidden case distinguishes an intended failing selftest from crash/refusal. The required r42 patch leg remains; C's own successful-selftest leg (46) cannot establish why patched executions failed. |
| A1: “It does not say which occurrence the value checks read.” | W1/R42reviewer02.md:50 | **Yes.** `dup-key-first-bad`, `dup-key-first-good`; C:13–14 resolves the ambiguity. H's `h6-duplicate-three-occurrences` (118,143–154) additionally requires two duplicate findings, intentionally changing the old per-key rule. |
| A2: “an implementer who runs the content checks independently gets two findings.” | W1/R42reviewer02.md:53 | **Yes, inherited case enforcement; no new clarification.** `population-symlink` in the required `r42table` leg (C:39–42) pins SYMLINK-only. No r43 visible/hidden population-symlink case or new population-specific grammar is added. W1/R42critic02.md:84 independently identifies this weakly stated policy. |
| N1: “The cases do not exercise this, because the malformed line is always last.” | W1/R42reviewer02.md:58 | **Yes for malformed headings followed by keys.** `heading-unattached-key` (T:8; C:152–153), `h3-two-unattached-keys` and `h4-unattached-before-valid-claim` (H:113–116); C:15–17 explicitly orphans subsequent keys until a valid claim. This does not define all digitless `## C`/`##C` boundary variants. See caveat below. |
| E-6 Round: “zero-padded or fullwidth `Round:` digits do not trigger DISPATCH-BEFORE-FREEZE” | corpus/lessons/round-42.md:223 | **Yes, by rejection rather than normalisation.** `round-zero-padded`, `round-fullwidth` (T:9–10). C:18–19 requires `ROUND-MALFORMED` and no dispatch scan. H:112 adds `h2-round-spelled-x`; H:111 accepts surrounding trailing whitespace. W2/R42w2critic02.md:52 gives the original A21/A22 witness. |
| E-6 Control: “a Control symlink whose link text is `EXIT=1` is read as red” | corpus/lessons/round-42.md:223 | **Yes.** `control-symlink-text` (T:12; C:162–163) and `h5-control-symlink-exit0-text` (H:117) demand `CONTROL-SYMLINK` for opposite link texts; C:20–21 forbids red-control reading. Original: W2/R42w2critic02.md:50. |
| E-6 reach: “FROZEN-EDITED does not cover the Control and a post-freeze edit of the preregistration itself is invisible” | corpus/lessons/round-42.md:224 | **Yes.** `frozen-edit-control` and `frozen-edit-prereg` (T:13–14; C:169–174) require C1/C0 findings respectively; C:22–24 explicitly extends scope. Original: W2/R42w2reviewer04.md:274–289. |
| E-6 boundary: “the HEADING-MALFORMED block-boundary clause is undefined in the docstring” | corpus/lessons/round-42.md:224 | **Yes for the named malformed-heading/key case.** Same `heading-unattached-key`, h3/h4 and C:15–17 as N1. W2/R42w2reviewer04.md:224–267 explains the precise open-block issue; W2/R42w2critic03.md:136–137 confirms downstream lost fields. |
| Timeout: “`run_tool` has no timeout handler” | corpus/lessons/round-42.md:189 | **Yes for bounded failure; GAP for exact refusal contract.** No case id: C `run_tool` (191–197) catches `TimeoutExpired`; table scoring (293–296) records `<case>:timeout`, loses that case, and eventually exits 1. C:31–32 instead promises refusal `CANDIDATE-TIMEOUT`; that token occurs only in its docstring. The nested r42 run is bounded by `run_script(...,1800)` (364–367), not repaired internally. H `run` (91–97) similarly converts timeout to scenario failure. No timeout probe was run. |

The requested “E-6 list” includes a provenance conflation: timeout is in the lesson's **N-C2c** at line 189, not the E-6 paragraph at 223–224. Both are covered above without misquoting their locations.

## Precise GAP / amendment dispositions (L1 findings only)

1. **D4 attacks C2 operability/retained patch leg:** a future, pre-freeze instrument should test semantic fault effects independently of `hashlib.sha256` vs `hashlib.new`, `run` vs `Popen`, argv spelling, and isolated child launch. Current C intentionally preserves the old leg. Do not amend the frozen r43 bytes.
2. **D5 attacks C2 discrimination/retained patch leg:** a future instrument should require an actual failing selftest result and reject traceback/refusal-only nonzero exits, not count any nonzero as a kill. No such discrimination case appears in T or H.
3. **Timeout attacks C's documented refusal contract:** choose/document either unmet-target timeout reporting (implemented) or enforce `REFUSAL CANDIDATE-TIMEOUT`/exit 2 (not implemented). Bounded failure itself is already present. This is not evidence of a hanging current candidate.
4. **Boundary scope caveat attacks completeness beyond N1:** W2/R42w2reviewer04.md:253–259 distinguishes digitless `## C` from `##C`. T/H test `##C2`, not those digitless variants. C's new grammar resolves the malformed-digit case, not every heading-like spelling; do not claim universal boundary coverage.

## Relevant static inconsistency (not an executed failure)

H:115–116 sets h4's expected classes to `[...,'C2:FIELD-MISSING*4']`, but `classes` (H:100–106) emits individual `LABEL:CLASS` strings and H:160 compares against `sorted(want)` without expanding `*4`. Therefore [INFERENCE] an ordinary candidate emitting four `C2 FIELD-MISSING` lines cannot satisfy h4 as written. This attacks the frozen hidden audit's reachability, not candidate parsing. The h4 entry nominally expresses the desired boundary reset, but executable enforcement is malformed. h3 and the visible heading case still independently enforce orphan-key rejection. Flag for L1; no fix applied.

## Exact commands and observed outputs

Shell command actually executed (cwd `/home/vgpnk/Projects/shokunin`; exit 0):

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 -- census/round-43/c2-cases.tsv census/round-43/c2-hidden-audit.py census/round-43/c2-counter.py && git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 census/round-43/c2-cases.tsv census/round-43/c2-hidden-audit.py census/round-43/c2-counter.py
```

Observed stdout (no intervening diff):

```text
8dfad888d7b7673de41cdcd92f30244c16e38519
100644 blob 474de2a824c2ef20af15e6c990d5aac74ae02fda census/round-43/c2-cases.tsv
100755 blob 09bd4580be0717eabf8e514c39c00e9854d049df census/round-43/c2-counter.py
100755 blob bb755c25d5f0b65adb8fc7ff5a39d5df41be81db census/round-43/c2-hidden-audit.py
```

Source-inspection tool calls (not test commands): `read skill://godspeed`; `read /home/vgpnk/.omp/agent/RULES.md`; `read xd://lsp` (unavailable, as above). `grep` first searched the supplied W2 directory for `D[1-5]|A1|A2|N1|E-6|zero|fullwidth|FROZEN-EDITED|HEADING-MALFORMED|timeout`; its broad results were narrowed to the six named paths, which reported the three missing unsuffixed files. `glob /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/**/R42reviewer02.md;/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/**/R42critic02.md;/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/**/R42critic03.md` returned all three in W1.

Relevant ranged `read` calls, all with the absolute lane prefix, were:

```text
census/round-42/waves/w1/R42critic03.md:43-95
census/round-42/waves/w1/R42reviewer02.md:40-110
census/round-42/waves/w1/R42critic02.md:53-85
census/round-42/waves/w2/R42w2critic03.md:128-158
census/round-43/c2-counter.py:1-100
census/round-43/c2-counter.py:116-197,275-311,351-374
census/round-43/c2-hidden-audit.py:100-230
```

Literal `grep` results supplied the additional cited lines: W2/R42w2critic02.md:50,52; W2/R42w2reviewer04.md:224–267,274–289; corpus/lessons/round-42.md:189,223–224; T:6–14; H:91–97; and the retained `census/round-42/c2-counter.py` patch definitions at 299–327 and nonzero counting at 408–410. Source-only finding; no scoring, test, build, mutation, or install was performed. No scratch exists to retain or clean. Only this assigned report was written.
