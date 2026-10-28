# W1ScribeMistake — one mined mistake for `corpus/lessons/round-39.md` `## Mistakes` (round 39, wave 1)

seat: `W1ScribeMistake`, role scribe, axis **calibration 7**.
lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (base `ed30b7f5b77939c9073348d810730bc4f355708d`,
HEAD at measurement `d4c17557b92fd98044e4c8f0ddc79c6d75701b15`).
contract read first: `census/round-39/preregistration.txt` (freeze
`b769bfb84a264d8b284c09bc211d99f39a3e9126`), C2 + amendment A1.
scratch: `/fast/scratch/hyaku/souji-r39/W1ScribeMistake` — created, used, **removed** (§7).
tooling: nothing installed or upgraded; `python3` 3.14.8 and `git` 2.56.0-1 were sufficient.
writes: this report only. The lane lesson `corpus/lessons/round-39.md` was **not** edited — the entry is
delivered paste-ready in §6 because the L1 is the sole integrator of that file. `git status --porcelain`
at the end of this seat showed tracked edits to `LOG.md`, `SKILL.md` and `corpus/QUALITY.md` by other
wave-1 seats, plus untracked receipts; none of them is this seat's.

**Verdict up front: candidate (a) chosen.** It reproduces from committed bytes and its fix is
demonstrated able to fail (§4, R4/R5/R6). Candidate (b) was rejected as material: no lane artifact
carries the `31/32` it names (§3).

---

## 1. Contract read

```
$ cat /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/preregistration.txt
```
quoted lines that bound this seat:

```
### C2 — operability (axis score 8)
... L1 unresolvable `--rev` (base: rc 1 with findings; new: rc 2, `REFUSAL REV-UNRESOLVED`), L2 `--rev`
naming a blob (same classes), L3 `--register-rev` unresolvable stays rc 2 (harm), ...
CONTROL (committed before any after-data): `census/round-39/records/c2-before.txt`.
### Amendment A1 — r39-citation-rev case class (2026-10-28, tighter-only, before any claim measurement)
... The repaired tool resolves `--register-rev` before it reads the register, so an unresolvable
`--register-rev` now refuses with `REFUSAL REV-UNRESOLVED` (exit 2).
```
Verdict: **contract read.** A1 is what makes the mask of §4 *silent* on the repaired bytes: the
register-arm refusal and the rev-arm refusal now carry the same class token.

## 2. The counter's shape, as committed

```
$ sed -n '104,112p' census/round-39/c2-counter.py
def run_citation(tool, root, rev, scratch, register_rev="0" * 40):
    return subprocess.run(
        ["python3", "-B", tool, "--root", root, "--rev", rev,
         "--register", "census/round-38/cells.tsv", "--register-rev", register_rev],
...
$ sed -n '185,215p' census/round-39/c2-counter.py     # L1/L2 pass register_rev=args.rev/base_rev; L3 passes ZERO
        new_p = run_citation(new_cit, root, ZERO, base_scratch, register_rev=args.rev)
        old_p = run_citation(old_cit, root, ZERO, base_scratch, register_rev=args.base_rev)
        ...
        # L3 — harm leg: an unresolvable --register-rev stays exit 2.
        new_p = run_citation(new_cit, root, args.rev, base_scratch, register_rev=ZERO)
```
Verdict: **read.** Line 108 still carries the `"0" * 40` default — the residue of the first draft, and
the reason L3 works; L1/L2 no longer take it.

## 3. Candidate (b) rejected as material (measured, not assumed)

```
$ grep -rn "31/32\|31 of 32\|31 \|settled after\|after closure" \
    .ufo/waves/round-38/w2/ .ufo/waves/round-38/report-draft.md \
    corpus/lessons/round-38-verifier-spotcheck.md
(no output)
$ grep -rn "\b31\b" .ufo/waves/round-38/report-draft.md .ufo/waves/round-38/w2/*.md corpus/lessons/round-38.md
.ufo/waves/round-38/report-draft.md:237:  check while the writer re-walks the path (`W1SentEnvelope` F2/R2: 31/60 runs wrote inside
.ufo/waves/round-38/w2/W2CritStale.md:159:   `31/60` (`writes_into_measured_tree=31`), eleven docstring variants (11 rows in
.ufo/waves/round-38/w2/W2CritWaves.md:175:... `kind: "spawn"`, `agentId: null` (42/42 and 32/32), and `updatedAt == createdAt`.
```
Verdict: **NOT FOUND.** The only `31` counts in the r38 artifacts are `31/60` write-envelope runs, not
a seat-report tally; the only `32/32` is the wave-2 registry plan size, which never reads `31/32`. A
lesson entry on (b) would have to cite a number no lane byte carries — exactly the `number-drift` class
r38 M4 was written about. (a) is the only candidate whose evidence is re-runnable from committed bytes.

