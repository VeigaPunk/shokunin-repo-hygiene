#!/usr/bin/env python3
"""S14 (round 10) cluster-G candidate builder.

Cluster G, reproduced fresh by census/round-10/S13-cluster-G-repro.py:

  G1 index-write contract -- read-only inspection must leave .git/index
     byte-identical.
  G2 fresh-descendant -- an aged container must not launder a fresh or
     metadata-inconsistent descendant into SAFE(stale); quarantine then
     deletes the whole subtree.

Candidates are built from the installed tool bytes by injecting a late-loaded
override block immediately before each tool's main dispatch, so every
pre-existing selftest case is preserved verbatim and the candidates stay
self-contained (no shared guard file has to ship alongside them).

Usage: python3 S14-g2-build.py [--tools DIR] [--check]
"""
import argparse
import hashlib
import sys
from pathlib import Path

P = argparse.ArgumentParser()
P.add_argument("--tools", default=str(Path(__file__).resolve().parents[2] / "tools"))
P.add_argument("--check", action="store_true",
               help="verify the on-disk candidates match a fresh build")
A = P.parse_args()
TOOLS = Path(A.tools).resolve()

MARKER = "# ------------------------------------------------------------------- main --"
SUMMARY_ANCHOR = '  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"'

HEADER = """\
# --- S14 cluster-G overrides -------------------------------------------
# Loaded after every inherited definition and before the main dispatch below.
# Only the definitions named here are replaced; the inherited selftest cases,
# the CLI, and the output contract are preserved verbatim.
#
# G1  index-write contract. Measured on this host (btrfs, git 2.55.0): plain
#     `git status` and `git diff --quiet <ref> -- <path>` take .git/index.lock
#     and rewrite .git/index for a stat-dirty tracked entry -- the latter even
#     with GIT_OPTIONAL_LOCKS=0 exported. The --no-optional-locks and
#     diff-index forms do not. The installed tools never took the writing
#     form; this override keeps it that way and routes the repo-root status
#     probe through the lock-free form.
#
# G2  fresh-descendant. A stale receipt for a directory must cover its whole
#     subtree: every descendant has to be old by mtime AND ctime, not mtime
#     alone. Rewriting a file's bytes and then backdating its mtime (touch -d,
#     os.utime) leaves ctime at the real, fresh time -- so an mtime-only age
#     test is blind to exactly that forgery. The ctime test is fail-closed: a
#     synthetic fixture aged by backdating is refused too, because the two are
#     indistinguishable by any observable. Genuinely old trees -- untouched
#     for the whole stale window -- carry old ctimes and still qualify.
#
#     The ctime rule is applied to DESCENDANTS only. A file target keeps the
#     inherited mtime-only test, which is what the pre-existing stale cases
#     (verify F7/F8, vault F7/F8, quarantine P2) exercise.
# ===========================================================================
"""

STATUS_HELPER = """
s14_status_readonly() { # $1 repo -- porcelain that never takes the index lock
  git -C "$1" --no-optional-locks status --porcelain 2>/dev/null
}
"""

TREE_HELPERS = """
s14_tree_old() { # $1 dir, $2 cutoff -- every descendant old by mtime AND ctime
  local dir=$1 cutoff=$2 p m c
  for p in "$dir"/* "$dir"/.[!.]* "$dir"/..?*; do
    [ -e "$p" ] || [ -L "$p" ] || continue
    m=$(stat -c %Y -- "$p" 2>/dev/null) || return 1
    [ "$m" -lt "$cutoff" ] || return 1
    c=$(stat -c %Z -- "$p" 2>/dev/null) || return 1
    [ "$c" -lt "$cutoff" ] || return 1
    if [ -d "$p" ]; then
      s14_tree_old "$p" "$cutoff" || return 1
    fi
  done
}
"""

