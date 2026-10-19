#!/usr/bin/env bash
# cand-b1-regress.sh — round-10 S03 cluster-B regression battery.
#
# Usage: bash tools/cand-b1-regress.sh <verify|vault|quarantine> <tool-path>
#
# Fresh fixtures only, all under `mktemp -d -p /var/tmp`. Every case is a
# fresh-closure regression for a defect S03 reproduced on the installed
# (S17-patched) tools in round 10:
#
#   B1-a  a ledger row that is not a complete, independent preservation
#         record must not authorize a removal (self-copy, vault inside the
#         source, relative vault path, empty digest).
#   B1-b  a ledger rewritten between row capture and the verdict (including
#         across the quarantine hold window) must not authorize a deletion.
#   B2    a target or list row whose name carries a control character, or a
#         list row that is not exactly two columns from the closed receipt
#         vocabulary, is a fail-closed refusal — never a receipt.
#
# Prints `B1REG<TAB>pass<TAB>fail` as its last line and exits non-zero when
# any check fails.
set -euo pipefail
B1_KIND=${1:?tool kind required}
B1_SELF=$(readlink -f -- "${2:?tool path required}")
case "$B1_KIND" in verify|vault|quarantine) : ;; *) exit 2 ;; esac

B1_TMP=$(mktemp -d -p /var/tmp souji-r10-b1reg.XXXXXX)
trap 'rm -rf -- "$B1_TMP"' EXIT
B1_PASS=0 B1_FAIL=0 B1_OUT="" B1_RC=0
export TMPDIR=/var/tmp LC_ALL=C GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=souji-b1 GIT_AUTHOR_EMAIL=souji-b1@fixture.invalid
export GIT_COMMITTER_NAME=souji-b1 GIT_COMMITTER_EMAIL=souji-b1@fixture.invalid
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE SOUJI_Q_TEST_HOOK

B1_HEADER=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

b1_ok() { B1_PASS=$((B1_PASS + 1)); printf 'PASS B1 %s\n' "$1"; }
b1_bad() { B1_FAIL=$((B1_FAIL + 1)); printf 'FAIL B1 %s: rc=%s out=%s\n' "$1" "$B1_RC" "$B1_OUT"; }
b1_check() { if [ "$2" = 1 ]; then b1_ok "$1"; else b1_bad "$1"; fi; }

b1_sha() { sha256sum -- "$1" | cut -d' ' -f1; }
b1_dd() { ( cd -- "$1" && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ); }

b1_commit() { # $1 repo, $2 parent(""), $3 msg -> sha
  local repo=$1 parent=$2 msg=$3 tr sha
  git -C "$repo" add -A >/dev/null 2>&1
  tr=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr" -p "$parent")
  else
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr")
  fi
  printf '%s' "$sha"
}

b1_new() { # $1 case name; builds a pushed fixture repo + ledger context
  B1_CASE="$B1_TMP/$1"
  B1_FLEET="$B1_CASE/fleet"
  B1_REPO="$B1_FLEET/case-shokunin"
  B1_LEDGER="$B1_CASE/ledger.tsv"
  B1_OUT="" B1_RC=0
  mkdir -p "$B1_FLEET" "$B1_CASE/home"
  git init -q --initial-branch=main "$B1_REPO"
  printf 'seed\n' > "$B1_REPO/seed.txt"
  local base
  base=$(b1_commit "$B1_REPO" "" "seed")
  git -C "$B1_REPO" update-ref refs/heads/main "$base"
  git -C "$B1_REPO" update-ref refs/remotes/origin/main "$base"
  git -C "$B1_REPO" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
  printf '%s\n' "$B1_HEADER" > "$B1_LEDGER"
  export HOME="$B1_CASE/home"
  export SHOKUNIN_ROOT="$B1_FLEET" SOUJI_Q_SHOKUNIN_ROOT="$B1_FLEET"
  export SOUJI_LEDGER="$B1_LEDGER" SOUJI_Q_LEDGER="$B1_LEDGER"
  export SOUJI_SELFTEST_ACTIVE=1 SOUJI_Q_SELFTEST_ACTIVE=1 SOUJI_CLI_BIN=/bin/false
  local sib
  sib=$(dirname -- "$B1_SELF")
  if [ "$B1_KIND" = quarantine ]; then
    if [ -f "$sib/cand-b1-verify.sh" ]; then SOUJI_VERIFY_BIN="$sib/cand-b1-verify.sh"
    else SOUJI_VERIFY_BIN="$sib/souji-verify.sh"; fi
    export SOUJI_VERIFY_BIN
  fi
}

