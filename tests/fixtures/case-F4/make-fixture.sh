#!/usr/bin/env bash
#
# tests/fixtures/case-F4/make-fixture.sh — build the F4 fixture (deterministic).
#
# F4: a repo registers a worktree whose directory has been deleted.
#     The registration survives in <owner>/.git/worktrees/wt-f4, and the
#     worktree branch is fully contained in the fake origin/master ref, so the
#     registering repo reports 0 unique commits for that worktree.
#     Expected verdict for the target path: SAFE(metadata-prune)
#
# layout built under <case_root> (see expected.json in this dir):
#   owner-shokunin/  repo, branch master (2 commits) + fake refs/remotes/origin/*
#   wt-f4            worktree on branch wt-f4; the DIRECTORY is removed after
#                    registration, the admin dir .git/worktrees/wt-f4 stays
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

CASE='F4'

die() { printf 'make-fixture(F4): %s\n' "$*" >&2; exit "${2:-2}"; }
note() { printf 'make-fixture(F4): %s\n' "$*" >&2; }

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

[ -n "$OUT" ] || OUT="$(mktemp -d "${TMPDIR:-/tmp}/souji-fixture-F4.XXXXXX")"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd -P)"

# --- refusal guards: never wipe anything repo-shaped or user-facing ---------
[ "$OUT" != '/' ] || die "refusing to wipe /"
case "$HOME/" in "$OUT"/*) die "refusing to wipe $OUT: it is an ancestor of \$HOME" ;; esac
for f in .git AGENTS.md make-fixture.sh tools/souji-verify.spec.md; do
  [ -e "$OUT/$f" ] && die "refusing to wipe $OUT: it contains '$f' — pass a fresh scratch dir"
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

# --- owner repo --------------------------------------------------------------
repo="$OUT/owner-shokunin"
git init -q "$repo"
base="$(fixture_commit "$repo" '-' 'fixture F4: base commit' 'README.md' 'souji fixture F4 base')"
tip="$(fixture_commit "$repo" "$base" 'fixture F4: second commit' 'docs/notes.md' 'souji fixture F4 notes')"
git -C "$repo" update-ref refs/heads/master "$tip"
git -C "$repo" symbolic-ref HEAD refs/heads/master
git -C "$repo" read-tree --reset -u HEAD   # materialise the main worktree (plumbing)

# fake remote: refs only, no network — nothing here may ever be fetched
git -C "$repo" config remote.origin.url '/nonexistent/souji-fixture-origin.git'
git -C "$repo" config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git -C "$repo" update-ref refs/remotes/origin/master "$tip"
git -C "$repo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

# --- registered worktree whose directory is then deleted ---------------------
wt="$OUT/wt-f4"
admin="$repo/.git/worktrees/wt-f4"
git -C "$repo" update-ref refs/heads/wt-f4 "$tip"
git -C "$repo" worktree add -q "$wt" wt-f4
rm -rf -- "$wt"

# --- self-checks: the fixture must actually be the shape F4 claims ----------
[ ! -e "$wt" ] || die "worktree dir still present: $wt" 1
[ -d "$admin" ] || die "worktree admin dir missing: $admin" 1
[ -f "$admin/HEAD" ] || die "worktree admin HEAD missing: $admin/HEAD" 1
grep -qx 'ref: refs/heads/wt-f4' "$admin/HEAD" || die "admin HEAD is not the wt-f4 branch" 1

reg_count="$(git -C "$repo" worktree list --porcelain | grep -c '^worktree ' || true)"
[ "$reg_count" = 2 ] || die "expected 2 worktree registrations, got $reg_count" 1
git -C "$repo" worktree list --porcelain | grep -qx "worktree $wt" \
  || die "registration for $wt not listed by worktree list --porcelain" 1

unique="$(git -C "$repo" log --oneline wt-f4 --not --all | wc -l | tr -d ' ')"
unpushed="$(git -C "$repo" log --oneline wt-f4 --not --remotes | wc -l | tr -d ' ')"
[ "$unique" = 0 ] || die "unique_commits=$unique (want 0) — spec rule for SAFE(metadata-prune)" 1
[ "$unpushed" = 0 ] || die "unpushed_commits=$unpushed (want 0) — wt-f4 tip must be under a remote-tracking ref" 1
dirty_owner="$(git -C "$repo" status --porcelain | wc -l | tr -d ' ')"
[ "$dirty_owner" = 0 ] || die "owner tree dirty ($dirty_owner entries) — fixture must be clean" 1
awk_meta="$(git -C "$repo" rev-parse --verify --quiet refs/heads/wt-f4)" || die "wt-f4 ref missing" 1
[ "$awk_meta" = "$tip" ] || die "wt-f4 tip != master tip" 1

# --- resolved expected.json (default: <out>/expected.json) ------------------
RESOLVED_EXPECTED="${RESOLVED_EXPECTED:-$OUT/expected.json}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
[ -f "$script_dir/expected.json" ] || die "expected.json not found next to make-fixture.sh ($script_dir)"
case "$OUT" in *'|'*|*'&'*|*'\'*) die "--out contains sed-hostile characters; pass a plain scratch path" ;; esac
sed "s|\${CASE_ROOT}|$OUT|g" "$script_dir/expected.json" > "$RESOLVED_EXPECTED"
note "resolved expected.json -> $RESOLVED_EXPECTED"

manifest="$(printf '{"case":"%s","case_root":"%s","owner_repo":"%s","target":"%s","worktree_paths":["%s"],"extra_paths":{"admin_dir":"%s"},"state":{"worktree_dir_present":false,"worktree_registered":true,"worktree_head":{"kind":"branch","ref":"wt-f4","commit":"%s"},"owner_head":{"kind":"branch","ref":"master","commit":"%s"},"dirty_owner":%s},"measurements":{"unique_commits":%s,"unpushed_commits":%s,"worktree_registration_count":%s},"commits":{"base":"%s","tip":"%s"},"expected":{"verdict":"SAFE","receipt":"metadata-prune"},"env":{"SHOKUNIN_ROOT":"%s"}}' \
  "$CASE" \
  "$(json_escape "$OUT")" \
  "$(json_escape "$repo")" \
  "$(json_escape "$wt")" \
  "$(json_escape "$wt")" \
  "$(json_escape "$admin")" \
  "$tip" \
  "$tip" \
  "$dirty_owner" \
  "$unique" \
  "$unpushed" \
  "$reg_count" \
  "$base" \
  "$tip" \
  "$(json_escape "$OUT")")"

if [ -n "$MANIFEST_OUT" ]; then
  printf '%s\n' "$manifest" > "$MANIFEST_OUT"
fi
printf '%s\n' "$manifest"