## 4. Candidate (a), measured from committed bytes

### 4.1 Byte extraction (read-only git)

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d4c17557b92fd98044e4c8f0ddc79c6d75701b15:tools/souji-citation-reconcile.py > $S/cit-new.py
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ed30b7f5b77939c9073348d810730bc4f355708d:tools/souji-citation-reconcile.py > $S/cit-old.py
$ sha256sum $S/cit-new.py $S/cit-old.py
59f1e57d7af02cac675757066fb6fa2629a0153f21c98a62e04b6d3b301d2b73  cit-new.py
56866ea8f832332c2f69dcba4ddcd9ba5d7894bf9a2e82715962e2fb19bfcbe8  cit-old.py
```
Verdict: **PASS** — `56866ea8f832` is the `tool_sha=` prefix of the frozen control
`census/round-39/records/c2-before.txt` and `59f1e57d7af0` the prefix of `c2-after.txt`; the probed
bytes are the bytes the round measured.

### 4.2 Paired-flag probes (each run: `--register census/round-38/cells.tsv`, `--root <lane>`)

| # | tool | `--rev` | `--register-rev` | observed | verdict |
|---|---|---|---|---|---|
| A1 | new | `000…` | `d4c1755` (valid) | `rc=2 class=REV-UNRESOLVED` | **rev arm closes** (R11 fixed) |
| A2 | old | `000…` | `ed30b7f` (valid) | `rc=1`, `SUMMARY cells=10 mismatches=20` | **base defect reproduces** |
| B1 | new | `d4c1755` (**valid**) | `000…` | `rc=2 class=REV-UNRESOLVED` | **mask: refusal from the register arm** |
| B2 | old | `ed30b7f` (**valid**) | `000…` | `rc=2 class=REFUSAL USAGE` | **mask at base** |
| B3 | new | `000…` | `000…` | `rc=2 class=REV-UNRESOLVED` | same reading as B1 |
| C1 | new | `d4c1755` | `d4c1755` | `rc=0`, `SUMMARY cells=10 mismatches=0` | control green |

Verdict: **PASS.** B1 is the finding: the repaired tool refuses with the rev-arm class token while
`--rev` is perfectly resolvable, so the token alone cannot say which flag refused.

### 4.3 Leg matrix — the committed pass condition, drafted vs fixed

Driver `$S/leg-matrix.py` (embedded here because the scratch tree is removed) re-implements the
counter's L1 predicate verbatim — `new_ok = rc==2 and "REV-UNRESOLVED" in stderr`, `old_has`
likewise, leg ok = `new_ok and not old_has`:

```python
import subprocess, sys
S, L, NEW, OLD = sys.argv[1:5]; Z = "0" * 40
NEWTOOL, OLDTOOL = S + "/cit-new.py", S + "/cit-old.py"
def run(tool, rev, regrev):
    p = subprocess.run(["python3", "-B", tool, "--root", L, "--rev", rev,
                        "--register", "census/round-38/cells.tsv",
                        "--register-rev", regrev], capture_output=True, text=True)
    return p.returncode, "REV-UNRESOLVED" in p.stderr
def leg(tag, nt, nrev, nreg, ot, orev, oreg):
    nrc, ncls = run(nt, nrev, nreg); orc, ocls = run(ot, orev, oreg)
    ok = (nrc == 2 and ncls) and not (orc == 2 and ocls)
    print("%-52s %s new rc=%d class=%s old rc=%d class=%s"
          % (tag, "PASS" if ok else "FAIL", nrc, ncls, orc, ocls))
