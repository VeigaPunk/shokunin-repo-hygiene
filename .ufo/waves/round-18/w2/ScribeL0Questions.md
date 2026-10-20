STATUS: DONE — two L0 question lines drafted and grounded in read-only probes; no lane code executed, no process signalled.

# Scope
Scribe seat ScribeL0Questions, wave 2 (FALSIFY), round 18. Attacked surface: the two open operator decisions that the round-18 handoff needs answered before the process-residue reap (Q32) and the r14 fixture session-kill can land. Lane tip 5efb519f00075d958c3d1109ef6fcb24c487eb87 read in place; no clone needed (no ALLOWED-EXEC item).

# L0 questions

souji | round-18 | Approve reaping the 58 souji fixture orphans (all cwd-deleted; pid set identical in census/round-18/leaked-procs-before-1631.txt and census/round-18/proc-census-live-1721.tsv) by re-verifying each (pid, starttime, boot_id) from the live census immediately before any signal, per QUALITY Q32, and recording each reap in LOG?

souji | round-18 | May souji re-derive the NAMESPACE_SHA256 pin in tools/souji-preservation-evidence.py (currently e6a984b1…14b2, which matches tests/fixtures/r14-census-boundary.py byte-for-byte) so the r14 fixture session-kill can land, accepting that the preservation-evidence digest changes?

# Evidence

## Q1 grounding
- `leaked-procs-before-1631.txt` has 58 lines (`wc -l` = 58); every line is a souji/r15/r16/r17 fixture scratch process.
- `proc-census-live-1721.tsv` header `# boot_id 3e7084f4-7046-4957-a8a2-c00542a3b469`; 65 data rows; 7 non-fixture rows (pids 1659, 1845, 1983, 2147, 2154933, 2257336, 863272 — Hyprland, 1Password, portal, Chromium renderers, a `import argparse`) excluded; the remaining 58 are all reason `cwd-deleted`.
- Python set comparison: live candidate pids == before-1631 pids, `True`; pids only in before: none; only in live: none.
- Q32 (`corpus/QUALITY.md:81`) requires operator approval, re-verification of (pid, starttime, boot_id) at act time, and a LOG record. The `before-1631` file carries no starttime or boot_id columns, so the binder must be taken from the live tsv (`starttime` column, e.g. pid 1026787 → 403309).
- Note: the file is named `before-1631` but the live snapshot is `1721`; the sets agree, so the names are a naming wrinkle, not a count defect.

## Q2 grounding
- `sha256sum tests/fixtures/r14-census-boundary.py` → `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`.
- `tools/souji-preservation-evidence.py:307` `NAMESPACE_SHA256 = "e6a984b1…14b2"`; `:1161` raises `pinned-mismatch` on any other digest; `:1923` checks the same pin.
- Consequence: the pin is currently satisfied by the r14 bytes as they sit at the tip, so the session-kill edit would fail the pin unless the pin is re-derived in the same change. The pin re-derivation is a policy/authority change, hence the operator question.

# Verdict
- Q1: question is grounded; the 58-pid claim holds against both snapshots.
- Q2: question is grounded; the pin value and the mismatch path were read at the cited lines.

# Commands run
- `read` on census/round-18/leaked-procs-before-1631.txt, census/round-18/proc-census-live-1721.tsv, corpus/QUALITY.md:80-81, and grep hits for NAMESPACE_SHA256 in tools/souji-preservation-evidence.py (exact named files only).
- `sha256sum tests/fixtures/r14-census-boundary.py` (matched pin).
- `python3` read-only counts/set comparison over the two named census files (no writes, no signals).
- `wc -l census/round-18/leaked-procs-before-1631.txt` → 58.

# Tooling
No installs or upgrades. pacman untouched.

# Out of scope
No edits to lane files; no reap performed; no census/operator-sweep-20261019/ access.

# Findings (defects)
- None against the claims attacked. Minor: naming mismatch `before-1631` vs `1721` snapshot; before-file lacks starttime/boot_id, so the re-verify binder must cite the live tsv.
