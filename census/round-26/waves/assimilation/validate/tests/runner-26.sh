#!/usr/bin/env bash
# tests/runner-26.sh — souji-shokunin round 2, seat S26 (test runner; twin of S17, independent).
#
# Independent test runner for tools/souji-verify.sh (binding spec:
# tools/souji-verify.spec.md). Everything it builds lives under mktemp -d;
# the only repo file it writes is the results JSON (default
# tests/results/runner-26.json). Fixture git repositories are the only place
# this runner runs mutating git commands — a guard refuses mutation anywhere
# outside the mktemp workspace.
#
# What it does:
#   1. builds one isolated fixture workspace (git repos shaped like the real
#      round-1 cases: pushed file, local-only commit, kotodama-shaped repo,
#      lore-shaped detached prunable worktree, gd2d-shaped named-branch
#      worktree, ledger match, scratch/census cases, secrets-shaped paths);
#   2. runs the whole case suite against an embedded spec-conformant
#      reference implementation — all cases must pass (positive control);
#   3. runs the suite against four deliberately defective mutants
#      (D1 default-branch, D2 worktree kind, D3 census-excluding sweep,
#      D4 secrets rail) and asserts the runner flags each defect;
#   4. if tools/souji-verify.sh exists, runs its --selftest and the same
#      suite against it, and reports per-case verdicts, false-SAFE count and
#      a PASS/FAIL/ABSENT verdict in the results JSON.
#
# Usage: tests/runner-26.sh [--tool PATH] [--out PATH] [--keep]
# Exit: 0 = harness calibrated and (tool PASS or tool absent); 1 = harness
#       calibration failure, or tool present and failing.
#
# Isolation contract assumed of the tool under test: it honours SHOKUNIN_ROOT
# for the fleet-root scan/sweep and SOUJI_LEDGER for the ledger; the runner
# also copies the tool into the fixture lane repo so tools that resolve
# `corpus/knowledge/obsidian-ledger.tsv` relative to their own script
# location work unchanged.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TOOL="$REPO/tools/souji-verify.sh"
OUT="$REPO/tests/results/runner-26.json"
KEEP=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --tool) TOOL="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --keep) KEEP=1; shift ;;
    -h|--help) sed -n '2,30p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) printf 'usage: %s [--tool PATH] [--out PATH] [--keep]\n' "$(basename "$0")" >&2; exit 2 ;;
  esac
done

MKT="$(mktemp -d /tmp/souji-s26.XXXXXX)"
cleanup() { [ "$KEEP" -eq 1 ] || rm -rf "$MKT"; }
trap cleanup EXIT

WS="$MKT/ws"
LEDGER="$WS/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv"
RECORDS="$MKT/records.tsv"
META="$MKT/meta.tsv"
: > "$RECORDS"
: > "$META"

mkdir -p "$MKT/home" "$MKT/wt" "$MKT/remotes" "$MKT/stderr"

# ---------------------------------------------------------------------------
# fixture git: hermetic env + mutation guard
# ---------------------------------------------------------------------------
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME="s26-fixture" GIT_AUTHOR_EMAIL="s26-fixture@example.invalid"
export GIT_COMMITTER_NAME="s26-fixture" GIT_COMMITTER_EMAIL="s26-fixture@example.invalid"
export GIT_TERMINAL_PROMPT=0

