# CritSourcedClaim — §2b sourced-claim verification (round 26, C2)

## Status

STATUS: FAIL — the ticket's specific hypothesis is **disproved** (no landed row reuses the
campaign date; all five new rows read `opened=2026-10-25`), but the §2b sourced claim is
still unsupported as landed: the frozen K2 gate that adjudicates it is RED at the tip
(`entries=2 ok=0 fail=2`, exit 1, both `check1-no-gate`), the §2b attestation (lesson Gate:
URL + access date + ≤25-word located quote per new row) was dropped between the wave drafts
and the landing, and two prereg-mandated receipts do not exist. C2's own kill rule
(`K2 exit != 0 or ok != 2`) is met.

Axes impacted: coverage (the claim C2 delivers) and calibration (a red gate recorded green
in a commit message). Operability untouched.

## Evidence

Read-only observations. Lane HEAD at the K4 run: `ba8b54b85814dd980aa96050fe111c7cbfd4956a`;
`git diff --stat HEAD -- corpus/` empty, so the corpus bytes below are the committed bytes.

1. Landed `opened` cells — all five rows carry the lane's re-open date, not the campaign's:

   ```
   $ awk -F'|' 'NR>=149 && NR<=153 {gsub(/^ +| +$/,"",$2); gsub(/^ +| +$/,"",$10); print $2" opened=["$10"]"}' corpus/SOURCES.md
   S128 opened=[2026-10-25]   S129 opened=[2026-10-25]   S130 opened=[2026-10-25]
   S131 opened=[2026-10-25]   S132 opened=[2026-10-25]
   ```

   Location: `corpus/SOURCES.md:149-153` (landed in `0833de9`).

2. Staged package still carries the campaign date, correctly **not** copied:

   ```
   $ awk -F'|' 'NR==7||NR==8||NR==9||NR==21||NR==29{...}' /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md
   S109 opened=2026-10-23  S110 opened=2026-10-23  S111 opened=2026-10-23  S123 opened=2026-10-23  S131 opened=2026-10-23
   ```

   Draft artifacts keep `2026-10-23` only where they reproduce staged bytes verbatim
   (`.ufo/waves/round-26/w1/sources-append-block.md:39-51`, `renumber-map.md:14-18`), and
   `renumber-map.md` §3 records the intended flip: "`opened` 2026-10-23 -> 2026-10-25
   (re-opened this round)".

3. Frozen K2, exact prereg command, at the tip — red:

   ```
   $ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
       --entries corpus/knowledge/git-auto-maintenance-trigger-set.md \
                 corpus/knowledge/git-auto-maintenance-trigger-set-r23.md \
       --snapshot-dir census/round-26/sources \
       --slice census/round-26/records/empty-slice \
       --slice-verdicts census/round-26/records/empty-verdicts
   FAIL corpus/knowledge/git-auto-maintenance-trigger-set.md check1-no-gate: ...
   FAIL corpus/knowledge/git-auto-maintenance-trigger-set-r23.md check1-no-gate: ...
   entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2
   EXIT=1
   ```

   Prereg after-literal is `entries=2 ok=2 fail=0`, exit 0 (`preregistration.txt:105-108`).

4. Same command against the wave-1 drafts — green, proving the predicate is satisfiable and
   the red is a landing regression:

   ```
   $ python3 -B tools/souji-gate-check.py ... --entries .ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md \
       .ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set-r23.md ...
   entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0
   EXIT=0
   ```

5. The Gate blocks exist only in the drafts. `grep -n '^## Gate'` →
   `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md:111`,
   `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set-r23.md:102`; the landed
   entries have headings Claim / What this does NOT establish / Lane link and consequence /
   Freshness only. Sizes: landed 67 and 92 lines vs drafts 122 and 111.

6. Lesson `## Gate` carries no §2b material. `sed -n '8,27p' corpus/lessons/round-26.md |
   grep -nE 'https?://|2026-10-2[0-9]|"'` → `NONE: no URL, no access date, no quoted bytes
   in Gate`. The Gate names rows with paraphrase only ("S128 (`git-fetch(1)` § OPTIONS
   switches)"). By contrast the conforming r25 shape carries per-row URL, access date,
   snapshot and word-counted quote, e.g. `corpus/lessons/round-25.md`:
   "ADMIT SOURCES S124 — https://git-scm.com/docs/gitrepository-layout § commondir,
   accessed 2026-10-25." Lands 23-word quote after it.

