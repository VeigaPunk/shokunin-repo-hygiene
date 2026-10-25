STATUS: PARTIAL

Critic seat `L1Souji22.ResClaims`. Judged the round's two claims on the frozen
predicates in `.ufo/waves/round-22/attempt2/preregistration.txt`; attacked the
landed bytes, not the authors. Read-only: no git/jj write, no cleanup, no
signals, no installs, no reads of `/proc`, credentials, private TSVs, `.tower` or
the operator sweep. `shokuknow` was `stat`ed only. Wrote only this report and
`residual/evidence/ResClaims-*`.

The lane moved five times during the review
(`4a6ee90 → c9f1fe3 → f8f0b4a → 8990ae4 → c1664fc`). Every finding below is
pinned to one revision and re-checked at the final tip
`c1664fcde8b12c7e6082a98cbbab1f1e7509177d` (SCORECARD digest
`c45da147…e116c04a`; instrument digest `65817d0d…f21448f4`). Findings that were
true at `4a6ee90` and repaired by `c1664fc` are labelled fixed, not carried.

## Executed

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev <R> --format counts
4edb25d (base)  assertions=55 resolved=52 skipped=33 mismatches=3   rc=1
8990ae4         assertions=62 resolved=62 skipped=39 mismatches=0   rc=0
c1664fc (tip)   assertions=62 resolved=62 skipped=39 mismatches=0   rc=0
f8f0b4a         assertions=63 resolved=61 skipped=39 mismatches=2   rc=1
  L14 AXES.md A mismatch:path-absent ; L14 65817d0d0d4874e8 B mismatch:rev-unresolved

$ python3 -B tools/souji-declared-evidence.py --selftest
selftest=8/8  PASS control always-zero -> FALSE-GREEN-REJECTED

$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0    rc=0
--selftest -> selftest=9/9, control always-green -> FALSE-GREEN-REJECTED

