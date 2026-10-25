#!/usr/bin/env bash
# cand-e1-regress.sh — round-10 S09 cluster-E regression battery.
#
# One fresh /var/tmp fixture per defect class, each run against BOTH the
# installed baseline tool and the cand-e1-* candidate, so every fix is shown
# as a verdict flip (unsafe acceptance -> fail-closed refusal) rather than an
# assertion about source text.
#
#   E1  any git command failure must refuse, never count as zero
#       E1a  scan scope unreadable  -> no SAFE(stale) from refs=0
#       E1b  broken branch ref      -> census never reports `clean`
#       E1c  status query fails     -> quarantine refuses the tracked target
#       E1d  history query fails    -> verify never reports SAFE(pushed)
#   E2  LC_ALL=C for case-sensitive matching incl. id_*
#       E2a  tr_TR locale           -> ID_* still flagged secret-shaped
#   E3  unique-commit count excludes the candidate's own HEAD
#       E3a  private detached commit-> no SAFE(metadata-prune); commit survives
#
# Usage: bash tools/cand-e1-regress.sh [--tools DIR] [--only a,b] [--out FILE]
# Exit 0 when every candidate check passes; 1 otherwise. Fixtures under
# /var/tmp only; the live fleet and lane repo are never read or written.
set -uo pipefail

TOOLS_DEFAULT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
TOOLS="$TOOLS_DEFAULT"
ONLY=""
OUT=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --tools) TOOLS=$(readlink -m -- "$2"); shift 2 ;;
    --tools=*) TOOLS=$(readlink -m -- "${1#*=}"); shift ;;
    --only) ONLY=$2; shift 2 ;;
    --only=*) ONLY=${1#*=}; shift ;;
    --out) OUT=$2; shift 2 ;;
    --out=*) OUT=${1#*=}; shift ;;
    -h|--help) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) printf 'cand-e1-regress: unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

want() { # $1 case id -> 0 when selected
  [ -z "$ONLY" ] && return 0
  case ",$ONLY," in *",$1,"*) return 0 ;; esac
  return 1
}

PASS=0 FAIL=0
RECORDS=""
TMPROOT=$(mktemp -d -p /var/tmp souji-r10-s09.XXXXXX)
cleanup() { rm -rf -- "$TMPROOT"; }
trap cleanup EXIT

note() { printf '%s\n' "$*"; }
record() { # $1 case, $2 detail
  RECORDS="${RECORDS}${RECORDS:+$'\n'}$1	$2"
}

ok() { PASS=$((PASS + 1)); note "PASS $1"; }
bad() { FAIL=$((FAIL + 1)); note "FAIL $1"; }

# --- fixture environment ---------------------------------------------------
# Deterministic identity and no inherited git/locale state; TMPDIR is pinned
# to /var/tmp because the host /tmp carries a disk quota.
fx_env() { # $1 fixture root -> prints nothing, exports FX_*
  FX_ROOT=$1
  FX_HOME="$FX_ROOT/home"
  FX_FLEET="$FX_ROOT/fleet"
  mkdir -p "$FX_HOME" "$FX_FLEET"
  FX_LEDGER="$FX_ROOT/ledger.tsv"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$FX_LEDGER"
  FX_GIT_ENV=(GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
    GIT_AUTHOR_NAME="s09 fixture" GIT_AUTHOR_EMAIL=s09@fixture.invalid
    GIT_COMMITTER_NAME="s09 fixture" GIT_COMMITTER_EMAIL=s09@fixture.invalid
    GIT_OPTIONAL_LOCKS=0)
  export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
  export GIT_AUTHOR_NAME="s09 fixture" GIT_AUTHOR_EMAIL=s09@fixture.invalid
  export GIT_COMMITTER_NAME="s09 fixture" GIT_COMMITTER_EMAIL=s09@fixture.invalid
}

fx_git() { env "${FX_GIT_ENV[@]}" git "$@"; }

