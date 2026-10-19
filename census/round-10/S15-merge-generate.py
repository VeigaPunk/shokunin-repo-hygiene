#!/usr/bin/env python3
"""S15 (round 10) composer: generate tools/cand-merge-*.sh from the two r9 lineages.

Inputs (read-only):
  S17 lineage  tools/souji-verify.sh, souji-vault-verify.sh, souji-quarantine.sh
               (installed, S17-patched: 40/51/91 selftests)
  S18 lineage  tools/souji-guard.r9-s18.sh (+ the three r9-s18 candidates, used
               only as the source of the guard and for reference diffs)

Composition rule (adjudicated by measurement, not by preference):
  base = S17 body  (keeps NUL list gate, ledger-revocation pin, default-ref
                    recheck in second_check, git-unverifiable refusals,
                    receipt-engine parsing, nested-repo refusal)
  guard = S18 shared hardening, inlined after the base's function definitions so
          it overrides the same-named helpers (dirty-pushed status, hidden live
          refs, recursive directory ages, complete independent ledger rows,
          durable-ref worktree graph, quarantine containment).
  renames = the minimum needed so the guard's delegating wrappers resolve to the
          S17 implementation instead of recursing:
            verify:      evaluate_path  -> s18_evaluate_path
            vault:       evaluate_path  -> s18_evaluate_path
                         try_ledger     -> s18_try_ledger
            quarantine:  flow_one       -> s18_flow_one
                         second_check   -> s18_second_check
  union patches = the two places where an override would DROP an S17 fix:
            verify: guard try_obsidian gains the ledger-revocation pin
            vault:  guard load_ledger gains LEDGER_PIN capture
          (both keep the guard's strict row validation AND the S17 pin)

Every substitution asserts it matched exactly once; a silent no-op would ship a
half-merged tool, so the generator fails closed instead.
"""
import hashlib
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "tools"
ST_NOTE = 'st_note() { printf \'%s\\n\' "$*"; }'

# --------------------------------------------------------------- guard text --
guard = (TOOLS / "souji-guard.r9-s18.sh").read_text()

UNION_OBSIDIAN = '''try_obsidian() {
  local target=$1 isdir=$2 row source_sha vault_sha ledger_pin
  ledger_pin=$(file_sha "$LEDGER") || { NOTES+=("obsidian=ledger-unverifiable"); return 1; }
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
    if [ "$(file_sha "$LEDGER" || true)" != "$ledger_pin" ]; then
      NOTES+=("obsidian=ledger-changed"); return 1
    fi
    R_VERDICT=SAFE; R_RECEIPT=moved-to-obsidian
    R_EVIDENCE="ledger=source+vault-digest ledger-row vault=$S18_VP source-sha256=${S18_SS:0:12}"
    return 0
  done < <(ledger_lines)
  NOTES+=("obsidian=no-matching-ledger-row")
  return 1
}'''

GUARD_OBSIDIAN = '''try_obsidian() {
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
}'''

GUARD_LOAD_LEDGER = '''load_ledger() {
  local row first=1
  LEDGER_ROWS=()
  s18_path_ok "$LEDGER" && [ -f "$LEDGER" ] || return 0
  while IFS= read -r row || [ -n "$row" ]; do
    if [ "$first" = 1 ]; then
      first=0
      case "$row" in source_path$'\\t'*) continue ;; esac
    fi
    [ -z "$row" ] || LEDGER_ROWS+=("$row")
  done < "$LEDGER"
}'''

UNION_LOAD_LEDGER = '''load_ledger() {
  local row first=1
  LEDGER_ROWS=()
  LEDGER_PIN=""
  s18_path_ok "$LEDGER" && [ -f "$LEDGER" ] || return 0
  LEDGER_PIN=$(file_sha "$LEDGER") || { LEDGER_PIN=""; return 0; }
  while IFS= read -r row || [ -n "$row" ]; do
    if [ "$first" = 1 ]; then
      first=0
      case "$row" in source_path$'\\t'*) continue ;; esac
    fi
    [ -z "$row" ] || LEDGER_ROWS+=("$row")
  done < "$LEDGER"
}'''


