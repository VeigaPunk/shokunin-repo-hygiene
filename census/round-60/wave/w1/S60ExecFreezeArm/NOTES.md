# S60ExecFreezeArm — `--substance` arm for tools/souji-freeze-check.py

Candidate: `souji-freeze-check.py` (sha256 928745cd7f294320e6a37551334f32f43eb409728169bb5d8606c8b7054cb24e).
Base: `tools/souji-freeze-check.py` at 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 (sha256 d1ca06fd0fb21d4c7a8452dbbc879f2ecf63ffaaf65378efa3c512e4dbfca364, 415 lines; the lane work tree bytes matched it at run time).

## What the arm checks (opt-in, `--substance`)

For each claim block, if `Control:` resolves to a non-symlink blob at FREEZE and the claim declares a
Counter, the Control receipt blob at FREEZE must carry, as column-0 lines (first occurrence of each key wins,
trailing space/tab trimmed):

- `instrument=<path>`: must equal the declared Counter path. Missing → `CONTROL-INSTRUMENT-MISSING`; different → `CONTROL-INSTRUMENT-MISMATCH`.
- `instrument_sha256=<64 hex>`: must equal sha256 of the declared Counter blob at FREEZE. Missing → `CONTROL-INSTRUMENT-MISSING`; different → `CONTROL-INSTRUMENT-MISMATCH`.
- `rev=<full40>`: missing → `CONTROL-REV-MISSING`; not 40-hex or not resolving to a commit → `CONTROL-REV-INVALID`; resolves but is not a strict ancestor of FREEZE (including FREEZE itself) → `CONTROL-REV-NOT-BEFORE-FREEZE`.
- `command=<text>`: missing → `CONTROL-COMMAND-MISSING`; text does not contain the Counter path → `CONTROL-COMMAND-MISMATCH`.

Every detail string starts with the receipt path (e.g. `census/round-59/before.txt has no instrument= line`).

Without `--substance` the code path is unchanged: `main` passes `substance=False`, `evaluate` skips
`control_substance`, and the default selftest cases are untouched. Verified byte-identical (see below).

## Selftest

- Default `--selftest`: the 41 existing cases, unchanged. `SELFTEST cases=41 pass=41 fail=0`.
- `--selftest --substance`: 12 new cases (`SUBSTANCE_CASES`): 2 accept cases (`substance-clean`, `substance-extra-lines`), and 10 refusal cases covering all seven new classes (instrument-missing ×2 incl. indented, instrument-mismatch, digest-missing→INSTRUMENT-MISSING, digest-mismatch, rev-missing, rev-invalid, rev-not-before, command-missing, command-mismatch). `SELFTEST cases=12 pass=12 fail=0`.
- Negative control (run by hand, not a shipped case): with `substance=False`, all 10 refusal substance cases fail the exact-finding comparison (the observed finding list differs from the expected one), so the expected CONTROL-* findings come only from the flag. The two accept cases pass in both modes by design.

## Byte-identity (default path)

Three real preregistrations at rev 1e8bfd87…: `census/round-59/preregistration.txt`, `census/round-58/...`, `census/round-57/...`. Base and candidate both exit 1; stdout and stderr compared with `cmp`: identical for all three; the default selftest stdout and stderr are also identical to base. Details and exact argv in `byte-identical.txt`.

## Substance on real preregistrations (informational)

`substance-on-real-preregs.txt`: with `--substance`, round-59 gains `CONTROL-INSTRUMENT-MISSING` (its `before.txt` receipt has no `instrument=` line); round-58 and round-57 output is unchanged from base. This is the arm working as designed on real receipts that predate the substance format; the freeze itself is not changed by this run.

## Limits (named)

1. `--selftest --substance` runs only the 12 substance cases, not the 41 base cases. Under `--substance` the base Control fixtures (`x\nEXIT=1`) carry no substance lines and would legitimately change verdict, so mixing them would not be a clean "unchanged" statement. The base 41 remain under plain `--selftest`.
2. Substance checks are skipped (not refused) when the Control blob is missing or a symlink at FREEZE (CONTROL-MISSING / CONTROL-SYMLINK already report those), and when the Counter is missing or a symlink at FREEZE (the instrument digest check is skipped; the `instrument=` path comparison still runs when the Counter path is declared).
3. `rev=` is checked for strict ancestry of the FREEZE commit only, not for being a commit that contains the Counter blob with the stated digest. The digest equality check against the Counter blob at FREEZE is what binds substance.
4. Trailing spaces/tabs are trimmed from substance values; leading spaces are not (the line must start at column 0).
5. `--substance` does not alter the FROZEN-EDITED or DISPATCH logic.
6. The milestone line also names atomic receipt writing (C2). This seat's Target is the freeze-check arm only; `tools/souji-receipt-write.py` is not in this delivery and is owned by another seat.
7. Fixtures use lightweight state only; no network, no pacman, no installs. Tooling: none installed (Python stdlib, git from the host).
8. The matrix seat (S60ExecMatrix) and reviewer seat (S60ReviewerFreeze) were pinged with the candidate path; their results are not part of this delivery.
