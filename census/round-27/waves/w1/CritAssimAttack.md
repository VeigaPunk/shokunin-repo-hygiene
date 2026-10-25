# CritAssimAttack — C2 assimilation compliance vs addendum §10

Seat: CritAssimAttack (critic, read-only) · round 27 w1 · lane souji-shokunin
Contract read: `.ufo/waves/round-27/preregistration.txt` (frozen; C2 at line 7) and
`scripts/hyaku/lane-addendum.md` §10 (lines 300–405).
Plan audited: `.ufo/waves/round-27/w1-dispatch.json` task prompts (79 tasks; C2-relevant
seats: ConnSources, ScoutRows152210211, ScoutGlibFetch, ScoutKnowledgeDrafts,
ScoutSliceReopen, ExecC2GateCheck, ExecAssimMirror, ExecRowsNormalize,
ExecKnowledgeWriter, ExecKnowledgeMechanism, RevC2Entries, RevC2Rows, RevC2Mirror,
MutC2Rows, LabCensusProbe, LabSliceFetch, ScribeLessonGate, ScribeSOURCES,
ScribeReport, ScribeFrontierNotes).

## Status

STATUS: PASS — all seven addendum §10 assimilation requirements are covered by the wave
plan; evidence for the id-collision proof is genuine and reproduces byte-for-byte; no hard
violation found. Three obligations are unowned or under-specified (attack log A1–A3) and
one execution-time risk is flagged (A4); none voids the claim.

## Evidence

- Collision proof rerun (exact §10 command, 0–3-space pattern) in scratch `/var/tmp/souji-r27-CritAssimAttack`:
  - `grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' <lane>/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort > reg-ids`
  - `grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' <shokuknow>/merge/souji/SOURCES.append.md | grep -oE 'S[0-9]+' | sort > staged-ids`
  - `comm -12 reg-ids staged-ids > collisions`
  - Output: `REG: 132 STAGED: 134 COLLISIONS: 24`; `diff collisions lane-evidence` → identical; reg-ids and staged-ids also match `.ufo/waves/round-27/assimilation/` byte-for-byte. Collision set = S109–S132.
- Frozen before-counters (measured): registry rows `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` = 132; `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l` = 2 (files: quarantine-staging-no-copy-r23.md, quarantine-origin-record-fields-r24.md) — matches prereg 132/2.
- Staged rows S152/S210/S211 defects (from `merge/souji/SOURCES.append.md`): S152 embeds escaped `\|` inside cells (`O_CREAT\|O_EXCL`; python `|`-split yields 15 columns vs 11); S210 and S211 carry prose + inline `curl` command in `recheck` (not ISO/cadence), a `grep` expression in `used-by`, and `opened` 2026-10-24 (campaign date). Confirms append-as-is would break census parse (requirement 5 is real).
- Souji quarantine slice (absent-defect-register.md): 8 data rows — S114, S123, S124, S126, S131, S133, S138 (payload-absent) and S118 (prose unreachable class). r24 `census/round-24/records/slice-verdicts.tsv` already carries a verdict for all 8 (all accepted, with notes).
- Draft `w1/origin-record-writer-r27.md` already contains `## Gate` with 7 ADMIT located quotes (snapshot sha256 66b588c4…, opened 2026-10-25) + 1 REJECT of staged S119 (reason+flip). `w1/c2-gate.sh` wires `--slice`/`--slice-verdicts census/round-27/records/slice-verdicts.tsv`.
- `ScribeReport` task explicitly names a "Sources & frontier" section in the report outline; `ScribeFrontierNotes` drafts F4 `next` lines.
- `ExecKnowledgeMechanism` task text (full, untruncated) ends: "Include a `## Gate` section with >=1 admit and >=1 reject (with reason+flip) from the staged set."

## Findings

