#!/usr/bin/env bash
# case-F9 fixture builder (D1: default-branch fallback resolution).
#
# Builds a self-contained git repo at <dest>/repo with:
#   - NO refs/remotes/origin/HEAD          (symbolic-ref resolution fails)
#   - exactly ONE refs/remotes/origin/* ref: refs/remotes/origin/master
#   - NO local refs/heads/master           (so the 'master' local fallback
#                                           cannot rescue a broken resolver)
#   - pushed-file.txt introduced by a commit that is an ancestor of
#     refs/remotes/origin/master
#
# Usage: bash build.sh [dest-dir]     # default dest = this script's dir
#
# Deterministic: fixed author/committer identities and dates, no user/system
# git config, no hooks, no reflogs. Re-running yields the same SHAs.
set -euo pipefail

dest="${1:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)}"
if [ -z "$dest" ] || [ "$dest" = "/" ]; then
  echo "build.sh: refusing dest '$dest'" >&2
  exit 2
fi
repo="$dest/repo"
mkdir -p "$dest"
rm -rf "$repo"
mkdir -p "$repo"

export GIT_AUTHOR_NAME="souji fixture"
export GIT_AUTHOR_EMAIL="souji@shokunin.local"
export GIT_COMMITTER_NAME="souji fixture"
export GIT_COMMITTER_EMAIL="souji@shokunin.local"
export GIT_AUTHOR_DATE="2024-01-01T00:00:00+0000"
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL=/dev/null

tmpl="$(mktemp -d)"
trap 'rm -rf "$tmpl"' EXIT
export GIT_TEMPLATE_DIR="$tmpl"

g() { git -c core.hooksPath="$tmpl/nohooks" -c core.autocrlf=false -c core.logAllRefUpdates=false -C "$repo" "$@"; }

g init -q -b main .

printf 'fixture base\n' >"$repo/base.txt"
g add base.txt
tree=$(g write-tree)
c1=$(g commit-tree "$tree" -m "fixture: root commit")

printf 'pushed payload\n' >"$repo/pushed-file.txt"
g add pushed-file.txt
tree=$(g write-tree)
c2=$(g commit-tree "$tree" -p "$c1" -m "fixture: add pushed-file.txt")

printf 'fixture base v2\n' >"$repo/base.txt"
g add base.txt
tree=$(g write-tree)
c3=$(g commit-tree "$tree" -p "$c2" -m "fixture: update base.txt")

g update-ref refs/heads/main "$c3"
g update-ref refs/remotes/origin/master "$c3"

# --- fixture invariants (fail loudly if git behaviour differs) ---------------
origin_refs="$(g for-each-ref --format='%(refname)' refs/remotes/origin)"
[ -z "$(g for-each-ref --format='%(refname)' refs/remotes/origin/HEAD)" ] \
  || { echo "build.sh: origin/HEAD unexpectedly present" >&2; exit 1; }
[ "$(printf '%s\n' "$origin_refs" | grep -c .)" -eq 1 ] \
  || { echo "build.sh: expected exactly 1 origin ref, got: $origin_refs" >&2; exit 1; }
[ "$origin_refs" = "refs/remotes/origin/master" ] \
  || { echo "build.sh: unexpected origin ref: $origin_refs" >&2; exit 1; }
[ -z "$(g for-each-ref --format='%(refname)' refs/heads/master)" ] \
  || { echo "build.sh: refs/heads/master unexpectedly present" >&2; exit 1; }
[ "$(g log --diff-filter=A --format=%H -1 -- pushed-file.txt)" = "$c2" ] \
  || { echo "build.sh: pushed-file.txt introducer mismatch" >&2; exit 1; }
g merge-base --is-ancestor "$c2" refs/remotes/origin/master \
  || { echo "build.sh: introducer is not an ancestor of origin/master" >&2; exit 1; }
g merge-base --is-ancestor "$c3" refs/remotes/origin/master \
  || { echo "build.sh: origin/master does not point at tip" >&2; exit 1; }
[ -z "$(g status --porcelain)" ] \
  || { echo "build.sh: working tree not clean" >&2; exit 1; }

printf 'case-F9 repo built at %s\n' "$repo"
printf '  refs/heads/main          -> %s\n' "$(g rev-parse refs/heads/main)"
printf '  refs/remotes/origin/master -> %s\n' "$(g rev-parse refs/remotes/origin/master)"
printf '  pushed-file.txt introducer -> %s\n' "$c2"