b1_run() { # rest = tool args; sets B1_OUT/B1_RC
  local -a args=()
  if [ "$B1_KIND" = quarantine ]; then args=(--hold 0 "$B1_REPO")
  elif [ "$B1_KIND" = vault ]; then args=(--fallback); fi
  B1_RC=0
  B1_OUT=$(bash "$B1_SELF" "${args[@]}" "$@" 2>&1) || B1_RC=$?
}

b1_refuses() { # $1 id
  if [ "$B1_KIND" = quarantine ]; then
    if [ "$B1_RC" = 3 ] && [[ "$B1_OUT" = *$'\tNOT-AUTHORIZED\t'* || "$B1_OUT" = *$'\tABORTED\t'* ]]; then
      b1_ok "$1"
    else b1_bad "$1"; fi
  else
    if [ "$B1_RC" = 0 ] && [[ "$B1_OUT" = *NOT-SAFE* || "$B1_OUT" = *NOT-VERIFIED* ]]; then
      b1_ok "$1"
    else b1_bad "$1"; fi
  fi
}

b1_bytes_kept() { # $1 id, $2 source path
  local found=0
  [ -e "$2" ] && found=1
  if [ "$found" = 0 ] && [ -d "$B1_REPO/.ufo-quarantine" ]; then
    local qp="$B1_REPO/.ufo-quarantine/$(date -u +%F)/${2#"$B1_REPO"/}"
    [ -e "$qp" ] && found=1
  fi
  b1_check "$1" "$([ "$found" = 1 ] && echo 1 || echo 0)"
}

# ------------------------------------------------------------ B1-a: rows ----

# R1 file row pointing the vault at the artifact itself
b1_new self-copy-row
src="$B1_REPO/solo.md"; printf 'sole copy\n' > "$src"
printf '%s\t%s\t%s\t%s\t2026-10-18\tself\n' "$src" "$(b1_sha "$src")" "$src" "$(b1_sha "$src")" >> "$B1_LEDGER"
b1_run "$src"
b1_refuses "R1 self-copy ledger row refuses"
b1_bytes_kept "R1 bytes retained" "$src"

# R2 relative vault path (cwd-dependent receipt)
b1_new relative-vault
src="$B1_REPO/rel.md"; printf 'payload\n' > "$src"
mkdir -p "$B1_CASE/vault"; cp -- "$src" "$B1_CASE/vault/rel.md"
printf '%s\t%s\t%s\t%s\t2026-10-18\trel\n' "$src" "$(b1_sha "$src")" "vault/rel.md" "$(b1_sha "$src")" >> "$B1_LEDGER"
b1_run "$src"
b1_refuses "R2 relative vault path refuses"
b1_bytes_kept "R2 bytes retained" "$src"

# R3 dir row whose vault lives inside the artifact being removed
b1_new vault-inside-source
dir="$B1_REPO/bundle"; mkdir -p "$dir/sub"; printf 'payload\n' > "$dir/f.txt"
printf '%s\t%s\t%s\t%s\t2026-10-18\tinside\n' "$dir" "$(b1_dd "$dir")" "$dir/sub" "$(b1_dd "$dir/sub")" >> "$B1_LEDGER"
b1_run "$dir"
b1_refuses "R3 vault inside source refuses"
b1_bytes_kept "R3 bytes retained" "$dir"

# R4 dir row with an empty vault digest (incomplete preservation record)
b1_new empty-vault-digest
dir="$B1_REPO/bundle2"; mkdir -p "$dir"; printf 'payload\n' > "$dir/f.txt"
vd="$B1_CASE/vault2"; mkdir -p "$vd"; printf 'payload\n' > "$vd/f.txt"
printf '%s\t%s\t%s\t\t2026-10-18\tincomplete\n' "$dir" "$(b1_dd "$dir")" "$vd" >> "$B1_LEDGER"
b1_run "$dir"
b1_refuses "R4 empty vault digest refuses"
b1_bytes_kept "R4 bytes retained" "$dir"

# R5 honest file row still earns the receipt (compat)
b1_new honest-file
src="$B1_REPO/ok.md"; printf 'payload\n' > "$src"
vf="$B1_CASE/vault-ok.md"; cp -- "$src" "$vf"
printf '%s\t%s\t%s\t%s\t2026-10-18\tok\n' "$src" "$(b1_sha "$src")" "$vf" "$(b1_sha "$vf")" >> "$B1_LEDGER"
b1_run "$src"
if [ "$B1_KIND" = quarantine ]; then
  b1_check "R5 honest file flow deletes" "$([ "$B1_RC" = 0 ] && [ ! -e "$src" ] && [ -f "$vf" ] && echo 1 || echo 0)"
else
  b1_check "R5 honest file row verifies" "$([[ "$B1_OUT" = *moved-to-obsidian* ]] && echo 1 || echo 0)"
fi

