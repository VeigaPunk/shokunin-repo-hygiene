#!/usr/bin/env bash
# r17-jj-receipts.sh — C3 coverage fixture for jj-colocated receipt roots.
#
# Round 17, seat FixtureJjReceipts (wave 1). Revised contract (L1, wave 1):
#
#   (a') durable roots for receipts are ALL refs except refs/jj/* — never
#        refs/jj/* and never HEAD. An absent linked-worktree registration
#        whose head commit is reachable only from refs/jj/keep/* is
#        NOT-SAFE, never SAFE(metadata-prune).
#   (b') a keep-only commit refuses a pushed receipt only when its object at
#        the target path is NOVEL: absent from remote history. Deletions and
#        identical-content (already published) predecessors do not refuse.
#
# Cases, all through the tools' CLIs (so the effective, last-defined
# functions are the ones measured):
#   J1  absent-worktree head held only by refs/jj/keep/*        -> NOT-SAFE
#   J2  same head also reachable from refs/heads/*             -> SAFE(metadata-prune)
#   J3  keep-only commit with NOVEL content at the target      -> NOT-SAFE
#   J4  keep-only commit whose target blob is already in remote
#       history (metaedit-shaped predecessor)                  -> SAFE(pushed)
#   J5  keep-only deletion of the target                       -> SAFE(pushed)
#   J6  plain repo (no refs/jj): verify/vault stdout must be
#       byte-identical between --tool-dir and --baseline-dir   -> identical
#   J7  plain repo, absent-worktree head held only by
#       refs/stash                                             -> SAFE(metadata-prune)
#   J8  refs/jj/root and refs/jj/remote-tags/x present with no
#       keep refs                                              -> unchanged (byte-identical)
#   J9  real jj 0.45.1 colocated clone (optional; CASE SKIP when
#       jj is absent) reproduces J1/J3 with genuine keep refs
#   J10 directory target: keep-only predecessors with identical or
#       re-arranged-but-published leaf blobs                  -> SAFE(pushed)
#   J11 directory target: keep-only commit adds a novel leaf  -> NOT-SAFE
#   J12 keep ref to a missing object (rev-list fails)         -> NOT-SAFE history-unverifiable
#   J13 keep ref to a non-commit object (tree/blob)           -> unchanged (SAFE pushed)
#   J14 >64K known objects on the path, keep carries a pushed
#       blob (would SIGPIPE a per-candidate printf|grep -q)    -> SAFE(pushed)
#   J15 keep blob published only on a side remote
#       (refs/remotes/upstream/*), never on local branches    -> SAFE(pushed)
# J10/J11 exercise the directory tree-id contraction: comparing `C:<rel>`
# itself over-refuses when every leaf blob is already pushed; leaf blobs
# must be compared instead. J12–J15 come from the wave-2 sentinel/mutation
# survivor notes (failure-path, non-commit keep refs, SIGPIPE scale,
# branches-vs-remotes discrimination).
#
# The fixture is git-only by default: refs/jj/keep/<sha> is synthesized with
# `git update-ref`, and real jj is used only by J9. Verdicts are fixed
# expectations, never adapted to the selected tool: at the 5fa6017 base J1
# and J3 are expected to FAIL by returning SAFE, which is the paired negative
# control.
#
# Usage: r17-jj-receipts.sh [--tool-dir DIR] [--baseline-dir DIR] [--list]
#   --tool-dir DIR      directory holding souji-verify.sh (required),
#                       souji-vault-verify.sh and souji-quarantine.sh
#                       (optional; their cases print SKIP when absent).
#                       Default: this repo's tools/.
#   --baseline-dir DIR  second tool directory for the J6 byte-identity
#                       comparison (normally the other arm). Absent -> J6 SKIP.
#   --list              print the case ids and exit.
#
# Output: TOOL / TOOL-BASELINE / GIT / JJ records, SCENARIO precondition
# records, then one CASE line per check:
#   CASE<TAB>id<TAB>PASS|FAIL|SKIP<TAB>detail
# and SUMMARY<TAB>total=PASS+FAIL<TAB>failed=N<TAB>skipped=N. Exit 0 when no
# case failed, 1 when one failed, 2 on usage error or a broken scenario
# precondition. SKIP is never counted as a pass.
#
# Isolation (Q4 parity): everything lives under one private `mktemp -d` in
# /var/tmp, removed by the EXIT trap. HOME, XDG_*, GIT_CONFIG_GLOBAL,
# JJ_CONFIG (own toml) and HYAKU_STATE point inside it before any git/jj
# call; GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE/GIT_OBJECT_DIRECTORY/
# GIT_ALTERNATE_OBJECT_DIRECTORIES/GIT_COMMON_DIR and JJ_USER/JJ_EMAIL are
# unset. Every git call is `-C <tmp repo>`, every jj call is `-R <tmp repo>`
# (a jj call from the lane cwd would mutate the lane). The only remote is a
# bare repository under the scratch dir; the lane's .jj is never copied.
# gc.auto=0 and maintenance.auto=false are pinned in the scratch global
# config and on every fixture git invocation so no detached gc outlives the
# trap. The tools themselves are executed in place; their bytes are hashed,
# never rewritten.
set -uo pipefail

export LC_ALL=C

SELF_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
LANE="$(cd -- "$SELF_DIR/../.." && pwd -P)"

CASE_IDS=(
  J1 J1-vault
  J2 J2-vault
  J3 J3-vault J3-quarantine
  J4 J4-vault J4-quarantine
  J5 J5-vault J5-quarantine
  J6-verify J6-vault
  J7
  J8-verify J8-vault
  J9-file J9-worktree
  J10-verify J10-vault J10-quarantine
  J11-verify J11-vault J11-quarantine
  J12-verify J12-vault J12-quarantine
  J13-verify J13-vault J13 J13-own
  J14-verify J14-vault
  J15-verify J15-vault
)

die() { printf 'r17-jj-receipts: %s\n' "$*" >&2; exit 2; }
usage_err() { printf 'r17-jj-receipts: %s\n' "$1" >&2; exit 2; }

TOOL_DIR=""
BASELINE_DIR=""
LIST=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --tool-dir) [ "$#" -ge 2 ] || usage_err "--tool-dir needs a value"; TOOL_DIR=$2; shift 2 ;;
    --tool-dir=*) TOOL_DIR=${1#*=}; shift ;;
    --baseline-dir) [ "$#" -ge 2 ] || usage_err "--baseline-dir needs a value"; BASELINE_DIR=$2; shift 2 ;;
    --baseline-dir=*) BASELINE_DIR=${1#*=}; shift ;;
    --list) LIST=1; shift ;;
    -h|--help)
      sed -n '2,60p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) usage_err "unknown argument: $1" ;;
  esac
done
[ "$LIST" = 1 ] && { printf '%s\n' "${CASE_IDS[@]}"; exit 0; }

[ -n "$TOOL_DIR" ] || TOOL_DIR="$LANE/tools"
TOOL_DIR="$(readlink -m -- "$TOOL_DIR")"
[ -d "$TOOL_DIR" ] || die "tool dir not found: $TOOL_DIR"
VERIFY_BIN="$TOOL_DIR/souji-verify.sh"
VAULT_BIN="$TOOL_DIR/souji-vault-verify.sh"
QUARANTINE_BIN="$TOOL_DIR/souji-quarantine.sh"
[ -f "$VERIFY_BIN" ] || die "souji-verify.sh missing in $TOOL_DIR"

BASE_VERIFY="" BASE_VAULT=""
if [ -n "$BASELINE_DIR" ]; then
  BASELINE_DIR="$(readlink -m -- "$BASELINE_DIR")"
  [ -d "$BASELINE_DIR" ] || die "baseline dir not found: $BASELINE_DIR"
  [ -f "$BASELINE_DIR/souji-verify.sh" ] && BASE_VERIFY="$BASELINE_DIR/souji-verify.sh"
  [ -f "$BASELINE_DIR/souji-vault-verify.sh" ] && BASE_VAULT="$BASELINE_DIR/souji-vault-verify.sh"
fi

command -v git >/dev/null 2>&1 || die "git not found"
command -v rg >/dev/null 2>&1 || die "rg not found (the receipt engine requires it)"
command -v timeout >/dev/null 2>&1 || die "timeout not found"
command -v sha256sum >/dev/null 2>&1 || die "sha256sum not found"

# Absolute jj path resolved BEFORE HOME is redirected (existence only -- no
# jj invocation from the caller's cwd: jj 0.45.1 loads the cwd workspace's
# repo config on every call, even with -R, and would rewrite the lane's
# .jj/repo/config-id). jj is optional: only J9 uses it.
REAL_HOME=$HOME
JJ_BIN="${JJ_BIN:-}"
if [ -z "$JJ_BIN" ]; then
  if command -v jj >/dev/null 2>&1; then JJ_BIN=$(command -v jj); else
    for cand in "$REAL_HOME/.local/bin/jj" /usr/local/bin/jj /usr/bin/jj; do
      [ -x "$cand" ] && { JJ_BIN=$cand; break; }
    done
  fi
