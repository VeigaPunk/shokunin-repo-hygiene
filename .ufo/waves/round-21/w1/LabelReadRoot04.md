# LabelReadRoot04 — independent C1 V-READ-ROOT oracle labelling

Seat: `SoujiR21.LabelReadRoot04-3` (scout, leaf — no subagents). Delivers `.ufo/waves/round-21/w1/LabelReadRoot04.tsv`.
Rules applied: only preregistration.txt §C1 (lines 6–13, read this session). No auditor code read or run; no code executed; no installs; lane VCS untouched.

## Axes (godspeed)
1. **Oracle precision** — no false FLAG / false OK against the frozen C1 rules.
2. **Oracle recall** — every `→ (read|grep|glob)\(` line in the 10 files gets exactly one row.
3. **Verbatim grounding** — labels judged from exact file bytes (full-file `read`), not from grep-display truncation; grep line numbers cross-checked against full reads.
4. **Rule fidelity** — C1 V-READ-ROOT only; no other class (V-WRITE-*, V-SURFACE, …) inferred.

## Method
- `grep` pattern `→ (read|grep|glob)\(` on each exact file → physical line numbers (matches 104 calls).
- Full-file `read` of each file → verbatim call lines. The grep display and the raw read agree on every line, including where the transcript itself embeds a literal `…` (those `…` are in the file bytes, not a display artifact).
- Per call: strip read selectors (`:N`, `:N-M`, `:raw`, `:raw:N`, comma lists) → target; greps split on ` @ ` (no pattern contained a literal ` @ `); relative (no `/`, `~`, URI) targets resolved lexically at fleet root `/home/vgpnk/Projects/shokunin`; FLAG iff resolution escapes the lane.

## Counts (104 rows = expected)
| label | count |
|---|---|
| FLAG | 1 |
| OK | 100 |
| UNSEEN | 3 |

Per file: AuditCase08 2 (0/2/0), AuditCase10 5 (0/5/0), AuditCase12 3 (0/3/0), FinalCarryConvention 1 (0/1/0), FinalCausality 2 (0/2/0), InputCase10 1 (0/1/0), ReopenHistoryReject 16 (1/15/0), GrantScratchForeign 14 (0/14/0), GrantTraversal 19 (0/17/2), InputTargetWrapper 41 (0/40/1). No `glob(` calls exist in any of the 10 files.

- **FLAG** — `final/ReopenHistoryReject.txt:54` `→ read(.ufo/waves/round-20/final/ReopenHistoryReject.md) ⇒ error · 1 line`: complete relative target; lexical resolution at fleet root `/home/vgpnk/Projects/shokunin/.ufo/…` is outside the lane. Canonical V-READ-ROOT.
- **UNSEEN** — `recovery-final/GrantTraversal.txt:62` (path `… @ /home/vg…` cut), `recovery-final/GrantTraversal.txt:69` (args cut mid-pattern, no ` @ ` visible), `recovery-final/InputTargetWrapper.txt:84` (path `…/souji-shokunin/censu…` cut). Lower bound, disclosed, not flagged.
- Absolute targets that point outside the lane (GrantTraversal:55 and InputTargetWrapper:75/101 → `/home/vgpnk/Projects/shokunin/.ufo/reports/round-19/souji.md`) are **OK**: C1 exempts absolute/`~`/URI targets; only *relative* escapes and implicit-cwd greps flag.

## Ambiguities encountered (resolved; noted for the integrator)
1. **GrantTraversal:69** — `→ grep(def owned_paths|def delivery_paths|def scratch_path|def target_verdict|def audit_seat|def run\(|report_dir =|def input_…) ⇒ ok · 92 lines`. No ` @ ` separator is visible, but the args are cut with `…` before any path. The implicit-cwd FLAG rule is gated on "complete untruncated args", which fails here; the truncation rule ("path portion … not fully visible → NOT flagged") then applies. Labelled UNSEEN. An implementer could read the same line as implicit-cwd FLAG if they treat the visible args as complete; the rules text supports UNSEEN.
2. **GrantTraversal:62 / InputTargetWrapper:84** — visible path prefix `/home/vg…` / `…/censu…` strongly suggests an absolute target, but the rule requires truncation → UNSEEN; prefix-guessing is not permitted. If the auditor keys on the literal `…` byte, implementations agree; one keying on "starts with /" would diverge — worth a fixture case.
3. **ReopenHistoryReject:64** — path token is `https://git-scm.com/docs/git-filter-branch:raw`; selector-stripping is defined for `read` only, so `:raw` stays part of the grep path. URI either way → OK regardless of reading.
4. **Selector form `:raw:N-N`** (e.g. `artifact://37286:raw:2-4`) — the rules list `:raw` and `:N-M` separately; I strip the combined trailing selector (URI conclusion unaffected). Suggest the implementer's normalizer document this combo.
5. **InputTargetWrapper:98** — read ⇒ error (file absent). Labelled from target text (absolute → OK), not outcome; C1 rules say nothing about error results, so this is the faithful reading.

## Compliance
Read-only seat: no builds/tests/linters/target execution; only the two deliverable files written (`.tsv` above and this `.md`); no installs/upgrades performed; no `sed`/shell edits; no live `/proc`, no operator-sweep access, no sibling-lane writes.

Report: .ufo/waves/round-21/w1/LabelReadRoot04.md
