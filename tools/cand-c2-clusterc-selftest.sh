#!/usr/bin/env bash
# cand-c2-clusterc-selftest.sh — round-10 S06 cluster-C regression battery.
#
# Cluster C = nested-.git scope, symlink containment, and quarantine-root
# containment. Every case builds a fresh fixture under `mktemp -d -p /var/tmp`;
# the tools under test are only ever pointed at those fixture roots.
#
# The harness is tool-set-agnostic: point it at the installed tools and at
# tools/cand-c2-* to read the before/after difference for the same cases.
#
#   bash tools/cand-c2-clusterc-selftest.sh <tools-dir> [label]
#
# Refusal cases assert on the VERDICT (any non-SAFE verdict), not on the
# receipt label: labels are candidate-specific, and a label-coupled corpus
# reads a safety-preserving integration as failure. C2_STRICT_LABELS=1 also
# demands this candidate's exact labels, to surface label drift.
#
# Cases
#   C2R01 nested .git directory in a directory target      -> NOT-SAFE (r9 S06-D1)
#   C2R02 nested .git gitfile in a directory target        -> NOT-SAFE
#   C2R03 symlink in scope (link to outside live repo)     -> NOT-SAFE (r10 S06-Q2)
#   C2R04 dangling symlink in scope                        -> NOT-SAFE (r10 S06-Q2)
#   C2R05 symlinked quarantine root: refuse, no outside writes (r10 S06-Q1)
#   C2R06 symlinked quarantine DATE dir: refuse, no outside writes
#   C2R07 poisoned row must not abort the whole --list batch (r10 S06-Q3)
#   C2R08 index-write contract: verify/vault/census leave the index alone
#   C2R09 absent index is not created by a read-only probe
#   C2R10 nested repo behind a mode-000 subdir             -> NOT-SAFE
#   C2R11 control: plain tracked+pushed dir                -> SAFE(pushed)
#   C2R12 control: symlink as the target itself            -> NOT-SAFE symlink-refused
set -uo pipefail

TOOLS=$(readlink -f -- "${1:?tools dir required}")
LABEL=${2:-$(basename -- "$TOOLS")}
V=$TOOLS/souji-verify.sh
W=$TOOLS/souji-vault-verify.sh
Q=$TOOLS/souji-quarantine.sh
C=$TOOLS/souji-census.sh
for f in "$V" "$W" "$Q"; do
  [ -f "$f" ] || { printf 'missing tool: %s\n' "$f" >&2; exit 2; }
done

export LC_ALL=C TMPDIR=/var/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=souji-clusterc GIT_AUTHOR_EMAIL=souji-clusterc@fixture.invalid
export GIT_COMMITTER_NAME=souji-clusterc GIT_COMMITTER_EMAIL=souji-clusterc@fixture.invalid
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true
unset SOUJI_VERIFY_BIN SOUJI_QUARANTINE_ALLOW_LIVE SOUJI_Q_TEST_HOOK 2>/dev/null || true

CC_PASS=0 CC_FAIL=0
cc_ok() { CC_PASS=$((CC_PASS + 1)); printf 'PASS C2 %s\n' "$1"; }
cc_bad() { CC_FAIL=$((CC_FAIL + 1)); printf 'FAIL C2 %s: %s\n' "$1" "$2"; }
cc_check() { if [ "$2" = 1 ]; then cc_ok "$1"; else cc_bad "$1" "${3:-}"; fi; }

ROOT=$(mktemp -d -p /var/tmp "souji-c2-clusterc-$LABEL.XXXXXX")
trap 'chmod -R u+rwX "$ROOT" 2>/dev/null; rm -rf -- "$ROOT"' EXIT

cc_git() { git -C "$1" "${@:2}"; }

# cc_new <name> -> sets CCB (case dir), CCF (fleet), CCR (repo), CCL (ledger)
cc_new() {
  CCB=$ROOT/$1; CCF=$CCB/fleet; CCR=$CCF/probe-shokunin
  mkdir -p "$CCF"
  git init -q --initial-branch=main "$CCR"
  printf 'base\n' > "$CCR/base.txt"
  git -C "$CCR" add -A >/dev/null 2>&1
  git -C "$CCR" commit -qm base >/dev/null 2>&1
  cc_push
  CCL=$CCB/ledger.tsv
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\n' > "$CCL"
  export SHOKUNIN_ROOT=$CCF SOUJI_LEDGER=$CCL SOUJI_Q_LEDGER=$CCL SOUJI_Q_SHOKUNIN_ROOT=$CCF
}

