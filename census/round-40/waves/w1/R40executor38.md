# R40executor38 — C2 wrapped-docstring edge attack

## Scope and named edge

**Distinct edge: over-joining across a class-entry boundary (continuation attribution), with the existing `EISDIR` false attribution as a concrete negative control.** This is separate from the preregistered positive probe (a trigger moved from a class line onto its wrapped continuation). No production files or frozen claims were changed.

## Evidence

- Frozen C2 predicate: `census/round-40/preregistration.txt:7-8` requires joining wrapped continuation lines, checking every frozen observed class/trigger pair, detecting a synthetic wrapped-trigger probe, and agreement with runtime behavior. The control is explicitly `r39 docstring_classes` extracting only the first class line.
- The r39 extractor is `census/round-39/c2-counter.py:133-144`: it splits the module docstring on `\n`, strips each line, recognizes lines starting with `RECORD-MISSING` or `RECORD-MALFORMED`, and stores only that first line (`:139-143`). It does not associate any following continuation line with the class.
- Runtime class source is `tools/souji-worktree-drift.py:124-148`: `os.open(..., O_RDONLY | O_NONBLOCK)`; `ENOENT` raises `RECORD-MALFORMED` (`:133-135`); other open errors raise `RECORD-MISSING` (`:136`); a non-regular descriptor raises `RECORD-MALFORMED` (`:137-139`).
- Committed prior measurement ` .ufo/waves/round-39/w1/W1ExecC2Docstring.md:190-210` records an explicit negative: the current docstring advertises `EISDIR` for `RECORD-MISSING`, but directory open succeeds and the `fstat` check raises `RECORD-MALFORMED`; observed both revisions. This demonstrates why validating just string presence, even after joining lines, is not sufficient: each named trigger must be checked against the class actually raised.
- Another committed counterexample documents weak mapping semantics: `.ufo/waves/round-39/w1/W1RevC2Doc.md:101-107` says the class token itself makes the `missing` substring check tautological for `RECORD-MISSING`; `:117-127` and `:141-152` describe wrong-class docstring mutations that L4 did not catch. These are prior evidence that mapping must be directional and trigger-specific, not token/presence-only.

## Attack result / bounded measurement plan

**Verdict: bounded, unmeasured risk for r40; no falsifier of its candidate implementation is claimed.** The frozen contract requires the positive wrapped-trigger probe but leaves the class-boundary semantics unspecified. A join implemented as a broad multi-line search can accidentally attribute continuation text to the preceding entry, or pass based on a trigger string which runtime never raises. The committed `EISDIR` discrepancy supplies an exact negative-control pair.

Bounded candidate measurement (not run here; candidate analyzer/counter bytes are not present in the preregistration or the r39 artifacts read):

1. Take each runtime class/trigger pair from the frozen candidate list. Make the trigger appear **only on a continuation line belonging to that class** and require detection.
2. Put an unrelated recognized class entry immediately after the wrapped entry; place a trigger only in the second entry's text and require that it not be attributed to the first class.
3. For the `RECORD-MISSING`/`EISDIR` negative control, confirm the actual directory-record invocation reports `RECORD-MALFORMED` (runtime path above); reject any mapping that credits `EISDIR` to `RECORD-MISSING` merely because the joined text contains that token.
4. Run the same synthetic bytes through the frozen r39 `docstring_classes` behavior and record that the wrapped-only trigger is missed. Preserve exact source bytes and analyzer outputs for both candidate and control.

This distinguishes “joined text contains a token” from “the right class entry describes the trigger the runtime actually emits.” It does not imply the candidate fails; without the candidate analyzer and candidate receipt, the preregistered comparison cannot be executed from the evidence available here.

## Commands and execution record

Commands actually run:

- `mkdir -p /fast/scratch/hyaku/souji-r40/R40executor38 && printf 'scratch=%s\\n' /fast/scratch/hyaku/souji-r40/R40executor38` — output: `scratch=/fast/scratch/hyaku/souji-r40/R40executor38`.
- Read-only file reads through the repository read tool: `census/round-40/preregistration.txt`; `census/round-39/c2-counter.py:105-160,215-250`; `tools/souji-worktree-drift.py:1-93,115-145`; `.ufo/waves/round-39/w1/W1ExecC2Docstring.md:1-100,160-220`; `.ufo/waves/round-39/w1/W1RevC2Doc.md:1-140`.

No analyzer, fixture, counter, git/jj command, build, test, or lint was run. No installs. Scratch directory removed before handoff.