fi
[ -n "$JJ_BIN" ] && [ -x "$JJ_BIN" ] || JJ_BIN=""

T=$(mktemp -d /var/tmp/r17-jj-receipts.XXXXXX) || die "cannot create /var/tmp fixture"
case "$T" in
  /var/tmp/?*) : ;;
  *) rm -rf -- "$T"; die "scratch is not under /var/tmp: $T" ;;
esac
trap 'rm -rf -- "$T"' EXIT INT TERM HUP
cd -- "$T" || die "cannot enter scratch $T"

mkdir -p "$T/home/.config" "$T/home/.local/state" "$T/home/.cache" \
         "$T/home/.local/share" "$T/tmp" "$T/err" "$T/fleet"

export HOME="$T/home"
export XDG_CONFIG_HOME="$T/home/.config"
export XDG_STATE_HOME="$T/home/.local/state"
export XDG_CACHE_HOME="$T/home/.cache"
export XDG_DATA_HOME="$T/home/.local/share"
export GIT_CONFIG_GLOBAL="$T/gitconfig"
export GIT_CONFIG_NOSYSTEM=1
export GIT_TERMINAL_PROMPT=0
export GIT_CEILING_DIRECTORIES="$T"
export HYAKU_STATE="$T/hyaku-state"
export JJ_CONFIG="$T/jj.toml"
export TMPDIR="$T/tmp"
export SHOKUNIN_ROOT="$T/fleet"
export SOUJI_LEDGER="$T/ledger.tsv"
export SOUJI_Q_SHOKUNIN_ROOT="$T/fleet"
export SOUJI_Q_LEDGER="$T/ledger.tsv"
export SOUJI_Q_STALE_DAYS=1
export SOUJI_VERIFY_BIN="$VERIFY_BIN"
export SOUJI_CLI_TIMEOUT=2
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY \
      GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_COMMON_DIR JJ_USER JJ_EMAIL \
      JJ_OP_HOSTNAME JJ_OP_USERNAME GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL \
      GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL 2>/dev/null || true

cat > "$GIT_CONFIG_GLOBAL" <<'EOF'
[user]
	name = r17 fixture
	email = r17@fixture.invalid
[gc]
	auto = 0
[maintenance]
	auto = false
[init]
	defaultBranch = main
[protocol "file"]
	allow = always
EOF
cat > "$JJ_CONFIG" <<'EOF'
[user]
name = "r17 fixture"
email = "r17@fixture.invalid"
[ui]
color = "never"
EOF
# Probed only now: cwd is the scratch dir and HOME/XDG are isolated, so jj
# cannot read or rewrite any real workspace's repo config.
JJ_VERSION="none"
[ -n "$JJ_BIN" ] && JJ_VERSION=$("$JJ_BIN" --version 2>/dev/null | head -1)
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$SOUJI_LEDGER"

g() { git -c gc.auto=0 -c maintenance.auto=false "$@"; }

PASS=0
FAIL=0
SKIP=0

record_case() { # id status detail
  local id=$1 st=$2 detail=${3:-}
  detail=${detail//$'\t'/ }
  detail=${detail//$'\n'/ }
  [ "${#detail}" -gt 300 ] && detail="${detail:0:297}..."
  printf 'CASE\t%s\t%s\t%s\n' "$id" "$st" "$detail"
  case "$st" in
    PASS) PASS=$((PASS + 1)) ;;
    FAIL) FAIL=$((FAIL + 1)) ;;
    SKIP) SKIP=$((SKIP + 1)) ;;
  esac
}
fail_case() { local id=$1; shift; record_case "$id" FAIL "$*"; }
skip_case() { local id=$1; shift; record_case "$id" SKIP "$*"; }

# ------------------------------------------------------------------ records --
printf 'TOOL-DIR\t%s\n' "$TOOL_DIR"
[ -n "$BASE_VERIFY" ] && printf 'TOOL-BASELINE\t%s\n' "$BASELINE_DIR"
printf 'GIT\t%s\n' "$(git --version 2>/dev/null)"
printf 'JJ\t%s\t%s\n' "${JJ_BIN:-none}" "$JJ_VERSION"
for t in "$VERIFY_BIN" "$VAULT_BIN" "$QUARANTINE_BIN" "$BASE_VERIFY" "$BASE_VAULT"; do
  [ -n "$t" ] && [ -f "$t" ] || continue
  printf 'TOOL\t%s\tsha256=%s\n' "$t" "$(sha256sum -- "$t" | cut -d' ' -f1)"
done

# ------------------------------------------------------------- tool workers --
V_RC=0 V_OUT=""
vfy_run() { # bin target
  V_RC=0
  V_OUT=$(timeout --kill-after=5 240 bash "$1" --stale-days 1 -- "$2" 2>"$T/err/verify.err") || V_RC=$?
}
vfy_fields() { # -> verdict|receipt|evidence
  printf '%s\n' "$V_OUT" | awk -F'\t' '$1=="VERDICT"{printf "%s|%s|%s", $3, $4, $5; exit}'
}

L_RC=0 L_OUT=""
vlt_run() { # bin target
  L_RC=0
  L_OUT=$(timeout --kill-after=5 240 bash "$1" --fallback --stale-days 1 -- "$2" 2>"$T/err/vault.err") || L_RC=$?
}
vlt_fields() { # -> verdict|receipt|evidence|r4
  local v
  v=$(printf '%s\n' "$L_OUT" | awk -F'\t' '$1=="VERDICT"{printf "%s|%s|%s", $3, $4, $5; exit}')
  printf '%s|%s' "$v" "$(printf '%s\n' "$L_OUT" | grep -m1 -E '^(NOT-)?VERIFIED\(' || true)"
}

Q_RC=0 Q_OUT=""
q_run() { # repo target
  Q_RC=0
  Q_OUT=$(timeout --kill-after=5 240 bash "$QUARANTINE_BIN" --dry-run --hold 0 \
            "$1" "$2" 2>"$T/err/quarantine.err") || Q_RC=$?
}
q_result() { # -> status|receipt|evidence
  printf '%s\n' "$Q_OUT" | awk -F'\t' '$1=="RESULT"{printf "%s|%s|%s", $3, $4, $5; exit}'
}
RECIPE_JJ_MODE=emulated
case "$JJ_VERSION" in
  "jj 0.45.1"*) RECIPE_JJ_MODE=jj-0.45.1 ;;
