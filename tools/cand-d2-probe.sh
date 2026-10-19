#!/usr/bin/env bash
# cand-d2-probe — fresh cluster-D repro battery for round 10 (S08).
#
# Cluster D = stale-sweep / worktree-metadata / directory-receipt classes:
# hidden live references, recursive directory age, directory receipt
# completeness (untracked/ignored/dirty descendants), tracked-to-stale
# fallback, hidden (non-branch) refs, and worktree registrations whose owner
# repo is not matched by the `*-shokunin` glob.
#
# Usage: cand-d2-probe.sh <tool-path> [label]
# Every fixture is built fresh under `mktemp -d -p /var/tmp`; the tool under
# test is only ever pointed at those fixture roots. Nothing outside /var/tmp
# is written; no live fleet path is read.
set -euo pipefail

TOOL=$(readlink -f -- "${1:?tool path required}")
LABEL=${2:-$(basename -- "$TOOL")}
ROOT=$(mktemp -d -p /var/tmp "souji-s08-d2-${LABEL//[^A-Za-z0-9._-]/_}.XXXXXX")
export TMPDIR=/var/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export LC_ALL=C
export GIT_AUTHOR_NAME=souji-selftest GIT_AUTHOR_EMAIL=souji-selftest@fixture.invalid
export GIT_COMMITTER_NAME=souji-selftest GIT_COMMITTER_EMAIL=souji-selftest@fixture.invalid
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

PASS=0; FAIL=0; UNREPRO=0; OUT=""; RC=0

say() { printf '%s\n' "$*"; }

