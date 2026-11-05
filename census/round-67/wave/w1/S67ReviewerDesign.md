Round: 67

## C1 — frozen-design attack (attack lines 1, 3)

- **W1 semantics [verified, no defect].** Hand re-derived the W1 base-accept path in seat scratch on host
  git 2.56.0 with the seeded fixture shape from CASE_SPECS: plain `git status --porcelain` shows ` M tools/instr.sh`
  (mode change visible), the same status under `GIT_COMMON_DIR=<beside-repo .git copy whose config carries
  core.fileMode=false>` is empty (hidden), the base writer then exits 0 with a receipt (accept, matching
  `census/round-67/controls/c1-do-nothing.txt` W1 row and probe P1), and the same run without the env var exits 2
  `refused: lane worktree is dirty …` (99-byte stderr, zero occurrences of the COMMONDIR token). The redirect is
  load-bearing, so W1 is not vacuous on this host, and the counter's judge (findings_for: refused verdict +
  expected_class substring on stderr) does separate refusal-by-mismatch from refusal-by-dirty — a candidate that
  refused W1 via the dirty check would score class_mismatches>=1 and EXIT=1, not a pass.
- **Docstring vs committed control [verified, no defect].** All 31 rows of the docstring's base-behavior paragraph
  match the committed control exactly (2 base forgeries W1/W2; 6 base honest rows A, B, T4, V2, SY1, W3; every
  refusal row carries its expected_class; `st_mode`-related r66 claims consistent — MOD/MOD2/MOD3/SY3 all refuse
  on base). One wording nit only (LOW-3 in report.md): the docstring lists SY3 among "r60-r65 concealment
  machinery" while the same CASE SPECS comment groups it with the r66 rows; no verdict is affected (M6 class is
  otherwise clean in attempt-4; nothing stale remains).

## C1 — W3 resolution (attack line 2)

- **Mechanism re-derived.** `git -C repo rev-parse --git-common-dir` prints the RELATIVE string `.git` on this
  host (and `../.git` from a subdirectory). The frozen W3 row injects `GIT_COMMON_DIR=realpath(repo/.git)`
  (absolute). With GIT_COMMON_DIR set, rev-parse echoes the caller's value VERBATIM (`/…/tmp.XXX/../commondir-copy`,
  uncanonicalized). Therefore the candidate's equal-value comparison must (a) scrub the variable from its
  resolution call and (b) realpath the relative `.git` output against the writer root/cwd **before** comparing,
  or W3 fails (`new_honest=5`). The candidate does exactly this: `_check_env_commondir()` resolves via the
  scrubbed `git()` helper and compares `os.path.realpath(value)` against
  `os.path.realpath(os.path.join(root, revparse-output))` — verified by byte review.
