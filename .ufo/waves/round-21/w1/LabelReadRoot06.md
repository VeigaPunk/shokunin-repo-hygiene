# C1 oracle labelling — V-READ-ROOT

Reviewed the frozen C1 rules in `.ufo/waves/round-21/preregistration.txt` and searched each of the 11 assigned transcript files with the requested pattern `→ (read|grep|glob)\(`. Labelled only the visible transcript call targets; no auditor code was run or read.

## Counts

| Label | Calls |
|---|---:|
| OK | 88 |
| FLAG | 0 |
| UNSEEN | 16 |
| **Total** | **104** |

Absolute paths and visible URI targets are OK under the frozen rule. Sixteen calls have incomplete/truncated target text (including truncated grep arguments where an implicit-cwd call cannot be distinguished from a path omitted by truncation); they are UNSEEN, not flagged. No complete, untruncated grep call without an ` @ ` separator was visible, so no implicit-fleet-root FLAG was assigned.

## Ambiguous / truncated boundary calls

The following call displays contain an ellipsis in the argument/target. I applied UNSEEN where the complete target cannot be established; in particular, a visible URI prefix does not reveal the complete truncated target. For calls without a visible ` @ ` separator, the visible ellipsis also prevents determining whether the full grep arguments were separator-free (which would imply fleet-root cwd) or truncated before a target.

- `recovery-final/InputMissing.txt:50` — `→ grep(input_sha256|manifest|transcript|read_bytes|write_bytes|write_text|open\(|mkdir|deliver|output @ /home/vgpnk/Projects/s…)`
- `recovery-final/InputMissing.txt:51` — `→ grep(input_snapshot|sha256|is_file|is_symlink|missing|deleted|tree_check|resolve_durable|MEASURED_PATHS @ /home/vgpnk/Projec…)`
- `recovery-final/InputMissing.txt:52` — `→ grep(input_snapshot|MEASURED_PATHS|input_sha256|write_text|write_bytes|json.dump|OUTPUT|output|snapshot|tree_check @ /home/v…)`
- `recovery-final/InputMissing.txt:53` — `→ grep(input_snapshot|MEASURED_PATHS|input_sha256|write_text|write_bytes|json.dump|OUTPUT|output|snapshot|tree_check @ /home/v…)`
- `recovery-final/InputMissing.txt:54` — `→ grep(input_snapshot|MEASURED_PATHS|input_sha256|write_text|write_bytes|json.dump|OUTPUT|output|snapshot|tree_check @ /home/v…)`
- `recovery-final/InputMissing.txt:55` — `→ grep(input_snapshot|MEASURED_PATHS|input_sha256|write_text|write_bytes|json.dump|OUTPUT|output|snapshot|tree_check|git_head …)`
- `recovery-final/InputR13Fixtures.txt:53` — `→ grep(MEASURED_PATHS|INPUT_PATHS|INPUT_SHA256|input_snapshot|resolve_durable|selftest|fixture|SHELL|frozen|dependency_map|com…)`
- `recovery-final/InputR13Fixtures.txt:54` — `→ grep(def input_snapshot|def resolve_durable|def run_selftest|tracked|regular|symlink|tree_check|diff|added|missing|sha256|in…)`
- `recovery-final/InputR13Fixtures.txt:55` — `→ grep(MEASURED_PATHS|INPUT_SHA256|input_snapshot|resolve_durable|def checked_inputs|def resolve_revision|def main|def execute…)`
- `recovery-final/InputR13Fixtures.txt:56` — `→ grep(MEASURED_PATHS|module\.MEASURED_PATHS|input_snapshot|resolve_revision|paths =|run-targeted|selftest|frozen|input_sha256…)`
- `recovery-final/InputR13Fixtures.txt:57` — `→ grep(DEMO_MEASURED_PATHS|input_snapshot|resolve_durable|git_head|FIXTURE|tracked_at|load_baseline_run|load_migrated_caller|w…)`
- `recovery-final/InputR13Fixtures.txt:70` — `→ grep(C2 operability|every r13/r14|actual helper|frozen corpus|input_sha256|complete MEASURED_PATHS|C2 @ /home/vgpnk/Projects…)`
- `recovery-final/InputR13Fixtures.txt:71` — `→ grep(r13 computes|r13 measured paths|r13.*MEASURED|frozen|shell selftest|souji-round9-selftest @ /home/vgpnk/Projects/shokun…)`
- `recovery-final/InputR13Fixtures.txt:83` — `→ grep(If the optional argument onerror is specified|otherwise it is ignored|onerror @ https://docs.python.org/3/library/os.ht…)`
- `recovery-final/SourceTimeout.txt:60` — `→ read(https://web.archive.org/web/20260919212856id_/https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocatio…)`
- `recovery-final/SourceTimeout.txt:66` — `→ read(http://web.archive.org/cdx/search/cdx?url=www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html&from=…)`

The TSV is the per-call oracle output. The transcript grep searches were the only inspection of call inventory; no auditor, build, fixture, or test was run. No tools were installed or updated.
