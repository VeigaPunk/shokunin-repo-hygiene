# S44mutationtester51 — C2 adversarial audit/counter discrimination probe (r44)

Axis probed: **operability** (C2 counter + repaired hidden audit). Frozen rev
`d314fd6e85d62565344fa6c4b102f52f62297884`; lane HEAD verified equal to it.
Instrument pins verified: `c2-counter.py` sha256 `0cb6ce80a2…525252` (matches
preregistration); `c2-hidden-audit.py` sha256 `50872b0d…5e843e`.

Method: cloned the lane to seat scratch
(`/fast/scratch/hyaku/souji-r44/S44mutationtester51/lane`), committed one
single-defect mutant per rev, ran the pristine bounded detector
(`python3 -B census/round-44/c2-counter.py --root <root> --rev <full40>
--scratch <dir>`, ~18–33 s each), and restored the clone to base after each
run (`sha256 50872b0d…` re-verified). The lane worktree was never modified
(final `git status` identical to session start). Detector script location does
not matter: it reads `--root` worktree only for the r43 retention counter;
every audited artifact is blob-bound at `--rev`.

## Runs (verbatim outputs)

**Baseline — pristine counter over frozen rev** → `EXIT=0`:

```
SUMMARY tool=present population=ok retention=ok hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok selftest=ok tmpdir=ok
```

**Mutant A** (`c8d9c5b6…`, audit verdict line 162 → `ok = True`) →
`EXIT=0`, identical target line → **SURVIVED**.

**Mutant A2** (`2c933990…`, also h10 `ok = p is not None`) → `EXIT=1`
→ **KILLED**:

```
SUMMARY tool=present population=ok retention=ok hidden_v2=10/10 clean_stub=ACCEPTED findings_stub=ACCEPTED controls_ran=ok selftest=ok tmpdir=ok
```

**Mutant B2** (`1d089f47…`, pure always-10/10 memorizer audit, 1595 B) →
`EXIT=1` → **KILLED**:

```
SUMMARY tool=present population=RED retention=ok hidden_v2=10/10 clean_stub=ACCEPTED findings_stub=ACCEPTED controls_ran=ok selftest=ok tmpdir=ok
```

**Mutant B3** (`c437a10b…`, branching memorizer audit, 2123 B — prints 10/10
iff `--tool` file > 2000 B, else 0/10; table embedded once as comments) →
`EXIT=0`, identical target line → **SURVIVED**.

**Mutant C** (`0798ff0f…`, h6 expectation drops `C0:FROZEN-EDITED`,
reproducing the r43 mis-expectation) → `EXIT=1` → **KILLED**:

```
SUMMARY tool=present population=ok retention=ok hidden_v2=RED clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok selftest=ok tmpdir=ok
```

**Mutant D** (counter mutant in scratch copy `c2-counter-mutD.py`:
stub verdict `ok = v is not None and v[1] > 0 and v[0] < v[2]` →
`ok = v is not None`) → over frozen rev `EXIT=0` (unchanged honest verdict);
over mutant-A2 rev `EXIT=0` with `clean_stub=REJECTED findings_stub=REJECTED`
where the pristine counter emitted `ACCEPTED`/`EXIT=1` →
**surrogate kill confirmed**: the stub-verdict predicate is load-bearing.

## Discrimination map (what each leg actually proves)

- `hidden_v2` discriminates **expectation regressions** (mutant C) but not
  degenerate/lenient audits: a lenient audit scores 10/10 on the honest tool.
- `clean_stub`/`findings_stub` legs discriminate degenerate audits — but only
  via the **h10 refusal check** alone (mutant A survived on h10's rc/stderr
  gate; mutant A2, h10-lenient, was killed as `ACCEPTED`).
- `population` is a **source-text grep**, not an evaluator: it checks each TSV
  `id`/`want_exit` appears literally in the audit source and counts exactly 10
  `("h\d+-…", ` tuples. It never verifies `want_classes` — mutant C regressed
  the h6 class list and `population` stayed `ok`. An 11th `("h…", ` token in
  an honest audit would falsely RED it (mutant B2's `IDS` tuple did exactly
  this).
- Nothing binds the audit blob's hash or verifies that fixture builds actually
  ran: **any file that emits `scenario-<id>=PASS` ×10 and
  `SUMMARY scenarios=10 pass=10 fail=0` with exit 0 is accepted** — mutant B3
  never invoked the tool at all and passed every leg, including both stub
  rejections, by branching on `--tool` file size (real blob = 20506 B, stubs
  ≈70–120 B).

All kills were clean field-level detections, not crashes or could-not-evaluate
(exit 2 never occurred).

## Findings

1. **Output-shaped trust (high):** the counter trusts the audit's stdout
   wholesale; a ~2 KB memorizer defeats the full C2 gate (B3, exit 0). The
   counter pins its own hash in preregistration but does not check the
   audited files' hashes — a defective or fake audit under a valid rev passes.
2. **h10 monoculture (medium):** against lenient audits, discrimination
   collapses to exactly one check — h10's `rc==2 and "REFUSAL" in stderr`.
   A two-line audit edit (A2) defeats all other pass/fail discrimination.
3. **Population leg under-checks (medium):** `want_classes` column is ignored;
   expectation regressions in class lists are invisible to it (mutant C:
   `population=ok` while `hidden_v2=RED`).
4. **Population leg fragile (low):** exactly-10 count on `("h\d+-…", ` makes a
   legitimate audit source an accidental RED if it ever holds an 11th matching
   literal (B2, `population=RED` for this reason alone).
5. Counter self-protection: the stub-verdict predicate
   (`fail>0 and pass<total`) is the only discriminator against degenerate
   audits; relaxing it to parse-only (mutant D) re-accepts a lenient audit.

## Limitations

- Probes cover the audit↔counter contract only; no c1/c3 legs, no
  whole-suite validation run (out of scope).
- Survived ≠ broken contract: A/A2-type leniency is a coverage finding about
  where discrimination lives, not license to change expectations.
- Mutant commits used fixture author identity `s44@x.invalid` in scratch
  clone only; no lane or fleet objects touched.

## Receipts

`receipts/` under `.ufo/waves/round-44/w1/S44mutationtester51/`:
mutant audit blobs `audit-<rev>.py` (sha256: A `d10ae147…`, A2 `f10edffa…`,
B2 `26b89041…`, B3 `4dea9823…`, C `8dab96b2…`), `c2-counter-mutD.py`
(`6455ca41…`), `runs.txt` transcript. Scratch deleted before yield.

Tools: none installed (pacman paused per directive; `python3 3.14.8`,
`git 2.56.0` pre-existing). No network used.
