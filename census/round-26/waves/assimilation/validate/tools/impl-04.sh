#!/usr/bin/env bash
# impl-04 — round-8 quarantine flow executor (seat S04, implementor; independent).
#
# Executes the lane's four physical removal stages (SKILL.md "Removal flow")
# as ticket-bounded, fail-closed operations. Round 7's O1 caveat: the flow
# was adjudicated but never executed (0 authorized tickets). This tool makes
# the execution path itself testable on fixture repos without ever reaching
# the live fleet.
#
#   stage 1  receipt via tools/souji-verify.sh + gates 1/2 re-checked HERE,
#            IMMEDIATELY BEFORE any move (r1 logs_tier lesson: establish the
#            receipt first; S15 rule: all three gates documented per target)
#   stage 2  move into <repo>/.ufo-quarantine/<utc-date>/<id>__<basename>
#            (git mv for tracked + quarantine commit; plain mv for untracked;
#            quarantine is a normal commit in the owning repo)
#   stage 3  hold: pushed -> 0s (second check suffices per SKILL); anything
#            else -> 86400s default, floor 450s (SKILL: >= one driver tick,
#            prefer 24h). Requested values below the floor are clamped UP.
#   stage 4  second check + delete: ticket intact, artifact bytes unchanged
#            (manifest digest), original path not resurrected (worktree and
#            index), no NEW unpushed commits touching the original path
#            beyond the recorded stage commit, receipt still derivable
#            (pushed: default ref resolves and intro is still an ancestor;
#            stale: zero live references still; moved-to-obsidian: ledger
#            row + vault digest still verify), hold elapsed, no symlinks in
#            scope. Only then rm -rf the quarantine copy.
#
# Gate profiles (--gates, default strict):
#   strict  r7 S15 authorization rule: gate2 refuses untracked targets too
#           (`git status --porcelain --untracked-files=all -- <path>` must be
#           empty). This is what made r7's lore .scratch NOT-SAFE.
#   skill   SKILL.md literal flow: plain `mv` is the sanctioned path for
#           untracked artifacts, so gate2 counts only tracked modifications
#           over the path. gate1 (no unpushed commits touching) holds in
#           both profiles for every receipt class.
#
# CLI
#   tools/impl-04.sh [--execute] [--json] [--hold-seconds N] [--stale-days N]
#                    [--gates strict|skill] [--verify <souji-verify-path>]
#                    stage   <path>...            # receipt + gates + move + ticket
#                    status  --ticket <file>      # hold remaining + check preview
#                    release --ticket <file>      # second check + delete
#                    gates   <repo> [path]        # read-only gate report
#                    --selftest
#
# Without --execute everything is a dry run: full checks, printed plan,
# zero writes anywhere. exit codes: 0 ran (a REFUSED line is the tool
# working, not an error); 1 selftest failure; 2 usage. No other codes.
#
# Safety rails
#   * --execute is refused (live-repo-not-authorized) unless the owning repo
#     realpath is under a fixture root (TMPDIR/souji-quarantine-selftest.* or
#     $SOUJI_FIXTURE_ROOT) or $SOUJI_ALLOW_LIVE_REPO equals the repo realpath
#     exactly — the operator's explicit two-key authorization. Dry runs are
#     read-only and need no authorization.
#   * The 450s hold floor may be lowered ONLY inside fixture roots
#     (SOUJI_TEST_HOLD_FLOOR=1 + fixture repo); live repos keep the floor.
#   * Secret-shaped paths never enter the flow: stage requires SAFE from
#     souji-verify, whose secrets-refusal verdict refuses them before any
#     read or move; symlink targets are refused before realpath.
#   * Git mutations are exactly: git mv, git add -A -- .ufo-quarantine,
#     git commit -- .ufo-quarantine (identity pinned to
#     souji-shokunin <souji@shokunin.local>). Never fetch/push/branch/
#     checkout/reset/rebase/amend. History only ever grows at the tip.
#   * Deletion targets are validated strictly inside
#     <repo>/.ufo-quarantine/ (realpath prefix) before rm -rf.
#   * bash + coreutils + git + rg only; writes only into the owning repo's
#     .ufo-quarantine/ (execute mode) and mktemp selftest fixtures; never
#     touches .ufo/state, .ufo/watchdog.log, or operator config.
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
VERIFY_BIN="${SOUJI_QA_VERIFY:-$SCRIPT_DIR/souji-verify.sh}"

EXECUTE=0
JSON=0
SELFTEST=0
HOLD_REQ=""           # empty = per-receipt default
STALE_DAYS=""
PROFILE="strict"
CMD=""

QA_STATUS=0           # 0 = all operations evaluated; 1 = selftest failed

# ---------------------------------------------------------------- output ----

QA_LINES=()
qa() { # $1 op  $2 key  $3 OK|REFUSED|INFO  $4 detail
  local line
  line="$(printf 'QA\t%s\t%s\t%s\t%s' "$1" "$2" "$3" "$4")"
  QA_LINES+=("$line")
  if [ "$JSON" = 0 ]; then printf '%s\n' "$line"; fi
}

json_escape() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}; s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; s=${s//$'\r'/\\r}
  printf '%s' "$s"
}

emit_json() {
  printf '{"tool":"impl-04","execute":%s,"ops":%s,"lines":[' \
    "$([ "$EXECUTE" = 1 ] && echo true || echo false)" "${#QA_LINES[@]}"
  local i first=1
  for i in "${!QA_LINES[@]}"; do
    IFS=$'\t' read -r _ op key status detail <<<"${QA_LINES[$i]}"
    [ "$first" = 1 ] && first=0 || printf ','
    printf '{"op":"%s","key":"%s","status":"%s","detail":"%s"}' \
      "$(json_escape "$op")" "$(json_escape "$key")" "$(json_escape "$status")" "$(json_escape "$detail")"
  done
  printf ']}\n'
}

die_usage() { printf 'impl-04: %s\n' "$1" >&2; exit 2; }

# ------------------------------------------------------------ git helpers ---

# mirrors tools/souji-verify.sh resolve_default_ref (r5 fix: no
# remote-tracking ref -> pushed unverifiable; a local ref can NEVER
# establish a pushed receipt).
resolve_default_ref() { # $1 repo -> prints ref, rc 0/1
  local repo=$1 b refs n
  b=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)
  if [ -n "$b" ] && git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$b" 2>/dev/null; then
    printf 'refs/remotes/origin/%s\n' "$b"; return 0
  fi
  refs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null | grep -v '^refs/remotes/origin/HEAD$' || true)
  n=$(printf '%s\n' "$refs" | grep -c . || true)
  if [ "$n" = 1 ]; then printf '%s\n' "$refs"; return 0; fi
  return 1
}

