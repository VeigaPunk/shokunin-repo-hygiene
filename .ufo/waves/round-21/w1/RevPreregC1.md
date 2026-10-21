# C1 preregistration review — calibration

STATUS: PARTIAL — the frozen C1 rule has a concrete parser disagreement, and the required before-implementation review encountered an uncommitted C1 implementation in the lane working tree. The after-vs-oracle idea can falsify an incorrect implementation, but the frozen measurement and harm-guard wording does not yet pin enough detail for independent, repeatable adjudication. No implementation or test was run by this read-only reviewer.

## Findings, highest severity first

### High — grep path parsing can disagree with the frozen rule

C1 defines `grep(PATTERN @ PATH) -> PATH` and says a complete grep call with no literal ` @ ` separator is an implicit-cwd search and must be flagged. It does not define ` in ` as a path delimiter. The uncommitted `tools/souji-seat-audit.py` diff adds a second delimiter: it parses `args.rsplit(" in ", 1)` before treating a no-`@` grep as implicit cwd. This can change the verdict, not just its diagnostic target.

Counterexample rendered call:

```text
→ grep(pattern in souji-shokunin/x) ⇒ ok
```

Reading the preregistration literally: no ` @ ` is present, so the target is implicit `.` at the fleet root, outside the lane: flag. Reading the current uncommitted implementation: ` in ` introduces `souji-shokunin/x`, which resolves inside the lane: do not flag. The committed r20 corpus also contains `grep` patterns with literal ` in ` text (for example `census/round-20/transcripts/recovery-final/GrantPatch.txt:65`), so inferring a delimiter from those characters is unsafe.

**Suggested exact wording:** “For `grep`, the only path delimiter is the literal string ` @ `; use its final occurrence to separate `PATTERN` from `PATH`. Do not interpret ` in ` as a delimiter. If complete arguments contain no ` @ `, use `.` as the implicit path.” If a legacy ` in ` form is intentionally supported, name it explicitly as an alternate syntax, define precedence and truncation behavior, and change the no-`@` rule accordingly.

### High — the corpus and oracle comparison are not fully executable from the command as written

`count-read-root.py --tool T` does not state what `T` denotes, how the baseline and after invocations are formed, which exact files are inputs, what key identifies one call in the TSV, or how oracle disagreements are settled. The fixture’s `--tool T --base-tool B` suggests T/B are auditor programs, but the count command does not say so. “Every committed transcript” should exclude `MANIFEST.sha256` and define whether only direct `*.txt` files are included. It must also prevent silent omissions: the existing auditor `run()` loops over `spec["items"]`; an extra transcript not named in that spec is not audited. For example, `census/round-20/transcripts/recovery-final/CorpusAdmission.txt:45` contains `→ glob(corpus/lessons) ⇒ error`; an incomplete spec can omit that call without making the auditor report it as missing.

The oracle needs a call identity that includes the full corpus-relative path. `GrantPatch.txt:65` occurs in both `recovery/` and `recovery-final/`; basename-plus-line keys would collapse distinct transcript calls. Equality on aggregate counts would also permit one call to disappear while another is added.

**Suggested exact wording:** “Run the counter twice with `--tool` set to the auditor executable: B is `git show 6ff3413bba9c8430c3b0bc4d2052e21d0407183f:tools/souji-seat-audit.py`; T is the auditor at the measured commit. The input universe is every direct regular `*.txt` member of each of `census/round-20/transcripts/final`, `.../recovery`, and `.../recovery-final`; exclude manifests and do not recurse. Fail nonzero if any transcript cannot be parsed or is not audited exactly once. The oracle TSV has one positive row per flagged call with key `(corpus-relative transcript path, 1-based physical line number, tool)`; compare sorted key sets, not counts or target-display text. Publish the TSV header and a deterministic adjudication rule for disagreeing labels before counting.”

### Medium — error-result calls have no pinned treatment

The rule never says whether an attempted read that returns `error` is still a violation. The uncommitted implementation flags independently of status, while an oracle could reasonably count only successful reads. This is present in the corpus: `census/round-20/transcripts/final/ReopenHistoryReject.txt:54` is a relative `read(.ufo/...) ⇒ error`, and `census/round-20/transcripts/recovery-final/CorpusAdmission.txt:45` is a relative `glob(corpus/lessons) ⇒ error`.

**Suggested exact wording:** “Classify attempted calls regardless of rendered result status; `⇒ error` remains eligible for V-READ-ROOT.” (If only successful operations are intended, explicitly say the opposite and apply it consistently to the oracle.)

### Medium — the truncation rule does not define which part must contain the marker

C1 exempts a call when its **path portion** is truncated, but the uncommitted implementation skips a component whenever `…` appears anywhere in it; for grep without ` @ ` it skips if `…` appears anywhere in the arguments. These differ for a complete visible path with a clipped selector, e.g.:

```text
→ read(MANIFEST.json:20-…) ⇒ ok
```

The path `MANIFEST.json` is visible and outside the lane; only the selector suffix is clipped. One oracle can flag it because the target path is complete, while the current code suppresses it. A truncated grep pattern with no visible path (`→ grep(pattern… ) ⇒ ok`) raises the analogous question: the arguments are incomplete, but the implicit path may still be known—or the truncation may hide a separator and path.

