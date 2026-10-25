STATUS: PASS

# RevImplB — independent dual-implementation review of the C1 declared-evidence tool

Item: review candidate B (impl-b) against the frozen C1 contract *without* reading the
impl-a review, then run **both** candidates against base `4edb25d` + `SCORECARD.md` and
diff their per-assertion TSVs. Verdict at the end. Read-only throughout; nothing written
outside `.ufo/waves/round-22/attempt2/w1/{RevImplB.md,evidence/RevImplB.md}`.

## Artifacts under review (exact bytes)

| side | path | sha256 | lines |
|---|---|---|---|
| A | `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/souji-declared-evidence.py` | `fdde02759a281aba003358636ec02707afcfe240df83ec7de0f91a359d6aae8c` | 448 |
| B | `.ufo/waves/round-22/attempt2/w1/evidence/impl-b/souji-declared-evidence.py` | `021d90e9946a5cf6d9d82bf8d5d5f49286e4aa4dc1d5b08dd1e45c3ff1f6dcbc` | 553 |

Contract source: `.ufo/waves/round-22/attempt2/preregistration.txt` §C1 (read first, not
restated here). Lane tip at review time: `2a130b4`; base: `4edb25dfe262515d0da63224bbba71e02e36cba5`.

Timeline caveat that affects any comparison with an earlier reader: the impl-a file changed
under me at 03:52:35. The snapshot I first measured (same byte size, older content) skipped
dot-prefixed repo paths and its `--selftest` crashed with `IndexError`. The final bytes above
fix both. **Every table below is against the sha256 in the table.** The earlier numbers are
named in L2 only so they are not mistaken for current behaviour.

## Executed evidence

Base measurement, `--root . --file SCORECARD.md --rev 4edb25d --format counts` (lane root):

```
A  assertions=56 resolved=53 skipped=45 mismatches=3   rc=1
B  assertions=54 resolved=51 skipped=25 mismatches=3   rc=1
L  assertions=56 resolved=53 skipped=33 mismatches=3   rc=1   (installed tools/souji-declared-evidence.py)
O  assertions=53 resolved=50 skipped=35 mismatches=3   rc=1   (my literal-reading oracle, /var/tmp)
```

Same command at the current tip `2a130b4`:

```
A  assertions=56 resolved=56 skipped=45 mismatches=0   rc=0
B  assertions=54 resolved=54 skipped=24 mismatches=0   rc=0
L  assertions=56 resolved=56 skipped=36 mismatches=0   rc=0
O  assertions=54 resolved=54 skipped=38 mismatches=0   rc=0
```

Mismatch sets at base are identical for A and B (and L, O):

```
3   AXES.md                                              A  mismatch:path-absent
63  reason-after.txt                                     A  mismatch:path-absent
77  .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md A  mismatch:path-absent
```

