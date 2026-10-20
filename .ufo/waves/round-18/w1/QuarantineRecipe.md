STATUS: DONE — Quarantine commit recipes now use the owning lane identity or an explicit unknown-owner placeholder.

## Axis
- Operability: avoid emitting a hard-coded lane identity that `jj-lane.sh` refuses.

## Change
- `tools/souji-quarantine.sh:246-279`: `q_jj_commit_recipe` reads `user.name` with `jj --ignore-working-copy -R <repo> config get user.name` when `jj` is available; it uses the suffix-stripped ID when valid, otherwise falls back to the Git top-level basename ending in `-shokunin`. If neither yields a valid lane ID, the recipe contains literal `--as <owning-lane-id>` and stderr says the owner is unknown. Dynamic recipe arguments remain `%q`-quoted.
- `tools/souji-quarantine.sh:1564-1594`: added selftest cases for colocated `kama-shokunin`, an unknown-named repo, and `souji-shokunin`. This adds three assertions: base count 101 → expected count 104. The selftest was not run in this editing wave.

## Retained evidence
- `scripts/hyaku/jj-lane.sh:105-110` derives the lane ID from `user.name` ending in `-shokunin`.
- `scripts/hyaku/jj-lane.sh:516-517` accepts only that lane ID or `protocol` for `--as`.
- The prior implementation at `tools/souji-quarantine.sh:246-251` hard-coded `--as souji`.

## Commands and outputs
- `git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18-QuarantineRecipe/lane && git -C /var/tmp/souji-r18-QuarantineRecipe/lane checkout --quiet --detach b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` — exit 0; no stdout/stderr.
- `git -C /var/tmp/souji-r18-QuarantineRecipe/lane diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-quarantine.sh > /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-18/w1/QuarantineRecipe.patch` — exit 0; diff captured at the stated path, no stdout/stderr.
- `TMPDIR=/var/tmp bash /var/tmp/souji-r18-QuarantineRecipe/lane/tools/souji-quarantine.sh --selftest`, `bash -n`, and `shellcheck` were not run; wave policy assigns verification to the integration owner.

## Verdict, risk, and smallest follow-up
- Verdict: partial verification. The requested implementation and three assertions are present; runtime checks are unobserved. The new assertions force `jj` lookup to fail so they exercise basename fallback, not the successful `jj` identity branch.
- Risk: the successful `jj` configuration path and full selftest remain unverified in this lane.
- Smallest follow-up: integration owner runs the authorized selftest, `bash -n`, and `shellcheck`; no other implementation change is indicated by retained evidence.
- Blockers: none.
