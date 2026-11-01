# souji round 47 — non-author closure verifier spot-check

author: hyaku closure (non-author integrator, zcode subagent (fresh session, non-author))

Closed 2026-11-01T07:03Z against lane tip `04b5e319322543c77472149973adb2cb47804764`
(branch master, pushed), round base `e469084b6b5630d0c248574fdd980775deeb1efd`.
Index-free git only (`rev-parse`, `cat-file`, `ls-tree`, `diff-tree`,
`merge-base --is-ancestor`, `show`, `log`, `ls-remote`); no `git status`, no
mutating command anywhere; no lane-authored file edited.

## 1. Step-1 conformance — PASS

- Report committed in the fleet repo by the lane identity:
  `git -C <fleet> log --format='%an <%ae> %H %cI' -1 -- .ufo/reports/round-47/souji.md`
  → `souji-shokunin <souji@shokunin.local> d68d8860fa3a73db669f0f534a0bc9738c7b21b4 2026-10-31T23:42:08-07:00`.
- `SHONEN` heading present in the report: `## SHONEN`, one `[~]` line per box
  (4 boxes) with resolvable evidence pointers; box 1 discloses "no named
  outside promotion verifier". Not a marker: work performed, evidence
  pointers, landed changes tied to LOG entries, before→after with counting
  commands, Sources & frontier, and trend verdicts are all present.
- Cited lane commits exist and are ancestors of master
  (`merge-base --is-ancestor <h> refs/heads/master`):
  `0027c977452e…` OK, `08646f362cf5…` OK, `04b5e3193225…` OK (tip);
  cross-cited `32f48da04846…` OK, base `e469084b6b56…` OK.
- Pushed: `git ls-remote origin refs/heads/master` = local `refs/heads/master`
  = `04b5e319322543c77472149973adb2cb47804764`.
- Round work reachable from `e469084b..04b5e319`; exactly three lane commits,
  all authored `souji-shokunin`:
  freeze `0027c977` 2026-11-01T04:36:24Z, content `08646f36` 05:52:24Z,
  end receipts `04b5e319` 06:34:22Z.
- Dispatch/complete digest: launch 2026-10-31T20:59:31-07:00
  (= 2026-11-01T03:59:31Z), complete 23:42:08-07:00 (= 06:42:08Z). All three
  lane commits and the report commit sit inside the window; commit-before-
  report ordering holds (last lane commit 06:34:22Z < report commit 06:42:08Z).

## 2. Fresh-start preregistration — LEGITIMATE (freeze genuinely preceded after-data)

- Commit order + timestamps: freeze `0027c977` (04:36:24Z) < content `08646f36`
  (05:52:24Z) < end receipts `04b5e319` (06:34:22Z); dispatch precedes all
  (03:59:31Z).
- The freeze commit touches ONLY pre-data artifacts:
  `preregistration.txt`, populations `c1-items.tsv` + `c2-targets.tsv`,
  counter `c2-counter.py`, BOTH do-nothing controls
  (`controls/c1-control-donothing.txt`, `controls/c2-control-donothing.txt`,
  both ending `EXIT=1`) plus red partial/junk arms (`c2-partial.tsv`,
  `c2-junk-safe.tsv`), before-census, NTFS base receipt, S270 quote capture.
  No after-data (per-artifact receipts, correction rows, tip receipts,
  census-after) exists before the later commits — verified from
  `diff-tree --name-status` of each commit.
- Digest pins: all four `sha256=` values in the frozen preregistration match
  the committed blobs exactly (c1-counter.py `5455fb46…`, c1-items.tsv
  `5e15b8f0…`, c2-counter.py `6abdb1d7…`, c2-targets.tsv `c19cbd61…`).
- Frozen bytes unchanged freeze→tip (`diff-tree -r` over
  preregistration/populations/counter/controls: empty).
- Verifier's own re-run of the freeze grammar tool (read-only, git
  object-store only, stdlib; run from the lane repo with worktree bytes
  sha256-verified equal to the committed bytes first):
  `python -B tools/souji-freeze-check.py --root . --prereg census/round-47/preregistration.txt --rev 0027c977…`
  → `SUMMARY claims=2 findings=0`, rc 0; same at `--rev 04b5e319…`, rc 0.
