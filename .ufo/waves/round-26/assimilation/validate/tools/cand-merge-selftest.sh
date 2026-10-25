#!/usr/bin/env bash
# cand-merge-selftest.sh — round-10 S15 composer merged selftest helper.
#
# Usage: bash tools/cand-merge-selftest.sh <verify|vault|quarantine> <tool-path>
#
# Ports every pre-existing shared case (the r9 helper's R9 battery: nested
# stale/pushed/gitfile, failed worktree queries, read-only index, tr_TR
# locale, ledger revocation, NUL list rows, default-ref rollback/missing) and
# adds one regression case per adjudicated r9 defect class J01-J23 that is
# expressible against this tool kind.
#
# Fixtures live under /var/tmp only (mktemp -d -p /var/tmp). No live fleet
# path is read or written.
set -euo pipefail

CM_KIND=${1:?tool kind required}
CM_SELF=$(readlink -f -- "${2:?tool path required}")
case "$CM_KIND" in verify|vault|quarantine) : ;; *) exit 2 ;; esac
CM_TMP=$(mktemp -d -p /var/tmp souji-r10-selftest.XXXXXX)
trap 'rm -rf -- "$CM_TMP"' EXIT
CM_PATH=$PATH
CM_GIT=$(command -v git)
CM_SHA=$(command -v sha256sum)
CM_PASS=0 CM_FAIL=0 CM_OUT="" CM_RC=0
CM_HEADER=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
export TMPDIR=/var/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=souji-selftest GIT_AUTHOR_EMAIL=souji-selftest@fixture.invalid
export GIT_COMMITTER_NAME=souji-selftest GIT_COMMITTER_EMAIL=souji-selftest@fixture.invalid
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE

cm_check() {
  if [ "$2" = 1 ]; then
    CM_PASS=$((CM_PASS + 1)); printf 'PASS CM %s\n' "$1"
  else
    CM_FAIL=$((CM_FAIL + 1)); printf 'FAIL CM %s: rc=%s output=%s\n' "$1" "$CM_RC" "$CM_OUT"
  fi
}

cm_expect() {
  local ok=0
  if [ "$CM_RC" = "$2" ] && [[ "$CM_OUT" = *"$3"* ]]; then ok=1; fi
  cm_check "$1" "$ok"
}

cm_commit() {
  local repo=$1 parent=${2:-} tree sha
  git -C "$repo" add -A
  tree=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf 'fixture\n' | git -C "$repo" commit-tree "$tree" -p "$parent")
  else
    sha=$(printf 'fixture\n' | git -C "$repo" commit-tree "$tree")
  fi
  git -C "$repo" update-ref refs/heads/main "$sha"
  printf '%s' "$sha"
}

cm_push() {
  local repo=${2:-$CM_REPO}
  git -C "$repo" update-ref refs/remotes/origin/main "$1"
  git -C "$repo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
}

cm_new() {
  CM_CASE="$CM_TMP/$1" CM_OUT="" CM_RC=0
  CM_FLEET="$CM_CASE/fleet"
  CM_REPO="$CM_FLEET/case-shokunin"
  export PATH="$CM_PATH" LC_ALL=C HOME="$CM_CASE/home"
  unset SOUJI_Q_TEST_HOOK SOUJI_QUARANTINE_ALLOW_LIVE
  mkdir -p "$CM_FLEET" "$HOME"
  git init -q --initial-branch=main "$CM_REPO"
  printf 'pushed seed\n' > "$CM_REPO/seed.txt"
  CM_BASE=$(cm_commit "$CM_REPO")
  cm_push "$CM_BASE"
  export SHOKUNIN_ROOT="$CM_FLEET" SOUJI_Q_SHOKUNIN_ROOT="$CM_FLEET"
  export SOUJI_LEDGER="$CM_CASE/ledger.tsv" SOUJI_Q_LEDGER="$CM_CASE/ledger.tsv"
  # Engine resolution: an explicit CM_VERIFY_BIN wins; a composed candidate is
  # exercised against its own merged sibling engine (the pair is the deliverable,
  # so pinning it to the installed engine would measure the unmerged lineage);
  # anything else uses the installed sibling, as before.
  if [ -n "${CM_VERIFY_BIN:-}" ]; then
    SOUJI_VERIFY_BIN="$CM_VERIFY_BIN"
  elif [ "$(basename -- "$CM_SELF")" = cand-merge-quarantine.sh ] \
    && [ -f "$(dirname -- "$CM_SELF")/cand-merge-verify.sh" ]; then
    SOUJI_VERIFY_BIN="$(dirname -- "$CM_SELF")/cand-merge-verify.sh"
  else
    SOUJI_VERIFY_BIN="$(dirname -- "$CM_SELF")/souji-verify.sh"
  fi
  export SOUJI_VERIFY_BIN
  export SOUJI_SELFTEST_ACTIVE=1 SOUJI_Q_SELFTEST_ACTIVE=1 SOUJI_CLI_BIN=/bin/false
  printf '%s\n' "$CM_HEADER" > "$SOUJI_LEDGER"
}

