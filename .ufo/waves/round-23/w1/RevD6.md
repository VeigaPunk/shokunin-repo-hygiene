# RevD6 — routed defect D6, verified independently

## Status

STATUS: PARTIAL — D6 is **real and open** at the lane base (`1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`): the
lesson Gate's reject reason is false on the candidate's own bytes. But this round's wave-1 spec contains **no
repair of that Gate** — no seat writes `corpus/lessons/round-22.md`, and `ScribeLesson` is explicitly told
`Do not edit corpus/lessons/`. As specified, the round *records* D6 and leaves the false reason standing, so it
does not close the defect. The minimal repair is 5 lines in one lane-owned file and is stated below with a
closure command that already fails at base (`rc=1`) and a filed-evidence guard that passes at base (`rc=0`).

## Evidence

**1. Reproduction — one command, run at base (`HEAD` = `1208bfb`, tree clean for both target files).**

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1208bfb:corpus/lessons/round-22.md | sed -n '337,341p'; \
grep -nE 'EXCHANGE|WHITEOUT|atomic swap|8 paths|Every writable mount' \
  /home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r24.md
```

Output:

```
- `quarantine-staging-no-copy-r24.md` → REFUSED. Reason: same primitive,
  second device list, no new refusal semantics or field, so no new
  consequence for the lane. Flip: a measurement on a filesystem or mount
  namespace the r23 entry did not cover *and* a consequence a staging tool
  would change.
--- candidate bytes ---
5:recheck: 90d — re-run `python3 fixtures/r24-renameat2-probe.py` (expect 8 paths, all ok) (ran 2026-10-23)
8:# Every writable mount implements the no-clobber rename, and so do the two flags S124 skipped
22:   `/var/tmp` (btrfs) — **8 paths, every one** with `RENAME_NOREPLACE`
24:2. **The two flags S124 omitted also work here.** `RENAME_EXCHANGE` (atomic
25:   two-path swap) and `RENAME_WHITEOUT` (the overlayfs whiteout) both
26:   **succeed** on all 8 paths. A staging tool could therefore use an atomic
34:- **`RENAME_WHITEOUT` "succeeding" is not overlayfs semantics being
38:- **The probe is a point-in-time measurement of 8 paths**, not of every
40:- `RENAME_NOREPLACE` and `RENAME_EXCHANGE` remain **mutually exclusive**
```

**2. Closure probe, run at base as the discriminating control** (same command as §"Closure proof" below):

```
rc=1
```

It fails on the first two conjuncts (`EXCHANGE` absent, `entry budget` absent) and on the third
(`no new refusal semantics` still present in the REFUSED bullet). Block-level counts at base: `EXCHANGE=0`,
`entry budget=0`, `no new refusal semantics=1`.

**3. Filed-evidence guard, run at base:**

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -q 'no new refusal semantics' HEAD -- corpus/lessons/round-22-verifier-spotcheck.md; echo rc=$?
rc=0
```

The phrase legitimately stands in the non-author spot-check (line 168) — it must survive the repair.

**4. Not closed at base.** `git status --porcelain -- corpus/lessons/round-22.md corpus/knowledge/quarantine-staging-no-copy-r23.md`
returns empty; base blobs `f892c91504249ad4a20f39ab665e5d189d485a67` (lesson) and
`a878a6d9eb1758f7351522a69666352adfd4f663` (r23 entry).

**5. Candidate bytes.** `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r24.md`,
`sha256 109a2a6bed4e594c4b3d89bf0b93e5912ee0a80a64d405f9dd6fab7e3d658e0e`, **47 lines** (the spot-check says 64).

**6. Probe receipt behind the candidate.** `/home/vgpnk/Projects/shokuknow/lanes/souji/round3/evidence/r24-renameat2-probe.out`,
`sha256 a53f1e301d0c6969d589f9071b8a3bac9db8f6e1d3ebbb0ace42c300904b0809`; line 2 `writable mounts probed: 8`; rows 3-10 are
8 `(path,fstype)` rows — `/fast` appears twice (btrfs, then xfs), so **8 rows over 7 distinct path strings**; line 11
`SUMMARY: every writable mount implements RENAME_NOREPLACE`.

**7. The entry-level wording already exists at base.** `corpus/knowledge/quarantine-staging-no-copy-r23.md:77` (Gate REJECT)
says: "it does add EXCHANGE/WHITEOUT and extra mounts, but none of that is wired to a consequence this lane's staging
plan can use", then grounds the refusal in adopting the candidate rewriting the r23 entry's own 'does not establish' list
inside the round's 1-3 entry budget. The lesson is the outlier, not the entry.

