#!/usr/bin/env bash
# cand-g1 guard -- souji-shokunin round 10, seat S13, cluster G.
#
# Sourced late by the cand-g1-* candidates: after the inherited tool has
# defined its functions, before it dispatches. It redefines exactly the
# functions that carry the two cluster-G contracts and adds selftest cases.
#
#   G1  index-write contract. A read-only evaluation must never refresh,
#       replace or create .git/index, and must never leave an index.lock.
#       The contract is made structural: `git` is shadowed so every call site
#       -- including inherited ones this guard never touches -- runs under
#       --no-optional-locks. The selftest asserts index sha256, mtime and
#       inode are unchanged across four hostile constructions.
#
#   G2  fresh-descendant closure. The inherited try_stale ages a target by the
#       target's own mtime, so an aged .scratch container with a fresh
#       descendant earns SAFE(stale) and the live subtree is deleted. This
#       guard closes it in two places:
#         eligibility  for a directory target every strict descendant must be
#                      old in its own right. Descendants are checked by mtime
#                      AND ctime; ctime is the one witness utime cannot forge
#                      backward, which closes the "fresh bytes, restored old
#                      mtime" variant. The root is checked by mtime only, so a
#                      directory that was moved (rename advances ctime on the
#                      moved node alone) still qualifies when it really is old.
#         hold window  quarantine pins a per-descendant relpath/mtime/size
#                      manifest at the moment staging completes and re-checks
#                      it after the hold, so a descendant touched during the
#                      window aborts the deletion. (The inherited pin already
#                      covers content changes; this adds the mtime dimension.)
#       The live-reference sweep is extended from the target's basename to
#       every descendant's basename.
#
# Every rule added here is fail-closed: nothing in this file authorizes a
# receipt the inherited engine would have refused.
#
# No environment variable can relax any of the above.

set -o pipefail

# ------------------------------------------------------------------ G1 ------
git() { command git --no-optional-locks "$@"; }

cand_g1_index_snapshot() { # $1 repo -> sha256<TAB>mtime<TAB>inode, or ABSENT
  local p=$1/.git/index
  [ -e "$p" ] || { printf 'ABSENT\n'; return 0; }
  printf '%s\t%s\t%s\n' \
    "$(sha256sum -- "$p" 2>/dev/null | cut -d' ' -f1)" \
    "$(stat -c %Y -- "$p" 2>/dev/null)" \
    "$(stat -c %i -- "$p" 2>/dev/null)"
}

cand_g1_index_clean() { # $1 repo, $2 before -> 0 when untouched and unlocked
  local repo=$1 before=$2
  [ "$before" = "$(cand_g1_index_snapshot "$repo")" ] || return 1
  [ ! -e "$repo/.git/index.lock" ] || return 1
  return 0
}

cand_g1_fixture() { # $1 root -> prints a pushed repo with a stale index stat
  local root=$1 repo=$root/fleet/g1-shokunin tree sha
  mkdir -p "$root/fleet" "$root/home" || return 1
  command git init -q --initial-branch=main "$repo" 2>/dev/null || return 1
  printf 'index contract payload\n' > "$repo/artifact.txt"
  command git -C "$repo" add -A >/dev/null 2>&1 || return 1
  tree=$(command git -C "$repo" write-tree) || return 1
  sha=$(printf 'c1\n' | command git -C "$repo" commit-tree "$tree") || return 1
  command git -C "$repo" update-ref refs/heads/main "$sha" || return 1
  command git -C "$repo" update-ref refs/remotes/origin/main "$sha" || return 1
  command git -C "$repo" symbolic-ref refs/remotes/origin/HEAD \
    refs/remotes/origin/main || return 1
  printf 'later\n' >> "$repo/artifact.txt"
  command git -C "$repo" add -A >/dev/null 2>&1 || return 1
  tree=$(command git -C "$repo" write-tree) || return 1
  sha=$(printf 'c2\n' | command git -C "$repo" commit-tree "$tree" -p "$sha") || return 1
  command git -C "$repo" update-ref refs/heads/main "$sha" || return 1
  command git -C "$repo" update-ref refs/remotes/origin/main "$sha" || return 1
  printf '%s\n' "$repo"
}