cc_push() {
  local c; c=$(git -C "$CCR" rev-parse HEAD 2>/dev/null) || return 0
  git -C "$CCR" update-ref refs/remotes/origin/main "$c"
  git -C "$CCR" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
}

cc_commit() {
  git -C "$CCR" add -A >/dev/null 2>&1
  git -C "$CCR" commit -qm "$1" >/dev/null 2>&1
  cc_push
}

cc_age() { touch -d "$2" -- "$1" 2>/dev/null || touch -d "$2" "$1"; }

# Refusal assertions are VERDICT-based, not label-based: a refusal is a
# refusal whatever receipt string the engine mints. Exact receipt labels are
# candidate-specific (this candidate says nested-repo-or-unverifiable, the
# S15 merged bytes say secrets-refusal for the same protected descendant),
# so a label-coupled corpus reports safety-preserving integration as failure
# and cannot serve as a cross-candidate gate. Set C2_STRICT_LABELS=1 to also
# demand the exact labels this candidate mints (label-drift detection).
CC_STRICT=${C2_STRICT_LABELS:-0}

cc_field() { # $1 tool, $2 target, $3 column (3=verdict, 4=receipt)
  local out rest v
  out=$(bash "$1" -- "$2" 2>&1)
  rest=${out#*$'\t'}; rest=${rest#*$'\t'}   # drop the VERDICT tag and the path
  v=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  if [ "$3" = 3 ]; then printf '%s' "$v"; else printf '%s' "${rest%%$'\t'*}"; fi
}
cc_verify() { cc_field "$1" "$2" 4; }
cc_verdict() { cc_field "$1" "$2" 3; }

cc_refusal_ok() { # $1 tool, $2 target, $3 expected label (checked only in strict mode)
  local v
  v=$(cc_verdict "$1" "$2")
  [ "$v" != SAFE ] || return 1
  if [ "$CC_STRICT" = 1 ] && [ -n "${3:-}" ]; then
    [ "$(cc_verify "$1" "$2")" = "$3" ] || return 1
  fi
  return 0
}

cc_nested_repo() { # $1 dir -> real nested git repo with one commit
  mkdir -p "$1"
  git init -q --initial-branch=main "$1"
  printf 'nested\n' > "$1/work.txt"
  git -C "$1" add -A >/dev/null 2>&1
  git -C "$1" -c user.email=n@fixture.invalid -c user.name=n commit -qm nested >/dev/null 2>&1
}

# --------------------------------------------------------------- C2R01 ------
cc_new r01
cc_nested_repo "$CCR/r01/legacy"
printf 'outer\n' > "$CCR/r01/readme.txt"
cc_commit r01
cc_check "C2R01 nested .git dir refused" \
  "$(cc_refusal_ok "$V" "$CCR/r01" nested-repo-or-unverifiable && echo 1 || echo 0)" \
  "verify=$(cc_verdict "$V" "$CCR/r01")/$(cc_verify "$V" "$CCR/r01")"

# --------------------------------------------------------------- C2R02 ------
cc_new r02
mkdir -p "$CCR/r02/inner"
printf 'gitdir: %s\n' "$CCB/nowhere.git" > "$CCR/r02/inner/.git"
printf 'outer\n' > "$CCR/r02/readme.txt"
cc_commit r02
cc_check "C2R02 nested gitfile refused" \
  "$(cc_refusal_ok "$V" "$CCR/r02" nested-repo-or-unverifiable && echo 1 || echo 0)" \
  "verify=$(cc_verdict "$V" "$CCR/r02")/$(cc_verify "$V" "$CCR/r02")"

# --------------------------------------------------------------- C2R03 ------
# A directory whose ONLY nested live repo is reachable through a symlinked
# subdir. Pre-fix this scanned clean and earned SAFE(pushed).
cc_new r03
mkdir -p "$CCB/outside-live"
cc_nested_repo "$CCB/outside-live"
mkdir -p "$CCR/r03"
printf 'outer\n' > "$CCR/r03/readme.txt"
ln -s "$CCB/outside-live" "$CCR/r03/link"
cc_commit r03
cc_check "C2R03 symlink in scope refused (verify)" \
  "$(cc_refusal_ok "$V" "$CCR/r03" nested-repo-or-unverifiable && echo 1 || echo 0)" \
  "verify=$(cc_verdict "$V" "$CCR/r03")/$(cc_verify "$V" "$CCR/r03")"
cc_check "C2R03 symlink in scope refused (vault)" \
  "$(cc_refusal_ok "$W" "$CCR/r03" nested-repo-or-unverifiable && echo 1 || echo 0)" \
  "vault=$(cc_verdict "$W" "$CCR/r03")/$(cc_verify "$W" "$CCR/r03")"

# --------------------------------------------------------------- C2R04 ------
cc_new r04
mkdir -p "$CCR/r04"
printf 'outer\n' > "$CCR/r04/readme.txt"
ln -s "$CCB/does-not-exist" "$CCR/r04/dangling"
cc_commit r04
cc_check "C2R04 dangling symlink in scope refused" \
  "$(cc_refusal_ok "$V" "$CCR/r04" nested-repo-or-unverifiable && echo 1 || echo 0)" \
  "verify=$(cc_verdict "$V" "$CCR/r04")/$(cc_verify "$V" "$CCR/r04")"

# --------------------------------------------------------------- C2R05 ------
# Symlinked quarantine root must refuse and write nothing outside the repo.
cc_new r05
OUT=$CCB/outside-q; mkdir -p "$OUT"
printf 'SENTINEL\n' > "$OUT/sentinel.txt"
mkdir -p "$CCR/.scratch/r05"; printf 'stale junk\n' > "$CCR/.scratch/r05/old.out"
cc_age "$CCR/.scratch/r05/old.out" '3 days ago'; cc_age "$CCR/.scratch/r05" '3 days ago'
cc_commit r05
ln -s "$OUT" "$CCR/.ufo-quarantine"
out=$(bash "$Q" --hold 0 "$CCR" .scratch/r05 2>&1); rc=$?
cc_check "C2R05 symlinked quarantine root refused" \
  "$([ "$rc" = 3 ] && [ "$(printf '%s' "$out" | grep -c '^RESULT.*NOT-AUTHORIZED')" = 1 ] \
     && { [ "$CC_STRICT" != 1 ] || [ "$(printf '%s' "$out" | grep -c '^RESULT.*quarantine-root-symlink')" = 1 ]; } \
     && echo 1 || echo 0)" \
  "rc=$rc out=$(printf '%s' "$out" | grep '^RESULT')"
cc_check "C2R05 original survives" "$([ -e "$CCR/.scratch/r05/old.out" ] && echo 1 || echo 0)"
cc_check "C2R05 no writes outside the repo" \
  "$([ "$(find "$OUT" -mindepth 1 | grep -vc '^'"$OUT"'/sentinel.txt$')" = 0 ] && echo 1 || echo 0)" \
  "outside=$(find "$OUT" -mindepth 1 | tr '\n' ' ')"
rm -f "$CCR/.ufo-quarantine"

# C2R05b: the abort path is where retained bytes actually hurt. A failing
# second check keeps the staged copy; with a symlinked root those bytes rest
# outside the repo, outside any quarantine the operator knows about. A FILE
# target is required: a directory target cannot be tampered by the hook.
cc_new r05b
OUT=$CCB/outside-ab; mkdir -p "$OUT"
printf 'stale junk\n' > "$CCR/old.out"
cc_age "$CCR/old.out" '3 days ago'
cc_commit r05b
HOOK=$CCB/hook.sh
printf '#!/usr/bin/env bash\nprintf "TAMPER" >> "$1"\n' > "$HOOK"
ln -s "$OUT" "$CCR/.ufo-quarantine"
out=$(SOUJI_Q_SELFTEST_ACTIVE=1 SOUJI_Q_TEST_HOOK="$HOOK" \
  bash "$Q" --hold 0 "$CCR" old.out 2>&1); rc=$?
cc_check "C2R05b abort leaves nothing outside the repo" \
  "$([ "$(find "$OUT" -mindepth 1 | wc -l)" = 0 ] && echo 1 || echo 0)" \
  "rc=$rc outside=$(find "$OUT" -mindepth 1 | tr '\n' ' ')"
cc_check "C2R05b original preserved" "$([ -e "$CCR/old.out" ] && echo 1 || echo 0)"
rm -f "$CCR/.ufo-quarantine"

# --------------------------------------------------------------- C2R06 ------
# Real .ufo-quarantine dir, but the per-date subdir is a symlink outside.
cc_new r06
OUT=$CCB/outside-qd; mkdir -p "$OUT"
printf 'SENTINEL\n' > "$OUT/sentinel.txt"
mkdir -p "$CCR/.ufo-quarantine"
ln -s "$OUT" "$CCR/.ufo-quarantine/$(date -u +%F)"
mkdir -p "$CCR/.scratch/r06"; printf 'stale junk\n' > "$CCR/.scratch/r06/old.out"
cc_age "$CCR/.scratch/r06/old.out" '3 days ago'; cc_age "$CCR/.scratch/r06" '3 days ago'
cc_commit r06
out=$(bash "$Q" --hold 0 "$CCR" .scratch/r06 2>&1); rc=$?
cc_check "C2R06 symlinked date dir refused" \
  "$([ "$(printf '%s' "$out" | grep -c '^RESULT.*NOT-AUTHORIZED')" = 1 ] && echo 1 || echo 0)" \
  "rc=$rc out=$(printf '%s' "$out" | grep '^RESULT')"
cc_check "C2R06 original survives" "$([ -e "$CCR/.scratch/r06/old.out" ] && echo 1 || echo 0)"
cc_check "C2R06 no writes outside the repo" \
  "$([ "$(find "$OUT" -mindepth 1 | grep -vc '^'"$OUT"'/sentinel.txt$')" = 0 ] && echo 1 || echo 0)" \
  "outside=$(find "$OUT" -mindepth 1 | tr '\n' ' ')"

# --------------------------------------------------------------- C2R07 ------
# A --list batch whose middle row is poisoned (symlink in scope) must not
# abort the run: every row gets a RESULT and the SUMMARY is emitted.
cc_new r07
mkdir -p "$CCR/.scratch/aaa" "$CCR/.scratch/poison" "$CCR/.scratch/zzz"
printf 'a\n' > "$CCR/.scratch/aaa/a.txt"
printf 'z\n' > "$CCR/.scratch/zzz/z.txt"
printf 'p\n' > "$CCR/.scratch/poison/p.txt"
ln -s "$CCF" "$CCR/.scratch/poison/link"
for d in aaa poison zzz; do cc_age "$CCR/.scratch/$d" '4 days ago'; done
cc_commit r07
LIST=$CCB/list.tsv
{
  printf 'path\treceipt\n'
  printf '%s\tpushed\n' "$CCR/.scratch/aaa"
  printf '%s\tpushed\n' "$CCR/.scratch/poison"
  printf '%s\tpushed\n' "$CCR/.scratch/zzz"
} > "$LIST"
out=$(bash "$Q" --hold 0 --list "$LIST" "$CCR" 2>&1); rc=$?
cc_check "C2R07 batch completes with a SUMMARY" \
  "$([ "$(printf '%s' "$out" | grep -c '^SUMMARY')" = 1 ] && echo 1 || echo 0)" \
  "rc=$rc tail=$(printf '%s' "$out" | tail -1)"
cc_check "C2R07 every row reported" \
  "$([ "$(printf '%s' "$out" | grep -c '^RESULT')" = 3 ] && echo 1 || echo 0)" \
  "results=$(printf '%s' "$out" | grep -c '^RESULT')"
cc_check "C2R07 poisoned row refused, others unaffected" \
  "$([ "$(printf '%s' "$out" | grep -c '^RESULT.*poison.*NOT-AUTHORIZED')" = 1 ] && echo 1 || echo 0)" \
  "$(printf '%s' "$out" | grep '^RESULT.*poison')"

# --------------------------------------------------------------- C2R08 ------
# Read-only contract: the receipt engines and census must not rewrite the index.
cc_new r08
mkdir -p "$CCB/idx"
git init -q --initial-branch=main "$CCB/idx"
printf 'same bytes\n' > "$CCB/idx/artifact.txt"
git -C "$CCB/idx" add -A >/dev/null 2>&1
git -C "$CCB/idx" -c user.email=n@fixture.invalid -c user.name=n commit -qm a >/dev/null 2>&1
cc_age "$CCB/idx/artifact.txt" '7 seconds ago'
idx_sha() { sha256sum "$CCB/idx/.git/index" 2>/dev/null | cut -d' ' -f1 || printf 'ABSENT'; }
b=$(idx_sha); bash "$V" -- "$CCB/idx" >/dev/null 2>&1; a=$(idx_sha)
cc_check "C2R08 verify leaves the index alone" "$([ "$b" = "$a" ] && echo 1 || echo 0)" "before=$b after=$a"
b=$(idx_sha); bash "$W" -- "$CCB/idx" >/dev/null 2>&1; a=$(idx_sha)
cc_check "C2R08 vault leaves the index alone" "$([ "$b" = "$a" ] && echo 1 || echo 0)" "before=$b after=$a"
if [ -f "$C" ]; then
  b=$(idx_sha); bash "$C" --root "$CCB" >/dev/null 2>&1; a=$(idx_sha)
  cc_check "C2R08 census leaves the index alone" "$([ "$b" = "$a" ] && echo 1 || echo 0)" "before=$b after=$a"
fi

# --------------------------------------------------------------- C2R09 ------
cc_new r09
mkdir -p "$CCB/idx2"
git init -q --initial-branch=main "$CCB/idx2"
printf 'b\n' > "$CCB/idx2/artifact.txt"
git -C "$CCB/idx2" add -A >/dev/null 2>&1
git -C "$CCB/idx2" -c user.email=n@fixture.invalid -c user.name=n commit -qm b >/dev/null 2>&1
rm -f "$CCB/idx2/.git/index"
bash "$V" -- "$CCB/idx2" >/dev/null 2>&1
cc_check "C2R09 verify does not create an absent index" \
  "$([ ! -e "$CCB/idx2/.git/index" ] && echo 1 || echo 0)"
rm -f "$CCB/idx2/.git/index"
bash "$W" -- "$CCB/idx2" >/dev/null 2>&1
cc_check "C2R09 vault does not create an absent index" \
  "$([ ! -e "$CCB/idx2/.git/index" ] && echo 1 || echo 0)"

# --------------------------------------------------------------- C2R10 ------
cc_new r10
cc_nested_repo "$CCR/r10/locked/nested"
printf 'outer\n' > "$CCR/r10/readme.txt"
cc_commit r10
chmod 000 "$CCR/r10/locked"
cc_check "C2R10 unreadable subdir refuses" \
  "$(cc_refusal_ok "$V" "$CCR/r10" nested-repo-or-unverifiable && echo 1 || echo 0)" \
  "verify=$(cc_verdict "$V" "$CCR/r10")/$(cc_verify "$V" "$CCR/r10")"
chmod 755 "$CCR/r10/locked"

# --------------------------------------------------------------- C2R11 ------
# Control: a plain tracked+pushed directory must still be removable. An
# over-refusing candidate would be a regression, not a fix.
cc_new r11
mkdir -p "$CCR/r11"
printf 'plain\n' > "$CCR/r11/a.txt"
cc_commit r11
cc_check "C2R11 control: plain pushed dir still SAFE" \
  "$([ "$(cc_verify "$V" "$CCR/r11")" = pushed ] && echo 1 || echo 0)" \
  "verify=$(cc_verify "$V" "$CCR/r11")"

# --------------------------------------------------------------- C2R12 ------
cc_new r12
mkdir -p "$CCB/outside-t"; cc_nested_repo "$CCB/outside-t"
ln -s "$CCB/outside-t" "$CCR/r12-link"
cc_commit r12
cc_check "C2R12 control: symlink target refused" \
  "$([ "$(cc_verify "$V" "$CCR/r12-link")" != pushed ] && echo 1 || echo 0)" \
  "verify=$(cc_verify "$V" "$CCR/r12-link")"

printf 'CLUSTERC\t%s\t%s\t%s\n' "$LABEL" "$CC_PASS" "$CC_FAIL"
[ "$CC_FAIL" = 0 ]