gitq() { # <dir> <git args...> — refuse mutating git outside the mktemp workspace
  local dir="$1"; shift
  case "$dir" in "$MKT"/*) ;; *) printf 'REFUSED: git outside fixture workspace: %s\n' "$dir" >&2; exit 9 ;; esac
  git -C "$dir" "$@"
}

new_repo() { # <path> — empty repo on master with one initial commit
  mkdir -p "$(dirname "$1")"
  gitq "$(dirname "$1")" init -q -b master "$1"
  printf 'seed\n' > "$1/seed.txt"
  gitq "$1" add -A
  gitq "$1" commit -qm "seed"
}

add_remote() { # <repo> <bare-name> — bare origin, push master, keep origin/HEAD unset
  local repo="$1" name="$2"
  gitq "$MKT/remotes" init -q --bare "$MKT/remotes/$name.git"
  gitq "$repo" remote add origin "$MKT/remotes/$name.git"
  gitq "$repo" push -q -u origin master
}

set_origin_head() { # <repo> <branch> — create refs/remotes/origin/HEAD (as a clone would)
  local repo="$1" branch="$2"
  gitq "$repo" remote set-head origin "$branch"
}

write_file() { # <path> <content>
  mkdir -p "$(dirname "$1")"
  printf '%s\n' "$2" > "$1"
}

age_file() { # <path> <days>
  touch -d "@$(( $(date +%s) - "$2" * 86400 ))" "$1"
}

# ---------------------------------------------------------------------------
# fixture workspace
# ---------------------------------------------------------------------------
build_fixtures() {
  local lane="$WS/souji-shokunin"

  # fixture lane repo (holds the tool copy, ledger, census sample)
  new_repo "$lane"
  mkdir -p "$lane/tools" "$lane/corpus/knowledge" "$lane/census/round-1" "$lane/tests" "$lane/.scratch" "$lane/notes"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$LEDGER"

  # F1/F2/F9 repos: origin remote, all pushable refs present
  new_repo "$WS/f1fix-shokunin"
  write_file "$WS/f1fix-shokunin/target-f1.txt" "f1 pushed payload"
  gitq "$WS/f1fix-shokunin" add -A
  gitq "$WS/f1fix-shokunin" commit -qm "F1: add pushed target"
  add_remote "$WS/f1fix-shokunin" f1
  set_origin_head "$WS/f1fix-shokunin" master

  new_repo "$WS/f2fix-shokunin"
  add_remote "$WS/f2fix-shokunin" f2
  set_origin_head "$WS/f2fix-shokunin" master
  write_file "$WS/f2fix-shokunin/target-f2.txt" "f2 local-only payload"
  gitq "$WS/f2fix-shokunin" add -A
  gitq "$WS/f2fix-shokunin" commit -qm "F2: local-only add"

  new_repo "$WS/f3fix-shokunin"
  write_file "$WS/f3fix-shokunin/tracked.txt" "kotodama-shaped tracked file"
  gitq "$WS/f3fix-shokunin" add -A
  gitq "$WS/f3fix-shokunin" commit -qm "F3: base commit"
  add_remote "$WS/f3fix-shokunin" f3
  set_origin_head "$WS/f3fix-shokunin" master
  write_file "$WS/f3fix-shokunin/local-only.txt" "one unpushed commit"
  gitq "$WS/f3fix-shokunin" add -A
  gitq "$WS/f3fix-shokunin" commit -qm "F3: unpushed local commit"
  write_file "$WS/f3fix-shokunin/dirty.txt" "one dirty entry"

  new_repo "$WS/f9fix-shokunin"
  write_file "$WS/f9fix-shokunin/target-f9.txt" "f9 pushed payload"
  gitq "$WS/f9fix-shokunin" add -A
  gitq "$WS/f9fix-shokunin" commit -qm "F9: add pushed target"
  add_remote "$WS/f9fix-shokunin" f9
  # deliberately no set_origin_head: refs/remotes/origin/HEAD absent

  # F4: detached worktree, dir removed, no unique commits (lore-shaped)
  new_repo "$WS/f4fix-shokunin"
  add_remote "$WS/f4fix-shokunin" f4
  set_origin_head "$WS/f4fix-shokunin" master
  gitq "$WS/f4fix-shokunin" worktree add -q --detach "$MKT/wt/f4-wt-a" origin/master
  rm -rf "$MKT/wt/f4-wt-a"

  # F5: named branch worktree, dir removed, one unpushed commit (gd2d-shaped)
  new_repo "$WS/f5fix-shokunin"
  add_remote "$WS/f5fix-shokunin" f5
  set_origin_head "$WS/f5fix-shokunin" master
  gitq "$WS/f5fix-shokunin" worktree add -q -b wt-r98 "$MKT/wt/f5-wt-r98" master
  write_file "$MKT/wt/f5-wt-r98/wt-only.txt" "one unpushed commit in the worktree branch"
  gitq "$MKT/wt/f5-wt-r98" add -A
  gitq "$MKT/wt/f5-wt-r98" commit -qm "F5: unpushed worktree commit"
  rm -rf "$MKT/wt/f5-wt-r98"

  # F5b: named branch worktree, dir present, dirty, branch fully pushed
  new_repo "$WS/f5bfix-shokunin"
  add_remote "$WS/f5bfix-shokunin" f5b
  set_origin_head "$WS/f5bfix-shokunin" master
  gitq "$WS/f5bfix-shokunin" worktree add -q -b wt-clean "$MKT/wt/f5b-wt-clean" master
  gitq "$MKT/wt/f5b-wt-clean" push -q -u origin wt-clean
  write_file "$MKT/wt/f5b-wt-clean/dirty-file.txt" "dirty entry one"
  write_file "$MKT/wt/f5b-wt-clean/dirty-two.txt" "dirty entry two"

  # F6: ledger-matched file (untracked, so the promoted receipt cannot apply)
  write_file "$lane/notes/f6-keepme.md" "f6 retained note payload"
  mkdir -p "$MKT/vault"
  write_file "$MKT/vault/f6-keepme.md" "f6 retained note payload"
  local ssha vsha
  ssha="$(sha256sum "$lane/notes/f6-keepme.md" | awk '{print $1}')"
  vsha="$(sha256sum "$MKT/vault/f6-keepme.md" | awk '{print $1}')"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tfixture row\n' \
    "$lane/notes/f6-keepme.md" "$ssha" "$MKT/vault/f6-keepme.md" "$vsha" >> "$LEDGER"

  # F7: old scratch file, no references anywhere
  new_repo "$WS/f7fix-shokunin"
  add_remote "$WS/f7fix-shokunin" f7
  set_origin_head "$WS/f7fix-shokunin" master
  write_file "$WS/f7fix-shokunin/.scratch/f7-old-dump.out" "old scratch payload f7"
  age_file "$WS/f7fix-shokunin/.scratch/f7-old-dump.out" 3

  # F12: fresh scratch file (stale threshold must be honoured)
  write_file "$WS/f7fix-shokunin/.scratch/f12-fresh-dump.out" "fresh scratch payload f12"

  # F8: old scratch in a sibling lane; its basename appears only in the census
  new_repo "$WS/f8fix-shokunin"
  add_remote "$WS/f8fix-shokunin" f8
  set_origin_head "$WS/f8fix-shokunin" master
  write_file "$WS/f8fix-shokunin/.scratch/f8-keepme-dump.out" "old scratch payload f8"

  # F8c: old scratch inside the lane repo itself; basename only in its census
  write_file "$lane/.scratch/f8c-keepme-dump2.out" "old scratch payload f8c"
  age_file "$lane/.scratch/f8c-keepme-dump2.out" 3

  {
    printf 'basename\tverdict\tsource\n'
    printf 'f8-keepme-dump.out\tSAFE(stale)\tfixture census sample\n'
    printf 'f8c-keepme-dump2.out\tSAFE(stale)\tfixture census sample\n'
  } > "$lane/census/round-1/census.tsv"

  # F10 / R10: secrets-shaped fixture paths (dummy payloads, never read by this runner)
  new_repo "$WS/f10fix-shokunin"
  write_file "$WS/f10fix-shokunin/notes.env" "FIXTURE_DUMMY=1"
  write_file "$WS/f10fix-shokunin/my_secret_notes.txt" "fixture dummy"
  write_file "$WS/f10fix-shokunin/id_fixture_key" "fixture dummy"
  write_file "$WS/f10fix-shokunin/cert.pem" "fixture dummy"
}

ws_manifest() { # content hash of fixture files, excluding git internals
  ( cd "$WS" && find . -type f -not -path '*/.git/*' -not -name .git | LC_ALL=C sort | xargs -r sha256sum ) | sha256sum | awk '{print $1}'
}

# ---------------------------------------------------------------------------
# reference implementation (calibration baseline; test-only, written to mktemp)
# ---------------------------------------------------------------------------
write_reference() {
  local dest="$1"
  mkdir -p "$(dirname "$dest")"
  cat > "$dest" <<'SOUJI_REF_EOF'
#!/usr/bin/env bash
# reference implementation of tools/souji-verify.sh — seat S26 calibration
# baseline. Written by tests/runner-26.sh into a mktemp workspace and never
# installed. Blocks delimited by #Dn-BEGIN/#Dn-END are mutation anchors.
set -euo pipefail

SELF="${BASH_SOURCE[0]}"
SELF_DIR="$(cd "$(dirname "$SELF")" && pwd -P)"
LANE_ROOT="$(cd "$SELF_DIR/.." && pwd -P)"
SHOKUNIN_ROOT="${SHOKUNIN_ROOT:-$(cd "$LANE_ROOT/.." && pwd -P)}"
LEDGER="${SOUJI_LEDGER:-$LANE_ROOT/corpus/knowledge/obsidian-ledger.tsv}"

STALE_DAYS=1
JSON_MODE=0
SELFTEST=0
targets=()
VERDICT_VAL=""
RECEIPT_VAL=""
EVIDENCE_VAL=""

usage() {
  printf 'usage: %s [--selftest] [--stale-days N] [--json] <path>...\n' "$(basename "$SELF")" >&2
}

is_secret_path() {
#D4-BEGIN
  case "$(basename "$1")" in
    *.env|*credential*|*secret*|id_*|*.pem) return 0 ;;
  esac
  return 1
#D4-END
}

#D1-BEGIN
resolve_default_branch() {
  local repo="$1" b="" n="" cand=""
  b="$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
  case "$b" in origin/*) b="${b#origin/}" ;; esac
  if [ -n "$b" ] && git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$b"; then
    printf '%s\n' "origin/$b"
    return 0
  fi
  n="$(git -C "$repo" for-each-ref --format='%(refname:short)' refs/remotes/origin 2>/dev/null | grep -vc '^origin/HEAD$' || true)"
  if [ "$n" -eq 1 ]; then
    cand="$(git -C "$repo" for-each-ref --format='%(refname:short)' refs/remotes/origin 2>/dev/null | grep -v '^origin/HEAD$' | head -n 1)"
    printf '%s\n' "$cand"
    return 0
  fi
  if git -C "$repo" show-ref --verify --quiet refs/heads/master; then
    printf '%s\n' "refs/heads/master"
    return 0
  fi
  return 1
}
#D1-END

count_refs() {
  local name="$1" n=""
  n="$(cd "$SHOKUNIN_ROOT" && { rg -l --no-ignore --fixed-strings -- "$name" . \
#D3-BEGIN
        -g '!.git' -g '!souji-shokunin/census/**' -g '!souji-shokunin/tests/**' -g '!**/.ufo-quarantine/**' \
#D3-END
        2>/dev/null || true; } | wc -l)"
  printf '%s\n' "$n"
}

worktree_owner() {
  local p="$1" d="" w="" owner="" line=""
  for d in "$SHOKUNIN_ROOT"/*-shokunin "$SHOKUNIN_ROOT"; do
    { [ -d "$d/.git" ] || [ -f "$d/.git" ]; } || continue
    w=""
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        worktree\ *) w="${line#worktree }" ;;
        '') if [ -n "$w" ] && [ "$w" = "$p" ]; then owner="$d"; fi ;;
      esac
      [ -n "$owner" ] && break
    done < <(git -C "$d" worktree list --porcelain 2>/dev/null; printf '\n')
    [ -n "$owner" ] && break
  done
  [ -n "$owner" ] || return 1
  printf '%s\n' "$owner"
}

is_scratch_type() {
  case "$1" in */.scratch/*|*/.scratch) return 0 ;; esac
  case "$(basename "$1")" in *.out|*.log|*-draft.*|*checkpoint*.json|*checkpoint*.png) return 0 ;; esac
  return 1
}

