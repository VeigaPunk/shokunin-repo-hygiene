#!/usr/bin/env bash
#
# tests/fixtures/case-F5/make-fixture.sh — build the F5 fixture (deterministic).
#
# F5: a repo has a worktree on a NAMED branch whose tip has exactly 1 commit
#     that is not under any remote-tracking ref (fake origin/master is set one
#     commit behind the worktree branch tip).
#     Expected verdict for the target path: NOT-SAFE(unpushed-branch)
#
# layout built under <case_root> (see expected.json in this dir):
#   owner-shokunin/  repo, branch master (1 commit) + fake refs/remotes/origin/*
#                    with origin/master parked at that base commit
#   wt-f5            worktree, directory PRESENT and clean, on named branch
#                    feature-f5 = base + 1 commit (not under any remote ref)
#
# Deterministic + read-only-friendly: no `git fetch/push/commit/branch/
# checkout/reset/rebase` is used. Commits and refs are built with git plumbing
# (hash-object/update-index/write-tree/commit-tree/update-ref) and the owner's
# main worktree is materialised with `git read-tree --reset -u HEAD`. Fixed
# author/committer dates and a hermetic git config make the SHAs stable across
# runs.
#
# usage: make-fixture.sh [--out DIR | DIR] [--manifest-out FILE] [--emit-resolved-expected FILE]
#   --out DIR | DIR             scratch dir to build in (default: mktemp -d);
#                               wiped first, must not be inside a git repo;
#                               a bare DIR is accepted as an alias for --out DIR
#   --manifest-out FILE         also write the stdout JSON manifest to FILE
#   --emit-resolved-expected F  write expected.json with ${CASE_ROOT} replaced
#                               by the resolved --out path
#                               (default: <out>/expected.json)
# stdout: one compact JSON manifest (paths, state, measurements, expected verdict)
# exit:   0 built | 1 fixture self-check failed | 2 usage/refused
set -euo pipefail

CASE='F5'

die() { printf 'make-fixture(F5): %s\n' "$*" >&2; exit "${2:-2}"; }
note() { printf 'make-fixture(F5): %s\n' "$*" >&2; }

usage() {
  sed -n '2,33p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

json_escape() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }

OUT=''
MANIFEST_OUT=''
RESOLVED_EXPECTED=''
while [ $# -gt 0 ]; do
  case "$1" in
    --out)                    [ $# -ge 2 ] || die "--out needs a value"; OUT=$2; shift 2 ;;
    --manifest-out)           [ $# -ge 2 ] || die "--manifest-out needs a value"; MANIFEST_OUT=$2; shift 2 ;;
    --emit-resolved-expected) [ $# -ge 2 ] || die "--emit-resolved-expected needs a value"; RESOLVED_EXPECTED=$2; shift 2 ;;
    -h|--help)                usage; exit 0 ;;
    -*) die "unknown argument: $1 (try --help)" ;;
    *) [ -z "$OUT" ] || die "two output dirs given: --out $OUT and $1"
       OUT=$1; shift ;;
  esac
done

[ -n "$OUT" ] || OUT="$(mktemp -d "${TMPDIR:-/tmp}/souji-fixture-F5.XXXXXX")"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd -P)"

