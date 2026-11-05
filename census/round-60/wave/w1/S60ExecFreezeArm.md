# S60ExecFreezeArm — round 60 findings

Delivery dir: `.ufo/waves/round-60/w1/S60ExecFreezeArm/`
- `souji-freeze-check.py` (candidate, sha256 928745cd7f294320e6a37551334f32f43eb409728169bb5d8606c8b7054cb24e, 530 lines)
- `selftest-default.txt`, `selftest-substance.txt`
- `byte-identical.txt`: base vs candidate, three real preregistrations at 1e8bfd87…, exact argv
- `substance-on-real-preregs.txt`: informational `--substance` output on the same three
- `NOTES.md`: arm semantics and named limits

## Verbatim SELFTEST lines

- default: `SELFTEST cases=41 pass=41 fail=0`
- `--substance`: `SELFTEST cases=12 pass=12 fail=0`

## Byte identity without the flag

Base tool at 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 (`git cat-file blob`, sha256 d1ca06fd…, 415 lines) and the candidate were run as `python3 -B <tool> --root <lane> --prereg census/round-{59,58,57}/preregistration.txt --rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4`. Stdout and stderr compared with `cmp`: identical for all three. Exit codes 1, 1, 1 for both. Default selftest stdout/stderr identical to base (`SELFTEST cases=41 pass=41 fail=0`, exit 0).

## Commands and results

- base extraction + run: `bash` driver in scratch (base-selftest exit 0; base r59/r58/r57 exit 1)
- candidate run: `python3 -B <cand> --selftest` exit 0; `python3 -B <cand> --selftest --substance` exit 0
- candidate real runs: exit 1 for r59, r58, r57 (default and `--substance`)

## Findings from the arm

- `--substance` on round-59 gives `FINDING C1 CONTROL-INSTRUMENT-MISSING census/round-59/before.txt has no instrument= line`: its receipt predates the substance format. Round-58 and round-57 `--substance` output equals their base output.
- Negative control: the 10 refusal substance cases fail the exact-finding comparison when run without the flag; the two accept cases pass in both modes.

## Limits

See `NOTES.md`. Main ones: substance selftest runs its 12 cases only (base 41 under plain `--selftest`); the receipt writer (C2) is not in this seat's delivery; no shims or fallbacks.

## Pings

Candidate path announced to S60ExecMatrix and S60ReviewerFreeze on the coop channel after delivery.

## Tools

No tools installed. Host Python 3 (stdlib) and git used read-only in the lane; fixture repos created under scratch only.