cm_run() {
  CM_RC=0
  local -a args=()
  if [ "$CM_KIND" = quarantine ]; then
    args=(--hold 0 "$CM_REPO")
  elif [ "$CM_KIND" = vault ]; then
    args=(--fallback)
  fi
  CM_OUT=$(bash "$CM_SELF" "${args[@]}" "$@" 2>&1) || CM_RC=$?
}

cm_refused() {
  if [ "$CM_KIND" = quarantine ]; then
    cm_expect "$1" 3 $'\tNOT-AUTHORIZED\t'
  else
    cm_expect "$1" 0 $'\tNOT-SAFE\t'
  fi
}

# ============================================================ ported r9 cases

for mode in stale pushed; do
  cm_new "nested-$mode"
  if [ "$mode" = stale ]; then
    target="$CM_REPO/.scratch/archive"
    mkdir -p "$target"
  else
    target="$CM_REPO/bundle"
    mkdir -p "$target"
    printf 'preserved\n' > "$target/public.txt"
    printf 'bundle/inner/\n' > "$CM_REPO/.gitignore"
    CM_BASE=$(cm_commit "$CM_REPO" "$CM_BASE")
    cm_push "$CM_BASE"
  fi
  git init -q --initial-branch=main "$target/inner"
  printf 'unpublished\n' > "$target/inner/local.txt"
  inner_sha=$(cm_commit "$target/inner")
  git -C "$target/inner" cat-file -e "$inner_sha^{commit}"
  printf 'dirty\n' > "$target/inner/work.txt"
  touch -d '3 days ago' "$target"
  cm_run "$target"
  cm_refused "nested-$mode refuses ancestor"
  cm_check "nested-$mode preserves unpublished bytes" "$([ -f "$target/inner/work.txt" ] && echo 1 || echo 0)"
done

cm_new nested-gitfile
target="$CM_REPO/.scratch/archive"
mkdir -p "$target/inner"
printf 'gitdir: missing-fixture-admin\n' > "$target/inner/.git"
touch -d '3 days ago' "$target"
cm_run "$target"
cm_refused 'nested gitfile refuses ancestor'

for mode in named detached; do
  cm_new "git-failure-$mode"
  admin="$CM_REPO/.git/worktrees/missing"
  mkdir -p "$admin" "$CM_CASE/bin"
  if [ "$mode" = named ]; then
    printf 'ref: refs/heads/main\n' > "$admin/HEAD"
  else
    printf '%s\n' "$CM_BASE" > "$admin/HEAD"
  fi
  printf '../..\n' > "$admin/commondir"
  printf '%s\n' "$CM_REPO/absent/.git" > "$admin/gitdir"
  cat > "$CM_CASE/bin/git" <<'SH'
#!/usr/bin/env bash
if [ -e "$CM_READY" ]; then exit 127; fi
if [[ " $* " = *' worktree list '* ]]; then
  "$CM_REAL_GIT" "$@"
  rc=$?
  : > "$CM_READY"
  exit "$rc"
fi
exec "$CM_REAL_GIT" "$@"
SH
  chmod +x "$CM_CASE/bin/git"
  export CM_READY="$CM_CASE/ready" CM_REAL_GIT="$CM_GIT" PATH="$CM_CASE/bin:$CM_PATH"
  cm_run "$CM_REPO/absent"
  cm_refused "failed $mode worktree query"
  cm_check "$mode discovery completed before failure" "$([ -f "$CM_READY" ] && echo 1 || echo 0)"
done

cm_new readonly-index
touch -d 'tomorrow' "$CM_REPO/seed.txt"
before=$(sha256sum -- "$CM_REPO/.git/index")
export GIT_OPTIONAL_LOCKS=1
cm_run "$CM_REPO"
after=$(sha256sum -- "$CM_REPO/.git/index")
cm_check 'inspection leaves index bytes unchanged' "$([ "$before" = "$after" ] && { [ "$CM_RC" = 0 ] || [ "$CM_RC" = 3 ]; } && echo 1 || echo 0)"
unset GIT_OPTIONAL_LOCKS

