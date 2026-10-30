#!/usr/bin/env bash
# score-candidate.sh — score candidate bytes with a frozen r43 counter without touching the lane.
#
#   bash census/round-43/score-candidate.sh <claim> <scratch-root> <dest-path>=<src-file>...
#
#   claim   c1 | c2 | c3      (counter census/round-43/<claim>-counter.py)
#   dest    repo-relative path the candidate would occupy in the lane, from the allowlist:
#           tools/souji-freeze-check.py            (c2 candidate tool)
#           tools/souji-worktree-drift.py          (c3 candidate tool, N10 fix)
#           tests/fixtures/r43-drift-survivors.py  (c3 candidate fixture)
#           tests/fixtures/r43-correction-prose.py (c1 fixture, for its own self-scoring)
#           census/round-43/c1-required.tsv        (c1 register variant probes)
#           corpus/lessons/round-43.md             (c1 lesson variants)
#           SCORECARD.md                           (append-only probes)
#   src     the candidate file (outside the lane)
#
# The script clones the lane's committed master tip with `git clone --shared` into a fresh
# directory under <scratch-root>, copies each candidate over its dest, commits in the CLONE only
# (identity through the environment, every git call names -C), runs the counter at that commit and
# removes the clone. It never writes into the lane. Exit code and output are the counter's.
set -u
LANE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
claim="${1:?claim}"; root="${2:?scratch-root}"; shift 2
case "$claim" in c1|c2|c3) ;; *) echo "score-candidate: unknown claim $claim" >&2; exit 2;; esac
[ -d "$root" ] || { echo "score-candidate: scratch root $root is not a directory" >&2; exit 2; }
D="$(mktemp -d -p "$root" souji-r43-score.XXXXXX)" || exit 2
trap 'rm -rf -- "$D"' EXIT
git clone -q --shared "$LANE" "$D/clone" || exit 2
C="$D/clone"
git -C "$C" checkout -q refs/heads/master || exit 2
[ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ] || { echo "score-candidate: clone root mismatch" >&2; exit 2; }
for pair in "$@"; do
  dest="${pair%%=*}"; src="${pair#*=}"
  # dest is allowlisted; traversal, absolute paths, symlinked destinations and
  # counter/population/preregistration paths are refused (r42 sentinel N9a-c pattern).
  case "$dest" in
    tools/souji-freeze-check.py|tools/souji-worktree-drift.py|tests/fixtures/r43-drift-survivors.py|tests/fixtures/r43-correction-prose.py|census/round-43/c1-required.tsv|corpus/lessons/round-43.md|SCORECARD.md) ;;
    *) echo "score-candidate: dest $dest is not on the allowlist" >&2; exit 2;;
  esac
  [ ! -L "$C/$dest" ] || { echo "score-candidate: dest $dest is a symlink in the clone" >&2; exit 2; }
  [ -f "$src" ] || { echo "score-candidate: $src is not a file" >&2; exit 2; }
  mkdir -p "$C/$(dirname "$dest")"
  cp "$src" "$C/$dest"
done
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
git -C "$C" add -A && git -C "$C" commit -q --allow-empty -m "candidate" || exit 2
REV="$(git -C "$C" rev-parse HEAD)"
python3 -B "$C/census/round-43/$claim-counter.py" --root "$C" --rev "$REV" --scratch "$D"
