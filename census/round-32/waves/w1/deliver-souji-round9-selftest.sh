#!/usr/bin/env bash
set -euo pipefail

R9_KIND=${1:?tool kind required}
R9_SELF=$(readlink -f -- "${2:?tool path required}")
case "$R9_KIND" in verify|vault|quarantine) : ;; *) exit 2 ;; esac
R9_TMP=$(mktemp -d "${TMPDIR:-/var/tmp}/souji-round9-selftest.XXXXXX")
trap 'rm -rf -- "$R9_TMP"' EXIT
R9_PATH=$PATH
R9_GIT=$(command -v git)
R9_SHA=$(command -v sha256sum)
R9_PASS=0 R9_FAIL=0 R9_OUT="" R9_RC=0
R9_HEADER=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
export TMPDIR="${TMPDIR:-/var/tmp}" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=souji-selftest GIT_AUTHOR_EMAIL=souji-selftest@fixture.invalid
export GIT_COMMITTER_NAME=souji-selftest GIT_COMMITTER_EMAIL=souji-selftest@fixture.invalid
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE

r9_check() {
  if [ "$2" = 1 ]; then
    R9_PASS=$((R9_PASS + 1)); printf 'PASS R9 %s\n' "$1"
  else
    R9_FAIL=$((R9_FAIL + 1)); printf 'FAIL R9 %s: rc=%s output=%s\n' "$1" "$R9_RC" "$R9_OUT"
  fi
}

r9_expect() {
  local ok=0
  if [ "$R9_RC" = "$2" ] && [[ "$R9_OUT" = *"$3"* ]]; then ok=1; fi
  r9_check "$1" "$ok"
}