cm_new turkish-locale
mkdir -p "$CM_CASE/locale" "$CM_REPO/.scratch/ID_EMPTY"
touch -d '3 days ago' "$CM_REPO/.scratch/ID_EMPTY"
if command -v localedef >/dev/null 2>&1 && localedef --no-archive -i tr_TR -f UTF-8 "$CM_CASE/locale/tr_TR" >/dev/null 2>&1; then
  fold=$(env LOCPATH="$CM_CASE/locale" LC_ALL=tr_TR bash -s <<'SH'
s=ID_EMPTY
printf '%s' "${s,,}"
SH
  )
  cm_check 'Turkish locale fixture is active' "$([ "$fold" = 'ıd_empty' ] && echo 1 || echo 0)"
  locale_args=()
  if [ "$CM_KIND" = quarantine ]; then locale_args=(--hold 0 "$CM_REPO"); fi
  if [ "$CM_KIND" = vault ]; then locale_args=(--fallback); fi
  CM_RC=0
  CM_OUT=$(env LOCPATH="$CM_CASE/locale" LC_ALL=tr_TR bash "$CM_SELF" "${locale_args[@]}" "$CM_REPO/.scratch/ID_EMPTY" 2>&1) || CM_RC=$?
  cm_refused 'Turkish locale preserves ID_* refusal'
else
  printf 'SKIP CM Turkish locale (localedef or locale source unavailable)\n'
fi

for mode in file directory; do
  cm_new "ledger-$mode"
  if [ "$mode" = file ]; then
    target="$CM_REPO/source.md" vault="$CM_CASE/vault.md"
    printf 'independent preservation\n' > "$target"
    cp -- "$target" "$vault"
    source_sha=$(sha256sum -- "$target" | cut -d' ' -f1)
    vault_sha=$source_sha
  else
    target="$CM_REPO/source" vault="$CM_CASE/vault"
    mkdir -p "$target" "$vault"
    printf 'independent preservation\n' > "$target/note.md"
    cp -- "$target/note.md" "$vault/note.md"
    source_sha=$(cd -- "$target" && sha256sum ./note.md | sha256sum | cut -d' ' -f1)
    vault_sha=$source_sha
  fi
  printf '%s\t%s\t%s\t%s\t2026-10-18\tfixture\n' "$target" "$source_sha" "$vault" "$vault_sha" >> "$SOUJI_LEDGER"
  mkdir -p "$CM_CASE/bin"
  cat > "$CM_CASE/bin/sha256sum" <<'SH'
#!/usr/bin/env bash
set -eu
if [ "${!#}" = "$CM_GATE_TARGET" ] || { [ -n "$CM_GATE_DIR" ] && [ "$PWD" = "$CM_GATE_DIR" ] && [ "$#" -gt 0 ]; }; then
  n=0
  if [ -f "$CM_COUNT" ]; then IFS= read -r n < "$CM_COUNT"; fi
  n=$((n + 1))
  printf '%s\n' "$n" > "$CM_COUNT"
  if [ "$n" = "$CM_GATE_HIT" ]; then
    printf '%s\n' "$CM_HEADER" > "$CM_LEDGER.tmp"
    mv -- "$CM_LEDGER.tmp" "$CM_LEDGER"
  fi
fi
exec "$CM_REAL_SHA" "$@"
SH
  chmod +x "$CM_CASE/bin/sha256sum"
  export CM_GATE_TARGET="$target" CM_GATE_DIR="" CM_GATE_HIT=1
  if [ "$CM_KIND" = quarantine ]; then
    export CM_GATE_TARGET="$vault" CM_GATE_HIT=2
  fi
  if [ "$mode" = directory ]; then export CM_GATE_DIR="$CM_GATE_TARGET"; fi
  export CM_COUNT="$CM_CASE/count" CM_REAL_SHA="$CM_SHA" CM_LEDGER="$SOUJI_LEDGER" CM_HEADER
  export PATH="$CM_CASE/bin:$CM_PATH"
  cm_run "$target"
  if [ "$CM_KIND" = quarantine ]; then
    cm_expect "revoked $mode ledger aborts" 3 $'\tABORTED\t'
    staged="$CM_REPO/.ufo-quarantine/$(date -u +%F)/${target#"$CM_REPO/"}"
    cm_check "revoked $mode ledger retains staged bytes" "$([ -e "$staged" ] && echo 1 || echo 0)"
  else
    cm_refused "revoked $mode ledger refuses SAFE"
  fi
  cm_check "$mode ledger revocation was reached" "$([ -f "$CM_COUNT" ] && [ "$(<"$CM_LEDGER")" = "$CM_HEADER" ] && echo 1 || echo 0)"