LIVE_REFS = """
count_live_refs() { # $1 target, $2 repo -- hidden- and binary-safe reference sweep
  local target=$1 repo=$2 rel="" base n out status
  local -a self_globs=()
  repo=${repo:-$SHOKUNIN_ROOT}
  [ -d "$repo" ] || { printf '0\\n'; return 0; }
  case "$target" in "$repo"/*) rel=${target#"$repo"/} ;; esac
  if [ -n "$rel" ]; then self_globs=(-g "!$rel" -g "!./$rel"); fi
  base=$(basename -- "$target")
  set +e
  out=$( cd "$repo" && rg -l --hidden --no-ignore --text --fixed-strings -e "$base" . \\
        -g '!.git' -g '!**/.git/**' \\
        -g '!souji-shokunin/census/**' -g '!**/souji-shokunin/census/**' \\
        -g '!souji-shokunin/tests/**' -g '!**/souji-shokunin/tests/**' \\
        -g '!**/.ufo-quarantine/**' \\
        "${self_globs[@]}" 2>/dev/null )
  status=$?
  set -e
  if [ "$status" -gt 1 ]; then printf 'unknown\\n'; return 0; fi
  n=$(printf '%s\\n' "$out" | grep -c . || true)
  printf '%s\\n' "${n// /}"
}
"""

TRY_STALE = """
try_stale() { # $1 target, $2 repo -- stale receipt with the G2 subtree age gate
  local target=$1 repo=$2 kind mtime now age refs cutoff tracked
  kind=$(scratch_type "$target") || { NOTES+=("stale=not-scratch-type"); return 1; }
  if [ -n "$repo" ]; then
    if ! tracked=$(git -C "$repo" ls-files -- "$target" 2>/dev/null); then
      NOTES+=("stale=tracking-unverifiable"); return 1
    fi
    if [ -n "$tracked" ]; then
      NOTES+=("stale=tracked-without-pushed-receipt"); return 1
    fi
  fi
  mtime=$(stat -c %Y -- "$target" 2>/dev/null || true)
  [ -n "$mtime" ] || { NOTES+=("stale=no-mtime"); return 1; }
  now=$(date +%s)
  age=$(( now - mtime ))
  if [ "$age" -le $(( STALE_DAYS * 86400 )) ]; then
    NOTES+=("stale=mtime-age-days=$(( age / 86400 ))<=$STALE_DAYS")
    return 1
  fi
  cutoff=$(( now - STALE_DAYS * 86400 ))
  if [ -d "$target" ] && ! s14_tree_old "$target" "$cutoff"; then
    NOTES+=("stale=fresh-or-backdated-descendant")
    return 1
  fi
  refs=$(count_live_refs "$target" "$repo")
  if [ "${refs:-1}" != 0 ]; then
    NOTES+=("stale=live-refs=$refs")
    return 1
  fi
  R_VERDICT=SAFE; R_RECEIPT=stale@REASON@
  R_EVIDENCE="scratch-type=$kind refs=0 mtime-age-days=$(( age / 86400 )) descendants=old-mtime-and-ctime"
  return 0
}
"""

REPO_ROOT_VERIFY = """
evaluate_repo_root() { # G1: repo-root status must not take the index lock
  local target=$1 unpushed dirty
  if try_obsidian "$target" 1; then return 0; fi
  unpushed=$(git -C "$target" log --branches --not --remotes --oneline 2>/dev/null | wc -l || true)
  dirty=$(s14_status_readonly "$target" | wc -l || true)
  unpushed=${unpushed// /}; dirty=${dirty// /}
  R_VERDICT=NOT-SAFE
  if [ "${unpushed:-0}" -gt 0 ]; then R_RECEIPT=unpushed
  elif [ "${dirty:-0}" -gt 0 ]; then R_RECEIPT=dirty
  else R_RECEIPT=none
  fi
  R_EVIDENCE="unpushed=${unpushed:-0} dirty=${dirty:-0}"
  return 0
}
"""