7. No round-26 provenance paragraph in the registry header: provenance paragraphs exist for
   r13/r14/r16/r17/r18/r19/r25 only (`corpus/SOURCES.md:5-16`), `## Registry` begins at `:18`.
   Round 26 is the first round since r25 to open rows and the only one to leave the header
   silent.

8. Receipts the prereg names are absent. `find . -name 'c2-gate*' -o -name 'c2-k4-after*'`
   → no output. Prereg `:142-143` requires `c2-k4-after.tsv` and "a gate-check receipt
   c2-gate.tsv (K2)", each `verify=ok`.

9. K4 does pass at the tip, so only its receipt is missing:

   ```
   $ python3 -B tools/souji-coverage-agreement.py --root . --rev ba8b54b85814dd980aa96050fe111c7cbfd4956a \
       --base-rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd
   grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0
   EXIT=0
   ```

10. `census/round-26/records/c2-before.tsv` was rewritten after after-data. At `89e0fce` it
    read `rev=12fd90bcd9cdfab495e178023eeaa838a977fcbe` (the freeze commit) and
    `utc=2026-10-25T17:06:11Z`; at `d6c13b0` (14:30:04, after the `0833de9` append at
    14:27:56) it reads `rev=89e0fceeefcf28db313c94120be6d25e03c60094`,
    `utc=2026-10-25T17:29:54Z` — one second before the after run at `17:29:55Z`.

11. The re-open itself is real and byte-verifiable: snapshots fetched 14:19-14:20 local and
    committed in `0833de9` (14:27:56), i.e. after r25's landing (`728b2ce` 10:25:55,
    `a877325` 10:38:15); all seven digests verify against
    `census/round-26/sources/SHA256SUMS`. Campaign own-work digests computed read-only this
    run match the cited prefixes: fixture `11c136aa71066733d50d226d`, prune evidence
    `510722c11a97f6bca8f93e49`, census `1ac71c4f7199a134c204b45f` under
    `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/`. Filed mtimes remain 2026-10-23.

## Findings

1. **The `opened`-cell check passes, contrary to the ticket hypothesis.** All five landed
   rows (`corpus/SOURCES.md:149-153`) carry `2026-10-25`; no landed row reuses the campaign
   date `2026-10-23`. Two traps this check must survive, both cleared: r25 rows also carry
   `2026-10-25` (so the cell alone cannot discriminate rounds — the discriminating evidence
   is the snapshot commit/mtime and the campaign digests, Evidence 11), and the staged rows
   reproduced verbatim inside draft files do carry `2026-10-23`
   (`sources-append-block.md:39-51`, `renumber-map.md:14-18`) — those are staged-input
   reproductions, not append candidates, and `renumber-map.md` §3 prescribes the flip.

2. **C2's frozen K2 is red at the tip, which is a kill-rule hit.** Evidence 3. Cause: both
   admitted entries lost their `## Gate` section on landing. The prereg's K2 after-literal
   cannot be reached by the landed bytes.

