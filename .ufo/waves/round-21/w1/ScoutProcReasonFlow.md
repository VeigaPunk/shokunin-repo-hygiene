# Proc-census byte flow: reason and command sinks

**Axes covered:** source-to-sink coverage, per-sink sanitation, concrete raw-secret paths. **Confidence: high** for the static control/data flow at pinned revision `544c8358039a07e8b45e6db72312da5c8d965275`; path examples are conditional on the stated synthetic filesystem state. No census, selftest, or target code was run. No `lsp` device/server is exposed in this session, so this is a literal source trace, not an LSP semantic-reference result.

## Observed flow and row fields

The ten row fields are declared at `tools/souji-proc-census.sh:13` and emitted by the `printf` at `375-377`. The only direct flows from `/proc/<pid>/cmdline` or `/proc/<pid>/fd` link targets into row *values* are `reason` and `cmd`:

- **`reason` (field 9):** The cwd link is read at `340`; if it qualifies as deleted, only the constant `cwd-deleted` is retained at `342-343` (cwd path bytes do not enter the field). `read_process_argv` is always called at `345`. It reads `/proc/<pid>/cmdline` as NUL-delimited arguments at `234, 256`. For each raw argument, it takes an absolute argument as candidate (`237`) or strips the leading option and `=` from `--*=/*` (`238`). The first candidate that is absolute, absent (`240`), under a configured prefix, and whose top-level scratch component is absent (`top_level_scratch_gone`, `168-185`) is stored unchanged in `PROC_GONE_PATH` (`243`). If cwd did not already set the reason, the path is control-sanitized at `347`, prefixed as `argv-path-gone:` at `348`, and control-sanitized again as the whole reason at `367-368`.
- If no cwd or argv reason exists, `find_deleted_fd_path` scans `/proc/<pid>/fd/*` (`258-273`): it reads each symlink target with `readlink` (`263`), requires the ` (deleted)` suffix (`264`), strips that suffix (`266`), requires an absolute target under a configured prefix with absent top-level component (`267-270`), and stores the first match raw (`270`). The reason becomes `fd-path-gone:<target>` after `sanitize_field` at `353-354`, then the whole reason is sanitized at `367-368`. The fd scan is skipped whenever cwd or argv already set a reason; it returns the first matching fd target.
- **`cmd` (field 10):** The same cmdline reader builds `CMD_RAW` from the arguments at `255`, joining NUL-separated arguments with one ASCII space. Candidate detection happens before command redaction. For a standalone case-insensitive `--token` argument, its following argument is replaced with `[REDACTED]` only in the command string (`249-253`); the candidate path, if any, was already saved raw. The finished string is passed to `redact_command` at `364`, and its result is emitted as `row_cmd` (`365-366, 377`). The fd target is never added to `cmd`.

Row-field mapping and other sinks:

| Sink | Source | Sanitization / transformation |
|---|---|---|
| pid | `/proc/[0-9]*` basename (`324-326`) | No `sanitize_field`; the proc-directory glob supplies the numeric name. |
| ppid, pgid, sid, starttime, state | Parsed `/proc/<pid>/stat` (`109-132`), emitted at `376-377` | No field sanitizer. ppid/pgid/sid/starttime are checked as decimal numbers at `126-127`; state is taken from parsed `fields[0]` (`128`). Not derived from cmdline or fd targets. |
| age_s | `/proc/uptime`-derived ticks and stat start ticks (`317-323, 335-336`) | Arithmetic/integer output; no cmdline/fd flow or field sanitizer. |
| wchan | `/proc/<pid>/wchan` (`359-360`) | Empty becomes `-` (`361`); `sanitize_field` at `362-363` replaces C0 controls and DEL with spaces. Not derived from cmdline/fd targets. |
| reason | cwd marker, first qualifying argv candidate, or first qualifying fd target (`339-354`) | C0/DEL replacement only: `sanitize_field` at `189` (definition), argv `347` / fd `353`, and final reason `367`. No secret-pattern redaction, escaping beyond control replacement, or length bound. |
| cmd | `/proc/<pid>/cmdline` | NUL delimiters are consumed and arguments joined by spaces (`234-256`); standalone `--token` next-arg replacement (`249-253`); then control-byte replacement and secret-pattern redaction (`redact_command`, `192-225`), then byte-slice to 160 bytes (`227`, with `LC_ALL=C` at `11`). Empty becomes `-` (`366`). |
| boot-id comment (not a TSV field) | `/proc/sys/kernel/random/boot_id` (`288`) | C0/DEL replacement at `290-291`; emitted at `322`. |
| header (not a TSV field) | Literal `HEADER` (`13`) | Static. |

`sanitize_field` (`188-190`) maps bytes `0x01–0x1f` and `0x7f` to ASCII space; it does not redact credentials or cap length. On the reason path this is applied to the candidate before prefixing and once more to the whole reason. All other path bytes, including credential-pattern matches, pass unchanged to `safe_reason` and the `%s` row output (`367-377`). Bash's NUL-delimited cmdline read consumes delimiter NULs; embedded argument bytes other than NUL are otherwise retained until the described replacement/redaction/truncation. Cwd link path bytes are discarded in favor of the fixed reason label.