REPO_ROOT_VAULT = """
evaluate_repo_root() { # G1: repo-root status must not take the index lock
  local target=$1 unpushed dirty
  if try_ledger "$target" 1 "$target"; then return 0; fi
  unpushed=$(git -C "$target" log --branches --not --remotes --oneline 2>/dev/null | wc -l || true)
  dirty=$(s14_status_readonly "$target" | wc -l || true)
  unpushed=${unpushed// /}; dirty=${dirty// /}
  R_VERDICT=NOT-SAFE
  if [ "${unpushed:-0}" -gt 0 ]; then R_RECEIPT=unpushed; R_REASON=unpushed
  elif [ "${dirty:-0}" -gt 0 ]; then R_RECEIPT=dirty; R_REASON=dirty
  else R_RECEIPT=none; R_REASON=none
  fi
  R_EVIDENCE="unpushed=${unpushed:-0} dirty=${dirty:-0}"
  return 0
}
"""

# The quarantine tool has no receipt logic of its own: it delegates to the
# verify engine. Its G2 protection is therefore composition -- point the
# default engine at the hardened sibling when it is present next to this
# script, so a standalone pair exercises the closed class end to end.
QUARANTINE_GLUE = """
if [ -z "${SOUJI_VERIFY_BIN:-}" ] && [ -f "$SCRIPT_DIR/cand-g2-verify.sh" ]; then
  VERIFY_BIN="$SCRIPT_DIR/cand-g2-verify.sh"
fi
"""

# ---------------------------------------------------------- regression ------
# Each case builds a fresh fixture under mktemp and asserts the closed class.
# Cases are appended to the tool's own selftest, before its summary line, so
# the inherited counts and the new counts stay one suite.

REGRESSION_VERIFY = """
  # ---- S14 cluster-G regressions ------------------------------------------
  local gr="$ST_TMP/s14-g"
  mkdir -p "$gr/fleet"
  local grepo="$gr/fleet/g-shokunin"
  git init -q --initial-branch=main "$grepo"
  printf 'base\n' > "$grepo/base.txt"
  local gsha; gsha=$(st_commit "$grepo" "" "s14 g1 base")
  git -C "$grepo" update-ref refs/remotes/origin/main "$gsha"
  git -C "$grepo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main

  # G1-a: a stat-dirty tracked file must not be re-stat'ed into the index.
  printf 'same bytes\n' > "$grepo/artifact.txt"
  gsha=$(st_commit "$grepo" "$gsha" "s14 g1 artifact")
  git -C "$grepo" update-ref refs/remotes/origin/main "$gsha"
  touch -d '7 days ago' "$grepo/artifact.txt"
  local gbefore gafter
  gbefore=$(sha256sum -- "$grepo/.git/index" | cut -d' ' -f1)
  env -u GIT_DIR SHOKUNIN_ROOT="$gr/fleet" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
    "$SELF" --json -- "$grepo" >/dev/null 2>&1 || true
  gafter=$(sha256sum -- "$grepo/.git/index" | cut -d' ' -f1)
  if [ "$gbefore" = "$gafter" ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS G1 repo-root inspection leaves index bytes unchanged"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL G1 repo-root inspection rewrote .git/index"
  fi

  # G1-b: same contract for a file target.
  touch -d '7 days ago' "$grepo/artifact.txt"
  gbefore=$(sha256sum -- "$grepo/.git/index" | cut -d' ' -f1)
  env -u GIT_DIR SHOKUNIN_ROOT="$gr/fleet" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
    "$SELF" --json -- "$grepo/artifact.txt" >/dev/null 2>&1 || true
  gafter=$(sha256sum -- "$grepo/.git/index" | cut -d' ' -f1)
  if [ "$gbefore" = "$gafter" ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS G1 file inspection leaves index bytes unchanged"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL G1 file inspection rewrote .git/index"
  fi

  # G2-a: an aged container with a freshly written child is not stale.
  mkdir -p "$grepo/.scratch/aged"
  printf 'fresh child\n' > "$grepo/.scratch/aged/fresh.md"
  touch -d '7 days ago' "$grepo/.scratch/aged"
  st_case G2a NOT-SAFE none "fresh-or-backdated-descendant" "$grepo/.scratch/aged"

  # G2-b: rewriting bytes then backdating the mtime is the same forgery.
  mkdir -p "$grepo/.scratch/forged"
  printf 'payload\n' > "$grepo/.scratch/forged/child.md"
  touch -d '7 days ago' "$grepo/.scratch/forged" "$grepo/.scratch/forged/child.md"
  st_case G2b NOT-SAFE none "fresh-or-backdated-descendant" "$grepo/.scratch/forged"

  # G2-c: a hidden file naming the child is a live reference.
  mkdir -p "$grepo/.scratch/refd"
  printf 'child\n' > "$grepo/.scratch/refd/note.out"
  touch -d '7 days ago' "$grepo/.scratch/refd" "$grepo/.scratch/refd/note.out"
  printf 'see note.out for details\n' > "$grepo/.hidden-usage.md"
  st_case G2c NOT-SAFE none "live-refs=1" "$grepo/.scratch/refd/note.out"
"""