is_older_than_days() {
  local mt now
  mt="$(stat -c %Y "$1" 2>/dev/null || printf '0')"
  now="$(date +%s)"
  [ "$(( now - mt ))" -gt "$(( STALE_DAYS * 86400 ))" ]
}

ledger_match() {
  local p="$1" src_sha="" f1="" f2="" f3="" f4="" vsha=""
  [ -f "$LEDGER" ] || return 1
  src_sha="$(sha256sum "$p" 2>/dev/null | awk '{print $1}' || true)"
  [ -n "$src_sha" ] || return 1
  while IFS=$'\t' read -r f1 f2 f3 f4 _rest; do
    [ "$f1" = "$p" ] || continue
    [ "$f2" = "$src_sha" ] || continue
    [ -f "$f3" ] || continue
    vsha="$(sha256sum "$f3" 2>/dev/null | awk '{print $1}' || true)"
    [ -n "$vsha" ] && [ "$f4" = "$vsha" ] || continue
    printf '%s\n' "ledger-row vault=$f3 vault-sha=$vsha"
    return 0
  done < "$LEDGER"
  return 1
}

verdict() { VERDICT_VAL="$1"; RECEIPT_VAL="$2"; EVIDENCE_VAL="$3"; }

emit() {
  if [ "$JSON_MODE" -eq 1 ]; then
    python3 -c 'import json,sys; print(json.dumps({"path":sys.argv[1],"verdict":sys.argv[2],"receipt":sys.argv[3],"evidence":sys.argv[4]}))' \
      "$1" "$VERDICT_VAL" "$RECEIPT_VAL" "$EVIDENCE_VAL"
  else
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$1" "$VERDICT_VAL" "$RECEIPT_VAL" "$EVIDENCE_VAL"
  fi
}

repo_root_verdict() {
  local p="$1" ev="" unpushed="" dirty=""
  if ev="$(ledger_match "$p")"; then verdict SAFE moved-to-obsidian "$ev"; return 0; fi
  unpushed="$(git -C "$p" log --branches --not --remotes --oneline 2>/dev/null | wc -l)"
  dirty="$(git -C "$p" status --porcelain 2>/dev/null | wc -l)"
  verdict NOT-SAFE none "unpushed=$unpushed dirty=$dirty"
}

worktree_verdict() {
  local p="$1" owner="$2" block="" head="" branch="" unique=0 unpushed=0 dirty=0
  block="$(git -C "$owner" worktree list --porcelain 2>/dev/null | awk -v t="$p" '
    $1 == "worktree" { cur = substr($0, 10) }
    cur == t { print }')"
  head="$(printf '%s\n' "$block" | awk '$1 == "HEAD" { print $2 }')"
  branch="$(printf '%s\n' "$block" | awk '$1 == "branch" { print $2 }')"
  if [ -n "$branch" ]; then
    unpushed="$(git -C "$owner" log --oneline "$branch" --not --remotes 2>/dev/null | wc -l)"
    if [ "$unpushed" -gt 0 ]; then
      verdict NOT-SAFE unpushed-branch "owner=$owner branch=$branch unpushed=$unpushed"
      return 0
    fi
  fi
  if [ ! -d "$p" ]; then
    unique="$(git -C "$owner" log --oneline "$head" --not --all 2>/dev/null | wc -l)"
    if [ "$unique" -eq 0 ]; then
      verdict SAFE metadata-prune "owner=$owner head=${head:0:12} dir=absent unique=0"
      return 0
    fi
    verdict NOT-SAFE unpushed-branch "owner=$owner head=${head:0:12} dir=absent unique=$unique"
    return 0
  fi
  dirty="$(git -C "$p" status --porcelain 2>/dev/null | wc -l)"
  if [ "$dirty" -gt 0 ]; then
    verdict NOT-SAFE dirty "owner=$owner dir=present dirty=$dirty"
    return 0
  fi
  verdict SAFE metadata-prune "owner=$owner dir=present dirty=0"
}

file_verdict() {
  local p="$1" dir="" repo="" c="" ref="" ev="" refs=0
  if [ -z "$p" ]; then verdict NOT-SAFE unreachable "empty-target"; return 0; fi
  if [ ! -e "$p" ]; then verdict NOT-SAFE unreachable "no-such-path"; return 0; fi
  if [ -d "$p" ]; then dir="$p"; else dir="$(dirname "$p")"; fi
  repo="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null || true)"
  if [ -n "$repo" ]; then
    c="$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$p" 2>/dev/null || true)"
    if [ -n "$c" ]; then
      if ! ref="$(resolve_default_branch "$repo")"; then
        verdict NOT-SAFE pushed-unverifiable "commit=${c:0:12} default-branch-unresolved"
        return 0
      fi
      if git -C "$repo" merge-base --is-ancestor "$c" "$ref" 2>/dev/null; then
        verdict SAFE pushed "commit=${c:0:12} ref=$ref"
        return 0
      fi
      ev="commit=${c:0:12} not-ancestor-of=$ref"
    fi
  fi
  if ev="$(ledger_match "$p")"; then verdict SAFE moved-to-obsidian "$ev"; return 0; fi
  if is_scratch_type "$p"; then
    refs="$(count_refs "$(basename "$p")")"
    if [ "$refs" -eq 0 ] && is_older_than_days "$p"; then
      verdict SAFE stale "refs=0 mtime-days-old=$(( ( $(date +%s) - $(stat -c %Y "$p") ) / 86400 ))"
      return 0
    fi
  fi
  verdict NOT-SAFE none "${ev:-no-receipt}"
}

evaluate() {
  local p="$1" owner=""
  if is_secret_path "$p"; then verdict NOT-SAFE secrets-refusal "refused-without-read"; return 0; fi
  if [ -z "$p" ]; then verdict NOT-SAFE unreachable "empty-target"; return 0; fi
  if owner="$(worktree_owner "$p")"; then
#D2-BEGIN
    worktree_verdict "$p" "$owner"
#D2-END
    return 0
  fi
  if [ -d "$p" ] && [ -d "$p/.git" ]; then repo_root_verdict "$p"; return 0; fi
  file_verdict "$p"
}