# R6 honest dir row still earns the receipt (compat)
b1_new honest-dir
dir="$B1_REPO/okdir"; mkdir -p "$dir"; printf 'payload\n' > "$dir/f.txt"
vd="$B1_CASE/vault-okdir"; mkdir -p "$vd"; printf 'payload\n' > "$vd/f.txt"
printf '%s\t%s\t%s\t%s\t2026-10-18\tokdir\n' "$dir" "$(b1_dd "$dir")" "$vd" "$(b1_dd "$vd")" >> "$B1_LEDGER"
b1_run "$dir"
if [ "$B1_KIND" = quarantine ]; then
  b1_check "R6 honest dir flow deletes" "$([ "$B1_RC" = 0 ] && [ ! -e "$dir" ] && [ -d "$vd" ] && echo 1 || echo 0)"
else
  b1_check "R6 honest dir row verifies" "$([[ "$B1_OUT" = *moved-to-obsidian* ]] && echo 1 || echo 0)"
fi

# ------------------------------------------------------- B1-b: revocation ---

# R7 the ledger is replaced while the check is running (sha256sum shim)
b1_new ledger-rewrite-in-check
src="$B1_REPO/live.md"; printf 'payload\n' > "$src"
vf="$B1_CASE/vault-live.md"; cp -- "$src" "$vf"
printf '%s\t%s\t%s\t%s\t2026-10-18\tlive\n' "$src" "$(b1_sha "$src")" "$vf" "$(b1_sha "$vf")" >> "$B1_LEDGER"
mkdir -p "$B1_CASE/bin"
cat > "$B1_CASE/bin/sha256sum" <<'SH'
#!/usr/bin/env bash
set -u
if [ "${!#}" = "$B1_GATE_TARGET" ]; then
  n=0; [ -f "$B1_COUNT" ] && IFS= read -r n < "$B1_COUNT"
  n=$((n + 1)); printf '%s\n' "$n" > "$B1_COUNT"
  if [ "$n" = "${B1_GATE_HIT:-1}" ]; then printf '%s\n' "$B1_HEADER" > "$B1_LEDGER"; fi
fi
exec "$B1_REAL_SHA" "$@"
SH
  chmod +x "$B1_CASE/bin/sha256sum"
export PATH="$B1_CASE/bin:$PATH"
export B1_GATE_TARGET="$src" B1_COUNT="$B1_CASE/count" B1_HEADER="$B1_HEADER"
export B1_LEDGER B1_REAL_SHA="$(command -v sha256sum || true)"
B1_REAL_SHA=/usr/bin/sha256sum
export B1_REAL_SHA
b1_run "$src"
b1_refuses "R7 ledger replaced mid-check refuses"
b1_check "R7 rewrite actually happened" "$([ -f "$B1_COUNT" ] && [ "$(cat "$B1_LEDGER")" = "$B1_HEADER" ] && echo 1 || echo 0)"
export PATH="${PATH#"$B1_CASE/bin:"}"
unset B1_GATE_TARGET B1_COUNT B1_REAL_SHA
B1_HEADER=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
export B1_HEADER

if [ "$B1_KIND" = quarantine ]; then
  # R8 the ledger is repointed at the staged copy during the hold window
  b1_new ledger-repoint-during-hold
  src="$B1_REPO/solo.md"; printf 'sole copy\n' > "$src"
  vf="$B1_CASE/vault-solo.md"; cp -- "$src" "$vf"
  printf '%s\t%s\t%s\t%s\t2026-10-18\trow\n' "$src" "$(b1_sha "$src")" "$vf" "$(b1_sha "$vf")" >> "$B1_LEDGER"
  cat > "$B1_CASE/hook.sh" <<SH