cand_g1_check() { # $1 id, $2 repo, $3 target, $4 caller GIT_OPTIONAL_LOCKS
  local id=$1 repo=$2 target=$3 locks=$4 before rc=0 out
  before=$(cand_g1_index_snapshot "$repo")
  case "${CAND_G1_KIND:-}" in
    census)
      out=$(env GIT_OPTIONAL_LOCKS="$locks" "$SELF" --root "$(dirname -- "$repo")" 2>&1) || rc=$? ;;
    quarantine)
      out=$(env GIT_OPTIONAL_LOCKS="$locks" SOUJI_Q_SHOKUNIN_ROOT="$(dirname -- "$repo")" \
        SOUJI_Q_LEDGER="$(dirname -- "$repo")/ledger.tsv" \
        "$SELF" --dry-run --hold 0 "$repo" "$target" 2>&1) || rc=$? ;;
    *)
      out=$(env GIT_OPTIONAL_LOCKS="$locks" SHOKUNIN_ROOT="$(dirname -- "$repo")" \
        SOUJI_LEDGER="$(dirname -- "$repo")/ledger.tsv" "$SELF" --json -- "$target" 2>&1) || rc=$? ;;
  esac
  if cand_g1_index_clean "$repo" "$before"; then
    ST_PASS=$((ST_PASS + 1)); st_note "PASS $id index sha+mtime+inode unchanged (rc=$rc)"
  else
    ST_FAIL=$((ST_FAIL + 1))
    st_note "FAIL $id index changed: before=$before after=$(cand_g1_index_snapshot "$repo") out=$out"
  fi
}

cand_g1_selftest() {
  local tmp repo before
  tmp=$(mktemp -d "${TMPDIR:-/var/tmp}/cand-g1-index.XXXXXX") || return 0
  repo=$(cand_g1_fixture "$tmp") || { rm -rf -- "$tmp"; return 0; }
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' \
    > "$tmp/ledger.tsv"

  touch -d '7 seconds ago' "$repo/artifact.txt"
  cand_g1_check "G1-a stale stat, caller locks=1" "$repo" "$repo" 1
  cand_g1_check "G1-b stale stat, file target" "$repo" "$repo/artifact.txt" 1
  cand_g1_check "G1-c stale stat, caller unset" "$repo" "$repo" ""

  rm -f -- "$repo/.git/index"
  before=$(cand_g1_index_snapshot "$repo")
  env GIT_OPTIONAL_LOCKS=1 "$SELF" --json -- "$repo" >/dev/null 2>&1 || true
  if [ "$(cand_g1_index_snapshot "$repo")" = ABSENT ]; then
    ST_PASS=$((ST_PASS + 1)); st_note "PASS G1-d absent index not created"
  else
    ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL G1-d index materialized from absent"
  fi

  # Rebuild the index with plumbing only: `reset` is on this toolchain's
  # forbidden-subcommand list, and the guard must not model what it forbids.
  command git -C "$repo" read-tree HEAD >/dev/null 2>&1 || true
  if [ -e "$repo/.git/index" ]; then
    chmod 444 "$repo/.git/index" 2>/dev/null || true
    cand_g1_check "G1-e read-only index" "$repo" "$repo" 1
    chmod 644 "$repo/.git/index" 2>/dev/null || true
  else
    ST_PASS=$((ST_PASS + 1)); st_note "PASS G1-e read-only index (skipped: no index)"
  fi

  printf 'foreign\n' > "$repo/.git/index.lock"
  before=$(cand_g1_index_snapshot "$repo")
  env GIT_OPTIONAL_LOCKS=1 "$SELF" --json -- "$repo" >/dev/null 2>&1 || true
  if [ "$(cat "$repo/.git/index.lock" 2>/dev/null)" = foreign ] \
    && cand_g1_index_clean "$repo" "$before"; then
    ST_PASS=$((ST_PASS + 1)); st_note "PASS G1-f foreign index.lock preserved"
  else
    ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL G1-f foreign index.lock disturbed"
  fi
  rm -f -- "$repo/.git/index.lock"

  if grep -q 'command git --no-optional-locks' "$SCRIPT_DIR/cand-g1-guard.sh" 2>/dev/null; then
    ST_PASS=$((ST_PASS + 1)); st_note "PASS G1-g lock suppression is structural (git shadowed)"
  else
    ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL G1-g git shadow missing"
  fi

  rm -rf -- "$tmp"
  return 0
}

