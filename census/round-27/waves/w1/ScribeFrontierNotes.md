# ScribeFrontierNotes — round 27 w1

## Status
STATUS: PASS — drafted w1/frontier-notes.md (delivery file) and this report;
all evidence read at base e78ac7c; no write outside
`.ufo/waves/round-27/w1/`; no tools installed; no scratch created.

## Evidence
- Lane HEAD = `e78ac7c4837b81b634db4a927605a751a7f006ba` (`git rev-parse HEAD`);
  `git status` shows corpus/README.md unmodified (untracked r27 w1 only).
- `corpus/README.md:42` (F4 row, base): "frontier; layout held, staging
  primitive + record read side admitted r22 (see § Round22 attempt 2)".
- `corpus/README.md:46` (F1): "remaining: keep-ref expiry unmeasured, fleet
  exposure numerator re-census."
- `corpus/README.md:47` (F2): "next: the /var/tmp write-safety fixture for
  `git repo structure`."
- `corpus/README.md:48` (F3): "a `duplicate` receipt class is an operator
  decision (taxonomy change)."
- `corpus/README.md:49` (F4 next): "per-item origin records (trashinfo-style)
  and `mv --no-copy` staging are tool changes for the operator."
- `corpus/README.md:549` (F5): "F5 stays list-only; reap and NAMESPACE remain
  operator-held."
- `w1/origin-record-writer-r27.md:4`: "ground: F4 — restorable quarantine
  (who WRITES a per-item origin record, and with what guarantees)"; Gate §:
  7 ADMIT / 1 REJECT (S119); amendment note (:60): "This entry re-grounds,
  at the round's own access date, the write side".
- `w1/origin-record-mechanism-set-r33.md:6`: "ground: F4 — restorable
  quarantine (whether a per-item origin record needs O_EXCL uniqueness,
  rollback, or a different scheme)"; Gate §: 5 ADMIT / 2 REJECT (incl.
  S152-reuse REJECT).
- Provenance: `glob` of `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/`
  lists `origin-record-writer-r27.md` and `origin-record-mechanism-set-r33.md`;
  `SOURCES.append.md:50,108,109` hold rows S152/S210/S211 (URL cell, S152):
  "https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c".
- Base lane `corpus/SOURCES.md` grep for `S152|S210|S211` → no rows (append
  pending, as claimed). `census/round-27/sources/` exists but is empty at
  observation; the two GLib snapshots cited in the Gates are not yet placed.

## Findings
1. F4 grounded set is 2 → 4 post-landing: pre = `quarantine-staging-no-copy-r23.md`,
   `quarantine-origin-record-fields-r24.md` (LabF4Probe, grep = 2); the two
   admitted entries add 2. Row :42 entries cell names 4 files pre-landing
   (2 grounded + spec + HELD rename); L1 appends the two new names.
2. The writer entry's amendment note cites `corpus/knowledge/origin-record-format-gvfs-r26.md`
   (S146) as "staged" — present only in the shokuknow merge set, absent from
   the lane corpus (`glob` none). Non-blocking if L1 keeps the "staged"
   wording; would dangle if a gate scans entry paths.
3. `census/round-27/sources/` empty at my read; C2's re-grounding snapshots
   must land before counters run (executor seats mid-flight).
4. F2 bullet at README :47 ("next: the /var/tmp write-safety fixture") is
   superseded by r24 C1 fixture cases 1-6 (README :517) — left unchanged per
   mandate; flagged for L1 awareness only.

## Attack log
None (not an attack item).
