# probe-lib.sh — shared helpers for the R42reviewer03 group-A probes (sourced, never run directly).
# Each probe builds its scenario under $SCRATCH_ROOT/probe-<ID>, runs the pinned tool and the mutant
# on identical arguments, and appends the observed rc/stdout/stderr to receipts/probe-<ID>.txt.
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
SEAT=$LANE/.ufo/waves/round-42/w1/R42reviewer03
PRISTINE=$LANE/tools/souji-worktree-drift.py
REAL_GIT=/usr/bin/git
SCRATCH_ROOT=/fast/scratch/hyaku/souji-r42/R42reviewer03
export GIT_AUTHOR_NAME=probe GIT_AUTHOR_EMAIL=probe@example.invalid
export GIT_COMMITTER_NAME=probe GIT_COMMITTER_EMAIL=probe@example.invalid

probe_setup() {
  PID=$1
  SCR="$SCRATCH_ROOT/probe-$PID"
  MUTANT="$SEAT/mut-$PID.py"
  RECEIPT="$SEAT/receipts/probe-$PID.txt"
  mkdir -p -- "$SEAT/receipts"
  rm -rf -- "$SCR"; mkdir -p -- "$SCR"
  trap 'rm -rf -- "$SCR"' EXIT
  : > "$RECEIPT"
  printf 'probe=%s pristine=%s mutant=%s\n' "$PID" \
    "$(sha256sum "$PRISTINE" | cut -c1-16)" "$(sha256sum "$MUTANT" | cut -c1-16)" | tee -a "$RECEIPT"
}

mkrepo() {
  mkdir -p -- "$1"
  "$REAL_GIT" init -q "$1"
  [ "$("$REAL_GIT" -C "$1" rev-parse --show-toplevel)" = "$(realpath -- "$1")" ] || { echo "toplevel mismatch: $1" >&2; exit 2; }
  "$REAL_GIT" -C "$1" commit -q --allow-empty -m init
}

run_case() {
  local label=$1 tool=$2 tmo=$3; shift 3
  local rc=0
  timeout "$tmo" python3 -B "$tool" "$@" >"$SCR/$label.out" 2>"$SCR/$label.err" || rc=$?
  {
    printf '=== %s rc=%s tool=%s args=%s\n' "$label" "$rc" "$(basename -- "$tool")" "$*"
    echo '--- stdout'; cat -- "$SCR/$label.out"
    echo '--- stderr'; cat -- "$SCR/$label.err"
  } | tee -a "$RECEIPT"
}

slow_git_wrapper() { # $1 = shell action taken for "worktree list" calls; the wrapper is $SCR/bin/git
  mkdir -p -- "$SCR/bin"
  printf '#!/bin/sh\ncase "$*" in *"worktree list"*) %s;; esac\nexec %s "$@"\n' "$1" "$REAL_GIT" > "$SCR/bin/git"
  chmod 0755 "$SCR/bin/git"
  export PATH="$SCR/bin:$PATH"
  echo "git resolves to: $(command -v git)" | tee -a "$RECEIPT"
}
