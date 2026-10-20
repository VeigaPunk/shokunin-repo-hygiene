STATUS: DONE — all three exemption rows' reasons verified true; no row can mask a non-identical dangling pointer; stale guard proven effective by one synthetic clone run (injected resolving-path exemption → exactly one LG-DANGLING-PTR-EXEMPT-STALE, exit 1).

## Attacked claim
C2 calibration exemption corpus `corpus/pointer-exemptions.tsv`@5efb519f00075d958c3d1109ef6fcb24c487eb87: each row's reason true; no row hides a real dangling pointer; the stale-exemption guard (LG-DANGLING-PTR-EXEMPT-STALE, round ≥ 18) catches an exemption whose path resolves.

## Row-by-row fact check (all paths at 5efb519)

Row 1 `census/operator-sweep-20261019/` — "operator-owned untracked output … cited only to name it": VERIFIED.
- Untracked: `git ls-tree -r 5efb519 --name-only | grep operator-sweep-20261019` → no hit (also absent at baseline b576341); exists on disk (dir, only stat'ed per operator rule — never opened).
- Cited only to name it: corpus/README.md:81 "The untracked `census/operator-sweep-20261019/` remains operator-owned and is excluded from round staging"; corpus/lessons/round-18.md:7 names it as a deliberate non-file; LOG.md round-17 sections (556, 745) call it OPERATOR-authored. No citation treats it as usable lane evidence.

Row 2 `tests/vault/vadv54-run/p/p6repo/.git` — "absent by design … moved out of the tracked tree in r17 (phantom-deletion hazard)": VERIFIED with one wording nit.
- Absent: not in tip tree (ls-tree), absent on disk; p6repo/ now holds only tracked `inner/keep.txt`, `one.txt`.
- Phantom-deletion hazard story corroborated by SKILL.md:110 (nested `.git` reads as `D` under jj; stub quarantined at `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` — exists on disk, dated Oct 18).
- Nit (minor, no behavior impact): the stub was never a git-tracked blob (`git log --all -- tests/vault/vadv54-run/p/p6repo/.git` → empty over all refs), so "moved out of the tracked tree" really means "removed from the work tree into the untracked r17 quarantine".

Row 3 `tests/fixtures/r14-cache-frozen/record.json` — "measured_commit 0123456… is a deliberate placeholder … never a measured run": VERIFIED.
- Blob content: `"measured_commit": "0123456789abcdef0123456789abcdef01234567"` (exact string as claimed).
- Wiring: expected.json `"record": "record.json"` → `_pin_repo_path` → that path; at round 18 the gate resolves `0123456…^{commit}` (fails rc=1) → would be LG-FROZEN-MEASURED, suppressed only by this exemption. Corroborated by lessons round-18.md:7 ("1 LG-FROZEN-MEASURED (the r14 synthetic placeholder)") and expected.json `verdict: reusable` (attempt_reuse demonstration).

## Can a row hide a real dangling pointer? No (exact-match, narrow).
- Suppression is exact string equality (`if path in exemptions`, tools/souji-landing-gate.py:861 region); no prefix/glob; `<>*` rejected at load (:783); a citation of `…/p6repo/.git/HEAD`, `census/operator-sweep-20261019/anything`, or a slash-less `census/operator-sweep-20261019` is NOT suppressed and still yields LG-DANGLING-PTR.
- Rows are keyed by path, not source: any source's exact-string citation of that one path is suppressed — by design, and the stale guard fires the moment the path becomes tracked/resolving or the citation disappears.

## Stale-guard effectiveness — synthetic run (the one ALLOWED-EXEC)
Clone `/var/tmp/souji-r18w2-RevExemptions/lane` detached at 5efb519; appended one row `tools/souji-landing-gate.py<TAB>synthetic r18w2 RevExemptions probe: this path resolves in the tree, so the exemption must be flagged stale`; committed as ce1803118f8456674c5e641ed48d313cf5f4e9fe; ran once:

`python3 tools/souji-landing-gate.py --root <clone> --rev ce1803118f84… --round 18 --fleet-root /home/vgpnk/Projects/shokunin --json …/stale-probe.json`

Output: `LG-DANGLING-PTR-EXEMPT-STALE  tools/souji-landing-gate.py  exemption does not suppress an unresolved pointer or dangling measured_commit at ce1803118f84` / `SUMMARY findings=1 checked_reg=33 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=4 status_lines=90 carry_heading=1 checked_reports=91 checked_ptrs=445 ptr_exempt=3 ptr_fleet=3`, gate exit 1. JSON: findings=[exactly the injected stale], 3 fleet classifications, error null.

Reading:
1. Guard effective: exemption for a tree-resolving path → stale finding, exit 1.
2. Rows 1–3 all genuinely used at round 18 (ptr_exempt=3 covers README:81 + lessons:7 sweep and SKILL:110 stub; row 3 consumed by the measured-commit branch) — none falsely stale.
3. Transitive control: probe commit differs from 5efb519 only by that one exemption row and yields exactly 1 finding ⇒ 5efb519 round 18 = 0 findings, matching the claimed tip result. The 7 pre-wave dangling citations (`census/round-17/gate-replays-ddb7347.json`, `jj-receipts-ddb7347.txt`) were re-pointed, not exempted — neither old path exists at tip and neither is in the exemptions file; SKILL.md:163-165 and README now cite committed `census/round-18/` records.

## Findings (severity-ordered)
1. MINOR (doc precision, corpus/pointer-exemptions.tsv row 2): "moved out of the tracked tree in r17" — the stub was never tracked in any commit; it was removed from the work tree into the untracked quarantine. Smallest fix: reword to "removed from the work tree in r17 into the r17 quarantine (never committed)".
2. RESIDUAL (no action needed): with `--fleet-root`, fleet classification precedes exemption matching (gate :855-865), so a `../`-normalized citation resolving under the fleet root leaves an exemption unused → false-positive STALE direction only; it cannot mask a dangling pointer.
3. RESIDUAL: `used_exemptions` unions pointer-use and measured-commit-use (:990), so a row kept alive by one live pointer stays unflagged even if its other suppression purpose is dead — looseness, not masking; both purposes protect the same path.

## Tooling / cleanup
No tools installed (repo python3/git only; pacman paused per operator). Clone deleted: `rm -rf /var/tmp/souji-r18w2-RevExemptions`. No lane file modified; the only writes were this report and the deleted clone.

## Verdict
HOLDS. Every reason is factually true at 5efb519 (one wording nit), exact-match suppression cannot hide non-identical danglers, and the stale guard demonstrably flags a resolving-path exemption while leaving all three real rows used.