# ---------------------------------------------------------------------------
# selftest (own fixture set; mirrors the spec F1-F10 cases)
# ---------------------------------------------------------------------------
ref_selftest() {
  local tmp rc=0
  tmp="$(mktemp -d)"
  ref_selftest_build "$tmp" || { rm -rf "$tmp"; return 1; }
  local ws="$tmp/ws" led="$tmp/ws/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv"
  local id="" want="" got="" args=""
  for id in F1 F2 F3 F4 F5 F6 F7 F8 F9 F10; do
    case "$id" in
      F1) want="SAFE pushed";        args="$ws/f1fix-shokunin/target-f1.txt" ;;
      F2) want="NOT-SAFE none";      args="$ws/f2fix-shokunin/target-f2.txt" ;;
      F3) want="NOT-SAFE none";      args="$ws/f3fix-shokunin" ;;
      F4) want="SAFE metadata-prune"; args="$tmp/wt/f4-wt-a" ;;
      F5) want="NOT-SAFE unpushed-branch"; args="$tmp/wt/f5-wt-r98" ;;
      F6) want="SAFE moved-to-obsidian"; args="$ws/souji-shokunin/notes/f6-keepme.md" ;;
      F7) want="SAFE stale";         args="$ws/f7fix-shokunin/.scratch/f7-old-dump.out" ;;
      F8) want="SAFE stale";         args="$tmp/nocase" ;;
      F9) want="SAFE pushed";        args="$ws/f9fix-shokunin/target-f9.txt" ;;
      F10) want="NOT-SAFE secrets-refusal"; args="$ws/f10fix-shokunin/notes.env" ;;
    esac
    if [ "$id" = "F2" ]; then want="NOT-SAFE none|pushed-unverifiable"; fi
    if [ "$id" = "F8" ]; then
      args="$ws/f8fix-shokunin/.scratch/f8-keepme-dump.out"
    fi
    got="$(env SHOKUNIN_ROOT="$ws" SOUJI_LEDGER="$led" bash "$SELF_PATH" $args 2>/dev/null | head -n 1 || true)"
    local gv="" gr=""
    IFS=$'\t' read -r _g1 _g2 gv gr _g5 <<< "$got" || true
    got="${gv} ${gr}"
    if [ "$id" = "F3" ] || [ "$id" = "F2" ]; then
      if [ "$gv" = "NOT-SAFE" ]; then
        printf 'selftest PASS %s (NOT-SAFE)\n' "$id" >&2
      else
        printf 'selftest FAIL %s want=%s got=%s\n' "$id" "$want" "$got" >&2
        rc=1
      fi
      continue
    fi
    case "$want" in
      *"|"*) if case "$want" in *"$gr"*) true ;; *) false ;; esac; then
               printf 'selftest PASS %s\n' "$id" >&2
             else
               printf 'selftest FAIL %s want=%s got=%s\n' "$id" "$want" "$got" >&2
               rc=1
             fi ;;
      *) if [ "$gv $gr" = "$want" ]; then
           printf 'selftest PASS %s\n' "$id" >&2
         else
           printf 'selftest FAIL %s want=%s got=%s\n' "$id" "$want" "$got" >&2
           rc=1
         fi ;;
    esac
  done
  rm -rf "$tmp"
  return "$rc"
}

ref_selftest_build() {
  local tmp="$1" ws="$1/ws" lane="$1/ws/souji-shokunin" led="$1/ws/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv"
  mkdir -p "$ws" "$lane/tools" "$lane/corpus/knowledge" "$lane/census/round-1" "$lane/notes" "$tmp/vault" "$tmp/wt"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$led"
  gq() { git -C "$1" "${@:2}"; }
  refrepo() { mkdir -p "$(dirname "$1")"; gq "$(dirname "$1")" init -q -b master "$1"; printf 'seed\n' > "$1/seed.txt"; gq "$1" add -A; gq "$1" commit -qm seed; }
  refremote() { gq "$tmp" init -q --bare "$tmp/$2.git"; gq "$1" remote add origin "$tmp/$2.git"; gq "$1" push -q -u origin master; }
  refrepo "$ws/f1fix-shokunin"; printf 'x\n' > "$ws/f1fix-shokunin/target-f1.txt"; gq "$ws/f1fix-shokunin" add -A; gq "$ws/f1fix-shokunin" commit -qm f1; refremote "$ws/f1fix-shokunin" f1; gq "$ws/f1fix-shokunin" remote set-head origin master
  refrepo "$ws/f2fix-shokunin"; refremote "$ws/f2fix-shokunin" f2; gq "$ws/f2fix-shokunin" remote set-head origin master; printf 'x\n' > "$ws/f2fix-shokunin/target-f2.txt"; gq "$ws/f2fix-shokunin" add -A; gq "$ws/f2fix-shokunin" commit -qm f2
  refrepo "$ws/f3fix-shokunin"; refremote "$ws/f3fix-shokunin" f3; gq "$ws/f3fix-shokunin" remote set-head origin master; printf 'x\n' > "$ws/f3fix-shokunin/tracked.txt"; gq "$ws/f3fix-shokunin" add -A; gq "$ws/f3fix-shokunin" commit -qm f3; printf 'y\n' > "$ws/f3fix-shokunin/dirty.txt"
  refrepo "$ws/f4fix-shokunin"; refremote "$ws/f4fix-shokunin" f4; gq "$ws/f4fix-shokunin" remote set-head origin master; gq "$ws/f4fix-shokunin" worktree add -q --detach "$tmp/wt/f4-wt-a" origin/master; rm -rf "$tmp/wt/f4-wt-a"
  refrepo "$ws/f5fix-shokunin"; refremote "$ws/f5fix-shokunin" f5; gq "$ws/f5fix-shokunin" remote set-head origin master; gq "$ws/f5fix-shokunin" worktree add -q -b wt-r98 "$tmp/wt/f5-wt-r98" master; printf 'z\n' > "$tmp/wt/f5-wt-r98/a.txt"; gq "$tmp/wt/f5-wt-r98" add -A; gq "$tmp/wt/f5-wt-r98" commit -qm f5; rm -rf "$tmp/wt/f5-wt-r98"
  printf 'f6\n' > "$lane/notes/f6-keepme.md"; printf 'f6\n' > "$tmp/vault/f6-keepme.md"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tfixture\n' "$lane/notes/f6-keepme.md" "$(sha256sum "$lane/notes/f6-keepme.md" | awk '{print $1}')" "$tmp/vault/f6-keepme.md" "$(sha256sum "$tmp/vault/f6-keepme.md" | awk '{print $1}')" >> "$led"
  refrepo "$ws/f7fix-shokunin"; refremote "$ws/f7fix-shokunin" f7; gq "$ws/f7fix-shokunin" remote set-head origin master; mkdir -p "$ws/f7fix-shokunin/.scratch"; printf 'old\n' > "$ws/f7fix-shokunin/.scratch/f7-old-dump.out"; touch -d "@$(( $(date +%s) - 259200 ))" "$ws/f7fix-shokunin/.scratch/f7-old-dump.out"
  refrepo "$ws/f8fix-shokunin"; refremote "$ws/f8fix-shokunin" f8; gq "$ws/f8fix-shokunin" remote set-head origin master; mkdir -p "$ws/f8fix-shokunin/.scratch"; printf 'old\n' > "$ws/f8fix-shokunin/.scratch/f8-keepme-dump.out"; touch -d "@$(( $(date +%s) - 259200 ))" "$ws/f8fix-shokunin/.scratch/f8-keepme-dump.out"; printf 'f8-keepme-dump.out\n' > "$lane/census/round-1/census.tsv"
  refrepo "$ws/f9fix-shokunin"; printf 'x\n' > "$ws/f9fix-shokunin/target-f9.txt"; gq "$ws/f9fix-shokunin" add -A; gq "$ws/f9fix-shokunin" commit -qm f9; refremote "$ws/f9fix-shokunin" f9
  refrepo "$ws/f10fix-shokunin"; printf 'FIXTURE_DUMMY=1\n' > "$ws/f10fix-shokunin/notes.env"
  return 0
}

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --stale-days)
      [ "$#" -ge 2 ] || { usage; exit 2; }
      STALE_DAYS="$2"; shift 2 ;;
    --json) JSON_MODE=1; shift ;;
    -h|--help) usage; exit 2 ;;
    --*) usage; exit 2 ;;
    *) targets=("$@"); break ;;
  esac