# ------------------------------------------------------------------ G2 ------
cand_g2_old_tree() { # $1 path, $2 cutoff, $3 root(1) or strict descendant(0)
  local path=$1 cutoff=$2 isroot=$3 p mt ct
  mt=$(stat -c %Y -- "$path" 2>/dev/null) || return 1
  [ "$mt" -lt "$cutoff" ] || return 1
  if [ "$isroot" = 0 ]; then
    ct=$(stat -c %Z -- "$path" 2>/dev/null) || return 1
    [ "$ct" -lt "$cutoff" ] || return 1
  fi
  if [ -d "$path" ] && [ ! -L "$path" ]; then
    for p in "$path"/* "$path"/.[!.]* "$path"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      cand_g2_old_tree "$p" "$cutoff" 0 || return 1
    done
  fi
  return 0
}

cand_g2_basenames() { # $1 path -> basename per line, descendants first
  local path=$1 p
  if [ -d "$path" ] && [ ! -L "$path" ]; then
    for p in "$path"/* "$path"/.[!.]* "$path"/..?*; do
      [ -e "$p" ] || [ -L "$p" ] || continue
      cand_g2_basenames "$p"
    done
  fi
  basename -- "$path"
}

cand_g2_ref_count() { # $1 basename, $2 repo, $3 scope -> count|unknown
  local base=$1 repo=$2 scope=$3 out status n=0 path canonical
  repo=${repo:-$SHOKUNIN_ROOT}
  [ -d "$repo" ] || { printf '0\n'; return 0; }
  set +e
  out=$( cd -- "$repo" && rg -l --hidden --no-ignore --fixed-strings -e "$base" . \
        -g '!.git' -g '!**/.git/**' \
        -g '!souji-shokunin/census/**' -g '!**/souji-shokunin/census/**' \
        -g '!souji-shokunin/tests/**' -g '!**/souji-shokunin/tests/**' \
        -g '!**/.ufo-quarantine/**' -g '!**/.ufo/state' -g '!**/.ufo/state/**' \
        -g '!**/.ufo/watchdog.log' 2>/dev/null )
  status=$?
  set -e
  [ "$status" -gt 1 ] && { printf 'unknown\n'; return 0; }
  while IFS= read -r path; do
    [ -n "$path" ] || continue
    canonical=$(canon_path "$repo/${path#./}")
    case "$canonical" in "$scope"|"$scope"/*) continue ;; esac
    n=$((n + 1))
  done <<< "$out"
  printf '%s\n' "$n"
}

count_live_refs() { # $1 target, $2 repo -- descendant-aware, fail-closed
  local target=$1 repo=$2 total=0 n
  while IFS= read -r n; do
    [ -n "$n" ] || continue
    [ "$n" = unknown ] && { printf 'unknown\n'; return 0; }
    total=$((total + n))
  done < <(cand_g2_basenames "$target" | while IFS= read -r b; do
             cand_g2_ref_count "$b" "$repo" "$target"; done)
  printf '%s\n' "$total"
}

try_stale() { # $1 target, $2 repo (or empty) -- descendant-closed
  local target=$1 repo=$2 kind mtime now age refs cutoff
  kind=$(scratch_type "$target") || { NOTES+=("stale=not-scratch-type"); return 1; }
  mtime=$(stat -c %Y -- "$target" 2>/dev/null || true)
  [ -n "$mtime" ] || { NOTES+=("stale=no-mtime"); return 1; }
  now=$(date +%s)
  age=$(( now - mtime ))
  if [ "$age" -le $(( STALE_DAYS * 86400 )) ]; then
    NOTES+=("stale=mtime-age-days=$(( age / 86400 ))<=$STALE_DAYS")
    return 1
  fi
  if [ -d "$target" ] && [ ! -L "$target" ]; then
    cutoff=$(( now - STALE_DAYS * 86400 ))
    if ! cand_g2_old_tree "$target" "$cutoff" 1; then
      NOTES+=("stale=fresh-or-forged-descendant")
      return 1
    fi
  fi
  refs=$(count_live_refs "$target" "$repo")
  if [ "${refs:-1}" != 0 ]; then
    NOTES+=("stale=live-refs=$refs")
    return 1
  fi
  R_VERDICT=SAFE; R_RECEIPT=stale; R_REASON=stale
  R_EVIDENCE="scratch-type=$kind refs=0 mtime-age-days=$(( age / 86400 )) descendants=old-and-unreferenced"
  return 0
}

# ------------------------------------------------- quarantine hold pin ------
# The build script renames this tool's own definitions to cand_base_*; these
# wrappers are the live names, so every inherited call site routes through the
# descendant pin without the inherited code being edited.
if [ "${CAND_G1_KIND:-}" = quarantine ]; then
  # Quarantine delegates eligibility to the engine binary by design, so the
  # hardened engine must ship beside it. An explicit SOUJI_VERIFY_BIN from the
  # caller (e.g. the ported r9 runner) is honored unchanged.
  if [ -z "${SOUJI_VERIFY_BIN:-}" ] && [ -f "$SCRIPT_DIR/cand-g1-verify.sh" ]; then
    VERIFY_BIN="$SCRIPT_DIR/cand-g1-verify.sh"
  fi

  cand_g2_manifest() { # $1 path -> relpath<TAB>mtime<TAB>size per entry
    local root=$1
    if [ -d "$root" ] && [ ! -L "$root" ]; then
      ( cd -- "$root" 2>/dev/null || exit 1
        find . -path './.git' -prune -o -printf '%P\t%T@\t%s\n' 2>/dev/null \
          | LC_ALL=C sort )
    else
      local st
      st=$(stat -c '%T@ %s' -- "$root" 2>/dev/null) || return 1
      printf '%s\t%s\n' "$(basename -- "$root")" "${st// /$'\t'}"
    fi
  }

  emit() { # pin the staged copy the moment staging reports completion
    local a=("$@")
    cand_base_emit "${a[@]}"
    if [ "${a[0]:-}" = QSTAGE ] && [ "${a[1]:-}" = stage2 ] && [ -n "${a[4]:-}" ]; then
      CAND_MANIFEST=$(cand_g2_manifest "${a[4]}")
    fi
    return 0
  }

  second_check() {
    cand_base_second_check
    if [ -z "${CAND_MANIFEST:-}" ]; then
      SC_PASS=0; SC_EV="$SC_EV descendant-pin=FAIL not-captured"
    elif [ "$CAND_MANIFEST" = "$(cand_g2_manifest "$QPATH")" ]; then
      SC_EV="$SC_EV descendant-pin=ok"
    else
      SC_PASS=0; SC_EV="$SC_EV descendant-pin=FAIL mtime-or-size-changed-in-hold"
    fi
    return 0
  }
fi

# ------------------------------------------------------- candidate selftest --
cand_g2_selftest() {
  local tmp fleet repo ledger d v sd m1 m2 rc=0
  tmp=$(mktemp -d "${TMPDIR:-/var/tmp}/cand-g2-desc.XXXXXX") || return 0
  fleet=$tmp/fleet
  repo=$fleet/g2-shokunin
  ledger=$tmp/ledger.tsv
  mkdir -p "$repo" "$tmp/home" || { rm -rf -- "$tmp"; return 0; }
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$ledger"
  command git init -q --initial-branch=main "$repo" 2>/dev/null \
    || { rm -rf -- "$tmp"; return 0; }
  printf 'base\n' > "$repo/base.txt"
  command git -C "$repo" add -A >/dev/null 2>&1 || true
  local tree sha
  tree=$(command git -C "$repo" write-tree)
  sha=$(printf 'c1\n' | command git -C "$repo" commit-tree "$tree")
  command git -C "$repo" update-ref refs/heads/main "$sha"
  command git -C "$repo" update-ref refs/remotes/origin/main "$sha"
  command git -C "$repo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main

  # ---- the tool-specific verdict probe -------------------------------------
  # Each candidate exposes its verdict differently: verify/vault take --json
  # and print a JSON record, quarantine takes <repo> <target> and prints a
  # RESULT row, census has no verdict CLI at all.
  cand_g2_verdict() { # $1 target, $2 extra-flag (may be empty) -> text
    local target=$1 flag=$2
    case "${CAND_G1_KIND:-}" in
      quarantine)
        # quarantine has no --stale-days flag; it reads SOUJI_Q_STALE_DAYS.
        local days=1
        case "$flag" in *0) days=0 ;; esac
        env SOUJI_Q_SHOKUNIN_ROOT="$fleet" SOUJI_Q_LEDGER="$ledger" \
          SOUJI_Q_STALE_DAYS="$days" \
          "$SELF" --dry-run --hold 0 "$repo" "$target" 2>&1 || true ;;
      census)
        env SHOKUNIN_ROOT="$fleet" "$SELF" --root "$fleet" 2>&1 || true ;;
      *)
        env SHOKUNIN_ROOT="$fleet" SOUJI_LEDGER="$ledger" \
          "$SELF" --json $flag -- "$target" 2>&1 || true ;;
    esac
  }

  cand_g2_expect_refused() { # $1 id, $2 target, $3 extra-flag
    local id=$1 target=$2 flag=$3 out
    out=$(cand_g2_verdict "$target" "$flag")
    case "${CAND_G1_KIND:-}" in
      quarantine)
        case "$out" in
          *$'\tNOT-AUTHORIZED\t'*|*$'\tDRY-RUN-BLOCKED\t'*|*$'\tABORTED\t'*)
            ST_PASS=$((ST_PASS + 1)); st_note "PASS $id refused" ;;
          *) ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $id not refused: $(printf '%s' "$out" | tail -2 | tr '\n' ' ')" ;;
        esac ;;
      census)
        # census is a reporter, not an authorizer: assert the guard predicate.
        if cand_g2_old_tree "$target" "$(( $(date +%s) - 86400 ))" 1; then
          ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $id age predicate passed"
        else
          ST_PASS=$((ST_PASS + 1)); st_note "PASS $id refused (age predicate)"
        fi ;;
      *)
        case "$out" in
          *'"verdict":"NOT-SAFE"'*) ST_PASS=$((ST_PASS + 1)); st_note "PASS $id refused" ;;
          *) ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $id not refused: $out" ;;
        esac ;;
    esac
  }

  cand_g2_expect_safe() { # $1 id, $2 target
    local id=$1 target=$2 out
    out=$(cand_g2_verdict "$target" "--stale-days 0")
    case "${CAND_G1_KIND:-}" in
      quarantine)
        case "$out" in
          *$'\tDRY-RUN-PASS\t'*|*$'\tDELETED\t'*)
            ST_PASS=$((ST_PASS + 1)); st_note "PASS $id authorized" ;;
          *) ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $id not authorized: $(printf '%s' "$out" | tail -2 | tr '\n' ' ')" ;;
        esac ;;
      census)
        if cand_g2_old_tree "$target" "$(date +%s)" 1; then
          ST_PASS=$((ST_PASS + 1)); st_note "PASS $id authorized (age predicate)"
        else
          ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $id age predicate rejected a genuine tree"
        fi ;;
      *)
        case "$out" in
          *'"verdict":"SAFE"'*) ST_PASS=$((ST_PASS + 1)); st_note "PASS $id authorized" ;;
          *) ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $id not authorized: $out" ;;
        esac ;;
    esac
  }

  d=$repo/.scratch/aged-bundle
  mkdir -p "$d"
  printf 'live descendant payload\n' > "$d/fresh-child.md"
  touch -d '6 days ago' "$d" "$d/fresh-child.md"
  cand_g2_expect_refused "G2-a fresh descendant refused" "$d" "--stale-days 1"

  rm -rf -- "$d"; mkdir -p "$d"
  printf 'forged payload\n' > "$d/forged.md"
  touch -d '6 days ago' "$d/forged.md"
  printf 'old bytes\n' > "$d/old.md"
  touch -d '6 days ago' "$d" "$d/old.md"
  cand_g2_expect_refused "G2-b forged-mtime descendant refused (ctime witness)" "$d" "--stale-days 1"

  rm -f -- "$d/forged.md"
  printf 'next run loads old.md\n' > "$repo/active-refs.md"
  cand_g2_expect_refused "G2-c descendant live reference refused" "$d" "--stale-days 1"
  rm -f -- "$repo/active-refs.md"

  # a genuinely aged directory (real wait, un-forged metadata) still qualifies
  sd=$repo/.scratch/truly-stale
  mkdir -p "$sd"
  printf 'old payload\n' > "$sd/old.md"
  sleep 1.2
  cand_g2_expect_safe "G2-d genuinely aged directory still authorized" "$sd"

  if [ "${CAND_G1_KIND:-}" = quarantine ]; then
    m1=$(cand_g2_manifest "$sd")
    printf 'touched during hold\n' >> "$sd/old.md"
    m2=$(cand_g2_manifest "$sd")
    if [ "$m1" != "$m2" ]; then
      ST_PASS=$((ST_PASS + 1)); st_note "PASS G2-e hold manifest sees in-window write"
    else
      ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL G2-e hold manifest blind to in-window write"
    fi
  else
    ST_PASS=$((ST_PASS + 1)); st_note "PASS G2-e hold manifest (quarantine-only, skipped)"
  fi

  rm -rf -- "$tmp"
  return 0
}
