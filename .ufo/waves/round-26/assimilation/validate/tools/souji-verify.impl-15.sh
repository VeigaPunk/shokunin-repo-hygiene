#!/usr/bin/env bash
# souji-verify (impl-15) — receipt-based verdict tool for the souji lane.
#
#   tools/souji-verify.impl-15.sh [--selftest] [--stale-days N] [--json] <path>...
#
# One line per target:
#   VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-reason<TAB>decisive-evidence
# --json emits one JSON object per line instead.
# Exit: 0 evaluated clean, 1 selftest failure or evaluation error, 2 usage.
#
# SAFE receipts: pushed, moved-to-obsidian, stale, metadata-prune.
# NOT-SAFE reasons: unpushed, dirty, unpushed-branch, pushed-unverifiable,
# none, unreachable, secrets-refusal, evaluation-error.
#
# Read-only over every inspected surface. The only writes are mktemp -d
# scratch dirs (selftest fixtures, worktree index), removed on exit.
#
# D3 sweep note: ripgrep 15.2.0 has no --basename flag, so the reference
# sweep is "files whose basename equals the target basename" implemented
# with rg --files -g plus an exact-basename filter; the spec's exclusion
# globs are applied verbatim from the repo root. A hit on the target
# itself does not count as a reference.
set -euo pipefail

SCRIPT_PATH=$(readlink -f -- "${BASH_SOURCE[0]}")
TOOLS_DIR=$(dirname -- "$SCRIPT_PATH")
LANE_ROOT=${SOUJI_LANE_ROOT:-$(dirname -- "$TOOLS_DIR")}
FLEET_ROOT=${SHOKUNIN_ROOT:-$(dirname -- "$LANE_ROOT")}
LEDGER_FILE=${SOUJI_LEDGER:-$LANE_ROOT/corpus/knowledge/obsidian-ledger.tsv}

STALE_DAYS=1
JSON=0
MODE=eval
TARGETS=()
TMPD=""
WT_INDEX=""
NOW=0
NAME_SAFE_RE='^[A-Za-z0-9._+@%,:=~-]+$'

usage() {
  printf 'usage: %s [--selftest] [--stale-days N] [--json] <path>...\n' \
    "$(basename -- "$0")" >&2
}

on_exit() {
  local rc=$?
  if [ -n "$TMPD" ]; then
    rm -rf -- "$TMPD" || true
  fi
  case $rc in
    0|1|2) exit "$rc" ;;
    *) exit 1 ;;
  esac
}

