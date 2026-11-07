#!/bin/bash
# souji r80 C2 domain trial (v2): base and candidate --dry-run over the same three real lane targets; byte-compare stdout.
# v1 (domain-trial-v1-vacuous.sh) left SOUJI_VERIFY_BIN unset: both copies, outside the lane, looked for
# <copy dir>/../tools/souji-verify.sh, exited 1 with empty stdout, and compared equal (vacuous). v2 pins the lane's
# engine and requires one RESULT line per target in both outputs before it can say identical=yes.
set -u
L=/home/vgpnk/Projects/shokunin/souji-shokunin; BASE=$1; CAND=$2; W=$3
tg=("$L/census/round-79/srcs/bash.info.gz-5.3" "$L/census/round-79/records/wave-w1" "$L/PROVINCE.md")
printf 'base_sha256=%s\ncand_sha256=%s\n' "$(sha256sum < "$BASE" | cut -d' ' -f1)" "$(sha256sum < "$CAND" | cut -d' ' -f1)"
mkdir -p "$W/b" "$W/c"
export SOUJI_VERIFY_BIN=$L/tools/souji-verify.sh
TMPDIR=$W/b bash "$BASE" --dry-run "$L" "${tg[@]}" > "$W/base.out" 2> "$W/base.err"; brc=$?
TMPDIR=$W/c bash "$CAND" --dry-run "$L" "${tg[@]}" > "$W/cand.out" 2> "$W/cand.err"; crc=$?
printf 'base_rc=%s cand_rc=%s\n' "$brc" "$crc"
printf 'base_stdout_sha256=%s\ncand_stdout_sha256=%s\n' "$(sha256sum < "$W/base.out" | cut -d' ' -f1)" "$(sha256sum < "$W/cand.out" | cut -d' ' -f1)"
printf 'signal_lines=%s\n' "$(grep -c '^SIGNAL' "$W/cand.out")"
printf 'tmpleft_base=%s tmpleft_cand=%s\n' "$(find "$W/b" -mindepth 1 | wc -l)" "$(find "$W/c" -mindepth 1 | wc -l)"
echo '--- candidate stdout'; cat "$W/cand.out"
nb=$(grep -c '^RESULT' "$W/base.out"); nc=$(grep -c '^RESULT' "$W/cand.out")
printf 'result_lines_base=%s result_lines_cand=%s\n' "$nb" "$nc"
if [ "$nb" = "${#tg[@]}" ] && [ "$nc" = "${#tg[@]}" ] && cmp -s "$W/base.out" "$W/cand.out" && [ "$brc" = "$crc" ]; then
  echo 'TRIAL identical=yes'; exit 0
fi
echo 'TRIAL identical=no'; diff "$W/base.out" "$W/cand.out" | head -20; exit 1
