#!/usr/bin/env bash
# souji-verify.impl-13.sh — seat S13 implementation of tools/souji-verify.spec.md (round 2).
#
# bash + coreutils + git + rg only. Read-only over every surface it inspects:
# no history-mutating git verbs (fetch/push/commit/branch/checkout/reset/rebase)
# appear anywhere in this file, and GIT_OPTIONAL_LOCKS=0 keeps git from
# refreshing the index. Fixtures in --selftest are built with plumbing only
# (hash-object / update-ref / write-tree / worktree add --no-checkout) inside a
# mktemp -d; the live tree is never touched.
#
# Host gap, disclosed not hidden: rg 15.2.0 here has no --basename flag, so the
# zero-references sweep runs the spec command when that flag exists and
# otherwise falls back to a content sweep for the basename plus a same-basename
# file sweep — never less conservative than the spec command. The evidence
# field records which sweep ran (sweep=basename|content).
#
# Usage: souji-verify.sh [--selftest] [--stale-days N] [--json] <path>...
# Exit:  0 evaluated clean; 1 selftest failure or evaluation error; 2 usage.

set -euo pipefail
export GIT_OPTIONAL_LOCKS=0
export LC_ALL=C

SELF_PATH=${BASH_SOURCE[0]}
case "$SELF_PATH" in
  */*) : ;;
  *) SELF_PATH=$(command -v -- "$SELF_PATH" 2>/dev/null || printf '%s' "$SELF_PATH") ;;
esac
LANE_DIR=$(cd -P -- "$(dirname -- "$SELF_PATH")/.." && pwd)
SHOKUNIN_ROOT=${SHOKUNIN_ROOT:-$(cd -P -- "$LANE_DIR/.." && pwd)}
LEDGER_REL=souji-shokunin/corpus/knowledge/obsidian-ledger.tsv
STALE_DAYS=1
JSON=0
SELFTEST=0
TARGETS=()
RESULTS=()
OWNERS=()
OWNERS_ROOT=
RG_BASENAME=no
EV_VERDICT=
EV_RECEIPT=
EV_EVIDENCE=

usage() {
  cat <<'EOF'
souji-verify.sh [--selftest] [--stale-days N] [--json] <path>...

  --selftest      build an isolated fixture git-repo under mktemp -d, run every
                  spec fixture case, assert exact verdict + receipt
  --stale-days N  mtime threshold in days, default 1 (older than 1 day)
  --json          emit the per-target records as a JSON array

output: VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-reason<TAB>evidence
EOF
}

die_usage() { printf 'souji-verify: %s\n' "$1" >&2; usage >&2; exit 2; }

norm() { realpath -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

cnt() { local v; v=$("$@" 2>/dev/null | wc -l || true); printf '%s' "${v//[[:space:]]/}"; }

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\n'/\\n}
  s=${s//$'\r'/\\r}
  printf '%s' "$s"
}

# --- safety rail: secret-shaped path components ---------------------------------

path_has_secret_component() {
  local p=$1 c
  local IFS=/
  local -a comps=()
  read -r -a comps <<< "$p"
  for c in "${comps[@]}"; do
    [ -n "$c" ] || continue
    case "${c,,}" in
      *.env|*credential*|*secret*|id_*|*.pem) return 0 ;;
    esac
  done
  return 1
}

# --- target kind detection ------------------------------------------------------

find_repo() {
  local d=$1 t
  if [ -f "$d" ]; then d=$(dirname -- "$d"); fi
  while :; do
    if [ -d "$d" ]; then
      t=$(git -C "$d" rev-parse --show-toplevel 2>/dev/null || true)
      if [ -n "$t" ]; then printf '%s' "$t"; return 0; fi
    fi
    if [ -d "$d/.git" ] || [ -f "$d/.git" ]; then printf '%s' "$d"; return 0; fi
    [ "$d" = / ] && break
    d=$(dirname -- "$d")
  done
  return 1
}

owners_init() {
  if [ "$OWNERS_ROOT" = "$SHOKUNIN_ROOT" ] && [ "${#OWNERS[@]}" -gt 0 ]; then return 0; fi
  OWNERS=()
  OWNERS_ROOT=$SHOKUNIN_ROOT
  local d
  if [ -d "$SHOKUNIN_ROOT" ]; then
    for d in "$SHOKUNIN_ROOT"/*-shokunin; do
      [ -d "$d" ] || continue
      [ -e "$d/.git" ] || continue
      OWNERS+=("$d")
    done
    if [ -e "$SHOKUNIN_ROOT/.git" ]; then OWNERS+=("$SHOKUNIN_ROOT"); fi
  fi
}

# Sets WT_OWNER/WT_HEAD/WT_BRANCH/WT_MAIN when the normalized target equals a
# `worktree <path>` registration of some owner repo.
worktree_scan() {
  local target=$1 owner line cpath chead cbranch done_blocks
  WT_OWNER=; WT_HEAD=; WT_BRANCH=; WT_MAIN=0
  owners_init
  for owner in "${OWNERS[@]}"; do
    cpath=; chead=; cbranch=; done_blocks=0
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        worktree\ *)
          if [ -n "$cpath" ] && [ "$(norm "$cpath")" = "$target" ]; then
            WT_OWNER=$owner; WT_HEAD=$chead; WT_BRANCH=$cbranch
            [ "$done_blocks" -eq 0 ] && WT_MAIN=1
            return 0
          fi
          [ -n "$cpath" ] && done_blocks=$((done_blocks + 1))
          cpath=${line#worktree }; chead=; cbranch=
          ;;
        HEAD\ *) chead=${line#HEAD } ;;
        branch\ *) cbranch=${line#branch } ;;
      esac
    done < <(git -C "$owner" worktree list --porcelain 2>/dev/null || true)
    if [ -n "$cpath" ] && [ "$(norm "$cpath")" = "$target" ]; then
      WT_OWNER=$owner; WT_HEAD=$chead; WT_BRANCH=$cbranch
      [ "$done_blocks" -eq 0 ] && WT_MAIN=1
      return 0
    fi
  done
  return 1
}

# --- receipts -------------------------------------------------------------------

resolve_default_ref() {
  local repo=$1 b ref
  local -a refs=()
  if b=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null); then
    b=${b#origin/}
    if [ -n "$b" ] && git -C "$repo" rev-parse --verify --quiet "refs/remotes/origin/$b" >/dev/null; then
      printf 'refs/remotes/origin/%s' "$b"
      return 0
    fi
  fi
  while IFS= read -r ref; do
    [ "$ref" = refs/remotes/origin/HEAD ] && continue
    [ -n "$ref" ] && refs+=("$ref")
  done < <(git -C "$repo" for-each-ref --format='%(refname)' 'refs/remotes/origin/*' 2>/dev/null || true)
  if [ "${#refs[@]}" -eq 1 ]; then
    printf '%s' "${refs[0]}"
    return 0
  fi
  if git -C "$repo" rev-parse --verify --quiet refs/heads/master >/dev/null 2>&1; then
    printf 'refs/heads/master'
    return 0
  fi
  return 1
}

ledger_match() {
  local target=$1 ledger row sp ssha vp vsha rest tsha vsha_actual
  ledger="$SHOKUNIN_ROOT/$LEDGER_REL"
  [ -f "$ledger" ] || return 1
  [ -f "$target" ] || return 1
  tsha=$(sha256sum -- "$target" 2>/dev/null | awk '{print $1}')
  [ -n "$tsha" ] || return 1
  while IFS= read -r row; do
    case "$row" in source_path*) continue ;; esac
    [ -n "$row" ] || continue
    IFS=$'\t' read -r sp ssha vp vsha rest <<< "$row"
    [ -n "${sp:-}" ] || continue
    if [ "$sp" != "$target" ] && [ "$(norm "$SHOKUNIN_ROOT/$sp")" != "$target" ]; then continue; fi
    [ "$ssha" = "$tsha" ] || continue
    [ -f "$vp" ] || continue
    vsha_actual=$(sha256sum -- "$vp" 2>/dev/null | awk '{print $1}')
    [ "$vsha_actual" = "$vsha" ] || continue
    printf 'source=%.12s vault=%s vault_sha=%.12s' "$tsha" "$vp" "$vsha_actual"
    return 0
  done < "$ledger"
  return 1
}

scratch_kind() {
  local p=$1 base comp
  base=$(basename -- "$p")
  local IFS=/
  local -a comps=()
  read -r -a comps <<< "$p"
  for comp in "${comps[@]}"; do
    [ "$comp" = .scratch ] && { printf '%s' scratch-dir; return 0; }
  done
  case "$base" in
    *.out) printf '%s' out; return 0 ;;
    *.log) printf '%s' log; return 0 ;;
    *checkpoint*.json|*checkpoint*.png) printf '%s' checkpoint; return 0 ;;
    *-draft.*) printf '%s' draft; return 0 ;;
  esac
  return 1
}

# Count of live references to `name` under `root`: files whose content mentions
# the basename, plus files carrying the same basename. The target itself never
# counts. The sweep runs with cwd = root because rg matches -g globs relative to
# the cwd, and the spec's excludes (souji-shokunin/census/** and friends) are
# repo-root-relative. Zero lines from the spec command, or from the disclosed
# fallback.
refs_count() {
  local name=$1 root=$2 self=$3 hits line n=0
  [ -d "$root" ] || return 1
  local -a gopts=(-g '!.git' -g '!souji-shokunin/census/**' -g '!souji-shokunin/tests/**' -g '!**/.ufo-quarantine/**')
  if [ "$RG_BASENAME" = yes ]; then
    hits=$(
      cd -- "$root" || exit 0
      rg -l --no-ignore --basename "${gopts[@]}" -- "$name" . 2>/dev/null || true
    )
  else
    hits=$(
      cd -- "$root" || exit 0
      {
        rg -l --no-ignore "${gopts[@]}" -F -- "$name" . 2>/dev/null || true
        rg --files --no-ignore "${gopts[@]}" -g "$name" -- . 2>/dev/null || true
      } | sed '/^$/d'
    )
  fi
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    case "$line" in ./*) line="$root/${line#./}" ;; esac
    [ "$(norm "$line")" = "$self" ] && continue
    n=$((n + 1))
  done <<< "$hits"
  printf '%s' "$n"
}

mtime_age_days() {
  local m now
  m=$(stat -c %Y -- "$1" 2>/dev/null) || return 1
  now=$(date +%s)
  printf '%s' $(( (now - m) / 86400 ))
}

probe_rg() {
  local rc=0
  printf '' | rg --basename souji-verify-probe >/dev/null 2>&1 || rc=$?
  case "$rc" in 0|1) RG_BASENAME=yes ;; *) RG_BASENAME=no ;; esac
}

# --- kind branches --------------------------------------------------------------

repo_root_eval() {
  local p=$1 ev unpushed dirty reason=none
  if ev=$(ledger_match "$p"); then
    EV_VERDICT=SAFE; EV_RECEIPT=moved-to-obsidian; EV_EVIDENCE=$ev
    return 0
  fi
  unpushed=$(cnt git -C "$p" log --oneline --branches --not --remotes)
  dirty=$(cnt git -C "$p" status --porcelain)
  if [ "$unpushed" -gt 0 ]; then reason=unpushed
  elif [ "$dirty" -gt 0 ]; then reason=dirty
  fi
  EV_VERDICT=NOT-SAFE; EV_RECEIPT=$reason; EV_EVIDENCE="unpushed=$unpushed dirty=$dirty"
}

worktree_eval() {
  local p=$1 dir_state branch unpushed unique dirty=0
  if [ -d "$p" ]; then dir_state=present; else dir_state=absent; fi
  if [ -n "$WT_BRANCH" ]; then
    branch=${WT_BRANCH#refs/heads/}
    if git -C "$WT_OWNER" rev-parse --verify --quiet "refs/heads/$branch" >/dev/null 2>&1; then
      unpushed=$(cnt git -C "$WT_OWNER" log --oneline "refs/heads/$branch" --not --remotes)
      if [ "$unpushed" -gt 0 ]; then
        EV_VERDICT=NOT-SAFE; EV_RECEIPT=unpushed-branch
        EV_EVIDENCE="branch=$branch unpushed=$unpushed dir=$dir_state"
        return 0
      fi
    fi
  fi
  if [ -z "$WT_HEAD" ]; then
    EV_VERDICT=NOT-SAFE; EV_RECEIPT=none; EV_EVIDENCE="dir=$dir_state head-unavailable"
    return 0
  fi
  unique=$(cnt git -C "$WT_OWNER" log --oneline "$WT_HEAD" --not --all)
  if [ "$dir_state" = absent ] && [ "$unique" = 0 ]; then
    EV_VERDICT=SAFE; EV_RECEIPT=metadata-prune; EV_EVIDENCE="dir=absent unique=0"
    return 0
  fi
  if [ "$dir_state" = present ]; then
    dirty=$(cnt git -C "$p" status --porcelain)
    if [ "$dirty" -gt 0 ]; then
      EV_VERDICT=NOT-SAFE; EV_RECEIPT=dirty; EV_EVIDENCE="dir=present dirty=$dirty"
      return 0
    fi
  fi
  EV_VERDICT=NOT-SAFE; EV_RECEIPT=none
  EV_EVIDENCE="dir=$dir_state unique=$unique dirty=$dirty"
}

artifact_eval() {
  local p=$1 repo intro ref ev note= scratch age refs root
  repo=$(find_repo "$p" || true)
  intro=
  if [ -n "$repo" ]; then
    intro=$({ git -C "$repo" log --diff-filter=A --format=%H -1 -- "$p" 2>/dev/null || true; } | head -n1 | tr -d '[:space:]')
  fi
  if [ -n "$intro" ] && [ -n "$repo" ]; then
    if ref=$(resolve_default_ref "$repo"); then
      if git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
        EV_VERDICT=SAFE; EV_RECEIPT=pushed
        EV_EVIDENCE="intro=${intro:0:12} ref=$ref"
        return 0
      fi
      note="intro=${intro:0:12} not-ancestor-of $ref"
    else
      EV_VERDICT=NOT-SAFE; EV_RECEIPT=pushed-unverifiable
      EV_EVIDENCE="intro=${intro:0:12} default-branch-unresolvable"
      return 0
    fi
  fi
  if ev=$(ledger_match "$p"); then
    EV_VERDICT=SAFE; EV_RECEIPT=moved-to-obsidian; EV_EVIDENCE=$ev
    return 0
  fi
  if scratch=$(scratch_kind "$p"); then
    if age=$(mtime_age_days "$p"); then
      if [ "$age" -gt "$STALE_DAYS" ]; then
        root=$repo
        [ -n "$root" ] || root=$SHOKUNIN_ROOT
        if refs=$(refs_count "$(basename -- "$p")" "$root" "$p"); then
          if [ "$refs" = 0 ]; then
            local sweep=content
            [ "$RG_BASENAME" = yes ] && sweep=basename
            EV_VERDICT=SAFE; EV_RECEIPT=stale
            EV_EVIDENCE="scratch=$scratch age_days=$age refs=0 sweep=$sweep scope=$root"
            return 0
          fi
          note="refs=$refs"
        else
          note=refs-unverifiable
        fi
      else
        note="age_days=$age"
      fi
    fi
  fi
  EV_VERDICT=NOT-SAFE; EV_RECEIPT=none
  if [ -n "$note" ]; then EV_EVIDENCE="no receipt; $note"
  else EV_EVIDENCE="no receipt${repo:+; repo=$repo}"; fi
}

evaluate_target() {
  local raw=$1 p
  EV_VERDICT=NOT-SAFE; EV_RECEIPT=none; EV_EVIDENCE=
  if [ -z "$raw" ]; then
    EV_RECEIPT=unreachable; EV_EVIDENCE="empty target"
    return 0
  fi
  p=$(norm "$raw")
  if path_has_secret_component "$p"; then
    EV_RECEIPT=secrets-refusal; EV_EVIDENCE="secret-shaped path component; not read"
    return 0
  fi
  if [ -d "$raw" ] && [ -d "$raw/.git" ]; then
    repo_root_eval "$p"
    return 0
  fi
  if [ -d "$raw" ] || [ ! -e "$raw" ]; then
    if worktree_scan "$p"; then
      worktree_eval "$p"
      return 0
    fi
  fi
  if [ ! -e "$raw" ]; then
    EV_RECEIPT=unreachable; EV_EVIDENCE="path does not exist"
    return 0
  fi
  artifact_eval "$p"
}

record_result() {
  local path=$1
  RESULTS+=("$path"$'\x1f'"$EV_VERDICT"$'\x1f'"$EV_RECEIPT"$'\x1f'"$EV_EVIDENCE")
}

print_results() {
  local rec path verdict receipt evidence
  if [ "$JSON" -eq 1 ]; then
    printf '[\n'
    local first=1
    for rec in "${RESULTS[@]}"; do
      IFS=$'\x1f' read -r path verdict receipt evidence <<< "$rec"
      [ "$first" -eq 0 ] && printf ',\n'
      first=0
      printf '  {"path": "%s", "verdict": "%s", "receipt": "%s", "evidence": "%s"}' \
        "$(json_escape "$path")" "$(json_escape "$verdict")" \
        "$(json_escape "$receipt")" "$(json_escape "$evidence")"
    done
    [ "${#RESULTS[@]}" -gt 0 ] && printf '\n'
    printf ']\n'
  else
    for rec in "${RESULTS[@]}"; do
      IFS=$'\x1f' read -r path verdict receipt evidence <<< "$rec"
      printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$path" "$verdict" "$receipt" "$evidence"
    done
  fi
}

# --- selftest -------------------------------------------------------------------

fx_init() { git init -q -b "$2" -- "$1"; }

fx_commit() {
  local repo=$1 msg=$2 parent=$3 tree
  tree=$(git -C "$repo" write-tree)
  {
    printf 'tree %s\n' "$tree"
    [ "$parent" = - ] || printf 'parent %s\n' "$parent"
    printf 'author Fixture <fixture@invalid> 1700000000 +0000\n'
    printf 'committer Fixture <fixture@invalid> 1700000000 +0000\n\n'
    printf '%s\n' "$msg"
  } | git -C "$repo" hash-object -w -t commit --stdin
}

fx_stage() { git -C "$1" add -A -- . >/dev/null; }

build_fixtures() {
  local FIX=$1 own c1 c2 c3 base sha1 sha2 sha3

  fx_init "$FIX" master
  mkdir -p "$FIX/souji-shokunin/census" "$FIX/souji-shokunin/tests/fixtures" \
    "$FIX/souji-shokunin/tests/results" "$FIX/souji-shokunin/corpus/knowledge" \
    "$FIX/.scratch" "$FIX/moved" "$FIX/vault" "$FIX/f10"
  printf 'fixture lane\n' > "$FIX/souji-shokunin/README.md"
  fx_stage "$FIX"
  base=$(fx_commit "$FIX" fleet-base -)
  git -C "$FIX" update-ref refs/heads/master "$base"

  # F1: introducing commit is an ancestor of origin/master
  mkdir -p "$FIX/f1repo/keep"
  fx_init "$FIX/f1repo" master
  printf 'artifact one\n' > "$FIX/f1repo/keep/artifact.txt"
  fx_stage "$FIX/f1repo"
  c1=$(fx_commit "$FIX/f1repo" one -)
  printf 'later\n' > "$FIX/f1repo/later.txt"
  fx_stage "$FIX/f1repo"
  c2=$(fx_commit "$FIX/f1repo" two "$c1")
  git -C "$FIX/f1repo" update-ref refs/heads/master "$c2"
  git -C "$FIX/f1repo" update-ref refs/remotes/origin/master "$c2"
  git -C "$FIX/f1repo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

  # F9: no origin/HEAD, exactly one origin branch ref -> same verdict as F1
  mkdir -p "$FIX/f9repo/keep9"
  fx_init "$FIX/f9repo" master
  printf 'artifact nine\n' > "$FIX/f9repo/keep9/artifact9.txt"
  fx_stage "$FIX/f9repo"
  c1=$(fx_commit "$FIX/f9repo" one -)
  printf 'later nine\n' > "$FIX/f9repo/later9.txt"
  fx_stage "$FIX/f9repo"
  c2=$(fx_commit "$FIX/f9repo" two "$c1")
  git -C "$FIX/f9repo" update-ref refs/heads/master "$c2"
  git -C "$FIX/f9repo" update-ref refs/remotes/origin/master "$c2"

  # F2: introducing commit is local-only
  fx_init "$FIX/f2repo" master
  printf 'base two\n' > "$FIX/f2repo/base.txt"
  fx_stage "$FIX/f2repo"
  c1=$(fx_commit "$FIX/f2repo" base -)
  git -C "$FIX/f2repo" update-ref refs/heads/master "$c1"
  git -C "$FIX/f2repo" update-ref refs/remotes/origin/master "$c1"
  printf 'local only\n' > "$FIX/f2repo/local-only.txt"
  fx_stage "$FIX/f2repo"
  c2=$(fx_commit "$FIX/f2repo" local "$c1")
  git -C "$FIX/f2repo" update-ref refs/heads/master "$c2"

  # F3: kotodama-shaped repo root — unpushed commits + dirty tree
  fx_init "$FIX/f3repo" master
  printf 'base three\n' > "$FIX/f3repo/base.txt"
  fx_stage "$FIX/f3repo"
  c1=$(fx_commit "$FIX/f3repo" base -)
  git -C "$FIX/f3repo" update-ref refs/heads/master "$c1"
  git -C "$FIX/f3repo" update-ref refs/remotes/origin/master "$c1"
  printf 'unpushed\n' > "$FIX/f3repo/more.txt"
  fx_stage "$FIX/f3repo"
  c2=$(fx_commit "$FIX/f3repo" more "$c1")
  git -C "$FIX/f3repo" update-ref refs/heads/master "$c2"
  printf 'dirty\n' >> "$FIX/f3repo/base.txt"

  # F11: no remote, no local master -> default branch unresolvable
  fx_init "$FIX/f11repo" trunk
  mkdir -p "$FIX/f11repo/keep"
  printf 'eleven\n' > "$FIX/f11repo/keep/f11.txt"
  fx_stage "$FIX/f11repo"
  c1=$(fx_commit "$FIX/f11repo" one -)
  git -C "$FIX/f11repo" update-ref refs/heads/trunk "$c1"

  # F4/F5 owner: registered worktrees
  own=$FIX/fixture-owner-shokunin
  fx_init "$own" master
  printf 'owner base\n' > "$own/base.txt"
  fx_stage "$own"
  c1=$(fx_commit "$own" base -)
  git -C "$own" update-ref refs/heads/master "$c1"
  printf 'owner second\n' > "$own/second.txt"
  fx_stage "$own"
  c2=$(fx_commit "$own" second "$c1")
  git -C "$own" update-ref refs/heads/master "$c2"
  git -C "$own" update-ref refs/remotes/origin/master "$c2"
  git -C "$own" worktree add -q --no-checkout --detach "$own/wt-prune" "$c1"
  rm -rf "$own/wt-prune"
  printf 'owner third\n' > "$own/third.txt"
  fx_stage "$own"
  c3=$(fx_commit "$own" third "$c2")
  git -C "$own" update-ref refs/heads/wt-branch "$c3"
  git -C "$own" worktree add -q --no-checkout "$own/wt-branch" wt-branch
  git -C "$own" worktree add -q --no-checkout --detach "$own/wt-dirty" "$c1"

  # F6: ledger rows — absolute row with matching hashes, relative row with
  # matching hashes, and a stale row whose source sha no longer matches
  printf 'obsidian payload one\n' > "$FIX/moved/keep.pdf"
  printf 'obsidian payload one\n' > "$FIX/vault/keep.pdf"
  printf 'obsidian payload two\n' > "$FIX/moved/keep2.pdf"
  printf 'obsidian payload two\n' > "$FIX/vault/keep2.pdf"
  printf 'obsidian payload three\n' > "$FIX/moved/keep3.pdf"
  sha1=$(sha256sum -- "$FIX/moved/keep.pdf" | awk '{print $1}')
  sha2=$(sha256sum -- "$FIX/moved/keep2.pdf" | awk '{print $1}')
  sha3=$(sha256sum -- "$FIX/moved/keep3.pdf" | awk '{print $1}')
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-01\tabstract\n' "$FIX/moved/keep.pdf" "$sha1" "$FIX/vault/keep.pdf" "$sha1"
    printf 'moved/keep2.pdf\t%s\t%s\t%s\t2026-10-01\trelative\n' "$sha2" "$FIX/vault/keep2.pdf" "$sha2"
    printf '%s\t%s\t%s\t%s\t2026-10-01\tstale-hash\n' "$FIX/moved/keep3.pdf" "${sha3:0:63}0" "$FIX/vault/keep3.pdf" "$sha3"
  } > "$FIX/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv"

  # F7/F8: scratch files, old mtime; the census-like dir mentions F8's basename
  printf 'scratch seven\n' > "$FIX/.scratch/f7-dump.out"
  printf 'scratch eight\n' > "$FIX/.scratch/f8-dump.out"
  printf 'census row mentioning f8-dump.out in its own text\n' > "$FIX/souji-shokunin/census/fixture-rows.tsv"
  touch -d '2026-01-01T00:00:00Z' "$FIX/.scratch/f7-dump.out" "$FIX/.scratch/f8-dump.out"

  # F13: scratch file with a real live reference outside the excluded dirs
  fx_init "$FIX/ref-repo" master
  mkdir -p "$FIX/ref-repo/.scratch"
  printf 'ref scratch\n' > "$FIX/ref-repo/.scratch/ref-dump.out"
  printf 'notes referencing ref-dump.out as a live dependency\n' > "$FIX/ref-repo/notes.txt"
  touch -d '2026-01-01T00:00:00Z' "$FIX/ref-repo/.scratch/ref-dump.out"

  # F10: secret-shaped path (contents are placeholders and are never read)
  printf 'PLACEHOLDER=1\n' > "$FIX/f10/.env"
  mkdir -p "$FIX/f10/.env.d"
  mkdir -p "$FIX/f10/nest"
  printf 'PLACEHOLDER=1\n' > "$FIX/f10/nest/id_rsa.pem"
}

selftest_case() {
  local id=$1 want_verdict=$2 want_receipt=$3 ev_re=$4 target=$5
  evaluate_target "$target"
  SELFTEST_CASES=$((SELFTEST_CASES + 1))
  if [ "$EV_VERDICT" = "$want_verdict" ] && [ "$EV_RECEIPT" = "$want_receipt" ] \
     && { [ -z "$ev_re" ] || printf '%s' "$EV_EVIDENCE" | grep -Eq -- "$ev_re"; }; then
    printf '%s PASS %s(%s) evidence=%s\n' "$id" "$EV_VERDICT" "$EV_RECEIPT" "$EV_EVIDENCE"
  else
    printf '%s FAIL want %s(%s)/%s got %s(%s) evidence=%s\n' \
      "$id" "$want_verdict" "$want_receipt" "${ev_re:--}" "$EV_VERDICT" "$EV_RECEIPT" "$EV_EVIDENCE"
    SELFTEST_FAILS=$((SELFTEST_FAILS + 1))
  fi
}

run_selftest() {
  local FIX saved_root
  FIX=$(mktemp -d) || { printf 'selftest: mktemp failed\n' >&2; return 1; }
  saved_root=$SHOKUNIN_ROOT
  SELFTEST_CASES=0
  SELFTEST_FAILS=0
  build_fixtures "$FIX" || { printf 'selftest: fixture build failed\n' >&2; rm -rf "$FIX"; return 1; }
  SHOKUNIN_ROOT=$FIX
  OWNERS_ROOT=
  printf 'selftest: fixtures under %s\n' "$FIX"
  selftest_case F1  SAFE     pushed            'intro=[0-9a-f]{12} ref=refs/remotes/origin/master' "$FIX/f1repo/keep/artifact.txt"
  selftest_case F2  NOT-SAFE none              'no receipt' "$FIX/f2repo/local-only.txt"
  selftest_case F3  NOT-SAFE unpushed          'unpushed=1 dirty=1' "$FIX/f3repo"
  selftest_case F4  SAFE     metadata-prune    'dir=absent unique=0' "$FIX/fixture-owner-shokunin/wt-prune"
  selftest_case F5  NOT-SAFE unpushed-branch   'branch=wt-branch unpushed=1' "$FIX/fixture-owner-shokunin/wt-branch"
  selftest_case F6  SAFE     moved-to-obsidian 'vault=' "$FIX/moved/keep.pdf"
  selftest_case F6b SAFE     moved-to-obsidian 'vault=' "$FIX/moved/keep2.pdf"
  selftest_case F6c NOT-SAFE none              'no receipt' "$FIX/moved/keep3.pdf"
  selftest_case F7  SAFE     stale             'refs=0' "$FIX/.scratch/f7-dump.out"
  selftest_case F8  SAFE     stale             'refs=0' "$FIX/.scratch/f8-dump.out"
  selftest_case F9  SAFE     pushed            'ref=refs/remotes/origin/master' "$FIX/f9repo/keep9/artifact9.txt"
  selftest_case F10 NOT-SAFE secrets-refusal   '' "$FIX/f10/.env"
  selftest_case F10b NOT-SAFE secrets-refusal  '' "$FIX/f10/nest/id_rsa.pem"
  selftest_case F11 NOT-SAFE pushed-unverifiable '' "$FIX/f11repo/keep/f11.txt"
  selftest_case F12 NOT-SAFE unreachable       '' "$FIX/nope/absent.txt"
  selftest_case F13 NOT-SAFE none              'refs=1' "$FIX/ref-repo/.scratch/ref-dump.out"
  selftest_case F14 NOT-SAFE dirty             'dir=present dirty=[1-9]' "$FIX/fixture-owner-shokunin/wt-dirty"
  SHOKUNIN_ROOT=$saved_root
  OWNERS_ROOT=
  rm -rf "$FIX"
  printf 'selftest: %d cases, %d failures\n' "$SELFTEST_CASES" "$SELFTEST_FAILS"
  [ "$SELFTEST_FAILS" -eq 0 ]
}

# --- main -----------------------------------------------------------------------

while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --stale-days)
      [ $# -ge 2 ] || die_usage "--stale-days requires N"
      case "$2" in ''|*[!0-9]*) die_usage "--stale-days wants a non-negative integer, got '$2'" ;; esac
      STALE_DAYS=$2; shift 2 ;;
    --stale-days=*)
      case "${1#--stale-days=}" in ''|*[!0-9]*) die_usage "--stale-days wants a non-negative integer, got '${1#--stale-days=}'" ;; esac
      STALE_DAYS=${1#--stale-days=}; shift ;;
    --) shift; while [ $# -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    -h|--help) usage; exit 0 ;;
    -*) die_usage "unknown flag: $1" ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done

if [ "$SELFTEST" -eq 0 ] && [ "${#TARGETS[@]}" -eq 0 ]; then
  die_usage "no targets and no --selftest"
fi

for dep in git rg sha256sum realpath stat; do
  command -v "$dep" >/dev/null 2>&1 || { printf 'souji-verify: missing dependency: %s\n' "$dep" >&2; exit 1; }
done
probe_rg

if [ "$SELFTEST" -eq 1 ]; then
  run_selftest || exit 1
fi

if [ "${#TARGETS[@]}" -gt 0 ]; then
  for t in "${TARGETS[@]}"; do
    evaluate_target "$t"
    record_result "$t"
  done
  print_results
fi
exit 0