unpushed_touching() { # $1 repo  $2 repo-relative path -> prints commit shas
  git -C "$1" log --branches --not --remotes --format=%H -- "$2" 2>/dev/null || true
}

# mirrors tools/souji-verify.sh dir_digest (r5 fix: symlink in scope ->
# fail closed rc 2; .git pruned).
dir_digest() {
  local d=$1
  if ( cd "$d" && find . -path './.git' -prune -o -type l -print -quit 2>/dev/null | grep -q . ); then
    return 2
  fi
  ( cd "$d" && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null
}

count_files() {
  ( cd "$1" && find . -path './.git' -prune -o -type f -print 2>/dev/null | wc -l )
}

file_sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

symlink_in_scope() { # $1 path -> rc 0 if any symlink is/inside $1
  if [ -L "$1" ]; then return 0; fi
  if [ -d "$1" ]; then
    ( cd "$1" && find . -type l -print -quit 2>/dev/null | grep -q . )
    return $?
  fi
  return 1
}

# mirrors tools/souji-verify.sh count_live_refs sweep (same exclusions incl.
# quarantine; fixed-string basename; artifact excluded from its own sweep).
count_live_refs() { # $1 orig abs path  $2 repo
  local target=$1 repo=$2 rel="" base n out status
  local -a self_globs=()
  case "$target" in "$repo"/*) rel=${target#"$repo"/} ;; esac
  if [ -n "$rel" ]; then self_globs=(-g "!$rel" -g "!./$rel"); fi
  base=$(basename -- "$target")
  set +e
  out=$( cd "$repo" && rg -l --no-ignore --fixed-strings -e "$base" . \
        -g '!.git' -g '!**/.git/**' \
        -g '!souji-shokunin/census/**' -g '!**/souji-shokunin/census/**' \
        -g '!souji-shokunin/tests/**' -g '!**/souji-shokunin/tests/**' \
        -g '!**/.ufo-quarantine/**' \
        "${self_globs[@]}" 2>/dev/null )
  status=$?
  set -e
  if [ "$status" -gt 1 ]; then printf 'unknown\n'; return 0; fi
  n=$(printf '%s\n' "$out" | grep -c . || true)
  printf '%s\n' "${n// /}"
}

# ---------------------------------------------------------- authorization ---

is_fixture_repo() {
  local r=$1 root="${SOUJI_FIXTURE_ROOT:-}"
  case "$r" in
    "${TMPDIR:-/tmp}"/souji-quarantine-selftest.*) return 0 ;;
  esac
  [ -n "$root" ] || return 1
  root=$(realpath -m -- "$root" 2>/dev/null || printf '%s' "$root")
  case "$r" in "$root"|"$root"/*) return 0 ;; esac
  return 1
}

authorize_repo() { # $1 op  $2 repo realpath; rc 1 + QA line on refusal
  local op=$1 repo=$2 allow allowrp
  if [ ! -d "$repo" ]; then qa "$op" "$repo" REFUSED "repo-missing"; return 1; fi
  if is_fixture_repo "$repo"; then return 0; fi
  allow="${SOUJI_ALLOW_LIVE_REPO:-}"
  if [ -n "$allow" ]; then
    allowrp=$(realpath -m -- "$allow" 2>/dev/null || printf '%s' "$allow")
    if [ "$allowrp" = "$repo" ]; then return 0; fi
  fi
  qa "$op" "$repo" REFUSED \
    "live-repo-not-authorized (fixtures under ${TMPDIR:-/tmp}/souji-quarantine-selftest.* or \$SOUJI_FIXTURE_ROOT are always allowed; live repos require SOUJI_ALLOW_LIVE_REPO=<repo realpath>, operator-owned)"
  return 1
}

hold_floor() { # $1 repo realpath  $2 receipt -> floor seconds
  if [ "$2" = "pushed" ]; then printf '0\n'; return 0; fi
  if [ "${SOUJI_TEST_HOLD_FLOOR:-}" = "1" ] && is_fixture_repo "$1"; then printf '0\n'; return 0; fi
  printf '450\n'
}

# ------------------------------------------------------------ verify call ---

V_VERDICT="NOT-SAFE"; V_RECEIPT="none"; V_EVIDENCE="not-run"; V_LINE=""

verify_one() { # $1 path; rc 0 iff SAFE
  V_VERDICT="NOT-SAFE"; V_RECEIPT="none"; V_EVIDENCE="verify-unavailable"; V_LINE=""
  local out last _t _p _ev
  if [ ! -e "$VERIFY_BIN" ]; then
    V_EVIDENCE="verify-tool-missing($VERIFY_BIN)"; return 1
  fi
  if [ -n "$STALE_DAYS" ]; then
    out=$("$VERIFY_BIN" --stale-days "$STALE_DAYS" -- "$1" 2>&1) || true
  else
    out=$("$VERIFY_BIN" -- "$1" 2>&1) || true
  fi
  last=$(printf '%s\n' "$out" | grep '^VERDICT' | tail -1 || true)
  if [ -z "$last" ]; then V_EVIDENCE="verify-no-verdict-line"; return 1; fi
  V_LINE=$last
  IFS=$'\t' read -r _t _p V_VERDICT V_RECEIPT _ev <<<"$last"
  V_EVIDENCE="$V_RECEIPT ${_ev:-}"
  [ "$V_VERDICT" = "SAFE" ]
}

# stage-time gates 1+2 (S15 rule): gate1 no unpushed commits touching the
# path (every receipt class); gate2 clean worktree over the path, where
# "clean" depends on the profile (strict: no untracked either).
stage_gates() { # $1 repo  $2 rel  $3 profile; rc 0 iff pass (QA emitted on fail)
  local repo=$1 rel=$2 profile=$3 nup nmod nuntr
  nup=$(unpushed_touching "$repo" "$rel" | grep -c . || true)
  if [ "$nup" != 0 ]; then
    qa stage "$rel" REFUSED "gate1-unpushed-touching($nup)"; return 1
  fi
  local st
  st=$(git -C "$repo" status --porcelain --untracked-files=all -- "$rel" 2>/dev/null || true)
  nmod=$(printf '%s' "$st" | grep -cv '^??' || true)
  nuntr=$(printf '%s' "$st" | grep -c '^??' || true)
  if [ "$nmod" != 0 ]; then
    qa stage "$rel" REFUSED "gate2-dirty-tracked($nmod)"; return 1
  fi
  if [ "$profile" = strict ] && [ "$nuntr" != 0 ]; then
    qa stage "$rel" REFUSED "gate2-untracked($nuntr) strict profile: untracked targets need --gates skill or operator disposition (r7 S15 rule)"; return 1
  fi
  return 0
}

# --------------------------------------------------------------- tickets ----

TICKET_VERSION="impl04-r8-1"

ticket_field() { # $1 tsv  $2 key -> value (last wins)
  local v="" k rest
  [ -f "$1" ] || return 0
  while IFS=$'\t' read -r k rest; do
    [ "$k" = "$2" ] && v=$rest
  done <"$1"
  printf '%s' "$v"
}

ticket_valid() { # $1 tsv; rc 0 iff required fields present and typed
  local tsv=$1 repo qpath epoch hold
  repo=$(ticket_field "$tsv" repo)
  qpath=$(ticket_field "$tsv" qpath)
  epoch=$(ticket_field "$tsv" stage_epoch)
  hold=$(ticket_field "$tsv" hold_seconds)
  [ -n "$repo" ] && [ -d "$repo" ] || { qa ticket "$tsv" REFUSED "ticket-invalid(repo)"; return 1; }
  [ -n "$qpath" ] || { qa ticket "$tsv" REFUSED "ticket-invalid(qpath)"; return 1; }
  case "$epoch" in ''|*[!0-9]*) qa ticket "$tsv" REFUSED "ticket-invalid(stage_epoch)"; return 1 ;; esac
  case "$hold" in ''|*[!0-9]*) qa ticket "$tsv" REFUSED "ticket-invalid(hold_seconds)"; return 1 ;; esac
  return 0
}

ticket_render_json() { # $1 tsv -> JSON on stdout
  local tsv=$1 k v
  local id="" repo="" orig="" rel="" kind="" receipt="" rev="" intro="" dref="" \
        hold=0 stage_utc="" stage_epoch=0 stage_mode="" stage_commit="" qpath="" \
        msha="" mcount=0 verify="" status=""
  while IFS=$'\t' read -r k v; do
    case "$k" in
      id) id=$v ;; repo) repo=$v ;; orig) orig=$v ;; rel) rel=$v ;; kind) kind=$v ;;
      receipt) receipt=$v ;; receipt_evidence) rev=$v ;; intro_commit) intro=$v ;;
      default_ref) dref=$v ;; hold_seconds) hold=$v ;; stage_utc) stage_utc=$v ;;
      stage_epoch) stage_epoch=$v ;; stage_mode) stage_mode=$v ;;
      stage_commit) stage_commit=$v ;; qpath) qpath=$v ;;
      manifest_sha) msha=$v ;; manifest_count) mcount=$v ;;
      verify_line) verify=$v ;; status) status=$v ;;
    esac
  done <"$tsv"
  printf '{"ticket_version":"%s","id":"%s","repo":"%s","orig":"%s","rel":"%s","kind":"%s","receipt":"%s","receipt_evidence":"%s","intro_commit":"%s","default_ref":"%s","hold_seconds":%s,"stage_utc":"%s","stage_epoch":%s,"stage_mode":"%s","stage_commit":"%s","qpath":"%s","manifest_sha":"%s","manifest_count":%s,"verify_line":"%s","status":"%s"}\n' \
    "$TICKET_VERSION" "$(json_escape "$id")" "$(json_escape "$repo")" "$(json_escape "$orig")" \
    "$(json_escape "$rel")" "$(json_escape "$kind")" "$(json_escape "$receipt")" \
    "$(json_escape "$rev")" "$(json_escape "$intro")" "$(json_escape "$dref")" \
    "$hold" "$(json_escape "$stage_utc")" "$stage_epoch" "$(json_escape "$stage_mode")" \
    "$(json_escape "$stage_commit")" "$(json_escape "$qpath")" "$(json_escape "$msha")" \
    "$mcount" "$(json_escape "$verify")" "$(json_escape "$status")"
}

ticket_event() { # $1 tsv  $2 name  $3 detail
  local tsv=$1 name=$2 detail=$3
  printf 'event\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$name" "$detail" >>"$tsv"
  sed -i "s|^status\t.*|status\t$name|" "$tsv"
}

# ---------------------------------------------------------------- staging ---

git_commit_quarantine() { # $1 repo  $2 rel  $3 msg -> commit sha; rc 1 on failure
  # Commits ONLY the staged rename halves (the .ufo-quarantine addition and
  # the original path's deletion — both staged by git mv). A pathspec commit
  # on `.ufo-quarantine` alone splits the rename (verified: the original path
  # stayed tracked and the unpushed-set check then saw an empty set); a
  # pathspec on the original path fatals after the move (`pathspec 'x' did
  # not match any files`). So: stage, verify nothing FOREIGN is staged, then
  # commit without a pathspec. Foreign staged changes => refuse loud (they
  # must never be swept into a quarantine commit).
  local repo=$1 rel=$2 msg=$3 staged foreign
  git -C "$repo" add -A -- .ufo-quarantine 2>/dev/null || true
  staged=$(git -C "$repo" diff --cached --name-only || true)
  foreign=$(printf '%s\n' "$staged" | grep -v -e '^\.ufo-quarantine/' -e "^${rel}$" || true)
  if [ -n "$foreign" ]; then
    printf 'foreign-staged: %s\n' "$foreign" >&2
    return 1
  fi
  git -C "$repo" -c user.name=souji-shokunin -c user.email=souji@shokunin.local \
    commit -q -m "$msg" || return 1
  git -C "$repo" rev-parse HEAD
}

owning_repo_of() { # $1 abs path -> prints repo dir or empty
  local p=$1 d
  if [ -d "$p/.git" ]; then printf '%s' "$p"; return 0; fi
  d=$(dirname -- "$p")
  while [ "$d" != "/" ]; do
    if [ -d "$d/.git" ]; then printf '%s' "$d"; return 0; fi
    d=$(dirname -- "$d")
  done
  return 0
}

do_stage() {
  local target rp repo rel id datestr qdir qpath receipt
  local intro dref hold floor kind msha mcount tracked stage_mode stage_commit
  local tsv tickets_dir out
  for target in "$@"; do
    if [ -L "$target" ]; then qa stage "$target" REFUSED "symlink-target"; continue; fi
    if [ ! -e "$target" ]; then qa stage "$target" REFUSED "unreachable"; continue; fi
    rp=$(realpath -m -- "$target")
    repo=$(owning_repo_of "$rp" || true)
    if [ -z "$repo" ]; then qa stage "$rp" REFUSED "no-owning-repo"; continue; fi
    rel=${rp#"$repo"/}

    # authorization precedes inspection: in execute mode an unauthorized
    # repo is never even read. Dry runs stay read-only and unauthorized.
    if [ "$EXECUTE" = 1 ] && ! authorize_repo stage "$repo"; then continue; fi
    # stage 1: receipt + gates BEFORE any mutation (r1 lesson)
    if ! verify_one "$rp"; then
      qa stage "$rp" REFUSED "receipt=NOT-SAFE($V_RECEIPT) evidence=$V_EVIDENCE"
      continue
    fi
    receipt=$V_RECEIPT
    if ! stage_gates "$repo" "$rel" "$PROFILE"; then continue; fi

    id="q$(date -u +%Y%m%dT%H%M%SZ)-$(printf '%s' "$rel" | sha256sum | cut -c1-8)"
    datestr=$(date -u +%Y%m%d)
    qdir="$repo/.ufo-quarantine/$datestr"
    qpath="$qdir/${id}__$(basename -- "$rp")"

    if symlink_in_scope "$rp"; then qa stage "$rp" REFUSED "symlink-in-scope"; continue; fi

    intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$rel" 2>/dev/null | head -1 || true)
    dref=$(resolve_default_ref "$repo" 2>/dev/null || true)

    if [ "$EXECUTE" = 0 ]; then
      if [ -n "$HOLD_REQ" ]; then hold=$HOLD_REQ
      elif [ "$receipt" = pushed ]; then hold=0; else hold=86400; fi
      floor=$(hold_floor "$repo" "$receipt")
      if [ "$hold" -lt "$floor" ]; then hold=$floor; fi
      qa stage "$rp" INFO "DRY-RUN plan: receipt=$receipt gates=pass; would move to $qpath; hold=${hold}s; profile=$PROFILE"
      continue
    fi

    if git -C "$repo" ls-files --error-unmatch -- "$rel" >/dev/null 2>&1; then
      tracked=1; stage_mode="git-mv"
    else
      tracked=0; stage_mode="mv"
    fi

    mkdir -p "$qdir"
    if [ "$tracked" = 1 ]; then
      # git mv has no -q switch (verified: `error: unknown switch `q'');
      # quietness comes from committing with -q below.
      if ! git -C "$repo" mv -- "$rel" "${qpath#"$repo"/}"; then
        qa stage "$rp" REFUSED "git-mv-failed"; continue
      fi
    else
      if ! mv -- "$rp" "$qpath"; then
        qa stage "$rp" REFUSED "mv-failed"; continue
      fi
    fi

    if [ -d "$qpath" ]; then kind="dir"; else kind="file"; fi
    if [ "$kind" = dir ]; then
      msha=$(dir_digest "$qpath"); mcount=$(count_files "$qpath")
    else
      msha=$(file_sha "$qpath"); mcount=1
    fi

    if [ -n "$HOLD_REQ" ]; then hold=$HOLD_REQ
    elif [ "$receipt" = pushed ]; then hold=0; else hold=86400; fi
    floor=$(hold_floor "$repo" "$receipt")
    if [ "$hold" -lt "$floor" ]; then hold=$floor; fi

    stage_commit=""
    if [ "$tracked" = 1 ]; then
      # quarantine is a normal commit in the owning repo; if the commit
      # fails after a successful move the stage is HALF-DONE — refuse loud
      # and write no ticket (a half-staged state must not enter the flow).
      if ! stage_commit=$(git_commit_quarantine "$repo" "$rel" \
        "souji: quarantine $rel receipt=$receipt ticket=$id
Evidence: $V_LINE
Hold: ${hold}s; release requires hold + second check (impl-04)"); then
        qa stage "$rp" REFUSED "stage-commit-failed (artifact moved to $qpath but quarantine commit failed; operator must inspect — no ticket issued)"
        continue
      fi
    fi

    tickets_dir="$repo/.ufo-quarantine/.tickets"
    mkdir -p "$tickets_dir"
    tsv="$tickets_dir/$id.ticket.tsv"
    {
      printf 'ticket_version\t%s\n' "$TICKET_VERSION"
      printf 'id\t%s\n' "$id"
      printf 'created_utc\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      printf 'repo\t%s\n' "$repo"
      printf 'orig\t%s\n' "$rp"
      printf 'rel\t%s\n' "$rel"
      printf 'kind\t%s\n' "$kind"
      printf 'receipt\t%s\n' "$receipt"
      printf 'receipt_evidence\t%s\n' "$V_LINE"
      printf 'intro_commit\t%s\n' "${intro:--}"
      printf 'default_ref\t%s\n' "${dref:--}"
      printf 'hold_seconds\t%s\n' "$hold"
      printf 'stage_utc\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      printf 'stage_epoch\t%s\n' "$(date -u +%s)"
      printf 'stage_mode\t%s\n' "$stage_mode"
      printf 'stage_commit\t%s\n' "${stage_commit:--}"
      printf 'qpath\t%s\n' "$qpath"
      printf 'manifest_sha\t%s\n' "$msha"
      printf 'manifest_count\t%s\n' "$mcount"
      printf 'status\tstaged\n'
      printf 'event\t%s\tstaged\tmode=%s commit=%s profile=%s\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$stage_mode" "${stage_commit:--}" "$PROFILE"
    } >"$tsv"
    ticket_render_json "$tsv" >"${tsv%.tsv}.json"

    qa stage "$rp" OK "receipt=$receipt ticket=$tsv qpath=$qpath hold=${hold}s commit=${stage_commit:--}"
    unset tsv tickets_dir out
  done
}

# ------------------------------------------------------------ second check --

second_check() { # $1 tsv  $2 execute(0/1); rc 0 iff every check passes
  local tsv=$1 do_exec=$2
  local repo orig rel kind receipt intro dref hold stage_epoch stage_mode stage_commit qpath msha mcount
  repo=$(ticket_field "$tsv" repo);          orig=$(ticket_field "$tsv" orig)
  rel=$(ticket_field "$tsv" rel);            kind=$(ticket_field "$tsv" kind)
  receipt=$(ticket_field "$tsv" receipt);    intro=$(ticket_field "$tsv" intro_commit)
  dref=$(ticket_field "$tsv" default_ref);   hold=$(ticket_field "$tsv" hold_seconds)
  stage_epoch=$(ticket_field "$tsv" stage_epoch); stage_mode=$(ticket_field "$tsv" stage_mode)
  stage_commit=$(ticket_field "$tsv" stage_commit); qpath=$(ticket_field "$tsv" qpath)
  msha=$(ticket_field "$tsv" manifest_sha);  mcount=$(ticket_field "$tsv" manifest_count)

  # 1. artifact still in quarantine, bytes unchanged since staging
  if [ ! -e "$qpath" ]; then qa check "$qpath" REFUSED "qpath-missing"; return 1; fi
  if symlink_in_scope "$qpath"; then qa check "$qpath" REFUSED "symlink-in-scope"; return 1; fi
  local cmsha ccount
  if [ "$kind" = dir ]; then
    if ! cmsha=$(dir_digest "$qpath"); then
      qa check "$qpath" REFUSED "symlink-in-scope"; return 1
    fi
    ccount=$(count_files "$qpath")
  else
    cmsha=$(file_sha "$qpath"); ccount=1
  fi
  if [ "$cmsha" != "$msha" ] || [ "$ccount" != "$mcount" ]; then
    qa check "$qpath" REFUSED "manifest-mismatch (quarantined copy changed after staging)"; return 1
  fi

  # 2. original path not resurrected (worktree and index)
  if [ -e "$orig" ]; then
    qa check "$orig" REFUSED "resurrected (path exists again at original location)"; return 1
  fi
  if [ "$stage_mode" = git-mv ] && git -C "$repo" ls-files --error-unmatch -- "$rel" >/dev/null 2>&1; then
    qa check "$rel" REFUSED "still-in-index (original path tracked again)"; return 1
  fi

  # 3. receipt still derivable at second-check time (before the set check:
  #    a vanished default ref is the deeper diagnosis)
  local rref
  case "$receipt" in
    pushed)
      if ! rref=$(resolve_default_ref "$repo"); then
        qa check "$repo" REFUSED "receipt-lost (pushed: default ref no longer resolves)"; return 1
      fi
      if [ -z "$intro" ] || [ "$intro" = "-" ]; then
        qa check "$repo" REFUSED "receipt-lost (no intro commit in ticket)"; return 1
      fi
      if ! git -C "$repo" merge-base --is-ancestor "$intro" "$rref" 2>/dev/null; then
        qa check "$repo" REFUSED "receipt-lost (pushed: intro no longer ancestor of $rref)"; return 1
      fi
      ;;
    stale)
      local nrefs
      nrefs=$(count_live_refs "$orig" "$repo")
      if [ "$nrefs" != "0" ]; then
        qa check "$rel" REFUSED "receipt-lost (stale: $nrefs live reference(s) now)"; return 1
      fi
      ;;
    moved-to-obsidian)
      local LEDGER row sp ss vp vs found=0 vd
      LEDGER="${SOUJI_LEDGER:-$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv}"
      if [ -f "$LEDGER" ]; then
        while IFS=$'\t' read -r sp ss vp vs _rest; do
          if [ "$sp" = "$orig" ] && [ -n "$vs" ] && [ -e "$vp" ]; then found=1; break; fi
        done <"$LEDGER"
      fi
      if [ "$found" != 1 ]; then
        qa check "$orig" REFUSED "receipt-lost (obsidian: ledger row with live vault target gone)"; return 1
      fi
      if [ -d "$vp" ]; then
        if ! vd=$(dir_digest "$vp"); then
          qa check "$vp" REFUSED "receipt-lost (obsidian: symlink in vault scope)"; return 1
        fi
      else
        vd=$(file_sha "$vp")
      fi
      if [ "$vd" != "$vs" ]; then
        qa check "$vp" REFUSED "receipt-lost (obsidian: vault digest mismatch)"; return 1
      fi
      ;;
    *)
      qa check "$receipt" REFUSED "unknown-receipt-class"; return 1
      ;;
  esac

  # 4. no NEW unpushed commits touching the original path beyond the stage commit
  local ups allowed_ok=1 ups_n
  ups=$(unpushed_touching "$repo" "$rel")
  ups_n=$(printf '%s' "$ups" | grep -c . || true)
  if [ "$stage_mode" = git-mv ]; then
    [ "$ups_n" = 1 ] || allowed_ok=0
    [ "$ups" = "$stage_commit" ] || allowed_ok=0
  else
    [ "$ups_n" = 0 ] || allowed_ok=0
  fi
  if [ "$allowed_ok" != 1 ]; then
    qa check "$rel" REFUSED "unpushed-touching-changed (set: $(printf '%s ' $ups))"; return 1
  fi

  # 5. hold elapsed
  local now remaining
  now=$(date -u +%s)
  remaining=$(( stage_epoch + hold - now ))
  if [ "$remaining" -gt 0 ]; then
    qa check "$qpath" REFUSED "hold-not-elapsed (${remaining}s remaining of ${hold}s)"; return 1
  fi

  # deletion safety: qpath strictly inside <repo>/.ufo-quarantine/
  local qr qpr
  qr=$(realpath -m -- "$repo/.ufo-quarantine")
  qpr=$(realpath -m -- "$qpath")
  case "$qpr" in
    "$qr"/*) : ;;
    *) qa check "$qpath" REFUSED "qpath-outside-quarantine"; return 1 ;;
  esac

  if [ "$do_exec" = 1 ]; then
    rm -rf -- "$qpr"
    ticket_event "$tsv" released "second-check passed; deleted $qpr"
    ticket_render_json "$tsv" >"${tsv%.tsv}.json"
    if [ "$stage_mode" = git-mv ]; then
      local rcommit
      if rcommit=$(git_commit_quarantine "$repo" "$rel" \
        "souji: quarantine release ticket=$(ticket_field "$tsv" id) (hold ${hold}s + second check passed)
Deleted: $qpr"); then
        qa release "$qpr" OK "deleted; release_commit=$rcommit"
      else
        qa release "$qpr" REFUSED "deleted-but-release-commit-failed (artifact gone; bookkeeping commit needs operator attention)"
      fi
    else
      qa release "$qpr" OK "deleted (untracked mode, no commit)"
    fi
  else
    qa check "$qpath" INFO "second-check would PASS; hold elapsed; deletion authorized on --execute"
  fi
  return 0
}

do_status() { # $1 tsv
  local tsv=$1 hold stage_epoch now remaining status
  if [ ! -f "$tsv" ]; then qa status "$tsv" REFUSED "ticket-missing"; return 0; fi
  ticket_valid "$tsv" || return 0
  hold=$(ticket_field "$tsv" hold_seconds); stage_epoch=$(ticket_field "$tsv" stage_epoch)
  now=$(date -u +%s); remaining=$(( stage_epoch + hold - now ))
  status=$(ticket_field "$tsv" status)
  if [ "$remaining" -gt 0 ]; then
    qa status "$tsv" INFO "state=$status hold-remaining=${remaining}s"
  else
    qa status "$tsv" INFO "state=$status hold-elapsed"
  fi
  second_check "$tsv" 0 || true
}

do_release() { # $1 tsv
  local tsv=$1 status repo
  if [ ! -f "$tsv" ]; then qa release "$tsv" REFUSED "ticket-missing"; return 0; fi
  ticket_valid "$tsv" || return 0
  status=$(ticket_field "$tsv" status)
  if [ "$status" = released ]; then
    qa release "$tsv" REFUSED "already-released"; return 0
  fi
  if [ "$EXECUTE" = 1 ]; then
    repo=$(ticket_field "$tsv" repo)
    authorize_repo release "$repo" || return 0
  fi
  second_check "$tsv" "$EXECUTE" || true
}

do_gates() { # $1 repo  $2 path-or-empty
  local repo=$1 path=${2:-} nup ndirty dref rp rel
  if [ ! -d "$repo" ]; then qa gates "$repo" REFUSED "repo-missing"; return 0; fi
  if [ -n "$path" ]; then
    rp=$(realpath -m -- "$path"); rel=${rp#"$(realpath -m -- "$repo")"/}
    nup=$(unpushed_touching "$repo" "$rel" | grep -c . || true)
    ndirty=$(git -C "$repo" status --porcelain --untracked-files=all -- "$rel" 2>/dev/null | grep -c . || true)
    qa gates "$rel" INFO "gate1-unpushed-touching=$nup gate2-dirty-touching=$ndirty"
  else
    nup=$(git -C "$repo" log --branches --not --remotes --oneline 2>/dev/null | grep -c . || true)
    ndirty=$(git -C "$repo" status --porcelain 2>/dev/null | grep -c . || true)
    qa gates "$repo" INFO "repo-wide unpushed=$nup dirty=$ndirty"
  fi
  if dref=$(resolve_default_ref "$repo"); then
    qa gates "$repo" INFO "gate3-default-ref=$dref (pushed receipt establishable)"
    if [ "${nup:-0}" = 0 ] && [ "${ndirty:-0}" = 0 ]; then
      qa gates "$repo" INFO "OPEN-ACTION: none technical; operator sign-off still required before tickets authorize (r7 dissent trigger 1)"
    else
      qa gates "$repo" INFO "OPEN-ACTION: owning lane/operator pushes the repo so gate1/gate2 pass"
    fi
  else
    qa gates "$repo" INFO "gate3-default-ref=none (origin dead or absent -> pushed unestablishable; OPEN-ACTION: operator creates/restores the remote, then pushes)"
  fi
}

# --------------------------------------------------------------- selftest ---

ST_PASS=0; ST_FAIL=0; ST_NOTES=()
st_pass() { ST_PASS=$((ST_PASS+1)); ST_NOTES+=("PASS $1"); }
st_fail() { ST_FAIL=$((ST_FAIL+1)); ST_NOTES+=("FAIL $1"); }

st_expect_refused() { # $1 label  $2 needle  rest: command
  local label=$1 needle=$2 out
  shift 2
  out=$("$@" 2>&1) || true
  case "$out" in
    *REFUSED*"$needle"*) st_pass "$label" ;;
    *) st_fail "$label (wanted REFUSED*$needle*, got: $(printf '%s' "$out" | tail -2 | tr '\n' ';'))" ;;
  esac
}

# evaluate an ALREADY-CAPTURED output — mutating commands must run exactly once
qa_in() { # $1 label  $2 op  $3 status  $4 captured output
  local label=$1 op=$2 status=$3 out=$4 l found=0
  # QA lines: QA<TAB>op<TAB>key<TAB>status<TAB>detail  (status = field 4)
  while IFS= read -r l; do
    [ "$(printf '%s' "$l" | cut -f1)" = "QA" ] || continue
    [ "$(printf '%s' "$l" | cut -f2)" = "$op" ] || continue
    [ "$(printf '%s' "$l" | cut -f4)" = "$status" ] || continue
    found=1
  done <<<"$out"
  if [ "$found" = 1 ]; then st_pass "$label"; else
    st_fail "$label (wanted QA/$op/*/status=$status, got: $(printf '%s' "$out" | tail -2 | tr '\n' ';'))"
  fi
}

