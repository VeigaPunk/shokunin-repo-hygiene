# LabF4Probe — F4 ground-count method probe (round 27, attempt 2)

## Status
STATUS: PASS — probe complete; observed grep counter = 2, tool grounded=9 mapped=9 dangling=0 mismatches=0, reconciled (tool counts all themes, claim counter is F4-only); README F4 row (:42) entries cell currently names 4 files, not exactly the 2 grounded ones.

## Evidence
- `grep -rlE '^ground: F4' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/ | wc -l` → `2`.
- Same grep without `wc -l` → exactly:
  - `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/quarantine-staging-no-copy-r23.md`
  - `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/quarantine-origin-record-fields-r24.md`
- `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-coverage-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev e78ac7c4837b81b634db4a927605a751a7f006ba` → `grounded=9 mapped=9 dangling=0 mismatches=0` (exit 0).
- Ground-marker census over `corpus/knowledge/` (`grep -rhE '^ground: ' | sort | uniq -c`): F4=2, F2=5, F1=2 → 9 total; `grep -rlE '^ground: '` lists exactly 9 files.
- `git -C <lane> show e78ac7c4837b81b634db4a927605a751a7f006ba:corpus/README.md | sed -n '42p'`: F4 row (read at HEAD e78ac7c; `git status --porcelain` shows corpus/README.md unmodified, so working tree = base).
- Ground lines (verbatim, no pipe):
  - `quarantine-staging-no-copy-r23.md:6`: `ground: F4 — restorable quarantine (the staging primitive: no-clobber rename)`
  - `quarantine-origin-record-fields-r24.md:7`: `ground: F4 — restorable quarantine (the read side of a per-item origin record)`
- `grep -cE '^ground:'` on the other two F4-row entries → 0 each (`trash-spec-restorable-quarantine.md`, `quarantine-same-filesystem-rename.md`).

## Findings
1. Claim counter observed = 2 (pre-state, as frozen: grounded F4 2→4). Location: `corpus/knowledge/` grep.
2. Tool output grounded=9 is theme-wide: F1=2, F2=5, F4=2. Tool counts every entry with a front-matter `^ground: F<k>` line (`souji-coverage-agreement.py` `entry_grounds`/`FRONT_GROUND`); it is not an F4 counter. Number `2` for F4 is consistent within 9. Location: `tools/souji-coverage-agreement.py:92-112,156-165`.
3. Reconcile: grep = F4-only count (2); tool = all-grounded count (9) that also verifies every grounded entry maps and no map path dangles (dangling=0). No conflict.
4. README F4 row entries cell (`corpus/README.md:42`, base e78ac7c at names 4 files, not exactly the 2 grounded: `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md` (both without `^ground:` marker), plus the 2 grounded `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md`. The row is the only F4 table row in README (grep `F4` table rows → :42 only).

## Attack log
None (read-only probe; no counter change proposed).