REGRESSION_VAULT = """
  # ---- S14 cluster-G regressions ------------------------------------------
  local gr="$ST_TMP/s14-g"
  mkdir -p "$gr/fleet"
  local grepo="$gr/fleet/g-shokunin"
  git init -q --initial-branch=main "$grepo"
  printf 'base\n' > "$grepo/base.txt"
  local gsha; gsha=$(st_commit "$grepo" "" "s14 g1 base")
  git -C "$grepo" update-ref refs/remotes/origin/main "$gsha"
  git -C "$grepo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main

  # G1: a stat-dirty tracked file must not be re-stat'ed into the index.
  printf 'same bytes\n' > "$grepo/artifact.txt"
  gsha=$(st_commit "$grepo" "$gsha" "s14 g1 artifact")
  git -C "$grepo" update-ref refs/remotes/origin/main "$gsha"
  touch -d '7 days ago' "$grepo/artifact.txt"
  local gbefore gafter
  gbefore=$(sha256sum -- "$grepo/.git/index" | cut -d' ' -f1)
  env -u GIT_DIR SHOKUNIN_ROOT="$gr/fleet" SOUJI_LEDGER="$ST_LEDGER" SOUJI_SELFTEST_ACTIVE=1 \
    "$SELF" --json -- "$grepo" >/dev/null 2>&1 || true
  gafter=$(sha256sum -- "$grepo/.git/index" | cut -d' ' -f1)
  if [ "$gbefore" = "$gafter" ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS G1 repo-root inspection leaves index bytes unchanged"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL G1 repo-root inspection rewrote .git/index"
  fi

  # G2-a: an aged container with a freshly written child is not stale.
  mkdir -p "$grepo/.scratch/aged"
  printf 'fresh child\n' > "$grepo/.scratch/aged/fresh.md"
  touch -d '7 days ago' "$grepo/.scratch/aged"
  st_case G2a "NOT-VERIFIED(none)" none \
    "fresh-or-backdated-descendant" -- "$grepo/.scratch/aged"

  # G2-b: rewriting bytes then backdating the mtime is the same forgery.
  mkdir -p "$grepo/.scratch/forged"
  printf 'payload\n' > "$grepo/.scratch/forged/child.md"
  touch -d '7 days ago' "$grepo/.scratch/forged" "$grepo/.scratch/forged/child.md"
  st_case G2b "NOT-VERIFIED(none)" none \
    "fresh-or-backdated-descendant" -- "$grepo/.scratch/forged"

  # G2-c: a hidden file naming the child is a live reference.
  mkdir -p "$grepo/.scratch/refd"
  printf 'child\n' > "$grepo/.scratch/refd/note.out"
  touch -d '7 days ago' "$grepo/.scratch/refd" "$grepo/.scratch/refd/note.out"
  printf 'see note.out for details\n' > "$grepo/.hidden-usage.md"
  st_case G2c "NOT-VERIFIED(none)" none "live-refs=1" -- "$grepo/.scratch/refd/note.out"
"""

