# AttackReadSeverityExit — C1 calibration attack (round 21 wave 2)

Seat: critic/revenger, leaf, read-only (no code executed; no tools installed — none needed).
Target: pinned integrated build `522dcd768ca90afe166532d37d306d3df70aeea5`, files
`tools/souji-seat-audit.py` (`implicit_root_read`, `audit_seat`) and `tests/fixtures/r21-read-root.py`,
against the frozen contract `.ufo/waves/round-21/preregistration.txt` (C1) and
`.ufo/waves/round-21/clarification-before-measurement.txt`.
Method: static line-level analysis only. Commands actually run (read-only):
`git show 522dcd7…:tools/souji-seat-audit.py`, `git show 522dcd7…:tests/fixtures/r21-read-root.py`,
`git show 6ff3413…:tools/souji-seat-audit.py`, `git diff 6ff3413…..522dcd7… -- tools/souji-seat-audit.py`.
No selftest, no census, no fixture run (fixture execution is executor business; this seat does not execute code).

The r21 C1 delta is exactly: two docstring blocks, `implicit_root_read` (new), and its call site
(`flag("V-READ-ROOT", "minor", target)`). Every other class, regex, and the exit path are byte-identical
to baseline `6ff3413bba9c8430c3b0bc4d2052e21d0407183f` (diff observed; baseline contains no
`implicit_root_read`/`V-READ-ROOT` at all — grep of `git show 6ff3413…` returned no match).

## Findings by severity

### F2 — FALSE POSITIVE (minor class): historical-renderer grep splits on the LAST `" in "`, so a path containing `" in "` flags a phantom outside-lane target

`implicit_root_read`, pinned rev lines 382–384:

```python
        elif " in " in args:
            # Historical renderer: grep(PATTERN in PATH).
            target = args.rsplit(" in ", 1)[1]
```

`rsplit(" in ", 1)` takes the **last** occurrence. For a rendered call whose PATH itself contains
`" in "` (historical renderer form, which the clarification binds to the same explicit-path rule as
`" @ "`), the "path" becomes the trailing words after the last `" in "`, judged as a fresh relative target.

Counterexample (synthetic transcript line, real renderer shape):

```
→ grep(CloseSouji20 in souji-shokunin/corpus/in depth notes.md) ⇒ ok
```

True target `souji-shokunin/corpus/in depth notes.md` resolves **inside** the lane → per the frozen rule
("NOT flagged when it resolves inside the lane (e.g. \"souji-shokunin/x\")") this must be NOT flagged.
Implementation: `target = "depth notes.md"` → strip → not `/`/`~`/URI → `os.path.normpath(fleet + "/depth notes.md")`
= outside `lane_root` → line 400–401 returns it → `flag("V-READ-ROOT", "minor", "depth notes.md")`. False positive.

Bounded caveat: the rendered text is genuinely ambiguous for this shape; `rsplit` is the correct choice
whenever the path is `" in "`-free or absolute (it also keeps the clarification's own requirement — the
existing selftest case `grep(foo in {lane})` must not acquire a spurious flag — satisfied; verified: absolute
target skips at line 395). The FP is confined to inside-lane relative/spaced paths containing `" in "`.

Fixture detection: **NO**. The only historical-renderer case is `('historical-renderer', 'grep', 'pattern in ' + LANE, False)`
(fixture line 58) — an `" in "`-free absolute path; the mis-split branch is never exercised.

Second-order risk for the measurement itself: C1 requires the after set to EQUAL the human oracle
"precision and recall both exact". The rule text ("treated as an explicit path just like ' @ '") does not
say which `" in "` wins, so a labelling seat and the implementation can legitimately split differently on any
corpus line whose path contains `" in "` (1347 calls in the 128-file universe; corpus seats own that check).
This is a latent oracle-disagreement vector, not just a code nit.

### F1 — FALSE NEGATIVE (bounded, contract-compliant): a relative read/grep/glob resolving AT the lane root is invisible to every class

`implicit_root_read` line 400: `if resolved != lane_root and not resolved.startswith(lane_root + "/"):`
— equality with the lane root is treated as inside → no V-READ-ROOT. The adjacent V-RECURSIVE check
(`audit_seat` lines 459–461) fires only when args **end with the absolute** lane/fleet spelling:

```python
            a = args.rstrip("…").rstrip()
            if a.endswith(lane) or a.endswith(fleet) or a.endswith(lane + "/") or a.endswith(fleet + "/"):
                flag("V-RECURSIVE", "minor")
```

So on these exact inputs:

- `→ read(souji-shokunin) ⇒ ok` — no flag at all (resolved == lane_root; args do not end with the absolute lane).
- `→ grep(pattern in souji-shokunin) ⇒ ok` — no flag (same, via the `" in "` branch).
- `→ glob(souji-shokunin/**) ⇒ ok` — no flag (`startswith(lane_root + "/")` holds → "inside").

