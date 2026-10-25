#!/usr/bin/env bash
# souji-verify (impl-16) — receipt-based artifact verdict tool, souji round 2.
# Implements tools/souji-verify.spec.md (binding). Seat S16 deliverable.
#
# Read-only over every surface it inspects. bash + coreutils + git + rg only.
#
# CLI:
#   [--selftest] [--stale-days N] [--json] <path>...
# Output, one line per target:
#   VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-reason<TAB>decisive-evidence
# Exit codes: 0 = evaluated clean; 1 = selftest failure or evaluation error;
#             2 = usage. No other codes.
#
# Mechanical adaptations of the spec, both documented and lossless:
# - D3 sweep: this ripgrep (15.x) dropped --basename, so a live reference is
#   the union of (a) a file whose basename equals the artifact name and (b) a
#   content match of that name, both under the spec's exclusion globs, with
#   the artifact itself excluded (a file is not a reference to itself).
# - SOUJI_LEDGER overrides the ledger path; the default is the spec's
#   <repo>/corpus/knowledge/obsidian-ledger.tsv. Only --selftest sets the
#   override, so fixture runs never read the live ledger.
#
# Two conservative guards beyond the letter of the spec (both only ever turn
# SAFE into NOT-SAFE, never the reverse; pinned by selftest F9c/F9d and the
# directory branch of the pushed receipt):
# - the spec's local-master fallback is used only when the repo has at least
#   one refs/remotes/* ref; a repo with no remote refs can never evidence a
#   push, so its committed artifacts are NOT-SAFE(pushed-unverifiable).
# - a directory artifact satisfies the pushed receipt only when nothing in it
#   is uncommitted and no unpushed commit touches it; the introducing commit
#   alone does not prove the directory's live content is pushed.
set -eEuo pipefail
export LC_ALL=C
export GIT_OPTIONAL_LOCKS=0

SELF=$(realpath -m -- "${BASH_SOURCE[0]}")
REPO_DIR=$(dirname -- "$(dirname -- "$SELF")")
LEDGER=${SOUJI_LEDGER:-$REPO_DIR/corpus/knowledge/obsidian-ledger.tsv}
SHOKUNIN_ROOT=${SHOKUNIN_ROOT:-$(dirname -- "$REPO_DIR")}
STALE_DAYS=1
JSON=0
DO_SELFTEST=0
TARGETS=()
CURR=''
ERRORS=0

trap 'rc=$?; printf "souji-verify: internal error rc=%s near line %s target=%s\n" \
  "$rc" "${BASH_LINENO[0]:-?}" "${CURR:-}" >&2; exit 1' ERR

SELFTEST_TMP=''
cleanup_selftest() {
  if [ -n "${SELFTEST_TMP:-}" ]; then rm -rf -- "$SELFTEST_TMP"; fi
  return 0
}
trap cleanup_selftest EXIT

usage() {
  printf 'usage: %s [--selftest] [--stale-days N] [--json] <path>...\n' \
    "$(basename -- "$SELF")"
}

# ---------- argument parsing ----------

while [ $# -gt 0 ]; do
  case $1 in
    --selftest) DO_SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --stale-days)
      shift
      [ $# -gt 0 ] || { usage >&2; exit 2; }
      STALE_DAYS=$1; shift ;;
    --stale-days=*) STALE_DAYS=${1#--stale-days=}; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; while [ $# -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    -*) usage >&2; exit 2 ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done
case $STALE_DAYS in ''|*[!0-9]*) usage >&2; exit 2 ;; esac

for _b in git rg sha256sum realpath stat date mktemp find xargs awk grep sed \
          wc cut tr sort head dirname basename; do
  command -v "$_b" >/dev/null 2>&1 || { printf 'souji-verify: missing required command: %s\n' "$_b" >&2; exit 1; }
done

# ---------- output ----------

json_esc() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  printf '%s' "$s"
}

emit() { # raw verdict receipt-or-reason evidence
  local raw=$1 v=$2 r=$3 ev=$4
  if [ "$JSON" = 1 ]; then
    printf '{"path":"%s","verdict":"%s","receipt":"%s","detail":"%s"}\n' \
      "$(json_esc "$raw")" "$v" "$r" "$(json_esc "$ev")"
  else
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$raw" "$v" "$r" "$ev"
  fi
}

# ---------- shared helpers ----------

