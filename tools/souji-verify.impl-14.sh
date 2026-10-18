#!/usr/bin/env bash
# souji-verify — receipt-gated artifact verifier (round-2 spec; seat S14 build).
# Spec: tools/souji-verify.spec.md. Read-only over every surface inspected.
# Host note: this ripgrep has no --basename, so reference sweeps are -F content
# searches using the spec's flags and exclusion globs.
set -euo pipefail

SCRIPT_PATH="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/$(basename -- "${BASH_SOURCE[0]}")"
LANE_ROOT="$(cd -- "$(dirname -- "$SCRIPT_PATH")/.." && pwd)"
FLEET_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$LANE_ROOT")}"
LEDGER="${SOUJI_LEDGER:-$LANE_ROOT/corpus/knowledge/obsidian-ledger.tsv}"

STALE_DAYS=1
JSON_OUT=0
MODE=targets
TARGETS=()
OWNERS=()
PUSHED_UNVERIFIABLE=0
PUSHED_NOTE=""

usage() {
  printf 'usage: %s [--selftest] [--stale-days N] [--json] <path>...\n' "$(basename -- "$SCRIPT_PATH")" >&2
  printf 'env: SHOKUNIN_ROOT=fleet-root SOUJI_LEDGER=obsidian-ledger.tsv\n' >&2
}

require_tools() {
  local t
  for t in git rg sha256sum stat realpath mktemp; do
    if ! command -v "$t" >/dev/null 2>&1; then
      printf 'souji-verify: required tool missing: %s\n' "$t" >&2
      exit 1
    fi
  done
}

norm_path() {
  local p="$1"
  if [ -z "$p" ]; then printf '%s' "$p"; return 0; fi
  realpath -m -- "$p" 2>/dev/null || printf '%s' "$p"
}

secret_component() {
  local p="$1" comp lc
  local -a parts=()
  IFS='/' read -r -a parts <<< "$p"
  for comp in "${parts[@]}"; do
    [ -n "$comp" ] || continue
    lc="${comp,,}"
    case "$lc" in
      .env|.env.*|*.env|*.env.*|*credential*|*secret*|id_*|*.pem) printf '%s' "$comp"; return 0 ;;
    esac
  done
  return 1
}

jesc() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\t'/\\t}"
  s="${s//$'\n'/\\n}"
  printf '%s' "$s"
}

emit() { # kind verdict receipt-or-reason evidence path
  if [ "$JSON_OUT" = 1 ]; then
    printf '{"path":"%s","kind":"%s","verdict":"%s","receipt":"%s","evidence":"%s"}\n' \
      "$(jesc "$5")" "$(jesc "$1")" "$(jesc "$2")" "$(jesc "$3")" "$(jesc "$4")"
  else
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$5" "$2" "$3" "$4"
  fi
}

find_repo_root() { # arg: existing directory; prints repo top-level
  local d="$1" out
  [ -d "$d" ] || return 1
  out=$(git -C "$d" rev-parse --show-toplevel 2>/dev/null) || return 1
  [ -n "$out" ] || return 1
  norm_path "$out"
}

resolve_default_ref() { # arg: repo root; prints default-branch ref (existing only)
  local repo="$1" sym refs n
  sym=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@') || true
  if [ -n "$sym" ]; then
    if git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$sym"; then
      printf 'refs/remotes/origin/%s' "$sym"
      return 0
    fi
  fi
  refs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin/ 2>/dev/null | grep -v '^refs/remotes/origin/HEAD$' || true)
  n=$(printf '%s\n' "$refs" | grep -c . || true)
  if [ "$n" -eq 1 ]; then
    printf '%s' "$refs"
    return 0
  fi
  if git -C "$repo" show-ref --verify --quiet refs/heads/master; then
    printf 'refs/heads/master'
    return 0
  fi
  return 1
}

