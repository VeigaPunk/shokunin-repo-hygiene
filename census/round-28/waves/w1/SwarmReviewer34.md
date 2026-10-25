# SwarmReviewer34 — round 28 w1 census-gate review

## Status
STATUS: PASS — all three census gates hold: candidate-mirror validate exit 0, live-tree validate exit 0, frozen manual commands (duplicate ids, enums, used-by missing) all empty/0.

## Evidence

Built scratch mirror at `/var/tmp/souji-r28-SwarmReviewer34/mirror` (copy of the Exec-C2AppendBlock candidate: lane `corpus/` + append block S212–S214 + the two admitted entries). Diff vs lane corpus confirms exactly the expected delta: only `SOURCES.md` (append) and the two new knowledge entries; `corpus/README.md` differs only because the lane worktree was edited after the mirror was built (mid-wave; not a census input).

**Gate 1 — mirror validate:** `sources-census.sh validate --file /var/tmp/souji-r28-SwarmReviewer34/mirror/corpus/SOURCES.md`
- exit 0; final line `file ok /var/tmp/souji-r28-SwarmReviewer34/mirror/corpus/SOURCES.md`
- W04 warnings only (pre-existing shared-URL rows S035/S036/S038/S049/S057/S058/S059/S063/S065/S072/S073/S075/S076/S077/S086/S087/S088/S089/S090/S091/S092/S093/S094/S095/S096/S097/S098/S099/S106/S108/S123/S124/S125/S126/S210); none from S212–S214.
- Mirror registry rows = 138; S212/S213/S214 each NF=13; malformed rows = 0.

**Gate 2 — live tree:** `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
- exit 0; `souji ok /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`; W04 only (same pre-existing set).

**Gate 3 — frozen manual census commands (run from lane root and mirror root):**
- rows: live=135, mirror=138
- malformed (NF!=13): live 0, mirror 0
- duplicate ids (`uniq -d`): empty both
- enum/tier/status/kind/inflation: empty both
- mined used-by paths missing: empty both (mirror run from mirror root; S212/S213 used-by = both entry files, S214 used-by = durability entry, all resolve)
- S212/S213/S214 verbatim (mirror lines 157–159): 11 columns, kind=spec, tier=A, status=mined, opened=2026-10-25, recheck=365d, used-by exactly the admitted entries.

## Findings
1. Candidate mirror is internally consistent and passes every frozen gate; no E-code, no missing used-by, no duplicate/enum violation introduced by the append. Location: `/var/tmp/souji-r28-SwarmReviewer34/mirror/corpus/SOURCES.md` rows S212–S214.
2. The two mirror entry files (`origin-record-exclusivity-r28.md`, `origin-record-durability-r28.md`) are present at the paths the S212–S214 used-by cells point to, so E11 is satisfied; they were pre-existing staged drafts (dated 2026-10-24) reused by the append-block builder, not re-grounded drafts, and carry no `## Gate` section — the L1/admission step must replace them with the re-grounded copies (per C2) before commit; this does not affect the census gates. Location: `/var/tmp/souji-r28-SwarmReviewer34/mirror/corpus/knowledge/`.
3. Live tree currently passes at 135 rows (base); the append is only in the candidate mirror, as expected pre-integration.