done

case "$STALE_DAYS" in ''|*[!0-9]*) usage; exit 2 ;; esac

SELF_PATH="$SELF_DIR/$(basename "$SELF")"
if [ "$SELFTEST" -eq 1 ]; then
  ref_selftest
  exit $?
fi
if [ "${#targets[@]}" -eq 0 ]; then usage; exit 2; fi
for t in "${targets[@]}"; do evaluate "$t"; emit "$t"; done
exit 0
SOUJI_REF_EOF
  chmod +x "$dest"
}

# ---------------------------------------------------------------------------
# case suite
# ---------------------------------------------------------------------------
norm() { printf '%s' "$1" | sed "s|$MKT|<TMP>|g" | tr '\t\n' '  '; }

claim_vars_reset() { VERDICT_OBS=""; RECEIPT_OBS=""; EVIDENCE_OBS=""; RC_OBS=""; CMD_OBS=""; }

norm_receipt() {
  local r="$1"
  r="${r#SAFE(}"; r="${r#NOT-SAFE(}"; r="${r%)}"
  printf '%s' "$r"
}

# run_tool <tool> <extra args...> -- <target>  : stdout in OUT_RAW, rc in RC_RAW
run_tool() {
  local tool="$1"; shift
  local err="$MKT/stderr/last"
  set +e
  OUT_RAW="$(cd "$WS/souji-shokunin" && env SHOKUNIN_ROOT="$WS" SOUJI_LEDGER="$LEDGER" HOME="$MKT/home" \
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null bash "$tool" "$@" 2>"$err")"
  RC_RAW=$?
  set -e
  ERR_RAW="$(cat "$err")"
}

# suite_case <impl> <tool> <id> <expect_verdict> <expect_receipts|*> <ev_regex|-> <expect_rc> <target> [tool flags...]
suite_case() {
  local impl="$1" tool="$2" id="$3" ev_verdict="$4" ev_receipts="$5" ev_regex="$6" ev_rc="$7" target="$8"; shift 8
  local why="" status="pass" cmd=""
  cmd="$(norm "bash $(basename "$tool") $* $target")"
  run_tool "$tool" "$@" "$target"
  local line f1 f2 f3 f4 f5
  line="$(printf '%s\n' "$OUT_RAW" | head -n 1)"
  IFS=$'\t' read -r f1 f2 f3 f4 f5 <<< "$line" || true
  local receipt; receipt="$(norm_receipt "${f4:-}")"
  [ "$RC_RAW" = "$ev_rc" ] || why="$why rc=$RC_RAW(want $ev_rc);"
  [ "$f1" = "VERDICT" ] || why="$why field1=${f1:-empty};"
  [ "$f2" = "$target" ] || why="$why field2=${f2:-empty};"
  [ "$f3" = "$ev_verdict" ] || why="$why verdict=${f3:-empty}(want $ev_verdict);"
  case "|$ev_receipts|" in
    *"|$receipt|"*) ;;
    *) why="$why receipt=${receipt:-empty}(want $ev_receipts);" ;;
  esac
  if [ "$ev_regex" != "-" ]; then
    printf '%s' "${f5:-}" | grep -Eq -- "$ev_regex" || why="$why evidence-missing($ev_regex);"
  fi
  [ -n "${f5:-}" ] || why="$why evidence-empty;"
  [ -z "$why" ] || status="fail"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "case" "$impl" "$id" "$ev_verdict($ev_receipts)" "$(printf '%s(%s)' "${f3:-rc=$RC_RAW}" "$receipt")" \
    "$status" "$RC_RAW" "$cmd" "$(norm "$why")" >> "$RECORDS"
}

suite_rc_case() { # <impl> <tool> <id> <expect_rc> <label> [args...]
  local impl="$1" tool="$2" id="$3" ev_rc="$4" label="$5"; shift 5
  local why="" status="pass" obs=""
  run_tool "$tool" "$@"
  [ "$RC_RAW" = "$ev_rc" ] || why="rc=$RC_RAW(want $ev_rc);"
  if [ "$ev_rc" = "2" ]; then
    [ -n "$ERR_RAW$OUT_RAW" ] || why="$why no-usage-output;"
  fi
  [ -z "$why" ] || status="fail"
  obs="rc=$RC_RAW"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "case" "$impl" "$id" "rc=$ev_rc $label" "$obs" "$status" "$RC_RAW" \
    "$(norm "bash $(basename "$tool") $*")" "$(norm "$why")" >> "$RECORDS"
}

case_shape() { # <impl> <tool> <id> <target>  — format contract on a 5-field line
  local impl="$1" tool="$2" id="$3" target="$4"
  local why="" status="pass" line nf f1 f2 f3 f5
  run_tool "$tool" "$target"
  line="$(printf '%s\n' "$OUT_RAW" | head -n 1)"
  nf="$(printf '%s' "$line" | awk -F'\t' '{print NF}')"
  IFS=$'\t' read -r f1 f2 f3 _ f5 <<< "$line" || true
  [ "$nf" -ge 5 ] || why="$why fields=$nf(want>=5);"
  [ "$f1" = "VERDICT" ] || why="$why field1=${f1:-empty};"
  [ "$f2" = "$target" ] || why="$why field2-mismatch;"
  [ -n "${f5:-}" ] || why="$why evidence-empty;"
  [ "$RC_RAW" = "0" ] || why="$why rc=$RC_RAW;"
  [ -z "$why" ] || status="fail"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "case" "$impl" "$id" "5-field line, exit 0" "fields=$nf verdict=${f3:-empty}" "$status" "$RC_RAW" \
    "$(norm "bash $(basename "$tool") $target")" "$(norm "$why")" >> "$RECORDS"
}

