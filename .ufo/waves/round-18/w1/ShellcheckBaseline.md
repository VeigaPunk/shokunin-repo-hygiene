STATUS: DONE — Q9 baseline completed at b5763415cc67ecff1e8fe56c58c39a6fb106d7a3; warning-level ShellCheck findings in two scripts

# Q9 baseline — round 18, wave 1

Axis: operability (assigned judgement). This records the requested baseline only; no implementation files were changed.

Baseline source: `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` in `/var/tmp/souji-r18-ShellcheckBaseline/lane`.

## Shell checks

Each row is the exit code from the exact command shown. Exit 0 produced no output. `bash -n` passed for every file; ShellCheck returned 1 only for `souji-verify.sh` and `souji-vault-verify.sh` due to the warnings below.

| File | `bash -n <file>` | `shellcheck -S warning <file>` |
|---|---:|---:|
| `tools/souji-verify.sh` | 0 | 1 |
| `tools/souji-vault-verify.sh` | 0 | 1 |
| `tools/souji-census.sh` | 0 | 0 |
| `tools/souji-quarantine.sh` | 0 | 0 |
| `tools/souji-repo-structure.sh` | 0 | 0 |
| `tests/fixtures/r12-maintenance-guard.sh` | 0 | 0 |
| `tests/fixtures/r13-quarantine-bounds.sh` | 0 | 0 |
| `tests/fixtures/r13-repo-structure.sh` | 0 | 0 |
| `tests/fixtures/r17-jj-receipts.sh` | 0 | 0 |

Exact commands for the table are `bash -n <file>` and `shellcheck -S warning <file>` with each listed path substituted literally. The clean checks emitted no output.

### ShellCheck output — `tools/souji-verify.sh` (exit 1)

```text
In tools/souji-verify.sh line 132:
      *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem)
      ^---^ SC2221 (warning): This pattern always overrides a later one on line 132.
            ^--^ SC2222 (warning): This pattern never matches because of a previous pattern on line 132.


In tools/souji-verify.sh line 394:
      R_VERDICT=NOT-SAFE; R_RECEIPT=unpushed-branch
                                    ^-------------^ SC2100 (warning): Use $((..)) for arithmetics, e.g. i=$((i - 2))


In tools/souji-verify.sh line 861:
      R_RECEIPT=unpushed-branch; R_REASON=unpushed-branch
                ^-------------^ SC2100 (warning): Use $((..)) for arithmetics, e.g. i=$((i - 2))
                                          ^-------------^ SC2100 (warning): Use $((..)) for arithmetics, e.g. i=$((i - 2))


In tools/souji-verify.sh line 894:
    R_VERDICT=NOT-SAFE; R_RECEIPT=secrets-refusal; R_REASON=secrets-refusal
                                                   ^------^ SC2034 (warning): R_REASON appears unused. Verify use (or export if used externally).


In tools/souji-verify.sh line 1013:
      if [ "$krc" != 1 ]; then SC_PASS=0; SC_EV="$SC_EV head-history=FAIL"; fi
                               ^-----^ SC2034 (warning): SC_PASS appears unused. Verify use (or export if used externally).
```

### ShellCheck output — `tools/souji-vault-verify.sh` (exit 1)

```text
In tools/souji-vault-verify.sh line 123:
      *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem)
      ^---^ SC2221 (warning): This pattern always overrides a later one on line 123.
            ^--^ SC2222 (warning): This pattern never matches because of a previous pattern on line 123.


In tools/souji-vault-verify.sh line 573:
      R_VERDICT=NOT-SAFE; R_RECEIPT=unpushed-branch; R_REASON=unpushed-branch
                                    ^-------------^ SC2100 (warning): Use $((..)) for arithmetics, e.g. i=$((i - 2))
                                                              ^-------------^ SC2100 (warning): Use $((..)) for arithmetics, e.g. i=$((i - 2))


In tools/souji-vault-verify.sh line 918:
    FAIL_REASON=pushed-unverifiable
    ^---------^ SC2034 (warning): FAIL_REASON appears unused. Verify use (or export if used externally).


In tools/souji-vault-verify.sh line 1066:
      R_RECEIPT=unpushed-branch; R_REASON=unpushed-branch
                ^-------------^ SC2100 (warning): Use $((..)) for arithmetics, e.g. i=$((i - 2))
                                          ^-------------^ SC2100 (warning): Use $((..)) for arithmetics, e.g. i=$((i - 2))


In tools/souji-vault-verify.sh line 1220:
        SC_PASS=0; SC_EV="$SC_EV head-history=FAIL"
        ^-----^ SC2034 (warning): SC_PASS appears unused. Verify use (or export if used externally).


In tools/souji-vault-verify.sh line 1749:
    --vault=*) VAULT_HINT=${1#*=}; shift ;;
               ^--------^ SC2034 (warning): VAULT_HINT appears unused. Verify use (or export if used externally).
```

## Python compilation

The tracked-file selection command was:

```text
git -C /var/tmp/souji-r18-ShellcheckBaseline/lane ls-files -- 'census/round-17/*.py' 'tests/fixtures/r1[4-7]-*.py'
```

It selected the 11 paths below. Each was compiled separately with the exact `python3 -m py_compile <file>` command shown; every invocation exited 0 and emitted no output.

| Exact command | Exit |
|---|---:|
| `python3 -m py_compile census/round-17/gate-replays.py` | 0 |
| `python3 -m py_compile census/round-17/run-matrix.py` | 0 |
| `python3 -m py_compile census/round-17/seat-audit-replay.py` | 0 |
| `python3 -m py_compile census/round-17/transcript-manifest.py` | 0 |
| `python3 -m py_compile tests/fixtures/r14-census-boundary.py` | 0 |
| `python3 -m py_compile tests/fixtures/r14-evidence-cache.py` | 0 |
| `python3 -m py_compile tests/fixtures/r15-census-config.py` | 0 |
| `python3 -m py_compile tests/fixtures/r15-preservation-evidence.py` | 0 |
| `python3 -m py_compile tests/fixtures/r15-preservation-frozen/regenerate.py` | 0 |
| `python3 -m py_compile tests/fixtures/r16-landing-gate.py` | 0 |
| `python3 -m py_compile tests/fixtures/r17-census-hygiene.py` | 0 |

## Findings and disposition

- `tools/souji-verify.sh:132` and `tools/souji-vault-verify.sh:123` — **fails warning-clean ShellCheck**: `*.env` overlaps `.env`, making the latter alternative unreachable (SC2221/SC2222). Smallest fix: remove the redundant `.env` alternative if it has identical handling; otherwise split/reorder the case patterns so the intended `.env` handling is reachable.
- `tools/souji-verify.sh:394,861` and `tools/souji-vault-verify.sh:573,1066` — **fails warning-clean ShellCheck**: SC2100 flags the `unpushed-branch` assignment RHS tokens. Smallest review step: preserve the intended literal value explicitly (e.g. quote the RHS) and rerun ShellCheck; no source edits were made in this baseline task.
- `tools/souji-verify.sh:894,1013` and `tools/souji-vault-verify.sh:918,1220,1749` — **fails warning-clean ShellCheck**: SC2034 reports `R_REASON`, `SC_PASS`, `FAIL_REASON`, and `VAULT_HINT` as unused at the cited assignments. Smallest fix: remove only genuinely dead assignments; where a value is consumed indirectly, make that output/data flow explicit or locally document the intentional indirect use.
- All 9 shell scripts **hold `bash -n`**; all 11 Python files **hold `py_compile`**. The other 7 shell files **hold `shellcheck -S warning`** with exit 0.

ShellCheck was already executable; no tool was installed or updated.