is_secret_path() { # never read files whose name is secret-shaped
  local p=$1 b
  b=${p##*/}
  case $b in
    *.env|*credential*|*secret*|id_*|*.pem) return 0 ;;
  esac
  case $p in
    */.env|*/.env/*) return 0 ;;
  esac
  return 1
}

is_scratch_path() {
  local p=$1 b
  b=${p##*/}
  case $p in */.scratch/*) return 0 ;; esac
  case $b in
    *.out|*.log) return 0 ;;
    *checkpoint*.json|*checkpoint*.png) return 0 ;;
    *-draft.*) return 0 ;;
  esac
  return 1
}

count_lines() { # stdout line count of a command; 0 on any failure
  { "$@" 2>/dev/null || true; } | wc -l | tr -d '[:space:]'
}

num_out() { # numeric stdout of a command (e.g. rev-list --count); 0 on failure
  local n
  n=$({ "$@" 2>/dev/null || true; } | tr -d '[:space:]')
  if [ -z "$n" ]; then n=0; fi
  printf '%s' "$n"
}

resolve_default_ref() { # D1: repo -> refname on stdout, or nothing
  local repo=$1 b refs n
  b=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null \
      | sed 's@^origin/@@' || true)
  if [ -n "$b" ] && git -C "$repo" rev-parse --verify --quiet "refs/remotes/origin/$b" >/dev/null 2>&1; then
    printf 'refs/remotes/origin/%s' "$b"
    return 0
  fi
  refs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null \
         | grep -v '^refs/remotes/origin/HEAD$' || true)
  n=$(printf '%s\n' "$refs" | grep -c . || true)
  if [ "$n" = 1 ]; then
    printf '%s' "$refs"
    return 0
  fi
  # The spec's last fallback is the local branch 'master'. A repository with
  # no remote-tracking refs at all cannot evidence a push, so the fallback is
  # used only when at least one refs/remotes/* ref exists.
  local rrefs
  rrefs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null || true)
  if [ -n "$rrefs" ] && git -C "$repo" rev-parse --verify --quiet refs/heads/master >/dev/null 2>&1; then
    printf 'refs/heads/master'
    return 0
  fi
  return 1
}

ledger_match() { # $1 normalized path; sets LM_ROW / LM_VAULT; 0 on full match
  local p=$1 rown=0 src ssha vpath vsha rest nsrc s vs
  LM_ROW=''
  LM_VAULT=''
  [ -f "$LEDGER" ] || return 1
  while IFS=$'\t' read -r src ssha vpath vsha rest; do
    rown=$((rown + 1))
    [ "$rown" -eq 1 ] && continue
    [ -n "${src:-}" ] || continue
    nsrc=$(realpath -m -- "$src" 2>/dev/null || true)
    [ "$nsrc" = "$p" ] || continue
    [ -n "${vpath:-}" ] || continue
    if [ -f "$p" ]; then
      is_secret_path "$vpath" && continue
      [ -f "$vpath" ] || continue
      s=$(sha256sum -- "$p" 2>/dev/null | cut -d' ' -f1 || true)
      [ -n "$s" ] && [ "${s,,}" = "${ssha,,}" ] || continue
      vs=$(sha256sum -- "$vpath" 2>/dev/null | cut -d' ' -f1 || true)
      [ -n "$vs" ] && [ "${vs,,}" = "${vsha,,}" ] || continue
    else
      [ -e "$vpath" ] || continue
    fi
    LM_ROW=$rown
    LM_VAULT=$vpath
    return 0
  done < "$LEDGER"
  return 1
}

count_refs() { # root name selfpath -> integer reference count (D3 sweep)
  local root=$1 name=$2 selfp=$3 hits=0 f rel files clist
  files=$(cd "$root" 2>/dev/null && rg --files --no-ignore --hidden --no-messages . \
      -g '!.git' -g '!souji-shokunin/census/**' -g '!souji-shokunin/tests/**' \
      -g '!**/.ufo-quarantine/**' 2>/dev/null || true)
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    rel=${f#./}
    [ "${rel##*/}" = "$name" ] || continue
    [ "$(realpath -m -- "$root/$rel" 2>/dev/null || true)" = "$selfp" ] && continue
    hits=$((hits + 1))
  done <<< "$files"
  clist=$(cd "$root" 2>/dev/null && rg -l -F --no-ignore --hidden --no-messages -e "$name" . \
      -g '!.git' -g '!souji-shokunin/census/**' -g '!souji-shokunin/tests/**' \
      -g '!**/.ufo-quarantine/**' 2>/dev/null || true)
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    rel=${f#./}
    [ "$(realpath -m -- "$root/$rel" 2>/dev/null || true)" = "$selfp" ] && continue
    hits=$((hits + 1))
  done <<< "$clist"
  printf '%s' "$hits"
}

worktree_listed_in() { # owner path -> 0 when path is a linked worktree of owner
  local owner=$1 p=$2 line cur top
  top=$(git -C "$owner" rev-parse --show-toplevel 2>/dev/null || true)
  top=$(realpath -m -- "$top" 2>/dev/null || true)
  while IFS= read -r line; do
    case $line in
      'worktree '*)
        cur=$(realpath -m -- "${line#worktree }" 2>/dev/null || true)
        [ "$cur" = "$p" ] || continue
        [ "$cur" = "$top" ] && return 1
        return 0 ;;
    esac
  done < <(git -C "$owner" worktree list --porcelain 2>/dev/null || true)
  return 1
}