Frozen kill-rule fixtures, run by an external harness that commits each fixture declaration
at the revision it is measured at (matching the counter's shape; scripts in `/var/tmp/revimplb/`):

```
A  control=PASS fixtures=8/8   (5 frozen fixtures + correct-digest positive + always-zero control + absent-declaration refusal)
B  control=PASS fixtures=8/8
L  control=PASS fixtures=8/8
```

Own self-tests: `B --selftest` → `selftest 8/8 PASS`, `control=FALSE-GREEN-REJECTED`;
`A --selftest` → `selftest=6/6` (final bytes; the earlier snapshot crashed).

Write check: `git status --porcelain` in a clean probe repo was empty before and after
running both candidates; neither created repo files. Installed tools: none (python3 stdlib +
git only).

## Per-assertion diff, base `4edb25d`

`diff` over normalised TSVs (assertion rows only, verdict ∈ {resolved, mismatch}):

```
A assertions=56  B assertions=54
line   token                                                      c  A          B
33     6f8ee0f                                                    B  resolved   SKIP
105    29c1f7e8df849be8ee1b2d62d2351e17ec9d21a8                   B  resolved   SKIP
--- agreement: 54 rows; disagreement: 2 rows
```

At tip `2a130b4` the same two rows disagree (lines 38 and 114, shifted by the repair commits);
everything else agrees. Per-class counts (`awk` over the TSVs) show the divergence is
confined to class B:

```
               class A   class B   class C
base  A           50        6         0
base  B           50        4         0
tip   A           51        5         0
tip   B           51        3         0
```

So the two independent implementations agree on **every class-A presence/absence outcome in
the frozen artifact** (50/50 at base, 51/51 at tip), have no class-C rows at all, and their
M values agree (3 at base, 0 at tip). The only SCORECARD-level disagreement is the prose-hex
reading.

Because the SCORECARD contains no 64-hex token at base or tip
(`grep -cE '[0-9a-f]{64}'` → 0 on both), class C is unexercised on real bytes. I therefore
built a 24-probe semantic corpus (declarations committed at the measured rev) to force the
ambiguity/defect set to the surface. Probe-level disagreements:

```
probe                          A            B            L(installed)  O(oracle)     classification
p1  prose hex, "measured"      assert       skip         assert        skip          spec-ambiguity (class B "table cell")
p20 prose hex, prose ctx       assert       skip         assert        skip          same clause as p1
p19 escaped \| path|hex        skip         assert       skip          assert        bug:A (cell split on "\|")
p22 escaped \| + dangling hex  M=0 (!!)     M=1          M=0 (!!)      M=1           bug:A — false green
p18 digest + glob path         TypeError    C mismatch   skip C        skip C        bug:A (crash) / bug:B (glob as C path)
p21 digest + path:12           C resolved   C mismatch   C resolved    C resolved    bug:B (":line" not stripped)
p3  digest + two paths         TypeError    skip C       skip C        skip C        bug:A (crash)
p17 prose digest + two paths   TypeError    skip C       skip C        skip C        bug:A (crash)
p24 table inside ``` fence    2 mismatches 0 enumerated 2 mismatches  2 mismatches   bug:B (class A unconditional)
p2,p4-p16,p23                  agree        agree        agree         agree         —
```

Probe expectations are the frozen text read literally; where readings legitimately differ the
row is labelled `spec-ambiguity` and the clause is named, not decided by me.

## Findings

### HIGH

**H1 `bug:A` — class-C skip path crashes instead of emitting the counts line.**
`run()` formats a skip detail as `reason % s["arg"]` (line 290) but `s["reason"]` holds the
`SKIP_REASONS` *key*, not its text; when any 64-hex token coexists with ≠1 backticked path
(two paths, a glob, or a prose line) the tool dies:
`TypeError: not all arguments converted during string formatting` → exit 1, no counts line
(probes p3, p17, p18). The frozen interface requires one counts line and exit 0 iff M==0.
Not reachable on the current SCORECARD (no 64-hex), but it is exactly the class-C shape the
contract defines.

**H2 `bug:B` — class-C path adjacency uses the raw span text.**
`cell_paths` stores `content.strip()` without passing it through class-A tokenisation
(lines 280-287, consumed at 318-325). Consequences: a glob is accepted as the single path and
the digest is looked up as a literal path (`p18` → spurious `mismatch:path-absent`), and a
`:line` suffix is not stripped (`p21`: `tools/present.sh:12` → `mismatch:path-absent`, while
A, the installed tool and my oracle resolve class C through `tools/present.sh`). Class C says
"exactly one backticked path … sha256 of that path's bytes"; a glob has no digest and a
line-suffixed token is class A's spelling. Direction: fail-closed (extra M), so it cannot
manufacture a green, but it can block a legitimate `M=0`.

**H3 `bug:A` — escaped `\|` is treated as a cell delimiter (false green).**
`scan()` uses `line.split("|")`, so a `\|` inside a Markdown cell manufactures fragments that
are not cells. `p22` — a dangling revision token in the same real cell as
`` `census/round-1/c1.json` `` — is skipped: **A reports `mismatches=0`, B and my oracle
report 1.** Direction: FALSE GREEN, the one direction the C1 kill rule exists to catch.
The installed reference tool shares this defect (`L` also prints `mismatches=0` on p22),
which is a risk to the frozen counter itself, not only to a candidate.

**H4 `bug:B` — class A is not applied inside fenced blocks, and the omission is not counted.**
`evaluate()` toggles a fence flag and `continue`s both fence markers and fenced lines. `p24`
(a table inside ``` fences) yields `assertions=0 skipped=0`; A, L and O each assert two
mismatches. Frozen class A is unconditional (no cell or fence condition), and skipping without
counting contradicts "N+S enumerates every candidate token the scanner saw". Latent today:
`grep -c '^```' SCORECARD.md` → 0 at base and tip.

### MEDIUM

**M1 `bug:B` — worktree fallback crashes.** `read_declaration()` returns
`handle.read()` outside the `with open(...)` block (line 124), so a declaration absent at
`--rev` but present in the worktree raises `ValueError: read of closed file` (exit 1, no
counts line). A refuses the same input cleanly with `rc=2`. Latent for the frozen counter
(the SCORECARD is tracked at both measured revs), but the "after" run is exactly the moment a
repair may be staged-but-uncommitted.

