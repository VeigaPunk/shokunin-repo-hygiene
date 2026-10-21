# AttackCorpus05 — C1 transcript classifier comparison

Independent per-call labels were completed and written to `.ufo/waves/round-21/w2/AttackCorpus05.tsv` **before** opening `tools/souji-seat-audit.py`. The labels use the frozen C1 text in `.ufo/waves/round-21/preregistration.txt`, `clarification-before-measurement.txt`, and the superseding `full-corpus-restoration.txt`.

## Label inventory

| Export path | Calls | FLAG | OK | UNSEEN |
|---|---:|---:|---:|---:|
| `final/AuditCase10.txt` | 5 | 0 | 5 | 0 |
| `final/AuditCase13.txt` | 1 | 0 | 1 | 0 |
| `final/FinalFrontier.txt` | 1 | 0 | 1 | 0 |
| `final/FinalNoTrade.txt` | 3 | 0 | 3 | 0 |
| `recovery-final/OracleAuditCases.txt` | 103 | 0 | 103 | 0 |
| **Total** | **113** | **0** | **113** | **0** |

Every visible target is either an absolute path (105 calls) or a URI (8 calls), so none resolves implicitly from the fleet-root cwd. The lone grep call at `recovery-final/OracleAuditCases.txt:201` has a complete ` @ ` separator and visible absolute `/var/tmp/...` target. URI examples include `skill://` and `artifact://`; the classifier's scheme test is case-insensitive. Three failed read attempts are still labeled from their visible targets (`final/FinalNoTrade.txt:69`, `recovery-final/OracleAuditCases.txt:43,79`); status does not make an absolute/URI target a root-read violation. No target component or selector was cut, so no row is UNSEEN.

## Pinned classifier comparison

Read the pinned classifier using `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 522dcd768ca90afe166532d37d306d3df70aeea5:tools/souji-seat-audit.py` (source only; no classifier or target code executed). In `implicit_root_read` (`tools/souji-seat-audit.py:377-402`):

- `grep` gives ` @ ` precedence, then recognizes legacy `grep(PATTERN in PATH)`, and treats a complete call with neither path form as an implicit `.` target.
- It splits semicolon-separated path components, skips empty/cut components, and removes trailing read selectors including `:raw`, numeric/range selectors, and `:conflicts`.
- It exempts absolute paths, `~` paths, and URI schemes with `re.IGNORECASE`; other visible targets resolve lexically from `fleet` and are returned only when outside `lane`.

The caller at `audit_seat` lines 455-458 applies this predicate only to `read`, `grep`, and `glob`, then emits minor `V-READ-ROOT` when the predicate returns a target. Comparing each independent row against that behavior yields **0 disagreements**: all 113 labels are OK and the pinned predicate returns no target for each. The statuses on failed calls do not alter this path-only result.

## Evidence limits

Source-only classification; no tests, builds, or target code were run. The available tool routes did not expose an LSP device, so definition/caller tracing used literal search followed by inspection of the pinned source and caller. No additional classifier behavior outside these 113 calls was evaluated.