find_owner_for_worktree() { # p -> owner root on stdout, or nothing
  local p=$1 d line cand=''
  if [ -f "$p/.git" ]; then
    line=$(head -n 1 -- "$p/.git" 2>/dev/null || true)
    case $line in
      gitdir:*)
        cand=${line#gitdir:}
        cand=${cand# }
        cand=${cand%$'\r'}
        case $cand in
          */.git/worktrees/*) cand=${cand%%/.git/worktrees/*} ;;
          *) cand='' ;;
        esac ;;
    esac
    if [ -n "$cand" ] && [ -d "$cand" ] && worktree_listed_in "$cand" "$p"; then
      realpath -m -- "$cand"
      return 0
    fi
  fi
  for d in "$SHOKUNIN_ROOT"/*-shokunin "$SHOKUNIN_ROOT"; do
    [ -d "$d" ] || continue
    [ -e "$d/.git" ] || continue
    [ "$(realpath -m -- "$d" 2>/dev/null || true)" = "$p" ] && continue
    if worktree_listed_in "$d" "$p"; then
      realpath -m -- "$d"
      return 0
    fi
  done
  return 1
}

# ---------- kind branches ----------

evaluate_worktree() {
  local raw=$1 p=$2 owner=$3
  local present=0 dir=absent line cur inblock=0 head='' branch=''
  local unique=0 unp=0 dirty=0 bshort=''
  [ -d "$p" ] && { present=1; dir=present; }
  while IFS= read -r line; do
    case $line in
      'worktree '*)
        cur=$(realpath -m -- "${line#worktree }" 2>/dev/null || true)
        inblock=0
        [ "$cur" = "$p" ] && inblock=1 ;;
      'HEAD '*) [ "$inblock" = 1 ] && head=${line#HEAD } ;;
      'branch '*) [ "$inblock" = 1 ] && branch=${line#branch } ;;
    esac
  done < <(git -C "$owner" worktree list --porcelain 2>/dev/null || true)
  if [ -n "$head" ]; then
    unique=$(count_lines git -C "$owner" log --oneline "$head" --not --all)
  fi
  if [ -n "$branch" ]; then
    bshort=${branch#refs/heads/}
    unp=$(count_lines git -C "$owner" log --oneline "$branch" --not --remotes)
  fi
  if [ -n "$branch" ] && [ "$unp" != 0 ]; then
    emit "$raw" NOT-SAFE unpushed-branch "branch=$bshort unpushed=$unp dir=$dir"
    return 0
  fi
  if [ "$present" = 0 ] && [ "$unique" = 0 ]; then
    emit "$raw" SAFE metadata-prune "dir=absent unique=0 head=${head:-none} owner=$owner"
    return 0
  fi
  if [ "$present" = 1 ]; then
    dirty=$(count_lines git -C "$p" status --porcelain)
    if [ "$dirty" != 0 ]; then
      emit "$raw" NOT-SAFE dirty "dirty=$dirty dir=present"
      return 0
    fi
  fi
  if [ "$present" = 0 ]; then
    emit "$raw" NOT-SAFE unpushed-commits "dir=absent unique=$unique head=${head:-none}"
    return 0
  fi
  emit "$raw" NOT-SAFE none "dir=present unique=$unique dirty=$dirty branch=${bshort:-detached} owner=$owner"
}

evaluate_repo_root() {
  local raw=$1 p=$2 unpushed=0 dirty=0 reason=none refs=''
  if ledger_match "$p"; then
    emit "$raw" SAFE moved-to-obsidian "ledger_row=$LM_ROW vault=$LM_VAULT"
    return 0
  fi
  if git -C "$p" rev-parse --verify --quiet HEAD >/dev/null 2>&1; then
    refs=$(git -C "$p" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null || true)
    if [ -n "$refs" ]; then
      unpushed=$(num_out git -C "$p" rev-list --count HEAD --not --remotes)
    else
      unpushed=$(num_out git -C "$p" rev-list --count HEAD)
    fi
  fi
  dirty=$(count_lines git -C "$p" status --porcelain)
  if [ "$unpushed" != 0 ] && [ "$dirty" != 0 ]; then
    reason=unpushed-dirty
  elif [ "$unpushed" != 0 ]; then
    reason=unpushed
  elif [ "$dirty" != 0 ]; then
    reason=dirty
  fi
  emit "$raw" NOT-SAFE "$reason" "unpushed=$unpushed dirty=$dirty"
}

evaluate_artifact() {
  local raw=$1 p=$2
  local dir repo='' rel='' ref_root='' push_state='no-commit' intro='' ref='' refs=0 m='' now=0 age=0
  local nrefs=0 unp_touching=0 dirty_inside=0
  dir=$(dirname -- "$p")
  repo=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null || true)
  if [ -n "$repo" ]; then
    repo=$(realpath -m -- "$repo" 2>/dev/null || true)
    case $p in
      "$repo"/*) rel=${p#"$repo"/} ;;
      *) repo='' ;;
    esac
  fi
  if [ -n "$repo" ]; then
    ref_root=$repo
  else
    push_state=no-repo
    ref_root=$dir
  fi
  if [ -n "$repo" ]; then
    intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$rel" 2>/dev/null || true)
    if [ -n "$intro" ]; then
      ref=$(resolve_default_ref "$repo" || true)
      if [ -z "$ref" ]; then
        nrefs=$(count_lines git -C "$repo" for-each-ref --format='%(refname)' refs/remotes)
        emit "$raw" NOT-SAFE pushed-unverifiable "intro=$intro remote_refs=$nrefs"
        return 0
      fi
      if git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
        # Directory artifacts must be fully reflected in pushed state too: a
        # live dir with unpushed commits touching it or uncommitted content
        # is not removable on the pushed receipt.
        if [ -d "$p" ]; then
          unp_touching=$(count_lines git -C "$repo" log --oneline HEAD --not --remotes -- "$rel")
          dirty_inside=$(count_lines git -C "$repo" status --porcelain -- "$rel")
          if [ "$unp_touching" != 0 ] || [ "$dirty_inside" != 0 ]; then
            if [ "$unp_touching" != 0 ]; then
              emit "$raw" NOT-SAFE unpushed "dir=yes unpushed_touching=$unp_touching dirty_inside=$dirty_inside intro=$intro ref=$ref"
            else
              emit "$raw" NOT-SAFE dirty "dir=yes unpushed_touching=0 dirty_inside=$dirty_inside intro=$intro ref=$ref"
            fi
            return 0
          fi
        fi
        emit "$raw" SAFE pushed "commit=$intro ref=$ref"
        return 0
      fi
      push_state="local-only ref=$ref"
    fi
  fi
  if ledger_match "$p"; then
    emit "$raw" SAFE moved-to-obsidian "ledger_row=$LM_ROW vault=$LM_VAULT"
    return 0
  fi
  if is_scratch_path "$p"; then
    refs=$(count_refs "$ref_root" "${p##*/}" "$p")
    m=$(stat -c %Y -- "$p" 2>/dev/null || true)
    now=$(date +%s)
    if [ -n "$m" ]; then age=$(( (now - m) / 86400 )); else m=$now; fi
    if [ "$refs" = 0 ] && [ $(( now - m )) -gt $(( STALE_DAYS * 86400 )) ]; then
      emit "$raw" SAFE stale "refs=0 age_days=$age"
      return 0
    fi
    emit "$raw" NOT-SAFE none "push=$push_state refs=$refs age_days=$age scratch=yes"
    return 0
  fi
  emit "$raw" NOT-SAFE none "push=$push_state scratch=no"
}