split_tsv5() {
  local line=$1 t=$'\t' rest
  TSV1=${line%%"$t"*}
  rest=${line#*"$t"}
  TSV2=${rest%%"$t"*}
  rest=${rest#*"$t"}
  TSV3=${rest%%"$t"*}
  rest=${rest#*"$t"}
  TSV4=${rest%%"$t"*}
  TSV5=${rest#*"$t"}
}

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

emit_line() {
  local raw=$1 verdict=$2 receipt=$3 evidence=$4
  if [ "$JSON" -eq 1 ]; then
    printf '{"path":"%s","verdict":"%s","receipt":"%s","evidence":"%s"}\n' \
      "$(json_escape "$raw")" "$verdict" "$receipt" "$(json_escape "$evidence")"
  else
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$raw" "$verdict" "$receipt" "$evidence"
  fi
}

norm_path() {
  local p=$1
  case $p in
    /*) ;;
    *) p=$PWD/$p ;;
  esac
  if command -v realpath >/dev/null 2>&1; then
    p=$(realpath -m -- "$p")
  fi
  while [ "${p%/}" != "$p" ] && [ "$p" != "/" ]; do
    p=${p%/}
  done
  printf '%s' "$p"
}

is_secret() {
  case $1 in
    *.env|*credential*|*secret*|id_*|*.pem) return 0 ;;
  esac
  return 1
}

is_scratch() {
  local path=$1 base=${1##*/}
  case $path in
    */.scratch|*/.scratch/*) return 0 ;;
  esac
  case $base in
    *.out|*.log|*-draft.*|*checkpoint*.json|*checkpoint*.png) return 0 ;;
  esac
  return 1
}

repo_root_for() {
  local p=$1 d
  if [ -d "$p" ]; then d=$p; else d=$(dirname -- "$p"); fi
  [ -d "$d" ] || return 1
  git -C "$d" rev-parse --show-toplevel 2>/dev/null || return 1
}

resolve_default_ref() {
  local repo=$1 name ref refs n
  name=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD \
    2>/dev/null | sed 's@^origin/@@' || true)
  if [ -n "$name" ]; then
    ref="refs/remotes/origin/$name"
    if git -C "$repo" rev-parse -q --verify "$ref" >/dev/null 2>&1; then
      printf '%s' "$ref"
      return 0
    fi
  fi
  refs=$(git -C "$repo" for-each-ref --format='%(refname:short)' \
    refs/remotes/origin/ 2>/dev/null | grep -v '^origin/HEAD$' || true)
  n=$(printf '%s\n' "$refs" | grep -c '[^[:space:]]' || true)
  if [ "$n" -eq 1 ]; then
    ref="refs/remotes/$refs"
    if git -C "$repo" rev-parse -q --verify "$ref" >/dev/null 2>&1; then
      printf '%s' "$ref"
      return 0
    fi
  fi
  if git -C "$repo" show-ref --verify --quiet refs/heads/master; then
    printf 'refs/heads/master'
    return 0
  fi
  return 1
}

wt_index_build() {
  [ -n "$WT_INDEX" ] && return 0
  WT_INDEX="$TMPD/worktrees.tsv"
  : > "$WT_INDEX"
  local repo entry p owner sha br
  for repo in "$FLEET_ROOT" "$FLEET_ROOT"/*-shokunin; do
    [ -d "$repo/.git" ] || continue
    git -C "$repo" worktree list --porcelain 2>/dev/null | awk -v owner="$repo" '
      BEGIN { RS=""; FS="\n" }
      {
        p=""; h=""; b="-"
        for (i = 1; i <= NF; i++) {
          if ($i ~ /^worktree /) p = substr($i, 10)
          else if ($i ~ /^HEAD /) h = substr($i, 6)
          else if ($i ~ /^branch /) { b = substr($i, 8); sub(/^refs\/heads\//, "", b) }
        }
        if (p != "") printf "%s\t%s\t%s\t%s\n", p, owner, h, b
      }' >> "$WT_INDEX" || true
  done
  local tmp="$WT_INDEX.norm"
  : > "$tmp"
  while IFS=$'\t' read -r p owner sha br; do
    [ -n "${p:-}" ] || continue
    printf '%s\t%s\t%s\t%s\n' "$(norm_path "$p")" "$owner" "$sha" "$br" >> "$tmp"
  done < "$WT_INDEX"
  mv -f -- "$tmp" "$WT_INDEX"
}

wt_lookup() {
  wt_index_build
  awk -F'\t' -v p="$1" '$1 == p { print $2 "\t" $3 "\t" $4; exit }' "$WT_INDEX"
}

ledger_match() {
  local path=$1 sum src ssum vault vsum _rest rp nsrc nvault nvsum
  [ -f "$LEDGER_FILE" ] || return 1
  if ! sum=$(sha256sum -- "$path" 2>/dev/null | awk '{print $1}') || [ -z "$sum" ]; then
    return 1
  fi
  rp=$(norm_path "$path")
  while IFS=$'\t' read -r src ssum vault vsum _rest; do
    [ -n "${src:-}" ] || continue
    [ "$src" = "source_path" ] && continue
    nsrc=$(norm_path "$src")
    [ "$nsrc" = "$rp" ] || [ "$src" = "$path" ] || continue
    [ "$ssum" = "$sum" ] || continue
    [ -n "${vault:-}" ] && [ -f "$vault" ] || continue
    nvault=$(norm_path "$vault")
    if ! nvsum=$(sha256sum -- "$vault" 2>/dev/null | awk '{print $1}') || [ -z "$nvsum" ]; then
      continue
    fi
    [ "$nvsum" = "$vsum" ] || continue
    printf 'ledger=%s vault=%s sha256=%s' "$LEDGER_FILE" "$nvault" "${sum:0:12}"
    return 0
  done < "$LEDGER_FILE"
  return 1
}

refs_zero() {
  local path=$1 repo=$2 root name inc line rel count=0 tgt hits
  name=${path##*/}
  if [ -n "$repo" ]; then root=$repo; else root=$(dirname -- "$path"); fi
  [ -d "$root" ] || return 1
  [ "$root" != "/" ] || return 1
  command -v rg >/dev/null 2>&1 || return 1
  inc=$name
  [[ $name =~ $NAME_SAFE_RE ]] || inc='*'
  tgt=$(norm_path "$path")
  hits=$(cd "$root" && rg --files --hidden --no-ignore -g "$inc" . \
    -g '!.git' -g '!souji-shokunin/census/**' -g '!souji-shokunin/tests/**' \
    -g '!**/.ufo-quarantine/**' 2>/dev/null || true)
  if [ -n "$hits" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      rel=${line#./}
      [ "${rel##*/}" = "$name" ] || continue
      [ "$(norm_path "$root/$rel")" = "$tgt" ] && continue
      count=$((count + 1))
    done <<< "$hits"
  fi
  [ "$count" -eq 0 ]
}

evaluate_target() {
  local raw=$1 path base trace="" pushed_unverifiable=0
  if [ -z "$raw" ]; then
    emit_line "$raw" NOT-SAFE unreachable "empty-target"
    return 0
  fi
  path=$(norm_path "$raw")
  base=${path##*/}
  if is_secret "$base"; then
    emit_line "$raw" NOT-SAFE secrets-refusal "basename=$base"
    return 0
  fi

  if [ -d "$path/.git" ]; then
    local up di reason=none
    up=$( { git -C "$path" log --oneline --branches --not --remotes 2>/dev/null || true; } | wc -l )
    di=$( { git -C "$path" status --porcelain 2>/dev/null || true; } | wc -l )
    if [ "$up" -gt 0 ]; then reason=unpushed; elif [ "$di" -gt 0 ]; then reason=dirty; fi
    emit_line "$raw" NOT-SAFE "$reason" "unpushed=$up dirty=$di"
    return 0
  fi

  local wt owner sha br absent=0 unique unp
  wt=$(wt_lookup "$path") || wt=""
  if [ -n "$wt" ]; then
    IFS=$'\t' read -r owner sha br <<< "$wt"
    [ -d "$path" ] || absent=1
    unique=$( { git -C "$owner" log --oneline "$sha" --not --all 2>/dev/null || true; } | wc -l )
    unp=0
    if [ "$br" != "-" ]; then
      unp=$( { git -C "$owner" log --oneline "$br" --not --remotes 2>/dev/null || true; } | wc -l )
    fi
    if [ "$br" != "-" ] && [ "$unp" -gt 0 ]; then
      emit_line "$raw" NOT-SAFE unpushed-branch \
        "owner=$owner branch=$br unpushed=$unp dir-absent=$absent"
      return 0
    fi
    if [ "$absent" -eq 1 ] && [ "$unique" -eq 0 ]; then
      emit_line "$raw" SAFE metadata-prune \
        "owner=$owner absent unique=0 branch=$br"
      return 0
    fi
    if [ "$absent" -eq 0 ]; then
      local wd
      wd=$( { git -C "$path" status --porcelain 2>/dev/null || true; } | wc -l )
      if [ "$wd" -gt 0 ]; then
        emit_line "$raw" NOT-SAFE dirty "owner=$owner present dirty=$wd"
        return 0
      fi
    fi
    emit_line "$raw" NOT-SAFE none \
      "owner=$owner absent=$absent branch=$br unique=$unique unpushed=$unp"
    return 0
  fi

  if [ ! -e "$path" ]; then
    emit_line "$raw" NOT-SAFE unreachable "absent"
    return 0
  fi

  local repo rel dref intro vault mt
  repo=$(repo_root_for "$path") || repo=""
  if [ -n "$repo" ] && [ "$path" != "$repo" ]; then
    rel=${path#"$repo"/}
    if [ "$rel" = "$path" ]; then
      repo=""
      trace+="outside-repo-toplevel; "
    fi
  else
    repo=""
    trace+="not-in-a-repo; "
  fi
  if [ -n "$repo" ]; then
    if dref=$(resolve_default_ref "$repo"); then
      intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- ":(literal)$rel" \
        2>/dev/null | head -1 || true)
      if [ -n "$intro" ]; then
        if git -C "$repo" merge-base --is-ancestor "$intro" "$dref" 2>/dev/null; then
          emit_line "$raw" SAFE pushed "intro=${intro:0:12} ref=$dref"
          return 0
        fi
        trace+="intro=${intro:0:12} not-ancestor-of $dref; "
      else
        trace+="no-introducing-commit; "
      fi
    else
      pushed_unverifiable=1
      trace+="default-branch-unresolvable; "
    fi
  fi

  if [ -f "$path" ]; then
    if vault=$(ledger_match "$path"); then
      emit_line "$raw" SAFE moved-to-obsidian "$vault"
      return 0
    fi
    trace+="ledger-no-row; "
  else
    trace+="ledger-directory-unhashable; "
  fi

  if is_scratch "$path"; then
    if refs_zero "$path" "$repo"; then
      mt=$(stat -c %Y -- "$path" 2>/dev/null || printf '0')
      if [ $((NOW - mt)) -gt $((STALE_DAYS * 86400)) ]; then
        emit_line "$raw" SAFE stale "mtime=$mt limit-days=$STALE_DAYS refs=0"
        return 0
      fi
      trace+="mtime-recent(mtime=$mt); "
    else
      trace+="live-references; "
    fi
  else
    trace+="not-scratch-type; "
  fi

  local reason=none
  [ "$pushed_unverifiable" -eq 1 ] && reason=pushed-unverifiable
  emit_line "$raw" NOT-SAFE "$reason" "${trace%; }"
  return 0
}

eval_main() {
  NOW=$(date +%s)
  local t out rc=0
  for t in "${TARGETS[@]}"; do
    if out=$(evaluate_target "$t"); then
      printf '%s\n' "$out"
    else
      emit_line "$t" NOT-SAFE evaluation-error "internal-failure"
      rc=1
    fi
  done
  return "$rc"
}

fx_init_repo() {
  local dir=$1 br=${2:-master}
  mkdir -p "$dir"
  git init -q -b "$br" "$dir"
}

fx_commit() {
  local repo=$1 msg=$2 tree parent c br args=()
  git -C "$repo" add -A >/dev/null
  tree=$(git -C "$repo" write-tree)
  if git -C "$repo" rev-parse -q --verify HEAD >/dev/null 2>&1; then
    parent=$(git -C "$repo" rev-parse HEAD)
    args=(-p "$parent")
  fi
  c=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tree" "${args[@]}")
  br=$(git -C "$repo" symbolic-ref --short HEAD 2>/dev/null || printf 'master')
  git -C "$repo" update-ref "refs/heads/$br" "$c"
  printf '%s' "$c"
}

CX_NAME=()
CX_PATH=()
CX_VERDICT=()
CX_RECEIPT=()
CX_EV=()

add_case() {
  CX_NAME+=("$1")
  CX_PATH+=("$2")
  CX_VERDICT+=("$3")
  CX_RECEIPT+=("$4")
  CX_EV+=("${5:-}")
}

url_key() {
  if [ -z "$1" ]; then printf '__EMPTY__'; else printf '%s' "$1"; fi
}

run_child() {
  SHOKUNIN_ROOT="$FX_ROOT" SOUJI_LEDGER="$FX_LEDGER" LC_ALL=C \
    bash "$SCRIPT_PATH" "$@"
}

selftest_req() {
  if "$@" >/dev/null 2>&1; then return 0; fi
  return 1
}

selftest_main() {
  local fx="$TMPD/fx" root="$TMPD/fx/root" fails=0 total=0
  mkdir -p "$root" "$fx/vault" "$fx/ledger" "$fx/wt"

  if ! command -v rg >/dev/null 2>&1; then
    printf 'SELFTEST FAIL: rg not found on PATH\n'
    return 1
  fi

  local live_before live_after
  live_before=$(git -C "$LANE_ROOT" status --porcelain --untracked-files=no \
    2>/dev/null || true)

  export GIT_AUTHOR_NAME='souji fixture' GIT_AUTHOR_EMAIL='fixture@example.invalid'
  export GIT_COMMITTER_NAME='souji fixture' GIT_COMMITTER_EMAIL='fixture@example.invalid'
  export GIT_AUTHOR_DATE='@1700000000 +0000' GIT_COMMITTER_DATE='@1700000000 +0000'

  local tip base f1 f2a f2b f3 ow f6 f7 f8 f9 f10 f13
  local ssum vsum

  # F1: introducing commit is an ancestor of origin/HEAD's default branch.
  f1="$root/pushed-shokunin"
  fx_init_repo "$f1"
  printf 'readme\n' > "$f1/README.md"
  fx_commit "$f1" base >/dev/null
  printf 'fixture\n' > "$f1/notes.md"
  tip=$(fx_commit "$f1" 'add notes')
  git -C "$f1" update-ref refs/remotes/origin/master "$tip"
  git -C "$f1" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  add_case F1 "$f1/notes.md" SAFE pushed \
    '^intro=[0-9a-f]{12} ref=refs/remotes/origin/master$'

  # F2a: no origin refs and no local master -> pushed-unverifiable.
  f2a="$root/trunk-shokunin"
  fx_init_repo "$f2a" trunk
  printf 'readme\n' > "$f2a/README.md"
  fx_commit "$f2a" base >/dev/null
  printf 'local\n' > "$f2a/local.txt"
  fx_commit "$f2a" local >/dev/null
  add_case F2a "$f2a/local.txt" NOT-SAFE pushed-unverifiable \
    'default-branch-unresolvable'

  # F2b: origin/master resolves, introducing commit is local-only.
  f2b="$root/localonly-shokunin"
  fx_init_repo "$f2b"
  printf 'readme\n' > "$f2b/README.md"
  base=$(fx_commit "$f2b" base)
  git -C "$f2b" update-ref refs/remotes/origin/master "$base"
  printf 'later\n' > "$f2b/later.txt"
  fx_commit "$f2b" later >/dev/null
  add_case F2b "$f2b/later.txt" NOT-SAFE none \
    'not-ancestor-of refs/remotes/origin/master'

  # F3: kotodama-shaped repo root — unpushed commits plus a dirty tree.
  f3="$root/kotodama-shaped-shokunin"
  fx_init_repo "$f3"
  printf 'readme\n' > "$f3/README.md"
  fx_commit "$f3" base >/dev/null
  printf 'wip\n' > "$f3/wip.txt"
  fx_commit "$f3" wip >/dev/null
  printf 'dirty\n' > "$f3/untracked.txt"
  add_case F3 "$f3" NOT-SAFE unpushed '^unpushed=[1-9][0-9]* dirty=[1-9][0-9]*$'

  # F4/F4b/F5: worktree registrations against one owner.
  ow="$root/wt-owner-shokunin"
  fx_init_repo "$ow"
  printf 'readme\n' > "$ow/README.md"
  base=$(fx_commit "$ow" base)
  git -C "$ow" update-ref refs/remotes/origin/master "$base"
  git -C "$ow" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$ow" worktree add -q -b wt-f4 "$fx/wt/f4" master
  git -C "$ow" worktree add -q --detach "$fx/wt/f4b" master
  git -C "$ow" worktree add -q -b wt-f5 "$fx/wt/f5" master
  printf 'wt work\n' > "$fx/wt/f5/f5.txt"
  fx_commit "$fx/wt/f5" 'wt work' >/dev/null
  rm -rf "$fx/wt/f4" "$fx/wt/f4b"
  add_case F4 "$fx/wt/f4" SAFE metadata-prune '^owner=.*absent unique=0'
  add_case F4b "$fx/wt/f4b" SAFE metadata-prune '^owner=.*absent unique=0'
  add_case F5 "$fx/wt/f5" NOT-SAFE unpushed-branch 'branch=wt-f5 unpushed=1'

  # F6: ledger row with matching source/vault sha256.
  f6="$root/obsidian-src-shokunin"
  fx_init_repo "$f6"
  printf 'readme\n' > "$f6/README.md"
  fx_commit "$f6" base >/dev/null
  mkdir -p "$f6/notes"
  printf 'archive me\n' > "$f6/notes/keep-me.md"
  cp "$f6/notes/keep-me.md" "$fx/vault/keep-me.md"
  ssum=$(sha256sum -- "$f6/notes/keep-me.md" | awk '{print $1}')
  vsum=$(sha256sum -- "$fx/vault/keep-me.md" | awk '{print $1}')
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-18T00:00:00Z\tfixture\n' \
      "$f6/notes/keep-me.md" "$ssum" "$fx/vault/keep-me.md" "$vsum"
  } > "$fx/ledger/obsidian-ledger.tsv"
  add_case F6 "$f6/notes/keep-me.md" SAFE moved-to-obsidian \
    "vault=$fx/vault/keep-me.md"

  # F7: scratch file, no references, old mtime.
  f7="$root/scratch-repo-shokunin"
  fx_init_repo "$f7"
  printf 'readme\n' > "$f7/README.md"
  fx_commit "$f7" base >/dev/null
  mkdir -p "$f7/.scratch"
  printf 'scratch out\n' > "$f7/.scratch/notes.out"
  touch -d '4 days ago' "$f7/.scratch/notes.out"
  add_case F7 "$f7/.scratch/notes.out" SAFE stale 'refs=0'

  # F8: same basename exists in a census-like dir (D3) -> still stale.
  f8="$root/scratch-census-repo-shokunin"
  fx_init_repo "$f8"
  printf 'readme\n' > "$f8/README.md"
  fx_commit "$f8" base >/dev/null
  mkdir -p "$f8/.scratch" "$f8/souji-shokunin/census/round-1"
  printf 'scratch out\n' > "$f8/.scratch/notes.out"
  printf 'same basename in census\n' > "$f8/souji-shokunin/census/round-1/notes.out"
  touch -d '4 days ago' "$f8/.scratch/notes.out"
  add_case F8 "$f8/.scratch/notes.out" SAFE stale 'refs=0'

  # F9: origin/HEAD missing, single origin branch ref (D1 fallback).
  f9="$root/single-ref-shokunin"
  fx_init_repo "$f9"
  printf 'readme\n' > "$f9/README.md"
  fx_commit "$f9" base >/dev/null
  printf 'f9\n' > "$f9/f9.md"
  tip=$(fx_commit "$f9" 'add f9')
  git -C "$f9" update-ref refs/remotes/origin/master "$tip"
  add_case F9 "$f9/f9.md" SAFE pushed 'ref=refs/remotes/origin/master'

  # F10: secrets refusal, plus a negative control.
  f10="$root/safety-shokunin"
  fx_init_repo "$f10"
  printf 'readme\n' > "$f10/README.md"
  fx_commit "$f10" base >/dev/null
  printf 'SECRET=1\n' > "$f10/.env"
  printf 'x\n' > "$f10/id_fixture"
  printf 'x\n' > "$f10/svc-credentials.txt"
  printf 'x\n' > "$f10/pair.pem"
  printf 'x\n' > "$f10/my-secret-note.md"
  printf 'x\n' > "$f10/.env.example"
  add_case F10 "$f10/.env" NOT-SAFE secrets-refusal 'basename=.env'
  add_case F10b "$f10/id_fixture" NOT-SAFE secrets-refusal 'basename=id_fixture'
  add_case F10c "$f10/svc-credentials.txt" NOT-SAFE secrets-refusal ''
  add_case F10d "$f10/pair.pem" NOT-SAFE secrets-refusal ''
  add_case F10e "$f10/my-secret-note.md" NOT-SAFE secrets-refusal ''
  add_case F10f "$f10/.env.example" NOT-SAFE none 'not-scratch-type'

  # F11/F12: missing and empty targets stay NOT-SAFE without failing the run.
  add_case F11 "$root/definitely-missing" NOT-SAFE unreachable 'absent'
  add_case F12 "" NOT-SAFE unreachable 'empty-target'

  # F13: clean, fully pushed repo root still needs a receipt.
  f13="$root/clean-shokunin"
  fx_init_repo "$f13"
  printf 'readme\n' > "$f13/README.md"
  tip=$(fx_commit "$f13" base)
  git -C "$f13" update-ref refs/remotes/origin/master "$tip"
  git -C "$f13" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  add_case F13 "$f13" NOT-SAFE none '^unpushed=0 dirty=0$'

  FX_ROOT="$root"
  FX_LEDGER="$fx/ledger/obsidian-ledger.tsv"

  local out st line key
  local -A got=()
  local lines=0
  st=0
  out=$(run_child --stale-days 1 "${CX_PATH[@]}") || st=$?
  if [ "$st" -ne 0 ]; then
    printf 'SELFTEST FAIL: batch run exited %s\n' "$st"
    fails=$((fails + 1))
  fi
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    lines=$((lines + 1))
    split_tsv5 "$line"
    if [ "$TSV1" != "VERDICT" ] || [ -z "$TSV5" ] || [[ $TSV5 == *$'\t'* ]]; then
      printf 'SELFTEST FAIL: malformed line: %s\n' "$line"
      fails=$((fails + 1))
      continue
    fi
    key=$(url_key "$TSV2")
    got["$key"]="$TSV3"$'\t'"$TSV4"$'\t'"$TSV5"
  done <<< "$out"

  if [ "$lines" -ne "${#CX_PATH[@]}" ]; then
    printf 'SELFTEST FAIL: expected %s lines, got %s\n' "${#CX_PATH[@]}" "$lines"
    fails=$((fails + 1))
  fi

  local idx name p expected verdict receipt evidence key2
  for idx in "${!CX_NAME[@]}"; do
    total=$((total + 1))
    name=${CX_NAME[$idx]}
    p=${CX_PATH[$idx]}
    expected="${CX_VERDICT[$idx]}(${CX_RECEIPT[$idx]})"
    key2=$(url_key "$p")
    if [ -z "${got[$key2]+x}" ]; then
      printf 'SELFTEST FAIL %s: no line for [%s]\n' "$name" "$p"
      fails=$((fails + 1))
      continue
    fi
    IFS=$'\t' read -r verdict receipt evidence <<< "${got[$key2]}"
    if [ "$verdict" != "${CX_VERDICT[$idx]}" ] || [ "$receipt" != "${CX_RECEIPT[$idx]}" ]; then
      printf 'SELFTEST FAIL %s: expected %s, got %s(%s) evidence=%s\n' \
        "$name" "$expected" "$verdict" "$receipt" "$evidence"
      fails=$((fails + 1))
      continue
    fi
    if [ -n "${CX_EV[$idx]}" ] && ! [[ $evidence =~ ${CX_EV[$idx]} ]]; then
      printf 'SELFTEST FAIL %s: evidence does not match /%s/: %s\n' \
        "$name" "${CX_EV[$idx]}" "$evidence"
      fails=$((fails + 1))
      continue
    fi
    printf 'SELFTEST PASS %s  %s(%s)\n' "$name" "$verdict" "$receipt"
  done

  # --stale-days is honored end to end (4-day-old file vs 30-day threshold).
  st=0
  out=$(run_child --stale-days 30 "$f7/.scratch/notes.out") || st=$?
  if [ "$st" -ne 0 ] || ! printf '%s\n' "$out" | grep -q $'\tNOT-SAFE\tnone\t'; then
    printf 'SELFTEST FAIL F7b: --stale-days 30 expected NOT-SAFE(none), got rc=%s out=%s\n' \
      "$st" "$out"
    fails=$((fails + 1))
  else
    total=$((total + 1))
    printf 'SELFTEST PASS F7b  NOT-SAFE(none)\n'
  fi

  # --json emits one JSON object per target.
  st=0
  out=$(run_child --json "$f1/notes.md") || st=$?
  if [ "$st" -ne 0 ] || ! [[ $out == '{"path":"'*'"verdict":"SAFE"'*'"receipt":"pushed"'* ]]; then
    printf 'SELFTEST FAIL JSON: rc=%s out=%s\n' "$st" "$out"
    fails=$((fails + 1))
  else
    total=$((total + 1))
    printf 'SELFTEST PASS JSON  SAFE(pushed)\n'
  fi

  # Usage contract: no targets, bad threshold, unknown flag -> exit 2.
  local usage_ok=1
  st=0
  if bash "$SCRIPT_PATH" >/dev/null 2>&1; then st=0; else st=$?; fi
  [ "$st" -eq 2 ] || usage_ok=0
  st=0
  if bash "$SCRIPT_PATH" --stale-days nope /tmp/x >/dev/null 2>&1; then st=0; else st=$?; fi
  [ "$st" -eq 2 ] || usage_ok=0
  st=0
  if bash "$SCRIPT_PATH" --bogus /tmp/x >/dev/null 2>&1; then st=0; else st=$?; fi
  [ "$st" -eq 2 ] || usage_ok=0
  if [ "$usage_ok" -eq 1 ]; then
    total=$((total + 1))
    printf 'SELFTEST PASS USAGE  exit 2 on no-target/bad-threshold/unknown-flag\n'
  else
    printf 'SELFTEST FAIL USAGE: expected exit 2\n'
    fails=$((fails + 1))
  fi

  live_after=$(git -C "$LANE_ROOT" status --porcelain --untracked-files=no \
    2>/dev/null || true)
  if [ "$live_before" = "$live_after" ]; then
    total=$((total + 1))
    printf 'SELFTEST PASS LIVE-TREE  tracked status unchanged\n'
  else
    printf 'SELFTEST FAIL LIVE-TREE: tracked status changed\n'
    fails=$((fails + 1))
  fi

  if [ "$fails" -eq 0 ]; then
    printf 'selftest: %s/%s passed\n' "$total" "$total"
    return 0
  fi
  printf 'selftest: %s failure(s) of %s checks\n' "$fails" "$total"
  return 1
}

parse_args() {
  while [ $# -gt 0 ]; do
    case $1 in
      --selftest) MODE=selftest ;;
      --json) JSON=1 ;;
      --stale-days)
        if [ $# -lt 2 ]; then usage; exit 2; fi
        STALE_DAYS=$2
        shift
        ;;
      --stale-days=*) STALE_DAYS=${1#--stale-days=} ;;
      --)
        shift
        while [ $# -gt 0 ]; do
          TARGETS+=("$1")
          shift
        done
        break
        ;;
      -*) usage; exit 2 ;;
      *) TARGETS+=("$1") ;;
    esac
    shift
  done
  if ! [[ $STALE_DAYS =~ ^[0-9]+$ ]]; then
    usage
    exit 2
  fi
  if [ "$MODE" = eval ] && [ "${#TARGETS[@]}" -eq 0 ]; then
    usage
    exit 2
  fi
}

main() {
  parse_args "$@"
  TMPD=$(mktemp -d "${TMPDIR:-/tmp}/souji-verify.XXXXXX")
  trap on_exit EXIT
  trap 'exit 1' INT TERM
  NOW=$(date +%s)
  if [ "$MODE" = selftest ]; then
    selftest_main
  else
    eval_main
  fi
}

main "$@"