**Suggested exact wording (conservative, matching the current code):** “Treat a call as incomplete if U+2026 occurs anywhere in its rendered argument text; do not emit V-READ-ROOT for that call, including when the marker is in a grep pattern or read selector. Only classify complete argument text.” Alternatively define path extraction first and suppress only when the extracted path itself is cut; also say how a clipped pattern can hide a path delimiter.

### Medium — read-selector grammar is underspecified

C1 lists `:N`, `:N-M`, `:raw`, and comma lists, but does not say whether this is exhaustive. The read tool also documents selectors such as `:img` and `:conflicts`, plus time/range forms and combinations. The uncommitted parser strips `:img` and numeric/time forms but not `:conflicts`. For example:

```text
→ read(souji-shokunin:conflicts) ⇒ ok
```

An oracle that recognizes `:conflicts` resolves the pathname to `souji-shokunin` (the lane root) and does not flag it; the current parser treats the suffix as part of a fleet-relative name and flags it. Even where the verdict is unchanged, target text and TSV rows can differ.

**Suggested exact wording:** “For `read`, remove the terminal selector chain using the read tool’s documented selector grammar for this wave, including `:raw`, `:img`, `:conflicts`, line ranges, video-time selectors, and valid selector combinations; then classify the remaining path. Do not infer a selector from an unrecognized colon suffix.” Pin the grammar/version used for both the auditor and oracle.

### Medium — the harm guard’s count-only alternative is weaker than its verdict requirement

“no existing class verdict … changes” is stronger than “per-class counts identical.” Counts do not prove verdict-set equality: a baseline may flag call A for `V-RECURSIVE`, while after flags call B for the same class; the count remains one. The same limitation applies to a summary such as `SELFTEST pass=118 fail=0` if case identities/expected verdicts can change while totals remain constant. The current uncommitted diff is additive, but the frozen acceptance rule should test the stated invariant directly.

**Suggested exact wording:** “For every pre-existing class, require exact equality of sorted per-call tuples `(corpus-relative transcript path, line, tool, class, severity)` between B and T on the full frozen transcript set; counts are summary-only. Preserve the exact existing selftest and fixture case-ID/verdict matrix, not only totals.”

### Low — the baseline-zero and positive-base-discriminating checks are not meaningful falsifiers by themselves

At pushed base `544c8358039a07e8b45e6db72312da5c8d965275` (same auditor as claim base `6ff3413bba9c8430c3b0bc4d2052e21d0407183f`), `V-READ-ROOT` and `implicit_root_read` are absent. Therefore “before = expected 0 V-READ-ROOT” is guaranteed by the missing class and cannot detect an undercount; likewise, a positive case is inherently distinguishable from a baseline that cannot emit the class. The after-set/oracle equality remains the meaningful falsifier once its universe and key are pinned.

**Suggested exact wording:** “Record B=0 only as a baseline compatibility observation, not as evidence of coverage. Acceptance depends on exact T-vs-oracle call-set equality, and the synthetic fixture must assert each named positive and negative expected verdict under T.”

## Soundness and residual risk

The explicit exclusion of absolute, `~`, and URI targets limits C1 to relative fleet-root resolution; it does not establish detection of every read from outside the lane. Keep that scope statement adjacent to the claim. The lower-bound treatment of truncated arguments is similarly intentional only if the marker rule is pinned. The `^[a-z]...://` URI expression is lowercase-only; a counterexample such as `read(Skill://godspeed)` is a URI under case-insensitive URI-scheme rules but is classified as relative by that regex. Pin either a case-insensitive scheme grammar or an explicitly lowercase-only URI definition.

The principal measure can fail in principle: an extra or missed V-READ-ROOT call should fail exact comparison. As frozen, however, the before-zero leg cannot fail for semantic reasons, and the unspecified input coverage/keying and oracle-label reconciliation prevent independent reproduction without interpretation.

## Evidence and verification limits

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- tools/souji-seat-audit.py tests/fixtures/r20-audit-contract.py tests/fixtures/r19-seat-audit-shapes.py` exited 0 and printed ` M tools/souji-seat-audit.py`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff 544c8358039a07e8b45e6db72312da5c8d965275 -- tools/souji-seat-audit.py` exited 0 and showed `37 insertions(+), 0 deletions(-)`, including the parser divergence above. This reviewer did not author that change and did not infer its author.
- Pinned-revision `git grep -n "V-READ-ROOT" ... 544c835... -- tools` and `git grep -n "implicit_root_read" ... 544c835... -- tools` each exited 1 with no matches.
- Corpus scans found 5 relative non-scheme read/glob rows, 82 grep rows without ` @ `, and 275 read/grep/glob rows containing the renderer ellipsis; these show why delimiters/truncation need exact rules. These are literal text scans, not runtime or semantic proof.
- `read xd://lsp` returned `No such tool: xd://lsp`; no LSP status/references/definition/diagnostics were available. No build, test, lint, formatter, or target-code execution was run, as required for a read-only seat. No tools were installed.