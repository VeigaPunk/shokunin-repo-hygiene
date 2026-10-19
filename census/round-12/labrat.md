# r12 labrat — git 2.55 auto-maintenance gate (final state)

Author: W2RoundSouji-8.R12Labrat (L2, read-only); transcribed verbatim by the L1 from its final output (session-scoped `agent://W2RoundSouji-8.R12Labrat`; this committed copy is the durable form). 2026-10-19.

`--selftest` now performs a real assertion, not a re-run.

**Change:** `SELFTEST_EXPECTED_IDS` is pinned in the script (`SOUJI-R12-MAINT-{plain-commit-sync,plain-commit-default,auto-off,locked,fresh,maintenance-auto}`); `selftest_check` diffs the emitted `id=` set against it and requires every verdict PASS, printing `selftest=PASS ids=6/6` or `selftest=FAIL ids=<got>/<want> missing=[…] extra=[…] failed_verdicts=<n>` as the last line; mismatch exits 1. Exit map stays 0/1/2 (clean/failed/could-not-evaluate), `shellcheck -S warning` exit 0.

**Verified (git 2.55.0):** third run byte-identical to runs 1–2, all six cases PASS (`plain-commit-sync 2→1`, `plain-commit-default 2→1`, `auto-off 2→2`, `locked 2→2`, `fresh 2→2`, `maintenance-auto 2→1`); `selftest=PASS ids=6/6` with exit 0; exit codes run1=0 run2=0 run3=0, selftest=0, unknown-arg=2. Drift probes on script copies: pinned-id deleted → `ids=6/5 extra=[SOUJI-R12-MAINT-fresh]` rc=1; case renamed → `missing=[…fresh] extra=[…fresh-x]` rc=1; expect mismatch → `failed_verdicts=1` rc=1.

**Results** `tests/results/r12-maintenance-guard.txt` overwritten (date, git version, shellcheck, gate exit codes, third-run stdout+stderr, selftest transcript, unknown-arg gate, reachability probe retaining `rev_parse=OK / refs=[] / reflog=0 / unreachable → present after 2.weeks prune, absent after --prune=now`). Generator scratch dir removed; no stray `/var/tmp/souji-r12-{gen,results,maintenance}.*` dirs remain. Reply with these outputs sent to `W2RoundSouji-8`.


## First result (hypothesis run, before the critic-driven hardening) — verbatim

**Verdict: CONFIRMED (with one refinement).** git 2.55.0, Linux x86_64, 2026-10-19.

Per-case numbers (third run, identical across all 3 runs): plain-commit 2→1 (expect 1, PASS); auto-off 2→2; locked 2→2; fresh 2→2; maintenance-auto 2→1.
Mechanism (trace2): plain `git commit` → `git maintenance run --auto --quiet --no-detach` → `git worktree prune --expire 3.months.ago`. `maintenance.auto=false` suppresses the maintenance child; `worktree lock` and an index younger than 3 months both hold at 2.

**Refinement:** the expiry clock is `.git/worktrees/<id>/index` mtime, **not** `gitdir` — aging only `index` prunes (2→1), aging only `gitdir` does not (2→2).

**Commit reachability after prune** (`detached_commit=e6d3fa5c…`): `rev-parse --verify <sha>^{commit}` OK, `for-each-ref --contains` empty, `reflog --all` zero hits, `fsck --unreachable` lists the commit; `gc --prune=2.weeks.ago` leaves it present, `gc --prune=now` makes it absent. So the detached commit is unreferenced but recoverable until `gc.pruneExpire` — ART's loss [INFERENCE] is "orphaned now, not deleted immediately".

Incident disclosed by this seat: its first probe ran with cwd = the fleet root (silent `cd` failure) — 4 commits c095ea1, 551478a, 4b2123b, b21278d on fleet-root master; throwaway registrations wt-a/wt-b created under /home/vgpnk/Projects/ with dirs removed, then pruned by maintenance; no reset/rebase performed (corpus/lessons/round-12.md `## Incident`).