esac
recipe_emulator_setup() {
  mkdir -p "$T/jj-emulated-bin" || return 1
  cat > "$T/jj-emulated-bin/jj" <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
[ "$#" -eq 4 ] &&
  [ "$1" = --ignore-working-copy ] &&
  [ "$2" = config ] && [ "$3" = get ] && [ "$4" = user.name ] || exit 2
awk -F '"' '/^user\.name[[:space:]]*=/ { print $2; found=1; exit }
  END { if (!found) exit 1 }' "$PWD/.jj/repo/config.toml"
EOF
  chmod +x "$T/jj-emulated-bin/jj" || return 1
}
recipe_build_repo() { # repo lane id -> colocated repo with lane user.name
  local repo=$1 lane_id=$2
  if [ "$RECIPE_JJ_MODE" = jj-0.45.1 ]; then
    "$JJ_BIN" git clone --colocate "$SRC/origin.git" "$repo" \
      >/dev/null 2>"$T/err/recipe-jj-clone.err" || return 1
    "$JJ_BIN" -R "$repo" config set --repo user.name "$lane_id-shokunin" \
      >/dev/null 2>"$T/err/recipe-jj-config.err" || return 1
  else
    g clone -q "$SRC/origin.git" "$repo" >/dev/null 2>&1 || return 1
    g -C "$repo" checkout -q main >/dev/null 2>&1 || return 1
    mkdir -p "$repo/.jj/repo" || return 1
    printf 'user.name = "%s-shokunin"\n' "$lane_id" > "$repo/.jj/repo/config.toml" || return 1
  fi
  # jj-lane.sh init mirrors the lane id into git config (lane.id, :440);
  # the quarantine recipe reads that binding, never jj itself.
  g -C "$repo" config lane.id "$lane_id" || return 1
  [ -d "$repo/.jj" ] && [ -e "$repo/.git" ] &&
    [ -z "$(g -C "$repo" --no-optional-locks status --porcelain 2>/dev/null)" ]
}
recipe_q_run() { # repo target; route the identity query to real jj or the scoped emulator
  if [ "$RECIPE_JJ_MODE" = jj-0.45.1 ]; then
    PATH="$(dirname -- "$JJ_BIN"):$PATH" q_run "$1" "$2"
  else
    PATH="$T/jj-emulated-bin:$PATH" q_run "$1" "$2"
  fi
}
recipe_expect() { # case id repo lane-id forbidden-lane-id
  local id=$1 repo=$2 lane_id=$3 forbidden_id=$4 f st qrec qev detail recipe count
  recipe_q_run "$repo" "$repo/f.txt"
  f=$(q_result); IFS='|' read -r st qrec qev <<< "$f"
  recipe=$(printf '%s\n' "$Q_OUT" |
    awk -F '\t' '$1=="CMD" && index($3, "jj-lane.sh commit ")==1 { print $3; exit }')
  count=$(printf '%s\n' "$Q_OUT" |
    awk -F '\t' '$1=="CMD" && index($3, "jj-lane.sh commit ")==1 { n++ }
      END { print n+0 }')
  detail="mode=$RECIPE_JJ_MODE exit=$Q_RC result=${st:-none} recipe=${recipe:-none}"
  if [ "$Q_RC" != 0 ] || [ "$st" != DRY-RUN-PASS ] || [ "$count" != 1 ] ||
     [[ "$recipe" != *" --as $lane_id "* ]] ||
     [[ "$recipe" == *" --as $forbidden_id "* ]]; then
    fail_case "$id" "$detail expected=one recipe with --as $lane_id and no --as $forbidden_id"
  else
    record_case "$id" PASS "$detail"
  fi
}


# ---------------------------------------------------------------- utilities --
idx_tree_with() { # repo base_tree rel content -> tree sha (private index)
  local repo=$1 base=$2 rel=$3 content=$4 idx="$T/idx.$RANDOM" blob
  rm -f -- "$idx"
  GIT_INDEX_FILE="$idx" g -C "$repo" read-tree "$base" || return 1
  blob=$(printf '%s\n' "$content" | g -C "$repo" hash-object -w --stdin) || return 1
  GIT_INDEX_FILE="$idx" g -C "$repo" update-index --add --cacheinfo "100644,$blob,$rel" || return 1
  GIT_INDEX_FILE="$idx" g -C "$repo" write-tree
  local rc=$?
  rm -f -- "$idx"
  return "$rc"
}
idx_tree_without() { # repo base_tree rel -> tree sha
  local repo=$1 base=$2 rel=$3 idx="$T/idx.$RANDOM"
  rm -f -- "$idx"
  GIT_INDEX_FILE="$idx" g -C "$repo" read-tree "$base" || return 1
  GIT_INDEX_FILE="$idx" g -C "$repo" update-index --force-remove -- "$rel" || return 1
  GIT_INDEX_FILE="$idx" g -C "$repo" write-tree
  local rc=$?
  rm -f -- "$idx"
  return "$rc"
}
mk_commit() { # repo tree parent msg -> commit sha
  printf '%s\n' "$4" | g -C "$1" commit-tree "$2" -p "$3" || return 1
}


# ----------------------------------------------------------------- scenario --
SRC="$T/src"
PREPO="$T/fleet/plainrepo"
KREPO="$T/fleet/keeprepo"
WT_PLAIN="$T/wt-plain"
WT_UNREF="$T/wt-plain-unref"
WT_KEEP="$T/wt-keep-only"
WT_STASH="$T/wt-stash"
WT_J9="$T/wt-j9"
BREPO="$T/fleet/brokenrepo"
BREPO2="$T/fleet/noncommitrepo"
BIGREPO="$T/fleet/bigrepo"

build_seed() {
  mkdir -p "$SRC"
  g init -q --bare "$SRC/origin.git" || die "bare origin init failed"
  g -C "$SRC/origin.git" symbolic-ref HEAD refs/heads/main || die "origin HEAD failed"
  g init -q "$SRC/seed" || die "seed init failed"
  local f
  for f in f.txt f_novel.txt f_meta.txt f_del.txt; do printf 'v1\n' > "$SRC/seed/$f"; done
  for f in f_broken.txt f_noncommit.txt f_side.txt; do printf 'v1\n' > "$SRC/seed/$f"; done
  mkdir -p "$SRC/seed/d"
  printf 'a\n' > "$SRC/seed/d/a.txt"
  printf 'b\n' > "$SRC/seed/d/b.txt"
  g -C "$SRC/seed" add . || die "seed add failed"
  g -C "$SRC/seed" commit -qm c1 || die "seed commit failed"
  g -C "$SRC/seed" branch -M main || die "seed branch failed"
  g -C "$SRC/seed" remote add origin "$SRC/origin.git" || die "seed remote failed"
  g -C "$SRC/seed" push -q origin main || die "seed push failed"
  # f_meta is published as v2 and then reverted: the v2 blob is in remote
  # history, which is what J4's non-novel predecessor must match.
  printf 'v2\n' > "$SRC/seed/f_meta.txt"
  g -C "$SRC/seed" commit -qam c2 || die "seed c2 failed"
  printf 'v1\n' > "$SRC/seed/f_meta.txt"
  g -C "$SRC/seed" commit -qam c3 || die "seed c3 failed"
  g -C "$SRC/seed" push -q origin main || die "seed c2/c3 push failed"
  g -C "$SRC/origin.git" symbolic-ref HEAD refs/heads/main || die "origin HEAD pin failed"
  C_TIP=$(g -C "$SRC/seed" rev-parse HEAD) || die "cannot resolve tip"
  BLOB_META_V1=$(g -C "$SRC/seed" rev-parse HEAD:f_meta.txt) || die "cannot resolve f_meta blob"
  BLOB_META_V2=$(g -C "$SRC/seed" rev-parse 'HEAD~1:f_meta.txt') || die "cannot resolve f_meta v2 blob"
  BLOB_NOVEL_V1=$(g -C "$SRC/seed" rev-parse HEAD:f_novel.txt) || die "cannot resolve f_novel blob"
  [ "$BLOB_META_V1" != "$BLOB_META_V2" ] || die "f_meta v1 and v2 blobs are identical"
  printf 'SCENARIO\tseed\ttip=%s\tmeta_v1=%s\tmeta_v2=%s\n' \
    "${C_TIP:0:12}" "${BLOB_META_V1:0:8}" "${BLOB_META_V2:0:8}"
}

build_plain() {
  g clone -q "$SRC/origin.git" "$PREPO" >/dev/null 2>&1 || die "plain clone failed"
  g -C "$PREPO" checkout -q main >/dev/null 2>&1 || die "plain checkout failed"

  # J6/J8/J7 share this repo's shapes: a pushed file, an absent worktree
  # reachable from refs/heads, an absent worktree no ref reaches.
  g -C "$PREPO" worktree add -q --detach "$WT_PLAIN" main \
    >/dev/null 2>"$T/err/wt-plain.err" || die "plain worktree add failed"
  rm -rf -- "$WT_PLAIN"
  [ ! -d "$WT_PLAIN" ] || die "plain absent worktree dir still present"
  C_UNREF=$(mk_commit "$PREPO" "$(g -C "$PREPO" rev-parse 'main^{tree}')" \
              "$(g -C "$PREPO" rev-parse main)" unref) || die "unref commit failed"
  g -C "$PREPO" worktree add -q --detach "$WT_UNREF" "$C_UNREF" \
    >/dev/null 2>"$T/err/wt-unref.err" || die "plain unref worktree add failed"
  rm -rf -- "$WT_UNREF"
  [ ! -d "$WT_UNREF" ] || die "plain unref worktree dir still present"
  [ -z "$(g -C "$PREPO" --no-optional-locks status --porcelain 2>/dev/null)" ] \
    || die "plain repo not clean"
  printf 'SCENARIO\tplain\tunref=%s\twts=absent\n' "${C_UNREF:0:12}"
}

build_keep_repo() {
  g clone -q "$SRC/origin.git" "$KREPO" >/dev/null 2>&1 || die "keep repo clone failed"
  g -C "$KREPO" checkout -q main >/dev/null 2>&1 || die "keep repo checkout failed"
  local tree tip
  tip=$(g -C "$KREPO" rev-parse main) || die "cannot resolve keep repo tip"
  tree=$(g -C "$KREPO" rev-parse 'main^{tree}') || die "cannot resolve keep repo tree"

  # J1/J2: worktree head held only by refs/jj/keep/*.
  C_KEEP=$(mk_commit "$KREPO" "$tree" "$tip" 'keep-only worktree head') \
    || die "keep-only worktree head commit failed"
  g -C "$KREPO" update-ref "refs/jj/keep/$C_KEEP" "$C_KEEP" || die "keep ref failed"

  # J3: keep-only commit with novel content at f_novel.txt.
  T_NOVEL=$(idx_tree_with "$KREPO" "$tree" f_novel.txt v2) || die "novel tree failed"
  C_NOVEL=$(mk_commit "$KREPO" "$T_NOVEL" "$tip" 'keep-only novel f_novel') \
    || die "novel commit failed"
  g -C "$KREPO" update-ref "refs/jj/keep/$C_NOVEL" "$C_NOVEL" || die "novel keep ref failed"

  # J4: keep-only predecessor whose f_meta blob (v2) is already published.
  T_META=$(idx_tree_with "$KREPO" "$tree" f_meta.txt v2) || die "meta tree failed"
  C_META=$(mk_commit "$KREPO" "$T_META" "$tip" 'keep-only metaedit f_meta') \
    || die "meta edit commit failed"
  g -C "$KREPO" update-ref "refs/jj/keep/$C_META" "$C_META" || die "meta keep ref failed"

  # J5: keep-only deletion of f_del.txt.
  T_DEL=$(idx_tree_without "$KREPO" "$tree" f_del.txt) || die "deletion tree failed"
  C_DEL=$(mk_commit "$KREPO" "$T_DEL" "$tip" 'keep-only delete f_del') \
    || die "deletion commit failed"
  g -C "$KREPO" update-ref "refs/jj/keep/$C_DEL" "$C_DEL" || die "deletion keep ref failed"

  # Registration for J1/J2.
  g -C "$KREPO" worktree add -q --detach "$WT_KEEP" "$C_KEEP" \
    >/dev/null 2>"$T/err/wt-keep.err" || die "keep repo worktree add failed"
  rm -rf -- "$WT_KEEP"
  [ ! -d "$WT_KEEP" ] || die "keep-only worktree dir still present"

  # Preconditions: every synthetic commit is keep-held and path-touching.
  [ "$(g -C "$KREPO" rev-list --count "$C_KEEP" --not --all 2>/dev/null)" = 0 ] \
    || die "keep-only head is not reachable from --all (keep ref missing)"
  [ "$(g -C "$KREPO" rev-list --count "$C_KEEP" --not --branches --tags --remotes)" = 1 ] \
    || die "keep-only head is reachable from a durable root"
  [ "$(g -C "$KREPO" rev-list --count "$C_NOVEL" --not --branches --tags --remotes 2>/dev/null)" = 1 ] \
    || die "novel commit is not keep-only"
  [ "$(g -C "$KREPO" rev-parse "$C_META:f_meta.txt")" = "$BLOB_META_V2" ] \
    || die "meta commit does not carry the published v2 blob"
  g -C "$KREPO" rev-parse -q --verify "$C_DEL:f_del.txt" >/dev/null \
    && die "deletion commit still carries f_del.txt"
  [ -n "$(g -C "$KREPO" rev-list --objects --remotes -- f_meta.txt |
            awk '{print $1}' | grep -Fx "$BLOB_META_V2" || true)" ] \
    || die "v2 f_meta blob is not in remote history"
  BLOB_NOVEL_V2=$(g -C "$KREPO" rev-parse "$T_NOVEL:f_novel.txt") \
    || die "cannot resolve the novel f_novel blob"
  [ "$BLOB_NOVEL_V2" != "$BLOB_NOVEL_V1" ] \
    || die "novel content is identical to the pushed blob"
  [ -z "$(g -C "$KREPO" rev-list --objects --remotes -- f_novel.txt |
            awk '{print $1}' | grep -Fx "$BLOB_NOVEL_V2" || true)" ] \
    || die "novel f_novel blob is already in remote history"
  [ -z "$(g -C "$KREPO" --no-optional-locks status --porcelain 2>/dev/null)" ] \
    || die "keep repo not clean after keep refs"
  printf 'SCENARIO\tkeeprepo\tkeep_head=%s\tkeep_novel=%s\tkeep_meta=%s\tkeep_del=%s\twts=absent\n' \
    "${C_KEEP:0:8}" "${C_NOVEL:0:8}" "${C_META:0:8}" "${C_DEL:0:8}"
}

# J10: a keep-only commit whose `d` tree is byte-identical to the pushed
# tree (never listed by the path filter -- trivially non-novel) and one
# whose `d` tree combines only already-published blobs into a tree id that
# was never pushed (the directory tree-id contraction).
build_dir_keeps() {
  local tip tree ta tb
  tip=$(g -C "$KREPO" rev-parse main) || die "cannot resolve keep repo tip"
  tree=$(g -C "$KREPO" rev-parse 'main^{tree}') || die "cannot resolve keep tree"
  C_DIRID=$(mk_commit "$KREPO" "$tree" "$tip" 'keep-only identical dir tree') \
    || die "identical dir commit failed"
  g -C "$KREPO" update-ref "refs/jj/keep/$C_DIRID" "$C_DIRID" || die "dirid keep ref failed"
  ta=$(g -C "$KREPO" rev-parse 'main:d/a.txt') || die "d/a blob failed"
  tb=$(g -C "$KREPO" rev-parse 'main:d/b.txt') || die "d/b blob failed"
  local idx="$T/idx.swap"
  rm -f -- "$idx"
  GIT_INDEX_FILE="$idx" g -C "$KREPO" read-tree "$tree" || die "swap read-tree failed"
  GIT_INDEX_FILE="$idx" g -C "$KREPO" update-index --cacheinfo "100644,$tb,d/a.txt" || die "swap a failed"
  GIT_INDEX_FILE="$idx" g -C "$KREPO" update-index --cacheinfo "100644,$ta,d/b.txt" || die "swap b failed"
  T_DIRSWAP=$(GIT_INDEX_FILE="$idx" g -C "$KREPO" write-tree) || die "swap write-tree failed"
  rm -f -- "$idx"
  [ "$T_DIRSWAP" != "$tree" ] || die "swapped tree equals the pushed tree"
  [ "$(g -C "$KREPO" rev-parse "$T_DIRSWAP:d/a.txt")" = "$tb" ] \
    && [ "$(g -C "$KREPO" rev-parse "$T_DIRSWAP:d/b.txt")" = "$ta" ] \
    || die "swap did not rearrange the published blobs"
  [ -n "$(g -C "$KREPO" diff --name-only "$tip" "$T_DIRSWAP" -- d 2>/dev/null)" ] \
    || die "swapped tree does not touch d"
  [ -z "$(g -C "$KREPO" rev-list --objects --remotes -- d |
            awk '{print $1}' | grep -Fx "$(g -C "$KREPO" rev-parse "$T_DIRSWAP:d")" || true)" ] \
    || die "swapped tree id is already in remote history (setup is not discriminating)"
  C_DIRSWAP=$(mk_commit "$KREPO" "$T_DIRSWAP" "$tip" 'keep-only rearranged dir blobs') \
    || die "swapped dir commit failed"
  g -C "$KREPO" update-ref "refs/jj/keep/$C_DIRSWAP" "$C_DIRSWAP" || die "dirswap keep ref failed"
  printf 'SCENARIO\tkeeprepo-dirs\tkeep_dirid=%s\tkeep_dirswap=%s\n' \
    "${C_DIRID:0:8}" "${C_DIRSWAP:0:8}"
}

# J12: a keep ref pointing at an object that does not exist makes the
# keep-commit enumeration fail; the (b') contract route is rc 2 ->
# history-unverifiable, never a SAFE.
build_broken_repo() {
  g clone -q "$SRC/origin.git" "$BREPO" >/dev/null 2>&1 || die "broken repo clone failed"
  g -C "$BREPO" checkout -q main >/dev/null 2>&1 || die "broken repo checkout failed"
  C_MISSING="ffffffffffffffffffffffffffffffffffffffff"
  g -C "$BREPO" cat-file -e "$C_MISSING" 2>/dev/null \
    && die "fake missing sha unexpectedly resolves"
  mkdir -p "$BREPO/.git/refs/jj/keep"
  printf '%s\n' "$C_MISSING" > "$BREPO/.git/refs/jj/keep/$C_MISSING"
  [ -n "$(g -C "$BREPO" for-each-ref --format='%(refname)' refs/jj/keep/ 2>/dev/null)" ] \
    || die "broken keep ref is not visible to for-each-ref"
  printf 'SCENARIO\tbrokenrepo\tkeep_missing=%s\n' "${C_MISSING:0:8}"
}

# J13: keep refs pointing at non-commit objects (tree and blob). git lists
# them in for-each-ref yet ignores them in rev-list, so they must not
# change any verdict.
build_noncommit_repo() {
  g clone -q "$SRC/origin.git" "$BREPO2" >/dev/null 2>&1 || die "noncommit repo clone failed"
  g -C "$BREPO2" checkout -q main >/dev/null 2>&1 || die "noncommit repo checkout failed"
  O_TREE=$(g -C "$BREPO2" rev-parse 'main^{tree}') || die "tree object failed"
  O_BLOB=$(g -C "$BREPO2" rev-parse 'main:f_noncommit.txt') || die "blob object failed"
  [ "$(g -C "$BREPO2" cat-file -t "$O_TREE")" = tree ] || die "O_TREE is not a tree"
  [ "$(g -C "$BREPO2" cat-file -t "$O_BLOB")" = blob ] || die "O_BLOB is not a blob"
  mkdir -p "$BREPO2/.git/refs/jj/keep"
  printf '%s\n' "$O_TREE" > "$BREPO2/.git/refs/jj/keep/$O_TREE"
  printf '%s\n' "$O_BLOB" > "$BREPO2/.git/refs/jj/keep/$O_BLOB"
  [ "$(g -C "$BREPO2" for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ |
       wc -l)" -ge 1 ] || die "non-commit keep refs are not listed"
  printf 'SCENARIO\tnoncommitrepo\ttree=%s\tblob=%s\n' "${O_TREE:0:8}" "${O_BLOB:0:8}"
}

# J14: a path with >64 KiB of known remote objects, where the keep-only
# predecessor carries a blob late in the listing. The wave-1 per-candidate
# `printf | grep -q` turns a grep early-exit into a SIGPIPE false-novel at
# this size; the fixed single-grep implementation must stay SAFE.
build_big_repo() {
  g init -q --bare "$SRC/big-origin.git" || die "big origin init failed"
  g -C "$SRC/big-origin.git" symbolic-ref HEAD refs/heads/main || die "big origin HEAD failed"
  {
    printf 'reset refs/heads/main\n'
    local i
    for i in $(seq 1 1200); do
      printf 'commit refs/heads/main\n'
      printf 'mark :%d\n' "$i"
      printf 'committer r17 <r17@fixture.invalid> 1700000000 +0000\n'
      printf 'data %d\nci-%d\n' "$((${#i} + 4))" "$i"
      [ "$i" -gt 1 ] && printf 'from :%d\n' "$((i - 1))"
      printf 'M 100644 inline f_big.txt\n'
      printf 'data %d\nv%d\n' "$((${#i} + 2))" "$i"
    done
  } | g -C "$SRC/big-origin.git" fast-import --quiet || die "big fast-import failed"
  g -C "$SRC/big-origin.git" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main \
    || die "big origin symref failed"
  g -C "$SRC/big-origin.git" update-ref refs/remotes/origin/main refs/heads/main || true
  g clone -q "$SRC/big-origin.git" "$BIGREPO" >/dev/null 2>&1 || die "big repo clone failed"
  g -C "$BIGREPO" checkout -q main >/dev/null 2>&1 || die "big repo checkout failed"
  local known_n blob_old
  known_n=$(g -C "$BIGREPO" rev-list --objects --remotes -- f_big.txt | wc -l)
  [ "$known_n" -ge 1000 ] || die "big repo known set too small: $known_n"
  blob_old=$(g -C "$BIGREPO" rev-parse 'origin/main~1:f_big.txt') || die "v1199 blob failed"
  # keep-only predecessor carrying a pushed blob (the v1199 content).
  local tip idx
  tip=$(g -C "$BIGREPO" rev-parse main) || die "big tip failed"
  idx="$T/idx.big"
  rm -f -- "$idx"
  GIT_INDEX_FILE="$idx" g -C "$BIGREPO" read-tree 'main~1' || die "big read-tree failed"
  C14=$(GIT_INDEX_FILE="$idx" g -C "$BIGREPO" write-tree)
  [ -n "$C14" ] || die "big write-tree failed"
  rm -f -- "$idx"
  C14=$(mk_commit "$BIGREPO" "$C14" "$tip" 'keep-only recent pushed blob') || die "big keep commit failed"
  g -C "$BIGREPO" update-ref "refs/jj/keep/$C14" "$C14" || die "big keep ref failed"
  [ "$(g -C "$BIGREPO" rev-list --count "$C14" --not --branches --tags --remotes)" = 1 ] \
    || die "big keep commit is not keep-only"
  [ "$(g -C "$BIGREPO" rev-parse "$C14:f_big.txt")" = "$blob_old" ] \
    || die "big keep commit does not carry the pushed blob"
  [ -z "$(g -C "$BIGREPO" --no-optional-locks status --porcelain 2>/dev/null)" ] \
    || die "big repo not clean"
  printf 'SCENARIO\tbigrepo\tknown=%s\tkeep=%s\tblob=%s\n' \
    "$known_n" "${C14:0:8}" "${blob_old:0:8}"
}

# J15: a blob published only through a side remote. refs/remotes/upstream/*
# is reachable via --remotes but never via --branches.
build_side_remote() {
  local tree c_side tip f_side_blob tip_blob
  tip=$(g -C "$KREPO" rev-parse main) || die "cannot resolve keep tip"
  tree=$(idx_tree_with "$KREPO" "$tip^{tree}" "f_side.txt" "side-v2") || die "side tree failed"
  c_side=$(mk_commit "$KREPO" "$tree" "$tip" 'side remote only') || die "side commit failed"
  g -C "$KREPO" update-ref refs/remotes/upstream/fork "$c_side" || die "upstream/fork ref failed"
  f_side_blob=$(g -C "$KREPO" rev-parse "$c_side:f_side.txt") || die "side blob failed"
  [ -z "$(g -C "$KREPO" rev-list --objects --branches -- f_side.txt |
           awk '{print $1}' | grep -Fx "$f_side_blob" || true)" ] \
    || die "side blob is reachable from a local branch (setup flaw)"
  [ -n "$(g -C "$KREPO" rev-list --objects --remotes -- f_side.txt |
           awk '{print $1}' | grep -Fx "$f_side_blob" || true)" ] \
    || die "side blob is not reachable from refs/remotes/*"
  # The keep-only predecessor carries that same published-elsewhere blob.
  tip_blob=$(g -C "$KREPO" rev-parse 'main:f_side.txt')
  [ "$tip_blob" != "$f_side_blob" ] || die "side blob equals pushed v1 (setup flaw)"
  local idx="$T/idx.side"
  rm -f -- "$idx"
  GIT_INDEX_FILE="$idx" g -C "$KREPO" read-tree "$tip" || die "side read-tree failed"
  GIT_INDEX_FILE="$idx" g -C "$KREPO" update-index --cacheinfo "100644,$f_side_blob,f_side.txt" \
    || die "side update-index failed"
  local tkeep
  tkeep=$(GIT_INDEX_FILE="$idx" g -C "$KREPO" write-tree) || die "side write-tree failed"
  rm -f -- "$idx"
  C_SIDEKEEP=$(mk_commit "$KREPO" "$tkeep" "$tip" 'keep-only side-remote blob') || die "sidekeep failed"
  g -C "$KREPO" update-ref "refs/jj/keep/$C_SIDEKEEP" "$C_SIDEKEEP" || die "sidekeep ref failed"
  printf 'SCENARIO\tkeeprepo-side\tfork=%s\tkeep=%s\tblob=%s\n' \
    "${c_side:0:8}" "${C_SIDEKEEP:0:8}" "${f_side_blob:0:8}"
}

# -------------------------------------------------------------------- cases --
# J10-J15 generic checkers: v_expect <id> <target> <verdict> <receipt-or-!re>
# [ev-substr]; l_expect <id> <target> <verdict> <receipt> <r4-or-!r4>
# [ev-substr]; q_expect <id> <repo> <target> <status|BLOCKED>.
v_expect() {
  local id=$1 target=$2 vwant=$3 rwant=$4 esub=${5:-} v r ev detail
  vfy_run "$VERIFY_BIN" "$target"
  local f; f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
  detail="exit=$V_RC verdict=${v:-none} receipt=${r:-none} evidence=${ev:-none}"
  if [ "$V_RC" != 0 ] || [ -z "$v" ]; then fail_case "$id" "$detail"; return; fi
  if [ "$v" != "$vwant" ]; then fail_case "$id" "$detail expected=$vwant"; return; fi
  case "$rwant" in
    '!') ;;
    '!'*) [ "$r" != "${rwant#'!'}" ] || { fail_case "$id" "$detail receipt=${rwant#'!'}!"; return; } ;;
    *) [ "$r" = "$rwant" ] || { fail_case "$id" "$detail expected-receipt=$rwant"; return; } ;;
  esac
  if [ -n "$esub" ] && [[ "$ev" != *"$esub"* ]]; then
    fail_case "$id" "$detail expected-evidence~$esub"; return
  fi
  record_case "$id" PASS "$detail"
}

l_expect() { # id target verdict receipt r4token [ev-substr]
  local id=$1 target=$2 vw=$3 recw=$4 r4w=$5 esub=${6:-} v r ev r4 detail f
  if [ ! -f "$VAULT_BIN" ]; then
    skip_case "$id" "souji-vault-verify.sh not present in tool dir"; return
  fi
  vlt_run "$VAULT_BIN" "$target"
  f=$(vlt_fields); IFS='|' read -r v r ev r4 <<< "$f"
  detail="exit=$L_RC verdict=${v:-none} receipt=${r:-none} r4=${r4:-none} evidence=${ev:-none}"
  if [ "$L_RC" != 0 ]; then fail_case "$id" "$detail"; return; fi
  if [ "$v" != "$vw" ]; then fail_case "$id" "$detail expected=$vw"; return; fi
  if [ "$r" != "$recw" ]; then fail_case "$id" "$detail expected-receipt=$recw"; return; fi
  case "$r4w" in
    '!') ;;
    '!'*) [ "$r4" != "${r4w#'!'}" ] || { fail_case "$id" "$detail r4=${r4w#'!'}!"; return; } ;;
    *) [ "$r4" = "$r4w" ] || { fail_case "$id" "$detail expected-r4=$r4w"; return; } ;;
  esac
  if [ -n "$esub" ] && [[ "$ev" != *"$esub"* ]]; then
    fail_case "$id" "$detail expected-evidence~$esub"; return
  fi
  record_case "$id" PASS "$detail"
}

q_expect() { # id repo target want-status (BLOCKED = DRY-RUN-BLOCKED|NOT-AUTHORIZED)
  local id=$1 repo=$2 target=$3 want=$4 st qrec qev detail f
  if [ ! -f "$QUARANTINE_BIN" ]; then
    skip_case "$id" "souji-quarantine.sh not present in tool dir"; return
  fi
  q_run "$repo" "$target"
  f=$(q_result); IFS='|' read -r st qrec qev <<< "$f"
  detail="exit=$Q_RC result=${st:-none} receipt=${qrec:-none} evidence=${qev:-none}"
  case "$want" in
    BLOCKED)
      [ "$st" = DRY-RUN-BLOCKED ] || [ "$st" = NOT-AUTHORIZED ] \
        || { fail_case "$id" "$detail expected=DRY-RUN-BLOCKED|NOT-AUTHORIZED"; return; } ;;
    *) [ "$st" = "$want" ] || { fail_case "$id" "$detail expected=$want"; return; } ;;
  esac
  record_case "$id" PASS "$detail"
}

# J10/J11: directory targets through every tool. First measure with only
# published-content keep predecessors (identical tree + rearranged pushed
# blobs -> SAFE), then add a keep-only commit with a novel leaf -> NOT-SAFE.
case_dirs() {
  v_expect J10-verify "$KREPO/d" SAFE pushed 'snapshot=equal'
  l_expect J10-vault "$KREPO/d" SAFE pushed 'VERIFIED(pushed)' 'snapshot=equal'
  q_expect J10-quarantine "$KREPO" "$KREPO/d" 'DRY-RUN-PASS'
  local tree novel_tip
  novel_tip=$(g -C "$KREPO" rev-parse main) || die "cannot resolve keep tip"
  tree=$(idx_tree_with "$KREPO" "$novel_tip^{tree}" "d/z.txt" "novel-dir-leaf") \
    || die "novel dir tree failed"
  C_DIRNOVEL=$(mk_commit "$KREPO" "$tree" "$novel_tip" 'keep-only novel dir leaf') \
    || die "novel dir commit failed"
  g -C "$KREPO" update-ref "refs/jj/keep/$C_DIRNOVEL" "$C_DIRNOVEL" \
    || die "novel dir keep ref failed"
  printf 'SCENARIO\tkeeprepo-dirnovel\tkeep=%s\n' "${C_DIRNOVEL:0:8}"
  v_expect J11-verify "$KREPO/d" NOT-SAFE '!'
  l_expect J11-vault "$KREPO/d" NOT-SAFE none 'NOT-VERIFIED(none)'
  q_expect J11-quarantine "$KREPO" "$KREPO/d" BLOCKED
}

# J12: a keep ref naming a missing object breaks keep enumeration; the
# history-unverifiable refusal path must win, never a pushed receipt.
case_j12() {
  v_expect J12-verify "$BREPO/f_broken.txt" NOT-SAFE '!' 'unverifiable'
  l_expect J12-vault "$BREPO/f_broken.txt" NOT-SAFE none 'NOT-VERIFIED(none)' 'unverifiable'
  q_expect J12-quarantine "$BREPO" "$BREPO/f_broken.txt" BLOCKED
}

# J13: keep refs pointing at a tree and a blob. rev-list ignores them; the
# pushed receipt must stand unchanged.
case_j13() {
  v_expect J13-verify "$BREPO2/f_noncommit.txt" SAFE pushed 'snapshot=equal'
  l_expect J13-vault "$BREPO2/f_noncommit.txt" SAFE pushed 'VERIFIED(pushed)' 'snapshot=equal'
}
# J13/J13-own: the runbook uses the recorded jj owner, not souji for every lane.
# Real jj 0.45.1 is used when available; otherwise the constrained jj shim reads
# the same repo-local user.name TOML key from the git-emulated .jj directory.
case_j13_recipe() {
  if [ ! -f "$QUARANTINE_BIN" ]; then
    skip_case J13 "souji-quarantine.sh not present in tool dir"
    skip_case J13-own "souji-quarantine.sh not present in tool dir"
    return
  fi
  if [ "$RECIPE_JJ_MODE" = emulated ] && ! recipe_emulator_setup; then
    skip_case J13 "cannot express jj user.name in the git-emulated .jj repo"
    skip_case J13-own "cannot express jj user.name in the git-emulated .jj repo"
    return
  fi
  local KAMA_REPO="$T/fleet/kama-shokunin"
  local SOUJI_REPO="$T/fleet/souji-shokunin"
  if recipe_build_repo "$KAMA_REPO" kama; then
    recipe_expect J13 "$KAMA_REPO" kama souji
  else
    fail_case J13 "cannot create jj-colocated kama-shokunin fixture"
  fi
  if recipe_build_repo "$SOUJI_REPO" souji; then
    recipe_expect J13-own "$SOUJI_REPO" souji kama
  else
    fail_case J13-own "cannot create jj-colocated souji-shokunin fixture"
  fi
}


# J14: 1200-commit remote history on the path (>64 KiB of known objects)
# and a keep-only predecessor carrying one pushed blob. A per-candidate
# `printf | grep -q` SIGPIPEs into a false novel; SAFE is required.
case_j14() {
  v_expect J14-verify "$BIGREPO/f_big.txt" SAFE pushed 'snapshot=equal'
  l_expect J14-vault "$BIGREPO/f_big.txt" SAFE pushed 'VERIFIED(pushed)' 'snapshot=equal'
}

# J15: the keep blob is published only through refs/remotes/upstream/fork,
# never through any local branch. A --branches-only known set over-refuses;
# --remotes keeps it SAFE.
case_j15() {
  v_expect J15-verify "$KREPO/f_side.txt" SAFE pushed 'snapshot=equal'
  l_expect J15-vault "$KREPO/f_side.txt" SAFE pushed 'VERIFIED(pushed)' 'snapshot=equal'
}

case_j1_j2() {
  local f v r ev detail
  # J1: head kept by jj alone.
  vfy_run "$VERIFY_BIN" "$WT_KEEP"
  f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
  detail="exit=$V_RC verdict=${v:-none} receipt=${r:-none} evidence=${ev:-none}"
  if [ "$V_RC" != 0 ] || [ -z "$v" ]; then
    fail_case J1 "$detail"
  elif [ "$v" != NOT-SAFE ] || [ "$r" = metadata-prune ]; then
    fail_case J1 "$detail expected=NOT-SAFE,never-SAFE(metadata-prune)"
  elif [[ "$ev" != *unique=* ]]; then
    fail_case J1 "$detail expected=unique= in evidence"
  else
    record_case J1 PASS "$detail"
  fi

  if [ ! -f "$VAULT_BIN" ]; then
    skip_case J1-vault "souji-vault-verify.sh not present in tool dir"
  else
    local r4
    vlt_run "$VAULT_BIN" "$WT_KEEP"
    f=$(vlt_fields); IFS='|' read -r v r ev r4 <<< "$f"
    detail="exit=$L_RC verdict=${v:-none} receipt=${r:-none} r4=${r4:-none}"
    if [ "$L_RC" != 0 ] || [ "$v" != NOT-SAFE ] || [ "$r4" = 'VERIFIED(metadata-prune)' ]; then
      fail_case J1-vault "$detail expected=NOT-SAFE,never-VERIFIED(metadata-prune)"
    else
      record_case J1-vault PASS "$detail"
    fi
  fi

  # J2: the same head becomes reachable from a branch.
  g -C "$KREPO" update-ref refs/heads/side "$C_KEEP" || die "side branch failed"
  vfy_run "$VERIFY_BIN" "$WT_KEEP"
  f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
  detail="exit=$V_RC verdict=${v:-none} receipt=${r:-none} evidence=${ev:-none}"
  if [ "$V_RC" != 0 ] || [ "$v" != SAFE ] || [ "$r" != metadata-prune ]; then
    fail_case J2 "$detail expected=SAFE/metadata-prune (head reachable from refs/heads)"
  else
    record_case J2 PASS "$detail"
  fi
  if [ ! -f "$VAULT_BIN" ]; then
    skip_case J2-vault "souji-vault-verify.sh not present in tool dir"
  else
    local r4
    vlt_run "$VAULT_BIN" "$WT_KEEP"
    f=$(vlt_fields); IFS='|' read -r v r ev r4 <<< "$f"
    detail="exit=$L_RC verdict=${v:-none} receipt=${r:-none} r4=${r4:-none}"
    if [ "$L_RC" != 0 ] || [ "$r4" != 'VERIFIED(metadata-prune)' ]; then
      fail_case J2-vault "$detail expected=VERIFIED(metadata-prune)"
    else
      record_case J2-vault PASS "$detail"
    fi
  fi
}

case_file_keeps() {
  local f v r ev detail r4 st qrec qev
  # J3: novel keep-only content must refuse.
  vfy_run "$VERIFY_BIN" "$KREPO/f_novel.txt"
  f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
  detail="exit=$V_RC verdict=${v:-none} receipt=${r:-none} evidence=${ev:-none}"
  if [ "$V_RC" != 0 ] || [ "$v" != NOT-SAFE ]; then
    fail_case J3 "$detail expected=NOT-SAFE (keep-only commit carries novel content)"
  else
    record_case J3 PASS "$detail"
  fi
  if [ ! -f "$VAULT_BIN" ]; then
    skip_case J3-vault "souji-vault-verify.sh not present in tool dir"
  else
    vlt_run "$VAULT_BIN" "$KREPO/f_novel.txt"
    f=$(vlt_fields); IFS='|' read -r v r ev r4 <<< "$f"
    detail="exit=$L_RC verdict=${v:-none} receipt=${r:-none} r4=${r4:-none}"
    if [ "$L_RC" != 0 ] || [ "$v" != NOT-SAFE ]; then
      fail_case J3-vault "$detail expected=NOT-SAFE"
    else
      record_case J3-vault PASS "$detail"
    fi
  fi
  if [ ! -f "$QUARANTINE_BIN" ]; then
    skip_case J3-quarantine "souji-quarantine.sh not present in tool dir"
  else
    q_run "$KREPO" "$KREPO/f_novel.txt"
    f=$(q_result); IFS='|' read -r st qrec qev <<< "$f"
    detail="exit=$Q_RC result=${st:-none} receipt=${qrec:-none} evidence=${qev:-none}"
    if [ "$st" != DRY-RUN-BLOCKED ] && [ "$st" != NOT-AUTHORIZED ]; then
      fail_case J3-quarantine "$detail expected=DRY-RUN-BLOCKED|NOT-AUTHORIZED"
    else
      record_case J3-quarantine PASS "$detail"
    fi
  fi

  # J4: published (non-novel) blob must not refuse.
  vfy_run "$VERIFY_BIN" "$KREPO/f_meta.txt"
  f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
  detail="exit=$V_RC verdict=${v:-none} receipt=${r:-none} evidence=${ev:-none}"
  if [ "$V_RC" != 0 ] || [ "$v" != SAFE ] || [ "$r" != pushed ]; then
    fail_case J4 "$detail expected=SAFE/pushed (blob already in remote history)"
  else
    record_case J4 PASS "$detail"
  fi
  if [ ! -f "$VAULT_BIN" ]; then
    skip_case J4-vault "souji-vault-verify.sh not present in tool dir"
  else
    vlt_run "$VAULT_BIN" "$KREPO/f_meta.txt"
    f=$(vlt_fields); IFS='|' read -r v r ev r4 <<< "$f"
    detail="exit=$L_RC verdict=${v:-none} receipt=${r:-none} r4=${r4:-none}"
    if [ "$L_RC" != 0 ] || [ "$r4" != 'VERIFIED(pushed)' ]; then
      fail_case J4-vault "$detail expected=VERIFIED(pushed)"
    else
      record_case J4-vault PASS "$detail"
    fi
  fi
  if [ ! -f "$QUARANTINE_BIN" ]; then
    skip_case J4-quarantine "souji-quarantine.sh not present in tool dir"
  else
    q_run "$KREPO" "$KREPO/f_meta.txt"
    f=$(q_result); IFS='|' read -r st qrec qev <<< "$f"
    detail="exit=$Q_RC result=${st:-none} receipt=${qrec:-none} evidence=${qev:-none}"
    if [ "$st" != DRY-RUN-PASS ]; then
      fail_case J4-quarantine "$detail expected=DRY-RUN-PASS (non-novel predecessor)"
    else
      record_case J4-quarantine PASS "$detail"
    fi
  fi

  # J5: a keep-only deletion must not refuse.
  vfy_run "$VERIFY_BIN" "$KREPO/f_del.txt"
  f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
  detail="exit=$V_RC verdict=${v:-none} receipt=${r:-none} evidence=${ev:-none}"
  if [ "$V_RC" != 0 ] || [ "$v" != SAFE ] || [ "$r" != pushed ]; then
    fail_case J5 "$detail expected=SAFE/pushed (deletions do not refuse)"
  else
    record_case J5 PASS "$detail"
  fi
  if [ ! -f "$VAULT_BIN" ]; then
    skip_case J5-vault "souji-vault-verify.sh not present in tool dir"
  else
    vlt_run "$VAULT_BIN" "$KREPO/f_del.txt"
    f=$(vlt_fields); IFS='|' read -r v r ev r4 <<< "$f"
    detail="exit=$L_RC verdict=${v:-none} receipt=${r:-none} r4=${r4:-none}"
    if [ "$L_RC" != 0 ] || [ "$r4" != 'VERIFIED(pushed)' ]; then
      fail_case J5-vault "$detail expected=VERIFIED(pushed)"
    else
      record_case J5-vault PASS "$detail"
    fi
  fi
  if [ ! -f "$QUARANTINE_BIN" ]; then
    skip_case J5-quarantine "souji-quarantine.sh not present in tool dir"
  else
    q_run "$KREPO" "$KREPO/f_del.txt"
    f=$(q_result); IFS='|' read -r st qrec qev <<< "$f"
    detail="exit=$Q_RC result=${st:-none} receipt=${qrec:-none} evidence=${qev:-none}"
    if [ "$st" != DRY-RUN-PASS ]; then
      fail_case J5-quarantine "$detail expected=DRY-RUN-PASS (deletion is not novel content)"
    else
      record_case J5-quarantine PASS "$detail"
    fi
  fi
}

# J6: plain-repo stdout must be byte-identical across the two tool dirs.
J6_TARGETS=()
case_j6() {
  local t outa outb same=1 diffs=() detail
  J6_TARGETS=("$PREPO/f.txt" "$WT_PLAIN" "$WT_UNREF" "$T/no-such-target")

  if [ -z "$BASE_VERIFY" ]; then
    skip_case J6-verify "no --baseline-dir with souji-verify.sh"
  else
    for t in "${J6_TARGETS[@]}"; do
      outa=$(timeout --kill-after=5 240 bash "$VERIFY_BIN" --stale-days 1 -- "$t" 2>/dev/null)
      outb=$(timeout --kill-after=5 240 bash "$BASE_VERIFY" --stale-days 1 -- "$t" 2>/dev/null)
      if [ "$outa" != "$outb" ]; then
        same=0
        diffs+=("$(basename -- "$t"):changed=[${outa:0:70}] baseline=[${outb:0:70}]")
      fi
    done
    detail="targets=$(printf '%s,' "${J6_TARGETS[@]}"); identical=$([ "$same" = 1 ] && printf yes || printf no)"
    if [ "$same" = 1 ]; then
      record_case J6-verify PASS "$detail"
    else
      fail_case J6-verify "$detail ${diffs[0]}"
    fi
  fi

  if [ -z "$BASE_VAULT" ] || [ ! -f "$VAULT_BIN" ]; then
    skip_case J6-vault "baseline/selected souji-vault-verify.sh missing"
  else
    same=1; diffs=()
    for t in "${J6_TARGETS[@]}"; do
      outa=$(timeout --kill-after=5 240 bash "$VAULT_BIN" --fallback --stale-days 1 -- "$t" 2>/dev/null)
      outb=$(timeout --kill-after=5 240 bash "$BASE_VAULT" --fallback --stale-days 1 -- "$t" 2>/dev/null)
      if [ "$outa" != "$outb" ]; then
        same=0
        diffs+=("$(basename -- "$t"):changed=[${outa:0:70}] baseline=[${outb:0:70}]")
      fi
    done
    detail="targets=$(printf '%s,' "${J6_TARGETS[@]}"); identical=$([ "$same" = 1 ] && printf yes || printf no)"
    if [ "$same" = 1 ]; then
      record_case J6-vault PASS "$detail"
    else
      fail_case J6-vault "$detail ${diffs[0]}"
    fi
  fi
}

# J7: absent-worktree head held only by refs/stash stays SAFE.
case_j7() {
  local tree tip c_stash f v r ev detail r4
  tip=$(g -C "$PREPO" rev-parse main) || die "cannot resolve plain tip"
  tree=$(g -C "$PREPO" rev-parse 'main^{tree}') || die "cannot resolve plain tree"
  c_stash=$(mk_commit "$PREPO" "$tree" "$tip" 'stash-only worktree head') \
    || die "stash-only commit failed"
  g -C "$PREPO" worktree add -q --detach "$WT_STASH" "$c_stash" \
    >/dev/null 2>"$T/err/wt-stash.err" || die "stash worktree add failed"
  rm -rf -- "$WT_STASH"
  g -C "$PREPO" update-ref refs/stash "$c_stash" || die "refs/stash failed"
  [ "$(g -C "$PREPO" rev-list --count "$c_stash" --not --branches --tags --remotes)" = 1 ] \
    || die "stash-only head is reachable from a branch/tag/remote"

  vfy_run "$VERIFY_BIN" "$WT_STASH"
  f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
  detail="exit=$V_RC verdict=${v:-none} receipt=${r:-none} evidence=${ev:-none}"
  if [ "$V_RC" != 0 ] || [ "$v" != SAFE ] || [ "$r" != metadata-prune ]; then
    fail_case J7 "$detail expected=SAFE/metadata-prune (refs/stash is a durable root)"
  else
    record_case J7 PASS "$detail"
  fi
}

# J8: jj namespace refs without keep refs change nothing.
case_j8() {
  local f v r ev detail r4 t
  local before=() after=()
  for t in "$PREPO/f.txt" "$WT_PLAIN"; do
    before+=("$(timeout --kill-after=5 240 bash "$VERIFY_BIN" --stale-days 1 -- "$t" 2>/dev/null)")
  done
  local tree tip c_other
  tip=$(g -C "$PREPO" rev-parse main) || die "cannot resolve plain tip"
  tree=$(g -C "$PREPO" rev-parse 'main^{tree}') || die "cannot resolve plain tree"
  c_other=$(mk_commit "$PREPO" "$tree" "$tip" 'jj-root other') || die "jj-root commit failed"
  g -C "$PREPO" update-ref refs/jj/root "$tip" || die "refs/jj/root failed"
  g -C "$PREPO" update-ref refs/jj/remote-tags/x "$c_other" || die "refs/jj/remote-tags failed"
  [ -z "$(g -C "$PREPO" for-each-ref --format='%(refname)' 'refs/jj/keep/*')" ] \
    || die "J8 repo unexpectedly has keep refs"

  for t in "$PREPO/f.txt" "$WT_PLAIN"; do
    after+=("$(timeout --kill-after=5 240 bash "$VERIFY_BIN" --stale-days 1 -- "$t" 2>/dev/null)")
  done
  detail="targets=f.txt,wt-plain identical=$([ "${before[0]}" = "${after[0]}" ] && [ "${before[1]}" = "${after[1]}" ] && printf yes || printf no)"
  if [ "${before[0]}" != "${after[0]}" ] || [ "${before[1]}" != "${after[1]}" ]; then
    fail_case J8-verify "$detail changed=[${after[0]:0:80}] before=[${before[0]:0:80}]"
  else
    vfy_run "$VERIFY_BIN" "$WT_PLAIN"
    f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
    if [ "$v" != SAFE ] || [ "$r" != metadata-prune ]; then
      fail_case J8-verify "$detail expected=SAFE/metadata-prune got=${v:-none}/${r:-none}"
    else
      vfy_run "$VERIFY_BIN" "$PREPO/f.txt"
      f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
      if [ "$v" != SAFE ] || [ "$r" != pushed ]; then
        fail_case J8-verify "$detail expected=SAFE/pushed got=${v:-none}/${r:-none}"
      else
        record_case J8-verify PASS "$detail"
      fi
    fi
  fi

  if [ ! -f "$VAULT_BIN" ]; then
    skip_case J8-vault "souji-vault-verify.sh not present in tool dir"
  else
    before=(); after=()
    for t in "$PREPO/f.txt" "$WT_PLAIN"; do
      before+=("$(timeout --kill-after=5 240 bash "$VAULT_BIN" --fallback --stale-days 1 -- "$t" 2>/dev/null)")
    done
    # Re-point the namespace refs at fresh objects so the comparison is live.
    c_other=$(mk_commit "$PREPO" "$tree" "$tip" 'jj-root other 2') || die "jj-root commit 2 failed"
    g -C "$PREPO" update-ref refs/jj/remote-tags/x "$c_other" || die "refs/jj/remote-tags re-point failed"
    for t in "$PREPO/f.txt" "$WT_PLAIN"; do
      after+=("$(timeout --kill-after=5 240 bash "$VAULT_BIN" --fallback --stale-days 1 -- "$t" 2>/dev/null)")
    done
    detail="targets=f.txt,wt-plain identical=$([ "${before[0]}" = "${after[0]}" ] && [ "${before[1]}" = "${after[1]}" ] && printf yes || printf no)"
    if [ "${before[0]}" != "${after[0]}" ] || [ "${before[1]}" != "${after[1]}" ]; then
      fail_case J8-vault "$detail changed=[${after[0]:0:80}] before=[${before[0]:0:80}]"
    else
      record_case J8-vault PASS "$detail"
    fi
  fi
}

# J9: real jj (optional). A colocated clone reproduces J1/J3 from genuine
# refs/jj/keep/* exports.
case_j9() {
  if [ -z "$JJ_BIN" ]; then
    skip_case J9-file "jj absent (optional real-jj arm)"
    skip_case J9-worktree "jj absent (optional real-jj arm)"
    return
  fi
  local JREPO="$T/fleet/jjrepo" v r ev f r4 detail
  "$JJ_BIN" git clone --colocate "$SRC/origin.git" "$JREPO" \
    >/dev/null 2>"$T/err/jj-clone.err" \
    || { fail_case J9-file "jj clone failed: $(tail -1 "$T/err/jj-clone.err")"
         skip_case J9-worktree "jj clone failed"; return; }
  printf 'v2\n' > "$JREPO/f.txt"
  "$JJ_BIN" -R "$JREPO" describe -m 'jj-only f.txt v2' >/dev/null 2>"$T/err/jj9.err" \
    || { fail_case J9-file "jj describe failed: $(tail -1 "$T/err/jj9.err")"
         skip_case J9-worktree "jj describe failed"; return; }
  local c_jj
  c_jj=$("$JJ_BIN" -R "$JREPO" log -r @ --no-graph -T 'commit_id' 2>/dev/null)
  "$JJ_BIN" -R "$JREPO" new main >/dev/null 2>>"$T/err/jj9.err" \
    || { fail_case J9-file "jj new main failed: $(tail -1 "$T/err/jj9.err")"
         skip_case J9-worktree "jj new main failed"; return; }
  [ -n "$(g -C "$JREPO" for-each-ref --format='%(refname)' "refs/jj/keep/$c_jj")" ] \
    || { fail_case J9-file "jj exported no keep ref for the abandoned commit"
         skip_case J9-worktree "no keep ref"; return; }
  [ -z "$(g -C "$JREPO" --no-optional-locks status --porcelain 2>/dev/null)" ] \
    || { fail_case J9-file "real jj repo not clean after jj new main"; skip_case J9-worktree "repo dirty"; return; }

  vfy_run "$VERIFY_BIN" "$JREPO/f.txt"
  f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
  detail="jj=${JJ_VERSION%% *} keep=${c_jj:0:8} verdict=${v:-none} receipt=${r:-none}"
  if [ "$V_RC" != 0 ] || [ "$v" != NOT-SAFE ]; then
    fail_case J9-file "$detail expected=NOT-SAFE"
  else
    record_case J9-file PASS "$detail"
  fi

  g -C "$JREPO" worktree add -q --detach "$WT_J9" "$c_jj" \
    >/dev/null 2>"$T/err/wt-j9.err" \
    || { fail_case J9-worktree "git worktree add failed: $(tail -1 "$T/err/wt-j9.err")"; return; }
  rm -rf -- "$WT_J9"
  vfy_run "$VERIFY_BIN" "$WT_J9"
  f=$(vfy_fields); IFS='|' read -r v r ev <<< "$f"
  detail="jj=${JJ_VERSION%% *} keep=${c_jj:0:8} verdict=${v:-none} receipt=${r:-none} evidence=${ev:-none}"
  if [ "$V_RC" != 0 ] || [ "$v" != NOT-SAFE ] || [ "$r" = metadata-prune ]; then
    fail_case J9-worktree "$detail expected=NOT-SAFE,never-SAFE(metadata-prune)"
  else
    record_case J9-worktree PASS "$detail"
  fi
}

# --------------------------------------------------------------------- main --
build_seed
build_plain
case_j6
case_j8
case_j7
build_keep_repo
case_j1_j2
case_file_keeps
case_j9
build_dir_keeps
case_dirs
build_broken_repo
case_j12
build_noncommit_repo
case_j13
case_j13_recipe
build_big_repo
case_j14
build_side_remote
case_j15

printf 'SUMMARY\ttotal=%d\tfailed=%d\tskipped=%d\n' "$((PASS + FAIL))" "$FAIL" "$SKIP"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