3. **The §2b attestation was dropped in the entry→lesson handoff.** Landing kept a pointer
   instead of the block (`corpus/knowledge/git-auto-maintenance-trigger-set.md:52`: "this
   round — see `corpus/lessons/round-26.md` `## Gate`") and the pointed-at Gate contains no
   URL, no access date and no verbatim quote (Evidence 6). The drafts hold the exact
   material the contract asks for, so this is a lost-content defect, not an unavailable
   source.

4. **The registry header has no round-26 provenance paragraph** (Evidence 7), so the only
   assertion that S128-S132 were opened this round is the `opened` cell plus a lesson Gate
   that omits the attesting quote. The r13-r25 convention is the provenance paragraph plus
   the Gate; r26 has neither of the two in conforming form.

5. **Two prereg-mandated receipts do not exist**: `census/round-26/records/c2-gate.tsv` (K2)
   and `c2-k4-after.tsv` (K4), both required by `preregistration.txt:142-143`. K4 passes at
   the tip (Evidence 9), so only the record is missing; K2 has no green record to produce.

6. **The red-before receipt was overwritten after the data landed** (Evidence 10). The
   literal is still honest (`grounded_f1=0`, `registry_rows=127` at a pre-data rev), but the
   prereg's "committed BEFORE after-data" property is destroyed and the original pre-data
   receipt is no longer the tip's bytes. This is the same class as the round's mined mistake
   (target/receipt captured from the wrong state) and is currently uncaptured.

7. **The prepared fix material carries a false locator.** `.ufo/waves/round-26/w1/gate-draft.md`
   locates the S132 quote at census `:28-29`; those lines are "`--- post-check: nothing was
   pruned ---`" and "`worktree list count after: 5`". The quoted text is at
   `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out:31-32`
   ("today: 0 prunable, 0 locked, 5 registrations ... 3-month expiry)"). Landing that
   locator as-is would put a wrong line reference inside the Gate — a located quote whose
   location is wrong.

## Attack log

- **Hypothesis tested (ticket): "rows opened this round are actually campaign-dated."**
  Disproved: Evidence 1, 2, 11. No row keeps `2026-10-23`.
- **Strongest available counterexample to the claim actually being sourced:** take the
  claim's own adjudicator and run it verbatim — K2 red at the tip (Evidence 3) while it is
  green on the drafts (Evidence 4). The `opened` cell is correct and the row is still
  unattested, because the attestation block never landed. A green `opened` cell and a red
  gate are consistent: the cell is the claim's premise, the Gate is its evidence, and the
  evidence is what went missing.
- **Self-proof attack on `opened=2026-10-25`:** r25 (S124-S126) shares the date, so the cell
  cannot be cited as its own proof of "this round". The surviving discriminators are
  snapshot fetch time/commit order and the campaign digests; both hold (Evidence 11). The
  claim may rest on the rows, but the report must not present the cell itself as the proof.
- **Duplicate-authority check:** three plausible homes for the attestation (entry `## Gate`,
  lesson `## Gate`, registry provenance paragraph) and none holds it; the entry's pointer
  resolves to the lesson Gate, which is the one that omits it. This is a single point of
  loss, not redundancy.
- **Premature-saturation check:** K4's after-literal is met at the tip with the amendment-1
  numbers (`grounded=9`, `kill_tested=7`), so the claim is not gated by the coverage map;
  the only blockers are the entry Gate, the lesson Gate/provenance record, and the two
  receipts.

## Smallest safe correction (L1 only; no predicate, target, case set or axis changes)

1. Restore the two `## Gate` blocks from the w1 drafts into the two `corpus/knowledge/`
   entries (`entry-...trigger-set.md:111`, `entry-...trigger-set-r23.md:102`). This re-lands
   content already drafted this round from already-committed snapshots — no new source
   access. Then run the frozen K2 command and commit `census/round-26/records/c2-gate.tsv`.
2. Land the lesson Gate and the registry provenance paragraph from the already-drafted
   `gate-draft.md`, **after** fixing its S132 locator to `:31-32` (Finding 7). Then run the
   frozen K4 command and commit `c2-k4-after.tsv`.
3. Restore `c2-before.tsv` to the `89e0fce` blob rather than leaving the post-data rewrite,
   and log the overwrite in `## Mistakes` (class: receipt rewritten after data; captured-by:
   append-only/hash check on committed receipts; fix: the check).
4. Until 1-2 land, score C2 FAIL under its own kill rule and record that the round has no
   §2b sourced claim; do not report K2 green.

## Limits

- Read-only seat: this report is the only file written. No `git add/commit/push/stash/
  checkout/reset`, no `jj`, no deletion, no signal. Read-only `git log/show/diff/status/
  rev-parse` and `sha256sum` against the campaign tree only.
- The terrain moved while this seat read (HEAD advanced `ea0bbe6` → `07f83e6` → `d6fe8a1` →
  `ba8b54b`); every measurement above is bound to the revision named with it, and the corpus
  bytes were unchanged across those commits (`git diff --stat HEAD -- corpus/` empty).
- No tool install or upgrade was needed; no pacman transaction was attempted. No scratch
  directory was created.
- The K2/K4 runs used the committed tools at the tip and wrote nothing
  (`tools/souji-gate-check.py` documents "Read-only; no writes anywhere").
