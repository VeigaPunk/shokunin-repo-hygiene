# SwarmReviewer39 — independent re-derivation of the C1 base counter (round 29, attempt 1, w1)

Item: re-derive C1 K1 (forward + reverse) and K2 from committed bytes at lane base
`691dd29211c53d0ef94fa072394cb9c8a69fe92e` using only `git show`/`ls-tree`/`cat-file` and my own
parser, then compare with `tools/souji-registry-agreement.py`.

## Status

STATUS: PASS — my independent implementation reproduces the tool's base count item for item
(`k1=6` = 1 forward + 5 reverse, `k2=4`, `mismatches=10`) with identical ids, paths and lines, and
the frozen target `0` is reachable by a truthful additive repair; however the counter's own parse
rules admit a `mismatches=0`, rc 0 result with **no truthful repair at all**, filed as ATTACK A1,
and one frozen kill-rule arm names an artifact that does not exist at the frozen revision.

## Evidence

Revisions (all reads against the lane repo, read-only):

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 691dd29211c53d0ef94fa072394cb9c8a69fe92e^{commit}
691dd29211c53d0ef94fa072394cb9c8a69fe92e
$ git -C ... rev-parse b8cb4b31ce80e2e3314b88e85d40ea9873180804^{commit}
b8cb4b31ce80e2e3314b88e85d40ea9873180804
$ git -C ... rev-parse HEAD                -> b8cb4b31ce80e2e3314b88e85d40ea9873180804
$ git -C ... symbolic-ref -q HEAD          -> (none; status -sb prints "## HEAD (no branch)")
$ git -C ... status --porcelain            -> " M .ufo/waves/round-26/w1/ScribeGateDraft.md"
$ git -C ... rev-parse --is-shallow-repository -> false ; for-each-ref refs/replace -> 0 ; git 2.56.0
```

Preregistration read first: `census/round-29/records/preregistration.txt` (C1/K1/K2 text, kill
rule, controls). `census/round-29/stale-statements.tsv` is **absent at base** (verified with
`cat-file -e 691dd292…:census/round-29/stale-statements.tsv`), so the base measurement is only
reproducible with `--list-rev b8cb4b31…`, as the frozen enumerate line says.

Tool run (baseline, exact frozen invocation):

```
$ python3 -B tools/souji-registry-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
K1 used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md
K1 cited-not-in-used-by S075 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S076 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S022 corpus/knowledge/quarantine-origin-record-fields-r24.md
K1 cited-not-in-used-by S024 corpus/knowledge/quarantine-same-filesystem-rename.md
K1 cited-not-in-used-by S025 corpus/knowledge/quarantine-same-filesystem-rename.md
K2 uncorrected LOG.md:1758
K2 uncorrected SCORECARD.md:23
K2 uncorrected corpus/lessons/round-28.md:22
K2 uncorrected corpus/lessons/round-28.md:40
SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e     (rc 1)
```

Same tool at the prereg commit (identical bytes for the measured files —
`git diff --stat 691dd292 b8cb4b31 -- corpus/SOURCES.md corpus/knowledge/ LOG.md SCORECARD.md` is
empty; the prereg commit only adds `census/round-29/*`):

```
SUMMARY k1=6 k2=4 mismatches=10 rev=b8cb4b31ce80e2e3314b88e85d40ea9873180804     (rc 1)
```

My independent derivation (own parser, `/var/tmp/souji-r29-SwarmReviewer39/rederive.py`, python
3.14.8, `python3 -B`; no code copied from the tool):

```
rows=139 dupes=none badrows=none entries=20 indent=3 fm=h1
FORWARD used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md
REVERSE cited-not-listed S075 corpus/knowledge/process-residue-observations.md
REVERSE cited-not-listed S076 corpus/knowledge/process-residue-observations.md
REVERSE cited-not-listed S022 corpus/knowledge/quarantine-origin-record-fields-r24.md
REVERSE cited-not-listed S024 corpus/knowledge/quarantine-same-filesystem-rename.md
REVERSE cited-not-listed S025 corpus/knowledge/quarantine-same-filesystem-rename.md
K2 no-correction-line LOG.md:1758 / SCORECARD.md:23 / corpus/lessons/round-28.md:22 / :40
SUMMARY k1=6 k2=4 mismatches=10
```

Agreement: **exact** — same 6 K1 tuples and same 4 K2 tuples, no extra, no missing. Totals behind
the count: 139 rows, 130 `used-by` path claims, 31 distinct paths (`0` absent at rev, `1`
non-`.md`: `tools/souji-size-census.py`), 21 rows with `—`/empty used-by; 20 entries, 64
front-matter `(entry, id)` pairs — 59 listed, 5 unlisted, 0 cited-with-no-row; 4 pinned statements
each with the phrase at the pinned line (`K2 uncorrected` = phrase present, correction absent) and
`grep -c '^R29-CORRECTION '` = 0 in all three files at base.

Every one of the 10 is a real declaration defect, checked against bytes:
- `S215` (`corpus/SOURCES.md:160`) claims `corpus/knowledge/git-auto-maintenance-trigger-set.md`;
  `git grep -c -w S215 691dd292… -- corpus/knowledge/` returns nothing — no entry cites S215.
- `S022` used-by names only `trash-spec-restorable-quarantine.md`, but
  `corpus/knowledge/quarantine-origin-record-fields-r24.md:4` starts `source: S022 — …`.
- `S024`/`S025` used-by is `—`, but `corpus/knowledge/quarantine-same-filesystem-rename.md:1`
  cites both.
- `S075`/`S076` used-by names `corpus/lessons/round-18.md` (which does contain both ids), not the
  entry that cites them: `corpus/knowledge/process-residue-observations.md:1`.

### Parse-mode sensitivity of my derivation (bytes unchanged)

| boundary / indent | k1 | reverse findings |
|---|---|---|
| `h1` stop (tool's rule), 0-3 indent | 6 | 5 |
| any ATX heading stop | 6 | 5 |
| strict YAML `---` block | 1 | 0 (no entry opens with a `---` fence) |
| whole file, no boundary | 6 | 5 |
| row indent 0 / row indent 4 | 6 / 6 | 5 / 5 |

So on today's bytes the tool's h1 boundary and a stricter heading boundary are indistinguishable,
and the pseudo-front-matter blocks are bare `source:` lines at file head, not YAML.

### False-zero / gaming probes (scratch clone at base, own identity, removed afterwards)

| probe | edit | result |
|---|---|---|
| P0 | none | `k1=6 k2=4` rc 1 |
| P1 | duplicate `S075` row whose used-by names the entry | `k1=5` |
| P2 | `S215` row indented 4 spaces | `k1=5` |
| P3 | entry keyword `source:` → `sources:` | `k1=5` |
| P4 | entry source line indented by 2 | `k1=5` |
| P5 | prose mention `S215` added to the entry | `k1=5` |
| P6 | body `source:` block cites unlisted `S999` | `k1=6` (missed) |
| P7 | entry at `corpus/knowledge/sub/x.md` citing `S999` | `k1=6` (missed) |
| R1 | `S055` unlisted while front matter says only `S051–S063` | `k1=6` (missed) |
| Q1 | four corrections inserted naively between `:22` and `:40` | `k2=1`, item becomes `K2 phrase-moved-or-edited corpus/lessons/round-28.md:40` |
| Q2 | in-place rewrite of `LOG.md:1758` keeping the phrase | not flagged |
| Q3 | `R29-CORRECTION LOG.md:17580 …` | `k2=3` (satisfies `LOG.md:1758`) |
| Q4 | space-separated used-by cell | `k1=8` (loud, not silent) |
| Q5/Q6 | 12-cell row / literal pipe in a cell | rc 2 `COULD-NOT-EVALUATE` (fail-closed) |
| R3 | `R29-CORRECTION` line inside a fenced block | counted (`k2=3`) |
| S1 | truthful additive repair + both `round-28.md` corrections below line 40 | `k1=0 k2=0` rc 0 |
| S2 | same but `S215` used-by retracted to `—` | `k1=0 k2=0` rc 0 |
| T1 | one TSV row dropped at the tip, run **without** `--list-rev` | `k2=3` (case silently dropped) |

## Findings

1. **F1 (medium) — K2's `round-28.md` double pin makes the naive repair self-defeating.**
   Location: `corpus/lessons/round-28.md:22` and `:40` (both pinned in
   `census/round-29/stale-statements.tsv`). Inserting a correction line after `:22` shifts `:40`
   to 41 and the counter reports `K2 phrase-moved-or-edited …:40` (probe Q1: `k2=4→1` when all
   four corrections look correct). A truthful repair must place **both** `round-28.md`
   correction lines at or after line 41 (e.g. at index 40, two lines). `LOG.md:1758` and
   `SCORECARD.md:23` have no second pin and are safe.
2. **F2 (medium) — the frozen kill rule's third arm names a nonexistent artifact.**
   Location: `census/round-29/records/preregistration.txt` C1 kill rule v.
   `tests/fixtures/r29-registry-agreement.py`: absent at base, absent at the prereg commit, absent
   in the worktree. The arm "the fixture accepts an always-zero emitter" cannot be executed at
   the frozen revision.
3. **F3 (medium) — correction tags match by substring, so wrong line numbers satisfy the pin.**
   Location: `tools/souji-registry-agreement.py:96` (`tag in x`). `R29-CORRECTION LOG.md:17580`
   clears `LOG.md:1758` (Q3), likewise `SCORECARD.md:230`, `…round-28.md:220`, `…:400`.
4. **F4 (medium) — "append-only" is not enforced, only phrase presence.**
   Location: `tools/souji-registry-agreement.py:92-96`. A statement rewritten in place while
   keeping the phrase passes (Q2), and a correction line inside a fenced block counts (R3). The
   contract's kill rule claim that K2 flags an in-place edit is true only for edits that drop the
   phrase (the shipped junk control `C1-junk2` is of that kind).
5. **F5 (medium) — duplicate row ids silently overwrite.**
   Location: `tools/souji-registry-agreement.py:46` (`rows[c[1]] = …`). P1: a duplicate `S075` row
   hides the original row's used-by disagreement (`k1 6→5`); no dupe detection, no error.
6. **F6 (low, latent) — body `source:` blocks are unscanned.**
   Location: rule at `tools/souji-registry-agreement.py:64-65` (stop at first `^#\s`). Live shape
   today: `corpus/knowledge/process-residue-observations.md:103` and `:148` (ids S086/S087/S088/
   S095, all correctly listed, so no count change now). P6 shows an unlisted id there is invisible.
7. **F7 (low, latent) — range citations contribute endpoints only.**
   Location: `corpus/knowledge/jj-colocation-receipts.md:1` (`source: see … (S051–S063)`) plus the
   `S\d{3,}` extraction at `tools/souji-registry-agreement.py:67`. Today this is *correct by
   content, not by parse*: the entry's own `## Source rows` section (line 132+) states that S057,
   S058, S059, S061, S062 are "Not cited by any claim in this entry", and those five rows
   accordingly do not list it. R1 shows that an interior id genuinely cited only by range would be
   missed.
8. **F8 (low, latent) — shape variants produce false zeros.** Rows indented ≥4 (row regex `tools/souji-registry-agreement.py:17`; P2), entry keyword
   `sources:`/indented (P3/P4), prose mention satisfying the forward test (P5), entries only under
   `corpus/knowledge/<name>.md` at depth 2 (`tools/souji-registry-agreement.py:60`; P7). None of these shapes exists at base: all 139 rows
   are at column 0 with 11 cells, no dupes, no `;` in any used-by cell, no symlinked used-by path.
9. **F9 (low, latent) — a symlinked used-by path is misread.** `cat-file blob rev:path` on a
   symlink returns the link text, so a symlink to a citing entry reports `used-by-no-cite` plus a
   reverse finding (probe S3: `k1 6→8`). No live instance (all 31 used-by paths are non-symlink
   blobs).
10. **F10 (low) — the case set can be swapped by omitting `--list-rev`.**
    Location: `tools/souji-registry-agreement.py:113` (`a.list_rev or a.rev`). T1: dropping one TSV
    row at the tip and running without `--list-rev` yields `k2=3` with the case silently gone.
    The L1's final-tip verification must always pass `--list-rev b8cb4b31…`.
11. **F11 (low) — an unenforced obligation.** The frozen C1 clause requires `used-by`/`status` cell
    changes to be logged old→new in `corpus/lessons/round-29.md`; no counter reads that log. Probe
    S1 reached `0/0` with no such edit.
12. **F12 (observation) — lane checkout is detached.** `symbolic-ref -q HEAD` returns nothing and
    `git status -sb` prints `## HEAD (no branch)` at `b8cb4b31…`, while the preregistration says
    "branch master". `master` does contain that commit, so bytes match, but a landing commit made
    in this state would not advance `master` — the "measured at the C1 landing commit and again at
    the final tip" wording presumes master.

13. **F13 (observation) — ignored bytecode residue in the lane tree.** `tools/__pycache__/` holds
    three `cpython-314.pyc` files (`souji-axis-check`, `souji-gate-check`,
    `souji-landing-gate`; mtimes 2026-10-25 14:25–14:58 UTC, i.e. before this seat's runs), matched
    by `.gitignore:3 __pycache__/`. Not created by me (all my runs used `python3 -B` or stdin
    scripts) and not removed by me under the write-scope bound; flagged for the L1.

## Attack log

**A1 — shape-only zero (headline).** Reached `SUMMARY k1=0 k2=0 mismatches=0`, rc 0 at a fresh
commit on a scratch clone of base with **no truthful repair**: (i) append duplicate `S075` and
`S076` rows whose used-by names the entry; (ii) indent the `S215` row by four spaces; (iii) change
`source:` → `sources:` on the one tripping line of `quarantine-origin-record-fields-r24.md` and on
line 1 of `quarantine-same-filesystem-rename.md`; (iv) add `R29-CORRECTION LOG.md:17580`,
`SCORECARD.md:230`, `corpus/lessons/round-28.md:220`, `:400` below the respective pins. The six
real disagreements remain byte-identical and none of the four statements is corrected. The kill
rule keys on `mismatches>0`, so it does not fire. The frozen junk controls
(`census/round-29/records/controls.tsv`) do not include this composition.

**A2 — kill-rule arm 2 as written is false.** "a repair that edits a stale phrase in place (K2
flags phrase-moved-or-edited)": a phrase-preserving in-place rewrite of `LOG.md:1758` scores the
same as no change (Q2).

**A3 — correction tags are substring pins.** Wrong line numbers that extend the pinned number are
accepted (F3, Q3); a correction line inside a code fence is also accepted (R3).

**A4 — repair and retraction are indistinguishable.** Retracting `S215`'s used-by claim to `—`
reaches `0/0` exactly like the truthful route of citing S215 in the entry (S1 vs S2). C1's zero
therefore does not certify that the declaration was made true rather than deleted.

**A5 — case-set substitution.** `--list-rev` omission lets the measured case set differ from the
frozen TSV (T1).

Recommendation (not an amendment; the frozen predicate is unchanged): land C1 by the truthful
additive route (S1 recipe), keep both `round-28.md` corrections at or below line 41, always pass
`--list-rev b8cb4b31…`, and have the L1 state in the round record that C1's `0` is corroborated by
the two independent derivations plus the old→new cell log — not by the counter's zero alone.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmReviewer39.md` (this report).

No other file was written in the lane. Scratch (`/var/tmp/souji-r29-SwarmReviewer39/` and the
clone `/var/tmp/souji-r29-SwarmReviewer39.oV3lUp/`) is removed; no tool was installed or upgraded;
no `git`/`jj` mutation was run outside that scratch clone.

## Residual risk and verification gaps

- I did not run the counter at a C1 landing commit or final tip; none exists. The `0` claim is
  evidenced by my scratch simulation (S1), not by a lane commit.
- F2 means the third kill arm is unexecutable as frozen; whether a seat adds that fixture later is
  outside my read.
- The tool inherits the caller's git environment (`GIT_DIR`/`GIT_OBJECT_DIRECTORY` are not cleared)
  and honours replace refs; the lane has none today (`for-each-ref refs/replace` = 0), and every
  run recorded here used the plain frozen invocation.
- C2/C3 counters were not exercised by this seat.