case_json() { # <impl> <tool> <id> <target>  — --json emits parseable JSON with the verdict
  local impl="$1" tool="$2" id="$3" target="$4"
  local why="" status="pass" parsed=""
  run_tool "$tool" --json "$target"
  if [ "$RC_RAW" != "0" ]; then why="rc=$RC_RAW;"; fi
  parsed="$(printf '%s\n' "$OUT_RAW" | python3 -c '
import json, sys
ok = 0
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        json.loads(line)
        ok += 1
    except Exception:
        print("parse-error"); sys.exit(0)
print("ok:%d" % ok)
' 2>/dev/null || printf 'parse-error')"
  [ "$parsed" = "ok:1" ] || why="$why json=$parsed;"
  printf '%s' "$OUT_RAW" | grep -q 'SAFE' || why="$why no-verdict-in-json;"
  printf '%s' "$OUT_RAW" | grep -q 'stale' || why="$why no-receipt-in-json;"
  [ -z "$why" ] || status="fail"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "case" "$impl" "$id" "--json: 1 parseable JSON line with verdict+receipt" "$parsed" "$status" "$RC_RAW" \
    "$(norm "bash $(basename "$tool") --json $target")" "$(norm "$why")" >> "$RECORDS"
}

case_multi() { # <impl> <tool> <id>  — two targets, one line each, order preserved
  local impl="$1" tool="$2" id="$3"
  local t1="$WS/f7fix-shokunin/.scratch/f7-old-dump.out" t2="$WS/f7fix-shokunin/.scratch/f12-fresh-dump.out"
  local why="" status="pass" n=0 v1="" v2="" r1="" r2=""
  run_tool "$tool" "$t1" "$t2"
  n="$(printf '%s\n' "$OUT_RAW" | grep -c '^VERDICT' || true)"
  [ "$n" = "2" ] || why="$why lines=$n(want 2);"
  IFS=$'\t' read -r _ _ v1 r1 _ <<< "$(printf '%s\n' "$OUT_RAW" | sed -n 1p)" || true
  IFS=$'\t' read -r _ _ v2 r2 _ <<< "$(printf '%s\n' "$OUT_RAW" | sed -n 2p)" || true
  [ "$v1" = "SAFE" ] && [ "$(norm_receipt "${r1:-}")" = "stale" ] || why="$why line1=$v1/${r1:-empty};"
  [ "$v2" = "NOT-SAFE" ] || why="$why line2=$v2/${r2:-empty};"
  [ -z "$why" ] || status="fail"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "case" "$impl" "$id" "2 targets -> SAFE(stale) + NOT-SAFE" "lines=$n v1=$v1/${r1:-} v2=$v2/${r2:-}" \
    "$status" "$RC_RAW" "$(norm "bash $(basename "$tool") <t1> <t2>")" "$(norm "$why")" >> "$RECORDS"
}

case_ambiguous_zero_targets() { # spec is ambiguous: usage(2) or NOT-SAFE(unreachable)(0)
  local impl="$1" tool="$2" id="$3"
  local why="" status="pass" note=""
  run_tool "$tool"
  if [ "$RC_RAW" = "2" ]; then
    note="rc=2 usage"
  elif [ "$RC_RAW" = "0" ] && printf '%s' "$OUT_RAW" | grep -q 'NOT-SAFE'; then
    note="rc=0 NOT-SAFE(unreachable)"
  else
    why="rc=$RC_RAW out=$(norm "$OUT_RAW");"
    status="fail"
    note="rc=$RC_RAW"
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "case" "$impl" "$id" "zero targets: exit 2 usage, or NOT-SAFE(unreachable) exit 0 (spec ambiguity)" \
    "$note" "$status" "$RC_RAW" "$(norm "bash $(basename "$tool")")" "$(norm "$why")" >> "$RECORDS"
}

run_suite() { # <impl label> <tool path>
  local impl="$1" tool="$2" t=""
  local f1t="$WS/f1fix-shokunin/target-f1.txt"
  local f7t="$WS/f7fix-shokunin/.scratch/f7-old-dump.out"
  suite_case "$impl" "$tool" F1 SAFE "pushed" - 0 "$f1t"
  suite_case "$impl" "$tool" F2 NOT-SAFE "none|pushed-unverifiable" - 0 "$WS/f2fix-shokunin/target-f2.txt"
  suite_case "$impl" "$tool" F3 NOT-SAFE "*" "unpushed=1.*dirty=1|dirty=1.*unpushed=1" 0 "$WS/f3fix-shokunin"
  suite_case "$impl" "$tool" F4 SAFE "metadata-prune" - 0 "$MKT/wt/f4-wt-a"
  suite_case "$impl" "$tool" F5 NOT-SAFE "unpushed-branch" - 0 "$MKT/wt/f5-wt-r98"
  suite_case "$impl" "$tool" F5b NOT-SAFE "dirty|none" "dirty=1" 0 "$MKT/wt/f5b-wt-clean"
  suite_case "$impl" "$tool" F6 SAFE "moved-to-obsidian" - 0 "$WS/souji-shokunin/notes/f6-keepme.md"
  suite_case "$impl" "$tool" F7 SAFE "stale" - 0 "$f7t"
  suite_case "$impl" "$tool" F8 SAFE "stale" - 0 "$WS/f8fix-shokunin/.scratch/f8-keepme-dump.out"
  suite_case "$impl" "$tool" F8c SAFE "stale" - 0 "$WS/souji-shokunin/.scratch/f8c-keepme-dump2.out"
  suite_case "$impl" "$tool" F9 SAFE "pushed" - 0 "$WS/f9fix-shokunin/target-f9.txt"
  suite_case "$impl" "$tool" F10 NOT-SAFE "secrets-refusal" - 0 "$WS/f10fix-shokunin/notes.env"
  suite_case "$impl" "$tool" R3 NOT-SAFE "unreachable" - 0 "$WS/does-not-exist-anywhere"
  suite_case "$impl" "$tool" R3b NOT-SAFE "unreachable" - 0 ""
  suite_case "$impl" "$tool" R10b NOT-SAFE "secrets-refusal" - 0 "$WS/f10fix-shokunin/my_secret_notes.txt"
  suite_case "$impl" "$tool" R10c NOT-SAFE "secrets-refusal" - 0 "$WS/f10fix-shokunin/id_fixture_key"
  suite_case "$impl" "$tool" R10d NOT-SAFE "secrets-refusal" - 0 "$WS/f10fix-shokunin/cert.pem"
  suite_case "$impl" "$tool" R12 NOT-SAFE "*" - 0 "$WS/f7fix-shokunin/.scratch/f12-fresh-dump.out"
  suite_case "$impl" "$tool" R12c NOT-SAFE "*" - 0 --stale-days 10 "$f7t"
  case_shape "$impl" "$tool" R4 "$f7t"
  case_json "$impl" "$tool" R5 "$f7t"
  case_multi "$impl" "$tool" R11
  suite_rc_case "$impl" "$tool" R13 2 "--stale-days abc" --stale-days abc "$f7t"
  suite_rc_case "$impl" "$tool" R15 2 "unknown flag" --bogus "$f7t"
  case_ambiguous_zero_targets "$impl" "$tool" R14
}

