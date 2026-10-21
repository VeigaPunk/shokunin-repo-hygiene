# ScoutProcSelftestExpect — reason-field expectations vs (r2)–(r4)

Static analysis only. Sources read via `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 544c8358039a07e8b45e6db72312da5c8d965275:<path>` for `tools/souji-proc-census.sh` and `tests/fixtures/r18-proc-census.sh`, plus `.ufo/waves/round-21/preregistration.txt`. No `lsp` device is exposed in the available tool routes, so no semantic definition/reference trace was available; findings below are source-text observations plus stated inferences. No tool/fixture executed; no /proc touched. String regex checks ran the literal `redact_command` patterns against representative literal template-expanded reason strings in a throwaway bash (string ops only); the fixed-template/random-suffix argument below covers all remaining templates.

## 1. Reason-field expectations, `tools/souji-proc-census.sh` --selftest (`run_selftest`)

Path construction: `SELFTEST_TMP=$(mktemp -d /var/tmp/souji-proc-st.XXXXXX)` (mktemp random part is `[A-Za-z0-9]{6}`). Then `mkdir -p "$SELFTEST_TMP/d"`, workers spawned, then `rm -rf -- "$SELFTEST_TMP"`. `gone_path=$SELFTEST_TMP/d/gone` (never created — just a path string inside the deleted tree). `fd_path=$SELFTEST_TMP/d/open-file` (created via `: >` then deleted with the tree). Default census prefixes `/var/tmp /tmp /dev/shm`.

Assertions keyed on the reason column:
| pid | expected reason | construction |
|---|---|---|
| `reader_pid` | `cwd-deleted` | cwd `$SELFTEST_TMP/d` deleted (`cat < fifo` blocker) |
| `sleeper_pid` | `cwd-deleted` | same deleted cwd |
| `argv_pid` | exactly `"argv-path-gone:$gone_path"` | argv element `--workspace=$gone_path`; first `--*=/*` candidate under `/var/tmp`, gone after `rm -rf`. Cmdline also carries `secret_arg='--token=fixture-secret ghp_FAKE_TOKEN_PART sk-fakevalue password=fakepass https://user:pass@example.test/path'`, `Bearer split-bearer-secret`, `AKIA1234567890123456`, `xoxb-test`, `--ToKeN split-token-secret` — all of which must stay out of `cmd` (secret_ok) while the reason stays the **raw path** |
| `fd_pid` | exactly `"fd-path-gone:$fd_path"` | fd on the deleted `$fd_path` |
| `mixed_pid` | exactly `cwd-deleted`, `mixed_rows == 1` | deleted cwd + deleted fd + gone argv → cwd precedence |
| `argv_fd_pid` | `argv-path-gone:*` (glob) | deleted cwd is live; argv first gone candidate is `$fd_path` |
| `control_pid` | absent | cwd `$SELFTEST_CONTROL_TMP/'x (deleted)'` is live (`mkdir`d, `-e` true); `boundary_arg=--workspace=/tmpfoo/souji-proc-boundary/gone` fails `path_under_prefix` (`/tmpfoo/` ≠ `/tmp/`) |
| `literal_fd_pid` | absent | fd is the live literal `'x (deleted)'` file (`-e $fd_link && -ef` skip) |
| narrow run (`--prefix $literal_fd_dir`) | reader/sleeper/mixed still `cwd-deleted`; argv/fd/argv_fd/literal_fd/control all absent | prefix scope |
| `stat_newline_ok`, `starttime_ok`, `secret_ok`, `redaction_unit_ok` | non-reason (stat parser, field 22, cmd-field redaction incl. unit probe `-H Authorization: Bearer b AKIA… xoxb-test --token=t --TOKEN=c ghp_… sk-fake password=x https://u:p@h`) | adjacent, not reason |

## 2. Reason-field expectations, `tests/fixtures/r18-proc-census.sh`

Path construction: `SCRATCH=$(mktemp -d /var/tmp/souji-r18-proc-census.XXXXXX)`; gone roots via `make_gone_root(label,name)`: `mkdtemp(prefix="souji-r18-proc-argv-<label>.", dir="/var/tmp")`, file `root/sub/<name>` written then `unlink()`ed, then `shutil.rmtree(root)` before the census runs. fd roots via `spawn_deleted_stdout(label,...)`: `mkdtemp(prefix="souji-r18-proc-fd-<label>.", dir="/var/tmp")`, `root/stdout` touched, inherited as worker stdout, unlinked, root rmdir'd.