fx_repo() { # $1 path, $2 branch; base commit + origin/<branch> pinned to it
  fx_git init -q --initial-branch="$2" "$1"
  fx_git -C "$1" symbolic-ref HEAD "refs/heads/$2"
  printf 'base\n' > "$1/base.txt"
  fx_git -C "$1" add base.txt
  fx_git -C "$1" commit -qm base
  fx_git -C "$1" update-ref "refs/remotes/origin/$2" HEAD
  fx_git -C "$1" symbolic-ref refs/remotes/origin/HEAD "refs/remotes/origin/$2"
}

# Runs one tool with a clean environment (no inherited GIT_*/SOUJI_*).
run_tool() { # $1 tool path, rest = args; prints stdout+stderr, sets RT_RC
  local tool=$1; shift
  RT_RC=0
  RT_OUT=$(env -i PATH="$PATH" HOME="$FX_HOME" TMPDIR=/var/tmp \
    LC_ALL="${RT_LC_ALL:-C}" ${RT_LANG:+LANG="$RT_LANG"} ${RT_LOCPATH:+LOCPATH="$RT_LOCPATH"} \
    SHOKUNIN_ROOT="${RT_ROOT:-$FX_FLEET}" SOUJI_LEDGER="$FX_LEDGER" \
    SOUJI_Q_SHOKUNIN_ROOT="${RT_ROOT:-$FX_FLEET}" SOUJI_Q_LEDGER="$FX_LEDGER" \
    SOUJI_VERIFY_BIN="$TOOLS/souji-verify.sh" \
    bash "$tool" "$@" 2>&1) || RT_RC=$?
}

verdict_of() { # $1 raw output -> SAFE|NOT-SAFE|other
  local line
  line=$(printf '%s\n' "$1" | head -1)
  case "$line" in
    VERDICT$'\t'*) : ;;
    *) printf 'other'; return 0 ;;
  esac
  local rest=${line#*$'\t'}
  rest=${rest#*$'\t'}
  printf '%s' "${rest%%$'\t'*}"
}

# ==========================================================================
# E1a — scan scope unreadable must not yield SAFE(stale)
# ==========================================================================
if want E1a; then
  C="$TMPROOT/e1a"; mkdir -p "$C"; fx_env "$C"
  mkdir -p "$FX_FLEET/case-shokunin/.scratch"
  TGT="$FX_FLEET/case-shokunin/.scratch/old.log"
  printf 'payload\n' > "$TGT"; touch -d '2026-09-01' "$TGT"
  printf 'see .scratch/old.log for details\n' > "$FX_FLEET/case-shokunin/NOTES.md"

  for pair in "verify:souji-verify.sh:cand-e1-verify.sh" \
              "vault:souji-vault-verify.sh:cand-e1-vault.sh"; do
    kind=${pair%%:*}; rest=${pair#*:}; base=${rest%%:*}; cand=${rest##*:}
    RT_ROOT="$FX_FLEET"; run_tool "$TOOLS/$base" "$TGT"; bv=$(verdict_of "$RT_OUT")
    RT_ROOT="$C/MISSING";  run_tool "$TOOLS/$base" "$TGT"; bb=$(verdict_of "$RT_OUT")
    RT_ROOT="$C/MISSING";  run_tool "$TOOLS/$cand" "$TGT"; cv=$(verdict_of "$RT_OUT")
    RT_ROOT="$FX_FLEET";   run_tool "$TOOLS/$cand" "$TGT"; cp_ok=$(verdict_of "$RT_OUT")
    # baseline must reproduce the defect, candidate must refuse, and the
    # candidate must keep the positive control (live ref still found).
    if [ "$bb" = SAFE ] && [ "$bv" = NOT-SAFE ]; then
      ok "E1a/$kind baseline reproduces false SAFE(stale) on unreadable scope"
    else
      bad "E1a/$kind baseline did not reproduce (live=$bv missing-scope=$bb)"
    fi
    if [ "$cv" = NOT-SAFE ] && [ "$cp_ok" = NOT-SAFE ]; then
      ok "E1a/$kind candidate refuses unreadable scope, keeps live-ref refusal"
    else
      bad "E1a/$kind candidate missing-scope=$cv live=$cp_ok want NOT-SAFE/NOT-SAFE"
    fi
    record "E1a/$kind" "baseline:live=$bv,missing-scope=$bb candidate:live=$cp_ok,missing-scope=$cv"
  done
fi

# ==========================================================================
# E1b — census must never report `clean` when a git query failed
# ==========================================================================
if want E1b; then
  C="$TMPROOT/e1b"; mkdir -p "$C"; fx_env "$C"
  fx_repo "$FX_FLEET/case-shokunin" master
  # a branch ref whose object does not exist: rev-list exits 128 while
  # status/worktree-list still succeed.
  fx_git -C "$FX_FLEET/case-shokunin" update-ref refs/heads/broken HEAD
  printf '%s\n' 2222222222222222222222222222222222222222 \
    > "$FX_FLEET/case-shokunin/.git/refs/heads/broken"
  if ! fx_git -C "$FX_FLEET/case-shokunin" rev-list --count --branches --not --remotes >/dev/null 2>&1; then
    ok "E1b fixture: git rev-list really fails (rc!=0)"
  else
    bad "E1b fixture: git rev-list unexpectedly succeeded"
  fi

  row_of() { printf '%s\n' "$1" | grep -F '/case-shokunin'$'\t' | head -1; }
  flags_of() { local r; r=$(row_of "$1"); printf '%s' "${r##*$'\t'}"; }

  RT_ROOT="$FX_FLEET"; RT_LC_ALL=C; run_tool "$TOOLS/souji-census.sh" --root "$FX_FLEET"
  bflags=$(flags_of "$RT_OUT")
  RT_ROOT="$FX_FLEET"; RT_LC_ALL=C; run_tool "$TOOLS/cand-e1-census.sh" --root "$FX_FLEET"
  cflags=$(flags_of "$RT_OUT")
  case ",$bflags," in
    *",clean,"*) ok "E1b baseline reproduces false clean on failed git query ($bflags)" ;;
    *) bad "E1b baseline flags='$bflags' (wanted clean to reproduce)" ;;
  esac
  case ",$cflags," in
    *",clean,"*) bad "E1b candidate still reports clean ($cflags)" ;;
    *unverifiable*) ok "E1b candidate flags the unverifiable query ($cflags)" ;;
    *) bad "E1b candidate flags='$cflags' (no unverifiable marker)" ;;
  esac
  record "E1b" "baseline=$bflags candidate=$cflags"