def sub_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit("FATAL: %s matched %d times (want 1)" % (label, n))
    return text.replace(old, new, 1)


# r10 S15 fix (fresh repro, git 2.55): `git diff --quiet <ref> -- <path>` rewrites
# .git/index to refresh stat info no matter what GIT_OPTIONAL_LOCKS says, so the
# S18 lineage's pushed check violated the read-only contract (S13 cluster G1).
# A private index keeps the same tracked-content-vs-ref semantics and touches
# nothing in the repository.
GUARD_DIFF_ANCHOR = '''try_pushed() {
  local target=$1 repo=$2 intro ref status touching'''

GUARD_SNAPSHOT_HELPER = '''s18_snapshot_equal() { # read-only tracked-content-vs-ref compare
  local repo=$1 ref=$2 path=$3 tmpidx rc
  tmpidx=$(mktemp -p "${TMPDIR:-/var/tmp}") || return 1
  rm -f -- "$tmpidx"
  if ! GIT_INDEX_FILE="$tmpidx" git -C "$repo" read-tree "$ref" 2>/dev/null; then
    rm -f -- "$tmpidx"; return 1
  fi
  GIT_INDEX_FILE="$tmpidx" git -C "$repo" update-index -q --refresh >/dev/null 2>&1
  GIT_INDEX_FILE="$tmpidx" git -C "$repo" diff-index --quiet "$ref" -- "$path" 2>/dev/null
  rc=$?
  rm -f -- "$tmpidx"
  return "$rc"
}

try_pushed() {
  local target=$1 repo=$2 intro ref status touching'''

GUARD_DIFF_CALL = '  if ! git -C "$repo" diff --quiet --no-ext-diff --no-textconv "$ref" -- "$target" 2>/dev/null; then'
GUARD_DIFF_READONLY = '  if ! s18_snapshot_equal "$repo" "$ref" "$target"; then'

# Adopted from the round-10 cluster fixes (each reproduced fresh by its author
# seat), because both close an unsafe class that neither r9 lineage closes and
# both are pure fail-closed additions:
#   G2 (S13/S14)  an aged .scratch container laundered a fresh or backdated
#                 descendant into SAFE(stale); the ctime witness is what a
#                 backdate forgery cannot produce.
#   F2 (S12/S06)  a repository root carrying a `.git` FILE fell through to the
#                 artifact engine and earned a false SAFE(pushed).
GUARD_OLD_SCOPE = '''s18_old_scope() {
  local path=$1 cutoff=$2 p mtime
  mtime=$(stat -c %Y -- "$path" 2>/dev/null) || return 1
  [ "$mtime" -lt "$cutoff" ] || return 1
  if [ -d "$path" ]; then
    for p in "$path"/* "$path"/.[!.]* "$path"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      s18_path_ok "$p" && s18_old_scope "$p" "$cutoff" || return 1
    done
  fi
}'''

GUARD_OLD_SCOPE_CTIME = '''s18_old_scope() {
  local path=$1 cutoff=$2 p mtime ctime isroot=${3:-1}
  mtime=$(stat -c %Y -- "$path" 2>/dev/null) || return 1
  [ "$mtime" -lt "$cutoff" ] || return 1
  if [ "$isroot" = 0 ]; then
    ctime=$(stat -c %Z -- "$path" 2>/dev/null) || return 1
    [ "$ctime" -lt "$cutoff" ] || return 1
  fi
  if [ -d "$path" ] && [ ! -L "$path" ]; then
    for p in "$path"/* "$path"/.[!.]* "$path"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      s18_path_ok "$p" && s18_old_scope "$p" "$cutoff" 0 || return 1
    done
  fi
}'''