- The frozen text itself discloses the pre-freeze feasibility probes (three
  souji-verify repo-root verdicts + one helpers-r74 probe) and that all four
  claim receipts were re-taken post-freeze. Honest preregistration.

## 3. Per-claim re-check

### C1 — calibration (lowest non-retired axis, 7): RE-MEASURED (+ counter receipts evidence-verified)

- `git show e469084b:SCORECARD.md | grep -c "^R46-CORRECTIO[N]"` → `0` (rc 1);
  at tip `04b5e319` → `3` (rc 0). Matches the reported 0 → 3.
- Append-only: base SCORECARD (173,108 bytes) is a byte-prefix of tip
  (`head -c` + `cmp` → PREFIX-OK); `diff-tree --numstat` = 47 added, 0 deleted.
  The `assertions=522` literal goes 1 → 2 (stale cell stays; the correction
  row names it) — consistent with append-only correction, no rewrite.
- The three R46-CORRECTION rows carry receipt-backed values and resolvable
  revisions; all citations resolve: `census/round-46/records/c1-tip-green.txt`
  at `32f48da0` (ancestor-verified) prints `SUMMARY assertions=533 …
  unfiled=0 instrument_sha256=a3324916…`; the r46 non-author verifier
  spotcheck §3 independently re-derived 533; W04 erratum (56→57) matches
  `grep -c W04 census-before.txt` = 57; the before-census citation correction
  matches the two committed receipts (conf-name rc 2, explicit-dir rc 0).
- Standing counter: evidence-verified from the committed receipts, NOT
  executed by this verifier — `census/round-46/c1-counter.py` reads
  `git status --porcelain` internally (the known-garbage surface on this
  host), so the gate standard's committed-evidence path applies:
  `records/c1-base-green.txt` (in the freeze commit) = base `e469084b`,
  `SUMMARY assertions=533 mismatches=70 … unfiled=0`, rc 0;
  `records/c1-tip-47.txt` = content tip `08646f36`,
  `SUMMARY assertions=538 mismatches=70 … unfiled=0`, rc 0 (+5 new
  assertions from the appended section, mismatches steady at 70, unfiled=0).
  The receipt is taken at the content tip, which is valid for the final tip:
  `diff-tree 08646f36 04b5e319 -- SCORECARD.md` is empty (SCORECARD bytes
  final at the content commit), exactly as the receipt header and report
  state.
- Freeze-grammar leg: RE-MEASURED by this verifier (freeze-check at both
  revisions, findings=0 — section 2 above).

### C2 — coverage (8): RE-MEASURED (+ independent predicate re-derivation)

- Base do-nothing control: `git cat-file -e e469084b:census/round-47/records/per-artifact-receipts.tsv`
  → rc 128 ("exists on disk, but not in …"), matching the frozen control arm.
- Verifier's own run at the tip (read-only, object-store only):
  `python -B census/round-47/c2-counter.py --root . --rev 04b5e319…`
  → `RECEIPTS rows=4 targets=4 findings=0`, rc 0; no-rev guard exits 2 as
  declared.
- Independent re-derivation over committed bytes without the lane's counter
  (awk over `git show 04b5e319:…receipts.tsv`): exactly 4 `VERDICT` rows;
  target path set equals the frozen `c2-targets.tsv` population exactly;
  all four verdicts `NOT-SAFE`; classes `secrets-refusal`/`dirty`/`none` in
  the declared taxonomy; evidence fields nonempty.
- Provenance: sha256 of `tools/souji-verify.sh` at the content commit =
  `e6cb3f9340f0ac8b51e052ed73e3b9293e8ff2ff408ef97ba7b9562fda51691f`,
  matching both the receipts TSV header and `records/receipt-commands.txt`;
  unchanged at the tip (tool not touched after the repair).

## 4. Conservation spot-check (the round's NOT-SAFE claim) — T2 shokunin-binary-forensics: AGREE

