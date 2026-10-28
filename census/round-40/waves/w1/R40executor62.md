# R40executor62 — C2 wrapped-docstring decoder attack

- Seat: executor (leaf; no dispatch)
- Scope: distinct item 62, **decoder edge case: continuation ownership/attachment when wrapped prose itself begins with a class-like trigger token**.
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Frozen contract read first: `census/round-40/preregistration.txt:8`.
- Claim under attack: r40 L4 analyzer joins wrapped continuation lines into one class entry and verifies observed class/trigger pairs; synthetic wrapped-trigger detected where r39 one-line analyzer misses it.
- Tool installs/upgrades: none; pacman untouched.

## Evidence and commands

Commands/tool reads actually used:

```text
read /home/vgpnk/.omp/agent/RULES.md
read skill://godspeed
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
read /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-39-verifier-spotcheck.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/waves/w1/W1ExecC2Docstring.md
```

Also listed `census/round-39` and searched the lane for `docstring_classes|class.*trigger|trigger`. No candidate r40 counter or source was found in the lane paths returned; I did not execute counters or create a fixture.

Exact committed evidence pointers:

1. Frozen discriminator: `census/round-40/preregistration.txt:8` requires wrapped continuation analysis and says synthetic wrapped-trigger must be detected while the r39 one-line analyzer misses it.
2. The r39 audit `census/round-39/waves/w1/W1ExecC2Docstring.md:20-45` identifies the extraction scheme: module docstring from `ast.get_docstring(..., clean=False)`, selecting lines with `line.lstrip().startswith(TOKENS)`. The scheme retains raw indentation; the report states continuation content was not part of the extracted class map.
3. That audit's `:47-83` records the base class map and specifically shows the wrapped continuation at `:71-76`: `RECORD-MALFORMED ...` continues on the next indented line with “or disagrees with the TOTAL row”; the base first-line extraction omits it. The audit's `:84-115` records the corrected one-line head mapping, with the class description spread over later lines, but not a r40 wrapped analyzer.
4. Runtime comparison evidence is at `:116-163`; it maps missing paths to `RECORD-MALFORMED`, EACCES/ELOOP to `RECORD-MISSING`, and non-regular records to `RECORD-MALFORMED`. The observed r39 C2 discriminator is detailed at `:165-188`; it tests class-to-trigger words on class lines, not continuation-token attachment.
5. `corpus/lessons/round-39-verifier-spotcheck.md:57-70` independently reports the r39 C2 docstring/runtime comparison and its `new_maps=True old_maps=False` result. It does not establish r40 continuation-boundary behavior.

## Distinct failure mode and bounded measurement plan

A parser that appends every non-class line to the preceding class until the next class can incorrectly assign a subsequent wrapped class's trigger when a continuation line is itself class-looking (or can bleed trailing prose into a following entry if indentation is mishandled). Conversely, a parser that starts a new entry on any continuation line beginning with a known token may split valid wrapped prose. This is a distinct attachment/segmentation edge from merely proving that a normal wrapped trigger is joined. No observed r40 source or output establishes how it resolves this boundary; this is a **bounded measurement plan**, not an observed defect.

At an explicitly named candidate revision, construct only an isolated in-memory/scratch synthetic module docstring with two observed classes: first class description continued over lines; second class entry beginning at the next class line. Put the second trigger token at the start of the first class's indented continuation prose in one variant, and put the same token on the second class's own wrapped continuation in another. Run the r40 analyzer and the r39 analyzer on identical bytes. Capture parsed class-to-trigger pairs. Acceptance for this edge: first variant must not manufacture a pair for the first class from text belonging to the next class (if the grammar cannot distinguish it, report ambiguity); second variant must attach the trigger to its owning class. Separately retain the preregistered ordinary wrapped-trigger probe to ensure this boundary probe does not mask the intended positive case. No git/jj/index mutation is needed.

## Verdict

**C2 operability: NOT MEASURED by this attack; no concrete falsifier observed.** The committed r39 evidence confirms the old one-line extraction's known limitation and the r40 frozen target, but does not show candidate r40 bytes or test continuation-to-class attachment boundaries. The potential boundary ambiguity above is a falsifiable, narrow extension of the frozen wrapped-line discriminator, not a claim that r40 fails. This seat did not run any checks; outputs/verdicts for candidate behavior are unrun, not pass.

## Scope and limits

- Read-only evidence review; only this report is written.
- No scratch files, fixture, tool install, counter execution, build, lint, test, or formatter run.
- Exact commands/results for source reads are recorded above; no shell commands were run.
- Risk: without the candidate source and a defined continuation grammar, parser behavior cannot be inferred from r39's audit. No production or frozen claim changes recommended on this evidence alone.