| case | expected reason | path (template, `XXXXXX` = `[A-Za-z0-9]{6}`) |
|---|---|---|
| P1 | `cwd-deleted` (+ FIFO-ish wchan) | cwd `SCRATCH/deleted-cwd` rmtree'd |
| P2 | exact `argv-path-gone:` + path | `/var/tmp/souji-r18-proc-argv-argv-p2.XXXXXX/sub/gone-argv-p2` |
| P6 | exact `argv-path-gone:` + path AND `R18_SYNTHETIC_PASSWORD_CANARY_NOT_A_CREDENTIAL` ∉ cmd AND REDACTION regex ∈ cmd | `/var/tmp/souji-r18-proc-argv-argv-p6.XXXXXX/sub/gone-argv-p6`; secret element `--password=CANARY` sits in the same cmdline but is **not** the gone-path source (its `=`-value is not `/`-absolute so `read_process_argv` skips it) |
| P9 | `fd-path-gone:` + path **or** that + ` (deleted)` (only tolerant expectation) | `/var/tmp/souji-r18-proc-fd-p9.XXXXXX/stdout` |
| P14 | exact `argv-path-gone:` + path; `R18_FAKE_BEARER_NOT_A_CREDENTIAL` redacted in cmd | `/var/tmp/souji-r18-proc-argv-redact-bearer.XXXXXX/sub/gone-bearer` |
| P15 | exact `argv-path-gone:` + path; `AKIA0000000000000000` redacted in cmd | `/var/tmp/souji-r18-proc-argv-redact-aws.XXXXXX/sub/gone-aws` |
| P16 | exact `argv-path-gone:` + path; `xoxb-r18-fake-not-a-token` redacted in cmd | `/var/tmp/souji-r18-proc-argv-redact-slack.XXXXXX/sub/gone-slack` |
| P18 | exact `cwd-deleted` (cwd > argv > fd) | argv path `/var/tmp/souji-r18-proc-argv-precedence-all.XXXXXX/sub/gone-precedence-all`, fd `/var/tmp/souji-r18-proc-fd-precedence-all.XXXXXX/stdout`, deleted cwd |
| P19 | exact `argv-path-gone:` + path (argv > fd) | `/var/tmp/souji-r18-proc-argv-precedence-argv.XXXXXX/sub/gone-precedence-argv` |
| P3, P10, P12, P13, P17 | absence expectations (live control; nested `SCRATCH/sub` top still exists; live literal ` (deleted)` cwd/fd; `-sibling` root under a still-existing top) | no reason text asserted |

Note P17 in the *default* census is also absent, and not because of prefixing: its top-level `/var/tmp/souji-r18-proc-census.XXXXXX` (the fixture's own SCRATCH) still exists during the run, so `top_level_scratch_gone` returns false.

## 3. Redaction-pattern exposure of every expected reason string

Checked representative template-expanded reason strings with the eight `redact_command` patterns (`ghp_…`, `sk-…`, `password=`, `--[Tt]oken=`, userinfo `scheme://…@`, `AKIA[0-9A-Z]{16}`, `xox[baprs]-…`, `Authorization: Bearer `): **all CLEAN, zero matches**. Structural inspection covers the remaining strings: every template is a fixed literal plus a 6-char `[A-Za-z0-9]` mktemp suffix; none contains `sk-`, `ghp_`, `AKIA`, `xox`, `password=`, `--token`, `://`, or `@`, and the random part cannot introduce them. `--workspace=` source elements match no secret pattern either, so (r2)'s "secret-bearing argv element" test is false for every fixture gone path; `--password=CANARY`'s candidate value never starts with `/` and is never selected.

## 4. Byte lengths (measured with `LC_ALL=C`, `${#var}`)

| reason | bytes |
|---|---|
| selftest `argv-path-gone:$gone_path` | 51 |
| selftest `fd-path-gone:$fd_path` | 54 |
| P2 / P6 | 75 |
| P9 | 56 (tolerated `+ " (deleted)"` variant: 66) |
| P15 | 74 |
| P16 | 78 |
| P14 | 80 |
| P19 — **worst case** | **91** |
| `cwd-deleted` | 11 |

Worst-case existing reason = 91 bytes; headroom to the (r4) 160-byte bound is 69 bytes. Since templates are static plus a fixed 6-char random suffix, no existing expectation can ever approach 145+15 bytes. (The 160-byte cap already exists for `cmd` via `REDACTED_CMD=${value:0:160}`; it is new for `reason`, which is currently unbounded after `sanitize_field`.)

## 5. Verdict: can (r2)–(r4) break these expectations?

**No — they cannot break any enumerated expectation, provided the implementation follows the prereg wording exactly.** Two binding constraints and one falsifier:

1. **(r2) must be per-argv-element, not per-cmdline.** Five exact-equality expectations have secrets elsewhere in the *same* cmdline while the reason must stay the raw path: selftest `argv_pid` (51 B) and r18 P6/P14/P15/P16 (75/80/74/78 B). If an implementer gates redaction on "cmdline contains a secret", all five break (reason becomes `argv-path-gone:[REDACTED]`). Per the prereg, redaction triggers only when the gone-path *candidate itself* is drawn from a `--token=`/`--password=`/`password=` value, the argument following a bare `--token`, or an element matching a secret pattern — no fixture path is, so all stay byte-exact. This is the single most important falsifier to report.
2. **(r3) applying `redact_command` patterns to the path text is a no-op on every fixture path** (§3, all CLEAN) — safe, but only because templates avoid the token shapes. A future canary path containing e.g. `sk-` in its template would flip an exact-equality case; the r21 canary fixture must keep secret material out of asserted raw paths or assert `[REDACTED]` there instead.
3. **(r4) 160-byte bound cannot break anything today**: worst case 91 B (P19), 69 B headroom; truncation would only bite if a reason exceeded 160 B, which no static template can produce. Note the bound must apply to the *whole* field after sanitize, and P9's tolerated `+ " (deleted)"` variant stays ≤ 66 B.

Confidence: high for all observations (read directly from the pinned rev; lengths/patterns mechanically checked). Residual unknown: the exact future implementation of "drawn from a secret-bearing argv element" is unwritten code — the per-element requirement in §5.1 is my reading of the prereg sentence, marked [INFERENCE] as to implementation intent, though the fixture-breaking consequence is factual if that reading is violated.
