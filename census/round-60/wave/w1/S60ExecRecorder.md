# S60ExecRecorder — souji-receipt-write.py (round 60, C2)

## Delivered (candidate, not placed in tools/)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecRecorder/souji-receipt-write.py` (26510 bytes, mode 0755, Python 3.14.8, stdlib only)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecRecorder/selftest.txt` (984 bytes)

## Command run
`python3 .../souji-receipt-write.py --selftest --work <scratch>/selftest-work --report .../selftest.txt`  exit 0

Verbatim final line: `SELFTEST cases=12 pass=12 fail=0`

Two prior runs failed; the first run caught a real bug (captured output was read but never appended to `chunks`, so every receipt body was empty). Fixed by adding `chunks.append(chunk)`; the rerun is the one delivered.

## Record shape
```
instrument=<relpath>
instrument_sha256=<sha256 of committed blob bytes at rev>
rev=<full40>
command=<shlex.join(argv)>
<combined stdout+stderr, trailing newlines normalized>
EXIT=<rc>
```
Base `record-receipt.sh` shape preserved, `command=` added. Digest = `git cat-file blob REV:INSTR` bytes, the same bytes as the base `git show | sha256sum`.

## Invocation
`souji-receipt-write.py --root LANE --rev FULL40 --instrument RELPATH --out FILE [--max-bytes N] [--allow-dirty] (--command "CMD" | -- ARGV...)`
`--selftest --work DIR [--report FILE]`

## Behaviour map (one selftest case each)
| # | Behaviour | Case | Result |
|---|---|---|---|
| 1 | argv / --command forms; mutually exclusive | arg-forms | ok |
| 2 | non-40-hex rev refused, nothing written | rev-format | ok |
| 3 | instrument absent / symlink at rev refused; regular passes | instrument-at-rev | ok |
| 4 | existing OUT refused, byte-identical, no temp | overwrite | ok |
| 5 | SIGTERM/SIGINT: no OUT, no temp left behind | atomic-signal | ok |
| 6 | --max-bytes over cap refused (flag + default 262144); exact cap passes | max-bytes | ok |
| 7 | dirty tree (modified + untracked) refused; --allow-dirty overrides | dirty-tree | ok |
| 8 | wrapped rc passed through; receipt written with EXIT=rc | exit-code | ok |
| 9 | temp beside OUT; TMPDIR untouched; no `/tmp` literal in source | no-scratch-literal | ok |
| 10 | root file set and porcelain unchanged by a run | readonly-root | ok |
| 11 | always-write stub (forged worktree instrument) rejected | always-write stub | ok |
| 12 | always-refuse stub rejected | always-refuse stub | ok |

Instrument byte-binding (worktree bytes must equal committed blob at rev) is enforced even under `--allow-dirty`; this is what rejects cases 11/12.

## Fixture contract (reply sent to S60ExecRecorderFix)
My flag form is authoritative. Their proposed contract differs in these ways: no positional args; exit is the wrapped command's rc (not always 0) with the receipt still written; extra refusals for symlink-at-rev, worktree/committed byte mismatch, --command plus argv, missing OUT parent, and OUT appearing during the run. Their fixture must parametrize onto the flag form or score as-is.

## Named limits
- Output is captured in memory (bounded by --max-bytes); the child is not streamed.
- A SIGKILL of the writer cannot run cleanup; a temp file could remain beside OUT only if killed during the short write window after the command completes. SIGTERM/SIGINT are handled.
- Digest binds bytes at rev, not execution (same limit as round-57 C2).
- Dirty check is `git status --porcelain` (ignored files not considered).
- Selftest uses `/bin/echo`, `sh`, `sleep`, and `python3` as wrapped commands; the signal case depends on `sleep 8` finishing within the test window.
- Not placed in `tools/`; L1 copies it. No production file touched. No git mutation run in the lane; all fixtures were throwaway repos under scratch, toplevel asserted before commit.

## Tools installed
None. No installs or upgrades performed.

## Scratch
`/fast/scratch/hyaku/souji-r60/S60ExecRecorder` removed after delivery (the selftest report was written directly into the delivery dir, so nothing needed copying).

## Subagent dispatch
None. The optional single labrat probe was not used.