done

if [ "$CM_KIND" = quarantine ]; then
  for mode in path pin prefix; do
    cm_new "nul-$mode"
    if [ "$mode" = path ]; then
      printf 'seed\0.txt\tpushed\n' > "$CM_CASE/list.tsv"
    elif [ "$mode" = pin ]; then
      printf 'seed.txt\tpush\0ed\n' > "$CM_CASE/list.tsv"
    else
      printf 'seed.txt\tpushed\nmissing\0.txt\tpushed\n' > "$CM_CASE/list.tsv"
    fi
    cm_run --list "$CM_CASE/list.tsv"
    cm_expect "NUL $mode list is a usage error" 2 'list contains a NUL byte'
    cm_check "NUL $mode list makes no moves" "$([ -f "$CM_REPO/seed.txt" ] && [ ! -e "$CM_REPO/.ufo-quarantine" ] && echo 1 || echo 0)"
  done
  for mode in rollback missing; do
    cm_new "default-$mode"
    printf 'preserved target\n' > "$CM_REPO/note.txt"
    tip=$(cm_commit "$CM_REPO" "$CM_BASE")
    cm_push "$tip"
    git -C "$CM_REPO" update-ref refs/remotes/backup/main "$tip"
    cat > "$CM_CASE/hook.sh" <<'SH'
#!/usr/bin/env bash
set -eu
if [ "$CM_MODE" = rollback ]; then
  git -C "$CM_REPO" update-ref refs/remotes/origin/main "$CM_BASE"
else
  git -C "$CM_REPO" symbolic-ref --delete refs/remotes/origin/HEAD
  git -C "$CM_REPO" update-ref -d refs/remotes/origin/main
fi
SH
    export SOUJI_Q_TEST_HOOK="$CM_CASE/hook.sh" CM_REPO CM_BASE CM_MODE="$mode"
    cm_run "$CM_REPO/note.txt"
    cm_expect "default ref $mode aborts" 3 'default-ref-unverifiable-or-not-ancestor'
    cm_check "default ref $mode retains staged bytes" "$([ -f "$CM_REPO/.ufo-quarantine/$(date -u +%F)/note.txt" ] && echo 1 || echo 0)"
  done
fi

# ==================================================== new r10 regression cases
# One case per adjudicated r9 class that this tool kind can observe.

# J01/J24-D2: pushed verdict must not ignore uncommitted replacement bytes.
cm_new j01-dirty-pushed
printf 'pushed original\n' > "$CM_REPO/tracked.txt"
CM_BASE=$(cm_commit "$CM_REPO" "$CM_BASE"); cm_push "$CM_BASE"
printf 'uncommitted replacement bytes\n' > "$CM_REPO/tracked.txt"
cm_run "$CM_REPO/tracked.txt"
cm_refused 'J01 uncommitted replacement on pushed file refused'

# J02/J24-D7: a hidden file that references the artifact is a live reference.
cm_new j02-hidden-live-ref
printf 'old output\n' > "$CM_REPO/old.out"
touch -d '3 days ago' "$CM_REPO/old.out"
printf 'see old.out for details\n' > "$CM_REPO/.usage.md"
cm_run "$CM_REPO/old.out"
cm_refused 'J02 hidden live reference blocks stale'

# J03/J24-D1: a directory receipt must cover ignored/untracked payload.
cm_new j03-dir-ignored-payload
mkdir -p "$CM_REPO/bundle"
printf 'tracked\n' > "$CM_REPO/bundle/kept.txt"
printf 'bundle/never-pushed.bin\n' > "$CM_REPO/.gitignore"
CM_BASE=$(cm_commit "$CM_REPO" "$CM_BASE"); cm_push "$CM_BASE"
printf 'ignored payload\n' > "$CM_REPO/bundle/never-pushed.bin"
cm_run "$CM_REPO/bundle"
cm_refused 'J03 ignored directory payload refused'

