# S14 — cluster G member 2 (`cand-g2-*`) — round 10 fragment

**Assignment:** close the r9 cluster-G defect classes (G1 index-write contract,
G2 fresh-descendant) on the S17-patched base, as cluster G member 2.
**Artifacts:** `tools/cand-g2-{verify,vault,quarantine}.sh`,
`census/round-10/S14-g2-build.py`, `census/round-10/S14-cluster-G-fragment.json`.
**Repro used:** `census/round-10/S13-cluster-G-repro.py` (S13, cluster G member 1)
and `census/round-10/S13-candidate-battery.py` (19 cases, independent).

## Pass counts (fresh runs, fixtures under /var/tmp only)

| tool | selftest | R9 runner | G2 false-SAFE | G2 unsafe deletes | G1 index writes |
|---|---|---|---|---|---|
| `souji-verify.sh` (installed) | 40 / 0 failed | 16 / 0 | 6 | 6 | 0 |
| `souji-vault-verify.sh` (installed) | 51 / 0 failed | 16 / 0 | 6 | 6 | 0 |
| `souji-quarantine.sh` (installed) | 91 / 0 failed | 28 / 0 | 6 | 6 | 0 |
| `souji-verify.r9-s18.sh` (r9 banked) | — | — | **1** | 0 | **1 (new)** |
| **`cand-g2-verify.sh` (this seat)** | **45 / 0 failed** | **16 / 0** | **0** | **0** | **0** |
| **`cand-g2-vault.sh` (this seat)** | **55 / 0 failed** | **16 / 0** | **0** | **0** | **0** |
| **`cand-g2-quarantine.sh` (this seat)** | **98 / 0 failed** | **28 / 0** | **0** | **0** | **0** |

All pre-existing selftest cases are ported verbatim; the counts grow only by the
new regression cases (verify +5, vault +4, quarantine +7).

S13's independent 19-case battery, run with the candidates under its expected
`cand-g1-*` naming: installed **0 index violations / 6 false-SAFE / 6 unsafe
deletes / refused=1** → candidates **0 / 0 / 0 / refused=7**.

## Defect classes and what was measured

Both classes were reproduced fresh before any edit; every number below is a
measured run, not a restatement of the r9 report.

| id | class | fresh repro | installed | candidate |
|---|---|---|---|---|
| G2-1 | fresh child under an aged `.scratch` container | `G2-plain` | SAFE(stale), DELETED | NOT-SAFE, retained |
| G2-2 | same, child named in `.gitignore` | `G2-ignored` | SAFE(stale), DELETED | NOT-SAFE, retained |
| G2-3 | same, visible file references the child | `G2-live-ref-child` | SAFE(stale), DELETED | NOT-SAFE, retained |
| G2-4 | same, **hidden** file references the child | `G2-live-ref-child-hidden` | SAFE(stale), DELETED | NOT-SAFE, retained |
| G2-5 | fresh nested directory under an aged container | `G2-fresh-dir-child` | SAFE(stale), DELETED | NOT-SAFE, retained |
| G2-6 | **bytes rewritten, mtime backdated** | `G2-content-fresh-mtime-old` | SAFE(stale), DELETED | NOT-SAFE, retained |
| G1 | index-write contract | S13 G1 suite (5 hostile constructions) | 0 violations | 0 violations |

### Root cause G2

`try_stale` aged the target by **mtime alone** and, for a directory, never looked
at descendants at all. On this host (btrfs, git 2.55.0) `touch -d` / `os.utime`
backdate mtime but leave **ctime** at the real, fresh time — so a rewrite plus
backdate is invisible to an mtime-only test. The fix requires every descendant to
be old by **mtime AND ctime**, which closes G2-1…G2-6.

The ctime rule is deliberately **fail-closed**: a synthetic fixture aged by
backdating is refused too, because it is indistinguishable from the forgery by
any observable. Genuinely old trees (untouched for the whole stale window) carry
old ctimes and still qualify — verified both directions:

- forged/fresh subtree → `NOT-AUTHORIZED`, retained
- genuinely old subtree (`--stale-days 0`) → `SAFE(stale)`, staged, `DELETED`

