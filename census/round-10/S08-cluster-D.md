# S08 — cluster D member 2 (cand-d2-*) — round 10 fragment

**Assignment:** close the r9 defect classes in cluster D (stale-sweep /
worktree-metadata / directory-receipt) on the S17-patched base.
**Artifacts:** `tools/cand-d2-verify.sh`, `census/round-10/S08-cluster-D-repro.py`,
`census/round-10/S08-cluster-D-fragment.py`, `census/round-10/S08-cluster-D-fragment.json`.
**Probe:** `tools/cand-d2-probe.sh` (pre-existing, cases A–J) + the new K–T battery.

## Pass counts (fresh runs, fixtures under /var/tmp only)

| tool | selftest | R9 runner | A–J | K–T | unsafe verdicts |
|---|---|---|---|---|---|
| `souji-verify.sh` (installed, patch base) | 40 / 0 failed | 16 / 0 | 1 pass / 9 defect | 3 pass / 8 defect | **17** |
| `souji-verify.r9-s18.sh` (r9 S18) | 24 / 0 failed | **14 / 2** | 9 / 1 | 9 / 2 | 5 |
| **`cand-d2-verify.sh` (this seat)** | **54 / 0 failed** | **16 / 0** | **10 / 0** | **11 / 0** | **0** |

`unsafe verdicts` = defect lines on both probes plus R9 failures. Zero means every
live-work fixture is refused and every positive control still fires.

## Defect classes closed (fresh repro per class)

| id | class | fixture | installed | candidate |
|---|---|---|---|---|
| D2-1 | reference reachable only via a dotfile (`rg` needs `--hidden`) | A | SAFE(stale) | NOT-SAFE |
| D2-2 | reference inside a binary file (`rg` needs `--text`) | K | SAFE(stale) | NOT-SAFE |
| D2-3 | aged dir with a fresh descendant (recursion depth ≥ 1) | B, P | SAFE(stale) | NOT-SAFE |
| D2-4 | scope name referenced from outside the scope | A, K | SAFE(stale) | NOT-SAFE |
| D2-5 | tracked local-only commit falls through to stale | E | SAFE(stale) | NOT-SAFE |
| D2-6 | unread secret-shaped surface silently claimed `refs=0` | L | SAFE(stale), no disclosure | SAFE(stale) + `unread-secret-shaped-files=N` |
| D2-7 | pushed dir with untracked / ignored / dirty descendant | C, D, G, N, O | SAFE(pushed) | NOT-SAFE |
| D2-8 | commit held only by a hidden ref (`refs/hidden/*`) | F | SAFE(pushed) | NOT-SAFE |
| D2-9 | default-ref snapshot differs from the working tree | E, M | SAFE(pushed) | NOT-SAFE |
| D2-10 | worktree owner not matched by the `*-shokunin` glob | H, R | SAFE(stale) | NOT-SAFE(dirty) |
| D2-11 | worktree HEAD is not a commit object | J | NOT-SAFE(git-unverifiable) | NOT-SAFE(git-unverifiable) (kept) |
| D2-12 | git 2.55 linked-worktree HEAD skew in `unique=0` | I | SAFE(metadata-prune) | NOT-SAFE(none) |
| D2-13 | symlink / unreadable entry inside a removal scope | new | SAFE(stale) | NOT-SAFE(unreadable-or-symlinked-scope) |

**D2-6 is a disclosure, not a refusal.** The province forbids reading secret
content, so the sweep must exclude it; the receipt now names the unread count so
an operator can see the unverifiable surface. Case L2 asserts the clause is not
boilerplate (absent when the surface is empty).

## Two base findings that changed the plan

1. **The r9 S18 candidate is not a drop-in base.** It closes 7/8 cluster-D
   classes but **regresses two r9 ledger-revocation checks** (R9 14/2 vs the
   installed 16/0): its guard's `try_obsidian` drops the ledger re-pin, so a
   ledger rewritten mid-verification can still certify a row. The installed
   (S17-patched) tool keeps that property, so the candidate is built on it.
2. **`git log <sha> --not --all` is unreliable for `unique=0` on git 2.55.**
   `--all` resolves linked-worktree HEADs, so a commit held *solely* by the very
   registration under test counted as reachable and read `unique=0`
   → SAFE(metadata-prune) on a live unique commit (case I). The candidate
   judges ancestry against `for-each-ref` durable refs only, and refuses when
   that query fails.

## Harness robustness

- **Read-only proven:** repo `.git/index`, the target listing, and
  `git status --porcelain` are byte-identical before/after every call, including
  on the live lane repo. H1 source audit: 0 forbidden git subcommands.
- **Host quota hazard:** this host's `/tmp` is quota-limited (r8/r9 incident).
  The candidate's fixtures default to `/var/tmp` and its sweep tempfile is
  fail-closed — an unwritable name list yields `stale=reference-sweep-unverifiable`,
  never `refs=0`. Selftest is **54/0 under both default and `TMPDIR=/tmp` forced**;
  the installed tool's selftest dies with rc=128 under the same condition.
- **Bounded work:** per-descendant sweeps cost one ripgrep per entry (31s on a
  3 600-file scope). The sweep is now one batched `rg -f` over the scope's name
  list (3.6s, ~9x faster) plus `D2_MAX_SCOPE` (default 20000) as a fail-closed
  ceiling.
- **Quarantine interop:** used as `SOUJI_VERIFY_BIN`, the candidate drives
  `tools/souji-quarantine.sh` dry-run to `DRY-RUN-PASS` on the same fixture the
  installed engine passes, with a stricter stage-1 evidence string.
- **Repeatability:** normalized probe output and selftest identical across runs.

## Boundaries and what is left

- Only `cand-d2-*` files and my `census/round-10/S08-*` fragment were written.
  No live fleet path was mutated; no installed tool was replaced.
- **Not done:** the candidate is one seat's proposal — promotion to
  `tools/souji-verify.sh` is the parent's composition decision, and cluster D
  coverage does not by itself certify the quarantine/vault/census tools.
- `D2-6` leaves a residual, disclosed gap: a reference that exists *only* inside
  a secret-shaped file is still not readable by this lane. That is a province
  boundary (kagi owns credentials), reported rather than worked around.
- Classes A–J were re-verified fresh; the pre-existing probe was not modified.
