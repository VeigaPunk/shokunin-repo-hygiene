STATUS: DONE — all assigned synthetic CLI totality probes passed; no actionable defect reproduced

# Attacked claim

R18-M5 totality in `tools/souji-landing-gate.py` at `5efb519f00075d958c3d1109ef6fcb24c487eb87`: early evaluation failures must be reported as exit 2 with a `SUMMARY`, rather than escaping through `emit()` as a traceback; malformed/unusual authority inputs must not crash the CLI.

# Findings

None. The tested cases returned only 0 or 2, each printed `SUMMARY`, and neither output stream contained a traceback. The cases exercise the early strict-UTF-8 exemption error and invalid `--fleet-root` errors, plus the CRLF, missing-LOG, unheaded-LOG, and binary-source paths.

Source evidence in the checked-out revision:

- `tools/souji-landing-gate.py:890-905` initializes every counter consumed by `emit()`, including `checked_measured`, before evaluation. `:1024-1029` converts `EvalError` to exit 2 and retains the initialized result. `:1032-1052` emits the TSV `SUMMARY` before the error diagnostic; `:1023` selects exit 2 for an error. The top-level exception fallback also supplies `checked_measured` (`:1968-1985`).
- `:763-789` turns non-UTF-8 exemption bytes into `EvalError`; `splitlines()` parses CRLF rows. `:792-795` rejects a missing/non-directory fleet root with `EvalError`.
- `:651-666` returns an empty LOG citation section when no heading for the requested round exists. LOG and other pointer-source bytes are decoded with replacement (`:822-835`); lesson/report bytes also use replacement (`:400`, `:418`).

# Commands and outputs

The CLI below was run from the 5efb519 checkout against independent, committed synthetic Git repositories under `/var/tmp/souji-r18w2-RevGateTotality/synthetic-cases`; no real fleet or repository was passed to it. All commands used `--rev HEAD --round 18`.

```text
python3 /var/tmp/souji-r18w2-RevGateTotality/lane/tools/souji-landing-gate.py --root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/non-utf8-exemptions --rev HEAD --round 18
rc=2
stdout: SUMMARY\tfindings=0\tchecked_reg=0\tchecked_changed=0\tchecked_pins=0\tchecked_measured=0\tchecked_markers=0\tstatus_lines=0\tcarry_heading=0\tchecked_reports=0
stderr: COULD-NOT-EVALUATE\tcorpus/pointer-exemptions.tsv is not UTF-8: 'utf-8' codec can't decode byte 0xff in position 24: invalid start byte

python3 /var/tmp/souji-r18w2-RevGateTotality/lane/tools/souji-landing-gate.py --root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/crlf-exemptions --rev HEAD --round 18
rc=0
stdout: SUMMARY\tfindings=0\tchecked_reg=0\tchecked_changed=0\tchecked_pins=0\tchecked_measured=0\tchecked_markers=0\tstatus_lines=0\tcarry_heading=0\tchecked_reports=1
stderr: (empty)

python3 /var/tmp/souji-r18w2-RevGateTotality/lane/tools/souji-landing-gate.py --root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/fleet-root-missing --rev HEAD --round 18 --fleet-root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/absent-fleet-root
rc=2
stdout: SUMMARY\tfindings=0\tchecked_reg=0\tchecked_changed=0\tchecked_pins=0\tchecked_measured=0\tchecked_markers=0\tstatus_lines=0\tcarry_heading=0\tchecked_reports=0
stderr: COULD-NOT-EVALUATE\t--fleet-root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/absent-fleet-root is not a directory

python3 /var/tmp/souji-r18w2-RevGateTotality/lane/tools/souji-landing-gate.py --root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/fleet-root-file --rev HEAD --round 18 --fleet-root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/fleet-root-is-file
rc=2
stdout: SUMMARY\tfindings=0\tchecked_reg=0\tchecked_changed=0\tchecked_pins=0\tchecked_measured=0\tchecked_markers=0\tstatus_lines=0\tcarry_heading=0\tchecked_reports=0
stderr: COULD-NOT-EVALUATE\t--fleet-root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/fleet-root-is-file is not a directory

python3 /var/tmp/souji-r18w2-RevGateTotality/lane/tools/souji-landing-gate.py --root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/round-18-no-log --rev HEAD --round 18
rc=0
stdout: SUMMARY\tfindings=0\tchecked_reg=0\tchecked_changed=0\tchecked_pins=0\tchecked_measured=0\tchecked_markers=0\tstatus_lines=0\tcarry_heading=0\tchecked_reports=1
stderr: (empty)

python3 /var/tmp/souji-r18w2-RevGateTotality/lane/tools/souji-landing-gate.py --root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/log-no-round-headings --rev HEAD --round 18
rc=0
stdout: SUMMARY\tfindings=0\tchecked_reg=0\tchecked_changed=0\tchecked_pins=0\tchecked_measured=0\tchecked_markers=0\tstatus_lines=0\tcarry_heading=0\tchecked_reports=1
stderr: (empty)

python3 /var/tmp/souji-r18w2-RevGateTotality/lane/tools/souji-landing-gate.py --root /var/tmp/souji-r18w2-RevGateTotality/synthetic-cases/binary-authority-sources --rev HEAD --round 18
rc=0
stdout: SUMMARY\tfindings=0\tchecked_reg=0\tchecked_changed=0\tchecked_pins=0\tchecked_measured=0\tchecked_markers=0\tstatus_lines=0\tcarry_heading=0\tchecked_reports=1
stderr: (empty)
```

The binary-source repository contained invalid UTF-8 bytes in `SKILL.md`, `SHONEN.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md`, the round-18 lesson and spotcheck, `LOG.md`, and the round report. The separate exemption test intentionally used strict-invalid UTF-8 and correctly returned exit 2.

# Verdict, residual risk, verification gaps

**Verdict: holds for the assigned cases.** No fix is indicated by these probes. The invalid exemption and invalid fleet-root cases fail closed with an error diagnostic and summary; CRLF exemptions parse; missing/unheaded LOG input and binary decoded text sources complete without a traceback.

Residual gap: no exit-1 fixture was part of the assigned case list, and the broad top-level unexpected-exception fallback was not deliberately induced; its counter shape was checked in source. The mounted tool inventory has no `lsp` device (`read xd://lsp` returned “No such tool”), so references/definition/diagnostics were unavailable. Text search was used only to locate source anchors, not as semantic proof. The clone and synthetic repositories were removed after these runs; no tool was installed or updated.