#!/usr/bin/env bash
qpath=\$1
d=\$(sha256sum -- "\$qpath" | cut -d' ' -f1)
printf '%s\n' "$B1_HEADER" > "$B1_LEDGER"
printf '%s\t%s\t%s\t%s\t2026-10-18\tforged\n' "$src" "\$d" "\$qpath" "\$d" >> "$B1_LEDGER"
SH
  chmod +x "$B1_CASE/hook.sh"
  export SOUJI_Q_TEST_HOOK="$B1_CASE/hook.sh"
  b1_run "$src"
  b1_refuses "R8 repointed ledger during hold aborts"
  b1_bytes_kept "R8 staged bytes retained" "$src"
  unset SOUJI_Q_TEST_HOOK

  # R9 the ledger is deleted during the hold window
  b1_new ledger-deleted-during-hold
  src="$B1_REPO/solo.md"; printf 'sole copy\n' > "$src"
  vf="$B1_CASE/vault-solo.md"; cp -- "$src" "$vf"
  printf '%s\t%s\t%s\t%s\t2026-10-18\trow\n' "$src" "$(b1_sha "$src")" "$vf" "$(b1_sha "$vf")" >> "$B1_LEDGER"
  printf '#!/usr/bin/env bash\nrm -f -- %q\n' "$B1_LEDGER" > "$B1_CASE/hook.sh"
  chmod +x "$B1_CASE/hook.sh"
  export SOUJI_Q_TEST_HOOK="$B1_CASE/hook.sh"
  b1_run "$src"
  b1_refuses "R9 deleted ledger during hold aborts"
  b1_bytes_kept "R9 staged bytes retained" "$src"
  unset SOUJI_Q_TEST_HOOK

  # ------------------------------------------------ B2: control chars ------

  # R10 positional target whose name carries a TAB (engine record field shift)
  b1_new tab-in-path-positional
  weird="$B1_REPO/fresh"$'\t'"SAFE"$'\t'"stale"$'\t'"no-receipt.txt"
  printf 'brand new, no receipt\n' > "$weird"
  b1_run "$weird"
  b1_refuses "R10 TAB-in-path target refuses"
  b1_bytes_kept "R10 TAB target retained" "$weird"

  # R11 positional target carrying a vertical tab
  b1_new vt-in-path-positional
  weird2="$B1_REPO/vt"$'\v'"name.txt"
  printf 'brand new, no receipt\n' > "$weird2"
  b1_run "$weird2"
  b1_refuses "R11 VT-in-path target refuses"
  b1_bytes_kept "R11 VT target retained" "$weird2"

  # R12 list rows that are not exactly two clean columns
  for mode in vt-receipt empty-path outside-vocab del-path; do
    b1_new "list-$mode"
    scr="$B1_REPO/.scratch"; mkdir -p "$scr"
    tgt="$scr/old.out"; printf 'stale\n' > "$tgt"
    touch -d '5 days ago' "$tgt" "$scr"
    case "$mode" in
      vt-receipt) printf '%s\tstale\x0b\n' "$tgt" > "$B1_CASE/list.tsv" ;;
      empty-path) printf '\tstale\n' > "$B1_CASE/list.tsv" ;;
      outside-vocab) printf '%s\tdelete-me\n' "$tgt" > "$B1_CASE/list.tsv" ;;
      del-path) printf '%s\x7f\tstale\n' "$tgt" > "$B1_CASE/list.tsv" ;;
    esac
    b1_run --list "$B1_CASE/list.tsv"
    b1_check "R12 $mode list row is a usage error" "$([ "$B1_RC" = 2 ] && echo 1 || echo 0)"
    b1_check "R12 $mode makes no moves" \
      "$([ -f "$tgt" ] && [ ! -e "$B1_REPO/.ufo-quarantine" ] && echo 1 || echo 0)"
  done

  # R13 honest CRLF list row still authorizes (compat)
  b1_new list-crlf-honest
  scr="$B1_REPO/.scratch"; mkdir -p "$scr"
  tgt="$scr/old-crlf.out"; printf 'stale\n' > "$tgt"
  touch -d '5 days ago' "$tgt" "$scr"
  printf 'path\treceipt\r\n%s\tstale\r\n' "$tgt" > "$B1_CASE/list.tsv"
  b1_run --list "$B1_CASE/list.tsv"
  b1_check "R13 CRLF honest list deletes" "$([ "$B1_RC" = 0 ] && [ ! -e "$tgt" ] && echo 1 || echo 0)"

  # R14 list row with no trailing newline still authorizes (compat)
  b1_new list-noeol-honest
  scr="$B1_REPO/.scratch"; mkdir -p "$scr"
  tgt="$scr/old-noeol.out"; printf 'stale\n' > "$tgt"
  touch -d '5 days ago' "$tgt" "$scr"
  printf '%s\tstale' "$tgt" > "$B1_CASE/list.tsv"
  b1_run --list "$B1_CASE/list.tsv"
  b1_check "R14 no-EOL honest list deletes" "$([ "$B1_RC" = 0 ] && [ ! -e "$tgt" ] && echo 1 || echo 0)"

  # R15 honest stale flow still deletes (compat)
  b1_new honest-stale
  scr="$B1_REPO/.scratch"; mkdir -p "$scr"
  tgt="$scr/old-report.out"; printf 'stale\n' > "$tgt"
  touch -d '5 days ago' "$tgt" "$scr"
  b1_run "$tgt"
  b1_check "R15 honest stale flow deletes" "$([ "$B1_RC" = 0 ] && [ ! -e "$tgt" ] && echo 1 || echo 0)"
fi

printf 'B1REG\t%s\t%s\n' "$B1_PASS" "$B1_FAIL"
[ "$B1_FAIL" = 0 ]