- Target exists and is a git repo; the tool verdict recorded
  `NOT-SAFE dirty unpushed=0 dirty=153` at receipt time.
- Conservation: `git log --author=souji` over ALL history in each of the four
  targets (kotodama-shokunin, shokunin-binary-forensics,
  shokunin-reverse-engineering) → ZERO commits; `helpers-r74/` exists with
  no `.git` (foreign root confirmed). Nothing moved, deleted, or proposed
  for removal by this round.
- The target repo's HEAD did move during the round window (`c9f490cd` →
  `3e980481`) — entirely from OTHER lanes' own work inside that window
  (revenger-shokunin r74–r76 landings 03:09–06:01Z, protocol-shokunin
  verifier spot-checks), which is precisely the growth the round disclosed
  ("dirty 131→150→153 across the round's three observations; live unpushed
  work confirmed by real diffs"). The r46 `HEAD=` values in the frozen
  population are census-evidence snapshots, not frozen-HEAD promises; the
  receipts record r47-time live state. Disclosure accurate; verdict honest.
- The other three verdicts were re-derived for shape from the committed TSV
  (section 3) and their targets verified present; T2 was the deep spot-check.

## 5. Mined mistakes — both honest, both fixed this round

- **Row 1 (host index drift).** The lesson names exactly what was touched:
  ONE index entry (`corpus/lessons/round-46-verifier-spotcheck.md`) via
  `git update-index --add --cacheinfo 100644,2162b581dc05f0075a8a0e61e57638576c6aeb1f,<path>`
  after sha256-verifying worktree bytes identical to the HEAD blob;
  "No content change, no commit touched". Byte-level truth confirmed:
  `ls-tree e469084b -- <path>` → blob `2162b581…` (the cacheinfo id);
  worktree file sha256 = HEAD blob sha256 = `0d1a4721…`;
  `git hash-object` of the worktree file = `2162b581…`. The repair put the
  HEAD blob's id into the host index for one named path and nothing else;
  the frozen tolerance (exactly six control-char-named staged deletions) is
  the documented precondition the drift had broken. Honest.
- **Row 2 (find_repo_for spin).** `records/t4-spin-probe.txt` isolates the
  root cause (MSYS `dirname` bottoms out at `.`; the loop breaks only at
  `/`) with per-level `-e` probes ruling out filesystem blocking. The repair
  is committed in `08646f36` with the T4 receipt it enables; consumer checks
  verify: `verify-selftest-base.txt` vs `verify-selftest-repaired.txt` are
  line-for-line identical (same PASS/FAIL/SKIP structure, 47 checks, the
  same 8 pre-existing host failures — F6, E6, 6×R9) except scratch dir names
  and random fixture hashes, exactly as reported. The registered
  r17-jj-receipts gate is could-not-evaluate on this host because its
  fixture hard-codes `/var/tmp` (`records/r17-jj-receipts-repaired.txt`) —
  environment-level, disclosed, same for base bytes. The frozen
  preregistration text is unchanged (freeze-check findings=0 at tip).

## 6. Discernment spot-check (non-author, from outside)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S270 git-clone(1) | admit (tier A, docs, naming scope) | https://git-scm.com/docs/git-clone re-opened live 2026-11-01 (HTTP 200) | AGREE | The 18-word quote is verbatim in DESCRIPTION ¶1; the page genuinely never mentions `refs/remotes/origin/HEAD`; the anchor cell ("last updated in 2.54.0" with "2.55.0 → 2.56.0 no changes") matches the live page exactly. Tier A for the naming scope is right. |
| S270 scoping refusal | reject-analogue (S270 must NOT ground the verdict half / default-ref resolution) | same live page | AGREE | The page documents remote-tracking NAMING only; grounding tool verdicts or `origin/HEAD` resolution on it would over-read the source. The lane's limit note is correct and is recorded in the row, lesson, and capture file. |
| No reject rows this round | negative claim | `diff-tree e469084b 04b5e319 -- corpus/SOURCES.md` | AGREE (verified) | The SOURCES diff is exactly the S270 row + a provenance line; no existing row's status/recheck/used-by changed and no rejected row was filed. The round-47 Gate's "no rejections" state is true; no reject sample existed to re-open beyond the scoping refusal above. |

Census duty: the contract's conf-name command
(`sources-census.sh validate --root <fleet> souji`) exits rc 2 on this host
("souji missing" — the `souji-shokunin/` path is absent here, the r46
PROVINCE host correction the lane discloses). The explicit-lane-directory
form the round used —
`sources-census.sh validate --root <fleet> <lane-repo-dir>` — exits rc 0,
`shokunin-repo-hygiene ok`, matching the committed `census-after.txt`
receipt (58 W04, the +1 being S270 itself; 193 → 194 rows verified by the
contract grep at base and tip). Exit 0 held at round end in the working
form. S270's ≤25-word quote: 18 words, verified.

## 7. Per-axis verdicts and trends

| axis | verdict | evidence |
|---|---|---|
| calibration | improved | C1 verified (re-measured): 3 receipt-backed append-only corrections close the three routed r46 record defects; the axis's own observable (SCORECARD entries match repo state) measurably improved. Numeric score honestly unchanged at 7 with the bookkeeping distinction recorded (r22 precedent). |
| operability | unchanged | No claim on this axis. The souji-verify termination repair is enabling work: behavior-preserving by the identity receipts, no score move claimed, none warranted. |
| coverage | improved | C2 verified (re-measured + independent predicate): the four r46 census candidates now carry per-artifact raw-tool receipts — the mission's receipt surface, not just census labels. Score honestly unchanged at 8, disclosed. |

No axis harmed; both claims verify; not exploratory (no exploratory claim
declared; none needed).

Trends (agreed with the lane's verdicts, verifier-checked):
- **expansion: unchanged** — no knowledge entry, no Core promotion, no
  capability row (`capabilities_added=[]`); one sourced row (S270) on
  existing receipt ground; SOURCES 193 → 194 verified.
- **quality: unchanged** — no admitted entry re-verified or superseded; the
  tool repair is behavior-preserving by committed identity receipts.
- **discernment: improved** — two real mistakes mined with receipts and
  executed same-round fixes; control-first freeze with red do-nothing
  controls; fresh-start rulings derived from r43/r44/r45 and recorded; the
  self-reference trap in the counting command (marker literal in the
  measurement table) avoided via the `[N]` class.

## 8. Conformance notes (status-neutral) and routed items

1. The closure contract's census command names the conf form (`souji`),
   which exits rc 2 on this host; the lane's explicit-lane-directory form is
   the working one (rc 0). Contract-vs-host mismatch for the operator to
   note; the lane disclosed it and committed both receipts (conf-name rc 2
   at `records/census-conf-name-host.txt`, explicit-dir rc 0 at
   `records/census-before.txt`). Not a lane defect.
2. The round-47 `## Gate` files no explicit reject row. Verified true (no
   SOURCES cell changed); the scoping refusal was sampled as the
   reject-analogue. CORPUS.md requires reject rows when rejections exist —
   none existed this round. Status-neutral.
3. `records/c1-tip-47.txt` is measured at the content tip `08646f36`, not
   the final tip: valid, because SCORECARD bytes are byte-identical
   content→final-tip (verified) and the receipt header states it.
4. SHONEN.md: 4 boxes, all `[~]` with resolvable pointers, byte-untouched
   this round. The boxes look fully checkable by a non-author (SKILL.md
   tables + corpus, LOG end-to-end entries, re-derivable receipts, PROVINCE
   accuracy) — flagged for the operator as a candidate promotion review.
   This verifier wrote no `[x]` (never self-attest, never promote).
5. Standing operator-owned L0 carried (routed around, nothing assumed
   answered): r44 symlink-contract disposition, r46 L2-floor disposition
   (no dispatch surface on this host; dispatched=0 again), r46
   staged-package disposition. r17 gate could-not-evaluate on this host
   (fixture `/var/tmp` uncreatable) — environment-level, named limit.
6. Defects routed to the lane for next round: none new. The lane's own
   planned r48 items (dispositions for the four receipted artifacts,
   standing receipt re-runs, census in the working form) stand as written.
