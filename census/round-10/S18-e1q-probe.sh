#!/usr/bin/env bash
# S18 E1 quarantine probe: porcelain failure must not read as "clean".
set -uo pipefail
TOOLS=${1:-/home/vgpnk/Projects/shokunin/souji-shokunin/tools}
B=$(mktemp -d -p /var/tmp s18-e1q.XXXXXX)
export TMPDIR=/var/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null LC_ALL=C
export GIT_AUTHOR_NAME=s18 GIT_AUTHOR_EMAIL=s18@x GIT_COMMITTER_NAME=s18 GIT_COMMITTER_EMAIL=s18@x
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE SOUJI_Q_TEST_HOOK SOUJI_QUARANTINE_ALLOW_LIVE
VNAME=${VNAME:-cand-e2-verify.sh} VANAME=${VANAME:-cand-e2-vault.sh} QNAME=${QNAME:-cand-e2-quarantine.sh}
FLEET=$B/fleet; R=$FLEET/case-shokunin; mkdir -p "$FLEET"
git init -q --initial-branch=main "$R"
printf 'seed\n' > "$R/seed.txt"; printf 'mode-test\n' > "$R/mode.txt"
git -C "$R" add -A; t=$(git -C "$R" write-tree); c=$(printf 'c\n' | git -C "$R" commit-tree "$t")
git -C "$R" update-ref refs/heads/main "$c"; git -C "$R" update-ref refs/remotes/origin/main "$c"
git -C "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$B/ledger.tsv"
export SHOKUNIN_ROOT=$FLEET SOUJI_LEDGER=$B/ledger.tsv SOUJI_Q_SHOKUNIN_ROOT=$FLEET SOUJI_Q_LEDGER=$B/ledger.tsv
export SOUJI_VERIFY_BIN=$TOOLS/$VNAME
chmod +x "$R/mode.txt"   # mode-only change: content == intro blob
mkdir -p "$B/bin"; REAL=$(command -v git)
cat > "$B/bin/git" <<'SH'
#!/usr/bin/env bash
for a in "$@"; do
  case "$a" in status) echo "fatal: simulated status failure" >&2; exit 128;; esac
done
exec "$S18_REAL_GIT" "$@"
SH
chmod +x "$B/bin/git"
echo "=== control (no shim): mode-only change must block ==="
bash "$TOOLS/$QNAME" --hold 0 "$R" "$R/mode.txt" 2>&1 | grep -E '^RESULT' | sed 's/^/  /'
echo "  survives: $([ -f "$R/mode.txt" ] && echo YES || echo NO-DELETED)"
echo "=== E1-q: status query fails, mode-only change ==="
PATH="$B/bin:$PATH" S18_REAL_GIT=$REAL bash "$TOOLS/$QNAME" --hold 0 "$R" "$R/mode.txt" 2>&1 | grep -E '^RESULT' | sed 's/^/  /'
echo "  survives: $([ -f "$R/mode.txt" ] && echo YES || echo NO-DELETED)"
echo "B=$B"