**8. This round's plan (`.ufo/waves/round-23/w1-spec.json`, 41 items; no wave-2 file exists).** Only two items mention D6:
`ScribeLesson` (items array index 18, "D6 an overbroad reject reason", deliverable a *draft* of `corpus/lessons/round-23.md`, prompt
closes with `Do not edit corpus/lessons/.`) and this reviewer item. `ScribeLog`'s correction entry is scoped to the r22
tuple, the slice tally and the D3 digest — not D6. No item names `corpus/lessons/round-22.md` as a write target.

## Findings

1. **D6 is real as stated, in substance.** The lesson's reason asserts "no new refusal semantics or field, so no new
   consequence for the lane" (`corpus/lessons/round-22.md:338-339`), while the candidate it rejects adds two flags that
   are not refusal semantics (`RENAME_EXCHANGE` atomic two-path swap, `RENAME_WHITEOUT`, lines 24-25) and itself names a
   staging consequence (lines 26-27, "A staging tool could therefore use an atomic swap"). The reason is false on the
   bytes it describes. Location: `corpus/lessons/round-22.md:337-341`.

2. **The stated flip is already satisfied by the candidate, which the spot-check does not say.** The lesson's flip asks for
   "a measurement on a filesystem or mount namespace the r23 entry did not cover *and* a consequence a staging tool would
   change" (lines 340-341). The candidate supplies both on its face: mounts `/fast` (btrfs and xfs), `/fast/scratch`,
   `/home/vgpnk`, `/run/user/1000` are outside the r23 entry's five devices (`/var/tmp`, `/home/vgpnk/Projects/shokunin`,
   `/home/vgpnk/Projects/shokuknow`, `/dev/shm`, `/tmp`), and it names the swap consequence. So the refusal is
   **self-contradictory**: it survives only on the entry budget and on r23's `mv --no-copy` fallback, never on its stated
   reason-plus-flip. D6's remedy as worded ("name the EXCHANGE/WHITEOUT delta") does not repair the flip, so a repair that
   follows only D6's sentence leaves a corrected reason contradicting its own flip.

3. **Precision defects in the spot-check's own evidence (no verdict change).** (a) The candidate is 47 lines, not 64.
   (b) "eight writable paths" repeats the candidate's label: the enumeration at lines 20-22 lists **7** distinct path
   strings and the receipt holds 8 `(path,fstype)` rows (`/fast` twice). A repair that writes "8 paths" is receipt-backed;
   one that writes "8 distinct paths" is not.

4. **The planned repair does not close D6.** A `## Mistakes` row in `corpus/lessons/round-23.md` plus a "D6" disposition in
   the `Round23` LOG entry record the mistake; neither corrects the standing false reason, and PROTOCOL.md:363 makes a
   corrected fact left standing in a file the lane touches still a defect. Nothing in the frozen counters C1-K1..K4 reads
   `corpus/lessons/round-22.md` prose, so **no counter in this round can detect the defect or its repair either way** —
   closure needs its own command (below), and the Round23 LOG disposition must not claim D6 "fixed" unless it lands.

