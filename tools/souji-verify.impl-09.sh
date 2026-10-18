#!/usr/bin/env bash
# souji-verify.sh — receipt-based artifact verification for souji-shokunin (round 2).
# Binding spec: tools/souji-verify.spec.md. Read-only over every inspected surface;
# bash + coreutils + git + rg only. Round-1 defects fixed by construction:
#   D1 default-branch resolution            -> resolve_default_ref()
#   D2 artifact-kind branches               -> evaluate()
#   D3 reference-sweep exclusions           -> live_refs()
# No git fetch/push/commit/branch/checkout/reset/rebase is ever issued. --selftest
# builds its fixture history with plumbing only (hash-object, mktree, commit-tree,
# update-ref, read-tree, worktree add --no-checkout) inside a mktemp dir; the suite
# covers F1-F10 plus guards F5b (absent dir + named branch), F10b/F10c (secret
# shapes) and F11 (unreachable).
set -euo pipefail

export GIT_OPTIONAL_LOCKS=0
export GIT_TERMINAL_PROMPT=0

SELF_PATH=${BASH_SOURCE[0]}
TOOL_DIR=$(cd -- "$(dirname -- "$SELF_PATH")" && pwd -P)
LANE_ROOT=$(dirname -- "$TOOL_DIR")
SHOKUNIN_ROOT=${SHOKUNIN_ROOT:-$(dirname -- "$LANE_ROOT")}
LEDGER=${SOUJI_LEDGER:-"$LANE_ROOT/corpus/knowledge/obsidian-ledger.tsv"}
VAULT_ROOT=${SOUJI_VAULT:-/home/vgpnk/Documents/shokuknowledge}

STALE_DAYS=1
JSON_OUT=0
RUN_SELFTEST=0
ST_TMP=""
ST_FAIL=0
WT_CACHE_LOADED=0
WT_CACHE=""
LEDGER_EVIDENCE=""

usage() {
  cat <<'EOF'
usage: souji-verify.sh [--selftest] [--stale-days N] [--json] <path>...

Prints one line per target:
  VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-reason<TAB>decisive-evidence

  --selftest       run the F1-F10 fixture suite in an isolated mktemp git repo
  --stale-days N   mtime threshold in days for the `stale` receipt (default 1)
  --json           one JSON object per target instead of TSV
  env: SHOKUNIN_ROOT, SOUJI_LEDGER, SOUJI_VAULT
exit: 0 = evaluated clean, 1 = selftest failure / evaluation error, 2 = usage
EOF
}

usage_err() {
  printf 'souji-verify: %s\n' "$1" >&2
  usage >&2
  exit 2
}

# ---------- primitives ----------

count_lines() { awk 'NF { n++ } END { print n + 0 }'; }

count_git() { # $1 = repo, rest = git args; count non-empty output lines
  local repo=$1
  shift
  { git -C "$repo" "$@" 2>/dev/null || true; } | count_lines
}

realpath_m() { realpath -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

sha256_of() { # $1 = regular file -> hex digest on stdout
  [ -f "$1" ] || return 1
  { sha256sum -- "$1" 2>/dev/null || true; } | awk '{ print $1 }' | head -1
}

is_secret_shaped() { # $1 = path; safety rail, matched per basename and per component
  local p=$1 base comp lower rest
  base=${p##*/}
  lower=${base,,}
  case "$lower" in *.env|*.pem|id_*) return 0 ;; esac
  case "$lower" in *credential*|*secret*) return 0 ;; esac
  rest=${p#/}
  local IFS='/'
  for comp in $rest; do
    lower=${comp,,}
    case "$lower" in *.env|*.pem|id_*) return 0 ;; esac
    case "$lower" in *credential*|*secret*) return 0 ;; esac
  done
  return 1
}

