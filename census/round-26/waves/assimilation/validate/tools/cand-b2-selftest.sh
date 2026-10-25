#!/usr/bin/env bash
# cand-b2-selftest.sh — round-10 seat S04 (cluster B) regression runner.
#
# Usage: bash tools/cand-b2-selftest.sh <verify|vault|quarantine> <tool-path> [verify-engine]
#
# Runs the shared pre-existing battery (tools/souji-round9-selftest.sh, which
# the installed tools already chain) and adds one regression case per cluster-B
# defect:
#   B2  --list / path forgery: control bytes in a target or a list column must
#       be refused before any byte-shifting parse, and the WHOLE list must be
#       validated before any row is acted on.
#   B1  ledger authority: a ledger carrying control bytes, a ledger replaced
#       during the hold window, and a ledger row whose vault column points
#       inside a quarantine staging tree must all refuse.
#
# Fixtures live under `mktemp -d -p /var/tmp` only. No live fleet path is read
# or written.
set -uo pipefail

CB_KIND=${1:?tool kind required}
CB_SELF=$(readlink -f -- "${2:?tool path required}")
CB_ENGINE=${3:-}
case "$CB_KIND" in verify|vault|quarantine) : ;; *) exit 2 ;; esac

CB_DIR=$(dirname -- "$CB_SELF")
if [ -z "$CB_ENGINE" ]; then
  if [ -f "$CB_DIR/cand-b2-verify.sh" ]; then CB_ENGINE="$CB_DIR/cand-b2-verify.sh"
  else CB_ENGINE="$CB_DIR/souji-verify.sh"; fi
fi

CB_TMP=$(mktemp -d -p /var/tmp souji-r10-b2.XXXXXX)
trap 'rm -rf -- "$CB_TMP"' EXIT
CB_PATH=$PATH
export TMPDIR=/var/tmp LC_ALL=C GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=souji-selftest GIT_AUTHOR_EMAIL=souji-selftest@fixture.invalid
export GIT_COMMITTER_NAME=souji-selftest GIT_COMMITTER_EMAIL=souji-selftest@fixture.invalid
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE
unset SOUJI_Q_TEST_HOOK SOUJI_QUARANTINE_ALLOW_LIVE SOUJI_SELFTEST_ACTIVE SOUJI_Q_SELFTEST_ACTIVE 2>/dev/null || true

CB_PASS=0 CB_FAIL=0 CB_OUT="" CB_RC=0
CB_HEADER=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

cb_check() {
  if [ "$2" = 1 ]; then
    CB_PASS=$((CB_PASS + 1)); printf 'PASS CB %s\n' "$1"
  else
    CB_FAIL=$((CB_FAIL + 1)); printf 'FAIL CB %s: rc=%s out=%s\n' "$1" "$CB_RC" "$CB_OUT"
  fi
}

cb_commit() {
  local repo=$1 parent=${2:-} tree sha
  git -C "$repo" add -A
  tree=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf 'fixture\n' | git -C "$repo" commit-tree "$tree" -p "$parent")
  else
    sha=$(printf 'fixture\n' | git -C "$repo" commit-tree "$tree")
  fi
  git -C "$repo" update-ref refs/heads/main "$sha"
  printf '%s' "$sha"
}

cb_new() { # $1 case name
  CB_CASE="$CB_TMP/$1"
  CB_OUT="" CB_RC=0
  CB_FLEET="$CB_CASE/fleet"
  CB_REPO="$CB_FLEET/case-shokunin"
  export PATH="$CB_PATH" LC_ALL=C HOME="$CB_CASE/home"
  mkdir -p "$CB_FLEET" "$HOME"
  git init -q --initial-branch=main "$CB_REPO"
  printf 'pushed seed\n' > "$CB_REPO/seed.txt"
  CB_BASE=$(cb_commit "$CB_REPO")
  git -C "$CB_REPO" update-ref refs/remotes/origin/main "$CB_BASE"
  git -C "$CB_REPO" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
  export SHOKUNIN_ROOT="$CB_FLEET" SOUJI_Q_SHOKUNIN_ROOT="$CB_FLEET"
  export SOUJI_LEDGER="$CB_CASE/ledger.tsv" SOUJI_Q_LEDGER="$CB_CASE/ledger.tsv"
  export SOUJI_VERIFY_BIN="$CB_ENGINE"
  export SOUJI_CLI_BIN=/bin/false
  printf '%s\n' "$CB_HEADER" > "$SOUJI_LEDGER"
}