fi

# ==========================================================================
# E1c — quarantine must refuse when the dirty check cannot run
# ==========================================================================
if want E1c; then
  # A status shim fails ONLY `status`; every other git query answers
  # normally, so the tool still reaches the dirty gate. Each tool gets its
  # OWN fixture: the baseline genuinely deletes, so sharing one fixture
  # would leave the candidate nothing to refuse.
  C="$TMPROOT/e1c"; mkdir -p "$C"
  mk_e1c() { # $1 fixture root
    local root=$1
    mkdir -p "$root/home" "$root/bin"
    FX_HOME="$root/home"; FX_FLEET="$root/fleet"
    mkdir -p "$FX_FLEET"
    FX_LEDGER="$root/ledger.tsv"
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$FX_LEDGER"
    fx_repo "$FX_FLEET/case-shokunin" master
    local r="$FX_FLEET/case-shokunin"
    mkdir -p "$r/bundle"; printf 'v1\n' > "$r/bundle/kept.txt"
    fx_git -C "$r" add bundle/kept.txt
    fx_git -C "$r" commit -qm "add bundle/kept.txt"
    fx_git -C "$r" update-ref refs/remotes/origin/master HEAD
    cat > "$root/bin/git" <<'SH'
#!/usr/bin/env bash
for a in "$@"; do
  if [ "$a" = status ]; then printf 'fatal: shimmed status failure\n' >&2; exit 128; fi
done
exec "$REAL_GIT" "$@"
SH
    chmod +x "$root/bin/git"
  }

  run_e1c() { # $1 root, $2 tool path
    local root=$1 tool=$2
    RT_RC=0
    RT_OUT=$(env -i PATH="$root/bin:$PATH" HOME="$root/home" TMPDIR=/var/tmp LC_ALL=C \
      REAL_GIT="$(command -v git)" \
      SHOKUNIN_ROOT="$root/fleet" SOUJI_LEDGER="$root/ledger.tsv" \
      SOUJI_Q_SHOKUNIN_ROOT="$root/fleet" SOUJI_Q_LEDGER="$root/ledger.tsv" \
      SOUJI_VERIFY_BIN="$TOOLS/souji-verify.sh" \
      bash "$tool" --hold 0 "$root/fleet/case-shokunin" \
      "$root/fleet/case-shokunin/bundle" 2>&1) || RT_RC=$?
  }

  BA="$C/base"; CA="$C/cand"
  mk_e1c "$BA"; mk_e1c "$CA"
  if ! env -i PATH="$BA/bin:$PATH" REAL_GIT="$(command -v git)" HOME="$BA/home" \
       git -C "$BA/fleet/case-shokunin" status --porcelain -- bundle >/dev/null 2>&1; then
    ok "E1c fixture: git status really fails (rc!=0)"
  else
    bad "E1c fixture: git status unexpectedly succeeded"
  fi

  run_e1c "$BA" "$TOOLS/souji-quarantine.sh"
  bres=$(printf '%s\n' "$RT_OUT" | grep -F 'RESULT'$'\t' | head -1)
  run_e1c "$CA" "$TOOLS/cand-e1-quarantine.sh"
  cres=$(printf '%s\n' "$RT_OUT" | grep -F 'RESULT'$'\t' | head -1)

  # The defect: the swallowed failure reads as "clean", so the tracked
  # directory is staged and deleted.
  case "$bres" in
    *DELETED*) ok "E1c baseline deletes on failed status ($bres)" ;;
    *) bad "E1c baseline did not reproduce deletion ($bres)" ;;
  esac
  case "$cres" in
    *NOT-AUTHORIZED*) ok "E1c candidate refuses on failed status ($cres)" ;;
    *) bad "E1c candidate did not refuse ($cres)" ;;
  esac
  if [ -e "$BA/fleet/case-shokunin/bundle" ]; then
    bad "E1c baseline left the bundle in place (deletion not reproduced)"
  else
    ok "E1c baseline really lost the bundle (defect is real)"
  fi
  if [ -e "$CA/fleet/case-shokunin/bundle" ]; then
    ok "E1c candidate retained the bundle"
  else
    bad "E1c candidate lost the bundle"
  fi
  record "E1c" "baseline=${bres:-none} candidate=${cres:-none} baseline_bundle=$([ -e "$BA/fleet/case-shokunin/bundle" ] && echo present || echo gone) candidate_bundle=$([ -e "$CA/fleet/case-shokunin/bundle" ] && echo present || echo gone)"