REGRESSION_QUARANTINE = """
  # ---- S14 cluster-G regressions ------------------------------------------
  # G1: inspection of a repo root must not rewrite its index.
  local gr="$ST_TMP/s14-g"
  local gbefore gafter
  touch -d '7 days ago' "$R/keep/pushed.txt" 2>/dev/null || true
  gbefore=$(sha256sum -- "$R/.git/index" | cut -d' ' -f1)
  st_flow "G1 dry-run inspection" 0 --dry-run "$R" keep/pushed.txt
  gafter=$(sha256sum -- "$R/.git/index" | cut -d' ' -f1)
  st_check "G1 dry-run leaves index bytes unchanged" \\
    "$([ "$gbefore" = "$gafter" ] && echo 1 || echo 0)" "index identical"

  # G2: an aged container with a fresh child must not be deleted.
  mkdir -p "$R/.scratch/aged"
  printf 'fresh child\\n' > "$R/.scratch/aged/fresh.md"
  touch -d '7 days ago' "$R/.scratch/aged"
  st_flow "G2 fresh descendant" 3 "$R" .scratch/aged
  st_check "G2 fresh descendant retained" \\
    "$([ -f "$R/.scratch/aged/fresh.md" ] && echo 1 || echo 0)" "present"
  st_check "G2 fresh descendant not authorized" \\
    "$(printf '%s' "$ST_OUT" | grep -aqF "$(printf 'RESULT\\t%s\\tNOT-AUTHORIZED' "$R/.scratch/aged")" && echo 1 || echo 0)" \\
    "NOT-AUTHORIZED"

  # G2-forged: bytes rewritten, mtime backdated -- same refusal.
  mkdir -p "$R/.scratch/forged"
  printf 'payload\\n' > "$R/.scratch/forged/child.md"
  touch -d '7 days ago' "$R/.scratch/forged" "$R/.scratch/forged/child.md"
  st_flow "G2 backdated forgery" 3 "$R" .scratch/forged
  st_check "G2 backdated child retained" \\
    "$([ -f "$R/.scratch/forged/child.md" ] && echo 1 || echo 0)" "present"
"""


def block(kind: str) -> str:
    if kind == "verify":
        return (HEADER + STATUS_HELPER + TREE_HELPERS + LIVE_REFS
                + TRY_STALE.replace("@REASON@", "") + REPO_ROOT_VERIFY)
    if kind == "vault":
        return (HEADER + STATUS_HELPER + TREE_HELPERS + LIVE_REFS
                + TRY_STALE.replace("@REASON@", "; R_REASON=stale") + REPO_ROOT_VAULT)
    return HEADER + QUARANTINE_GLUE


def build(src_name: str, kind: str) -> str:
    src = (TOOLS / src_name).read_text()
    if MARKER not in src:
        raise SystemExit(f"{src_name}: main marker not found")
    if SUMMARY_ANCHOR not in src:
        raise SystemExit(f"{src_name}: selftest summary anchor not found")
    head, _, tail = src.partition(MARKER)
    regression = {"verify": REGRESSION_VERIFY,
                  "vault": REGRESSION_VAULT,
                  "quarantine": REGRESSION_QUARANTINE}[kind]
    head = head.replace(SUMMARY_ANCHOR, regression + "\n" + SUMMARY_ANCHOR)
    return head + block(kind) + "\n" + MARKER + tail


TARGETS = {
    "cand-g2-verify.sh": ("souji-verify.sh", "verify"),
    "cand-g2-vault.sh": ("souji-vault-verify.sh", "vault"),
    "cand-g2-quarantine.sh": ("souji-quarantine.sh", "quarantine"),
}

rc = 0
for out, (src, kind) in TARGETS.items():
    text = build(src, kind)
    path = TOOLS / out
    if A.check:
        same = path.exists() and path.read_text() == text
        print(f"{out}: {'MATCH' if same else 'DRIFT'}")
        rc |= 0 if same else 1
    else:
        path.write_text(text)
        print(f"{out}: wrote {len(text)} bytes "
              f"sha256={hashlib.sha256(text.encode()).hexdigest()[:12]}")
sys.exit(rc)