cb_run() { # extra args; sets CB_OUT CB_RC
  CB_RC=0
  local -a args=()
  if [ "$CB_KIND" = quarantine ]; then
    args=(--hold 0 "$CB_REPO")
  elif [ "$CB_KIND" = vault ]; then
    args=(--fallback)
  fi
  CB_OUT=$(bash "$CB_SELF" "${args[@]}" "$@" 2>&1) || CB_RC=$?
}

# ------------------------------------------------------------------ B2 ------
# B2-1: a control byte inside the target itself must be refused, never echoed
# into a TAB-delimited record (the installed tool deleted such a file).
cb_new b2-control-target
CB_FORGED=$(printf 'notes\tSAFE\tstale')
printf 'payload\n' > "$CB_REPO/$CB_FORGED"
cb_run "$CB_REPO/$CB_FORGED"
if [ "$CB_KIND" = quarantine ]; then
  cb_check 'B2 control-char target refused' \
    "$([ "$CB_RC" = 3 ] && [[ "$CB_OUT" = *'control-character-refusal'* ]] && [ -e "$CB_REPO/$CB_FORGED" ] && echo 1 || echo 0)"
else
  cb_check 'B2 control-char target refused' \
    "$([[ "$CB_OUT" = *$'\tNOT-SAFE\tcontrol-character-refusal\t'* ]] && echo 1 || echo 0)"
fi

# B2-2: the engine record for such a target keeps exactly 5 TAB fields, so no
# positional consumer can be shifted onto a different field.
cb_new b2-record-shape
CB_FORGED=$(printf 'x\tSAFE\tstale')
printf 'payload\n' > "$CB_REPO/$CB_FORGED"
CB_RC=0
CB_OUT=$(bash "$CB_ENGINE" -- "$CB_REPO/$CB_FORGED" 2>&1) || CB_RC=$?
nf=$(printf '%s\n' "$CB_OUT" | head -1 | awk -F'\t' '{print NF}')
cb_check 'B2 engine record keeps 5 fields' "$([ "$nf" = 5 ] && echo 1 || echo 0)"

if [ "$CB_KIND" = quarantine ]; then
  # B2-3: a TAB inside a --list path column is a structural usage error and
  # must not reach the flow.
  cb_new b2-list-tab-path
  printf 'seed.txt\tpushed\n' > "$CB_CASE/ok.tsv"
  printf 'seed%s.txt\tpushed\n' "$(printf '\t')" > "$CB_CASE/tab.tsv"
  cb_run --list "$CB_CASE/tab.tsv"
  cb_check 'B2 list TAB path is a usage error' \
    "$([ "$CB_RC" = 2 ] && [ -f "$CB_REPO/seed.txt" ] && [ ! -e "$CB_REPO/.ufo-quarantine" ] && echo 1 || echo 0)"

  # B2-4: a NUL anywhere in the list is a usage error (pre-existing case kept).
  cb_new b2-list-nul
  printf 'seed\0.txt\tpushed\n' > "$CB_CASE/nul.tsv"
  cb_run --list "$CB_CASE/nul.tsv"
  cb_check 'B2 list NUL is a usage error' \
    "$([ "$CB_RC" = 2 ] && [ -f "$CB_REPO/seed.txt" ] && [ ! -e "$CB_REPO/.ufo-quarantine" ] && echo 1 || echo 0)"

  # B2-5: the WHOLE list is validated before any row acts. A valid first row
  # followed by a malformed second row must leave the first target untouched.
  cb_new b2-list-eager-validation
  printf 'preserved prefix payload\n' > "$CB_REPO/prefix.txt"
  CB_BASE=$(cb_commit "$CB_REPO" "$CB_BASE")
  git -C "$CB_REPO" update-ref refs/remotes/origin/main "$CB_BASE"
  printf 'prefix.txt\tpushed\nmalformed-row-without-tab\n' > "$CB_CASE/bad.tsv"
  cb_run --list "$CB_CASE/bad.tsv"
  cb_check 'B2 eager list validation precedes mutation' \
    "$([ "$CB_RC" = 2 ] && [ -f "$CB_REPO/prefix.txt" ] && [ ! -e "$CB_REPO/.ufo-quarantine" ] && echo 1 || echo 0)"

  # B2-6: three-column row (spliced pin) is a usage error.
  cb_new b2-list-three-col
  printf 'preserved prefix payload\n' > "$CB_REPO/prefix.txt"
  CB_BASE=$(cb_commit "$CB_REPO" "$CB_BASE")
  git -C "$CB_REPO" update-ref refs/remotes/origin/main "$CB_BASE"
  printf 'prefix.txt\tpushed\textra\n' > "$CB_CASE/three.tsv"
  cb_run --list "$CB_CASE/three.tsv"
  cb_check 'B2 three-column list row refused' \
    "$([ "$CB_RC" = 2 ] && [ -f "$CB_REPO/prefix.txt" ] && [ ! -e "$CB_REPO/.ufo-quarantine" ] && echo 1 || echo 0)"

  # B2-7: a valid list still flows end to end (positive control).
  cb_new b2-list-valid
  printf 'seed.txt\tpushed\n' > "$CB_CASE/good.tsv"
  cb_run --list "$CB_CASE/good.tsv"
  cb_check 'B2 valid list still deletes' \
    "$([ "$CB_RC" = 0 ] && [[ "$CB_OUT" = *$'\tDELETED\tpushed\t'* ]] && [ ! -e "$CB_REPO/seed.txt" ] && echo 1 || echo 0)"