fi

# ==========================================================================
# E1d — a failing history query must not read as "nothing unpushed"
# ==========================================================================
if want E1d; then
  C="$TMPROOT/e1d"; mkdir -p "$C"; fx_env "$C"
  fx_repo "$FX_FLEET/case-shokunin" master
  R="$FX_FLEET/case-shokunin"
  printf 'payload\n' > "$R/target.txt"
  fx_git -C "$R" add target.txt; fx_git -C "$R" commit -qm "add target.txt"
  fx_git -C "$R" update-ref refs/remotes/origin/master HEAD
  fx_git -C "$R" update-ref refs/heads/broken HEAD
  printf '%s\n' 3333333333333333333333333333333333333333 > "$R/.git/refs/heads/broken"
  if ! fx_git -C "$R" log --branches --not --remotes --oneline -- "$R/target.txt" >/dev/null 2>&1; then
    ok "E1d fixture: git log --branches really fails (rc!=0)"
  else
    bad "E1d fixture: git log unexpectedly succeeded"
  fi

  for pair in "verify:souji-verify.sh:cand-e1-verify.sh" \
              "vault:souji-vault-verify.sh:cand-e1-vault.sh"; do
    kind=${pair%%:*}; rest=${pair#*:}; base=${rest%%:*}; cand=${rest##*:}
    RT_ROOT="$FX_FLEET"; RT_LC_ALL=C; run_tool "$TOOLS/$base" "$R/target.txt"; bv=$(verdict_of "$RT_OUT")
    RT_ROOT="$FX_FLEET"; RT_LC_ALL=C; run_tool "$TOOLS/$cand" "$R/target.txt"; cv=$(verdict_of "$RT_OUT")
    if [ "$bv" = SAFE ]; then
      ok "E1d/$kind baseline reproduces SAFE on failed history query"
    else
      bad "E1d/$kind baseline verdict=$bv (wanted SAFE to reproduce)"
    fi
    if [ "$cv" = NOT-SAFE ]; then
      ok "E1d/$kind candidate refuses on failed history query"
    else
      bad "E1d/$kind candidate verdict=$cv want NOT-SAFE"
    fi
    record "E1d/$kind" "baseline=$bv candidate=$cv"
  done
fi

# ==========================================================================
# E2a — ID_* refusal must survive a non-C locale
# ==========================================================================
if want E2a; then
  C="$TMPROOT/e2a"; mkdir -p "$C/locale"; fx_env "$C"
  fx_repo "$FX_FLEET/case-shokunin" master
  R="$FX_FLEET/case-shokunin"
  mkdir -p "$R/.scratch"
  printf 'secret-ish payload\n' > "$R/.scratch/ID_SENTINEL.log"
  touch -d '2026-09-01' "$R/.scratch/ID_SENTINEL.log"
  fx_git -C "$R" add -A; fx_git -C "$R" commit -qm "add ID_SENTINEL.log"
  fx_git -C "$R" update-ref refs/remotes/origin/master HEAD

  if command -v localedef >/dev/null 2>&1 \
     && localedef --no-archive -i tr_TR -f UTF-8 "$C/locale/tr_TR" >/dev/null 2>&1; then
    fold=$(env -i PATH="$PATH" LOCPATH="$C/locale" LANG=tr_TR bash -c 's=ID_SENTINEL; printf "%s" "${s,,}"')
    if [ "$fold" = 'ıd_sentınel' ]; then
      ok "E2a fixture: Turkish locale is active (I -> dotless i)"
    else
      bad "E2a fixture: Turkish fold='$fold' (locale not active)"
    fi
    flags_of() { local r; r=$(printf '%s\n' "$1" | grep -F '/case-shokunin'$'\t' | head -1); printf '%s' "${r##*$'\t'}"; }

    RT_ROOT="$FX_FLEET"; RT_LC_ALL=C; RT_LANG=C; RT_LOCPATH=""
    run_tool "$TOOLS/cand-e1-census.sh" --root "$FX_FLEET"; c_ok=$(flags_of "$RT_OUT")
    RT_LC_ALL=tr_TR; RT_LANG=tr_TR; RT_LOCPATH="$C/locale"
    run_tool "$TOOLS/souji-census.sh" --root "$FX_FLEET"; b_tr=$(flags_of "$RT_OUT")
    run_tool "$TOOLS/cand-e1-census.sh" --root "$FX_FLEET"; c_tr=$(flags_of "$RT_OUT")

    case ",$c_ok," in
      *",secret-shaped,"*) ok "E2a candidate flags ID_* under C ($c_ok)" ;;
      *) bad "E2a candidate C flags='$c_ok'" ;;
    esac
    case ",$b_tr," in
      *",secret-shaped,"*) bad "E2a baseline kept the flag under tr_TR ($b_tr) - no defect" ;;
      *) ok "E2a baseline reproduces the lost flag under tr_TR ($b_tr)" ;;
    esac
    case ",$c_tr," in
      *",secret-shaped,"*) ok "E2a candidate keeps ID_* refusal under tr_TR ($c_tr)" ;;
      *) bad "E2a candidate tr_TR flags='$c_tr' (refusal lost)" ;;
    esac
    record "E2a" "C=$c_ok baseline_tr_TR=$b_tr candidate_tr_TR=$c_tr"
  else
    note "SKIP E2a (localedef or tr_TR source unavailable)"
    record "E2a" "skipped-no-turkish-locale"
  fi
