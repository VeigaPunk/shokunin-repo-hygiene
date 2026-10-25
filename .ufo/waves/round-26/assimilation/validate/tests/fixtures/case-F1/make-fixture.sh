#!/usr/bin/env bash
# Fixture case F1 — the pushed file's introducing commit IS an ancestor of the
# default-branch ref (a fake origin/master minted locally with `git update-ref`).
# Expectation: pushed.txt -> SAFE, receipt "pushed".
#
# Repo shape (both case fixtures share it, so either target is checkable):
#   commit1 (pushed.txt)   -> refs/heads/master == refs/remotes/origin/master
#                             refs/remotes/origin/HEAD -> refs/remotes/origin/master
#   commit2 (local-only.txt)-> refs/heads/local-work, HEAD -> local-work, unpublished
# So pushed.txt is an ancestor of origin/master, of refs/heads/master and of HEAD;
# local-only.txt is an ancestor of HEAD only, never of a published ref.
#
# Usage: make-fixture.sh [OUT_DIR]      (OUT_DIR defaults to this case directory)
# Builds a throwaway git repo under mktemp -d, writes OUT_DIR/expected.json,
# prints that JSON on stdout, and fixture key=value facts on stderr.
# Re-runnable: every run mints a fresh fixture and rewrites expected.json.
# No network, no fetch, no mutating git porcelain — commits are built with
# plumbing only (write-tree / commit-tree / update-ref / symbolic-ref HEAD).
set -euo pipefail

case_name=F1
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
out_dir=${1:-${OUT_DIR:-$script_dir}}

# Hermetic: ignore operator/global git config, pin identity + dates so object
# ids are reproducible across runs, never prompt.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_TERMINAL_PROMPT=0
export GIT_AUTHOR_NAME='Souji Fixture' GIT_AUTHOR_EMAIL='fixture@souji.local'
export GIT_COMMITTER_NAME='Souji Fixture' GIT_COMMITTER_EMAIL='fixture@souji.local'
export GIT_AUTHOR_DATE='2001-01-01T00:00:00+0000' GIT_COMMITTER_DATE='2001-01-01T00:00:00+0000'

tmp_base=${SOUJI_FIXTURE_TMPDIR:-${TMPDIR:-/tmp}}
tmp_base=${tmp_base%/}
mkdir -p "$tmp_base"
fixture_root=$(mktemp -d "$tmp_base/souji-fixture-case-$case_name.XXXXXX")
repo="$fixture_root/repo"
mkdir -p "$repo"

git init -q -b master "$repo" 2>/dev/null || {
  git init -q "$repo"
  git -C "$repo" symbolic-ref HEAD refs/heads/master
}
git -C "$repo" config user.name 'Souji Fixture'
git -C "$repo" config user.email 'fixture@souji.local'
git -C "$repo" config commit.gpgsign false
git -C "$repo" config core.autocrlf false
git -C "$repo" config gc.auto 0

pushed_path="$repo/pushed.txt"
local_only_path="$repo/local-only.txt"

# commit1: introducing commit of pushed.txt, published to the fake remote ref.
printf 'pushed fixture content\n' >"$pushed_path"
git -C "$repo" add -- pushed.txt
tree1=$(git -C "$repo" write-tree)
commit1=$(git -C "$repo" commit-tree "$tree1" -m 'fixture: add pushed.txt')
git -C "$repo" update-ref refs/heads/master "$commit1"
git -C "$repo" update-ref refs/remotes/origin/master "$commit1"
git -C "$repo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

# commit2: local-only.txt, on the unpublished branch local-work. HEAD is moved
# to local-work by metadata only (index + worktree already hold commit2's tree),
# so the target exists on disk, stays clean, and `git log -- <path>` (HEAD-based)
# still finds its introducing commit.
printf 'local-only fixture content\n' >"$local_only_path"
git -C "$repo" add -- local-only.txt
tree2=$(git -C "$repo" write-tree)
commit2=$(git -C "$repo" commit-tree "$tree2" -p "$commit1" -m 'fixture: add local-only.txt')
git -C "$repo" update-ref refs/heads/local-work "$commit2"
git -C "$repo" symbolic-ref HEAD refs/heads/local-work

case "$pushed_path$local_only_path" in
*[\"\\]*)
  printf 'make-fixture: refusing path with quote or backslash: %s\n' "$pushed_path" >&2
  exit 1
  ;;
esac

mkdir -p "$out_dir"
json_tmp=$(mktemp "$fixture_root/expected.XXXXXX")
cat >"$json_tmp" <<JSON
{
  "targets": [
    "$pushed_path",
    "$local_only_path"
  ],
  "expect": [
    {
      "path": "$pushed_path",
      "verdict": "SAFE",
      "receipt": "pushed"
    },
    {
      "path": "$local_only_path",
      "verdict": "NOT-SAFE"
    }
  ]
}
JSON
mv -f "$json_tmp" "$out_dir/expected.json"

{
  printf 'fixture_root=%s\n' "$fixture_root"
  printf 'repo=%s\n' "$repo"
  printf 'head_branch=%s\n' "$(git -C "$repo" symbolic-ref --quiet --short HEAD || echo DETACHED)"
  printf 'pushed_target=%s\n' "$pushed_path"
  printf 'local_only_target=%s\n' "$local_only_path"
  printf 'commit_pushed=%s\n' "$commit1"
  printf 'commit_local_only=%s\n' "$commit2"
  printf 'expected_json=%s\n' "$out_dir/expected.json"
} >&2

cat "$out_dir/expected.json"
