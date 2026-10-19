#!/usr/bin/env bash
# S18 E2 probe: compiled Turkish locale + case-variant secret shapes.
set -uo pipefail
TOOLS=${1:-/home/vgpnk/Projects/shokunin/souji-shokunin/tools}
LABEL=${2:-baseline}
B=$(mktemp -d -p /var/tmp "s18-e2-$LABEL.XXXXXX")
export TMPDIR=/var/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=s18 GIT_AUTHOR_EMAIL=s18@x GIT_COMMITTER_NAME=s18 GIT_COMMITTER_EMAIL=s18@x
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE SOUJI_Q_TEST_HOOK SOUJI_QUARANTINE_ALLOW_LIVE
VNAME=${VNAME:-cand-e2-verify.sh} VANAME=${VANAME:-cand-e2-vault.sh} QNAME=${QNAME:-cand-e2-quarantine.sh}
FLEET=$B/fleet; R=$FLEET/case-shokunin; mkdir -p "$FLEET"
git init -q --initial-branch=main "$R"
printf 'seed\n' > "$R/seed.txt"; git -C "$R" add -A
t=$(git -C "$R" write-tree); c=$(printf 'c\n' | git -C "$R" commit-tree "$t")
git -C "$R" update-ref refs/heads/main "$c"; git -C "$R" update-ref refs/remotes/origin/main "$c"
git -C "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$B/ledger.tsv"
export SHOKUNIN_ROOT=$FLEET SOUJI_LEDGER=$B/ledger.tsv SOUJI_Q_SHOKUNIN_ROOT=$FLEET SOUJI_Q_LEDGER=$B/ledger.tsv
export SOUJI_VERIFY_BIN=$TOOLS/$VNAME
mkdir -p "$B/locale"
if localedef --no-archive -i tr_TR -f UTF-8 "$B/locale/tr_TR" >/dev/null 2>&1; then
  fold=$(env LOCPATH="$B/locale" LC_ALL=tr_TR bash -c 's=ID_RSA; printf "%s" "${s,,}"')
  echo "locale active: fold(ID_RSA)=$fold"
else
  echo "SKIP: no tr_TR locale source"; exit 0
fi
# secret-shaped fixtures, aged so a stale receipt would otherwise apply
mkdir -p "$R/.scratch"
for n in ID_RSA id_rsa Id_Rsa .ENV .env credENTIALS my-secret.pem; do
  d="$R/.scratch/$n"; mkdir -p "$d"; printf 'x\n' > "$d/f.txt"; touch -d '3 days ago' "$d"
done
echo "--- verify under tr_TR (want NOT-SAFE/secrets-refusal) ---"
for n in ID_RSA id_rsa Id_Rsa .ENV credENTIALS my-secret.pem; do
  p="$R/.scratch/$n"
  o=$(env LOCPATH="$B/locale" LC_ALL=tr_TR bash "$TOOLS/$VNAME" --stale-days 1 "$p" 2>&1)
  v=$(printf '%s' "$o" | cut -f3); r=$(printf '%s' "$o" | cut -f4)
  printf '  %-16s %s(%s)\n' "$n" "$v" "$r"
done
echo "--- vault under tr_TR ---"
for n in ID_RSA id_rsa .ENV; do
  p="$R/.scratch/$n"
  o=$(env LOCPATH="$B/locale" LC_ALL=tr_TR bash "$TOOLS/$VANAME" --fallback "$p" 2>&1 | head -1)
  printf '  %-16s %s(%s)\n' "$n" "$(printf '%s' "$o" | cut -f3)" "$(printf '%s' "$o" | cut -f4)"
done
echo "--- quarantine under tr_TR (want NOT-AUTHORIZED/secrets-refusal, file preserved) ---"
for n in ID_RSA id_rsa .ENV; do
  p="$R/.scratch/$n"
  o=$(env LOCPATH="$B/locale" LC_ALL=tr_TR bash "$TOOLS/$QNAME" --hold 0 "$R" "$p" 2>&1 | grep '^RESULT')
  printf '  %-16s %s(%s) survives=%s\n' "$n" "$(printf '%s' "$o" | cut -f3)" "$(printf '%s' "$o" | cut -f4)" "$([ -e "$p" ] && echo YES || echo NO)"
done
echo "B=$B"