build_owners() {
  local d
  OWNERS=()
  [ -d "$FLEET_ROOT" ] && OWNERS+=("$FLEET_ROOT")
  for d in "$FLEET_ROOT"/*-shokunin; do
    [ -d "$d" ] && OWNERS+=("$d")
  done
  return 0
}

worktree_lookup() { # args: target_abs [extra owner]; prints "path<TAB>owner<TAB>head<TAB>branch"
  local want="$1" extra="${2:-}" owner owner_abs out
  for owner in "${OWNERS[@]}" "$extra"; do
    [ -n "$owner" ] || continue
    [ -d "$owner" ] || continue
    owner_abs=$(norm_path "$owner")
    out=$(git -C "$owner" worktree list --porcelain 2>/dev/null | awk -v want="$want" -v owner="$owner_abs" '
      function emit_row() {
        if (n && path == want && path != owner)
          printf "%s\t%s\t%s\t%s\n", path, owner, head, br
      }
      /^worktree / { if (n) emit_row(); path = substr($0, 10); head = ""; br = ""; n = 1; next }
      /^HEAD / { head = substr($0, 6); next }
      /^branch / { br = substr($0, 8); next }
      END { if (n) emit_row() }
    ') || true
    if [ -n "$out" ]; then
      printf '%s' "$out"
      return 0
    fi
  done
  return 1
}

ledger_match() { # arg: target regular file; prints "vault<TAB>sha256"
  local target="$1" sp ssha vp vsha rest sha_src sha_vault vp_abs
  [ -f "$target" ] || return 1
  [ -r "$LEDGER" ] || return 1
  sha_src=$(sha256sum -- "$target" 2>/dev/null | cut -c1-64) || return 1
  [ -n "$sha_src" ] || return 1
  while IFS=$'\t' read -r sp ssha vp vsha rest; do
    [ -n "$sp" ] || continue
    [ "$sp" = "source_path" ] && continue
    [ "$(norm_path "$sp")" = "$target" ] || continue
    [ "$ssha" = "$sha_src" ] || continue
    [ -n "$vp" ] || continue
    vp_abs=$(norm_path "$vp")
    [ -f "$vp_abs" ] || continue
    secret_component "$vp_abs" >/dev/null 2>&1 && continue
    sha_vault=$(sha256sum -- "$vp_abs" 2>/dev/null | cut -c1-64) || true
    [ -n "$sha_vault" ] || continue
    [ "$sha_vault" = "$vsha" ] || continue
    printf '%s\t%s' "$vp_abs" "$sha_vault"
    return 0
  done < "$LEDGER"
  return 1
}

is_scratch_type() {
  local p="$1" base="${1##*/}"
  case "$p" in
    */.scratch/*|*/.scratch) return 0 ;;
  esac
  case "$base" in
    *.out|*.log|*-draft.*|*checkpoint*.json|*checkpoint*.png) return 0 ;;
  esac
  return 1
}

reference_count() { # args: sweep_root name target_abs; prints hit count excluding the target itself
  local root="$1" name="$2" tgt="$3" out filtered rc=0 n rel
  rel="${tgt#"$root"/}"
  # rg matches -g globs against the path as passed, so the sweep runs from
  # inside the root to keep the spec's repo-relative exclusion globs working.
  out=$(
    cd -- "$root" 2>/dev/null || exit 66
    rg -l -F --no-ignore \
      -g '!.git' \
      -g '!souji-shokunin/census/**' \
      -g '!souji-shokunin/tests/**' \
      -g '!**/.ufo-quarantine/**' \
      -- "$name" . 2>/dev/null
  ) || rc=$?
  [ "$rc" -le 1 ] || return 2
  filtered=$(printf '%s\n' "$out" | grep -vxF -e "$tgt" -e "./$rel" || true)
  n=$(printf '%s\n' "$filtered" | grep -c . || true)
  printf '%s' "$n"
}

evaluate_repo_root() {
  local p="$1" unpushed dirty
  # A directory cannot be sha256-hashed, so the moved-to-obsidian receipt is
  # unreachable here; every repo root therefore lands NOT-SAFE.
  unpushed=$(git -C "$p" log --branches --not --remotes --oneline 2>/dev/null | wc -l | tr -d '[:space:]') || unpushed="?"
  dirty=$(git --no-optional-locks -C "$p" status --porcelain 2>/dev/null | wc -l | tr -d '[:space:]') || dirty="?"
  emit repo-root NOT-SAFE not-preserved "unpushed=$unpushed dirty=$dirty" "$p"
}