fi

# ==========================================================================
# E3a — unique count must exclude the candidate's own worktree HEAD
# ==========================================================================
if want E3a; then
  C="$TMPROOT/e3a"; mkdir -p "$C"; fx_env "$C"
  fx_repo "$FX_FLEET/case-shokunin" master
  R="$FX_FLEET/case-shokunin"
  WT="$C/wt"
  # Build the private commit inside a real linked work tree, then keep the
  # registration and remove ONLY the directory (rm -rf, not `worktree
  # remove`, which would drop the registration the tool must classify).
  fx_git -C "$R" worktree add -q --detach "$WT" HEAD
  printf 'private\n' > "$WT/private.txt"
  fx_git -C "$WT" add private.txt
  fx_git -C "$WT" commit -qm "PRIVATE never-pushed commit"
  PRIV=$(fx_git -C "$WT" rev-parse HEAD)
  rm -rf -- "$WT"
  if [ -e "$R/.git/worktrees" ] && [ -n "$(ls -A "$R/.git/worktrees" 2>/dev/null)" ]; then
    ok "E3a fixture: registration kept with dir absent"
  else
    bad "E3a fixture: registration was dropped"
  fi
  if fx_git -C "$R" cat-file -e "$PRIV^{commit}" 2>/dev/null; then
    ok "E3a fixture: private commit exists before the decision"
  else
    bad "E3a fixture: private commit missing before the decision"
  fi
  # Ground truth for the fix: the commit is reachable from the registration
  # HEAD but from no durable ref.
  if [ "$(fx_git -C "$R" rev-list --count "$PRIV" --not --all 2>/dev/null)" = 0 ] \
     && [ "$(fx_git -C "$R" rev-list --count "$PRIV" --not refs/heads/master refs/remotes/origin/master -- 2>/dev/null)" = 1 ]; then
    ok "E3a fixture: --all says unique=0 while durable refs say unique=1 (skew present)"
  else
    bad "E3a fixture: unique-commit skew not reproduced"
  fi

  for pair in "verify:souji-verify.sh:cand-e1-verify.sh" \
              "vault:souji-vault-verify.sh:cand-e1-vault.sh"; do
    kind=${pair%%:*}; rest=${pair#*:}; base=${rest%%:*}; cand=${rest##*:}
    RT_ROOT="$FX_FLEET"; RT_LC_ALL=C; run_tool "$TOOLS/$base" "$WT"; bv=$(verdict_of "$RT_OUT")
    RT_ROOT="$FX_FLEET"; RT_LC_ALL=C; run_tool "$TOOLS/$cand" "$WT"; cv=$(verdict_of "$RT_OUT")
    if [ "$bv" = SAFE ]; then
      ok "E3a/$kind baseline reproduces false SAFE(metadata-prune)"
    else
      bad "E3a/$kind baseline verdict=$bv (wanted SAFE to reproduce)"
    fi
    if [ "$cv" = NOT-SAFE ]; then
      ok "E3a/$kind candidate refuses the private commit"
    else
      bad "E3a/$kind candidate verdict=$cv want NOT-SAFE"
    fi
    record "E3a/$kind" "baseline=$bv candidate=$cv private=${PRIV:0:12}"
  done

  # Acting on the unsafe receipt (fixture-only) destroys the commit; the
  # candidate's refusal is what keeps an operator from reaching this state.
  fx_git -C "$R" worktree prune
  fx_git -C "$R" reflog expire --expire=now --all >/dev/null 2>&1 || true
  fx_git -C "$R" gc --prune=now -q >/dev/null 2>&1 || true
  if fx_git -C "$R" cat-file -e "$PRIV^{commit}" 2>/dev/null; then
    note "  E3a note: commit survived fixture prune+GC"
    record "E3a-survival" "commit_present_after_prune_gc=yes"
  else
    ok "E3a consequence: acting on the baseline receipt destroys the commit"
    record "E3a-survival" "commit_present_after_prune_gc=no"
  fi
fi

# ==========================================================================
note ""
note "cand-e1-regress: $((PASS + FAIL)) checks, $FAIL failed"
if [ -n "$OUT" ]; then
  {
    printf 'tool\t%s\n' "$(basename -- "$TOOLS")"
    printf 'fixture_root\t%s\n' "$TMPROOT"
    printf 'git\t%s\n' "$(git --version 2>/dev/null || printf 'git-absent')"
    printf 'pass\t%s\nfail\t%s\n' "$PASS" "$FAIL"
    printf '%s\n' "$RECORDS"
  } > "$OUT"
  note "records written to $OUT"
fi
if [ "$FAIL" -gt 0 ]; then exit 1; fi
exit 0