# J05/J24-D6: a self-referential ledger row must not qualify.
cm_new j05-self-ledger
printf 'sole copy\n' > "$CM_REPO/source.md"
ssha=$(sha256sum -- "$CM_REPO/source.md" | cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\t2026-10-18\tfixture\n' "$CM_REPO/source.md" "$ssha" "$CM_REPO/source.md" "$ssha" >> "$SOUJI_LEDGER"
cm_run "$CM_REPO/source.md"
cm_refused 'J05 self-referential ledger row refused'

# J06: a directory ledger row without the mandatory vault digest must not qualify.
cm_new j06-missing-vault-digest
mkdir -p "$CM_REPO/source" "$CM_CASE/vault"
printf 'preserved\n' > "$CM_REPO/source/note.md"
cp -- "$CM_REPO/source/note.md" "$CM_CASE/vault/note.md"
ssha=$(cd -- "$CM_REPO/source" && sha256sum ./note.md | sha256sum | cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\t2026-10-18\tfixture\n' "$CM_REPO/source" "$ssha" "$CM_CASE/vault" "" >> "$SOUJI_LEDGER"
cm_run "$CM_REPO/source"
cm_refused 'J06 directory ledger without vault digest refused'

# J08/J24-D3: an unpushed commit touching a backdated scratch file vetoes stale.
cm_new j08-unpushed-stale
printf 'seed\n' > "$CM_REPO/old.out"
CM_BASE=$(cm_commit "$CM_REPO" "$CM_BASE"); cm_push "$CM_BASE"
printf 'local-only change\n' > "$CM_REPO/old.out"
CM_BASE=$(cm_commit "$CM_REPO" "$CM_BASE")
touch -d '5 days ago' "$CM_REPO/old.out"
cm_run "$CM_REPO/old.out"
cm_refused 'J08 unpushed commit vetoes stale fallback'

# J12: a detached HEAD with unpushed commits must be refused.
cm_new j12-detached-head
printf 'seed\n' > "$CM_REPO/seed.txt"
printf 'detached work\n' > "$CM_REPO/detached.txt"
dsha=$(cm_commit "$CM_REPO" "$CM_BASE")
git -C "$CM_REPO" checkout -q --detach "$dsha"
cm_run "$CM_REPO/detached.txt"
cm_refused 'J12 detached HEAD unpushed commit refused'

# J07: a symlinked quarantine root must not be followed out of the repo.
if [ "$CM_KIND" = quarantine ]; then
  cm_new j07-quarantine-root-symlink
  outside="$CM_CASE/outside"
  mkdir -p "$outside"
  printf 'target\n' > "$CM_REPO/old.out"
  CM_BASE=$(cm_commit "$CM_REPO" "$CM_BASE"); cm_push "$CM_BASE"
  touch -d '5 days ago' "$CM_REPO/old.out"
  ln -s -- "$outside" "$CM_REPO/.ufo-quarantine"
  cm_run "$CM_REPO/old.out"
  cm_check 'J07 symlinked quarantine root refused' "$([ "$CM_RC" = 3 ] && [ -z "$(ls -A "$outside")" ] && echo 1 || echo 0)"
fi

# ---- S15 merge-specific regressions (classes adopted from sibling clusters) --

# G2 (S13/S14): an aged .scratch container must not launder a backdated
# descendant. utime moves mtime backward but cannot move ctime, so a fixture
# whose child keeps a fresh ctime is exactly the forgery shape and must refuse.
cm_new s15-g2-backdated-descendant
mkdir -p "$CM_REPO/.scratch/aged"
printf 'old payload\n' > "$CM_REPO/.scratch/aged/old.txt"
printf 'rewritten payload\n' > "$CM_REPO/.scratch/aged/fresh.md"
touch -d '6 days ago' "$CM_REPO/.scratch" "$CM_REPO/.scratch/aged" \
  "$CM_REPO/.scratch/aged/old.txt" "$CM_REPO/.scratch/aged/fresh.md"
cm_run "$CM_REPO/.scratch/aged"
cm_refused 'S15 backdated fresh descendant refused'

# F2 (S12/S06): a repository root whose .git is a FILE is a repo root, not an
# artifact -- it must not earn a pushed receipt from the artifact engine.
cm_new s15-f2-gitfile-root
admin="$CM_CASE/separate-admin"
git init -q --initial-branch=main --separate-git-dir "$admin" "$CM_CASE/gitfile-root"
gfr="$CM_CASE/gitfile-root"
printf 'root payload\n' > "$gfr/note.txt"
gfr_sha=$(cm_commit "$gfr")
cm_push "$gfr_sha" "$gfr"
cm_run "$gfr"
cm_refused 'S15 gitfile repository root refused as artifact'

printf 'R10\t%s\t%s\n' "$CM_PASS" "$CM_FAIL"
[ "$CM_FAIL" = 0 ]
