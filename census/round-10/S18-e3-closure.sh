#!/usr/bin/env bash
set -uo pipefail
T=${1:-/home/vgpnk/Projects/shokunin/souji-shokunin/tools}
export TMPDIR=/var/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null LC_ALL=C
export GIT_AUTHOR_NAME=s18 GIT_AUTHOR_EMAIL=s18@x GIT_COMMITTER_NAME=s18 GIT_COMMITTER_EMAIL=s18@x
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE
VNAME=${VNAME:-cand-e2-verify.sh} VANAME=${VANAME:-cand-e2-vault.sh} QNAME=${QNAME:-cand-e2-quarantine.sh}
B=$(mktemp -d -p /var/tmp s18-e3close.XXXXXX)
FLEET=$B/fleet; R=$FLEET/main-shokunin; mkdir -p "$FLEET"
git init -q --initial-branch=main "$R"; printf 'base\n' > "$R/base.txt"
git -C "$R" add -A; t=$(git -C "$R" write-tree); c1=$(printf 'c\n' | git -C "$R" commit-tree "$t")
git -C "$R" update-ref refs/heads/main "$c1"; git -C "$R" update-ref refs/remotes/origin/main "$c1"
git -C "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$B/ledger.tsv"
export SHOKUNIN_ROOT=$FLEET SOUJI_LEDGER=$B/ledger.tsv SOUJI_Q_SHOKUNIN_ROOT=$FLEET SOUJI_Q_LEDGER=$B/ledger.tsv
W=$B/wt-dead; mkdir -p "$W"; git -C "$R" worktree add -q --detach "$W" "$c1"
printf 'private\n' > "$W/private.txt"; git -C "$W" add -A; tw=$(git -C "$W" write-tree)
c2=$(printf 'p\n' | git -C "$W" commit-tree "$tw" -p "$c1"); git -C "$W" update-ref HEAD "$c2"
rm -rf "$W"
echo "fixture: private commit $c2, registration present, dir absent"
printf '  --not --all (old basis)      : '; git -C "$R" log --oneline "$c2" --not --all | wc -l
printf '  refs-only (new basis)        : '; git -C "$R" log --oneline "$c2" --not --branches --not --remotes --not --tags | wc -l
printf '  verify: '; bash "$T/$VNAME" "$W" 2>&1 | cut -f3,4,5
printf '  vault : '; bash "$T/$VANAME" --fallback "$W" 2>&1 | head -1 | cut -f3,4,5
echo "  --- quarantine stage1 (candidate engine) ---"
SOUJI_VERIFY_BIN=$T/$VNAME bash "$T/$QNAME" --hold 0 "$R" "$W" 2>&1 | grep -E '^RESULT' | cut -f3,4,5 | sed 's/^/  q: /'
echo "B=$B"