The ctime rule applies to **descendants only**. A file target keeps the inherited
mtime-only test, which is exactly what the pre-existing stale cases exercise
(verify F7/F8, vault F7/F8, quarantine P2) — this is why all 182 inherited
assertions still pass.

### Root cause G1

Measured with a logging `git` wrapper around every invocation: on a stat-dirty
tracked file, plain `git status --porcelain` **and**
`git diff --quiet --no-ext-diff --no-textconv <ref> -- <path>` create
`.git/index.lock` and rewrite `.git/index`. `GIT_OPTIONAL_LOCKS=0` does **not**
suppress the `diff --quiet` form. `--no-optional-locks`, `diff-index`,
`ls-files`, `hash-object` and `diff --name-only` are read-only.

The installed tools never took the writing form (0 violations measured), so the
G1 work here is a **contract guard**: the repo-root and worktree status probes are
routed through a lock-free helper so a future edit cannot reintroduce the write.

**Note for the parent:** r9's S18 banked candidate is *not* G1-clean — the guard's
`try_pushed` uses the writing `diff --quiet` form and reproduces a fresh
index-write violation on the file target that the installed tool does not have
(S13's repro reports `index_write_violation: ["verify"]` for
`index-stale-stat-file`). Do not install that call shape unmodified.

## Candidate shape

Built from the installed tool bytes by `census/round-10/S14-g2-build.py`, which
injects a late-loaded override block immediately before each tool's main dispatch.
Consequences:

- **Self-contained**: no shared guard file has to ship alongside them.
- Every inherited definition, selftest case, CLI flag and output line is
  preserved; only `try_stale` (verify, vault), `count_live_refs` (both) and the
  status probes are replaced, plus a default-engine pointer for quarantine.
- `cand-g2-quarantine.sh` defaults `SOUJI_VERIFY_BIN` to the hardened sibling
  `cand-g2-verify.sh` when present, so the pair exercises the closed class end to
  end; `SOUJI_VERIFY_BIN` still wins when set.
- Reproducible: `python3 census/round-10/S14-g2-build.py --check` → MATCH.

SHA-256 prefixes: verify `07199a514df9`, vault `92e75bf09c4c`,
quarantine `d08ac3fb6a81`. Installed tools were **not** modified — verify
`4baa8d955c53`, vault `ea43bb0f9b9f`, quarantine `f6f8516c15ab`, census
`11bf9cdf8d4f` (unchanged from the seat's initial snapshot).

## Verification commands

```bash
TMPDIR=/var/tmp bash tools/cand-g2-verify.sh --selftest        # 45 / 0 failed
TMPDIR=/var/tmp bash tools/cand-g2-vault.sh --selftest         # 55 / 0 failed
TMPDIR=/var/tmp bash tools/cand-g2-quarantine.sh --selftest    # 98 / 0 failed
python3 census/round-10/S13-cluster-G-repro.py --tools <dir-with-cand-g2-as-souji-*.sh>
python3 census/round-10/S13-candidate-battery.py --cand <dir/cand-g1-*.sh>
python3 census/round-10/S14-g2-build.py --check
bash -n tools/cand-g2-*.sh && shellcheck -x -S error -P tools tools/cand-g2-*.sh
```

## Boundaries / not claimed

- **In-cluster scope only.** The wider S18 battery (37 cases) moves from 12/37 to
  18/37; the 16 remaining failures are out-of-cluster classes owned by other
  seats (dirty-pushed, detached-unpushed, worktree detached-head, ledger
  self-copy, tab-path injection, quarantine symlink root, vault alias, ignored
  directory payload). Not addressed here.
- **3 battery "compatibility failures" are the intended trade.** The S18 battery's
  `positive-stale-directory` fixture ages its subtree with `os.utime`, i.e. it is
  a backdated forgery by construction, so the ctime rule refuses it. This is the
  documented fail-closed behavior, not an accident.
- The shared round-10 suite (`cand-merge-selftest.sh`) improves for every tool —
  verify 18→21, vault 19→22, quarantine 31→35 pass — but retains pre-existing
  out-of-cluster failures (J01, J03, J05, J07, S15 gitfile). Those are unchanged
  by this seat and belong to other clusters.
- No fleet mutation, no installation, no certification. Candidates are
  **banked for parent selection/composition**; installed safety must not be
  marked fixed merely because these candidates pass.