evaluate() {
  local raw=$1 p='' wt='' is_repo_root=0
  if [ -z "$raw" ]; then
    emit "$raw" NOT-SAFE unreachable empty-target
    return 0
  fi
  p=$(realpath -m -- "$raw" 2>/dev/null || true)
  if [ -z "$p" ]; then
    emit "$raw" NOT-SAFE unreachable unresolvable-path
    return 0
  fi
  if is_secret_path "$p"; then
    emit "$raw" NOT-SAFE secrets-refusal "basename=${p##*/}"
    return 0
  fi
  [ -d "$p/.git" ] && is_repo_root=1
  if [ "$is_repo_root" = 0 ] && [ ! -f "$p" ]; then
    wt=$(find_owner_for_worktree "$p" || true)
  fi
  if [ -n "$wt" ]; then
    evaluate_worktree "$raw" "$p" "$wt"
    return 0
  fi
  if [ "$is_repo_root" = 1 ]; then
    evaluate_repo_root "$raw" "$p"
    return 0
  fi
  if [ ! -e "$p" ]; then
    emit "$raw" NOT-SAFE unreachable missing
    return 0
  fi
  evaluate_artifact "$raw" "$p"
}

# ---------- selftest fixtures (git plumbing only: no worktree-mutating verbs) ----------

fx_init() { git -c init.defaultBranch=master init -q -- "$1"; }

fx_stage() { # repo rel content
  local repo=$1 rel=$2 content=$3 d blob
  d=$(dirname -- "$rel")
  [ "$d" = "." ] || mkdir -p -- "$repo/$d"
  printf '%s\n' "$content" > "$repo/$rel"
  blob=$(printf '%s\n' "$content" | git -C "$repo" hash-object -w --stdin)
  git -C "$repo" update-index --add --cacheinfo "100644,$blob,$rel"
}

