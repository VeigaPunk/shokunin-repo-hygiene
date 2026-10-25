# CritQ54Gate — Q54 applicability vs the C2 Gate locators (round 26, w1)

STATUS: PARTIAL — Q54's applicability holds on the staged entry bytes
(`entries=2 locators=2 locators_bad=0`), but the instrument the prereg binds for C2's
Gate (K2, `tools/souji-gate-check.py`) cannot resolve any locator, no frozen C2 counter or
receipt runs Q54, and at HEAD both admitted entries carry no `## Gate` at all (K2 rc=1) while
Q54 reports `UNSCOPED` and exits 0.

## Evidence

Revision: lane HEAD `ea0bbe66c974062984134bb5b491b21bbb3c17d7`; base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`.
Staged bytes are moving under siblings; all staged results below are pinned to:
`entry-git-auto-maintenance-trigger-set.md` sha256 `53144e1d237c4dac09f47a1db041342af15598831655d3347fa2f0a922ca7014` (122 lines),
`entry-git-auto-maintenance-trigger-set-r23.md` sha256 `449eccab4ba37e792da386837c1c0841c374741bca2b55326307f36786d7f865` (111 lines).

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries .ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md \
             .ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set-r23.md \
    --snapshot-dir census/round-26/sources --slice .../empty-slice --slice-verdicts .../empty-verdicts
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0          gate_rc=0

$ python3 -B tests/fixtures/r23-locator-heading.py --entries <same two> --snapshot-dir census/round-26/sources
entries=2 locators=2 locators_bad=0                            q54_rc=0

$ python3 -B tests/fixtures/r23-locator-heading.py --selftest --snapshot-dir census/round-22/attempt2/sources
case=control locators=11 locators_bad=0 expect=0
case=mutant(real r22 defect: § OPTIONS on man7-mv.1.txt, which has no OPTIONS heading) locators_bad=1 expect>=1
selftest=2/2                                                   selftest_rc=0
```

Snapshot grounding: `census/round-26/sources/git-fetch.1.txt:2995` is
`<h2 id="_options"><a class="anchor" href="#_options"></a>OPTIONS</h2>`; the quoted default
sentence sits at `3195-3197` (`This is enabled by default.</p>` at 3197). Entry A's body line 39
claims `(lines 3199-3202)`, which is the `--write-commit-graph` block.

At HEAD (blob check, not worktree): `git show HEAD:corpus/knowledge/git-auto-maintenance-trigger-set.md`
and `...-r23.md` each contain **0** `^## Gate` lines (67 and 92 lines); `git grep -l '^ground: F1' HEAD
-- corpus/knowledge/ | wc -l` = 2. Running K2's exact command shape on those paths:

```
FAIL corpus/knowledge/git-auto-maintenance-trigger-set.md check1-no-gate: ...
FAIL corpus/knowledge/git-auto-maintenance-trigger-set-r23.md check1-no-gate: ...
entries=2 ok=0 ... fail=2                                      gate_rc=1
UNSCOPED corpus/knowledge/git-auto-maintenance-trigger-set.md  Gate names no snapshot (predates Q54)
UNSCOPED corpus/knowledge/git-auto-maintenance-trigger-set-r23.md  Gate names no snapshot (predates Q54)
entries=2 locators=0 locators_bad=0                            q54_rc=0
```

`census/round-26/records/` at HEAD holds c1-before/after, c2-before/after, c2-k4-base,
c3-before/after/control, empty-slice, empty-verdicts — no `c2-gate.tsv`, no `c2-k4-after.tsv`,
and `grep -rl locator census/round-26/records/` is empty.

## Findings

1. **The gate never resolves a locator — it only requires one to be present.**
   `tools/souji-gate-check.py:42` defines `LOCATOR_RE` (a presence alternation); `:85` drops
   quote-less rows, `:88` is `if not LOCATOR_RE.search(locator_probe):`, and the only content
   test is `:111` `if squash(q) not in body:`. The probe at `:87` strips quoted spans and the
   `snapshot:` token, then asks only whether some locator-ish token remains. There is no
   heading set, no `§`-to-snapshot mapping and no line arithmetic anywhere in the file (last
   touched round 22, `9fcc4f7`).