GUARD_OLD_SCOPE_CALL = '  if ! s18_old_scope "$target" "$((now - STALE_DAYS * 86400))"; then'
GUARD_OLD_SCOPE_CALL_NEW = '  if ! s18_old_scope "$target" "$((now - STALE_DAYS * 86400))" 1; then'

GUARD_EVALPATH_ANCHOR = '''  if [ -d "$target" ] && ! s18_scope_ok "$target"; then
    R_VERDICT=NOT-SAFE; R_RECEIPT=secrets-refusal; R_REASON=secrets-refusal
    R_EVIDENCE="protected-or-unsupported-descendant-refused"; return 0
  fi
  s18_evaluate_path "$raw"'''

GUARD_EVALPATH_GITFILE = '''  if [ -d "$target" ] && ! s18_scope_ok "$target"; then
    R_VERDICT=NOT-SAFE; R_RECEIPT=secrets-refusal; R_REASON=secrets-refusal
    R_EVIDENCE="protected-or-unsupported-descendant-refused"; return 0
  fi
  # r10 cluster F (F2): a repository root whose `.git` is a FILE is a repo root,
  # not an ordinary artifact -- the S17/S18 nested-metadata gate only inspects
  # directory targets, so without this the root fell through to the artifact
  # engine and earned a false SAFE(pushed).
  if [ -d "$target" ] && s18_is_repo_root "$target"; then
    evaluate_repo_root "$target"; return 0
  fi
  s18_evaluate_path "$raw"'''

GUARD_GITFILE_HELPER = '''s18_repo_gitdir() { # $1 worktree root -> resolved git dir on stdout
  local p=$1 g
  if [ -d "$p/.git" ]; then canon_path "$p/.git"; return 0; fi
  [ -f "$p/.git" ] || return 1
  g=$(sed -n 's/^gitdir: //p' "$p/.git" 2>/dev/null | head -1)
  [ -n "$g" ] || return 1
  case "$g" in /*) : ;; *) g="$p/$g" ;; esac
  canon_path "$g"
  return 0
}

s18_is_repo_root() { # $1 path -- repo root, not a linked worktree
  local p=$1 g
  [ -e "$p/.git" ] || return 1
  [ -d "$p/.git" ] && return 0
  [ -f "$p/.git" ] || return 1
  g=$(s18_repo_gitdir "$p") || return 1
  [ -e "$g" ] || return 1
  case "$g" in */worktrees/*) return 1 ;; esac
  return 0
}

# r10 cluster F (F1/F1b): structural owner discovery, multi-claimant records and
# conflict refusal live in the F1 override block appended after the guard (they
# must override the guard's own evaluate_worktree).
s18_old_scope() {'''

GUARD_OLD_SCOPE_HEAD = '''s18_old_scope() {'''

# The cluster-F ownership fix must override the guard's own evaluate_worktree,
# so it is appended AFTER the whole guard text: the guard's per-claimant
# evaluator is renamed and my multi-claimant dispatcher takes the public name.
GUARD_EVAL_WT_ANCHOR = '''evaluate_worktree() {
  local target=$1 meta=$2 owner head branch unp uniq dirty refs status'''

GUARD_EVAL_WT_RENAMED = '''s18_evaluate_worktree_one() {
  local target=$1 meta=$2 owner head branch unp uniq dirty refs status'''

