# S12 (round 8) — quarantine-flow runner fragment

Seat S12, runner. Built + ran the quarantine-flow state machine end-to-end on
mktemp fixtures; live fleet only probed via --dry-run. Full evidence:
`results/qrun-12.json` (transcript `/tmp/s12-qrun-transcript.log`, driver
`/tmp/s12-driver.sh`, both outside the repo and now disposable).

## What exists now

`tools/souji-quarantine.impl-S12.sh`
(sha256 `06e2530794ee84e29fa15fbdde30f587270e5ec6783290ff512c40142f52d850`)
turns the AGENTS.md removal flow into executable state:
receipt (`tools/souji-verify.sh` is the engine of record, sha
`a91049c9…`) → stage (copy into `.ufo-quarantine/<entry>/payload`, digest
re-verified before the original is unlinked, `manifest.tsv` rides along) →
hold (default 86400s) → second receipt check (re-derives evidence: stale
live-ref sweep, pushed still-on-origin, obsidian vault re-hash; plus payload
digest + origin-not-recreated) → release (re-checks internally, appends
`RELEASES.log`, then removes) | restore (byte-identical return).

Safety: every mutating subcommand requires root AND target inside
`SOUJI_QUARANTINE_ALLOW` → else rc=3 `LIVE-TREE-LOCKED` before the target is
read. Dry-run works anywhere, writes nothing. Release/restore refuse when the
origin path was recreated — fail-safe pair, no release and no overwrite.

## Evidence (commands + observed)

- `--selftest` → **26 checks, 0 failed** (rc=0). First run was 20/26 failed;
  root causes fixed in-round: inverted `case`-inside-`if` receipt gate
  (refused every SAFE target), selftest assertions matching the tool's own
  help text (false PASSes), trap/local under `set -u`, wrong grep literal.
- Runner matrix (10/10 PASS): pushed / stale / moved-to-obsidian full flows
  end in `RELEASED` + origin-absent; dirty, live-refs, secrets, lock, hold,
  origin-recreated all refuse with rc 4/3/5 and leave origin intact; restore
  returns sha256-identical bytes.
- Live dry-run probes: `souji-shokunin/results/.write-probe` → refused
  (`stale=not-scratch-type`); `kotodama-shokunin/.scratch` → refused
  (`stale=mtime-age-days=0<=1`). Both consistent with r7's "receipts deny
  everything". Mutation proof: `git status --porcelain | sha256sum` identical
  before/after (`5bda2a1a…`), probe file mtime/size unchanged.

## Fixes to shared understanding (found by running)

1. RELEASES.log audit hole fixed in-round: it wrote the entry id in the
   target column and lost the canonical path on removal; now logs
   `entry= target= receipt= sha256= evidence=`.
2. Lock-before-read ordering for mutating stage (a locked tool must not even
   read the target).
3. Second-check semantics deviation (V-a in qrun-12.json): the engine cannot
   re-verify a staged-away path, so check re-derives evidence with the
   engine's own primitives; stage still uses the engine verdict as receipt of
   record.

## Gate-opening runbook (seed, for the parent's runbook lane)

For an operator-authorized target T:
1. `--dry-run stage T` (read-only verdict);
2. `SOUJI_QUARANTINE_ALLOW=<approved-root> --hold-seconds 86400 stage T`;
3. `status`; 4. after hold: `check <entry>`; 5. `release <entry>`
(re-checks internally, appends RELEASES.log). Abort: `restore <entry>`.
Live fleet stays locked unless the operator allow-lists a root.

Claims: quarantine flow EXERCISED on fixtures (met); zero live mutation
(met); live gate-opening remains blocked on operator sign-off / lane pushes /
remote creation (r7 boundary unchanged) — nothing forced.
