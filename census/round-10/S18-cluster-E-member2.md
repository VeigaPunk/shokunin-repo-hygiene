# Round 10 — S18, cluster E member 2 (git-error zero-counts, locale folding, git-2.55 worktree HEAD skew)

Fixture policy: every case builds a fresh fixture under `mktemp -d -p /var/tmp`.
No live fleet path is read or written; the live lane repo is only read for
`bash -n` / `shellcheck` / source greps. No live artifact was quarantined or
removed.

## Patch base and candidates

Installed (S17) tools measured at:

```
4baa8d955c531fcc73edc6b62021cb9531a31e1baed8aa853ba957b204d1cfc1  tools/souji-verify.sh
ea43bb0f9b9fe96cc26451df1a41d2df97d2d044852f122c987c209b6ec7b7a7  tools/souji-vault-verify.sh
f6f8516c15ab654f7e5f2dc2a7840eef0b53b9f9433e2ff70a64490b35fde68f  tools/souji-quarantine.sh
11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381  tools/souji-census.sh
```

Candidates produced by this seat (full source, installed bytes + the E fixes):

```
881ae5adb8d5c01d1c559e46bdfe536584a63c4b14c2ddc08ab59b3830ddd306  tools/cand-e2-verify.sh
4a9cec0d81dc54889aafcc9999c44a116b8ab45d1d4958f72919d6b5cb95050d  tools/cand-e2-vault.sh
69f6ce9f95cc07bea6760fb0c9b7616c3250a42b953390f24c7ed75aa04118ac  tools/cand-e2-quarantine.sh
```

Full manifest incl. evidence scripts: `census/round-10/S18-cluster-E-member2.sha256`.

## Selftest counts

| tool | installed (S17) | candidate | new checks |
|---|---:|---:|---:|
| souji-verify / cand-e2-verify | 40 / 40 | **53 / 53** | 13 |
| souji-vault-verify / cand-e2-vault | 51 / 51 | **64 / 64** | 13 |
| souji-quarantine / cand-e2-quarantine | 91 / 91 | **134 / 134** | 43 |
| souji-census (untouched) | 32 / 32 | — | 0 |

All candidate suites exit 0. Every pre-existing case is ported: the tools' own
F1–F10/E1–E8/H1–H6 (verify), V-series/H-series (vault), the P/S/D/U/A/H-series
(quarantine), **and** the r9 shared helper battery, which still passes on the
candidates: `ROUND9 16 0` (verify), `ROUND9 16 0` (vault), `ROUND9 28 0`
(quarantine). Raw output: `census/round-10/S18-selftest-counts.txt`.

No regression check is vacuous: the E-cluster cases were written against fresh
repros that the installed bytes fail (see below), so a suite that passes only
because the assertion is weak would show up as an installed-tool pass.

## Defects confirmed on the installed (S17) tools

Baseline evidence: `census/round-10/S18-installed-baseline.txt`.
Patched evidence: `census/round-10/S18-candidate.txt`.

**E1-A (unsafe DELETE, HIGH).** `git_dirty_tracked` ended in `|| true`, so a
*failed* `git status` query produced empty output, which the r7 gate2 read as
"clean". A tracked file whose only change was a mode bit is invisible to the
intro-blob comparison, so the porcelain gate was the sole control: with the
query failing, the tool staged and deleted it.

```
installed : RESULT <path>/mode.txt  DELETED         pushed  ... prong1=NOT-SAFE(none) prong1-tolerated
            survives: NO-DELETED
candidate : RESULT <path>/mode.txt  NOT-AUTHORIZED  dirty-tracked  r10-gate2 status query failed (rc=128)
            survives: YES
```

The control (no shim) correctly blocked in both cases with `r7-gate2 porcelain= M mode.txt`,
so the pre-existing gate is sound; only the failure path was wrong.

**E1-B (false SAFE, HIGH).** `try_pushed`'s r6 "no unpushed commit touches the
path" check was `git … | wc -l`, which returns 0 on a *failed* query and made
the veto read as satisfied. With `--branches` failing, a pushed file still
earned `SAFE(pushed)` in both engines.

```
installed : verify SAFE(pushed)  intro=… ref=refs/remotes/origin/main ancestor=yes
            vault  SAFE(pushed)
candidate : verify NOT-SAFE(git-unverifiable)  pushed=unpushed-touching-unverifiable
            vault  NOT-SAFE(none)              pushed=unpushed-touching-unverifiable
```