F1_OVERRIDE_BLOCK = '''

# ---- r10 cluster F (F1/F1b) ownership + registration conflicts, adopted by S15 ----
# A linked worktree whose owner directory is not named `*-shokunin` was never
# scanned, so it fell through to a stale receipt and was DELETED (J22); and two
# registrations for one path resolved last-writer-wins, letting a pushed
# registration mask an unpushed one (J20). Discovery is now structural and every
# claimant is evaluated, failing closed when they disagree.
scan_worktrees() {
  local repo gd path head branch line
  for repo in "$SHOKUNIN_ROOT" "$SHOKUNIN_ROOT"/*; do
    [ -d "$repo" ] || continue
    [ -e "$repo/.git" ] || continue
    gd=$(s18_repo_gitdir "$repo") || continue
    case "$gd" in */worktrees/*) continue ;; esac
    path=""; head=""; branch=""
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        'worktree '*)
          if [ -n "$path" ]; then _wt_record "$repo" "$path" "$head" "$branch"; fi
          path=${line#worktree }; head=""; branch="" ;;
        'HEAD '*) head=${line#HEAD } ;;
        'branch '*) branch=${line#branch } ;;
        'detached'*) branch="" ;;
        'prunable'*) : ;;
      esac
    done < <(git -C "$repo" worktree list --porcelain 2>/dev/null || true)
    if [ -n "$path" ]; then _wt_record "$repo" "$path" "$head" "$branch"; fi
  done
  return 0
}

_wt_record() { # $1 repo, $2 path, $3 head, $4 branch -- every claimant is kept
  local repo=$1 path=$2 head=$3 branch=$4 cp
  [ -n "$path" ] || return 0
  [ "$path" = "$repo" ] && return 0
  cp=$(canon_path "$path")
  if [ -n "${WT_MAP[$cp]:-}" ]; then
    WT_MAP["$cp"]="${WT_MAP[$cp]}"$'\\n'"$repo"$'\\t'"$head"$'\\t'"$branch"
  else
    WT_MAP["$cp"]="$repo"$'\\t'"$head"$'\\t'"$branch"
  fi
  return 0
}

evaluate_worktree() { # $1 target, $2 meta: one owner<TAB>head<TAB>branch per line
  local target=$1 meta=$2 line ov="" orc="" oev="" first=1 any_safe=0 any_ns=0
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    s18_evaluate_worktree_one "$target" "$line"
    if [ "$R_VERDICT" = NOT-SAFE ]; then any_ns=1; else any_safe=1; fi
    if [ "$first" = 1 ] || [ "$R_VERDICT" = NOT-SAFE ]; then
      ov=$R_VERDICT; orc=$R_RECEIPT; oev=$R_EVIDENCE; first=0
    fi
  done <<< "$meta"
  R_VERDICT=$ov; R_RECEIPT=$orc; R_EVIDENCE=$oev
  if [ "$any_safe" = 1 ] && [ "$any_ns" = 1 ]; then
    R_VERDICT=NOT-SAFE; R_RECEIPT=registration-conflict
    R_EVIDENCE="multiple registrations disagree ($oev)"
  fi
  return 0
}
'''

# Applied once, for all three composed tools.
guard = sub_once(guard, GUARD_DIFF_ANCHOR, GUARD_SNAPSHOT_HELPER, "guard snapshot helper")
guard = sub_once(guard, GUARD_DIFF_CALL, GUARD_DIFF_READONLY, "guard diff read-only")
guard = sub_once(guard, GUARD_OLD_SCOPE, GUARD_OLD_SCOPE_CTIME, "guard ctime witness")
guard = sub_once(guard, GUARD_OLD_SCOPE_CALL, GUARD_OLD_SCOPE_CALL_NEW, "guard ctime call")
guard = sub_once(guard, GUARD_EVALPATH_ANCHOR, GUARD_EVALPATH_GITFILE, "guard gitfile root")
guard = sub_once(guard, GUARD_OLD_SCOPE_HEAD, GUARD_GITFILE_HELPER, "guard gitfile helpers")
guard = sub_once(guard, GUARD_EVAL_WT_ANCHOR, GUARD_EVAL_WT_RENAMED, "guard worktree rename")
guard = guard + F1_OVERRIDE_BLOCK


def split_at_st_note(text, label):
    idx = text.find("\n" + ST_NOTE)
    if idx < 0:
        sys.exit("FATAL: %s: st_note anchor not found" % label)
    return text[: idx + 1], text[idx + 1 :]


