# CritCounterFidelity — round-27 counter-fidelity attack

## Status

STATUS: PARTIAL — C1 values reproduce at base but its receipt binds a false gate sha256 and the counter depends on the live fleet root; C2 counters are worktree-scoped with no byte binding and no false-green control; C3 passes all four attack dimensions (design; fixtures not yet delivered).

## Evidence

All runs at base rev `e78ac7c4837b81b634db4a927605a751a7f006ba` (HEAD == origin/master, ahead=0). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.

- C1 frozen counter reproduced (`python3 -B tools/souji-landing-gate.py --root <lane> --rev e78ac7c... --round 27 --fleet-root /home/vgpnk/Projects/shokunin`):
  - stdout: `LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at e78ac7c4837b`
  - stdout: `LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at e78ac7c4837b`
  - SUMMARY: `SUMMARY	findings=2	checked_reg=50	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0`
  - stderr: `COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-27/ at e78ac7c4837b81b634db4a927605a751a7f006ba`; exit rc=2.
- Gate bytes: sha256 of `tools/souji-landing-gate.py` at base blob and worktree (identical, `git diff --quiet` rc 0) = `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`.
- `records/c1-before.tsv` line 2: `e78ac7c4837b81b634db4a927605a751a7f006ba	e67810d130817879fddd71c5ceeb5d5fd37e6ea8	2	50	2` — pinned `gate_sha256` = `e67810d130817879fddd71c5ceeb5d5fd37e6ea8` ≠ executed/committed gate bytes. No blob of `tools/souji-landing-gate.py` in history has that hash (`git rev-list --all` scan, empty); candidates (stdout, stderr, exemptions blob, gate-check blob, preregistration bytes, four argv permutations) all differ.
- Gate without `--fleet-root` at base: 5 findings; the extra 3 are the hyaku tokens `../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`, `../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md`, `.ufo/waves/hyaku/jj-w1/reports/` (sources `corpus/README.md:217`, `corpus/knowledge/jj-colocation-receipts.md:148`). With `--fleet-root`, they are fleet-classified via `os.path.exists` on the live fleet root and excluded → findings=2.
- C2 counters reproduced from base bytes: `git show e78ac7c:corpus/SOURCES.md | grep -cE ...` = 132; grounded F4 at base = 2 (`corpus_knowledge_quarantine-origin-record-fields-r24.md`, `corpus_knowledge_quarantine-staging-no-copy-r23.md`). Worktree corpus == base (diff rc 0).
- `records/c2-before.tsv`: header `rev	rows	grounded_f4	gate_tool_present`; row `e78ac7c4837b81b634db4a927605a751a7f006ba	132	2	absent`. `git ls-tree e78ac7c` contains `tools/souji-gate-check.py` (blob `63ac63b8...`), so `gate_tool_present=absent` contradicts the committed tree (unless the column meant the not-yet-installed `census/round-27/c2-gate.sh` wrapper; undocumented).
- `records/c3-before.tsv`: `rev	tool_present` / base row `absent`; base tree contains neither `tools/souji-pre-report-gate.sh` nor `tests/fixtures/r27-pre-report-gate.sh` (verified via `git ls-tree -r`).
- QUALITY.md:129 (Q55): "A count quoted in a lane record must name a receipt that binds the revision and the sha256 of the bytes that produced it."
- Landing-gate selftest contains explicit red cases (e.g. `dangling-skill-pointer` expect_n=1, `missing-cited-path` expect_n=1, `pin-mismatch`, bad-rev/no-skill/no-wave-dir → exit 2, exact CLI SUMMARY assertion).
- `tools/souji-gate-check.py` selftest (lines 280-284) includes `control always-green -> FALSE-GREEN-REJECTED`; the frozen C2 counter command does not invoke `--selftest`, and the row/ground greps have no control.

## Findings

1. C1 receipt byte-binding is false (Q55 defect): `c1-before.tsv` `gate_sha256` `e67810d1...` is not the sha256 of the counter bytes at base nor worktree (`02b58f81...`), nor any committed blob or candidate artifact. It does not bind the bytes that produced findings=2. (calibration)
2. C1 counter is only partially revision-scoped: findings include the 3 hyaku tokens unless the live fleet root currently exists them (`os.path.exists`); the base run exits `COULD-NOT-EVALUATE` (rc 2) because no round-27 wave `.md` reports exist in the tree — the claim's before=2 comes from a could-not-evaluate run and the after run will likewise exit 2 unless wave reports are committed at tip. (calibration)
3. C2 counters are not revision-scoped and have no byte binding: the frozen commands read live `corpus/SOURCES.md` / `corpus/knowledge/` paths; `c2-before.tsv` has no sha256 column; the counter text itself exists only in the untracked `preregistration.txt` (no committed counter bytes at base). `c2-before.tsv` `gate_tool_present=absent` contradicts the base tree. (coverage)
4. C2 lacks a false-green control for the row/ground counters (an always-zero emitter — broken regex/path — would pass silently); the gate tool's embedded FALSE-GREEN check is not part of the frozen counter invocation. (coverage)
5. C3 passes: tool absence at base verified; the fixture contract includes an explicit FALSE-GREEN always-pass control that must be rejected; planned after-receipt includes `tool_sha256` of installed fixture bytes. (operability; execution pending integration)
6. Cross-cutting: `preregistration.txt` itself is untracked at base (`git ls-files` empty), so "committed counter bytes" exist only for the C1 tool, not for the contract text or the C2 commands; before numbers (C1 findings=2, C2 132/2) are nonetheless reproducible from base bytes.

## Attack log

- C1: D1 values pass / byte-binding fail; D2 fail (false gate_sha256); D3 pass (selftest red cases incl. exact SUMMARY assertion); D4 partial (data reads tree at rev, but fleet-root live-exists dependency + execution from worktree; pre-wave exit 2).
- C2: D1 fail (no committed counter definition; receipt without byte binding); D2 fail (no sha256 for any quoted count); D3 fail (no control in frozen counter); D4 fail (worktree-dependent greps and gate reads).
- C3: D1 pass; D2 pass-by-design (after receipt must bind fixture sha256); D3 pass; D4 pass (hermetic /var/tmp fixture worlds).

Smallest safe corrections: (1) regenerate `c1-before.tsv` with `gate_sha256` = sha256 of the executed tool bytes at the measured rev and record the rc=2 could-not-evaluate semantics; commit wave reports before the after-run so the gate exits 0. (2) Make C2 counters revision-scoped (`git show <rev>:corpus/SOURCES.md | grep -cE ...` and ls-tree-equivalent for grounded F4), add input-byte digests to `c2-before.tsv`/after receipts, fix or rename the `gate_tool_present` column, and add a control that a non-empty registry/ground set yields a nonzero count. (3) Keep the C3 false-green case and bind the after receipt to the fixture bytes.