ticket_of() { # $1 command output -> first *.ticket.tsv path
  printf '%s' "$1" | sed -n 's/.*ticket=\([^ ]*\.ticket\.tsv\).*/\1/p' | head -1
}

fixture_git() { # $1 repo, rest: git args (fixture identity)
  local r=$1; shift
  git -C "$r" -c user.name=fixture -c user.email=fixture@invalid -c commit.gpgsign=false "$@"
}

FIXTURE_ROOTS=()
MR_DIR=""
mk_repo() { # sets MR_DIR to the repo path (arrays cannot cross $( ) bounds)
  local d
  d=$(mktemp -d "${TMPDIR:-/tmp}/souji-quarantine-selftest.XXXXXX")
  FIXTURE_ROOTS+=("$d")
  mkdir -p "$d/repo"
  fixture_git "$d/repo" init -q -b main "$d/repo" 2>/dev/null \
    || fixture_git "$d/repo" init -q "$d/repo"
  MR_DIR="$d/repo"
}

cleanup_fixtures() {
  local froot
  for froot in "${FIXTURE_ROOTS[@]:-}"; do
    [ -n "$froot" ] && [ -d "$froot" ] && rm -rf -- "$froot"
  done
  [ -n "${LG_DIR:-}" ] && [ -d "$LG_DIR" ] && rm -rf -- "$LG_DIR"
  return 0
}