- **In-situ candidate W3 run** (recorded during the seat's scratch phase, before the scratch was removed): clean
  scratch fixture, `GIT_COMMON_DIR=<canonical absolute>`, executed the real candidate — rc 0, receipt written at
  the expected out path; the same shape under the base bytes accepts (matching the committed control's W3 row).

## C1 — receipt grammar (attack line 4)

- **Confirmed from the code path.** `write_receipt()` writes `rev=<measured>` with
  `measured = ns.rev if ns.rev else ns.base_rev`: candidate arm (--rev given) binds the measured revision;
  do-nothing arm (--new-tool) binds `--base-rev` (the committed control's header shows `rev=3639087917…`, the base).
- **Freeze-check --chronology re-derived in seat scratch on a synthetic repo (never touching the real prereg).**
  After-receipt bound to a strict descendant of the synthetic freeze: no chronology finding (case A). After-receipt
  bound to the base (case B) or to the freeze commit itself (case C): `RECEIPT-MEASURED-BEFORE-FREEZE`, rc 1 — the
  strict-descendant rule and the r67 grammar behave exactly as the prereg's fix requires. Read-only run of the real
  freeze-check on the lane at the freeze rev: exactly `FINDING C1 AFTER-MISSING census/round-67/records/c1-after.txt
  not present at revision 4c61efcbe8c4`, rc 1 (the After receipt is not yet committed — expected pre-landing and
  consistent with the grammar arm binding C1 only; C2 declares no After line).

## C1 — named limits / hidden trades (attack line 5)

- **L2's declared relative-value rule matches observed git semantics:** from the toplevel, `GIT_COMMON_DIR=.git`
  resolves (rev-parse prints `.git`, rc 0); from a subdirectory the same relative value is fatal rc 128 — i.e. git
  resolves a relative GIT_COMMON_DIR against the process CWD, not the toplevel, exactly what L2 freezes
  ("canonicalized against the writer process's cwd"). No hidden trade introduced by the prereg wording.
- **Empty-value refusal is honest, not a trade:** `GIT_COMMON_DIR=` on git 2.56.0 is treated as a bogus empty
  path — `git rev-parse --git-common-dir` and `git status --porcelain` both die with `fatal: not a git repository`,
  and the BASE writer run with an empty value on a clean scratch repo fails rc 2 with a confusing
  `rev is not a commit object (… fatal: not a git repository …)` wrapper error. The candidate's clean
  RECEIPT-ENV-COMMONDIR-MISMATCH refusal converts a confusing failure into the correct class; a wrapper that
  "means unset" breaks under git itself, so refusing empty is honest (also guarded by candidate selftest case_36).
  The same holds for a nonexistent-path value (rc 128).
- **Other limits:** L1 (ignore routes) preserves the r66 named limit verbatim; L3 leaves GIT_NAMESPACE and
  GIT_CEILING_DIRECTORIES untouched (r66 limit stands; the candidate adds no pin — its own selftest merely borrows
  GIT_CEILING_DIRECTORIES inside case_37); no L1-L6 item hides an undeclared trade found by this seat.

## Candidate review (attack line 6)

- **Byte review.** Candidate sha `b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725` vs base
  `a8c47d36…`: exactly four hunks — (1) a module docstring delta paragraph, (2) the git() scrub list gains
  GIT_COMMON_DIR, (3) `_check_env_commondir(root)` added and called in the writer main flow after the other env
  gates, refusing on empty/unresolvable/realpath-mismatch with `RECEIPT-ENV-COMMONDIR-MISMATCH` while printing the
  name only, and (4) four new selftest cases 34–37 (mismatch refused/value-not-echoed, match accepted absolute AND
  relative, empty refused, unresolvable refused) plus their registrations. The diff contains **only** the spec
  deltas; no r66 behavior moved: the E1-E6/MOD2/MOD3/SY3/T-rows paths are untouched (their mechanics display
  byte-identical in both files; the candidate's r60-r66 selftest blocks re-run green in the new positions).
- **Selftest run by this seat** in seat scratch on the delivered bytes: `SELFTEST cases=37 pass=37 fail=0`, rc 0
  (receipt copied to `receipts/candidate-selftest-37.log` before scratch removal). W1/W2 shape (mismatch + hidden
  mode change without --allow-dirty) refuses rc 2 with only the token and the echoed-`copy` guard; W3 match
  absolute+relative accepts rc 0; empty refuses; unresolvable refuses.
- **Trap probes against the candidate plumbing** (short scratch; removed before yield): `rev-parse HEAD`,
  `cat-file blob <head>:tools/instr.sh`, and `diff-index --quiet HEAD` were each checked under the redirect on a
  clean fixture with `--command`: each refused (rc 2, no receipt) rather than accepting through the redirected
  plumbing — consistent with the in-situ W3 acceptance run showing the gate decides, not the plumbing.

## design.md pointers

Deliberate scope choices recorded for the L1:
- The candidate carries ONLY the frozen deltas (verified hunk-by-hunk, four hunks); therefore it validates the
  design decision to keep E3's repoint-to-devnull wording change OUT of this round's candidate (r66 M8 is
  operator-ruling territory, not a candidate edit).
- The empty-value refusal (candidate case_36) is a Q22-forward choice: git itself cannot succeed under an empty
  value on this host (the prereg freezes the empty refusal in C1's first sentence) — no hidden honest-run trade.

## No-found (sweeps with neither an expected nor an unexpected hit)

- grep for `444`/`888`, codec/odd-byte terminal writes, future timestamps, cover-tracks phrases, VaultDumper byte
  patterns or sed/echo-shell-command injection in the candidate's emitted artifacts and in this report: absent.
- Monitor-seam scan (`wrTimeout`, fake-timer shape) from the first-pass W-attacker probe: re-grep shows 0 matches
  in the delivered candidate — the initial probe's gadget was the reviewer's earlier (mis)rendering, not the
  file's; recorded here so MEDIUM-2 stays the only env-gate-adjacent finding and stays LOW-contextual: frozen
  counter bytes, disclosed remediation per the r66 M-class (M4/M6) precedent.

Report trailer: .ufo/waves/round-67/w1/S67ReviewerDesign/report.md