evaluate_artifact() { # args: path_abs repo_or_empty
  local p="$1" repo="$2" k base rel intro ref m vault shv root n mtime now age
  base="${p##*/}"
  PUSHED_UNVERIFIABLE=0
  PUSHED_NOTE=""
  if [ -d "$p" ]; then k="dir"; else k="file"; fi

  if [ -n "$repo" ]; then
    rel=$(realpath -m --relative-to="$repo" -- "$p" 2>/dev/null) || rel=""
    case "$rel" in ""|/*|..*) rel="" ;; esac
    if [ -n "$rel" ]; then
      intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- ":(literal)$rel" 2>/dev/null | head -n1) || true
      if [ -n "$intro" ]; then
        ref=$(resolve_default_ref "$repo" || true)
        case "$ref" in
          refs/remotes/*)
            if git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then
              emit "$k" SAFE pushed "commit=$intro ref=${ref#refs/remotes/}" "$p"
              return 0
            fi
            ;;
          '')
            PUSHED_UNVERIFIABLE=1
            PUSHED_NOTE="no-default-branch-ref"
            ;;
          *)
            # A local-only fallback ref proves nothing about publication; the
            # ref resolves but grants no pushed receipt.
            PUSHED_UNVERIFIABLE=1
            PUSHED_NOTE="local-only-ref=$ref"
            ;;
        esac
      fi
    fi
  fi

  if m=$(ledger_match "$p"); then
    vault=${m%%$'\t'*}
    shv=${m#*$'\t'}
    emit "$k" SAFE moved-to-obsidian "vault=$vault sha256=$shv" "$p"
    return 0
  fi

  if is_scratch_type "$p"; then
    root=$(find_repo_root "$(dirname -- "$p")" 2>/dev/null || true)
    [ -n "$root" ] || root="$(dirname -- "$p")"
    if n=$(reference_count "$root" "$base" "$p"); then
      if [ "$n" -eq 0 ]; then
        mtime=$(stat -c %Y -- "$p" 2>/dev/null) || mtime=0
        now=$(date +%s)
        age=$(( now - mtime ))
        [ "$age" -ge 0 ] || age=0
        if [ "$age" -gt $(( STALE_DAYS * 86400 )) ]; then
          emit "$k" SAFE stale "refs=0 age-days=$(( age / 86400 )) mtime=$(date -u -d "@$mtime" +%Y-%m-%dT%H:%M:%SZ)" "$p"
          return 0
        fi
      fi
    fi
  fi

  if [ "$PUSHED_UNVERIFIABLE" = 1 ]; then
    emit "$k" NOT-SAFE pushed-unverifiable "${PUSHED_NOTE:-no-default-branch-ref}" "$p"
  else
    emit "$k" NOT-SAFE none "receipts=0" "$p"
  fi
}

evaluate_worktree() { # args: path_abs owner head_sha branch_ref
  local p="$1" owner="$2" head="$3" br="$4" branch_ref="" unpushed dirty unique
  if [ -n "$br" ]; then
    branch_ref="refs/heads/${br#refs/heads/}"
    if git -C "$owner" show-ref --verify --quiet "$branch_ref"; then
      unpushed=$(git -C "$owner" log --oneline "$branch_ref" --not --remotes 2>/dev/null | wc -l | tr -d '[:space:]') || unpushed=1
      if [ "$unpushed" -gt 0 ]; then
        emit worktree-registration NOT-SAFE unpushed-branch "branch=${branch_ref#refs/heads/} unpushed=$unpushed" "$p"
        return 0
      fi
    fi
  fi
  if [ -d "$p" ]; then
    if dirty=$(git --no-optional-locks -C "$p" status --porcelain 2>/dev/null | wc -l | tr -d '[:space:]'); then
      if [ "$dirty" -gt 0 ]; then
        emit worktree-registration NOT-SAFE dirty "dirty=$dirty" "$p"
        return 0
      fi
      emit worktree-registration NOT-SAFE worktree-live "dirty=0" "$p"
      return 0
    fi
    emit worktree-registration NOT-SAFE worktree-unverifiable "status-unavailable" "$p"
    return 0
  fi
  if [ -n "$head" ]; then
    # git 2.55's --all walks registered worktree HEADs, which would report every
    # registration as unique=0; reachability from real refs is the honest set.
    if unique=$(git -C "$owner" log --oneline "$head" --not --branches --remotes --tags 2>/dev/null | wc -l | tr -d '[:space:]'); then
      if [ "$unique" -eq 0 ]; then
        emit worktree-registration SAFE metadata-prune "head=$head unique=0" "$p"
        return 0
      fi
      emit worktree-registration NOT-SAFE unique-commits "head=$head unique=$unique" "$p"
      return 0
    fi
  fi
  emit worktree-registration NOT-SAFE worktree-unverifiable "no-head-record" "$p"
}

evaluate_target() {
  local raw="$1" p sc wt wt_path wt_owner wt_head wt_branch
  PUSHED_UNVERIFIABLE=0
  if [ -z "$raw" ]; then
    emit unreachable NOT-SAFE unreachable "arg=empty" "$raw"
    return 0
  fi
  if sc=$(secret_component "$raw"); then
    emit refused NOT-SAFE secrets-refusal "matched=$sc" "$raw"
    return 0
  fi
  p=$(norm_path "$raw")
  # Kind 2 is checked before the existence test so an absent worktree dir can
  # still carry the metadata-prune receipt.
  wt=$(worktree_lookup "$p" "$(find_repo_root "$(dirname -- "$p")" 2>/dev/null || true)") || true
  if [ -n "$wt" ]; then
    IFS=$'\t' read -r wt_path wt_owner wt_head wt_branch <<< "$wt"
    evaluate_worktree "$p" "$wt_owner" "$wt_head" "$wt_branch"
    return 0
  fi
  if [ ! -e "$p" ]; then
    emit unreachable NOT-SAFE unreachable "stat=missing" "$p"
    return 0
  fi
  if [ -d "$p" ] && [ -e "$p/.git" ]; then
    evaluate_repo_root "$p"
    return 0
  fi
  evaluate_artifact "$p" "$(find_repo_root "$(dirname -- "$p")" 2>/dev/null || true)"
}

st_skip() { printf 'SKIP %s\n' "$1"; }

main_targets() {
  local t rc=0
  if [ "${#TARGETS[@]}" -eq 0 ]; then
    usage
    exit 2
  fi
  if [ -e "$LEDGER" ] && [ ! -r "$LEDGER" ]; then
    printf 'souji-verify: ledger unreadable: %s\n' "$LEDGER" >&2
    exit 1
  fi
  build_owners
  for t in "${TARGETS[@]}"; do
    evaluate_target "$t" || rc=1
  done
  return "$rc"
}

# ---------------------------------------------------------------- selftest --

ST_PASS=0
ST_FAIL=0

st_ok() { ST_PASS=$((ST_PASS + 1)); printf 'ok   %s\n' "$1"; }
st_bad() { ST_FAIL=$((ST_FAIL + 1)); printf 'FAIL %s\n' "$1"; }

st_check() { # name want_verdict want_receipt want_evidence_regex target [stale_days]
  local name="$1" wv="$2" wr="$3" we="$4" target="$5" days="${6:-1}"
  local line rc=0 v r e
  line=$(bash "$SCRIPT_PATH" --stale-days "$days" -- "$target" 2>/dev/null) || rc=$?
  if [ "$rc" -ne 0 ]; then st_bad "$name: exit $rc"; return 0; fi
  v=$(printf '%s\n' "$line" | awk -F'\t' 'NR==1 { print $3 }')
  r=$(printf '%s\n' "$line" | awk -F'\t' 'NR==1 { print $4 }')
  e=$(printf '%s\n' "$line" | awk -F'\t' 'NR==1 { print $5 }')
  if [ "$v" != "$wv" ]; then st_bad "$name: verdict '$v' != '$wv'"; return 0; fi
  if [ "$r" != "$wr" ]; then st_bad "$name: receipt '$r' != '$wr'"; return 0; fi
  if [ "$we" != "-" ] && ! printf '%s' "$e" | grep -qE -- "$we"; then
    st_bad "$name: evidence '$e' !~ '$we'"
    return 0
  fi
  st_ok "$name"
}

st_exit() { # name want_rc args...
  local name="$1" want="$2"
  shift 2
  local rc=0
  bash "$SCRIPT_PATH" "$@" >/dev/null 2>&1 || rc=$?
  if [ "$rc" != "$want" ]; then st_bad "$name: exit $rc != $want"; return 0; fi
  st_ok "$name"
}

st_multi() { # name path_a path_b
  local name="$1" out n v1 v2
  out=$(bash "$SCRIPT_PATH" -- "$2" "$3" 2>/dev/null) || { st_bad "$name: exit"; return 0; }
  n=$(printf '%s\n' "$out" | grep -c . || true)
  v1=$(printf '%s\n' "$out" | awk -F'\t' 'NR==1 { print $3 "/" $4 }')
  v2=$(printf '%s\n' "$out" | awk -F'\t' 'NR==2 { print $3 "/" $4 }')
  if [ "$n" != 2 ]; then st_bad "$name: $n lines != 2"; return 0; fi
  if [ "$v1" != "SAFE/pushed" ] || [ "$v2" != "NOT-SAFE/not-preserved" ]; then
    st_bad "$name: $v1 $v2"
    return 0
  fi
  st_ok "$name"
}

st_json() { # name target want_verdict want_receipt
  local name="$1" target="$2" wv="$3" wr="$4" line
  line=$(bash "$SCRIPT_PATH" --json -- "$target" 2>/dev/null) || { st_bad "$name: exit"; return 0; }
  if ! command -v python3 >/dev/null 2>&1; then st_skip "$name (no python3)"; return 0; fi
  if printf '%s' "$line" | python3 -c '
import json, sys
d = json.loads(sys.stdin.read())
assert d["verdict"] == sys.argv[1], d
assert d["receipt"] == sys.argv[2], d
assert len(d["path"]) > 0 and "kind" in d
' "$wv" "$wr" >/dev/null 2>&1; then
    st_ok "$name"
  else
    st_bad "$name: bad json: $line"
  fi
}

fixture_git() {
  git -c user.name=souji-fixture -c user.email=fixture@shokunin.local \
      -c commit.gpgsign=false -c init.defaultBranch=main \
      -c advice.detachedHead=false "$@"
}

selftest() {
  local tmp r1 r3 ownA ownB r6 r7 r9 r11 ownC ownD vault s6 v6 t9 a1 c1 c3 loose tree own
  tmp=$(mktemp -d)
  case "$tmp" in
    /tmp/*) ;;
    *) printf 'souji-verify: selftest refusing non-/tmp mktemp dir: %s\n' "$tmp" >&2; return 1 ;;
  esac
  ST_TMP="$tmp"
  trap 'rm -rf -- "${ST_TMP:-}"' EXIT

  export GIT_CONFIG_NOSYSTEM=1
  export GIT_AUTHOR_DATE='2020-01-01T00:00:00Z'
  export GIT_COMMITTER_DATE='2020-01-01T00:00:00Z'
  export HOME="$tmp/home"
  mkdir -p "$HOME"
  export SHOKUNIN_ROOT="$tmp/fleet"
  mkdir -p "$SHOKUNIN_ROOT"
  export SOUJI_LEDGER="$tmp/ledger.tsv"

  # F1/F2 — pushed vs local-only introducing commit, origin/HEAD resolving to main
  r1="$tmp/f1"
  fixture_git init -q "$r1"
  printf 'keep\n' > "$r1/keep.txt"
  fixture_git -C "$r1" add -A
  fixture_git -C "$r1" commit -qm 'add keep.txt'
  printf 'tip\n' > "$r1/tip.txt"
  fixture_git -C "$r1" add -A
  fixture_git -C "$r1" commit -qm 'tip'
  t9=$(fixture_git -C "$r1" rev-parse HEAD)
  fixture_git -C "$r1" update-ref refs/remotes/origin/main "$t9"
  fixture_git -C "$r1" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
  printf 'local\n' > "$r1/local-only.txt"
  fixture_git -C "$r1" add -A
  fixture_git -C "$r1" commit -qm 'local only'
  st_check F1-pushed-pre-tip SAFE pushed 'commit=[0-9a-f]{40} ref=origin/main' "$r1/keep.txt"
  st_check F2-local-only-intro NOT-SAFE none 'receipts=0' "$r1/local-only.txt"

  # F3 — repo root with unpushed commits + dirty tree (kotodama-shaped)
  r3="$tmp/f3"
  fixture_git init -q "$r3"
  printf 'a\n' > "$r3/a.txt"
  fixture_git -C "$r3" add -A
  fixture_git -C "$r3" commit -qm base
  c3=$(fixture_git -C "$r3" rev-parse HEAD)
  fixture_git -C "$r3" update-ref refs/remotes/origin/main "$c3"
  printf 'b\n' >> "$r3/a.txt"
  fixture_git -C "$r3" commit -qam unpushed
  printf 'dirty\n' >> "$r3/a.txt"
  st_check F3-repo-unpushed-dirty NOT-SAFE not-preserved 'unpushed=1 dirty=1' "$r3"

  # F4/F5 — worktree registrations: prunable (pushed branch) vs unpushed branch
  ownA="$SHOKUNIN_ROOT/ownA-shokunin"
  fixture_git init -q "$ownA"
  printf 'a\n' > "$ownA/f.txt"
  fixture_git -C "$ownA" add -A
  fixture_git -C "$ownA" commit -qm c1
  a1=$(fixture_git -C "$ownA" rev-parse HEAD)
  fixture_git -C "$ownA" update-ref refs/remotes/origin/main "$a1"
  fixture_git -C "$ownA" branch wt-prune "$a1"
  fixture_git -C "$ownA" worktree add -q "$tmp/f4-wt" wt-prune
  rm -rf -- "$tmp/f4-wt"
  st_check F4-worktree-prunable SAFE metadata-prune 'head=[0-9a-f]{40} unique=0' "$tmp/f4-wt"

  ownB="$SHOKUNIN_ROOT/ownB-shokunin"
  fixture_git init -q "$ownB"
  printf 'a\n' > "$ownB/f.txt"
  fixture_git -C "$ownB" add -A
  fixture_git -C "$ownB" commit -qm c1
  a1=$(fixture_git -C "$ownB" rev-parse HEAD)
  fixture_git -C "$ownB" update-ref refs/remotes/origin/main "$a1"
  printf 'b\n' > "$ownB/g.txt"
  fixture_git -C "$ownB" add -A
  fixture_git -C "$ownB" commit -qm c2
  c1=$(fixture_git -C "$ownB" rev-parse HEAD)
  fixture_git -C "$ownB" branch wt-live "$c1"
  fixture_git -C "$ownB" worktree add -q "$tmp/f5-wt" wt-live
  rm -rf -- "$tmp/f5-wt"
  st_check F5-worktree-unpushed-branch NOT-SAFE unpushed-branch 'branch=wt-live unpushed=1' "$tmp/f5-wt"

  # F6 — ledger rows: match, source-sha mismatch, vault-sha mismatch
  r6="$tmp/f6"
  fixture_git init -q "$r6"
  printf 'report bytes\n' > "$r6/old-report.bin"
  fixture_git -C "$r6" add -A
  fixture_git -C "$r6" commit -qm 'add report'
  printf 'vault bytes\n' > "$r6/wrong-vault.bin"
  printf 'other bytes\n' > "$r6/wrong-src.bin"
  vault="$tmp/vault"
  mkdir -p "$vault"
  cp -- "$r6/old-report.bin" "$vault/old-report.bin"
  cp -- "$r6/wrong-vault.bin" "$vault/other.bin"
  s6=$(sha256sum -- "$r6/old-report.bin" | cut -c1-64)
  v6=$(sha256sum -- "$vault/old-report.bin" | cut -c1-64)
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2020-01-01\tF6 match\n' "$r6/old-report.bin" "$s6" "$vault/old-report.bin" "$v6"
    printf '%s\t%s\t%s\t%s\t2020-01-01\tF6b source-sha mismatch\n' \
      "$r6/wrong-src.bin" '0000000000000000000000000000000000000000000000000000000000000000' \
      "$vault/old-report.bin" "$v6"
    printf '%s\t%s\t%s\t%s\t2020-01-01\tF6c vault-sha mismatch\n' \
      "$r6/wrong-vault.bin" "$(sha256sum -- "$r6/wrong-vault.bin" | cut -c1-64)" \
      "$vault/other.bin" '1111111111111111111111111111111111111111111111111111111111111111'
  } > "$SOUJI_LEDGER"
  st_check F6-ledger-match SAFE moved-to-obsidian "vault=$vault/old-report.bin sha256=$v6" "$r6/old-report.bin"
  st_check F6b-ledger-source-sha-mismatch NOT-SAFE none 'receipts=0' "$r6/wrong-src.bin"
  st_check F6c-ledger-vault-sha-mismatch NOT-SAFE none 'receipts=0' "$r6/wrong-vault.bin"

  # F7/F8 — stale receipts: no refs, census-only ref (D3), live ref, fresh mtime
  r7="$tmp/f7"
  fixture_git init -q "$r7"
  mkdir -p "$r7/.scratch" "$r7/souji-shokunin/census"
  printf 'stale payload\n' > "$r7/.scratch/old-note.out"
  printf 'census payload\n' > "$r7/.scratch/census-note.out"
  printf 'referenced payload\n' > "$r7/.scratch/referenced-note.log"
  printf 'fresh payload\n' > "$r7/.scratch/new-note.out"
  printf 'mentions census-note.out only in the census dir\n' > "$r7/souji-shokunin/census/seat-01.json"
  printf 'mentions referenced-note.log as a live reference\n' > "$r7/notes.md"
  touch -d '2020-01-01T00:00:00Z' -- "$r7/.scratch/old-note.out" "$r7/.scratch/census-note.out" "$r7/.scratch/referenced-note.log"
  st_check F7-stale-zero-refs SAFE stale 'refs=0 age-days=' "$r7/.scratch/old-note.out"
  st_check F8-stale-census-excluded SAFE stale 'refs=0' "$r7/.scratch/census-note.out"
  st_check F7b-stale-live-ref NOT-SAFE none 'receipts=0' "$r7/.scratch/referenced-note.log"
  st_check F7c-stale-fresh-mtime NOT-SAFE none 'receipts=0' "$r7/.scratch/new-note.out"
  st_check F7d-stale-days-flag SAFE stale 'refs=0' "$r7/.scratch/old-note.out" 0

  # F9 — D1 fallback: no origin/HEAD, exactly one origin ref, no local master
  r9="$tmp/f9"
  fixture_git init -q --initial-branch=work "$r9"
  printf 'pushed file\n' > "$r9/f9-file.txt"
  fixture_git -C "$r9" add -A
  fixture_git -C "$r9" commit -qm 'add'
  printf 'tip\n' > "$r9/tip.txt"
  fixture_git -C "$r9" add -A
  fixture_git -C "$r9" commit -qm 'tip'
  t9=$(fixture_git -C "$r9" rev-parse HEAD)
  fixture_git -C "$r9" update-ref refs/remotes/origin/trunk "$t9"
  st_check F9-single-origin-ref-fallback SAFE pushed 'ref=origin/trunk' "$r9/f9-file.txt"

  # F10 — secret-shaped targets refuse before any inspection
  mkdir -p "$tmp/f10/.env.d"
  printf 'placeholder=1\n' > "$tmp/f10/.env"
  printf 'placeholder=1\n' > "$tmp/f10/id_rsa"
  printf 'placeholder=1\n' > "$tmp/f10/.env.d/x.txt"
  st_check F10-env-refusal NOT-SAFE secrets-refusal 'matched=\.env' "$tmp/f10/.env"
  st_check F10b-id-refusal NOT-SAFE secrets-refusal 'matched=id_rsa' "$tmp/f10/id_rsa"
  st_check F10c-env-component-refusal NOT-SAFE secrets-refusal 'matched=\.env\.d' "$tmp/f10/.env.d/x.txt"

  # extra — pushed-unverifiable, live/present worktrees, detached unique commits
  r11="$tmp/f11"
  fixture_git init -q --initial-branch=work "$r11"
  printf 'x\n' > "$r11/x.txt"
  fixture_git -C "$r11" add -A
  fixture_git -C "$r11" commit -qm 'add x'
  st_check F11-pushed-unverifiable NOT-SAFE pushed-unverifiable 'no-default-branch-ref' "$r11/x.txt"

  r11b="$tmp/f11b"
  fixture_git init -q --initial-branch=master "$r11b"
  printf 'y\n' > "$r11b/y.txt"
  fixture_git -C "$r11b" add -A
  fixture_git -C "$r11b" commit -qm 'add y'
  st_check F11b-local-master-no-remote NOT-SAFE pushed-unverifiable 'local-only-ref=refs/heads/master' "$r11b/y.txt"

  ownC="$SHOKUNIN_ROOT/ownC-shokunin"
  fixture_git init -q "$ownC"
  printf 'a\n' > "$ownC/f.txt"
  fixture_git -C "$ownC" add -A
  fixture_git -C "$ownC" commit -qm c1
  a1=$(fixture_git -C "$ownC" rev-parse HEAD)
  fixture_git -C "$ownC" update-ref refs/remotes/origin/main "$a1"
  fixture_git -C "$ownC" branch wt-clean "$a1"
  fixture_git -C "$ownC" worktree add -q "$tmp/f13-wt" wt-clean
  st_check F13-worktree-present-clean NOT-SAFE worktree-live 'dirty=0' "$tmp/f13-wt"
  printf 'z\n' > "$tmp/f13-wt/untracked.tmp"
  st_check F12-worktree-present-dirty NOT-SAFE dirty 'dirty=1' "$tmp/f13-wt"

  ownD="$SHOKUNIN_ROOT/ownD-shokunin"
  fixture_git init -q "$ownD"
  printf 'a\n' > "$ownD/f.txt"
  fixture_git -C "$ownD" add -A
  fixture_git -C "$ownD" commit -qm c1
  a1=$(fixture_git -C "$ownD" rev-parse HEAD)
  fixture_git -C "$ownD" update-ref refs/remotes/origin/main "$a1"
  tree=$(fixture_git -C "$ownD" rev-parse 'HEAD^{tree}')
  loose=$(fixture_git -C "$ownD" commit-tree "$tree" -p "$a1" -m 'loose commit')
  fixture_git -C "$ownD" worktree add -q --detach "$tmp/f14-wt" "$loose"
  rm -rf -- "$tmp/f14-wt"
  fixture_git -C "$ownD" worktree add -q --detach "$tmp/f14b-wt" "$a1"
  rm -rf -- "$tmp/f14b-wt"
  st_check F14-worktree-detached-unique NOT-SAFE unique-commits 'head=[0-9a-f]{40} unique=1' "$tmp/f14-wt"
  st_check F14b-worktree-detached-prune SAFE metadata-prune 'unique=0' "$tmp/f14b-wt"

  # CLI surface — usage exits, unreachable targets, ordering, JSON
  st_exit U1-usage-no-args 2
  st_exit U2-usage-unknown-flag 2 --frobnicate
  st_exit U3-usage-bad-days 2 --stale-days abc "$r1/keep.txt"
  st_check U5-unreachable NOT-SAFE unreachable 'stat=missing' "$tmp/no-such-target"
  st_check U6-empty-arg NOT-SAFE unreachable 'arg=empty' ""
  st_multi U7-multi-target-order "$r1/keep.txt" "$r3"
  st_json U8-json-shape "$r1/keep.txt" SAFE pushed

  printf 'SELFTEST passed=%d failed=%d\n' "$ST_PASS" "$ST_FAIL"
  [ "$ST_FAIL" -eq 0 ]
}

# --------------------------------------------------------------------- cli --

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) MODE=selftest; shift ;;
    --json) JSON_OUT=1; shift ;;
    --stale-days)
      [ "$#" -ge 2 ] || { usage; exit 2; }
      case "$2" in ''|*[!0-9]*) usage; exit 2 ;; esac
      STALE_DAYS="$2"
      shift 2
      ;;
    --stale-days=*)
      v="${1#*=}"
      case "$v" in ''|*[!0-9]*) usage; exit 2 ;; esac
      STALE_DAYS="$v"
      shift
      ;;
    --help|-h) usage; exit 0 ;;
    --) shift; while [ "$#" -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    -*) usage; exit 2 ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done

require_tools

if [ "$MODE" = selftest ]; then
  selftest
  exit $?
fi

main_targets
exit $?