is_scratch_path() { # $1 = absolute path; scratch-type test for the `stale` receipt
  local base=${1##*/}
  case "$1" in
    */.scratch|*/.scratch/*|.scratch|.scratch/*) return 0 ;;
  esac
  case "$base" in
    *.out|*.log|*-draft.*|*checkpoint*.json|*checkpoint*.png) return 0 ;;
    launch-*.json|prior-owners.json|interactive-wall.png) return 0 ;;
  esac
  return 1
}

older_than_days() { # $1 = path, $2 = days
  [ -n "$(find "$1" -maxdepth 0 -mtime +"$2" -print -quit 2>/dev/null || true)" ]
}

repo_of() { # $1 = absolute path -> enclosing repo toplevel (empty if none)
  local dir
  if [ -d "$1" ]; then dir=$1; else dir=$(dirname -- "$1"); fi
  git -C "$dir" rev-parse --show-toplevel 2>/dev/null || true
}

# D1: resolve the default branch from existing refs only (no fetch):
# origin/HEAD symbolic ref, else the single refs/remotes/origin/* ref,
# else local master, else unresolved.
resolve_default_ref() { # $1 = repo -> "<ref>[TAB]<mode>" on stdout
  local repo=$1 name refs n
  name=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
  if [ -n "$name" ]; then
    printf 'refs/remotes/%s\torigin-HEAD-ref\n' "$name"
    return 0
  fi
  refs=$({ git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin/ 2>/dev/null || true; } \
    | { grep -v -x 'refs/remotes/origin/HEAD' || true; })
  n=$(printf '%s\n' "$refs" | count_lines)
  if [ "$n" -eq 1 ]; then
    printf '%s\tsingle-origin-branch-ref\n' "$refs"
    return 0
  fi
  if git -C "$repo" rev-parse --verify --quiet refs/heads/master >/dev/null 2>&1; then
    printf 'refs/heads/master\tlocal-master\n'
    return 0
  fi
  return 1
}

# D2 support: worktree registrations across $SHOKUNIN_ROOT/*-shokunin and the
# fleet root itself; cached once per run.
wt_cache_build() {
  if [ "$WT_CACHE_LOADED" -eq 1 ]; then return 0; fi
  local candidate line path head branch owner
  WT_CACHE=""
  for candidate in "$SHOKUNIN_ROOT"/*-shokunin "$SHOKUNIN_ROOT"; do
    if [ ! -e "$candidate/.git" ]; then continue; fi
    owner=$(realpath_m "$candidate")
    path=""
    head=""
    branch=""
    while IFS= read -r line; do
      case "$line" in
        'worktree '*) path=${line#worktree } ;;
        'HEAD '*) head=${line#HEAD } ;;
        'branch '*) branch=${line#branch } ;;
        '')
          if [ -n "$path" ]; then
            WT_CACHE+="$(realpath_m "$path")"$'\t'"$owner"$'\t'"$head"$'\t'"$branch"$'\n'
          fi
          path=""
          head=""
          branch=""
          ;;
      esac
    done < <(git -C "$candidate" worktree list --porcelain 2>/dev/null || true)
    if [ -n "$path" ]; then
      WT_CACHE+="$(realpath_m "$path")"$'\t'"$owner"$'\t'"$head"$'\t'"$branch"$'\n'
    fi
  done
  WT_CACHE_LOADED=1
}

wt_lookup() { # $1 = absolute path -> cache line (path owner head branch) if registered
  local abs=$1
  wt_cache_build
  if [ -z "$WT_CACHE" ]; then return 0; fi
  printf '%s' "$WT_CACHE" | awk -F'\t' -v t="$abs" '$1 == t { print; exit }'
}

# D3: zero live references. The spec's --basename is not a ripgrep flag (rg 15.2);
# the faithful equivalent is a fixed-strings content search. Globs are **/-anchored
# because rg matches them against absolute paths; --hidden and the secret-shaped
# exclusions keep the sweep complete without reading rail-protected files.
live_refs() { # $1 = basename -> integer, or "unknown" when unmeasurable
  local name=$1 out rc=0
  if ! command -v rg >/dev/null 2>&1; then printf 'unknown'; return 0; fi
  if [ ! -d "$SHOKUNIN_ROOT" ]; then printf 'unknown'; return 0; fi
  out=$(rg -l --no-ignore --hidden --no-messages --fixed-strings \
    -g '!**/.git' \
    -g '!**/.git/**' \
    -g '!**/souji-shokunin/census/**' \
    -g '!**/souji-shokunin/tests/**' \
    -g '!**/.ufo-quarantine/**' \
    -g '!**/*.env' \
    -g '!**/*credential*' \
    -g '!**/*secret*' \
    -g '!**/id_*' \
    -g '!**/*.pem' \
    -- "$name" "$SHOKUNIN_ROOT" 2>/dev/null) || rc=$?
  if [ "$rc" -gt 1 ]; then printf 'unknown'; return 0; fi
  printf '%s' "$out" | count_lines
}

# moved-to-obsidian: ledger row must match source path, source sha256, vault
# path and vault sha256; the vault side is read-only.
ledger_match() { # $1 = target as given, $2 = abs; sets LEDGER_EVIDENCE
  LEDGER_EVIDENCE=""
  local target=$1 abs=$2
  if [ ! -f "$abs" ]; then return 1; fi
  if [ ! -f "$LEDGER" ]; then return 1; fi
  if is_secret_shaped "$LEDGER"; then return 1; fi
  local sha=""
  sha=$(sha256_of "$abs") || true
  if [ -z "$sha" ]; then return 1; fi
  local line_no=0 src ssha vpath vsha extra vfull vactual
  while IFS=$'\t' read -r src ssha vpath vsha extra; do
    line_no=$((line_no + 1))
    if [ "$line_no" -eq 1 ]; then continue; fi
    if [ -z "$src" ] || [ -z "$ssha" ] || [ -z "$vpath" ] || [ -z "$vsha" ]; then continue; fi
    case "$src" in
      "$target"|"$abs") ;;
      *)
        if [ -e "$src" ] && [ "$(realpath_m "$src")" = "$abs" ]; then :; else continue; fi
        ;;
    esac
    if [ "$ssha" != "$sha" ]; then continue; fi
    vfull=$vpath
    case "$vpath" in
      /*) ;;
      *) vfull="$VAULT_ROOT/$vpath" ;;
    esac
    if [ ! -f "$vfull" ]; then continue; fi
    if is_secret_shaped "$vfull"; then continue; fi
    vactual=""
    vactual=$(sha256_of "$vfull") || true
    if [ -z "$vactual" ]; then continue; fi
    if [ "$vactual" != "$vsha" ]; then continue; fi
    LEDGER_EVIDENCE="ledger_line=$line_no source_sha256=$sha vault_path=$vfull"
    return 0
  done < "$LEDGER"
  return 1
}

# ---------- verdict ----------

evaluate() { # $1 = target as given -> "<SAFE|NOT-SAFE>[TAB]<receipt>[TAB]<evidence>"
  local target=$1 abs base
  base=${target##*/}

  if is_secret_shaped "$target"; then
    printf '%s\t%s\t%s\n' NOT-SAFE secrets-refusal "secret-shaped path refused basename=$base"
    return 0
  fi
  if [ -z "$target" ]; then
    printf '%s\t%s\t%s\n' NOT-SAFE unreachable "empty-target"
    return 0
  fi
  abs=$(realpath_m "$target")

  # D2 kind 1: repo-root
  if [ -d "$abs" ] && [ -d "$abs/.git" ]; then
    local unpushed dirty receipt
    unpushed=$(count_git "$abs" log --oneline --branches --not --remotes)
    dirty=$(count_git "$abs" status --porcelain)
    if ledger_match "$target" "$abs"; then
      printf '%s\t%s\t%s\n' SAFE moved-to-obsidian "$LEDGER_EVIDENCE"
      return 0
    fi
    if [ "$unpushed" -eq 0 ] && [ "$dirty" -eq 0 ]; then
      receipt=none
    elif [ "$unpushed" -gt 0 ]; then
      receipt=unpushed
    else
      receipt=dirty
    fi
    printf '%s\t%s\t%s\n' NOT-SAFE "$receipt" "unpushed=$unpushed dirty=$dirty"
    return 0
  fi

  # D2 kind 2: worktree-registration (also matches registrations whose dir is gone)
  local wt
  wt=$(wt_lookup "$abs")
  if [ -n "$wt" ]; then
    local wt_path owner whead wbranch present=0 unique=0 dirty=0 bunpushed=0 bname
    IFS=$'\t' read -r wt_path owner whead wbranch <<<"$wt"
    if [ -e "$abs" ]; then present=1; fi
    if [ -n "$whead" ]; then
      unique=$(count_git "$owner" log --oneline "$whead" --not --all)
    fi
    # An unpushed named branch outranks the prune condition: round-1's reference
    # verdicts hold the 3 gd2d named-branch worktrees NOT-SAFE with absent dirs.
    if [ -n "$wbranch" ]; then
      bname=${wbranch#refs/heads/}
      bunpushed=$(count_git "$owner" log --oneline "$bname" --not --remotes)
      if [ "$bunpushed" -gt 0 ]; then
        printf '%s\t%s\t%s\n' NOT-SAFE unpushed-branch "branch=$wbranch unpushed=$bunpushed present=$present owner=$owner"
        return 0
      fi
    fi
    if [ "$present" -eq 0 ] && [ "$unique" -eq 0 ]; then
      printf '%s\t%s\t%s\n' SAFE metadata-prune "owner=$owner unique=0 head=$whead"
      return 0
    fi
    if [ "$present" -eq 1 ]; then
      dirty=$(count_git "$abs" status --porcelain)
      if [ "$dirty" -gt 0 ]; then
        printf '%s\t%s\t%s\n' NOT-SAFE dirty "dirty=$dirty owner=$owner registered=$wt_path"
        return 0
      fi
      printf '%s\t%s\t%s\n' NOT-SAFE live-worktree "present=1 dirty=0 owner=$owner registered=$wt_path"
      return 0
    fi
    printf '%s\t%s\t%s\n' NOT-SAFE unpushed-branch "owner=$owner unique=$unique head=$whead"
    return 0
  fi

  if [ ! -e "$abs" ]; then
    printf '%s\t%s\t%s\n' NOT-SAFE unreachable "target=$target"
    return 0
  fi

  # D2 kind 3: file/dir artifact — receipts in order: pushed, moved-to-obsidian, stale
  local repo="" rel="" intro="" refname="" refmode="" unverifiable=0
  repo=$(repo_of "$abs")
  if [ -n "$repo" ]; then
    if [ "$abs" = "$repo" ]; then
      rel="."
    else
      case "$abs" in
        "$repo"/*) rel=${abs#"$repo"/} ;;
        *) rel=$abs ;;
      esac
    fi
    intro=$({ git -C "$repo" log --diff-filter=A --format=%H -1 -- "$rel" 2>/dev/null || true; } | head -1)
    if [ -n "$intro" ]; then
      local resolved=""
      resolved=$(resolve_default_ref "$repo") || resolved=""
      if [ -z "$resolved" ]; then
        unverifiable=1
      else
        IFS=$'\t' read -r refname refmode <<<"$resolved"
        if git -C "$repo" merge-base --is-ancestor "$intro" "$refname" >/dev/null 2>&1; then
          printf '%s\t%s\t%s\n' SAFE pushed "commit=$intro ref=$refname mode=$refmode"
          return 0
        fi
      fi
    fi
  fi

  if ledger_match "$target" "$abs"; then
    printf '%s\t%s\t%s\n' SAFE moved-to-obsidian "$LEDGER_EVIDENCE"
    return 0
  fi

  if is_scratch_path "$abs" && older_than_days "$abs" "$STALE_DAYS"; then
    local refs
    refs=$(live_refs "$base")
    if [ "$refs" = 0 ]; then
      printf '%s\t%s\t%s\n' SAFE stale "basename=$base refs=0 mtime=older-than-${STALE_DAYS}d"
      return 0
    fi
  fi

  if [ "$unverifiable" -eq 1 ]; then
    printf '%s\t%s\t%s\n' NOT-SAFE pushed-unverifiable "intro=$intro default-branch-unresolved repo=$repo"
    return 0
  fi
  if [ -z "$intro" ]; then
    printf '%s\t%s\t%s\n' NOT-SAFE none "no-introducing-commit repo=${repo:--}"
    return 0
  fi
  printf '%s\t%s\t%s\n' NOT-SAFE none "intro=$intro ref=$refname not-an-ancestor"
  return 0
}

json_escape() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\t/\\t/g' -e 's/\r//g'
}

emit_row() {
  local t=$1 out verdict receipt evidence
  out=$(evaluate "$t")
  IFS=$'\t' read -r verdict receipt evidence <<<"$out"
  if [ "$JSON_OUT" -eq 1 ]; then
    printf '{"record":"VERDICT","path":"%s","verdict":"%s","receipt":"%s","evidence":"%s"}\n' \
      "$(json_escape "$t")" "$verdict" "$receipt" "$(json_escape "$evidence")"
  else
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$t" "$verdict" "$receipt" "$evidence"
  fi
}

# ---------- selftest ----------

st_cleanup() {
  if [ -n "$ST_TMP" ] && [ -d "$ST_TMP" ]; then
    rm -rf -- "$ST_TMP"
  fi
}

st_run() { # $1 = target; runs this tool against the fixture root
  SHOKUNIN_ROOT="$ST_ROOT" SOUJI_LEDGER="$ST_LEDGER" SOUJI_VAULT="$ST_VAULT" \
    "$SELF_PATH" --stale-days 1 -- "$1"
}

st_assert() { # name want_verdict want_receipt target [evidence-regex]
  local name=$1 want_v=$2 want_r=$3 target=$4 pat=${5:-} line verdict receipt evidence ok=1
  if ! line=$(st_run "$target" 2>/dev/null); then
    printf 'FAIL %s: tool exited nonzero\n' "$name"
    ST_FAIL=$((ST_FAIL + 1))
    return 0
  fi
  IFS=$'\t' read -r _ _ verdict receipt evidence <<<"$line"
  if [ "$verdict" != "$want_v" ]; then ok=0; fi
  if [ "$receipt" != "$want_r" ]; then ok=0; fi
  if [ -n "$pat" ]; then
    if ! printf '%s' "$evidence" | grep -Eq -- "$pat"; then ok=0; fi
  fi
  if [ "$ok" -eq 1 ]; then
    printf 'ok   %s: %s(%s)\n' "$name" "$verdict" "$receipt"
  else
    printf 'FAIL %s: got %s(%s) evidence=[%s] want %s(%s)%s\n' \
      "$name" "$verdict" "$receipt" "$evidence" "$want_v" "$want_r" "${pat:+ /$pat/}"
    ST_FAIL=$((ST_FAIL + 1))
  fi
  return 0
}

st_blob() { printf '%s\n' "$2" | git -C "$1" hash-object -w --stdin; }

st_commit() { # $1 = repo, $2 = message, $3 = parent|- ; mktree lines on stdin
  local repo=$1 msg=$2 parent=$3 tree
  tree=$(git -C "$repo" mktree)
  if [ "$parent" = "-" ]; then
    git -C "$repo" commit-tree "$tree" -m "$msg"
  else
    git -C "$repo" commit-tree "$tree" -p "$parent" -m "$msg"
  fi
  git -C "$repo" read-tree "$tree"
}

st_repo() { # $1 = path -> initial commit sha on refs/heads/master, work tree in sync
  mkdir -p -- "$1"
  git -C "$1" init -q --initial-branch=master
  git -C "$1" remote add origin /nonexistent/souji-fixture-origin.git
  local bb tc
  bb=$(st_blob "$1" 'base')
  tc=$(printf '100644 blob %s\tbase.txt\n' "$bb" | st_commit "$1" 'fixture: base' -)
  git -C "$1" update-ref refs/heads/master "$tc"
  git -C "$1" symbolic-ref HEAD refs/heads/master
  printf 'base\n' > "$1/base.txt"
  printf '%s\n' "$tc"
}

st_publish() { # $1 = repo, $2 = commit -> origin/master + origin/HEAD (as if pushed)
  git -C "$1" update-ref refs/remotes/origin/master "$2"
  git -C "$1" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
}

selftest() {
  ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-verify-selftest.XXXXXX") || {
    printf 'selftest: mktemp failed\n' >&2
    return 1
  }
  ST_ROOT=$ST_TMP
  ST_LEDGER="$ST_ROOT/ledger.tsv"
  ST_VAULT="$ST_ROOT/vault"
  mkdir -p -- "$ST_ROOT/wts" "$ST_ROOT/files" "$ST_VAULT" \
    "$ST_ROOT/f7dir/.scratch" "$ST_ROOT/f8dir/.scratch" \
    "$ST_ROOT/souji-shokunin/census/round-1" "$ST_ROOT/souji-shokunin/tests" \
    "$ST_ROOT/sentineldir"

  export GIT_AUTHOR_NAME=souji GIT_AUTHOR_EMAIL=souji@shokunin.local
  export GIT_COMMITTER_NAME=souji GIT_COMMITTER_EMAIL=souji@shokunin.local
  export GIT_AUTHOR_DATE='@1767225600 +0000' GIT_COMMITTER_DATE='@1767225600 +0000'

  local r1="$ST_ROOT/repo-f1" bb bs bl t1 t2 c1 c2
  c1=$(st_repo "$r1")
  st_publish "$r1" "$c1"
  bb=$(st_blob "$r1" 'base')
  bs=$(st_blob "$r1" 'safe payload')
  t1=$(printf '100644 blob %s\tbase.txt\n100644 blob %s\tsafe.txt\n' "$bb" "$bs" | st_commit "$r1" 'fixture: add safe.txt' "$c1")
  git -C "$r1" update-ref refs/remotes/origin/master "$t1"
  git -C "$r1" update-ref refs/heads/master "$t1"
  printf 'safe payload\n' > "$r1/safe.txt"

  bl=$(st_blob "$r1" 'local only')
  t2=$(printf '100644 blob %s\tbase.txt\n100644 blob %s\tlocal-only.txt\n100644 blob %s\tsafe.txt\n' \
    "$bb" "$bl" "$bs" | st_commit "$r1" 'fixture: local-only add' "$t1")
  git -C "$r1" update-ref refs/heads/master "$t2"
  printf 'local only\n' > "$r1/local-only.txt"

  local r3="$ST_ROOT/repo-f3" c3 t3 bl3
  c3=$(st_repo "$r3")
  st_publish "$r3" "$c3"
  bl3=$(st_blob "$r3" 'local three')
  t3=$(printf '100644 blob %s\tbase.txt\n100644 blob %s\tlocal.txt\n' \
    "$(st_blob "$r3" 'base')" "$bl3" | st_commit "$r3" 'fixture: unpushed local commit' "$c3")
  git -C "$r3" update-ref refs/heads/master "$t3"
  printf 'local three\n' > "$r3/local.txt"
  printf 'dirty\n' > "$r3/dirty.txt"

  local wr="$ST_ROOT/wtest-shokunin" cw t4 b4
  cw=$(st_repo "$wr")
  st_publish "$wr" "$cw"
  git -C "$wr" worktree add --no-checkout --detach "$ST_ROOT/wts/prune-me" "$cw" >/dev/null 2>&1
  git -C "$wr" worktree add --no-checkout --detach "$ST_ROOT/wts/branchy" "$cw" >/dev/null 2>&1
  b4=$(st_blob "$wr" 'branch work')
  t4=$(printf '100644 blob %s\tbase.txt\n100644 blob %s\tbranchfile.txt\n' \
    "$(st_blob "$wr" 'base')" "$b4" | st_commit "$wr" 'fixture: unpushed branch work' "$cw")
  git -C "$wr" update-ref refs/heads/wt-branchy "$t4"
  git -C "$ST_ROOT/wts/branchy" symbolic-ref HEAD refs/heads/wt-branchy
  git -C "$wr" worktree add --no-checkout --detach "$ST_ROOT/wts/gone" "$cw" >/dev/null 2>&1
  git -C "$wr" update-ref refs/heads/wt-gone "$t4"
  git -C "$ST_ROOT/wts/gone" symbolic-ref HEAD refs/heads/wt-gone
  rm -rf -- "$ST_ROOT/wts/prune-me" "$ST_ROOT/wts/gone"

  printf 'obsidian payload\n' > "$ST_ROOT/files/report.md"
  cp -- "$ST_ROOT/files/report.md" "$ST_VAULT/note.md"
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$ST_ROOT/files/report.md" \
      "$(sha256_of "$ST_ROOT/files/report.md")" "$ST_VAULT/note.md" \
      "$(sha256_of "$ST_VAULT/note.md")" '2026-01-01' 'selftest fixture'
  } > "$ST_LEDGER"

  printf 'scratch payload seven\n' > "$ST_ROOT/f7dir/.scratch/f7-scratch.log"
  printf 'scratch payload eight\n' > "$ST_ROOT/f8dir/.scratch/f8-scratch.log"
  printf 'census fragment mentioning f8-scratch.log\n' > "$ST_ROOT/souji-shokunin/census/round-1/seat-01.json"
  printf 'tests fragment mentioning f8-scratch.log\n' > "$ST_ROOT/souji-shokunin/tests/seat-01.txt"
  touch -d '10 days ago' -- "$ST_ROOT/f7dir/.scratch/f7-scratch.log" "$ST_ROOT/f8dir/.scratch/f8-scratch.log"

  local r9="$ST_ROOT/repo-f9" c9 t9 b9
  c9=$(st_repo "$r9")
  b9=$(st_blob "$r9" 'pushed nine')
  t9=$(printf '100644 blob %s\tbase.txt\n100644 blob %s\tpushed9.txt\n' \
    "$(st_blob "$r9" 'base')" "$b9" | st_commit "$r9" 'fixture: pushed nine' "$c9")
  git -C "$r9" update-ref refs/heads/master "$t9"
  git -C "$r9" update-ref refs/remotes/origin/master "$t9"
  printf 'pushed nine\n' > "$r9/pushed9.txt"

  printf 'SECRET=1\n' > "$ST_ROOT/sentineldir/.env"
  printf 'SECRET=2\n' > "$ST_ROOT/souji-shokunin/tests/prod.env"
  chmod 000 "$ST_ROOT/souji-shokunin/tests/prod.env"
  printf 'PRIVATE KEY\n' > "$ST_ROOT/sentineldir/id_rsa"

  st_assert F1 SAFE pushed "$r1/safe.txt" 'commit=[0-9a-f]{40} ref=refs/remotes/origin/master'
  st_assert F2 NOT-SAFE none "$r1/local-only.txt"
  st_assert F3 NOT-SAFE unpushed "$r3" 'unpushed=1 dirty=1'
  st_assert F4 SAFE metadata-prune "$ST_ROOT/wts/prune-me" 'unique=0'
  st_assert F5 NOT-SAFE unpushed-branch "$ST_ROOT/wts/branchy" 'unpushed=1'
  st_assert F5b NOT-SAFE unpushed-branch "$ST_ROOT/wts/gone" 'unpushed=1'
  st_assert F6 SAFE moved-to-obsidian "$ST_ROOT/files/report.md" 'ledger_line=2'
  st_assert F7 SAFE stale "$ST_ROOT/f7dir/.scratch/f7-scratch.log" 'refs=0'
  st_assert F8 SAFE stale "$ST_ROOT/f8dir/.scratch/f8-scratch.log" 'refs=0'
  st_assert F9 SAFE pushed "$r9/pushed9.txt" 'mode=single-origin-branch-ref'
  st_assert F10 NOT-SAFE secrets-refusal "$ST_ROOT/sentineldir/.env"
  st_assert F10b NOT-SAFE secrets-refusal "$ST_ROOT/souji-shokunin/tests/prod.env"
  st_assert F10c NOT-SAFE secrets-refusal "$ST_ROOT/sentineldir/id_rsa"
  st_assert F11 NOT-SAFE unreachable "$ST_ROOT/does-not-exist/thing.txt"

  if [ "$ST_FAIL" -eq 0 ]; then
    printf 'selftest: PASS (14/14)\n'
    return 0
  fi
  printf 'selftest: FAIL (%d failed)\n' "$ST_FAIL"
  return 1
}

# ---------- main ----------

main() {
  local -a targets=()
  while [ $# -gt 0 ]; do
    case "$1" in
      --selftest) RUN_SELFTEST=1; shift ;;
      --json) JSON_OUT=1; shift ;;
      --stale-days) if [ $# -lt 2 ]; then usage_err '--stale-days needs a value'; fi; STALE_DAYS=$2; shift 2 ;;
      --stale-days=*) STALE_DAYS=${1#*=}; shift ;;
      -h|--help) usage; exit 0 ;;
      --) shift; while [ $# -gt 0 ]; do targets+=("$1"); shift; done ;;
      -*) usage_err "unknown option: $1" ;;
      *) targets+=("$1"); shift ;;
    esac
  done

  case "$STALE_DAYS" in
    ''|*[!0-9]*) usage_err "--stale-days must be a non-negative integer: $STALE_DAYS" ;;
  esac

  if [ "$RUN_SELFTEST" -eq 1 ]; then
    if selftest; then exit 0; else exit 1; fi
  fi

  if [ "$JSON_OUT" -eq 0 ] && [ -z "$SHOKUNIN_ROOT" ]; then
    usage_err 'SHOKUNIN_ROOT could not be derived'
  fi

  if ! command -v git >/dev/null 2>&1; then
    printf 'souji-verify: git not found\n' >&2
    exit 1
  fi
  if ! command -v sha256sum >/dev/null 2>&1; then
    printf 'souji-verify: sha256sum not found\n' >&2
    exit 1
  fi

  if [ "${#targets[@]}" -eq 0 ]; then
    usage_err 'no targets given'
  fi

  local t
  for t in "${targets[@]}"; do
    emit_row "$t"
  done
  exit 0
}

trap st_cleanup EXIT
trap 'st_cleanup; exit 1' INT TERM

main "$@"
