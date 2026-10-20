STATUS: DONE — wave-2 revision landed: shared `jj_keep_novel` now compares leaf blobs (directory-safe) via a single fixed-string grep (SIGPIPE-safe), broken keep names fail closed, un-prefixed rel guarded; verify selftest 49/0, vault 57/0, quarantine 101/0, fixture SUMMARY total=35 failed=0.

# VerifyJjRoots — souji-verify.sh jj-colocated receipt roots (L1 REVISED C3, wave-2 round)

Own: tools/souji-verify.sh (+136 net vs HEAD incl. selftest), plus the identical
`jj_keep_novel` body and caller guard applied to tools/souji-vault-verify.sh and
tools/souji-quarantine.sh (idle owners reassigned by L1; only helper + call
sites + the dead `try_pushed` revert touched there). Helper body sha256 is
identical in all three files (`7fc7cc63…`).

## Wave-2 implementation

`jj_keep_novel` (new body, identical ×3):

```bash
jj_keep_novel() { # $1 repo, $2 path relative to the repo root
  local repo=$1 rel=$2 c o known objs=""
  [ -n "$(git -C "$repo" for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ 2>&1)" ] || return 1
  if ! known=$(git -C "$repo" rev-list --objects --remotes -- "$rel" 2>/dev/null | cut -d' ' -f1); then
    return 2
  fi
  if ! c=$(git -C "$repo" rev-list "--glob=refs/jj/keep/*" --not --branches --tags --remotes -- "$rel" 2>/dev/null); then
    return 2
  fi
  while IFS= read -r c; do
    [ -n "$c" ] || continue
    o=$(git -C "$repo" ls-tree -r --format='%(objectname)' "$c" -- "$rel" 2>/dev/null) || return 2
    [ -n "$o" ] && objs+=$o$'\n'
  done <<< "$c"
  [ -n "$objs" ] || return 1
  grep -Fxvq -f <(printf '%s\n' "$known") <<< "${objs%$'\n'}" && return 0
  return 1
}
```

Mapping to findings:
- F1/F2 (SIGPIPE under pipefail + O(K×N)): candidates are collected into
  `objs`; one `grep -Fxvq -f <(known)` checks them all. `grep` reads its
  pattern file to EOF, so no early-exit SIGPIPE exists. `<(…)` is process
  substitution (outside pipefail), and `&& return 0` in a `||`-guarded
  function is exit-safe.
- Directory over-refusal (CriticC3Coverage2 §2): `ls-tree -r` yields leaf
  blobs under `rel`, so a directory tree that merely recombines pushed blobs
  is not novel; file targets yield the same single blob; deletions yield
  nothing (not novel). ls-tree failure -> 2 (history-unverifiable), stricter
  than sentinel's proposed `continue`.
- F3 (broken keep ref name hidden by probe): probe is `2>&1` — a
  `warning: ignoring ref with broken name` on stderr counts as "keep refs
  exist", so `rev-list` then fails -> rc 2 -> history-unverifiable. Plain
  repos still print nothing -> byte-identical.
- F6 (un-prefixed rel fail-open): verify :729-730
  `if [ "$rel" = "$target" ]; then jjrc=2; else jjrc=0; jj_keep_novel…`;
  vault :923-925 mirrors with `jjrel`. Quarantine's live callers keep `REL`
  (always relative). Quarantine's DEAD `try_pushed` (no caller) was reverted
  to 5fa6017 bytes — verified `diff` empty.
- Stale comments updated: verify r17 header, vault r17 header + pre-helper
  doc, quarantine r17 header + pre-helper doc now describe leaf-blob
  semantics; the quarantine `# Q8 bounds (r13)` heading and a duplicated
  vault tail line were repaired (all three files still `bash -n` clean).

## Selftest additions (souji-verify.sh, plumbing only)

- J6 SAFE(pushed): keep-only commit whose `jj/dirsw` tree is a never-pushed
  combination of two already-pushed dirsw blobs — the exact directory
  recombination shape.
- J7 NOT-SAFE jj-keep-novel: keep-only commit adds a novel blob under
  `jj/dirnv`.
- J8 NOT-SAFE history-unverifiable: repo whose only refs/jj/keep entry is a
  broken-name loose ref written directly (`refs/jj/keep/has space`).
- J9 SAFE(pushed): `sigpipe-shokunin` with 2500 `rev-list` commits touching
  `jj/sig.txt` (`known` >64 KiB) and a keep-only commit carrying the most
  recent pushed blob — the F1 false-refusal shape, now a permanent detector.

`--selftest`: **49 checks, 0 failed** (45 + J6..J9), `ROUND9 16 0`, ~2.7 s.

## Sibling selftests (copies under /var/tmp/souji-r17-VerifyJjRoots/w2copy)

- souji-vault-verify.sh: **57 checks, 0 failed**, ROUND9 16 0.
- souji-quarantine.sh: **101 checks, 0 failed**, ROUND9 28 0 (copy-root
  `.git` precondition per MutateJjNovel's documented setup).
- shellcheck `-S warning`: 5 / 6 / 0 findings respectively — same count set
  as base for each file; none in new lines.
- `bash -n` on all three: OK.

## Committed fixture (ALLOWED-EXEC)

`tests/fixtures/r17-jj-receipts.sh --tool-dir …/tools --baseline-dir
/var/tmp/souji-r17-L1/base` (baseline = 5fa6017 tool bytes):

`SUMMARY total=35 failed=0 skipped=0` — includes J10 (dir recomposition
SAFE), J11 (dir novel refuses), J12 (missing-object keep →
history-unverifiable), J13 (non-commit keep refs unchanged), J14 (>64K
known objects, identical blob → SAFE), J15 (side-remote published blob →
SAFE), J6/J8 byte-identity vs the 5fa6017 baseline, J9 real-jj cases.

## Survivor map (MutateJjNovel)

- M05/M11/M17 (failure path): killed by J12 fixture + verify selftest J8.
- M06/M12/M18 (directory skip): killed by J10/J11 fixture + J6/J7 selftest.
- M03 (verify --branches): verify J2 detector already existed.
- M09/M15 (vault/quarantine --branches-vs-remotes): fixture J15 now kills;
  vault/quarantine selftest side-remote detectors NOT added (L1 scoped me to
  helper + call sites there; the committed fixture covers the path).
- F2 liveness (50k×100k): single-grep makes it O(N+K)+K forks — Sentinel's
  table showed 51 s→3 s and 300 s→53 s; no selftest for the 50k case (cost),
  J9 covers the correctness axis at 2.5k scale.

## Sandbox

/var/tmp/souji-r17-VerifyJjRoots retained (w1 sandbox outputs, rep/ fixture,
w2copy/ tool copies with their `.git` precondition, tools-qbase, fit/).
/var/tmp/souji-r17-L1/base holds the 5fa6017 baseline tools used by the
fixture run. Delete both on admission.