`redact_command` applies these patterns only to `CMD_RAW` (`192-227`): control bytes at `194`; case-insensitive `Authorization: Bearer <nonspace>` at `196-199`; `--token=<nonspace>` at `200-203`; `ghp_...` at `204-207`; `sk-...` at `208-211`; `password=...` at `212-215`; URL userinfo before `@` at `216-219`; `AKIA` plus 16 uppercase/digit characters at `220-222`; and `xox[baprs]-...` at `223-225`. None of these transformations is called on `reason`. In particular, `PROC_GONE_PATH` is assigned before command sanitization (`234-243` precedes `249-255`), and `redact_command` is invoked only with `CMD_RAW` (`364`), not with `reason`.

## Concrete synthetic argv counterexamples

For each case below, assume the synthetic process is otherwise eligible for a row, the default `/var/tmp` prefix is active, and `/var/tmp/gone` does not exist. Each `argv` item shown as one quoted item is one NUL-delimited argument; these are source-level examples, not executed tests. `--workspace=` is just an example of the accepted `--*=/*` form. The expected reason contains the value/pattern raw even where `cmd` would redact it.

| Synthetic argv | Expected raw reason | Why the command-field protection does not protect reason |
|---|---|---|
| `['worker', '--token=/var/tmp/gone']` | `argv-path-gone:/var/tmp/gone` | Candidate extracted at `238`; `--token=` command pattern can hide the value in `cmd` (`200-203`), but candidate is already stored raw. |
| `['worker', '--token', '/var/tmp/gone']` | `argv-path-gone:/var/tmp/gone` | The next arg is captured as candidate before `redact_next` changes only its command copy to `[REDACTED]` (`234-253`). |
| `['worker', '--workspace=/var/tmp/gone/ghp_FAKE_TOKEN_PART']` | `argv-path-gone:/var/tmp/gone/ghp_FAKE_TOKEN_PART` | `ghp_` is a `cmd` pattern (`204-207`), not a reason pattern. |
| `['worker', '--workspace=/var/tmp/gone/sk-fakevalue']` | `argv-path-gone:/var/tmp/gone/sk-fakevalue` | `sk-` is a `cmd` pattern (`208-211`), not a reason pattern. |
| `['worker', '--workspace=/var/tmp/gone/password=fakepass']` | `argv-path-gone:/var/tmp/gone/password=fakepass` | `password=` is a `cmd` pattern (`212-215`), not a reason pattern. |
| `['worker', '--workspace=/var/tmp/gone/Authorization: Bearer fixture-secret']` (one argument containing spaces) | `argv-path-gone:/var/tmp/gone/Authorization: Bearer fixture-secret` | The bearer pattern applies to `cmd` (`196-199`) only; reason control sanitization does not remove spaces or redact the value. |
| `['worker', '--workspace=/var/tmp/gone/https://user:pass@example.test/path']` | `argv-path-gone:/var/tmp/gone/https://user:pass@example.test/path` | URL-userinfo pattern applies to `cmd` (`216-219`) only. |
| `['worker', '--workspace=/var/tmp/gone/AKIA1234567890123456']` | `argv-path-gone:/var/tmp/gone/AKIA1234567890123456` | AWS-key pattern applies to `cmd` (`220-222`) only. |
| `['worker', '--workspace=/var/tmp/gone/xoxb-test']` | `argv-path-gone:/var/tmp/gone/xoxb-test` | Slack-token pattern applies to `cmd` (`223-225`) only. |

A standalone absolute argument such as `['worker', '/var/tmp/gone/ghp_FAKE_TOKEN_PART']` reaches the same candidate path through `237`, without any option prefix. Conversely, a secret-looking non-path argument such as `ghp_FAKE_TOKEN_PART` by itself does not become an argv reason candidate; it can still be redacted in `cmd`. The first qualifying argv path wins (`240-244`), so a later secret-bearing path will not replace an earlier accepted candidate.

The fd path has the same raw-secret issue independently of argv: a qualifying deleted fd target such as `/var/tmp/gone/ghp_FAKE_TOKEN_PART (deleted)` is stripped to `/var/tmp/gone/ghp_FAKE_TOKEN_PART` (`263-270`) and reaches `fd-path-gone:` with only control-byte replacement (`353, 367`). This is a bounded hypothetical fd example, not an argv shape.

## Unresolved / not claimed

- No live-process behavior, actual filesystem state, or selftest outcome was observed; the counterexamples depend on `/var/tmp/gone` being absent and the process passing the census eligibility checks.
- Static source proves the flow and bypass; it does not establish whether a particular deployment has affected secret-bearing argv or fd paths.
- No `lsp` device/server was available, so no semantic definition/reference query was possible.