The absolute twins `read({LANE})`, `glob({LANE})` are V-RECURSIVE minor (selftest cases
`recursive-read-lane-root`, `recursive-glob-tool`). Identical semantics, asymmetric verdict, depending only
on spelling. The pinned V-RECURSIVE definition ("a read/grep/glob call rooted at the lane root or the fleet
root", docstring lines 32–33) covers the relative form, but that gap predates r21 and the C1 harm guard
("per-class counts identical except the new class") forbids extending V-RECURSIVE this round. The new class's
letter ("FLAG when its normalized resolution is not inside the lane") legitimately excludes it if "inside" is
read inclusively — which is the reading the implementation took. Reportable because the frozen text never
resolves inclusive-vs-strict for the lane-root-equality case; if oracle labellers read it strictly, the
after-set/oracle equality claim breaks on this shape. L1 should pin that reading before measurement.

Fixture detection: **NO** — every lane-relative negative case is strictly inside
(`souji-shokunin/tools/x.py`, `souji-shokunin/x/../tools/*.py`); no lane-root-equality case exists.

### F5 — BOUNDED PROOF: audit exit is unchanged when a relative read is the only violation (the C1 exit boundary holds)

Chain, pinned rev:

1. Line 458 (only emitter): `flag("V-READ-ROOT", "minor", target)` — severity hardcoded `"minor"`.
2. Lines 511–514: `summary.major` counts only `v["severity"] == "major"`.
3. Line 797: `return 1 if sm["major"] else 0` — exit 1 requires a major.

No other class can fire on a plain relative read outside the lane: `SURFACE_RE` (line 423) needs
sweep/`.ufo/state`/watchdog/omp text in args; the V-RECURSIVE endswith check (above) needs the absolute
spelling. A transcript whose sole flagged line is `→ read(corpus/x.md) ⇒ ok` yields exactly one minor
V-READ-ROOT → `major=0` → exit 0; the same transcript at baseline yields no rows → exit 0. Exit unchanged. ✓

Caveat (base-identical, not a C1 regression): a relative read whose text contains
`census/operator-sweep-<digits>` (e.g. `→ read(census/operator-sweep-20261019/x) ⇒ ok`) trips V-SURFACE
**major** → exit 1, plus V-READ-ROOT minor. `SURFACE_RE` is byte-identical at both revs (observed diff), so
this is pre-existing V-SURFACE behavior the harm guard explicitly preserves ("existing V-RECURSIVE /
V-SURFACE untouched"), not an exit-semantics change. The fixture pins only the absolute variant
(`forbidden-control`, expected False, preserved V-SURFACE); the relative co-flag shape is unfixtured — a gap,
not a defect.

The fixture's `all(r['severity'] == 'minor' for r in now if r['class'] == 'V-READ-ROOT')` (fixture line 70)
transitively pins the exit boundary: any future major-severity V-READ-ROOT fails the fixture. ✓

### F3 — FIXTURE ROBUSTNESS (minor): `base_discriminating` is reported, not enforced

Fixture lines 71–75: `discriminating += old_actual != expected` only feeds the printed
`SUMMARY … base_discriminating=N`; `failed += not ok` never counts it, and the exit code is
`int(bool(failed))`. A degenerate run (`--base-tool` accidentally the same file as `--tool`) would print
`pass=33 fail=0 base_discriminating=0` and **exit 0**, satisfying neither the prereg's "every positive case
base-discriminating" check nor any automated gate. Practical risk is low against the real baseline: every
positive case has `expected=True` and the 6ff3413 auditor cannot emit V-READ-ROOT at all (class absent,
verified), so all 14 positives are necessarily discriminating in a correctly wired run. Still, the fixture
alone cannot certify its own baseline wiring; only the SUMMARY line exposes a mis-wire.

### F4 — OBSERVATION (no verdict impact, proven): read-selector strip regex omits `+`; provably verdict-insensitive

Line 394: the class `[-\d,+hms]+` accepts `:N`, `:N-M`, `:,`-lists, `:raw`, `:img`, `:conflicts`,
`:1h5m42s`, `:01:23` but not the real harness form `:50+150` (`+` not in class) — the selector tail survives
into the judged component. This can never flip a verdict: the strip only removes a suffix containing no `/`,
and path resolution is prefix-monotone — if the stripped path resolves inside the lane, the unstripped path
(a lane-inside directory plus a colon-bearing final filename component) also resolves inside, and vice versa
the only strip-induced flip is outside-with-suffix → lane-root-exact, which is exactly the contract's own
"selector removed first" semantics. Effect limited to the reported `target` text. The frozen contract's
selector list (":N", ":N-M", ":raw", comma lists) omits `:N+M` too, so the implementation is compliant;
noted for L1 in case the corpus contains `+`-selectors whose oracle targets are compared verbatim.

## Residual risk and verification gaps

- The `" in "` FP (F2) and lane-root-equality FN (F1) are proven at function level on synthetic lines; whether
  the 128 committed transcripts (1347 calls) contain matching shapes was **not** measured — corpus seats own
  the census, and this seat must not run it. If zero corpus matches, both remain latent-only.
- The oracle labelling reading of "inside the lane" for the lane-root-equality case (F1) is unpinned in the
  frozen text; one ambiguous clause can decide precision on that shape.
- Selftest pass=118 fail=0, r19 17/0, r20 78/78/0 harm guards are claimed but were **not** run (execution
  forbidden for this seat); static inspection shows the C1 diff adds one flag call in a branch that cannot
  produce any pre-existing class on non-read/grep/glob lines, and the call site precedes the untouched
  V-RECURSIVE endswith block, so per-class counts except the new class should be unchanged — structural
  argument, not an observed run.
- `count-read-root.py`, `read-root-oracle.tsv` and the corpus measurement are out of this seat's scope.

## Verdict (author-side advisory, non-closure)

No major finding. One concrete minor false positive (F2), one bounded contract-compliant false negative with
an unpinned contract reading (F1), one fixture-enforcement gap (F3), and a bounded proof that the C1 exit
boundary holds (F5). F2 and the F1 reading should be resolved — or their absence in the corpus demonstrated —
before the after-set/oracle equality claim is treated as exact.

Report: .ufo/waves/round-21/w2/AttackReadSeverityExit.md