2. **Exact locator strings each instrument will try to resolve.**
   - Entry A, gate-check: it resolves *nothing*. Per quoted Gate row it only demands a token
     hit: line 116 (`§`, `lines `), 117 (`line `), 118 (`line `), 119 (`line `), 120 (`line `),
     121 (`line `); REJECT at 122 has no quotes and is skipped by the quote loop.
   - Entry A, Q54 (`r23-locator-heading.py:30`): exactly one token, `OPTIONS` from entry line
     116 (`§ OPTIONS --auto-maintenance`), matched against the union heading set of the five
     `snapshot:` paths the Gate names; it matches `options` at `git-fetch.1.txt:2995`.
   - Entry B, gate-check: one quoted row (line 108) → probe hit `§ OPTIONS`; rows 109 and 110
     are skipped wholesale at `:85` because they carry no quotes.
   - Entry B, Q54: exactly one token, `OPTIONS` from entry line 108, matched against
     `git-fetch.1.txt` (the only `snapshot:` in that Gate).
3. **C2's kill rule names Q54 but nothing implements it.** The frozen clause is
   "any admitted entry's Gate locator failing Q54 (every snapshot § locator resolves to a
   heading line)". K1 runs `c2-counter.sh` (which prints only `grounded_f1` and
   `registry_rows`), K2 runs the gate, K3 runs `sources-census.sh validate`, K4 runs
   `souji-coverage-agreement.py`; the receipt list names `c2-before`, `c2-k4-base`, `c2-after`,
   `c2-k4-after`, `c2-gate`. Amendment 1 (K4 base literal) and amendment 2 (C1 protected spans)
   do not add a Q54 arm. So a Q54 failure is unobservable in every receipt the claim binds.
   Q54's own rule text is `corpus/QUALITY.md:128`: "A `corpus/knowledge/` Gate that declares
   `snapshot:` paths must have every `§ <NAME>` locator resolve to a heading-like line in one of
   those snapshots."
4. **Front-matter and body `§` locators are outside both scans.** `gate_section`
   (`tools/souji-gate-check.py:55`) slices from `\n## Gate`; `gate_block`
   (`tests/fixtures/r23-locator-heading.py:34`) slices from `## Gate`. Entry A's front-matter
   locator is line 1 (the one carrying the `heading line 2995` claim) plus body line 35; entry B
   has front matter line 4 and body line 33 (`PROVINCE.md § Owns`, not a snapshot at all).
   Mutating only those front-matter locators to `§ NOSUCHHEADING` leaves both instruments green
   (gate rc=0, Q54 rc=0 `locators_bad=0`).
5. **Line numbers and ranges are decorative in both instruments.** Entry A line 39 asserts the
   quoted default sentence is at `(lines 3199-3202)`; the snapshot has it at 3195-3197, and
   3199-3202 is the next option's block (verified above). Mutating a Gate row's
   `(snapshot lines 3190-3202)` to `(snapshot lines 1-9)` leaves gate rc=0 and Q54 rc=0. The
   Gate's own `(snapshot lines 3190-3202)` is also wide by four lines (the auto-maintenance
   option entry ends at 3198).
6. **Q54's heading set is a union over every snapshot the Gate names, not row-scoped.**
   `r23-locator-heading.py:109` `heads |= headings(text)` then `:115`
   `if not head or not any(head.lower() in h for h in heads):`. Rewriting entry A's row 2 to
   `"int enable_auto_gc = 1;" — § OPTIONS builtin/fetch.c line 2528 — ... snapshot:
   census/round-26/sources/git-builtin-fetch.c` yields gate rc=0 **and** Q54 rc=0
   `locators_bad=0`, although `git-builtin-fetch.c` has no `options` heading (its extracted
   heading set is 15 tokens, none `options`) — the man page named by row 1 supplies it.
7. **The heading detector admits ordinary C code in `.c` snapshots.** `SHORT_CAPS`
   (`r23-locator-heading.py:64`) matches short all-caps code lines, so `headings()`
   yields 15 "headings" for `git-builtin-fetch.c` including `bug_on_opt_neg(unset);`. A Gate row
   `§ BUG_ON_OPT_NEG` with `snapshot: .../git-builtin-fetch.c` passes Q54 (rc=0), i.e. the
   locator resolves to a code identifier, not a heading.