print("== as drafted: register_rev left at its '0'*40 default ==")
leg("R1 first control (new=old=base)", OLDTOOL, Z, Z, OLDTOOL, Z, Z)
leg("R2 repaired, --rev RESOLVABLE",   NEWTOOL, NEW, Z, OLDTOOL, OLD, Z)
leg("R3 repaired, --rev unresolvable", NEWTOOL, Z,   Z, OLDTOOL, OLD, Z)
print("== as fixed: register_rev = the arm's own revision ==")
leg("R4 base vs base (--rev 000..)",   OLDTOOL, Z, OLD, OLDTOOL, Z, OLD)
leg("R5 repaired vs base (--rev 000..)", NEWTOOL, Z, NEW, OLDTOOL, Z, OLD)
leg("R6 repaired, --rev RESOLVABLE",   NEWTOOL, NEW, NEW, OLDTOOL, Z, OLD)
```

```
$ python3 -B $S/leg-matrix.py $S /home/vgpnk/Projects/shokunin/souji-shokunin \
    d4c17557b92fd98044e4c8f0ddc79c6d75701b15 ed30b7f5b77939c9073348d810730bc4f355708d
== as drafted: register_rev left at its '0'*40 default ==
R1 first control (new=old=base)                      FAIL new rc=2 class=False old rc=2 class=False
R2 repaired, --rev RESOLVABLE                        PASS new rc=2 class=True old rc=2 class=False
R3 repaired, --rev unresolvable                      PASS new rc=2 class=True old rc=2 class=False
== as fixed: register_rev = the arm's own revision ==
R4 base vs base (--rev 000..)                        FAIL new rc=1 class=False old rc=1 class=False
R5 repaired vs base (--rev 000..)                    PASS new rc=2 class=True old rc=1 class=False
R6 repaired, --rev RESOLVABLE                        FAIL new rc=0 class=False old rc=1 class=False
```

- **R1** reproduces the first control run's reading exactly —
  `new rc=2 class=False old rc=2 class=False`, the tail of the transcript's
  `LEG L1 FAIL new rc=2 class=False old rc=2 class=False` (§4.4); the prefix differs because the
  matrix driver is not the counter, the two refusal readings do not.
- **R2 vs R3**: the drafted leg returns the **same verdict** for a resolvable and an unresolvable
  `--rev`. Its pass is produced by `--register-rev`; the named flag cannot move it. This is the
  "could not fail" the ticket names, stated precisely: not "it always passes" (R1 fails), but "no value
  of the flag it names changes the verdict".
- **R4 vs R5**: the fixed leg fails on the base bytes and passes on the repaired bytes — it
  discriminates.
- **R6**: the fixed leg fails again as soon as `--rev` resolves (`rc=0`), so its pass is not reachable
  by a green run either.

Verdict: **PASS — the fix can fail.**

### 4.4 Primary record of the first control run (transcript, outside the repo)

```
$ grep -o '.\{0,300\}rc=2 class=False.\{0,300\}' \
    /home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-28T14-01-34-216Z_01a182d0-f308-7371-97bc-ca8b0ed0633f/SoujiR39.jsonl
