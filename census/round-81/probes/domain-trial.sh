#!/usr/bin/env bash
# souji r81 C2 domain trial: base and candidate souji-vault-verify.sh, installed in turn at ONE path
# (<work>/arm/tools/souji-vault-verify.sh, so the tool's self-derived REPO_ROOT is the same for both arms; r80 M2),
# run over the same real lane targets with the lane's real ledger and the real fleet root, no CLI override.
# Prints per arm the rc and the sha256 of stdout, then `TRIAL identical=<yes|no> verdicts=<n per arm>`.
# Refuses a vacuous comparison: each arm must print exactly one VERDICT record per target (r80 S80CriticDiscern F4:
# the expected verdict count is part of the probe), else EXIT=1.
# usage: domain-trial.sh BASE_TOOL CAND_TOOL WORK TARGET...
set -u
base=$1 cand=$2 work=$3; shift 3
lane=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
fleet=$(dirname "$lane")
[[ -e $work ]] && { echo "domain-trial: $work exists" >&2; exit 2; }
mkdir -p "$work/arm/tools"
n=$#
declare -A rc sum cnt
for arm in base cand; do
  src=$base; [[ $arm == cand ]] && src=$cand
  install -m 0755 "$src" "$work/arm/tools/souji-vault-verify.sh"
  r=0
  ( cd "$lane" && env -u SOUJI_CLI_BIN -u SOUJI_CLI_TIMEOUT SOUJI_LEDGER="$lane/corpus/knowledge/obsidian-ledger.tsv" \
      SHOKUNIN_ROOT="$fleet" TMPDIR="$work" bash "$work/arm/tools/souji-vault-verify.sh" "$@" ) \
      > "$work/$arm.out" 2> "$work/$arm.err" || r=$?
  rc[$arm]=$r
  sum[$arm]=$(sha256sum < "$work/$arm.out" | cut -d' ' -f1)
  cnt[$arm]=$(grep -c $'^VERDICT\t' "$work/$arm.out")
  printf 'ARM %s sha256(tool)=%s rc=%s verdicts=%s stdout_sha256=%s\n' "$arm" \
    "$(sha256sum < "$src" | cut -d' ' -f1)" "$r" "${cnt[$arm]}" "${sum[$arm]}"
  sed 's/^/  /' "$work/$arm.out"
done
same=no
[[ ${rc[base]} == "${rc[cand]}" && ${sum[base]} == "${sum[cand]}" ]] && same=yes
echo "TRIAL identical=$same targets=$n verdicts=${cnt[base]}/${cnt[cand]}"
[[ $same == yes && ${cnt[base]} == "$n" && ${cnt[cand]} == "$n" ]] && exit 0
exit 1
