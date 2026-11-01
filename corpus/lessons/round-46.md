# Round 46 — tip landing-suite receipt, register-verifier selftest, F4 restore-collision ground

Fresh-start continuation on a new Windows host. The round's claims were frozen
2026-10-30 (`census/round-46/preregistration.txt`) by the earlier r46 session
before any wave dispatch; that session died before any after-data existed. This
session lands the frozen claims as written, with one disclosed host adaptation
(Amendment 1) and one implemented-but-missing kill rule (Amendment 1 addendum),
both committed before the after-measurements they affect.

## Gate

- S268 admitted: https://man7.org/linux/man-pages/man2/renameat2.2.html opened
  2026-10-30 by the freeze session (capture
  `census/round-46/sources/renameat2-located-quote.txt`, HTTP 200); re-opened
  live 2026-10-31 by this landing session (HTTP 200, quotes re-verified
  verbatim). Located quote (13 words): "Don't overwrite newpath of the rename.
  Return an error if newpath already exists." Context: § DESCRIPTION,
  RENAME_NOREPLACE flag; the page's ERRORS section adds "EEXIST flags contains
  RENAME_NOREPLACE and newpath already exists." Grounds the C3 restore-side
  refusal semantics only.
- S269 rejected: https://specifications.freedesktop.org/trash-spec/latest/
  opened 2026-10-30, HTTP 404 — the freedesktop 404 page, not the spec
  (`census/round-46/sources/trash-latest-404.txt`). No restore-collision rule
  can be grounded at this access. Flip: a later access serves the spec and its
  restore/expunge section addresses occupied original paths.
- S110 re-opened 2026-10-30 (capture `census/round-46/sources/rename2-reopen.txt`),
  located quote (9 words): "If newpath already exists, it will be atomically
  replaced". Row unchanged; used-by gains nothing (C3 cites it in the entry
  header only, per the frozen kill rules).
- Source rows before 191; before validation exited 0 (explicit lane dir — see
  Host note). After: 193 rows, exit 0
  (`census/round-46/records/census-after.txt`). Existing status/recheck/used-by
  cells unchanged. No knowledge entry beyond the one frozen C3 entry; no
  frontier row advanced; no Core promotion.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| text-mode newline translation on the new host | `git diff 8eabfba3924778e903537b46ae0c20979b1391a2..4b316f22ef0f9a43cee46ff8fd88b65c4e7d64c4 --stat` shows 1266/1180 wholesale line churn across README/SOURCES (CRLF) | Q7 named-path byte discipline; landing-diff review before filing | Normalize to LF by binary read/replace/write; net diff vs round base is exactly the intended lines (`git diff 5540250..bc50661 --stat`); C2 receipts re-measured at the normalized bytes. |
| prereg kill rule never implemented + stale pin target | frozen C1 sentence promised "instrument sha256 != pinned value"; the counter at 7f8fa3c only printed the digest, and its "r22-attempt2 bytes" pin was stale (r32 commit 98e5203 changed the instrument; r22 pin 65817d0d... vs round-base a3324916...) | spot-check of the green counter run before filing (this round) | Amendment 1 addendum: counter hard-pins the round-base digest a3324916... and refuses on drift (mutation witness `census/round-46/records/c1-pin-mutation.txt`, exit 2 at r28 rev ed270c4). |
| unanchored path filter turned a 6-path repair into a whole-tree loop | session log: `git ls-files \| grep -P '\n'` matched every line under MSYS grep; the loop then ran `git checkout HEAD --` per tracked file until killed | Q7 (stages/operates only on named paths); the worktree was verified clean before, so no content changed — disclosed as process defect, not data damage | NUL-delimited enumeration with exact byte matching (`ls-files -z` + control-char filter) for any path repair; targeted plumbing only. |

## Host note (absent-surface corrections, §6)

- The fleet conf still resolves lane `souji` to `souji-shokunin/`, which does
  not exist on this host; the lane lives at `shokunin-repo-hygiene/` (fleet
  root symlink). `sources-census.sh validate --root <fleet-root> souji` prints
  `souji missing` and exits 2 here
  (`census/round-46/records/census-conf-name-host.txt`); the documented
  explicit-lane-directory form validates the real registry, exit 0
  (`census/round-46/records/census-before.txt`, `census-after.txt`).
  PROVINCE.md carries the same correction.
- Six HEAD paths whose names contain control characters cannot be checked out
  by this host's git ("invalid path"; file creation fails with "Invalid
  argument" even with core.protectNTFS=false), so `git status --porcelain` is
  permanently non-empty here. Amendment 1 tunes only C1's drift precondition
  around exactly this class; receipts
  `census/round-46/records/c1-host-before.txt`,
  `c1-host-uncheckoutable.txt`.

## L2 floor note

The r45 operator stop left the L2 floor unmet, and this host exposes no
AgentSwarm/wave dispatch surface to this session: the frozen 32-seat w1 plan
(`.ufo/waves/round-46/w1-spec.json`, `w1-dispatch.json`) was validated at
freeze but seats were never spawned, here or earlier. Dispatched=0,
completed=0, dead=0; no WAVE-DONE is claimed; no seat output is cited as
verification. An L0 question is filed asking for the floor's disposition on
this host.

## Admission distinction

C1's green counter run at the tip re-derives dispositions that were already
committed (r44 register) — the round's work is making the instrument runnable
and truthful on this host (Amendment 1), landing the whole-suite tip receipt,
and closing the r45 routed debts (C2 selftest; whole-suite validation), not
newly corrected beliefs. Calibration's numeric score stays 7; no outstanding
false-belief count changes. C2 acquires a runnable, expectation-pinned
self-invocation mode whose default path is proven byte-behavior-identical; the
r45 interface-debt disclosure is closed. C3 adds one sourced knowledge entry
on existing F4 frontier ground — no Core promotion, no tool change, no
deletion or restore authority granted.