$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
ec=0 (souji ok corpus/SOURCES.md; 114 rows)
```

Both frozen counters reproduce their "After" lines exactly at the tip, both
reject their always-green control, and both "Before" conditions hold
(C1: M=3 > 0; C2: entries absent → rc=1, per round 1). Full log and byte
snapshots: `residual/evidence/ResClaims-*`.

## Claim verdicts

### C1 — calibration: `verifies-bounded`

The frozen statement ("zero assertions that do not resolve, over the enumerated
set") is **supported**: 62/62 resolved, 0 mismatches, rc=0 at both the revision
the row names (`8990ae4`) and the revision that carries the row (`c1664fc`), with
one pinned instrument (`65817d0`) producing both ends of the before/after
(55/52/33/3 → 62/62/39/0). A do-nothing control scores M=3. No token the enum
should count is dangling: raw-text sweep of the audited file found 12 hex-like
tokens (0 dangling) and 66 path-like tokens, whose only absent targets are an
absolute host file that exists (`/home/vgpnk/Projects/shokunin/AXES.md`), a path
the row now records as absent, and non-backticked bare filenames in command
context. The brace-range glob and the `jj-receipts-*.txt` glob that survive are
either outside the frozen `*` class or resolve (2 matches).

**The calibration axis move is not supported — and, at the tip, is no longer
claimed.** The row says "record accuracy, not a scored axis move" and keeps
score 7. That is the correct disposition: the enum has named holes (below), so a
7→8 credit on `mismatches=0` would be premature saturation. Round 1's
"move not supported" therefore stands, but the round has stopped asserting the
move rather than defending it.

Two **new** residual counterexamples (neither is a round-1 restatement):

**C1-R1 — the cited before receipt contradicts the row's own base number
(executed, BLOCKING for "same instrument, both ends").**
The row quotes base `assertions=55 resolved=52 skipped=33 mismatches=3` and, in
the same cell, cites `census/round-22/attempt2/declared-evidence-before.tsv` as
the before receipt. That committed file's own counts line is
`assertions=56 resolved=53 skipped=33 mismatches=3` and it carries a class-B row
the pinned instrument no longer enumerates:

```
$ tail -1 census/round-22/attempt2/declared-evidence-before.tsv
assertions=56 resolved=53 skipped=33 mismatches=3
$ grep -n 41553adb …
2:14  41553adb139d06511dc386bb3ce4326aebfba675  B  resolved
```

Mechanism, executed, not inferred: at base L14 that 40-hex appears inside a
`` `git show <rev>:…` `` command span and again glued to the word `base`. The
pre-`4a6ee90` `cells_of` split the line on an escaped pipe *inside* the cell,
mis-pairing backticks so the command-embedded token survived the span blanking
and was counted; the escaped-pipe split (`4a6ee90`) blanks it, and the glued
occurrence is excluded by the regex's own boundary. So **55 is the frozen enum's
count and 56 is an artifact of the old scanner** — the receipt was produced by a
different instrument than the one now pinned. Reproduced end to end: tool at
`5fdd5d5` on base → 56/53; tool at `4a6ee90`/`c1664fc` on base → 55/52.
The same stale count is in a second landed record: M15 of
`corpus/lessons/round-22.md` (`:314`) cites that receipt with
`assertions=56 resolved=53 skipped=33 mismatches=3`, so the lesson and the
SCORECARD row now disagree with the instrument they both point at by one
assertion.
*Smallest correction:* regenerate the before TSV at `4edb25d` with `65817d0`
(55 rows, counts line 55/52/33/3) or drop the receipt pointer and cite the
command only. Do not edit the counts line in place without regenerating the rows.

**C1-R2 — the instrument-authority file names a red revision as the lane tip
(executed).** `census/round-22/attempt2/instrument-digests.txt` is the file the
row pins the instrument to; its metadata line reads
`lane_tip=f8f0b4a2c4ab3d16369413b6aa9f2d2c08590581`. At exactly that revision the
same pinned tool and file report `assertions=63 resolved=61 skipped=39
mismatches=2, rc=1` (bare `AXES.md`; a truncated 16-hex `65817d0d0d4874e8` that
is not a commit object). The row names `8990ae4` (green, after row cleanup) and
is itself committed at `c1664fc`, so the evidence bundle carries two different
"tip" claims and the one a reader would use to re-derive the record is the red
one. *Smallest correction:* set `lane_tip` to the revision the row names, or to
the commit in which the digest file was written, and re-measure; or delete the
`lane_tip` field — the two tool digests in that file are correct
(`65817d0…` and `5b8025a…` both match the committed tools).

Round-1 findings, checked against the landed tip (not restated as new):

| round-1 finding | state at `c1664fc` |
|---|---|
| headline receipt drifted from the tool output | **fixed** — quoted `62/62/39/0` reproduces at `8990ae4` and `c1664fc` |
| instrument not digest-pinned | **fixed** — `instrument-digests.txt`; see C1-R2 for the stale `lane_tip` in it |
| false "same 56 assertions" conservation sentence | **fixed** — "multiset delta is instrument-dependent and is not claimed" |
| `AXES.md` repair satisfies none of the three frozen branches | **still open** — absolute host path, no revision, no receipt; now disclosed in the row ("leaves class A"), but disclosure is not one of the three branches. If the prereg Target's truth-preserving clause is read as part of C1, C1 is short of `verifies` on this one cell. The host file exists, so the pointer itself is true outside the lane repo |
| class B over-counts prose lines (`cells_of` → `[line]`) | **still open** — tip L38 (`6f8ee0f`, pipes=0) and L114 (`29c1f7e…`, pipes=0) are counted; not in the row's enum-limits list, though both resolve |
| class C structurally empty; command-embedded paths skipped; skips not itemised; class B proves existence, not measurement | **still open, disclosed** in the row |
| brace-range globs (`round-{6..11}.md`) skipped | **still open, not disclosed** — outside the frozen `*` class, so not a claim violation, but the row's "enum limits, named" list omits it |

### C2 — coverage: `verifies-bounded`

The frozen counter and both halves of the Target reproduce: `entries=2 ok=2
slice_verdicts=8 slice_total=8 fail=0`, rc=0, selftest 9/9 with the always-green
control rejected, and `sources-census.sh validate … souji` rc=0. The slice has
exactly one verdict per id (5 accepted / 2 present / 1 unverifiable / 0 refused,
matching M23), and the counter matches ids rather than only counts, so a missing
row lowers V.

**The COVERAGE credit is not supported by Q1/Q2 — and at the tip it is not
claimed.** `CritC2Coverage`'s Q1 (both halves of the theme already held by
`trash-spec-restorable-quarantine.md` and `quarantine-same-filesystem-rename.md`)
and Q2 (adapting a staged entry is import, not coverage) still hold against the
adopted bytes. The round now absorbs that verdict rather than contesting it:
the coverage row reads "Numeric delta0 … r22 no expansion claimed", M22 records
"the claim is only admissible as **import with re-grounding**, not as new
ground … coverage score is left unchanged", and both entries state an explicit
delta over the held entries. So the correct answer to "is the credit supported"
is **no**, and the only reason no honor is falsely banked is that the credit was
withdrawn. If a judge were asked for a coverage gain, +2 files is corpus growth,
not a frontier move: both entries decline to change F4's next step.

**Strongest remaining counterexample (executed):** the `8/8` counts classified
rows, not verified anchors. Only one of eight verdict rows names a committed
artifact in the wave (`S126` → `gtk-filetrash.txt`); the other seven are prose
(`S114` "snapshot git-scm git-prune", `S118` a DOI, `S123`/`S131` git-worktree
pages, `S133` "payload line 11", `S138` "qiita page"). `S133` is the sharpest:

```
$ nl -ba census/round-22/attempt2/sources/vendor-noreplace-probe.out   # 6 lines, last is "kernel: …"
$ grep -rn "every writable mount" .          # only the S133 verdict row itself
```

An `accepted` row whose supporting line is `line 11` of a six-line artifact, and
whose quoted string exists nowhere in the lane. The frozen slice predicate
(class + non-empty pointer) permits this, so it does not falsify the counter; it
bounds what `V=8` may be cited for. M23's own flip ("a row classed `accepted`
whose span is in no reachable document") is not literally triggered — S133's
quoted span is rename(2) prose — but the supporting claim is unbacked and should
be `unverifiable` or re-pointed.

Round-1 findings, checked against the landed tip:

| round-1 finding | state at `c1664fc` |
|---|---|
| F1 r24 cites a dangling `…-r23.md` lane pointer | **fixed in substance** — now `merge/souji/knowledge/corpus/knowledge/quarantine-origin-record-fields-r23.md`, which exists in the package (stat OK); the landing gate no longer emits `LG-DANGLING-PTR` for it. Caveat: package-relative with no root marker, and the gate's extractor ignores the prefix, so it is un-gated rather than gated-and-clean |
| F2 r23 Gate locator named a non-existent `OPTIONS` heading | **fixed** — "§ DESCRIPTION, option `--no-copy`"; the quoted line is `man7-mv.1.txt:91` under DESCRIPTION (`:60`), and the page has no OPTIONS heading |
| F3 r23 title overclaimed "every device" | **fixed** — "exists on the five devices this fleet's repositories live on" |
| F4 two id spaces in one round's evidence | **still open (minor)** — `slice-verdicts.tsv` still has no header or `campaign:` marker; the map lives only in M16/M21 |
| F5 the coverage claim overstates novelty | **resolved by withdrawing the credit** (see above); the residual "S022 `used-by` understates its users" is unaddressed but is not a frozen requirement |

Out of scope here: the gate-check predicate holes demonstrated by
`CritC2Counter` (fabricated roots, authored snapshots, seam splicing) and the
strict-adequacy claim; I did not re-run those fixtures. The lane's **landing
gate is red at the tip** (`rc=1, findings=4`: `README.md:217` ×2,
`jj-colocation-receipts.md:148`, `round-22-verifier-spotcheck.md:32`), but the
same four findings are present at base, so they are inherited, not caused by
C1/C2, and lie outside both frozen counters.

## Impacted axes

* **calibration** — the claimed record accuracy reproduces at the tip, but the
  evidence bundle is internally contradictory (C1-R1, C1-R2): its linked before
  receipt is one assertion off and from the pre-pin instrument, and its
  instrument-authority file names a red revision as the tip. Neither is visible
  to the enum (no class D), which is the same failure mode round 1 named, now
  with two concrete instances rather than a hypothetical.
* **coverage** — no gain is claimed and none is supported; `V=8` is a row count,
  not an anchor audit, and 7/8 pointers cannot be re-derived from lane bytes.
* **operability** — the instrument is pinned (improvement), but the pin file's
  `lane_tip` is stale and red, so the pin does not by itself make the receipt
  reproducible.

## Smallest safe corrections

1. Regenerate `declared-evidence-before.tsv` at `4edb25d` with the pinned tool
   (55/52/33/3) — or drop the receipt pointer from the row and keep the command.
2. Set `instrument-digests.txt`'s `lane_tip` to the revision the row names, or
   delete the field; re-derive the row's after receipt once at that revision.
3. Add "prose lines are cells; class B over-counts non-table lines" and "brace
   ranges are skipped" to the row's enum-limits list, or restrict class B to
   lines with ≥2 pipes (one condition in `cells_of`).
4. Re-point or downgrade `S133`'s payload-line claim and add an id-space header
   to `slice-verdicts.tsv`.

None of these needs a new claim, a new revision, or deletion authority.

## Executed vs inferred

Executed: the four C1 counters and their token-level deltas; the pre/post
`4a6ee90` before-count difference with its span/backtick mechanism; the
committed before-TSV content and counts line; `instrument-digests.txt` content
and the red `f8f0b4a` measurement; the raw-text sweep of 66 path-like and 12
hex-like tokens (and 0 64-hex) in the audited file; C1/C2 selftests; the C2
counter, verdict classes, `S133` grep and probe line count; `sources-census.sh
validate`; the landing gate at base and tip; entry/Gate/title/pointer checks and
the `stat` of the package pointer. Inferred (marked in place): that the
pre-`4a6ee90` 56 is an artifact *rather than* an enum-required token — the
mechanism is shown directly, and the frozen wording ("bare hex token") is what
makes 55 correct.