run_selftest() {
  if [ -n "${SOUJI_QUARANTINE_SELFTEST_ACTIVE:-}" ]; then
    printf 'impl-04: refusing nested --selftest\n' >&2; exit 1
  fi
  export SOUJI_QUARANTINE_SELFTEST_ACTIVE=1
  # every fixture is removed on process exit, including abort paths
  trap cleanup_fixtures EXIT
  local R R2 tsv tsv2 out cnt h f

  # ---- fixture A: pushed happy path + dry-run proof (S1/S8) -----------
  mk_repo; R=$MR_DIR
  printf 'payload-a\n' >"$R/a.txt"
  fixture_git "$R" add a.txt
  fixture_git "$R" commit -q -m "add a.txt"
  fixture_git "$R" update-ref refs/remotes/origin/main HEAD
  cnt=$(fixture_git "$R" rev-list --count HEAD)
  out=$("$SELF" --stale-days 1 stage "$R/a.txt" 2>&1) || true
  qa_in "S8 dry-run prints plan" stage INFO "$out"
  [ "$cnt" = "$(fixture_git "$R" rev-list --count HEAD)" ] \
    && st_pass "S8 dry-run zero commits" || st_fail "S8 dry-run committed"
  [ ! -e "$R/.ufo-quarantine" ] \
    && st_pass "S8 dry-run zero quarantine dir" || st_fail "S8 dry-run created quarantine dir"

  out=$("$SELF" --execute stage "$R/a.txt" 2>&1) || true
  qa_in "S1 stage pushed OK" stage OK "$out"
  tsv=$(ticket_of "$out")
  if [ -n "$tsv" ] && [ -f "$tsv" ]; then st_pass "S1 ticket written"; else st_fail "S1 ticket missing ($tsv)"; fi
  [ ! -e "$R/a.txt" ] && st_pass "S1 orig gone" || st_fail "S1 orig still present"
  ls "$R/.ufo-quarantine/"*/*"__a.txt" >/dev/null 2>&1 \
    && st_pass "S1 quarantined copy present" || st_fail "S1 quarantine copy missing"
  [ "$(fixture_git "$R" rev-list --count HEAD)" = "$((cnt+1))" ] \
    && st_pass "S1 quarantine commit appended" || st_fail "S1 commit count"
  # whole-rename invariant: the stage commit must touch the ORIGINAL path too
  [ "$(fixture_git "$R" log --branches --not --remotes --format=%H -- a.txt)" = "$(fixture_git "$R" rev-parse HEAD)" ] \
    && st_pass "S1 rename committed whole (orig deletion in stage commit)" \
    || st_fail "S1 rename split (orig path not in stage commit)"
  out=$("$SELF" status --ticket "$tsv" 2>&1) || true
  qa_in "S1 second-check preview passes" check INFO "$out"
  out=$("$SELF" --execute release --ticket "$tsv" 2>&1) || true
  qa_in "S1 release OK" release OK "$out"
  ls "$R/.ufo-quarantine/"*/*"__a.txt" >/dev/null 2>&1 \
    && st_fail "S1 still in quarantine" || st_pass "S1 quarantine deleted"
  [ "$(ticket_field "$tsv" status)" = released ] \
    && st_pass "S1 ticket released" || st_fail "S1 ticket status"
  out=$("$SELF" --execute release --ticket "$tsv" 2>&1) || true
  case "$out" in *REFUSED*"already-released"*) st_pass "S1b double release refused" ;; *) st_fail "S1b (got: $out)" ;; esac

  # ---- fixture B: hold enforcement on stale (S2) ----------------------
  mk_repo; R=$MR_DIR
  mkdir -p "$R/.scratch"
  printf 'junk\n' >"$R/.scratch/old.out"
  touch -d "2026-10-01" "$R/.scratch/old.out"
  out=$("$SELF" --execute --stale-days 1 --gates skill stage "$R/.scratch/old.out" 2>&1) || true
  qa_in "S2 stage stale OK (skill profile)" stage OK "$out"
  tsv=$(ticket_of "$out")
  h=$(ticket_field "$tsv" hold_seconds)
  [ "$h" = 86400 ] && st_pass "S2 stale hold default 24h" || st_fail "S2 hold=$h"
  st_expect_refused "S2 release refused before hold" "hold-not-elapsed" \
    "$SELF" --execute release --ticket "$tsv"
  # strict profile refuses the same untracked target (S15 rule)
  printf 'junk2\n' >"$R/.scratch/old2.out"
  touch -d "2026-10-01" "$R/.scratch/old2.out"
  st_expect_refused "S2b strict profile refuses untracked" "gate2-untracked" \
    "$SELF" --execute --stale-days 1 stage "$R/.scratch/old2.out"
  # fixture-only floor bypass proves release can pass after a real short hold
  out=$(SOUJI_TEST_HOLD_FLOOR=1 "$SELF" --execute --stale-days 1 --gates skill \
        --hold-seconds 1 stage "$R/.scratch/old2.out" 2>&1) || true
  tsv2=$(ticket_of "$out")
  h=$(ticket_field "$tsv2" hold_seconds)
  [ "$h" = 1 ] && st_pass "S2c fixture floor bypass honored" || st_fail "S2c hold=$h"
  st_expect_refused "S2c release refused at t=0" "hold-not-elapsed" \
    "$SELF" --execute release --ticket "$tsv2"
  sleep 1.2
  out=$("$SELF" --execute release --ticket "$tsv2" 2>&1) || true
  qa_in "S2c release after 1s hold OK" release OK "$out"

  # ---- fixture C: second check bites (S3/S4/S5/S7) --------------------
  mk_repo; R=$MR_DIR
  for f in t1 t2 t3 t4; do printf 'payload-%s\n' "$f" >"$R/$f.txt"; done
  fixture_git "$R" add t1.txt t2.txt t3.txt t4.txt
  fixture_git "$R" commit -q -m "add t1..t4"
  fixture_git "$R" update-ref refs/remotes/origin/main HEAD
  local tsv_t1 tsv_t2 tsv_t3 tsv_t4
  for f in t1 t2 t3 t4; do
    out=$("$SELF" --execute stage "$R/$f.txt" 2>&1) || true
    eval "tsv_$f=\$(ticket_of \"\$out\")"
  done
  # S3 tamper: rewrite the quarantined copy in place (date-dir glob depth)
  printf 'tampered\n' > "$R/.ufo-quarantine/"*/*"__t1.txt"
  st_expect_refused "S3 tamper refused" "manifest-mismatch" \
    "$SELF" --execute release --ticket "$tsv_t1"
  # S4 resurrect: recreate the original path
  printf 'resurrected\n' > "$R/t2.txt"
  st_expect_refused "S4 resurrect refused" "resurrected" \
    "$SELF" --execute release --ticket "$tsv_t2"
  # S5 new unpushed commit touching the original path, WITHOUT resurrecting
  # the worktree: build it with plumbing (hash-object/mktree/commit-tree) on
  # a side branch off the PRE-STAGE commit (where t3.txt still exists), so
  # the unpushed-set check (not resurrect) is what fires.
  local blob tree basec newsneak
  basec=$(fixture_git "$R" rev-parse refs/remotes/origin/main)
  blob=$(printf 'sneaky edit\n' | fixture_git "$R" hash-object -w --stdin)
  tree=$(fixture_git "$R" ls-tree "$basec" \
        | awk -v b="$blob" '{ if ($4 == "t3.txt") printf "%s %s %s\t%s\n", $1, $2, b, $4; else printf "%s %s %s\t%s\n", $1, $2, $3, $4 }' \
        | fixture_git "$R" mktree)
  newsneak=$(fixture_git "$R" commit-tree "$tree" -p "$basec" -m "sneak: edit t3.txt post-stage")
  fixture_git "$R" update-ref refs/heads/sneak "$newsneak"
  st_expect_refused "S5 unpushed-touching refused" "unpushed-touching-changed" \
    "$SELF" --execute release --ticket "$tsv_t3"
  # S7 receipt lost: the default ref vanishes (origin deleted/restored)
  fixture_git "$R" update-ref -d refs/remotes/origin/main
  st_expect_refused "S7 receipt-lost refused" "receipt-lost" \
    "$SELF" --execute release --ticket "$tsv_t4"

  # ---- fixture D: stage-time refusals (S6 dirty, S10 secrets) ---------
  mk_repo; R=$MR_DIR
  printf 'v1\n' >"$R/dirty.txt"
  fixture_git "$R" add dirty.txt
  fixture_git "$R" commit -q -m "add dirty"
  fixture_git "$R" update-ref refs/remotes/origin/main HEAD
  printf 'v2 uncommitted\n' >"$R/dirty.txt"
  st_expect_refused "S6 dirty target refused at stage" "gate2-dirty-tracked" \
    "$SELF" --execute stage "$R/dirty.txt"
  [ -f "$R/dirty.txt" ] && st_pass "S6 nothing moved" || st_fail "S6 file moved despite refusal"
  printf 'k\n' >"$R/id_key.pem"
  st_expect_refused "S10 secret-shaped path refused" "receipt=NOT-SAFE" \
    "$SELF" --execute stage "$R/id_key.pem"
  [ ! -e "$R/.ufo-quarantine" ] \
    && st_pass "S10 no quarantine created" || st_fail "S10 quarantine dir exists"

  # ---- ticket validation (S11) ----------------------------------------
  mk_repo; R=$MR_DIR
  st_expect_refused "S11 missing ticket refused" "ticket-missing" \
    "$SELF" --execute release --ticket "$R/nope.ticket.tsv"
  printf 'garbage not tsv\n' >"$R/bad.ticket.tsv"
  st_expect_refused "S11 malformed ticket refused" "ticket-invalid" \
    "$SELF" --execute release --ticket "$R/bad.ticket.tsv"

  # ---- live-repo guard (S9) -------------------------------------------
  # deliberately NOT named souji-quarantine-selftest.* : the repo must be
  # refused as non-fixture even though it sits under TMPDIR.
  local LG="${TMPDIR:-/tmp}/impl04-live-guard.$$"; LG_DIR=$LG
  mkdir -p "$LG/repo"
  fixture_git "$LG/repo" init -q -b main "$LG/repo"
  printf 'x\n' >"$LG/repo/x.txt"
  fixture_git "$LG/repo" add x.txt
  fixture_git "$LG/repo" commit -q -m "x"
  cnt=$(fixture_git "$LG/repo" rev-list --count HEAD)
  st_expect_refused "S9 live repo refused" "live-repo-not-authorized" \
    "$SELF" --execute stage "$LG/repo/x.txt"
  [ ! -e "$LG/repo/.ufo-quarantine" ] \
    && st_pass "S9 live repo untouched" || st_fail "S9 quarantine created on live repo"
  [ "$cnt" = "$(fixture_git "$LG/repo" rev-list --count HEAD)" ] \
    && st_pass "S9 live repo no commits" || st_fail "S9 live repo mutated"
  rm -rf -- "$LG"

  # ---- hold clamp: below-floor requests clamp UP (S13) -----------------
  mk_repo; R=$MR_DIR
  printf 'p\n' >"$R/p.txt"
  fixture_git "$R" add p.txt
  fixture_git "$R" commit -q -m p
  fixture_git "$R" update-ref refs/remotes/origin/main HEAD
  out=$("$SELF" --execute --hold-seconds 0 stage "$R/p.txt" 2>&1) || true
  local tsp; tsp=$(ticket_of "$out")
  [ "$(ticket_field "$tsp" hold_seconds)" = 0 ] \
    && st_pass "S13 pushed hold=0 honored" || st_fail "S13 hold"

  # ---- gates subcommand (S14) ------------------------------------------
  out=$("$SELF" gates "$R" 2>&1) || true
  case "$out" in
    *"gate3-default-ref=refs/remotes/origin/main"*) st_pass "S14 gates default-ref" ;;
    *) st_fail "S14 gates (got: $out)" ;;
  esac
  mk_repo; R2=$MR_DIR
  out=$("$SELF" gates "$R2" 2>&1) || true
  case "$out" in
    *"gate3-default-ref=none"*) st_pass "S14 gates dead-origin OPEN-ACTION" ;;
    *) st_fail "S14 gates dead origin (got: $out)" ;;
  esac

  local froot
  for froot in "${FIXTURE_ROOTS[@]}"; do rm -rf -- "$froot"; done

  printf 'selftest: %d pass, %d fail\n' "$ST_PASS" "$ST_FAIL"
  local n
  for n in "${ST_NOTES[@]}"; do printf '  %s\n' "$n"; done
  [ "$ST_FAIL" = 0 ] || QA_STATUS=1
  return 0
}

# ------------------------------------------------------------------ main ----

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --execute) EXECUTE=1; shift ;;
    --dry-run) EXECUTE=0; shift ;;
    --hold-seconds) [ "$#" -ge 2 ] || die_usage "--hold-seconds needs a value"; HOLD_REQ=$2; shift 2 ;;
    --hold-seconds=*) HOLD_REQ=${1#*=}; shift ;;
    --stale-days) [ "$#" -ge 2 ] || die_usage "--stale-days needs a value"; STALE_DAYS=$2; shift 2 ;;
    --stale-days=*) STALE_DAYS=${1#*=}; shift ;;
    --gates) [ "$#" -ge 2 ] || die_usage "--gates needs strict|skill"
             case "$2" in strict|skill) PROFILE=$2 ;; *) die_usage "--gates must be strict|skill" ;; esac
             shift 2 ;;
    --gates=*) PROFILE=${1#*=}; case "$PROFILE" in strict|skill) ;; *) die_usage "--gates must be strict|skill" ;; esac; shift ;;
    --verify) [ "$#" -ge 2 ] || die_usage "--verify needs a path"; VERIFY_BIN=$2; shift 2 ;;
    --verify=*) VERIFY_BIN=${1#*=}; shift ;;
    -h|--help) sed -n '2,70p' "$SELF" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --) shift; break ;;
    stage|status|release|gates)
      [ -z "$CMD" ] || die_usage "multiple commands given"
      CMD=$1; shift; break ;;
    *) die_usage "unknown argument: $1" ;;
  esac
done
[ "$SELFTEST" = 1 ] || [ -n "$CMD" ] || die_usage "need a command: stage|status|release|gates|--selftest"

case "$HOLD_REQ" in ''|*[!0-9]*) [ -z "$HOLD_REQ" ] || die_usage "--hold-seconds must be a non-negative integer" ;; esac
case "$STALE_DAYS" in ''|*[!0-9]*) [ -z "$STALE_DAYS" ] || die_usage "--stale-days must be a non-negative integer" ;; esac

if [ "$SELFTEST" = 1 ]; then
  run_selftest
  if [ "$JSON" = 1 ]; then emit_json; fi
  exit "$QA_STATUS"
fi

case "$CMD" in
  stage)
    [ "$#" -ge 1 ] || die_usage "stage needs at least one path"
    do_stage "$@"
    ;;
  status)
    [ "$1" = "--ticket" ] && [ -n "${2:-}" ] || die_usage "status needs --ticket <file>"
    do_status "$2"
    ;;
  release)
    [ "$1" = "--ticket" ] && [ -n "${2:-}" ] || die_usage "release needs --ticket <file>"
    do_release "$2"
    ;;
  gates)
    [ "$#" -ge 1 ] || die_usage "gates needs a repo path"
    do_gates "$@"
    ;;
esac

if [ "$JSON" = 1 ]; then emit_json; fi
exit 0
