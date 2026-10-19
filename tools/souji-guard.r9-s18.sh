#!/usr/bin/env bash
export LC_ALL=C GIT_OPTIONAL_LOCKS=0 GIT_LITERAL_PATHSPECS=1
export TMPDIR="${TMPDIR:-/var/tmp}"

s18_path_ok() {
  local p=$1 part cur=""
  [[ "$p" != *[[:cntrl:]]* ]] || return 1
  is_secret_shaped "$p" && return 1
  case "/${p#/}/" in
    */.git/*|*/.ufo/state/*|*/.ufo/watchdog.log/*) return 1 ;;
  esac
  [[ "$p" = /* ]] || p="$PWD/$p"
  local -a parts=()
  IFS=/ read -r -a parts <<< "$p"
  for part in "${parts[@]}"; do
    [ -n "$part" ] || continue
    cur="$cur/$part"
    [ ! -L "$cur" ] || return 1
  done
  return 0
}

s18_scope_ok() {
  local d=$1 root=${2:-$1} p
  [ -r "$d" ] && [ -x "$d" ] || return 1
  for p in "$d"/* "$d"/.[!.]* "$d"/..?*; do
    [ -e "$p" ] || [ -L "$p" ] || continue
    [ "$p" != "$root/.git" ] || continue
    s18_path_ok "$p" || return 1
    if [ -d "$p" ]; then
      s18_scope_ok "$p" "$root" || return 1
    elif [ ! -f "$p" ]; then
      return 1
    fi
  done
}

is_hex64() { [[ "$1" =~ ^[0-9a-f]{64}$ ]]; }

file_sha() {
  s18_path_ok "$1" && [ -f "$1" ] || return 1
  sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1
}

dir_digest() {
  local d=$1
  s18_path_ok "$d" && [ -d "$d" ] && s18_scope_ok "$d" || return 2
  ( set -o pipefail
    cd -- "$d" && find . -path './.git' -prune -o -type f -print0 \
      | LC_ALL=C sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1
  ) 2>/dev/null
}

s18_row_parse() {
  local rest=$1
  [[ "$rest" = *$'\t'* ]] || return 1
  S18_SP=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  [[ "$rest" = *$'\t'* ]] || return 1
  S18_SS=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  [[ "$rest" = *$'\t'* ]] || return 1
  S18_VP=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  S18_VS=${rest%%$'\t'*}
}

s18_row_ok() {
  local target=$1 isdir=$2 real_vault
  [[ "$S18_SP" = /* && "$S18_VP" = /* ]] || return 1
  is_hex64 "$S18_SS" && is_hex64 "$S18_VS" || return 1
  s18_path_ok "$S18_SP" && s18_path_ok "$S18_VP" || return 1
  real_vault=$(canon_path "$S18_VP")
  [ "$target" != "$real_vault" ] || return 1
  if [ "$isdir" = 1 ]; then
    case "$real_vault/" in "$target/"*) return 1 ;; esac
    case "$target/" in "$real_vault/"*) return 1 ;; esac
  fi
  return 0
}

load_ledger() {
  local row first=1
  LEDGER_ROWS=()
  s18_path_ok "$LEDGER" && [ -f "$LEDGER" ] || return 0
  while IFS= read -r row || [ -n "$row" ]; do
    if [ "$first" = 1 ]; then
      first=0
      case "$row" in source_path$'\t'*) continue ;; esac
    fi
    [ -z "$row" ] || LEDGER_ROWS+=("$row")
  done < "$LEDGER"
}

ledger_lines() {
  local row
  s18_path_ok "$LEDGER" && [ -f "$LEDGER" ] || return 0
  while IFS= read -r row || [ -n "$row" ]; do
    case "$row" in source_path$'\t'*|'#'*|'') continue ;; esac
    printf '%s\n' "$row"
  done < "$LEDGER"
}

try_obsidian() {
  local target=$1 isdir=$2 row source_sha vault_sha
  while IFS= read -r row; do
    s18_row_parse "$row" || continue
    [ "$S18_SP" = "$target" ] || continue
    if ! s18_row_ok "$target" "$isdir"; then
      NOTES+=("obsidian=invalid-or-nonindependent-row")
      continue
    fi
    if [ "$isdir" = 1 ]; then
      source_sha=$(dir_digest "$target") && vault_sha=$(dir_digest "$S18_VP") || continue
    else
      source_sha=$(file_sha "$target") && vault_sha=$(file_sha "$S18_VP") || continue
    fi
    [ "$source_sha" = "$S18_SS" ] && [ "$vault_sha" = "$S18_VS" ] || continue
    R_VERDICT=SAFE; R_RECEIPT=moved-to-obsidian
    R_EVIDENCE="ledger=source+vault-digest ledger-row vault=$S18_VP source-sha256=${S18_SS:0:12}"
    return 0
  done < <(ledger_lines)
  NOTES+=("obsidian=no-matching-ledger-row")
  return 1
}

try_ledger() {
  local target=$1 isdir=$2 raw=${3:-} row matched=0 rejected=0 reason=row-incomplete
  local -a rows=("${LEDGER_ROWS[@]}") LEDGER_ROWS=()
  for row in "${rows[@]}"; do
    s18_row_parse "$row" || continue
    [ "$S18_SP" = "$target" ] || [ "$S18_SP" = "$raw" ] || continue
    matched=1
    if s18_row_ok "$target" "$isdir"; then
      LEDGER_ROWS+=("$row")
    else
      rejected=1
      if [ "$S18_VP" = "$target" ]; then reason=source-equals-vault; fi
    fi
  done
  if [ "${#LEDGER_ROWS[@]}" -gt 0 ]; then
    s18_try_ledger "$target" "$isdir" "$raw"
    return $?
  fi
  if [ "$matched" = 1 ] && [ "$rejected" = 1 ]; then
    NOTES+=("$reason row-incomplete nonindependent-or-invalid-ledger-row")
    finish_mismatch "$reason"
    return 0
  fi
  return 1
}

try_pushed() {
  local target=$1 repo=$2 intro ref status touching
  [ -n "$repo" ] || { NOTES+=("pushed=no-repo"); return 1; }
  if ! status=$(git -C "$repo" --no-optional-locks status --porcelain --untracked-files=all --ignored=matching -- "$target" 2>/dev/null); then
    NOTES+=("pushed=status-unverifiable"); return 1
  fi
  if [ -n "$status" ]; then
    NOTES+=("pushed=dirty-or-untracked-content"); return 1
  fi
  if ! intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$target" 2>/dev/null) || [ -z "$intro" ]; then
    NOTES+=("pushed=no-introducing-commit"); return 1
  fi
  if ! ref=$(resolve_default_ref "$repo"); then
    FAIL_REASON=pushed-unverifiable
    NOTES+=("pushed=unverifiable(no-default-ref) intro=${intro:0:12}"); return 1
  fi
  if ! touching=$(git -C "$repo" log --format=%H HEAD --branches --not --remotes -- "$target" 2>/dev/null); then
    NOTES+=("pushed=history-unverifiable"); return 1
  fi
  if [ -n "$touching" ]; then
    NOTES+=("pushed=unpushed-commits-touching intro=${intro:0:12}"); return 1
  fi
  if ! git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
    NOTES+=("pushed=not-ancestor intro=${intro:0:12} ref=$ref"); return 1
  fi
  if ! git -C "$repo" diff --quiet --no-ext-diff --no-textconv "$ref" -- "$target" 2>/dev/null; then
    NOTES+=("pushed=default-snapshot-mismatch"); return 1
  fi
  R_VERDICT=SAFE; R_RECEIPT=pushed; R_REASON=pushed
  R_EVIDENCE="intro=${intro:0:12} ref=$ref ancestor=yes snapshot=equal clean=yes"
  return 0
}

count_live_refs() {
  local target=$1 repo=${2:-} scope=${3:-$1} base out status=0 n=0 path canonical pattern
  local -a excludes=()
  repo=${repo:-$SHOKUNIN_ROOT}
  [ -d "$repo" ] || { printf 'unknown\n'; return; }
  for pattern in '*.env' '.env' '.env.*' '.envrc' '*credential*' '*secret*' 'id_*' '*.pem'; do
    excludes+=(--iglob "!**/$pattern" --iglob "!**/$pattern/**")
  done
  base=$(basename -- "$target")
  out=$(cd -- "$repo" && rg -l --hidden --no-ignore --text --fixed-strings -e "$base" . \
    -g '!.git' -g '!**/.git/**' \
    -g '!souji-shokunin/census/**' -g '!**/souji-shokunin/census/**' \
    -g '!souji-shokunin/tests/**' -g '!**/souji-shokunin/tests/**' \
    -g '!**/.ufo-quarantine/**' -g '!**/.ufo/state' -g '!**/.ufo/state/**' \
    -g '!**/.ufo/watchdog.log' "${excludes[@]}" 2>/dev/null) || status=$?
  if [ "$status" -gt 1 ]; then printf 'unknown\n'; return; fi
  while IFS= read -r path; do
    [ -n "$path" ] || continue
    [[ "$path" != *[[:cntrl:]]* ]] || { printf 'unknown\n'; return; }
    canonical=$(canon_path "$repo/${path#./}")
    case "$canonical" in "$scope"|"$scope"/*) continue ;; esac
    n=$((n + 1))
  done <<< "$out"
  printf '%s\n' "$n"
}

s18_old_scope() {
  local path=$1 cutoff=$2 p mtime
  mtime=$(stat -c %Y -- "$path" 2>/dev/null) || return 1
  [ "$mtime" -lt "$cutoff" ] || return 1
  if [ -d "$path" ]; then
    for p in "$path"/* "$path"/.[!.]* "$path"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      s18_path_ok "$p" && s18_old_scope "$p" "$cutoff" || return 1
    done
  fi
}

s18_scope_unreferenced() {
  local path=$1 repo=$2 scope=$3 p refs
  refs=$(count_live_refs "$path" "$repo" "$scope")
  if [ "$refs" != 0 ]; then NOTES+=("stale=live-refs=$refs"); return 1; fi
  if [ -d "$path" ]; then
    for p in "$path"/* "$path"/.[!.]* "$path"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      s18_scope_unreferenced "$p" "$repo" "$scope" || return 1
    done
  fi
}

try_stale() {
  local target=$1 repo=$2 kind now mtime tracked
  kind=$(scratch_type "$target") || { NOTES+=("stale=not-scratch-type"); return 1; }
  if [ -n "$repo" ]; then
    if ! tracked=$(git -C "$repo" ls-files -- "$target" 2>/dev/null); then
      NOTES+=("stale=tracking-unverifiable"); return 1
    fi
    if [ -n "$tracked" ]; then
      NOTES+=("stale=tracked-without-pushed-receipt"); return 1
    fi
  fi
  now=$(date +%s)
  if ! s18_old_scope "$target" "$((now - STALE_DAYS * 86400))"; then
    NOTES+=("stale=mtime-or-descendant-too-young"); return 1
  fi
  s18_scope_unreferenced "$target" "$repo" "$target" || return 1
  mtime=$(stat -c %Y -- "$target") || return 1
  R_VERDICT=SAFE; R_RECEIPT=stale; R_REASON=stale
  R_EVIDENCE="scratch-type=$kind refs=0 mtime-age-days=$(((now - mtime) / 86400)) descendants=old-and-unreferenced"
  return 0
}

evaluate_worktree() {
  local target=$1 meta=$2 owner head branch unp uniq dirty refs status
  local -a roots=()
  IFS=$'\t' read -r owner head branch <<< "$meta"
  R_VERDICT=NOT-SAFE; R_RECEIPT=none; R_REASON=none
  if ! git -C "$owner" cat-file -e "$head^{commit}" 2>/dev/null; then
    R_RECEIPT=history-unverifiable; R_REASON=history-unverifiable
    R_EVIDENCE="worktree-head-unverifiable head=$head"; return
  fi
  if [ -n "$branch" ]; then
    if ! unp=$(git -C "$owner" rev-list --count "$branch" --not --remotes 2>/dev/null); then
      R_RECEIPT=history-unverifiable; R_REASON=history-unverifiable
      R_EVIDENCE="worktree-branch-unverifiable branch=$branch"; return
    fi
    if [ "$unp" != 0 ]; then
      R_RECEIPT=unpushed-branch; R_REASON=unpushed-branch
      R_EVIDENCE="branch=${branch#refs/heads/} unpushed=$unp dir=$([ -d "$target" ] && printf present || printf absent) owner=$(basename -- "$owner")"; return
    fi
  fi
  if [ ! -d "$target" ]; then
    if ! refs=$(git -C "$owner" for-each-ref --format='%(objectname)' 2>/dev/null); then
      R_EVIDENCE="durable-refs-unverifiable"; return
    fi
    if [ -n "$refs" ]; then mapfile -t roots <<< "$refs"; fi
    if ! uniq=$(git -C "$owner" rev-list --count "$head" --not "${roots[@]}" -- 2>/dev/null); then
      R_EVIDENCE="worktree-ancestry-unverifiable"; return
    fi
    if [ "$uniq" = 0 ]; then R_VERDICT=SAFE; R_RECEIPT=metadata-prune; R_REASON=metadata-prune; fi
    R_EVIDENCE="dir=absent unique=$uniq head=${head:0:12} owner=$(basename -- "$owner") durable-refs-only=yes"
    return
  fi
  if ! status=$(git -C "$target" --no-optional-locks status --porcelain 2>/dev/null); then
    R_RECEIPT=dirty; R_REASON=dirty; R_EVIDENCE="dir=present status-unverifiable"; return
  fi
  dirty=0
  [ -z "$status" ] || dirty=$(printf '%s\n' "$status" | wc -l)
  if [ "$dirty" != 0 ]; then R_RECEIPT=dirty; R_REASON=dirty; fi
  R_EVIDENCE="dir=present dirty=$dirty owner=$(basename -- "$owner")"
}

evaluate_path() {
  local raw=$1 target
  if ! s18_path_ok "$raw"; then
    R_VERDICT=NOT-SAFE; R_RECEIPT=secrets-refusal; R_REASON=secrets-refusal
    R_EVIDENCE="secret-shaped-or-protected-symlink-or-control-path-refused"; return 0
  fi
  target=$(canon_path "$raw")
  if [ -d "$target" ] && ! s18_scope_ok "$target"; then
    R_VERDICT=NOT-SAFE; R_RECEIPT=secrets-refusal; R_REASON=secrets-refusal
    R_EVIDENCE="protected-or-unsupported-descendant-refused"; return 0
  fi
  s18_evaluate_path "$raw"
}

if [ "$S18_KIND" = quarantine ]; then
  resolve_default_ref() {
    local repo=$1 ref refs
    if ref=$(git -C "$repo" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null) \
      && git -C "$repo" rev-parse --verify "$ref^{commit}" >/dev/null 2>&1; then
      printf '%s\n' "$ref"; return
    fi
    refs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null) || return 1
    refs=$(printf '%s\n' "$refs" | grep -v '^refs/remotes/origin/HEAD$') || return 1
    [[ "$refs" != *$'\n'* && -n "$refs" ]] || return 1
    printf '%s\n' "$refs"
  }

  s18_q_storage_ok() {
    local path=$1 expected="$Q_CREPO/.ufo-quarantine"
    case "$path" in "$expected/"*) : ;; *) return 1 ;; esac
    s18_path_ok "$path" || return 1
    [ "$(canon_path "$path")" = "$path" ]
  }

  run_verify() {
    local t=$1 rc=0 prefix rest rel
    V_VERDICT=ERROR; V_RECEIPT=engine-error; V_EV=invalid-engine-record
    if ! s18_path_ok "$t" || ! s18_path_ok "$VERIFY_BIN"; then
      V_EV=unsafe-input-path; return 0
    fi
    V_RAW=$(SHOKUNIN_ROOT="$SV_ROOT" SOUJI_LEDGER="$SV_LEDGER" \
      bash "$VERIFY_BIN" --stale-days "$STALE_DAYS" -- "$t" 2>"$ERRTMP") || rc=$?
    prefix=$'VERDICT\t'"$t"$'\t'
    if [ "$rc" != 0 ] || [[ "$V_RAW" = *$'\n'* || "$V_RAW" != "$prefix"* ]]; then return 0; fi
    rest=${V_RAW#"$prefix"}
    [[ "$rest" = *$'\t'* ]] || return 0
    V_VERDICT=${rest%%$'\t'*}; rest=${rest#*$'\t'}
    [[ "$rest" = *$'\t'* ]] || { V_VERDICT=ERROR; return 0; }
    V_RECEIPT=${rest%%$'\t'*}; V_EV=${rest#*$'\t'}
    if [[ "$V_EV" = *[[:cntrl:]]* ]] || [[ "$V_VERDICT" != SAFE && "$V_VERDICT" != NOT-SAFE ]]; then
      V_VERDICT=ERROR; V_RECEIPT=engine-error; return 0
    fi
    if [ "$V_VERDICT" = SAFE ] && [ "$V_RECEIPT" = pushed ]; then
      case "$t" in "$Q_CREPO/.ufo-quarantine/"*) return 0 ;; esac
      rel=${t#"$Q_CREPO/"}
      S18_PUSH_REF=$(resolve_default_ref "$Q_CREPO") || { V_VERDICT=ERROR; return 0; }
      S18_PUSH_OBJECT=$(git -C "$Q_CREPO" rev-parse --verify "$S18_PUSH_REF:$rel" 2>/dev/null) || V_VERDICT=ERROR
    fi
  }

  ledger_row_for() {
    local want=$1 row isdir=${ISDIR:-0}
    s18_path_ok "$SV_LEDGER" && [ -f "$SV_LEDGER" ] || return 0
    while IFS= read -r row || [ -n "$row" ]; do
      s18_row_parse "$row" || continue
      [ "$S18_SP" = "$want" ] || continue
      s18_row_ok "$want" "$isdir" || continue
      case "$(canon_path "$S18_VP")/" in "$QPATH/"*) continue ;; esac
      printf '%s\t%s\t%s\n' "$S18_SS" "$S18_VP" "$S18_VS"
      return 0
    done < "$SV_LEDGER"
  }

  flow_one() {
    local raw=$1
    [[ "$raw" = /* ]] || raw="$REPO/$raw"
    if ! s18_path_ok "$raw"; then
      N_TOTAL=$((N_TOTAL + 1)); block_one "$raw" unsafe-path "secret-shaped-or-protected-symlink-or-control-path-refused"; return 0
    fi
    raw=$(canon_path "$raw")
    local qpath rel status
    rel=${raw#"$Q_CREPO/"}
    qpath="$Q_CREPO/.ufo-quarantine/$(date -u +%F)/$rel"
    if ! s18_q_storage_ok "$qpath"; then
      N_TOTAL=$((N_TOTAL + 1)); block_one "$raw" quarantine-containment "symlink-or-noncanonical-quarantine-path"; return 0
    fi
    if git_tracked "$Q_CREPO" "$rel"; then
      status=$(git_dirty_tracked "$Q_CREPO" "$rel")
      if [ -n "$status" ]; then
        N_TOTAL=$((N_TOTAL + 1)); block_one "$raw" dirty-tracked "r7-gate2 dirty-tracked-content"; return 0
      fi
    fi
    s18_flow_one "$@"
  }

  second_check() {
    s18_second_check
    if ! s18_q_storage_ok "$QPATH"; then
      SC_PASS=0; SC_EV="$SC_EV containment=FAIL"; return 0
    fi
    if [ "$P1_VERDICT" = ERROR ]; then
      SC_PASS=0; SC_EV="$SC_EV engine-error=FAIL"
    fi
    if [ "$CLASS" = pushed ]; then
      local ref object touching intro
      if ! ref=$(resolve_default_ref "$CREPO") \
        || [ "$ref" != "${S18_PUSH_REF:-}" ] \
        || ! object=$(git -C "$CREPO" rev-parse --verify "$ref:$REL" 2>/dev/null) \
        || [ "$object" != "${S18_PUSH_OBJECT:-}" ]; then
        SC_PASS=0; SC_EV="$SC_EV default-snapshot=FAIL"
      fi
      intro=$(git -C "$CREPO" log --diff-filter=A --format=%H -1 -- "$REL" 2>/dev/null) || intro=""
      if [ -z "$intro" ] || [ -z "${ref:-}" ] \
        || ! git -C "$CREPO" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
        SC_PASS=0; SC_EV="$SC_EV default-ancestry=FAIL"
      fi
      if ! touching=$(git -C "$CREPO" log --format=%H HEAD --branches --not --remotes -- "$REL" 2>/dev/null) || [ -n "$touching" ]; then
        SC_PASS=0; SC_EV="$SC_EV head-history=FAIL"
      fi
    fi
    return 0
  }
fi