# --- refusal guards: never wipe anything repo-shaped or user-facing ---------
[ "$OUT" != '/' ] || die "refusing to wipe /"
case "$HOME/" in "$OUT"/*) die "refusing to wipe $OUT: it is an ancestor of \$HOME" ;; esac
for f in .git AGENTS.md make-fixture.sh tools/souji-verify.spec.md; do
  if [ -e "$OUT/$f" ]; then
    die "refusing to wipe $OUT: it contains '$f' — pass a fresh scratch dir"
  fi
done
if git -C "$OUT" rev-parse --show-toplevel >/dev/null 2>&1; then
  die "refusing to wipe $OUT: it is inside a git repository — pass a scratch dir under ${TMPDIR:-/tmp}"
fi
find "$OUT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +

# --- hermetic, deterministic git environment --------------------------------
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_SYSTEM=/dev/null
export GIT_TERMINAL_PROMPT=0
export LC_ALL=C TZ=UTC
export GIT_AUTHOR_NAME='souji-fixture'    GIT_AUTHOR_EMAIL='fixture@souji.invalid'
export GIT_COMMITTER_NAME='souji-fixture' GIT_COMMITTER_EMAIL='fixture@souji.invalid'
export GIT_AUTHOR_DATE='2001-02-03T04:05:06+0000'
export GIT_COMMITTER_DATE='2001-02-03T04:05:06+0000'

# fixture_commit <repo> <parent-sha|-> <message> <path-in-tree> <file-content>
# Builds one commit object with plumbing only; prints the new commit sha.
fixture_commit() {
  local repo=$1 parent=$2 msg=$3 fpath=$4 fcontent=$5
  local idx blob tree
  idx="$repo/.git/fixture-index.$$"
  rm -f "$idx"
  if [ "$parent" != '-' ]; then
    GIT_INDEX_FILE="$idx" git -C "$repo" read-tree "$parent"
  fi
  blob="$(printf '%s\n' "$fcontent" | git -C "$repo" hash-object -w --stdin)"
  GIT_INDEX_FILE="$idx" git -C "$repo" update-index --add --cacheinfo "100644,$blob,$fpath"
  tree="$(GIT_INDEX_FILE="$idx" git -C "$repo" write-tree)"
  rm -f "$idx"
  if [ "$parent" != '-' ]; then
    git -C "$repo" commit-tree "$tree" -p "$parent" -m "$msg"
  else
    git -C "$repo" commit-tree "$tree" -m "$msg"
  fi
}

# --- owner repo: master base, fake origin/master parked at the base ---------
repo="$OUT/owner-shokunin"
git init -q "$repo"
base="$(fixture_commit "$repo" '-' 'fixture F5: base commit' 'README.md' 'souji fixture F5 base')"
git -C "$repo" update-ref refs/heads/master "$base"
git -C "$repo" symbolic-ref HEAD refs/heads/master
git -C "$repo" read-tree --reset -u HEAD   # materialise the main worktree (plumbing)

git -C "$repo" config remote.origin.url '/nonexistent/souji-fixture-origin.git'
git -C "$repo" config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git -C "$repo" update-ref refs/remotes/origin/master "$base"   # fake remote stays behind
git -C "$repo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

# --- 1 commit under no remote-tracking ref, on a named branch ---------------
tip="$(fixture_commit "$repo" "$base" 'fixture F5: unpushed commit' 'feature/unpushed.txt' 'souji fixture F5 unpushed work')"
git -C "$repo" update-ref refs/heads/feature-f5 "$tip"

# --- worktree on that named branch, directory present and clean -------------
wt="$OUT/wt-f5"
admin="$repo/.git/worktrees/wt-f5"
git -C "$repo" worktree add -q "$wt" feature-f5

# --- self-checks: the fixture must actually be the shape F5 claims ----------
[ -d "$wt" ] || die "worktree dir missing: $wt" 1
[ -f "$wt/.git" ] || die "worktree .git file missing: $wt/.git" 1
[ -d "$admin" ] || die "worktree admin dir missing: $admin" 1
grep -qx 'ref: refs/heads/feature-f5' "$admin/HEAD" || die "admin HEAD is not the feature-f5 branch" 1
[ "$(git -C "$wt" rev-parse --abbrev-ref HEAD)" = 'feature-f5' ] || die "worktree HEAD is not feature-f5" 1
[ "$(git -C "$wt" rev-parse HEAD)" = "$tip" ] || die "worktree HEAD != feature-f5 tip" 1

reg_count="$(git -C "$repo" worktree list --porcelain | grep -c '^worktree ' || true)"
[ "$reg_count" = 2 ] || die "expected 2 worktree registrations, got $reg_count" 1
git -C "$repo" worktree list --porcelain | grep -qx "worktree $wt" \
  || die "registration for $wt not listed by worktree list --porcelain" 1

unpushed="$(git -C "$repo" log --oneline feature-f5 --not --remotes | wc -l | tr -d ' ')"
[ "$unpushed" = 1 ] || die "unpushed_commits=$unpushed (want 1) — spec rule for NOT-SAFE(unpushed-branch)" 1
unique="$(git -C "$repo" log --oneline feature-f5 --not --all | wc -l | tr -d ' ')"
[ "$unique" = 0 ] || die "unique_commits=$unique (want 0) — feature-f5 ref is under --all" 1
ahead="$(git -C "$repo" rev-list --count refs/remotes/origin/master..feature-f5 | tr -d ' ')"
[ "$ahead" = 1 ] || die "ahead_of_origin_master=$ahead (want 1)" 1
dirty_wt="$(git -C "$wt" status --porcelain | wc -l | tr -d ' ')"
[ "$dirty_wt" = 0 ] || die "worktree dirty ($dirty_wt entries) — F5 needs dir-present but clean" 1
dirty_owner="$(git -C "$repo" status --porcelain | wc -l | tr -d ' ')"
[ "$dirty_owner" = 0 ] || die "owner tree dirty ($dirty_owner entries) — fixture must be clean" 1

# --- resolved expected.json (default: <out>/expected.json) ------------------
RESOLVED_EXPECTED="${RESOLVED_EXPECTED:-$OUT/expected.json}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
[ -f "$script_dir/expected.json" ] || die "expected.json not found next to make-fixture.sh ($script_dir)"
case "$OUT" in *'|'*|*'&'*|*'\'*) die "--out contains sed-hostile characters; pass a plain scratch path" ;; esac
sed "s|\${CASE_ROOT}|$OUT|g" "$script_dir/expected.json" > "$RESOLVED_EXPECTED"
note "resolved expected.json -> $RESOLVED_EXPECTED"

manifest="$(printf '{"case":"%s","case_root":"%s","owner_repo":"%s","target":"%s","worktree_paths":["%s"],"extra_paths":{"admin_dir":"%s","worktree_gitfile":"%s"},"state":{"worktree_dir_present":true,"worktree_registered":true,"worktree_head":{"kind":"branch","ref":"feature-f5","commit":"%s"},"owner_head":{"kind":"branch","ref":"master","commit":"%s"},"dirty_owner":%s,"dirty_worktree":%s},"measurements":{"unique_commits":%s,"unpushed_commits":%s,"ahead_of_origin_master":%s,"worktree_registration_count":%s},"commits":{"base":"%s","tip":"%s"},"expected":{"verdict":"NOT-SAFE","receipt":"unpushed-branch"},"env":{"SHOKUNIN_ROOT":"%s"}}' \
  "$CASE" \
  "$(json_escape "$OUT")" \
  "$(json_escape "$repo")" \
  "$(json_escape "$wt")" \
  "$(json_escape "$wt")" \
  "$(json_escape "$admin")" \
  "$(json_escape "$wt/.git")" \
  "$tip" \
  "$base" \
  "$dirty_owner" \
  "$dirty_wt" \
  "$unique" \
  "$unpushed" \
  "$ahead" \
  "$reg_count" \
  "$base" \
  "$tip" \
  "$(json_escape "$OUT")")"

if [ -n "$MANIFEST_OUT" ]; then
  printf '%s\n' "$manifest" > "$MANIFEST_OUT"
fi
printf '%s\n' "$manifest"