fx_commit() { # repo parent('' or sha) msg -> sha
  local repo=$1 parent=$2 msg=$3 tree sha
  tree=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(git -C "$repo" commit-tree "$tree" -p "$parent" -m "$msg")
  else
    sha=$(git -C "$repo" commit-tree "$tree" -m "$msg")
  fi
  printf '%s' "$sha"
}

fx_head() { # repo branch sha
  git -C "$1" update-ref "refs/heads/$2" "$3"
  git -C "$1" symbolic-ref HEAD "refs/heads/$2"
}

fx_index() { git -C "$1" read-tree "$2"; }

build_fixtures() {
  local fix=$1 repo
  local c1 c2 s1 s2 v1 zero

  # F1/F2: pushed and local-only introducing commits
  repo=$fix/r-pushed
  fx_init "$repo"
  fx_stage "$repo" a1.txt one
  c1=$(fx_commit "$repo" '' c1)
  fx_stage "$repo" other.txt two
  c2=$(fx_commit "$repo" "$c1" c2)
  fx_head "$repo" master "$c2"
  git -C "$repo" update-ref refs/remotes/origin/master "$c2"
  git -C "$repo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  fx_index "$repo" "$c2"
  FIX_PUSHED_COMMIT=$c1

  repo=$fix/r-local
  fx_init "$repo"
  fx_stage "$repo" other2.txt o2
  c1=$(fx_commit "$repo" '' c1)
  fx_stage "$repo" a2.txt a2
  c2=$(fx_commit "$repo" "$c1" c2)
  fx_head "$repo" master "$c2"
  git -C "$repo" update-ref refs/remotes/origin/master "$c1"
  git -C "$repo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  fx_index "$repo" "$c2"

  # F2b: no origin refs, no local master -> default ref unresolvable
  repo=$fix/r-noref
  fx_init "$repo"
  fx_stage "$repo" a3.txt a3
  c1=$(fx_commit "$repo" '' c1)
  fx_head "$repo" main "$c1"
  fx_index "$repo" "$c1"

  # F9: single origin ref, origin/HEAD missing
  repo=$fix/r-oneref
  fx_init "$repo"
  fx_stage "$repo" a9.txt a9
  c1=$(fx_commit "$repo" '' c1)
  fx_stage "$repo" other9.txt o9
  c2=$(fx_commit "$repo" "$c1" c2)
  fx_head "$repo" master "$c2"
  git -C "$repo" update-ref refs/remotes/origin/master "$c2"
  fx_index "$repo" "$c2"

  # F9b: two origin refs, no origin/HEAD, no local master -> unresolvable
  repo=$fix/r-tworef
  fx_init "$repo"
  fx_stage "$repo" a10.txt a10
  c1=$(fx_commit "$repo" '' c1)
  fx_head "$repo" main "$c1"
  git -C "$repo" update-ref refs/remotes/origin/master "$c1"
  git -C "$repo" update-ref refs/remotes/origin/dev "$c1"
  fx_index "$repo" "$c1"

  # F9c: two origin refs and local master -> spec fallback refs/heads/master
  repo=$fix/r-masterfall
  fx_init "$repo"
  fx_stage "$repo" a11.txt a11
  c1=$(fx_commit "$repo" '' c1)
  fx_stage "$repo" other11.txt o11
  c2=$(fx_commit "$repo" "$c1" c2)
  fx_head "$repo" master "$c2"
  git -C "$repo" update-ref refs/remotes/origin/master "$c1"
  git -C "$repo" update-ref refs/remotes/origin/dev "$c1"
  fx_index "$repo" "$c2"

  # F9d: no remote refs at all -> pushed can never be verified
  repo=$fix/r-noremote
  fx_init "$repo"
  fx_stage "$repo" a12.txt a12
  c1=$(fx_commit "$repo" '' c1)
  fx_head "$repo" master "$c1"
  fx_index "$repo" "$c1"

  # F3: kotodama-shaped repo root: 2 unpushed commits + dirty tree
  repo=$fix/kotodama-shape
  fx_init "$repo"
  fx_stage "$repo" x.txt v1
  c1=$(fx_commit "$repo" '' c1)
  fx_stage "$repo" y.txt y
  c2=$(fx_commit "$repo" "$c1" c2)
  fx_stage "$repo" x.txt v2
  c3=$(fx_commit "$repo" "$c2" c3)
  fx_head "$repo" master "$c3"
  git -C "$repo" update-ref refs/remotes/origin/master "$c1"
  fx_index "$repo" "$c3"
  printf 'v1-dirty\n' > "$repo/x.txt"
  printf 'untracked\n' > "$repo/z.tmp"

  # F4/F5: worktree owner (matches the *-shokunin scan glob)
  repo=$fix/owner-shokunin
  fx_init "$repo"
  fx_stage "$repo" w.txt w1
  c1=$(fx_commit "$repo" '' c1)
  fx_head "$repo" master "$c1"
  git -C "$repo" update-ref refs/remotes/origin/master "$c1"
  fx_index "$repo" "$c1"
  git -C "$repo" worktree add --detach "$fix/wt-gone" "$c1" >/dev/null 2>&1
  rm -rf -- "$fix/wt-gone"
  fx_stage "$repo" z.txt z1
  c2=$(fx_commit "$repo" "$c1" c2)
  git -C "$repo" update-ref refs/heads/wtfeat "$c2"
  git -C "$repo" worktree add "$fix/wt-named" wtfeat >/dev/null 2>&1
  fx_stage "$repo" z2.txt z2
  c3=$(fx_commit "$repo" "$c2" c3)
  git -C "$repo" update-ref refs/heads/wt-orphan "$c3"
  git -C "$repo" worktree add "$fix/wt-orphan" wt-orphan >/dev/null 2>&1
  rm -rf -- "$fix/wt-orphan"
  fx_index "$repo" "$c1"

  # F6/F6b: obsidian ledger, matched and sha-mismatched rows
  repo=$fix/r-obs
  fx_init "$repo"
  fx_stage "$repo" other6.txt o6
  c1=$(fx_commit "$repo" '' c1)
  fx_head "$repo" master "$c1"
  git -C "$repo" update-ref refs/remotes/origin/master "$c1"
  fx_index "$repo" "$c1"
  mkdir -p -- "$fix/vault"
  printf 'obsidian payload\n' > "$repo/obs.txt"
  cp -- "$repo/obs.txt" "$fix/vault/obs.txt"
  printf 'obsidian payload two\n' > "$repo/obs2.txt"
  s1=$(sha256sum -- "$repo/obs.txt" | cut -d' ' -f1)
  v1=$(sha256sum -- "$fix/vault/obs.txt" | cut -d' ' -f1)
  s2=$(sha256sum -- "$repo/obs2.txt" | cut -d' ' -f1)
  zero=0000000000000000000000000000000000000000000000000000000000000000
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-01-01\tfixture\n' "$repo/obs.txt" "$s1" "$fix/vault/obs.txt" "$v1"
    printf '%s\t%s\t%s\t%s\t2026-01-01\tfixture-bad-sha-%s\n' "$repo/obs2.txt" "$zero" "$fix/vault/obs.txt" "$v1" "$s2"
  } > "$fix/ledger.tsv"

  # F7/F8/F11: scratch files, exclusions, negative control
  repo=$fix/r-scratch
  fx_init "$repo"
  fx_stage "$repo" readme.txt r
  c1=$(fx_commit "$repo" '' c1)
  fx_head "$repo" master "$c1"
  git -C "$repo" update-ref refs/remotes/origin/master "$c1"
  fx_index "$repo" "$c1"
  mkdir -p -- "$repo/.scratch"
  printf 'lorem ipsum\n' > "$repo/.scratch/notes-a.out"
  touch -d '3 days ago' -- "$repo/.scratch/notes-a.out"

  repo=$fix/r-scratch2
  fx_init "$repo"
  fx_stage "$repo" readme.txt r
  c1=$(fx_commit "$repo" '' c1)
  fx_head "$repo" master "$c1"
  git -C "$repo" update-ref refs/remotes/origin/master "$c1"
  fx_index "$repo" "$c1"
  mkdir -p -- "$repo/.scratch" "$repo/souji-shokunin/census/round-1" \
    "$repo/souji-shokunin/tests/fixtures" "$repo/.ufo-quarantine"
  printf 'lorem ipsum\n' > "$repo/.scratch/notes-a.out"
  touch -d '3 days ago' -- "$repo/.scratch/notes-a.out"
  printf 'lorem ipsum\n' > "$repo/souji-shokunin/census/round-1/notes-a.out"
  printf 'row: .scratch/notes-a.out source sha\n' > "$repo/souji-shokunin/census/round-1/census.tsv"
  printf 'lorem\n' > "$repo/souji-shokunin/tests/fixtures/notes-a.out"
  printf 'lorem\n' > "$repo/.ufo-quarantine/notes-a.out"

  repo=$fix/r-scratch3
  fx_init "$repo"
  fx_stage "$repo" readme.txt r
  c1=$(fx_commit "$repo" '' c1)
  fx_head "$repo" master "$c1"
  git -C "$repo" update-ref refs/remotes/origin/master "$c1"
  fx_index "$repo" "$c1"
  mkdir -p -- "$repo/.scratch"
  printf 'lorem ipsum\n' > "$repo/.scratch/notes-a.out"
  touch -d '3 days ago' -- "$repo/.scratch/notes-a.out"
  printf 'see notes-a.out for details\n' > "$repo/refs.md"

  # F10: secret-shaped targets
  mkdir -p -- "$fix/r-secrets/sub"
  printf 'K=1\n' > "$fix/r-secrets/.env"
  printf '{}\n' > "$fix/r-secrets/sub/credentials.json"
  printf 'ssh-key\n' > "$fix/r-secrets/id_rsa"
}