8. **LIVE tip defect: the admitted entries have no Gate, and Q54 calls that out of scope.**
   `r23-locator-heading.py:103-105` prints `UNSCOPED ... (predates Q54)` and `continue`s when
   the Gate names no snapshot, and a missing `## Gate` produces the same path with rc=0. So the
   current HEAD state (both entries 0 `## Gate` lines, K2 rc=1 `check1-no-gate`) is a Q54 pass.
   The staged w1 candidates do carry the Gate (A `## Gate` at 111, B at 102) and pass Q54; the
   landed blobs do not.

Impacted axes: **coverage** (C2's kill rule has an unbound clause; K2 green is not Q54 evidence),
**calibration** (a frozen kill rule with no counter is a self-assessment gap), **operability**
(the gate's stated contract exceeds what it checks). No axis is harmed by fixing any of the above.

## Attack log

- **A1 — K2 is blind to locator resolution.** Counterexample: identical staged bytes with only
  `§ OPTIONS` → `§ NOSUCHHEADING` produce `entries=2 ok=2 fail=0` rc=0 from the gate and
  `locators_bad=2` rc=1 from Q54. Evidence: commands above; `tools/souji-gate-check.py:42,85-89,111`.
  Axes: coverage, operability. Smallest safe correction: file the Q54 fixture as a receipted C2
  arm at the landing commit (the kill rule already names it; stricter-only, L1 decides), so
  `c2-q54.tsv` exists next to `c2-gate.tsv`.
- **A2 — A missing Gate is a Q54 pass.** Counterexample: the two HEAD blobs (0 `## Gate`) →
  `UNSCOPED ... predates Q54`, rc=0. Evidence: HEAD blob grep and Q54 run above;
  `r23-locator-heading.py:103-105`. Axes: coverage, calibration. Smallest correction: run Q54 on
  the landed paths and refuse `UNSCOPED` for entries whose front matter declares `ground:` and
  `source:` but has no Gate.
- **A3 — Front-matter locators are unchecked.** Counterexample: front-matter-only
  `§ NOSUCHHEADING` mutations → gate rc=0, Q54 rc=0. Evidence: entry A line 1, entry B line 4,
  body 35/33; slice functions at gate-check `:55` and fixture `:34`. Axes: coverage.
  Smallest correction: do not let the front-matter source line be the only place a `§` claim
  lives; keep the Gate row's `§` as the load-bearing locator (it already is for both entries).
- **A4 — Wrong line range ships green.** Counterexample: entry A line 39 `(lines 3199-3202)`
  vs actual 3195-3197; and a mutated Gate row `snapshot lines 1-9` passes both tools.
  Axes: calibration. Smallest correction: correct entry A line 39 to `(lines 3195-3197)` and
  tighten Gate row 116 to `(snapshot lines 3190-3198)`, before landing.
- **A5 — Cross-snapshot resolution false negative.** Counterexample: `§ OPTIONS` on a row whose
  snapshot is `git-builtin-fetch.c` passes Q54 only because another snapshot in the same Gate
  (the man page) has `OPTIONS`. Evidence: `r23-locator-heading.py:109,115`; heading-set probe
  (15 headings, no `options`). Axes: coverage. Smallest correction: scope the heading set to the
  row's own `snapshot:` when the row names one (hardening; not needed for the two admitted rows,
  which name the man page).
- **A6 — Code identifiers count as headings.** Counterexample: `§ BUG_ON_OPT_NEG` on
  `git-builtin-fetch.c` → Q54 rc=0. Evidence: `r23-locator-heading.py:64,79-87`. Axes: coverage.
  Smallest correction: restrict `SHORT_CAPS` to lines that are not statements (e.g. reject
  strings containing `;` `(` `)` or `_`), or allow `.c` snapshots to contribute no headings.

Scratch used: `/var/tmp/souji-r26-CritQ54Gate/` (removed). No lane file, index, registry or
campaign byte was written; every tool above is read-only.