r9_commit() {
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

r9_push() {
  git -C "$R9_REPO" update-ref refs/remotes/origin/main "$1"
  git -C "$R9_REPO" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
}

r9_new() {
  R9_CASE="$R9_TMP/$1" R9_OUT="" R9_RC=0
  R9_FLEET="$R9_CASE/fleet"
  R9_REPO="$R9_FLEET/case-shokunin"
  export PATH="$R9_PATH" LC_ALL=C HOME="$R9_CASE/home"
  unset SOUJI_Q_TEST_HOOK SOUJI_QUARANTINE_ALLOW_LIVE
  mkdir -p "$R9_FLEET" "$HOME"
  git init -q --initial-branch=main "$R9_REPO"
  printf 'pushed seed\n' > "$R9_REPO/seed.txt"
  R9_BASE=$(r9_commit "$R9_REPO")
  r9_push "$R9_BASE"
  export SHOKUNIN_ROOT="$R9_FLEET" SOUJI_Q_SHOKUNIN_ROOT="$R9_FLEET"
  export SOUJI_LEDGER="$R9_CASE/ledger.tsv" SOUJI_Q_LEDGER="$R9_CASE/ledger.tsv"
  SOUJI_VERIFY_BIN="$(dirname -- "$R9_SELF")/souji-verify.sh"
  export SOUJI_VERIFY_BIN
  export SOUJI_SELFTEST_ACTIVE=1 SOUJI_Q_SELFTEST_ACTIVE=1 SOUJI_CLI_BIN=/bin/false
  printf '%s\n' "$R9_HEADER" > "$SOUJI_LEDGER"
}

r9_run() {
  R9_RC=0
  local -a args=()
  if [ "$R9_KIND" = quarantine ]; then
    args=(--hold 0 "$R9_REPO")
  elif [ "$R9_KIND" = vault ]; then
    args=(--fallback)
  fi
  R9_OUT=$(bash "$R9_SELF" "${args[@]}" "$@" 2>&1) || R9_RC=$?
}

r9_refused() {
  if [ "$R9_KIND" = quarantine ]; then
    r9_expect "$1" 3 $'\tNOT-AUTHORIZED\t'
  else
    r9_expect "$1" 0 $'\tNOT-SAFE\t'
  fi
}

for mode in stale pushed; do
  r9_new "nested-$mode"
  if [ "$mode" = stale ]; then
    target="$R9_REPO/.scratch/archive"
    mkdir -p "$target"
  else
    target="$R9_REPO/bundle"
    mkdir -p "$target"
    printf 'preserved\n' > "$target/public.txt"
    printf 'bundle/inner/\n' > "$R9_REPO/.gitignore"
    R9_BASE=$(r9_commit "$R9_REPO" "$R9_BASE")
    r9_push "$R9_BASE"
  fi
  git init -q --initial-branch=main "$target/inner"
  printf 'unpublished\n' > "$target/inner/local.txt"
  inner_sha=$(r9_commit "$target/inner")
  git -C "$target/inner" cat-file -e "$inner_sha^{commit}"
  printf 'dirty\n' > "$target/inner/work.txt"
  touch -d '3 days ago' "$target"
  r9_run "$target"
  r9_refused "nested-$mode refuses ancestor"
  r9_check "nested-$mode preserves unpublished bytes" "$([ -f "$target/inner/work.txt" ] && echo 1 || echo 0)"
done

r9_new nested-gitfile
target="$R9_REPO/.scratch/archive"
mkdir -p "$target/inner"
printf 'gitdir: missing-fixture-admin\n' > "$target/inner/.git"
touch -d '3 days ago' "$target"
r9_run "$target"
r9_refused 'nested gitfile refuses ancestor'

for mode in named detached; do
  r9_new "git-failure-$mode"
  admin="$R9_REPO/.git/worktrees/missing"
  mkdir -p "$admin" "$R9_CASE/bin"
  if [ "$mode" = named ]; then
    printf 'ref: refs/heads/main\n' > "$admin/HEAD"
  else
    printf '%s\n' "$R9_BASE" > "$admin/HEAD"
  fi
  printf '../..\n' > "$admin/commondir"
  printf '%s\n' "$R9_REPO/absent/.git" > "$admin/gitdir"
  cat > "$R9_CASE/bin/git" <<'SH'
#!/usr/bin/env bash
if [ -e "$R9_READY" ]; then exit 127; fi
if [[ " $* " = *' worktree list '* ]]; then
  "$R9_REAL_GIT" "$@"
  rc=$?
  : > "$R9_READY"
  exit "$rc"
fi
exec "$R9_REAL_GIT" "$@"
SH
  chmod +x "$R9_CASE/bin/git"
  export R9_READY="$R9_CASE/ready" R9_REAL_GIT="$R9_GIT" PATH="$R9_CASE/bin:$R9_PATH"
  r9_run "$R9_REPO/absent"
  r9_refused "failed $mode worktree query"
  r9_check "$mode discovery completed before failure" "$([ -f "$R9_READY" ] && echo 1 || echo 0)"
done

r9_new readonly-index
touch -d 'tomorrow' "$R9_REPO/seed.txt"
before=$(sha256sum -- "$R9_REPO/.git/index")
export GIT_OPTIONAL_LOCKS=1
r9_run "$R9_REPO"
after=$(sha256sum -- "$R9_REPO/.git/index")
r9_check 'inspection leaves index bytes unchanged' "$([ "$before" = "$after" ] && { [ "$R9_RC" = 0 ] || [ "$R9_RC" = 3 ]; } && echo 1 || echo 0)"
unset GIT_OPTIONAL_LOCKS

r9_new turkish-locale
mkdir -p "$R9_CASE/locale" "$R9_REPO/.scratch/ID_EMPTY"
touch -d '3 days ago' "$R9_REPO/.scratch/ID_EMPTY"
if command -v localedef >/dev/null 2>&1 && localedef --no-archive -i tr_TR -f UTF-8 "$R9_CASE/locale/tr_TR" >/dev/null 2>&1; then
  fold=$(env LOCPATH="$R9_CASE/locale" LC_ALL=tr_TR bash -s <<'SH'
s=ID_EMPTY
printf '%s' "${s,,}"
SH
  )
  r9_check 'Turkish locale fixture is active' "$([ "$fold" = 'ıd_empty' ] && echo 1 || echo 0)"
  locale_args=()
  if [ "$R9_KIND" = quarantine ]; then locale_args=(--hold 0 "$R9_REPO"); fi
  if [ "$R9_KIND" = vault ]; then locale_args=(--fallback); fi
  R9_RC=0
  R9_OUT=$(env LOCPATH="$R9_CASE/locale" LC_ALL=tr_TR bash "$R9_SELF" "${locale_args[@]}" "$R9_REPO/.scratch/ID_EMPTY" 2>&1) || R9_RC=$?
  r9_refused 'Turkish locale preserves ID_* refusal'
else
  printf 'SKIP R9 Turkish locale (localedef or locale source unavailable)\n'
fi

for mode in file directory; do
  r9_new "ledger-$mode"
  if [ "$mode" = file ]; then
    target="$R9_REPO/source.md" vault="$R9_CASE/vault.md"
    printf 'independent preservation\n' > "$target"
    cp -- "$target" "$vault"
    source_sha=$(sha256sum -- "$target" | cut -d' ' -f1)
    vault_sha=$source_sha
  else
    target="$R9_REPO/source" vault="$R9_CASE/vault"
    mkdir -p "$target" "$vault"
    printf 'independent preservation\n' > "$target/note.md"
    cp -- "$target/note.md" "$vault/note.md"
    source_sha=$(cd -- "$target" && sha256sum ./note.md | sha256sum | cut -d' ' -f1)
    vault_sha=$source_sha
  fi
  printf '%s\t%s\t%s\t%s\t2026-10-18\tfixture\n' "$target" "$source_sha" "$vault" "$vault_sha" >> "$SOUJI_LEDGER"
  mkdir -p "$R9_CASE/bin"
  cat > "$R9_CASE/bin/sha256sum" <<'SH'
#!/usr/bin/env bash
set -eu
if [ "${!#}" = "$R9_GATE_TARGET" ] || { [ -n "$R9_GATE_DIR" ] && [ "$PWD" = "$R9_GATE_DIR" ] && [ "$#" -gt 0 ]; }; then
  n=0
  if [ -f "$R9_COUNT" ]; then IFS= read -r n < "$R9_COUNT"; fi
  n=$((n + 1))
  printf '%s\n' "$n" > "$R9_COUNT"
  if [ "$n" = "$R9_GATE_HIT" ]; then
    printf '%s\n' "$R9_HEADER" > "$R9_LEDGER.tmp"
    mv -- "$R9_LEDGER.tmp" "$R9_LEDGER"
  fi
fi
exec "$R9_REAL_SHA" "$@"
SH
  chmod +x "$R9_CASE/bin/sha256sum"
  export R9_GATE_TARGET="$target" R9_GATE_DIR="" R9_GATE_HIT=1
  if [ "$R9_KIND" = quarantine ]; then
    export R9_GATE_TARGET="$vault" R9_GATE_HIT=2
  fi
  if [ "$mode" = directory ]; then export R9_GATE_DIR="$R9_GATE_TARGET"; fi
  export R9_COUNT="$R9_CASE/count" R9_REAL_SHA="$R9_SHA" R9_LEDGER="$SOUJI_LEDGER" R9_HEADER
  export PATH="$R9_CASE/bin:$R9_PATH"
  r9_run "$target"
  if [ "$R9_KIND" = quarantine ]; then
    r9_expect "revoked $mode ledger aborts" 3 $'\tABORTED\t'
    staged="$R9_REPO/.ufo-quarantine/$(date -u +%F)/${target#"$R9_REPO/"}"
    r9_check "revoked $mode ledger retains staged bytes" "$([ -e "$staged" ] && echo 1 || echo 0)"
  else
    r9_refused "revoked $mode ledger refuses SAFE"
  fi
  r9_check "$mode ledger revocation was reached" "$([ -f "$R9_COUNT" ] && [ "$(<"$R9_LEDGER")" = "$R9_HEADER" ] && echo 1 || echo 0)"
done

if [ "$R9_KIND" = quarantine ]; then
  for mode in path pin prefix; do
    r9_new "nul-$mode"
    if [ "$mode" = path ]; then
      printf 'seed\0.txt\tpushed\n' > "$R9_CASE/list.tsv"
    elif [ "$mode" = pin ]; then
      printf 'seed.txt\tpush\0ed\n' > "$R9_CASE/list.tsv"
    else
      printf 'seed.txt\tpushed\nmissing\0.txt\tpushed\n' > "$R9_CASE/list.tsv"
    fi
    r9_run --list "$R9_CASE/list.tsv"
    r9_expect "NUL $mode list is a usage error" 2 'list contains a NUL byte'
    r9_check "NUL $mode list makes no moves" "$([ -f "$R9_REPO/seed.txt" ] && [ ! -e "$R9_REPO/.ufo-quarantine" ] && echo 1 || echo 0)"
  done
  for mode in rollback missing; do
    r9_new "default-$mode"
    printf 'preserved target\n' > "$R9_REPO/note.txt"
    tip=$(r9_commit "$R9_REPO" "$R9_BASE")
    r9_push "$tip"
    git -C "$R9_REPO" update-ref refs/remotes/backup/main "$tip"
    cat > "$R9_CASE/hook.sh" <<'SH'
#!/usr/bin/env bash
set -eu
if [ "$R9_MODE" = rollback ]; then
  git -C "$R9_REPO" update-ref refs/remotes/origin/main "$R9_BASE"
else
  git -C "$R9_REPO" symbolic-ref --delete refs/remotes/origin/HEAD
  git -C "$R9_REPO" update-ref -d refs/remotes/origin/main
fi
SH
    export SOUJI_Q_TEST_HOOK="$R9_CASE/hook.sh" R9_REPO R9_BASE R9_MODE="$mode"
    r9_run "$R9_REPO/note.txt"
    r9_expect "default ref $mode aborts" 3 'default-ref-unverifiable-or-not-ancestor'
    r9_check "default ref $mode retains staged bytes" "$([ -f "$R9_REPO/.ufo-quarantine/$(date -u +%F)/note.txt" ] && echo 1 || echo 0)"
  done
fi

printf 'ROUND9\t%s\t%s\n' "$R9_PASS" "$R9_FAIL"
[ "$R9_FAIL" = 0 ]