# ---------------------------------------------------------------------------
# mutations (block replacement between #Dn-BEGIN / #Dn-END markers)
# ---------------------------------------------------------------------------
write_mutator() {
  mkdir -p "$MKT/mutants"
  cat > "$MKT/mutate.py" <<'MUT_EOF'
import pathlib, re, sys

MUTATIONS = {
    "M-D1": ("D1", '''resolve_default_branch() {
  printf '%s\\n' "origin/main"
  return 0
}'''),
    "M-D2": ("D2", ''': # worktree-registration kind disabled (D2 defect)'''),
    "M-D3": ("D3", '''        -g '!.git' \\\\'''),
    "M-D4": ("D4", '''  return 1'''),
}

src = pathlib.Path(sys.argv[1]).read_text()
mid = sys.argv[2]
out = pathlib.Path(sys.argv[3])
tag, repl = MUTATIONS[mid]
pat = re.compile(r"(?m)^#%s-BEGIN\n(.*?)^#%s-END\n" % (tag, tag), re.S)
if not pat.search(src):
    print("anchor-missing")
    sys.exit(1)
mutated, n = pat.subn(lambda m: "#%s-BEGIN\n%s\n#%s-END\n" % (tag, repl, tag), src)
# keep the runner's own marker lines intact; replacement text has no markers
if n != 1:
    print("anchor-count:%d" % n)
    sys.exit(1)
out.write_text(mutated)
print("applied")
MUT_EOF
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
printf 'fixture workspace: %s\n' "$MKT"
build_fixtures
WS_SHA_BEFORE="$(ws_manifest)"

write_reference "$MKT/ref/souji-verify.sh"
REF="$MKT/ref/souji-verify.sh"
cp "$REF" "$WS/souji-shokunin/tools/souji-verify.sh"
chmod +x "$WS/souji-shokunin/tools/souji-verify.sh"

# positive control: the reference passes its own selftest
set +e
bash "$REF" --selftest >"$MKT/ref-selftest.log" 2>&1
REF_ST_EXIT=$?
set -e
REF_ST_PASS="$(grep -c '^selftest PASS' "$MKT/ref-selftest.log" || true)"
REF_ST_FAIL="$(grep -c '^selftest FAIL' "$MKT/ref-selftest.log" || true)"

# positive control: the reference passes every case
run_suite reference "$REF"

# negative controls: four defective mutants must be caught
write_mutator
MUTANT_IDS="M-D1 M-D2 M-D3 M-D4"
MUT_SUMMARY=""
for mid in $MUTANT_IDS; do
  if python3 "$MKT/mutate.py" "$REF" "$mid" "$MKT/mutants/$mid.sh" > "$MKT/mutants/$mid.apply" 2>&1; then
    cp "$MKT/mutants/$mid.sh" "$WS/souji-shokunin/tools/souji-verify.sh"
    chmod +x "$WS/souji-shokunin/tools/souji-verify.sh"
    run_suite "$mid" "$MKT/mutants/$mid.sh"
    printf 'mutant\t%s\t%s\tapplied\n' "$mid" "$(cat "$MKT/mutants/$mid.apply")" >> "$META"
  else
    printf 'mutant\t%s\t%s\tapply-failed\n' "$mid" "$(cat "$MKT/mutants/$mid.apply" 2>/dev/null || true)" >> "$META"
  fi
done

# reinstall the reference copy (tool under test evaluation copies its own)
cp "$REF" "$WS/souji-shokunin/tools/souji-verify.sh"

# the tool under test
TOOL_PRESENT=0
TOOL_SHA=""
TOOL_ST_EXIT=""
TOOL_EXEC=0
if [ -f "$TOOL" ]; then
  TOOL_PRESENT=1
  TOOL_SHA="$(sha256sum "$TOOL" | awk '{print $1}')"
  [ -x "$TOOL" ] && TOOL_EXEC=1 || TOOL_EXEC=0
  cp "$TOOL" "$WS/souji-shokunin/tools/souji-verify.sh"
  chmod +x "$WS/souji-shokunin/tools/souji-verify.sh"
  set +e
  ( cd "$REPO" && timeout 180 bash "$TOOL" --selftest ) >"$MKT/tool-selftest.log" 2>&1
  TOOL_ST_EXIT=$?
  set -e
  run_suite tool "$WS/souji-shokunin/tools/souji-verify.sh"
fi

WS_SHA_AFTER="$(ws_manifest)"
LEDGER_SHA="$(sha256sum "$LEDGER" | awk '{print $1}')"
if [ "$TOOL_PRESENT" -eq 1 ]; then
  TOOL_SHA_AFTER="$(sha256sum "$TOOL" | awk '{print $1}')"
else
  TOOL_SHA_AFTER=""
fi

{
  printf 'meta\tseat\tS26\n'
  printf 'meta\tround\t2\n'
  printf 'meta\trunner\ttests/runner-26.sh\n'
  printf 'meta\tgenerated_at\t%s\n' "$(date -Is)"
  printf 'meta\tspec\ttools/souji-verify.spec.md\n'
  printf 'meta\tgit_version\t%s\n' "$(git --version)"
  printf 'meta\trg_version\t%s\n' "$(rg --version | head -n 1)"
  printf 'meta\tpython3_version\t%s\n' "$(python3 --version 2>&1)"
  printf 'meta\trg_basename_flag\tabsent (rg 15.2.0 has no --basename; sweep = content search)\n'
  printf 'meta\tstale_days_default\t1\n'
  printf 'meta\tisolation\tmktemp -d workspace; git mutations fixture-only; tool runs with SHOKUNIN_ROOT + SOUJI_LEDGER + HOME + git config overrides\n'
  printf 'meta\tws_sha_before\t%s\n' "$WS_SHA_BEFORE"
  printf 'meta\tws_sha_after\t%s\n' "$WS_SHA_AFTER"
  printf 'meta\tws_untouched\t%s\n' "$([ "$WS_SHA_BEFORE" = "$WS_SHA_AFTER" ] && printf true || printf false)"
  printf 'meta\tfixture_ledger_sha\t%s\n' "$LEDGER_SHA"
  printf 'meta\treference_selftest_exit\t%s\n' "$REF_ST_EXIT"
  printf 'meta\treference_selftest_pass\t%s\n' "$REF_ST_PASS"
  printf 'meta\treference_selftest_fail\t%s\n' "$REF_ST_FAIL"
  printf 'meta\ttool_path\ttools/souji-verify.sh\n'
  printf 'meta\ttool_present\t%s\n' "$TOOL_PRESENT"
  printf 'meta\ttool_sha256\t%s\n' "$TOOL_SHA"
  printf 'meta\ttool_sha256_after\t%s\n' "$TOOL_SHA_AFTER"
  printf 'meta\ttool_selftest_exit\t%s\n' "$TOOL_ST_EXIT"
  printf 'meta\ttool_executable\t%s\n' "$TOOL_EXEC"
  printf 'meta\tmkt\t%s\n' "$(norm "$MKT")"
} >> "$META"

run_suite_py() {
  python3 - "$RECORDS" "$META" "$OUT" <<'PY_EOF'
import json, sys
from collections import OrderedDict

records_path, meta_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

meta = OrderedDict()
for line in open(meta_path):
    line = line.rstrip("\n")
    if not line:
        continue
    parts = line.split("\t")
    if parts[0] == "meta":
        meta[parts[1]] = parts[2]
    elif parts[0] == "mutant":
        meta.setdefault("_mutant_apply", OrderedDict())[parts[1]] = parts[3]

cases = []
for line in open(records_path):
    line = line.rstrip("\n")
    if not line:
        continue
    kind, impl, cid, expected, observed, status, rc, cmd, why = line.split("\t")
    cases.append(OrderedDict([
        ("impl", impl), ("id", cid), ("expected", expected), ("observed", observed),
        ("status", status), ("exit_code", rc), ("command", cmd), ("failure", why),
    ]))

def group(impl):
    return [c for c in cases if c["impl"] == impl]

def stats(group_cases):
    passed = sum(1 for c in group_cases if c["status"] == "pass")
    failed = [c["id"] for c in group_cases if c["status"] != "pass"]
    false_safe = [c["id"] for c in group_cases
                  if c["expected"].startswith("NOT-SAFE") and c["observed"].startswith("SAFE")]
    return passed, failed, false_safe

ref_cases = group("reference")
ref_passed, ref_failed, ref_false_safe = stats(ref_cases)

EXPECTED_FLIPS = {
    "M-D1": (["F1", "F9"], "D1: default-branch resolution bypassed (hardcoded origin/main)"),
    "M-D2": (["F4", "F5", "F5b"], "D2: worktree-registration kind disabled"),
    "M-D3": (["F8", "F8c"], "D3: census/tests/quarantine sweep exclusions dropped"),
    "M-D4": (["F10", "R10b", "R10c", "R10d"], "D4: secrets refusal rail disabled"),
}
ref_fail_set = set(ref_failed)
mutants = []
for mid in ["M-D1", "M-D2", "M-D3", "M-D4"]:
    mcs = group(mid)
    want, desc = EXPECTED_FLIPS[mid]
    applied = meta.get("_mutant_apply", {}).get(mid) == "applied"
    if not mcs:
        mutants.append(OrderedDict([
            ("id", mid), ("defect", desc), ("applied", applied),
            ("expected_flips", want), ("observed_flips", []), ("unexpected_flips", []),
            ("detected", False),
        ]))
        continue
    failed = [c["id"] for c in mcs if c["status"] != "pass"]
    base_failed = set(ref_failed)
    flips = sorted(set(failed) - base_failed)
    unexpected = sorted(set(flips) - set(want))
    mutants.append(OrderedDict([
        ("id", mid), ("defect", desc), ("applied", applied),
        ("expected_flips", want), ("observed_flips", flips), ("unexpected_flips", unexpected),
        ("detected", applied and set(want) <= set(flips)),
    ]))

cal_ok = (not ref_failed) and all(m["detected"] for m in mutants) and meta.get("reference_selftest_exit") == "0"

tool_present = meta.get("tool_present") == "1"
tool_cases = group("tool")
tool_report = None
if tool_present:
    t_passed, t_failed, t_false_safe = stats(tool_cases)
    tool_report = OrderedDict([
        ("path", meta.get("tool_path")),
        ("sha256", meta.get("tool_sha256")),
        ("sha256_after", meta.get("tool_sha256_after")),
        ("unmodified_by_run", meta.get("tool_sha256") == meta.get("tool_sha256_after")),
        ("executable", meta.get("tool_executable") == "1"),
        ("selftest_exit", meta.get("tool_selftest_exit")),
        ("cases_total", len(tool_cases)),
        ("passed", t_passed), ("failed", t_failed), ("failed_ids", t_failed),
        ("false_safe", t_false_safe),
        ("verdict", "PASS" if not t_failed else "FAIL"),
    ])

findings = [
    "rg 15.2.0 on this host has no --basename flag; the spec's sweep command is unrunnable as written and any implementation must use a content-search equivalent (the reference uses rg -l --no-ignore -F).",
    "Sweep-root choice is untested by F8 vs F8c: F8 (census in a sibling lane) only exercises D3 for fleet-root sweeps, F8c (census in the target's own repo) exercises D3 for per-repo sweeps; the reference sweeps SHOKUNIN_ROOT, so M-D3 flips both.",
    "Zero-target invocation is ambiguous in the spec (usage exit 2 vs missing-target NOT-SAFE(unreachable) exit 0); R14 accepts either.",
    "Worktree ordering matters: F5 requires the named-branch-unpushed check before the dir-absent/unique=0 metadata-prune rule, else gd2d-shaped registrations would be mis-SAFEd.",
    "F2 accepts NOT-SAFE(none) or NOT-SAFE(pushed-unverifiable) per spec text.",
]

summary = OrderedDict([
    ("harness_calibrated", bool(cal_ok)),
    ("tool_verdict", tool_report["verdict"] if tool_report else "ABSENT"),
    ("tool_failed_ids", tool_report["failed_ids"] if tool_report else []),
    ("tool_false_safe", tool_report["false_safe"] if tool_report else []),
])

doc = OrderedDict([
    ("runner", "tests/runner-26.sh"),
    ("seat", "S26"),
    ("round", 2),
    ("generated_at", meta.get("generated_at")),
    ("spec", meta.get("spec")),
    ("environment", OrderedDict([
        ("git", meta.get("git_version")),
        ("rg", meta.get("rg_version")),
        ("python3", meta.get("python3_version")),
        ("rg_basename_flag", meta.get("rg_basename_flag")),
        ("stale_days_default", meta.get("stale_days_default")),
    ])),
    ("isolation", OrderedDict([
        ("workspace", meta.get("mkt")),
        ("mode", meta.get("isolation")),
        ("fixture_tree_sha_before", meta.get("ws_sha_before")),
        ("fixture_tree_sha_after", meta.get("ws_sha_after")),
        ("fixture_tree_untouched", meta.get("ws_untouched") == "true"),
        ("fixture_ledger_sha", meta.get("fixture_ledger_sha")),
    ])),
    ("calibration", OrderedDict([
        ("reference", OrderedDict([
            ("selftest_exit", meta.get("reference_selftest_exit")),
            ("selftest_pass", meta.get("reference_selftest_pass")),
            ("selftest_fail", meta.get("reference_selftest_fail")),
            ("cases_total", len(ref_cases)),
            ("passed", ref_passed), ("failed", ref_failed), ("false_safe", ref_false_safe),
        ])),
        ("mutants", mutants),
        ("verdict", "CALIBRATED" if cal_ok else "BROKEN"),
    ])),
    ("tool_under_test", tool_report),
    ("cases", OrderedDict([
        ("reference", ref_cases),
        ("mutants", OrderedDict((m["id"], group(m["id"])) for m in mutants)),
        ("tool", tool_cases),
    ])),
    ("findings", findings),
    ("summary", summary),
])

with open(out_path, "w") as fh:
    json.dump(doc, fh, indent=2, sort_keys=False)
    fh.write("\n")

print("harness_calibrated=%s reference=%d/%d failed=%s mutants_detected=%d/4 tool=%s" % (
    cal_ok, ref_passed, len(ref_cases), ref_failed,
    sum(1 for m in mutants if m["detected"]), summary["tool_verdict"]))
PY_EOF
}

mkdir -p "$(dirname "$OUT")"
run_suite_py

if [ "$TOOL_PRESENT" -eq 1 ]; then
  if grep -q '"tool_verdict": "PASS"' "$OUT"; then :; fi
fi

# final exit code: harness must be calibrated; a present tool must pass
CAL_OK="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print("yes" if d["calibration"]["verdict"]=="CALIBRATED" else "no")' "$OUT")"
TOOL_VERDICT="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["summary"]["tool_verdict"])' "$OUT")"
printf 'results: %s\n' "$OUT"
printf 'calibration: %s\n' "$CAL_OK"
printf 'tool: %s%s\n' "$TOOL_VERDICT" "$([ "$TOOL_VERDICT" = "ABSENT" ] && printf ' (tools/souji-verify.sh not present — harness calibrated against the reference; re-run when the tool lands)' || true)"
if [ "$CAL_OK" != "yes" ]; then exit 1; fi
if [ "$TOOL_PRESENT" -eq 1 ] && [ "$TOOL_VERDICT" != "PASS" ]; then exit 1; fi
exit 0