**M2 `spec-ambiguity` — "inside a table cell" (class B) vs prose lines.** A resolves a
non-table line as one context unit (documented in its `scan()` docstring) and asserts the two
prose revision tokens at base lines 33 and 105; B applies the frozen cell restriction
literally and skips them. Base: N 56 vs 54, M 3 vs 3. Tip: N 56 vs 54, M 0 vs 0. The clause
`B. a bare hex token … inside a table cell that also names a revision context` is decisive
for N and therefore for the "enumeration" claim in C1, but the prereg does not say whether a
prose line is "a cell". Owner must freeze one reading; B is compliant with the literal text.

**M3 `spec-ambiguity` — "skipped counts tokens excluded by these rules (so N+S enumerates
every candidate token the scanner saw)".** A: S=45, counts every backticked span and every
hex-shaped run (occurrence-counted, including embedded runs such as `repair4d5bf…`).
B: S=25, counts hex tokens and path-shaped words only. "Candidate token" is never defined, so
both satisfy their own scanner; N+S is not comparable across implementations.

### LOW

**L1 `spec-ambiguity` — declaration source.** A reads only `rev:file` (clean `rc=2` if
absent). B reads `rev:file`, warns on stderr when the worktree differs, and falls back to the
worktree when the file is absent at rev. The prereg is silent; both audit the committed bytes
in the frozen counter's shape.

**L2 temporal note (obsolete finding).** The impl-a snapshot measured at 03:49 skipped
dot-prefixed repo paths (`PATH_RE` first character class excluded `.`), reporting base
`M=2` and losing the genuine `.ufo/scopes/…/obsidian-cli-probe.md` mismatch; its selftest
crashed. Final impl-a bytes (`fdde0275…`) enumerate `.ufo/…` correctly and its selftest
passes 6/6. No current finding.

## Verdict on impl-b

**ACCEPT-WITH-FIXES.**

Against the frozen contract on the measured artifact, B is contractual: identical class-A and
class-C outcomes to the independent implementation on every row, identical mismatch set and
M at base (3) and tip (0), all five frozen fixtures plus the always-zero control
(8/8, `FALSE-GREEN-REJECTED`), no writes, counts line and exit semantics exact. Its
SCORECARD-level disagreement with A (M2) is the *literal* reading of the frozen clause, so it
is not a defect.

Required fixes before B could be named the counter:
1. H2 — run class-C adjacency paths through class-A tokenisation (strip `:line`, reject
   glob/absolute/`..` spans); otherwise a legal SCORECARD cell can force a false mismatch.
2. H4 — apply class A inside fences (or count the skipped tokens), so a fenced table cannot
   vanish from N+S.
3. M1 — read the fallback bytes inside the `with` block.

Optional, if the owner freezes M2 toward the broader reading: extend class B/C to non-table
lines, which would align B with A and the installed tool at N=56.

## Residual risk

- **The installed counter shares H3** (and A's non-table-line reading). Both are M-neutral on
  base and tip, but the frozen C1 enumeration is therefore not the strictest reading
  available: a cell that carries a token, `\|`, and its revision context in one Markdown cell
  is silently unmeasured. This is the largest remaining calibration risk in C1.
- Class C has **no real-bytes coverage** (0 64-hex tokens in either SCORECARD), so both
  candidates' class-C behaviour is only proven on synthetic probes; B's two C defects are
  invisible on the artifact C1 actually measures.
- All four implementations agree on the three base mismatches and on `M=0` at tip, so the
  C1 before/after direction is robust to the implementation choice.

## Verification gaps

- My fixture harness commits declarations at the measured rev (the counter's shape); it is
  not a byte-copy of the prereg's fixture repository, although the fixture *semantics*
  (1-5) and the always-zero control are the frozen ones.
- Read-only was checked with `git status --porcelain` and filesystem inspection, not a
  syscall trace.
- I read neither the impl-a review nor either executor's report; only the two `.py` files and
  their runtime behaviour. The oracle and probe corpus in `/var/tmp/revimplb/` are my own
  literal reading and are labelled as such wherever they appear.

Report: written to `.ufo/waves/round-22/attempt2/w1/RevImplB.md` (report) and
`.ufo/waves/round-22/attempt2/w1/evidence/RevImplB.md` (named evidence path), identical bytes.