# ---------- selftest ----------

run_selftest() {
  local fix total=0 fails=0 snap1='' snap2='' out rc f1 f2 f3 f4 f5 why
  fix=$(mktemp -d "${TMPDIR:-/tmp}/souji-verify-selftest.XXXXXX")
  SELFTEST_TMP=$fix
  export GIT_AUTHOR_NAME='souji selftest' GIT_AUTHOR_EMAIL='selftest@souji.local'
  export GIT_COMMITTER_NAME='souji selftest' GIT_COMMITTER_EMAIL='selftest@souji.local'
  export GIT_AUTHOR_DATE='2026-01-01T00:00:00+0000' GIT_COMMITTER_DATE='2026-01-01T00:00:00+0000'
  FIX_ROOT=$fix
  build_fixtures "$fix"

  snap_tree() { (cd "$fix" && find . -type f | LC_ALL=C sort | xargs -d '\n' -r sha256sum) 2>/dev/null | sha256sum | cut -d' ' -f1; }

  run_target_case() { # NAME EXP_VERDICT EXP_RECEIPT EXP_EVIDENCE_GREP -- target [tool args...]
    local name=$1 ev=$2 er=$3 eg=$4
    shift 4
    if [ "${1:-}" = "--" ]; then shift; fi
    total=$((total + 1))
    rc=0
    CURR=${1:-}
    out=$(SHOKUNIN_ROOT="$fix" SOUJI_LEDGER="$fix/ledger.tsv" bash "$SELF" "$@" 2>/dev/null) || rc=$?
    f1=$(printf '%s\n' "$out" | cut -f1)
    f2=$(printf '%s\n' "$out" | cut -f2)
    f3=$(printf '%s\n' "$out" | cut -f3)
    f4=$(printf '%s\n' "$out" | cut -f4)
    f5=$(printf '%s\n' "$out" | cut -f5-)
    why=''
    if [ "$rc" != 0 ]; then why="exit=$rc"; fi
    if [ -z "$why" ] && [ "$f1" != VERDICT ]; then why="col1=${f1:-none}"; fi
    if [ -z "$why" ] && [ "$f3" != "$ev" ]; then why="verdict=${f3:-none}"; fi
    if [ -z "$why" ] && [ "$f4" != "$er" ]; then why="receipt=${f4:-none}"; fi
    if [ -z "$why" ] && [ -n "$eg" ]; then
      case $f5 in *"$eg"*) ;; *) why="evidence=$f5" ;; esac
    fi
    if [ -z "$why" ]; then
      printf 'ok   %s\n' "$name"
    else
      printf 'FAIL %s: %s (rc=%s line=%s)\n' "$name" "$why" "$rc" "$out"
      fails=$((fails + 1))
    fi
  }

  check_exit() { # NAME WANT -- args...
    local name=$1 want=$2
    shift 2
    if [ "${1:-}" = "--" ]; then shift; fi
    total=$((total + 1))
    rc=0
    ( SHOKUNIN_ROOT="$fix" SOUJI_LEDGER="$fix/ledger.tsv" bash "$SELF" "$@" >/dev/null 2>&1 ) || rc=$?
    if [ "$rc" = "$want" ]; then
      printf 'ok   %s\n' "$name"
    else
      printf 'FAIL %s: exit=%s want=%s\n' "$name" "$rc" "$want"
      fails=$((fails + 1))
    fi
  }

  snap1=$(snap_tree)

  run_target_case 'F1 pushed file (ancestor of origin/HEAD)' SAFE pushed \
    "commit=$FIX_PUSHED_COMMIT" -- "$fix/r-pushed/a1.txt"
  run_target_case 'F2 local-only introducing commit' NOT-SAFE none \
    'push=local-only' -- "$fix/r-local/a2.txt"
  run_target_case 'F2b default ref unresolvable' NOT-SAFE pushed-unverifiable \
    'intro=' -- "$fix/r-noref/a3.txt"
  run_target_case 'F3 repo-root 2 unpushed+dirty (kotodama-shape)' NOT-SAFE unpushed-dirty \
    'unpushed=2 dirty=' -- "$fix/kotodama-shape"
  run_target_case 'F4 worktree absent, unique commits 0' SAFE metadata-prune \
    'unique=0' -- "$fix/wt-gone"
  run_target_case 'F4b worktree absent, named branch unpushed' NOT-SAFE unpushed-branch \
    'unpushed=2 dir=absent' -- "$fix/wt-orphan"
  run_target_case 'F5 worktree named branch, 1 unpushed' NOT-SAFE unpushed-branch \
    'unpushed=1' -- "$fix/wt-named"
  run_target_case 'F6 ledger match (path+sha both sides)' SAFE moved-to-obsidian \
    'ledger_row=' -- "$fix/r-obs/obs.txt"
  run_target_case 'F6b ledger sha mismatch' NOT-SAFE none \
    '' -- "$fix/r-obs/obs2.txt"
  run_target_case 'F7 scratch, no refs, old mtime' SAFE stale \
    'refs=0 age_days=3' -- "$fix/r-scratch/.scratch/notes-a.out"
  run_target_case 'F7b --stale-days 5 -> not stale' NOT-SAFE none \
    'age_days=3' -- --stale-days 5 "$fix/r-scratch/.scratch/notes-a.out"
  run_target_case 'F7c --stale-days 0 -> stale' SAFE stale \
    'refs=0' -- --stale-days 0 "$fix/r-scratch/.scratch/notes-a.out"
  run_target_case 'F8 census/tests/quarantine refs excluded (D3)' SAFE stale \
    'refs=0' -- "$fix/r-scratch2/.scratch/notes-a.out"
  run_target_case 'F11 live ref present (negative control)' NOT-SAFE none \
    'refs=1' -- "$fix/r-scratch3/.scratch/notes-a.out"
  run_target_case 'F9 origin/HEAD missing, single origin ref' SAFE pushed \
    'ref=refs/remotes/origin/master' -- "$fix/r-oneref/a9.txt"
  run_target_case 'F9b two origin refs, no HEAD -> unverifiable' NOT-SAFE pushed-unverifiable \
    'intro=' -- "$fix/r-tworef/a10.txt"
  run_target_case 'F9c fallback local master (remote refs exist)' SAFE pushed \
    'ref=refs/heads/master' -- "$fix/r-masterfall/a11.txt"
  run_target_case 'F9d no remote refs -> pushed unverifiable' NOT-SAFE pushed-unverifiable \
    'remote_refs=0' -- "$fix/r-noremote/a12.txt"
  run_target_case 'F10 .env refused' NOT-SAFE secrets-refusal \
    '' -- "$fix/r-secrets/.env"
  run_target_case 'F10b credentials.json refused' NOT-SAFE secrets-refusal \
    '' -- "$fix/r-secrets/sub/credentials.json"
  run_target_case 'F10c id_rsa refused' NOT-SAFE secrets-refusal \
    '' -- "$fix/r-secrets/id_rsa"
  run_target_case 'U1 missing target -> unreachable' NOT-SAFE unreachable \
    '' -- "$fix/no-such-thing"
  run_target_case 'E1 empty target -> unreachable' NOT-SAFE unreachable \
    'empty-target' -- ''

  total=$((total + 1))
  rc=0
  out=$(SHOKUNIN_ROOT="$fix" SOUJI_LEDGER="$fix/ledger.tsv" bash "$SELF" --json "$fix/r-pushed/a1.txt" 2>/dev/null) || rc=$?
  case $out in
    *'"verdict":"SAFE"'*'"receipt":"pushed"'*) printf 'ok   J1 --json shape\n' ;;
    *) printf 'FAIL J1 --json shape: rc=%s out=%s\n' "$rc" "$out"; fails=$((fails + 1)) ;;
  esac

  check_exit 'X1 no targets -> exit 2' 2
  check_exit 'X2 unknown flag -> exit 2' 2 -- --bogus
  check_exit 'X3 bad --stale-days -> exit 2' 2 -- --stale-days abc "$fix/r-pushed/a1.txt"

  total=$((total + 1))
  local pat bad
  pat='git[^|;&]*\b(fetch|push|commit|checkout|reset|rebase)\b'
  bad=$(awk '!/^[[:space:]]*#/' "$SELF" | grep -nE -- "$pat" | grep -v -- 'commit-tree' || true)
  if [ -z "$bad" ]; then
    printf 'ok   S1 no forbidden git verbs on executable lines (static)\n'
  else
    printf 'FAIL S1 forbidden git verb line(s): %s\n' "$bad"
    fails=$((fails + 1))
  fi

  snap2=$(snap_tree)
  total=$((total + 1))
  if [ "$snap1" = "$snap2" ]; then
    printf 'ok   S2 fixture tree byte-identical after all tool runs (read-only)\n'
  else
    printf 'FAIL S2 fixture tree changed during verification runs\n'
    fails=$((fails + 1))
  fi

  printf 'selftest: %s checks, %s failure(s)\n' "$total" "$fails"
  if [ "$fails" = 0 ]; then exit 0; else exit 1; fi
}

# ---------- main ----------

if [ "$DO_SELFTEST" = 1 ]; then
  run_selftest
  exit 1
fi

if [ "${#TARGETS[@]}" = 0 ]; then
  usage >&2
  exit 2
fi

for _t in "${TARGETS[@]}"; do
  CURR=$_t
  if ! evaluate "${_t}"; then
    ERRORS=$((ERRORS + 1))
  fi
done
CURR=''
[ "$ERRORS" = 0 ] || exit 1
exit 0