def build(kind, base_name, renames, guard_patches, header_note, base_patches=()):
    base = (TOOLS / base_name).read_text()
    head, tail = split_at_st_note(base, base_name)
    for old, new in base_patches:
        head = sub_once(head, old, new, "%s base patch" % base_name)
    for old, new in renames:
        head = sub_once(head, old, new, "%s rename %s" % (base_name, old))
    g = guard
    for old, new in guard_patches:
        g = sub_once(g, old, new, "%s guard patch" % base_name)
    body = (
        header_note
        + "\n# ---- S18 shared hardening (round-9 S18 guard), inlined by r10 S15 ----\n"
        + "S18_KIND=%s\n" % kind
        + g
        + "\n# ---- end inlined S18 guard ----\n\n"
    )
    return head + body + tail


def write(path, text):
    Path(path).write_text(text)
    Path(path).chmod(0o755)
    print("%-34s %7d bytes  sha256 %s" % (Path(path).name, len(text.encode()),
                                          hashlib.sha256(text.encode()).hexdigest()[:16]))


def main():
    verify = build(
        "verify", "souji-verify.sh",
        [("evaluate_path() {", "s18_evaluate_path() {")],
        [(GUARD_OBSIDIAN, UNION_OBSIDIAN)],
        "# cand-merge-verify.sh -- round-10 S15 composed candidate.\n"
        "# S17 receipt engine (round-2 base + S08 repairs) with the S18 shared\n"
        "# hardening layer inlined after it, plus the ledger-revocation pin that the\n"
        "# S18 override would otherwise drop. Renames: base evaluate_path ->\n"
        "# s18_evaluate_path, which the guard's evaluate_path wrapper delegates to.",
    )
    vault = build(
        "vault", "souji-vault-verify.sh",
        [("evaluate_path() {", "s18_evaluate_path() {"),
         ("try_ledger() {", "s18_try_ledger() {")],
        [(GUARD_LOAD_LEDGER, UNION_LOAD_LEDGER)],
        "# cand-merge-vault.sh -- round-10 S15 composed candidate.\n"
        "# S17 ledger verifier with the S18 shared hardening layer inlined after it,\n"
        "# plus the LEDGER_PIN capture that the S18 load_ledger override would\n"
        "# otherwise drop. Renames: base evaluate_path -> s18_evaluate_path (the\n"
        "# guard wrapper delegates to it); base try_ledger -> s18_try_ledger (the\n"
        "# guard's strict row filter delegates to it, so row validation AND the\n"
        "# revocation pin both run).",
    )
    quarantine = build(
        "quarantine", "souji-quarantine.sh",
        [("flow_one() {", "s18_flow_one() {"),
         ("second_check() {", "s18_second_check() {")],
        [],
        "# cand-merge-quarantine.sh -- round-10 S15 composed candidate.\n"
        "# S17 quarantine flow (NUL list gate, default-ref recheck, ledger pin,\n"
        "# engine-record parsing) with the S18 shared hardening layer inlined after\n"
        "# it. Renames: base flow_one -> s18_flow_one and base second_check ->\n"
        "# s18_second_check, which the guard's containment wrappers delegate to.",
        base_patches=[(
            'VERIFY_BIN="${SOUJI_VERIFY_BIN:-$REPO_ROOT/tools/souji-verify.sh}"',
            '# Composed pair: default to the merged sibling engine when it sits next to\n'
            '# this candidate, else fall back to the installed receipt engine.\n'
            'if [ -z "${SOUJI_VERIFY_BIN:-}" ] && [ -f "$SCRIPT_DIR/cand-merge-verify.sh" ]; then\n'
            '  VERIFY_BIN="$SCRIPT_DIR/cand-merge-verify.sh"\n'
            'else\n'
            '  VERIFY_BIN="${SOUJI_VERIFY_BIN:-$REPO_ROOT/tools/souji-verify.sh}"\n'
            'fi',
        )],
    )
    write(TOOLS / "cand-merge-verify.sh", verify)
    write(TOOLS / "cand-merge-vault.sh", vault)
    write(TOOLS / "cand-merge-quarantine.sh", quarantine)
    return 0


if __name__ == "__main__":
    sys.exit(main())