1. Requirement 1 (id-collision proof as wave evidence, exact comm command, 0–3-space pattern) — **covered, evidence genuine**. Files `.ufo/waves/round-27/assimilation/{reg-ids,staged-ids,collisions}` reproduce the exact §10 command byte-for-byte (0–3-space pattern included). RevC2Mirror is tasked to confirm `comm -12` with the 0–3-space pattern and the full S109–S132 set; LabCensusProbe proves the indented `  | S210 |` fixture yields nonempty collisions. Gap: nothing records the command string/pattern itself in the evidence, and the §10 "paste both id lists, collision count and renumber map into the report" step is not assigned to any seat (ScribeReport's prompt does not name it).
2. Requirement 2 (quarantine slice reporting, verdict per row) — **covered**. 8-row slice; all 8 have r24 verdicts; ScoutSliceReopen re-derives and fresh-verdicts changed/new rows; LabSliceFetch probes S114/S118/S126/S138 reachability (own-work rows S123/S124/S131/S133 are lane-internal and skipped); verdicts land in `census/round-27/records/slice-verdicts.tsv` consumed by ExecC2GateCheck. Acceptable as long as ScoutSliceReopen emits all 8 rows (carry-over counts as a verdict).
3. Requirement 3 (≥1 admit AND ≥1 reject per Gate block) — **covered in plan; writer draft already meets it**. Writer entry: 7 ADMIT + 1 REJECT (staged S119, reason+flip). Mechanism-set prompt mandates ≥1 admit + ≥1 reject from the staged set (draft not yet delivered). ScribeLessonGate adds reject candidates to the lesson Gate.
4. Requirement 4 (re-grounding from our own fetch; campaign `opened` dates prove nothing) — **covered in plan**. ScoutGlibFetch fetches GLib 2.84.0 `gio/glocalfile.c` + `glib/gfileutils.c` with sha256 and located ≤25-word quotes; drafts carry `verified-at: <today ISO>` and snapshot sha256; RevC2Entries enforces "no campaign-quote reuse". Caveat: `census/round-27/sources/` is currently empty — the sha256 cited in the writer draft must match ScoutGlibFetch's fetched bytes at integration.
5. Requirement 5 (no staged row appended as-is; normalization) — **covered**. ScoutRows152210211 produces the defect + normalization table; ExecRowsNormalize builds the 11-column block (recheck→365d, status=mined, used-by exactly the admitted entries, opened=today, no literal/escaped `|` in cells); RevC2Rows reviews; MutC2Rows mutation-tests five defect classes.
6. Requirement 6 (scratch transform + mirror gate exit 0 before any append) — **covered**. ExecAssimMirror mirrors corpus + normalized append block + knowledge files and runs `scripts/sources-census.sh validate --file <mirror>/corpus/SOURCES.md` to exit 0 before any lane append, iterating on E03/E04; RevC2Mirror reviews false-pass vectors.
7. Requirement 7 (assimilation named in the report's Sources & frontier section) — **covered**. ScribeReport's outline explicitly includes Sources & frontier; ScribeFrontierNotes drafts F4 next lines; the ScribeReport prompt is the only place the "Assimilation: …" adopt/none line is not spelled out (minor wording risk only).

## Attack log

- A1 (kill-rule adversarial reading): C2's frozen kill rule reads "the id-collision proof producing a nonempty `collisions` set without a committed renumber map fails C2". The wave's `collisions` IS nonempty (S109–S132) and no renumber map is produced anywhere. A strict judge could fail the claim on the literal text even though the three adopted ids (S152/S210/S211) are disjoint from the collision set. Smallest safe correction: the report (and assimilation evidence) must state explicitly — paste both id lists, the collision count, and "no adopted id collides; therefore no renumber map is required" — and RevC2Mirror's conclusion should be routed into ScribeReport. Currently unowned.
- A2 (order/continuation deviation): appending S152/S210/S211 after S132 leaves the registry non-monotonic (gap S133–S151), deviating from §10 "adopted ids continue the lane's registry (append-only)". Frozen claim pins the ids, so keep them, but document the gap and confirm `sources-census.sh validate` tolerates out-of-order ids (LabCensusProbe's 132→135 run tests this empirically; state the result in the report).
- A3 (command provenance): the wave evidence holds outputs only, not the exact comm command or the 0–3-space pattern string. Store the two `grep`/`comm` command lines verbatim in `assimilation/` (e.g. a short README) and cite them in the report so the proof is self-contained.
- A4 (snapshot receipt risk): the writer draft cites `census/round-27/sources/glocalfile.c` sha256 66b588c4… while the directory is empty at review time. Landing L1 must verify the sha256 equals ScoutGlibFetch's fetched bytes before installing the entry (gate tool `--snapshot-dir` should enforce); otherwise the Gate's `snapshot:` pointer would be unbacked.

## Conclusion

All seven §10 requirements have plan coverage; no counterexample disproves the plan's sufficiency. The attack log records four corrective actions (A1–A4) for the L1's integration pass — none changes a frozen predicate, counter, target, or case set.
