# SwarmMutationTester57 — C2 counter mutation test (souji r29, w1)

Report: .ufo/waves/round-29/w1/SwarmMutationTester57.md

## Status

STATUS: PASS — 13 mutants built from the frozen counter bytes, run on a 16-fixture scratch battery; 12 killed, 1 survivor proved semantically equivalent (M8, dead `and mans` clause under the frozen floor rule). Pristine counter matched analytic expectations on all 16 fixtures (`BASELINE_OK=True`). Lane counter bytes unmodified (pre/post sha256 identical); no tooling installed; scratch removed.

## Evidence

- Instrument: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/c2-counter.py`, sha256 `5ab641c41459ca72529baa57268eef99bb16b849f92e8bc2b0dd6fd7df3b1b3f`, introduced at prereg commit `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e` predates it — `git cat-file blob 691dd29...:census/round-29/c2-counter.py` → "exists on disk, but not in …"). Working tree = committed bytes at HEAD: `git -C <lane> cat-file blob HEAD:census/round-29/c2-counter.py | sha256sum` → `5ab641c4…` (pre and post).
- Battery: `/var/tmp/souji-r29-MutateC2Counter/battery.py` (`python3 -B`), scratch git repos via `git init -q` with `git -C <repo> rev-parse --show-toplevel == <repo>` asserted per repo; throwaway identity via `git -C <scratch repo> config` only. Command: `python3 -B /var/tmp/souji-r29-MutateC2Counter/battery.py`, wall 59.78 s.
- Detector: exact stdout (all per-round + SUMMARY lines) plus exit code, mutant vs pristine on the same fixture rev; `stderr != ''` labeled `crash` (none occurred — all diffs were `output`).
- Baseline (pristine vs hand-computed expectations, 16 fixtures): `BASELINE_OK=True`; e.g. FFC (r26/27/28 exactly at floor 1230/124/75, fully covered) → `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0`, rc 0; F2 (wrong recorded hash) → `r29 records=2 failed=1 uncovered=0 floor_violation=0`, rc 1; F4 (real newline + real backslash in names, GNU-escaped records) → clean, rc 1 only from missing floor manifests.
- Fixtures (all tiny scratch repos; floor rounds omitted on purpose — frozen missing-floor rule then contributes a known constant 3): F0 clean+symlink-excused; F1 absent path; F2 wrong hash; F3 symlink recorded in manifest with correct target-string hash; F4 escaped names; F5a `./` prefix; F5b `././` prefix; F7 symlink target ≠ symlinks.tsv col2; F8 waves files but no manifest; F9 no census tree; F10 r27 exactly at floor (124); F11 r27 below floor (10); F12 duplicate record wrong-then-right; F12b right-then-wrong; F14 nested `sub/.gitignore` uncovered; FFC floor-clean rc-0 shape.
- Mutant construction: single-anchor string replacements on pristine bytes, each `count==1` asserted, `py_compile` checked; anchors on the counter's own lines (e.g. `if e is None or e[0] == '120000':`, `re.sub(r'\\([\\n])'`, `hashlib.sha256(git(a.root, 'cat-file', 'blob', e[1])).hexdigest()`).
- Restoration: post-run `sha256sum` of lane counter = `5ab641c4…` (identical to pre); `git -C <lane> status --porcelain -- census/round-29/c2-counter.py` → 0 lines; lane never written (counter only copied out); scratch tree removed at end.

## Findings

1. Counter is mutation-tight on all probed semantics — location: `census/round-29/c2-counter.py:52-95` (record loop, uncovered loop, floors, return). 12/13 mutants killed by exact output+rc; no survivor indicates a verification hole (see Finding 2 for the one survivor).
2. M8 survivor is EQUIVALENT, not a gap — location: `census/round-29/c2-counter.py:95` (`return 0 if (tf == 0 and tu == 0 and tfl == 0 and mans) else 1`). Proof: `tfl ≥ len(missing)` and `missing` is every FLOORS round (`26,27,28`) without a committed manifest; hence `mans == []` ⇒ `floor_violations ≥ 3` ⇒ rc 1 regardless of `and mans`. The clause is dead code; battery cases F8/F9 (manifests=0) show byte-identical output and rc for mutant and pristine. Killable only in combination with floor removal: combo M1+M8 on F9 → `SUMMARY manifests=0 failed=0 uncovered=0 floor_violations=0`, rc 0 — and M1 itself is killed by 14 fixtures, so the dead clause cannot open a passing path while floors hold. This is an equivalence-class finding about the frozen counter, not a proposed change.
3. Waves files in a manifest-less round are unreported — location: `census/round-29/c2-counter.py:47` (uncovered is computed only per manifest-bearing round) plus prereg C2 contract wording "for every manifest.sha256 present at --rev". Battery: F8 (r29 waves files, no manifest) and F9 (no census at all) print the identical line `SUMMARY manifests=0 failed=0 uncovered=0 floor_violations=3`, rc 1. Gameability is bounded by the frozen rules: dropping the r29 manifest fails the `manifests=4`-at-final-tip kill rule, so this is recorded as an observation of frozen-counter semantics, not an attack on the target.
4. Duplicate manifest records collapse (last wins, `records=` counts deduped names) — location: `census/round-29/c2-counter.py:60` (`recs[name] = mm.group(1)`). Battery: F12 (wrong hash first, right last) → `r29 records=1 failed=0`; F12b (right first, wrong last) → `records=1 failed=1`. A malformed extra line is tolerated when a later correct line for the same name exists, but committed content is still verified against that correct hash, so no verification weakness; recorded for completeness.

## Attack log

Mutation probes against the frozen C2 counter (behavior-bearing point mutated; same detector on pristine/mutant; lane bytes never edited):

| Mutant | Change (single point) | Expected detector | Output | Verdict | Killed by |
|---|---|---|---|---|---|
| M1_ignore_floors | `fl = 0`, `tfl += 0` | floor_violations>0 survives → rc flip | differs | KILLED | 14 fixtures (F0-F14) |
| M2_symlink_records_ok | mode `120000` records accepted | failed=1 on F3 stays failed | F3 `failed=0` | KILLED | F3 |
| M3_no_unescape | decoder regex never matches | escaped records decode → failed=0 | F4 `failed=2 uncovered=2` | KILLED | F4 |
| M4a_strip_dot_twice | `./` stripped twice | F5b stays failed+uncovered | F5b clean | KILLED | F5b |
| M4b_strip_dot_never | `./` never stripped | F5a stays clean | F5a `failed=1 uncovered=1` | KILLED | F5a |
| M5_manifest_counted_uncovered | `p == m` → never true | manifest.sha256 uncovered | `uncovered=1` (+3 on FFC) | KILLED | 14 fixtures |
| M6_no_tsv_target_check | symlink target equality dropped | F7 stays uncovered | F7 `uncovered=0` | KILLED | F7 |
| M7_hash_of_blob_sha | sha256 of blob-sha hex instead of content | clean fixtures stay clean | every verified record fails | KILLED | 12 fixtures |
| M8_pass_without_manifests | `and mans` dropped from rc | manifests=0 → rc 0 | identical everywhere | SURVIVED (equivalent, Finding 2) | — |
| M9_first_duplicate_wins | first duplicate kept | F12 failed=0 / F12b failed=1 swap | both flip | KILLED | F12, F12b |
| M10_floor_leak_le | `<` → `<=` | at-floor manifests stay fl=0 | fl=1 at exact floor | KILLED | 8 fixtures incl. F10, FFC |
| M11_symlinks_never_excused | tsv excuse disabled | F0 stays uncovered=0 | F0 `uncovered=1` | KILLED | F0-F2 |
| M13_skip_dotfiles_uncovered | dotfile basenames skipped | F14 stays uncovered=1 | F14 `uncovered=0` | KILLED | F14 |

Baseline failure rule: none — pristine matched analytic expectations on all 16 fixtures (`BASELINE_OK=True`), so every kill above is conclusive. One earlier F5b expectation mismatch was my own (manifest has one record line → `records=1`, counter was right); corrected before the final run.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmMutationTester57.md` (this report; the only file written outside scratch).
- Tooling installed: none (python3 + git only). No pacman transactions. Scratch `/var/tmp/souji-r29-MutateC2Counter/` removed after this report was written.