Quarantine's second check already status-checked this query (it recorded
`class=FAIL unpushed-touching=unverifiable` and aborted), so this half of the
class was a verifier-only defect. `evaluate_repo_root` had the same shape in
both engines (failed queries reported `unpushed=0 dirty=0`); now it refuses with
`git-unverifiable` / `repo-root state query failed`.

**E2 (defence-in-depth, no live repro).** The three tools already `export
LC_ALL=C` at startup and a genuinely compiled `tr_TR.UTF-8` locale did **not**
produce a false SAFE: all six case variants (`ID_RSA`, `id_rsa`, `Id_Rsa`,
`.ENV`, `credENTIALS`, `my-secret.pem`) were refused by all three tools. I could
not produce an unsafe outcome, so this is **not counted as a confirmed defect**.
The residual exposure is that the `id_*` invariant depended on process-global
state rather than being local to the comparison; the fold is now performed in a
subshell with `LC_ALL=C` pinned, and the fixture proves the locale is genuinely
active before asserting refusal (`fold(ID_RSA)=ıd_rsa`).

**E3 (unsafe metadata-prune recommendation, HIGH — r9 J19).** On git 2.55.0
`git log <commit> --not --all` consults every linked-worktree HEAD, *including
the candidate registration's own*. A detached worktree holding a private commit
therefore counted `unique=0` and earned `SAFE(metadata-prune)`; acting on that
receipt and GC-ing loses the commit (r9's fixture-loss class).

```
fixture   : --not --all = 0   refs-only (--not --branches --not --remotes --not --tags) = 1
installed : verify SAFE(metadata-prune)  dir=absent unique=0
            vault  SAFE(metadata-prune)  dir=absent unique=0
candidate : verify NOT-SAFE(none)        dir=absent unique=1
            vault  NOT-SAFE(none)        dir=absent unique=1
            quarantine stage1 NOT-AUTHORIZED  (stage1=NOT-SAFE(none))
```

`--exclude=HEAD`, `--single-worktree` and `rev-list` all still returned 0, so
the exclusion cannot be expressed by patching the `--all` form; the fix counts
against explicit ref spaces instead. The legitimate dead-registration control
(a registration whose HEAD is on the pushed default ref) still returns
`unique=0` → `SAFE(metadata-prune)`, so the metadata-prune receipt is not
blanket-disabled.

## Files changed by this seat

- `tools/cand-e2-verify.sh` — added `git_count` / `git_unique_count`; status-checked
  the unpushed-touching veto in `try_pushed`; `evaluate_repo_root` refuses on
  failed state queries; worktree unique count moved off `--not --all`;
  locale-pinned `is_secret_shaped`; `st_e_cluster` regression block.
- `tools/cand-e2-vault.sh` — same five fixes mirrored with `R_REASON`; own
  `st_e_cluster` block adapted to the vault output contract.
- `tools/cand-e2-quarantine.sh` — `git_dirty_tracked` no longer swallows the
  exit status and the stage-1 gate blocks on failure; `git_count` added;
  locale-pinned `is_secret_shaped`; `st_e_cluster` block.
- `census/round-10/S18-cluster-E-member2.{md,sha256}` — this fragment + manifest.
- `census/round-10/S18-{e1,e1q,e2,e3}-*.sh`, `S18-{installed-baseline,candidate,selftest-counts}.txt`
  — the runnable repros and their captured output.

No other repository path was written. `LOG.md`, `SCORECARD.md`, `AGENTS.md`,
`SKILL.md`, the installed `tools/souji-*.sh` and the live fleet are untouched.

## Safety and limits

- Every destructive call ran inside a `mktemp -d -p /var/tmp` fixture; the
  failing-`git` shims exist only inside those fixtures.
- `bash -n` and `shellcheck -S error` are clean on all three candidates; the
  source audit finds 0 forbidden git subcommands (no fetch/push/commit/branch/
  checkout/reset/rebase in executable lines).
- Live lane porcelain and `LOG.md` are unchanged and no live `.ufo-quarantine`
  exists (asserted by the quarantine suite's H3 checks).
- **Not claimed:** these candidates close the E1/E3 manifestations above, not
  the other 14 open r9 root classes (J01–J08, J12, J14, J15, J17, J19's
  remaining variants, J20, J22, J23) and not arbitrary check-to-delete races.
  No certification or deletion authorization is asserted by this fragment.
- Quarantine's stage 1 delegates to the receipt engine, so E3's benefit there
  requires the merged build to pair it with a fixed verifier; the regression
  pins this by setting `SOUJI_VERIFY_BIN` to the sibling candidate.