5. **The repair must not be a corpus-wide sweep.** The superseded phrase is also quoted in
   `corpus/lessons/round-22-verifier-spotcheck.md:168` (non-author, filed evidence, not the lane's to rewrite). A closure
   predicate of the form `! git grep -q 'no new refusal semantics' HEAD -- corpus/` is unclosable without editing filed
   evidence; the predicate must be scoped to `corpus/lessons/round-22.md` while positively requiring the spot-check copy
   to survive.

6. **The target is the lesson only, not the entry.** `corpus/knowledge/quarantine-staging-no-copy-r23.md:77` states a
   scoping judgment ("none of that is wired to a consequence this lane's staging plan can use") plus the budget and the
   delta — that form is defensible and already committed. Editing it would be scope creep and would also disturb a
   `used-by` citation surface.

## Minimal repair

**File:** `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-22.md`
**Location:** `## Gate — attempt 2` (section opens at line 327), the `quarantine-staging-no-copy-r24.md` REFUSED bullet,
lines 337-341 — replace lines 338-341 (reason + flip); line 337's opening is unchanged.

**Wording constraint** (verbatim-ready; 5 lines, same bullet indentation as its siblings, no `|`, no numeric
`<n> <class>` token, ≤25-word spans so it can be quoted):

```
- `quarantine-staging-no-copy-r24.md` → REFUSED. Reason: it does add
  `RENAME_EXCHANGE`/`RENAME_WHITEOUT` and 8 probe rows (7 distinct paths over
  tmpfs, btrfs, xfs), but the r23 entry already carries the portable
  `mv --no-copy` fallback, and adopting it would rewrite that entry's limits
  list inside the round's 1-3 entry budget. Flip: a consequence that survives
  the `--no-copy` fallback *and* a filesystem class absent from the 8 rows.
```

Constraints, each tied to a committed rule or counter:
- the two ADMITTED bullets (330-336) and the Campaign bullet (342-346) stay byte-identical (PROTOCOL.md:363 sweep, not
  collateral rewrite);
- **no** `<n> <class>` token (class in {accepted, present, unverifiable, refused}) may be introduced: preregistration K3
  derives those tallies from `census/round-22/attempt2/slice-verdicts.tsv` (0 refused), so a stray "0 refused" here would
  be a second source of truth and a future K3 mismatch;
- no pipe character anywhere in the bullet (it is quoted into SOURCES/README cells elsewhere in this corpus);
- do not touch `corpus/knowledge/quarantine-staging-no-copy-r23.md:77` or
  `corpus/lessons/round-22-verifier-spotcheck.md:168`.

**Closure proof** (one command; `rc=1` at base, `rc=0` only after the repair, and it fails if anyone "fixes" the
spot-check instead of the lesson):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && \
blk=$(git show HEAD:corpus/lessons/round-22.md | sed -n '/^- `quarantine-staging-no-copy-r24.md`/,/^- Campaign/p') && \
printf '%s\n' "$blk" | grep -q 'EXCHANGE' && \
printf '%s\n' "$blk" | grep -q 'entry budget' && \
printf '%s\n' "$blk" | grep -q 'no-copy' && \
! printf '%s\n' "$blk" | grep -q 'no new refusal semantics' && \
! git grep -q 'no new refusal semantics' HEAD -- corpus/lessons/round-22.md && \
git grep -q 'no new refusal semantics' HEAD -- corpus/lessons/round-22-verifier-spotcheck.md && \
echo 'D6-CLOSED rc=0'
```

## Achievability, and the append-only alternative

The repair is achievable without touching filed evidence or operator files: `corpus/lessons/round-22.md` is lane-owned
(CORPUS.md:53-56, "Lanes own `lessons/round-<N>.md`"), it is not a filed *report* (PROTOCOL.md:134-137's erratum rule does
not bind it), it is not an append-only file in the sense PROTOCOL.md:124 gives `LOG.md`, and it touches no frozen counter
key (K1-K4). D4's own remedy in the same spot-check prescribes exactly this in-place form for `corpus/README.md` and the
lesson.

If the L1 reads CORPUS.md:53 ("Corrections are new entries, never rewrites") as barring in-place edits even for the owner,
the append-only route is available and has house precedent in the same file: `## Attempt 2 — seat-driven corrections
(M17–M21)` at line 382 and `## Attempt 2 — claims-level corrections (M22–M23)` at line 437. Append, at EOF (after line
460), a block in that style — `## Attempt 2 — routed-defect correction (D6)` — whose bullet names the superseded sentence
verbatim ("no new refusal semantics or field, so no new consequence for the lane"), the corrected entry-level reason, the
`*Captured-by:*` criterion and a `*Flip:*` that is not already met. Under that route the closure command's Gate-block
conjuncts are replaced by: the block exists, it quotes the superseded sentence, and it carries `EXCHANGE`, `entry budget`
and `no-copy`. The append-only route is weaker on one point — PROTOCOL.md:363 still counts a corrected fact left standing
in a touched file as a defect — so in-place correction of the Gate is the recommended minimal repair.

## Attack log

Not an attack item; no predicate, target or key set is proposed for change. One scope observation for the L1, not an
attack: C1's frozen key set (K1-K4) was fixed for D1/D2/D4/D5 only, so **D6/D7/D8 have no counter**. The honest form is
the Round23 LOG disposition plus this report's standalone closure command — not a claim that a green C1 implies D6 landed.

## Bounds observed

Read-only throughout; no `git add/commit/push/checkout/stash`, no `jj`, no `rm`/`mv`, no signals, no lane state created.
Files read outside the lane: `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/…` (candidate) and
`/home/vgpnk/Projects/shokuknow/lanes/souji/round3/evidence/r24-renameat2-probe.out` (cited receipt), plus the fleet
`CORPUS.md`/`PROTOCOL.md` rules — reads only. No scratch directory created. **No tool installs or upgrades**; no pacman
transaction (host-wide pause respected). Certification OFF, K5 HELD, F5 reap and NAMESPACE holds untouched.
