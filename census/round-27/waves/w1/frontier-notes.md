# Frontier notes — round 27 (w1 draft)

DRAFT for the L1 (only integrator): content for the `## Frontier`
section of `corpus/README.md` (:44-49), the F4-ground row (:42), and
the F5 state note, after C2 landing. Every quote below is verbatim from
base e78ac7c bytes opened this run (pre-landing). The unchanged-state
bullets must stay byte-identical when the section lands.

## F4 status after landing

- Grounded F4 entries: 2 → 4. Adds `corpus/knowledge/origin-record-writer-r27.md`
  (source S152 — GLib tag 2.84.0 `gio/glocalfile.c`, opened 2026-10-25) and
  `corpus/knowledge/origin-record-mechanism-set-r33.md` (sources S210/S211 —
  `gio/glocalfile.c` + `glib/gfileutils.c`, opened 2026-10-25).
- Both entries carry a `## Gate` section with >=1 ADMIT and >=1 REJECT from
  the staged set (writer: 7 ADMIT / 1 REJECT, S119; mechanism-set: 5 ADMIT /
  2 REJECT, incl. S152-reuse REJECT).
- Record format and staging tool changes remain operator decisions
  (unchanged from r22 language, README :438); neither entry decides a
  receipt format — each entry's Limits/What-this-does-not-establish section
  says so.
- The writer entry's amendment note names the read-side entry
  `corpus/knowledge/origin-record-format-gvfs-r26.md` (S146) as "staged":
  it exists only in the shokuknow merge set, not in this lane's corpus. L1
  keeps the "staged" wording, or admits the entry (out of scope this round).

## Corpus/README.md updates (proposed)

F4 row (:42) status cell — append to the existing status:

`frontier; layout held, staging primitive + record read side admitted r22 (see § Round22 attempt 2), writer + mechanism set admitted r27 (see § Round 27)`

F4 row (:42) entries cell — append two names:

`knowledge/origin-record-writer-r27.md`, `knowledge/origin-record-mechanism-set-r33.md`

`## Frontier` bullets (:44-49) — post-landing:

- F1 git-native housekeeping vs receipts — next: the trigger set and the measured prune are now held (round-26 entries `knowledge/git-auto-maintenance-trigger-set{,-r23}.md`, S128-S132); remaining: keep-ref expiry unmeasured, fleet exposure numerator re-census. [unchanged]
- F2 repository size census — next: the /var/tmp write-safety fixture for `git repo structure`. [unchanged]
- F3 duplicate verdicts — next: a `duplicate` receipt class is an operator decision (taxonomy change). [unchanged]
- F4 restorable quarantine — next: per-item origin records (trashinfo-style) and `mv --no-copy` staging are tool changes for the operator. *(r27: the writer (GLib `g_local_file_trash()` at tag 2.84.0, S152) and the mechanism set (`O_EXCL` reservation, temp-file content write, atomic rename; S210/S211) are now admitted — see § Round 27; the record format and any staging tool change remain the operator's decision.)*

F5 state — unchanged; keep the r25 frontier line (:549):

`F5 stays list-only; reap and NAMESPACE remain operator-held. Certification OFF, K5 HELD.`