check() { # $1 class, $2 want-verdict, $3 want-receipt|"", $4 note
  local cls=$1 wv=$2 wr=$3 note=${4:-}
  local v="" r=""
  v=${OUT%%$'\t'*}; OUT2=${OUT#*$'\t'}
  if [ "$OUT2" != "$OUT" ]; then
    OUT2=${OUT2#*$'\t'}
    v=${OUT2%%$'\t'*}; OUT3=${OUT2#*$'\t'}
    r=${OUT3%%$'\t'*}; ev=${OUT3#*$'\t'}
  fi
  local ok=0
  if [ "$v" = "$wv" ] && { [ -z "$wr" ] || [ "$r" = "$wr" ]; }; then ok=1; fi
  if [ "$ok" = 1 ]; then
    PASS=$((PASS + 1)); say "PASS	$cls	$v($r)"
  else
    FAIL=$((FAIL + 1)); say "DEFECT	$cls	got=$v($r)	want=$wv($wr)	ev=$ev	$note"
  fi
}

control() { # $1 class, $2 note — a correct fail-closed refusal that the installed tool already produces
  local cls=$1
  local v="${OUT%%$'\t'*}"
  v=${OUT#*$'\t'}; v=${v#*$'\t'}; v=${v%%$'\t'*}
  if [ "$v" = "NOT-SAFE" ]; then
    PASS=$((PASS + 1)); say "PASS	$cls	control=$v"
  else
    FAIL=$((FAIL + 1)); say "DEFECT	$cls	control got=$v want=NOT-SAFE"
  fi
}

run_tool() { # rest = targets
  RC=0
  OUT=$(env -u GIT_DIR SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$LEDGER" \
        SOUJI_SELFTEST_ACTIVE=1 bash "$TOOL" --stale-days 1 "$@" 2>&1) || RC=$?
}

new_fleet() { # $1 case name -> FLEET, LEDGER, REPO
  local name=$1
  CASE="$ROOT/$name"
  FLEET="$CASE/fleet"
  mkdir -p "$FLEET"
  LEDGER="$CASE/ledger.tsv"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$LEDGER"
  REPO="$FLEET/case-shokunin"
  git init -q --initial-branch=main "$REPO"
  printf 'pushed seed\n' > "$REPO/seed.txt"
  BASE=$(commit_repo "$REPO")
  push_refs "$BASE"
}

commit_repo() { # $1 repo, $2 parent(optional) -> sha
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

push_refs() { # $1 sha -> origin/main == sha
  git -C "$REPO" update-ref refs/remotes/origin/main "$1"
  git -C "$REPO" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
}

register_wt() { # $1 owner, $2 admin-name, $3 wt-path, $4 head(sha|"ref: refs/heads/x"), $5 link(0/1)
  local owner=$1 name=$2 wt=$3 head=$4 link=${5:-0} adm
  adm="$owner/.git/worktrees/$name"
  mkdir -p "$adm"
  printf '%s\n' "$head" > "$adm/HEAD"
  printf '../..\n' > "$adm/commondir"
  printf '%s\n' "$wt/.git" > "$adm/gitdir"
  if [ "$link" = 1 ]; then printf 'gitdir: %s\n' "$adm" > "$wt/.git"; fi
}

# ---------------------------------------------------------------- cases ----

# A: hidden live reference (ripgrep skips dotfiles without --hidden)
new_fleet hidden-live-ref
mkdir -p "$REPO/.scratch"
printf 'payload\n' > "$REPO/.scratch/old-a.out"
printf 'old-a.out is the active artifact\n' > "$REPO/.scratch/.active-reference"
touch -d '3 days ago' "$REPO/.scratch/old-a.out"
run_tool "$REPO/.scratch/old-a.out"
check hidden-live-ref NOT-SAFE "" "hidden referrer must block the stale receipt"

# B: stale directory with a freshly written descendant
new_fleet stale-dir-fresh-child
mkdir -p "$REPO/.scratch/old-b"
printf 'old\n' > "$REPO/.scratch/old-b/old.txt"
printf 'fresh\n' > "$REPO/.scratch/old-b/new.txt"
touch -d '3 days ago' "$REPO/.scratch/old-b/old.txt" "$REPO/.scratch/old-b/new.txt" "$REPO/.scratch/old-b"
printf 'fresh\n' > "$REPO/.scratch/old-b/new.txt"
run_tool "$REPO/.scratch/old-b"
check stale-dir-fresh-child NOT-SAFE "" "a fresh descendant must block the stale receipt"

# C: pushed directory carrying an untracked (never-committed) child
new_fleet dir-untracked-child
mkdir -p "$REPO/bundle"
printf 'preserved\n' > "$REPO/bundle/public.txt"
printf 'bundle/local-only.txt\n' > "$REPO/.gitignore"
BASE=$(commit_repo "$REPO" "$BASE")
push_refs "$BASE"
printf 'unpublished\n' > "$REPO/bundle/local-only.txt"
run_tool "$REPO/bundle"
check dir-untracked-child NOT-SAFE "" "an untracked child has no pushed copy"

# D: pushed directory carrying an ignored child
new_fleet dir-ignored-child
mkdir -p "$REPO/bundle"
printf 'preserved\n' > "$REPO/bundle/public.txt"
printf 'bundle/ignored.txt\n' > "$REPO/.gitignore"
BASE=$(commit_repo "$REPO" "$BASE")
push_refs "$BASE"
printf 'ignored sole copy\n' > "$REPO/bundle/ignored.txt"
run_tool "$REPO/bundle"
check dir-ignored-child NOT-SAFE "" "an ignored child has no pushed copy"

# E: tracked, locally committed (unpushed) scratch-type file falls through to stale
new_fleet stale-unpushed-fallback
printf 'local only\n' > "$REPO/local-e.out"
BASE=$(commit_repo "$REPO" "$BASE")
touch -d '3 days ago' "$REPO/local-e.out"
run_tool "$REPO/local-e.out"
check stale-unpushed-fallback NOT-SAFE "" "tracked local-only content must not fall through to stale"

# F: commit reachable only from a non-branch (hidden) ref
new_fleet hidden-ref
printf 'keep\n' > "$REPO/keep-f.txt"
BASE=$(commit_repo "$REPO" "$BASE")
push_refs "$BASE"
printf 'hidden edit\n' > "$REPO/keep-f.txt"
git -C "$REPO" add -A
HIDTREE=$(git -C "$REPO" write-tree)
HIDSHA=$(printf 'hidden\n' | git -C "$REPO" commit-tree "$HIDTREE" -p "$BASE")
git -C "$REPO" update-ref refs/hidden/keep "$HIDSHA"
git -C "$REPO" update-ref refs/heads/main "$BASE"
run_tool "$REPO/keep-f.txt"
check hidden-ref NOT-SAFE "" "a commit held only by refs/hidden/* is not pushed"

# G: pushed directory whose tracked child has uncommitted edits
new_fleet dir-dirty-child
mkdir -p "$REPO/bundle"
printf 'preserved\n' > "$REPO/bundle/public.txt"
BASE=$(commit_repo "$REPO" "$BASE")
push_refs "$BASE"
printf 'uncommitted edit\n' > "$REPO/bundle/public.txt"
run_tool "$REPO/bundle"
check dir-dirty-child NOT-SAFE "" "uncommitted bytes in the scope are not pushed"

# H: worktree registration owned by a repo the `*-shokunin` glob never matches
new_fleet owner-name
LEGACY="$FLEET/legacy-lane"
git init -q --initial-branch=main "$LEGACY"
printf 'seed\n' > "$LEGACY/seed.txt"
git -C "$LEGACY" add -A
LTREE=$(git -C "$LEGACY" write-tree)
LSHA=$(printf 'legacy\n' | git -C "$LEGACY" commit-tree "$LTREE")
git -C "$LEGACY" update-ref refs/heads/main "$LSHA"
git -C "$LEGACY" update-ref refs/remotes/origin/main "$LSHA"
git -C "$LEGACY" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
mkdir -p "$LEGACY/.scratch/wt-h"
touch -d '3 days ago' "$LEGACY/.scratch/wt-h"
register_wt "$LEGACY" wt-h "$LEGACY/.scratch/wt-h" "ref: refs/heads/wt-h"
run_tool "$LEGACY/.scratch/wt-h"
check owner-name NOT-SAFE "" "a registered live worktree must not read as a stale scratch dir"

# I: control — detached worktree HEAD with a unique commit, owner matched
new_fleet wt-detached-unique
printf 'detached\n' > "$REPO/d.txt"
git -C "$REPO" add -A
DTREE=$(git -C "$REPO" write-tree)
DSHA=$(printf 'detached\n' | git -C "$REPO" commit-tree "$DTREE" -p "$BASE")
register_wt "$REPO" wt-i "$CASE/wt-i-absent" "$DSHA"
run_tool "$CASE/wt-i-absent"
control wt-detached-unique

# J: control — worktree registration whose HEAD is unparseable
new_fleet wt-invalid-head
register_wt "$REPO" wt-j "$CASE/wt-j-absent" "not-a-real-object-name"
run_tool "$CASE/wt-j-absent"
control wt-invalid-head

say "PROBE	$LABEL	pass=$PASS	defect=$FAIL	root=$ROOT"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
