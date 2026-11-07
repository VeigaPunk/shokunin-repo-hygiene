#!/bin/bash
# souji r80 C2 domain trial: base and candidate --dry-run over the same three real lane targets; byte-compare stdout
set -u
L=/home/vgpnk/Projects/shokunin/souji-shokunin; BASE=$1; CAND=$2; W=$3
tg=("$L/census/round-79/srcs/bash.info.gz-5.3" "$L/census/round-79/records/wave-w1" "$L/PROVINCE.md")
printf 'base_sha256=%s\ncand_sha256=%s\n' "$(sha256sum < "$BASE" | cut -d' ' -f1)" "$(sha256sum < "$CAND" | cut -d' ' -f1)"
mkdir -p "$W/b" "$W/c"
TMPDIR=$W/b bash "$BASE" --dry-run "$L" "${tg[@]}" > "$W/base.out" 2> "$W/base.err"; brc=$?
TMPDIR=$W/c bash "$CAND" --dry-run "$L" "${tg[@]}" > "$W/cand.out" 2> "$W/cand.err"; crc=$?
printf 'base_rc=%s cand_rc=%s\n' "$brc" "$crc"
printf 'base_stdout_sha256=%s\ncand_stdout_sha256=%s\n' "$(sha256sum < "$W/base.out" | cut -d' ' -f1)" "$(sha256sum < "$W/cand.out" | cut -d' ' -f1)"
printf 'signal_lines=%s\n' "$(grep -c '^SIGNAL' "$W/cand.out")"
printf 'tmpleft_base=%s tmpleft_cand=%s\n' "$(find "$W/b" -mindepth 1 | wc -l)" "$(find "$W/c" -mindepth 1 | wc -l)"
echo '--- candidate stdout'; cat "$W/cand.out"
if cmp -s "$W/base.out" "$W/cand.out" && [ "$brc" = "$crc" ]; then echo 'TRIAL identical=yes'; exit 0; fi
echo 'TRIAL identical=no'; diff "$W/base.out" "$W/cand.out" | head -20; exit 1