...c2 rc=1
LEG L1 FAIL new rc=2 class=False old rc=2 class=False
LEG L2 FAIL new rc=2 class=False old rc=2 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
...
{"type":"message","id":"e0e3b7c5",...,"timestamp":"2026-10-28T17:43:57.792Z",...
"thinking":"... C2 control issues:
- L1: `new rc=2 class=False` — the base tool already returns rc 2 for `--rev 000...`? Why? Because
`runtime` check: `if not REV.match(args.rev)` passes (40 hex). Then register read with
`--register-rev 000..` → `git_show` returns None → RegisterError → rc 2 BEFORE the rev loop. So the
unresolvable register_rev masks the rev. Right: my run_citation passes `--register-rev` default
\"0\"*40 → rc 2. Need register_rev = a valid revision. Fix: pass register_rev = the base rev (valid)
in L1/L2. ... I overwrote that file though... the run output was in the transcript, not committed"
```
Verdict: **PASS (primary record located).** The L1 diagnosed the mask in the same turn it observed it;
the observation itself was overwritten (`census/round-39/records/c2-before.txt` carries the repaired
reading), which is why §6's evidence pointer cites the re-runnable pair and not the receipt alone.

## 5. The fixed counter, re-run (landing and base)

```
$ mkdir -p $S/ctr-after $S/ctr-before
$ python3 -B census/round-39/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev d4c17557b92fd98044e4c8f0ddc79c6d75701b15 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --scratch $S/ctr-after
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
rc=0
$ python3 -B census/round-39/c2-counter.py --root ... --rev ed30b7f5... --base-rev ed30b7f5... --scratch $S/ctr-before
LEG L1 FAIL new rc=1 class=False old rc=1 class=False
LEG L2 FAIL new rc=1 class=False old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=e555d8281484
rc=1
```

Verdicts:
- **landing run: PASS**, and its `tool_sha=59f1e57d7af0/e48ed08e6728` and every L1-L6 line equal
  `c2-after.txt`; the SUMMARY differs in one field only, `fixture_sha=7ab7c3d85a81` (receipt) vs
  `e555d8281484` (now) — the fixture moved once more after that receipt was written (`d4c1755`).
- **base run: PASS as a control** (`pass=2 fail=4`, matching the frozen control) — but with a
  disclosed difference: the frozen `c2-before.txt` records `fixture_sha=c142c1bc28b8` and
  `LEG L5 FAIL new=(8, 5, 3, 1)`; the current fixture bytes are `e555d8281484`
  (`git log -- tests/fixtures/r39-citation-rev.py` → `d4c1755`, `bbd9b974`, `b769bfb`), so L5's base
  arm now reads `(8, 4, 4, 1)`. The tool bytes are identical (`56866ea8f832/14e9c0f77d7e`); only the
  fixture moved, after the receipt was frozen. **This receipt is therefore not reproducible with the
  current fixture** — a disclosed limit (§8), not a defect this seat repairs.
- two first attempts of this check failed before producing a reading:
  `FileNotFoundError: ... /W1ScribeMistake/ctr-after/souji-r39-c2.bosk8ah1` (the counter's `--scratch`
  is a parent for `mkdtemp`, so it must exist) — recorded because an unrun check has not passed.

## 6. The entry (paste-ready, after M2, before `## Named limits`)

```markdown
### M3 — a leg whose refusal came from the flag it did not name (class: masked-control)

**Class:** masked-control. The C2 counter's first control run called the citation tool for L1/L2
through `run_citation` without a `--register-rev`, so the helper's `"0" * 40` default made the tool
refuse on the register revision before the `--rev` arm ran: both arms printed `rc=2`, and the new
arm's `class=False` was produced by the register arm, not by the rev arm the leg names. The verdict
was therefore insensitive to `--rev` — with the repaired bytes the drafted leg reads PASS whether
`--rev` is the landing revision or `000…`, so the leg could not fail on the property it certifies.
**Evidence pointer:** first control run, L1 transcript 2026-10-28T17:43:57Z:
`LEG L1 FAIL new rc=2 class=False old rc=2 class=False` and
`LEG L2 FAIL new rc=2 class=False old rc=2 class=False`. That receipt was overwritten by the
repaired reading and never committed, so the pointer is the re-runnable pair: the committed
`census/round-39/c2-counter.py:108` still carries the `register_rev="0" * 40` default, and the leg
matrix over committed bytes (`d4c1755` / `ed30b7f`) re-derives the line — R1
`FAIL new rc=2 class=False old rc=2 class=False`; R2 (`--rev d4c1755`, resolvable) and R3
(`--rev 000…`) both `PASS new rc=2 class=True old rc=2 class=False`.
**Captured-by:** the L1's own control run, before any after-data. The arm failed loudly
(`class=False` on both sides) and no rule in the counter requires a leg's refusal class to come from
the flag the leg names.
**Fix:** L1/L2 pass the arm's own revision as `--register-rev` (`register_rev=args.rev` /
`args.base_rev`); L3 keeps `0…` because the register arm is the one it measures. The fix can fail:
with a resolvable `--register-rev` the leg reads `new rc=1 class=False` on the base bytes
(`census/round-39/records/c2-before.txt`; matrix R4) and `new rc=2 class=True` only on the repaired
bytes (`c2-after.txt`; R5), and it fails again as soon as the named revision resolves
(`--rev d4c1755` → `rc=0`, R6).
```

### 6.1 The sweeping command that found it (and the general form)

```
$ for rev in 0000000000000000000000000000000000000000 d4c17557b92fd98044e4c8f0ddc79c6d75701b15; do
    python3 -B $S/cit-new.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev "$rev" \
      --register census/round-38/cells.tsv --register-rev 0000000000000000000000000000000000000000 \
      >/dev/null 2>$S/sw.err; echo "rev=$rev rc=$? class=$(grep -o 'REV-UNRESOLVED' $S/sw.err | head -1)"; done
rev=0000000000000000000000000000000000000000 rc=2 class=REV-UNRESOLVED
rev=d4c17557b92fd98044e4c8f0ddc79c6d75701b15 rc=2 class=REV-UNRESOLVED
$ for rev in 0000000000000000000000000000000000000000 d4c17557b92fd98044e4c8f0ddc79c6d75701b15; do
    python3 -B $S/cit-new.py --root ... --rev "$rev" --register census/round-38/cells.tsv \
      --register-rev d4c17557b92fd98044e4c8f0ddc79c6d75701b15 >/dev/null 2>$S/sw2.err; \
    echo "rev=$rev rc=$? class=$(grep -o 'REV-UNRESOLVED' $S/sw2.err | head -1)"; done
rev=0000000000000000000000000000000000000000 rc=2 class=REV-UNRESOLVED
rev=d4c17557b92fd98044e4c8f0ddc79c6d75701b15 rc=0 class=
```

The first loop is the sweep: **vary only the flag the leg names, holding every other flag at a
resolvable value; if the reading does not move, the leg is not measuring that flag.** The second loop
is the same sweep with the mask removed, and the reading moves (`rc=2` → `rc=0`) — the control the
fixed leg needs.

```
$ grep -nE 'LEG L[0-9]+ (PASS|FAIL) new rc=2 class=False' census/round-39/records/*.txt
no hits in committed receipts
```
Verdict: **PASS (sweep clean).** No committed receipt carries the mask signature; the mistake left no
committed trace, which is why §6's pointer is a command plus the transcript rather than a receipt.

## 7. Scratch

```
$ rm -rf -- /fast/scratch/hyaku/souji-r39/W1ScribeMistake
$ ls -d /fast/scratch/hyaku/souji-r39/W1ScribeMistake
ls: cannot access '/fast/scratch/hyaku/souji-r39/W1ScribeMistake': No such file or directory
```
Verdict: **PASS — no scratch tree left on disk.** The driver is embedded in §4.3 and the probes are
the six single commands of §4.2/§6.1, so every reading above is re-creatable from this report plus
committed bytes.

## 8. Limits and out-of-scope (disclosed, status-neutral)

- **The first control receipt is gone.** `census/round-39/records/c2-before.txt` was committed at the
  freeze (`b769bfb`) carrying the *repaired* reading; the L1's own transcript records the overwrite
  ("I overwrote that file though... the run output was in the transcript, not committed"). The first
  run's bytes never reached the lane — the in-place rewrite class r38 routed as R9 — so the reading
  survives only in the transcript and in §4.3's re-derivation. This seat does not repair it (the file
  is a frozen receipt); whether the lane should commit a `c2-firstrun.txt` reconstruction is the L1's
  call, and a reconstruction would be a derivation, not an observation, and should say so.
- **`c2-before.txt` is not reproducible with the current fixture bytes** (§5): `fixture_sha`
  `c142c1bc28b8` → `e555d8281484`, L5 base `(8, 5, 3, 1)` → `(8, 4, 4, 1)`. The tool bytes and every
  L1-L4/L6 reading are identical. Not claimed as a defect: the fixture was amended after the freeze
  (A1, `bbd9b974`) and the control was measured before it.
- **The transcript is outside the repo** (`~/.omp/agent/sessions/.../SoujiR39.jsonl`) and is not a
  lane artifact; it is cited as the primary record because the receipt it should have produced does
  not exist.
- **Scope:** this seat wrote this report only. It did not edit `corpus/lessons/round-39.md`, the
  counters, the fixture, the prereg, or any receipt; it ran no mutating git/jj command and no
  counter that writes to the lane. Candidate (b) was not written up as a lesson entry (§3).
- **Not judged here:** whether C2's frozen predicate is satisfied — §5's landing run reads
  `pass=6 fail=0 harm=0`, which the L1's own integration owns.
