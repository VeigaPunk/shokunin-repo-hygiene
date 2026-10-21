# LabelReadRoot09 — independent C1 V-READ-ROOT oracle

## Result

Applied only the V-READ-ROOT rules in the frozen round-21 preregistration C1 section to each matching call in the 11 requested round-20 transcripts. The TSV contains 103 call rows, matching the expected count.

| Label | Count |
|---|---:|
| FLAG | 0 |
| OK | 95 |
| UNSEEN | 8 |

No complete target resolves relatively outside the lane, and no complete grep call omits the ` @ ` separator. All complete targets are URIs or absolute paths; the one complete grep has an explicit absolute in-lane path. There are no glob calls among the matches.

## Ambiguous / lower-bound lines

- `recovery-final/InputDemo.txt:68`: `→ grep(def load_baseline_run|def load_migrated_caller|baseline_code|baseline_source|verification\.json|run-verification\.py|in…) ⇒ ok · 122 lines` — the arguments are truncated before any ` @ ` separator is visible. The rule explicitly flags a *complete* no-separator grep and treats a truncated path as not flagged; it does not state explicitly whether truncation before the separator is itself enough to treat the call as an incomplete target. I labelled it UNSEEN, not FLAG.
- `recovery-final/InputR14Frozen.txt:61`: `→ grep(input_snapshot|MEASURED_PATHS|resolve_durable|r14-cache-frozen|expected|record|dependency|git_head|input_sha256|snapsho…) ⇒ ok · 471 lines` — same ambiguity: truncated arguments, no visible separator.
- `recovery-final/InputR14Frozen.txt:69`: `→ grep(MEASURED_PATHS|resolve_revision|input_snapshot|checked_inputs|input_sha256|inputs_unchanged|corpus/knowledge|SOURCES.md…) ⇒ ok · 77 lines` — same ambiguity: truncated arguments, no visible separator.
- `recovery-final/F5Redaction.txt:47`: `→ grep(argv|reason|redact|sanitize|exception|error @ /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-rev-pin.py;/home…) ⇒ ok · 251 lines` — the first semicolon-separated path is complete and absolute; the second is truncated. The rules say to judge components and flag once if any component flags, but do not explicitly specify whether a call with a truncated component and no known-flagging component is labelled UNSEEN or OK. I labelled it UNSEEN because the complete call target is not visible.

The other four UNSEEN rows have a visible ` @ ` separator but a truncated path: `recovery-final/InputDemo.txt:52`, `:53`, `:69`, and `recovery-final/InputR14Frozen.txt:82`. They follow the explicit truncated-target lower-bound rule.

## Method and bounds

Used the required grep pattern `→ (read|grep|glob)\(` on each exact requested file to obtain physical line numbers. Cross-checked transcript content, including grep-elided ranges and the ambiguous call lines, with targeted reads. Applied the contract's fleet-root/lane distinction only to complete relative targets; URI and absolute targets were not V-READ-ROOT candidates even where a read returned an error or the file was missing. No auditor code was read or run. No tool was installed or updated.
