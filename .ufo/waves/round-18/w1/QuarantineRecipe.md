STATUS: PARTIAL — The local-only lane-id fix and requested behavior tests pass; ShellCheck exits nonzero on existing diagnostics outside the edited regions.

## Axis
- Operability: a printed `jj-lane.sh` recipe must bind only to the repository's own lane identity, never inherited global configuration.

## Change
- `tools/souji-quarantine.sh:252-279`: read `lane.id` using `git -C <repo> config --local --get lane.id`; reject malformed IDs, then fall back to the Git top-level basename ending in `-shokunin`, then to `--as <owning-lane-id>` plus an owner-unknown stderr note. Dynamic recipe values remain `%q`-quoted.
- `tools/souji-quarantine.sh:1566-1628`: preserved the four lane.id/basename/unknown/souji cases. Added isolated conflicting-global coverage for a repo with no local ID, plus invalid-local-ID coverage for both basename fallback and unknown-owner placeholder. The initial b576341 selftest count was 101; the 5efb519 base already had four R1 assertions (105), and this patch adds three more. The observed total is 108.

## Retained evidence
- `scripts/hyaku/jj-lane.sh:445-449` records `lane.id` with `git config` during lane initialization; `scripts/hyaku/jj-lane.sh:613-615` enforces the repo's lane ID or `protocol` for `--as`.
- `corpus/QUALITY.md:78` identifies the J13 fixture command. `tests/fixtures/r17-jj-receipts.sh:751-775` defines J13/J13-own recipe checks.
- The exact 5efb519 base resolved to `5efb519f00075d958c3d1109ef6fcb24c487eb87`.

## Commands and outputs
- `git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18-QuarantineRecipeFix/lane && git -C /var/tmp/souji-r18-QuarantineRecipeFix/lane checkout --quiet --detach 5efb519f00075d958c3d1109ef6fcb24c487eb87` — exit 0; no stdout/stderr.
- `TMPDIR=/var/tmp bash /var/tmp/souji-r18-QuarantineRecipeFix/lane/tools/souji-quarantine.sh --selftest` — exit 0; `selftest: 108 checks, 0 failed`.
- `bash -n /var/tmp/souji-r18-QuarantineRecipeFix/lane/tools/souji-quarantine.sh && shellcheck /var/tmp/souji-r18-QuarantineRecipeFix/lane/tools/souji-quarantine.sh` — `bash -n` passed silently; ShellCheck ran and exited 1 after reporting SC2016, SC2015, and SC2329 informational diagnostics in untouched code (lines 802, 913–1425, 1770); no diagnostic points to the changed function or selftest block.
- In `/var/tmp/souji-r18-QuarantineRecipeFix/lane`, `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` — exit 0; `CASE J13 PASS`, `CASE J13-own PASS`, `SUMMARY total=35 failed=0 skipped=2`.
- `git -C /var/tmp/souji-r18-QuarantineRecipeFix/lane diff 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- tools/souji-quarantine.sh > /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-18/w1/QuarantineRecipeFix.patch` — exit 0; diff delivered at the stated path, no stdout/stderr.

## Verdict, risk, and smallest follow-up
- Verdict: requested recipe behavior, selftest, and J13 checks hold. ShellCheck is not clean because it exits 1 on informational diagnostics outside the changed regions.
- Risk: those existing ShellCheck diagnostics remain in this base; they were not broadened into this owned-file fix.
- Smallest follow-up: integration owner may decide whether the untouched ShellCheck findings merit separate work; no additional change to this assignment is indicated.
- Blockers: none.