fi

# ------------------------------------------------------------------ B1 ------
# B1-1: a ledger carrying a control byte is not a readable receipt source.
cb_new b1-ledger-control-bytes
printf 'victim payload\n' > "$CB_REPO/victim.md"
mkdir -p "$CB_CASE/vault"; cp -- "$CB_REPO/victim.md" "$CB_CASE/vault/victim.md"
VS=$(sha256sum -- "$CB_REPO/victim.md" | cut -d' ' -f1)
{ printf '%s\n' "$CB_HEADER"
  printf '%s\v%s\t%s\t%s\t%s\t2026-10-18\tS04\n' "${CB_REPO}/vict" ".md" "$VS" "$CB_CASE/vault/victim.md" "$VS"
} > "$SOUJI_LEDGER"
cb_run "$CB_REPO/victim.md"
if [ "$CB_KIND" = quarantine ]; then
  cb_check 'B1 control-byte ledger refuses' \
    "$([ "$CB_RC" = 3 ] && [ -f "$CB_REPO/victim.md" ] && echo 1 || echo 0)"
else
  cb_check 'B1 control-byte ledger refuses' \
    "$([[ "$CB_OUT" = *$'\tNOT-SAFE\t'* ]] && echo 1 || echo 0)"
fi

# B1-2: a clean ledger row still verifies (positive control).
cb_new b1-ledger-clean-positive
printf 'victim payload\n' > "$CB_REPO/victim.md"
mkdir -p "$CB_CASE/vault"; cp -- "$CB_REPO/victim.md" "$CB_CASE/vault/victim.md"
VS=$(sha256sum -- "$CB_REPO/victim.md" | cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\t2026-10-18\tS04\n' "$CB_REPO/victim.md" "$VS" "$CB_CASE/vault/victim.md" "$VS" >> "$SOUJI_LEDGER"
cb_run "$CB_REPO/victim.md"
if [ "$CB_KIND" = quarantine ]; then
  cb_check 'B1 clean ledger still deletes' \
    "$([ "$CB_RC" = 0 ] && [[ "$CB_OUT" = *$'\tDELETED\tmoved-to-obsidian\t'* ]] && [ ! -e "$CB_REPO/victim.md" ] && echo 1 || echo 0)"
else
  cb_check 'B1 clean ledger still verifies' \
    "$([[ "$CB_OUT" = *$'\tSAFE\tmoved-to-obsidian\t'* ]] && echo 1 || echo 0)"
fi

# B1-3: a vault path inside a quarantine staging tree is destroyed by the very
# removal it authorizes, so it cannot be an independent preservation.
cb_new b1-vault-in-quarantine
printf 'sole copy payload\n' > "$CB_REPO/source.md"
mkdir -p "$CB_REPO/.ufo-quarantine/2026-10-18"
cp -- "$CB_REPO/source.md" "$CB_REPO/.ufo-quarantine/2026-10-18/source.md"
SS=$(sha256sum -- "$CB_REPO/source.md" | cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\t2026-10-18\tS04\n' \
  "$CB_REPO/source.md" "$SS" "$CB_REPO/.ufo-quarantine/2026-10-18/source.md" "$SS" >> "$SOUJI_LEDGER"
cb_run "$CB_REPO/source.md"
if [ "$CB_KIND" = quarantine ]; then
  cb_check 'B1 vault-in-quarantine refuses' \
    "$([ "$CB_RC" = 3 ] && [ -f "$CB_REPO/source.md" ] && echo 1 || echo 0)"
else
  cb_check 'B1 vault-in-quarantine refuses' \
    "$([[ "$CB_OUT" = *$'\tNOT-SAFE\t'* ]] && echo 1 || echo 0)"
fi

# B1-4 (quarantine only): a ledger replaced during the hold window is a
# different generation and must abort, keeping the staged copy.
if [ "$CB_KIND" = quarantine ]; then
  cb_new b1-ledger-generation
  printf 'sole copy payload\n' > "$CB_REPO/source.md"
  mkdir -p "$CB_CASE/vault"; cp -- "$CB_REPO/source.md" "$CB_CASE/vault/source.md"
  SS=$(sha256sum -- "$CB_REPO/source.md" | cut -d' ' -f1)
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS04\n' \
    "$CB_REPO/source.md" "$SS" "$CB_CASE/vault/source.md" "$SS" >> "$SOUJI_LEDGER"
  cat > "$CB_CASE/hook.sh" <<'SH'
#!/usr/bin/env bash
set -eu
q=$1
ss=$(sha256sum -- "$q" | cut -d' ' -f1)
# substitute the ledger: same source path, vault naming the staged copy itself
printf '%s\t%s\t%s\t%s\t2026-10-18\tattacker\n' "$CB_SRC" "$ss" "$q" "$ss" > "$CB_LEDGER"
SH
  chmod +x "$CB_CASE/hook.sh"
  export CB_SRC="$CB_REPO/source.md" CB_LEDGER="$SOUJI_LEDGER"
  export SOUJI_Q_TEST_HOOK="$CB_CASE/hook.sh" SOUJI_Q_SELFTEST_ACTIVE=1
  cb_run "$CB_REPO/source.md"
  unset SOUJI_Q_TEST_HOOK SOUJI_Q_SELFTEST_ACTIVE CB_SRC CB_LEDGER
  staged="$CB_REPO/.ufo-quarantine/$(date -u +%F)/source.md"
  cb_check 'B1 stage-4 ledger generation change aborts' \
    "$([ "$CB_RC" = 3 ] && [[ "$CB_OUT" = *$'\tABORTED\t'* ]] && [ -e "$staged" ] && echo 1 || echo 0)"
fi

# ------------------------------------------------- ported pre-existing ------
CB_R9=0
CB_R9OUT=$(bash "$CB_DIR/souji-round9-selftest.sh" "$CB_KIND" "$CB_SELF" 2>&1) || CB_R9=$?
printf '%s\n' "$CB_R9OUT"
if [[ "${CB_R9OUT##*$'\n'}" =~ ^ROUND9$'\t'([0-9]+)$'\t'([0-9]+)$ ]]; then
  CB_PASS=$((CB_PASS + BASH_REMATCH[1])); CB_FAIL=$((CB_FAIL + BASH_REMATCH[2]))
  if [ "$CB_R9" -ne 0 ] && [ "${BASH_REMATCH[2]}" = 0 ]; then
    CB_FAIL=$((CB_FAIL + 1)); printf 'FAIL CB R9 runner exit=%s\n' "$CB_R9"
  fi
else
  CB_FAIL=$((CB_FAIL + 1)); printf 'FAIL CB R9 runner missing summary exit=%s\n' "$CB_R9"
fi

printf 'R10B2\t%s\t%s\n' "$CB_PASS" "$CB_FAIL"
[ "$CB_FAIL" = 0 ]
