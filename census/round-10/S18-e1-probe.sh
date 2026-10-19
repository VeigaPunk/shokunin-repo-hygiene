#!/usr/bin/env bash
# S18 fresh E1 probe: failed git queries must refuse, never count as zero.
set -uo pipefail
TOOLS=${1:-/home/vgpnk/Projects/shokunin/souji-shokunin/tools}
LABEL=${2:-installed}
B=$(mktemp -d -p /var/tmp "s18-e1-$LABEL.XXXXXX")
export TMPDIR=/var/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null LC_ALL=C
export GIT_AUTHOR_NAME=s18 GIT_AUTHOR_EMAIL=s18@x GIT_COMMITTER_NAME=s18 GIT_COMMITTER_EMAIL=s18@x
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE SOUJI_Q_TEST_HOOK SOUJI_QUARANTINE_ALLOW_LIVE
FLEET=$B/fleet; R=$FLEET/case-shokunin; mkdir -p "$FLEET"
git init -q --initial-branch=main "$R"
printf 'seed\n' > "$R/seed.txt"; printf 'payload\n' > "$R/art.txt"
git -C "$R" add -A; t=$(git -C "$R" write-tree); c=$(printf 'c\n' | git -C "$R" commit-tree "$t")
git -C "$R" update-ref refs/heads/main "$c"; git -C "$R" update-ref refs/remotes/origin/main "$c"
git -C "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$B/ledger.tsv"
export SHOKUNIN_ROOT=$FLEET SOUJI_LEDGER=$B/ledger.tsv SOUJI_Q_SHOKUNIN_ROOT=$FLEET SOUJI_Q_LEDGER=$B/ledger.tsv
VNAME=${VNAME:-cand-e2-verify.sh} VANAME=${VANAME:-cand-e2-vault.sh} QNAME=${QNAME:-cand-e2-quarantine.sh}
export SOUJI_VERIFY_BIN=$TOOLS/$VNAME
# shim: fail ONLY the unpushed-touching history query (log --branches --not --remotes)
mkdir -p "$B/bin"
cat > "$B/bin/git" <<'SH'
#!/usr/bin/env bash
for a in "$@"; do
  case "$a" in --branches) echo "fatal: simulated index/object read failure" >&2; exit 128;; esac
done
exec "$S18_REAL_GIT" "$@"
SH
chmod +x "$B/bin/git"
REAL=$(command -v git)
echo "=== E1-a: pushed FILE, history query fails (verify/vault) ==="
out=$(PATH="$B/bin:$PATH" S18_REAL_GIT=$REAL bash "$TOOLS/$VNAME" "$R/art.txt" 2>&1); echo "  verify: $out"
out=$(PATH="$B/bin:$PATH" S18_REAL_GIT=$REAL bash "$TOOLS/$VANAME" "$R/art.txt" 2>&1 | head -1); echo "  vault : $out"
echo "=== E1-b: pushed FILE via quarantine stage2, history query fails ==="
out=$(PATH="$B/bin:$PATH" S18_REAL_GIT=$REAL bash "$TOOLS/$QNAME" --hold 0 "$R" "$R/art.txt" 2>&1)
printf '%s\n' "$out" | grep -E '^(RESULT|STAGE|VERDICT)' | head -6 | sed 's/^/  /'
echo "  art.txt survives: $([ -f "$R/art.txt" ] && echo YES || echo NO-DELETED)"
echo "  staged: $(ls -R "$R/.ufo-quarantine" 2>/dev/null | tr '\n' ' ')"
echo "=== E1-c: repo-root with git failing (verify/vault evidence) ==="
out=$(PATH="$B/bin:$PATH" S18_REAL_GIT=$REAL bash "$TOOLS/$VNAME" "$R" 2>&1); echo "  verify: $out"
echo "B=$B"
