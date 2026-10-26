#!/usr/bin/env bash
# r30 C3 fixture — when does a `refs/jj/keep/*` ref go away, and when does the commit behind it
# stop being an object in the git store?
#
# Builds jj-colocated repositories ONLY under $TMPDIR, never in a lane or fleet repo, and prints:
#   jj-version: <jj --version>
#   git-version: <git --version>
#   RESULT step=<name> keep_refs=<count of refs/jj/keep/*> object_present=<yes|no> <note>
#
# keep_refs counts `git for-each-ref --format=%(refname) refs/jj/keep/*`.
# object_present is `git cat-file -e <tracked commit id>` (exit 0 => yes).
# <note> carries `target_keep=yes|no` — whether a keep ref names the tracked (abandoned) commit — so
# "the ref went" and "the object went" are readable apart.
#
# Steps 1-5 are the assigned sequence. Step 6 is the assigned "expire in the future" control; jj 0.45.1
# accepts only the literal `now` for --expire (`Error: --expire only accepts 'now'`,
# cli/src/commands/util/gc.rs@v0.45.1:55-57), so a future timestamp cannot be expressed. The control is
# therefore measured as (a) the rejection itself and (b) the real "not yet expired" arm: the default
# 14-day threshold on a second repository (step 7), followed by --expire=now on the same repository
# (step 8) to show the threshold is the lever.
#
# No timestamps and no commit ids are printed, so two runs on the same machine are byte-identical
# (commit ids differ between runs because jj commit ids hash the commit time).
set -u

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

# --- refuse to run outside scratch -------------------------------------------------------------
[ -n "${TMPDIR:-}" ] || die "TMPDIR is unset or empty; refusing to run"
[ -d "${TMPDIR}" ] || die "TMPDIR=$TMPDIR is not a directory; refusing to run"
case "$(cd "$TMPDIR" && pwd -P)" in
  /home/vgpnk/Projects/shokunin/souji-shokunin | /home/vgpnk/Projects/shokunin/souji-shokunin/*)
    die "TMPDIR=$TMPDIR resolves inside the souji lane (/home/vgpnk/Projects/shokunin/souji-shokunin); refusing to run" ;;
  /home/vgpnk/Projects/shokunin | /home/vgpnk/Projects/shokunin/*)
    die "TMPDIR=$TMPDIR resolves inside /home/vgpnk/Projects/shokunin; refusing to run" ;;
esac
command -v jj >/dev/null 2>&1 || die "jj is not on PATH"
command -v git >/dev/null 2>&1 || die "git is not on PATH"

printf 'jj-version: %s\n' "$(jj --version)"
printf 'git-version: %s\n' "$(git --version)"

BASE=$(mktemp -d "$TMPDIR/r30-jj-keep-expiry.XXXXXX") || die "mktemp failed under $TMPDIR"
case "$(cd "$BASE" && pwd -P)" in
  /home/vgpnk/Projects/shokunin | /home/vgpnk/Projects/shokunin/*)
    rm -rf "$BASE"; die "created dir $BASE resolves inside /home/vgpnk/Projects/shokunin" ;;
esac
cleanup() { rm -rf "$BASE"; }
trap cleanup EXIT
trap 'exit 2' INT TERM

NAME=r30-expiry
EMAIL=r30-expiry@example.invalid
JJCFG=(--color=never --config ui.paginate=never --config "user.name=$NAME" --config "user.email=$EMAIL")

# D is set per repository; JJ always names it with -R, G always with -C. jj resolves pathspecs
# against the process cwd, not -R, so JJ also runs its child in D.
JJ() { ( cd "$D" && jj -R "$D" "${JJCFG[@]}" "$@" ); }
G() { git -C "$D" -c maintenance.auto=false -c gc.auto=0 "$@"; }

keep_count() { G for-each-ref --format='%(refname)' 'refs/jj/keep/*' | wc -l | tr -d ' '; }
target_keep() { # whether a keep ref names the tracked commit
  if G for-each-ref --format='%(refname)' 'refs/jj/keep/*' | grep -q -- "$TARGET"; then printf 'yes'; else printf 'no'; fi
}
present() { if G cat-file -e "$TARGET" 2>/dev/null; then printf 'yes'; else printf 'no'; fi; }
result() { printf 'RESULT step=%s keep_refs=%s object_present=%s note=target_keep=%s %s\n' \
  "$1" "$(keep_count)" "$(present)" "$(target_keep)" "${2:-}"; }

# --- repository 1: assigned sequence -----------------------------------------------------------
MAIN=$BASE/main
mkdir -p "$MAIN"
D=$MAIN
# `jj git init` cannot take -R (the repo does not exist yet); every later call names the repo with -R.
jj "${JJCFG[@]}" git init --colocate "$MAIN" >/dev/null 2>&1 || die "jj git init --colocate failed in $MAIN"

printf 'a\n' >"$D/a.txt"
JJ commit -m A a.txt >/dev/null 2>&1 || die "commit A failed"
printf 'b\n' >"$D/b.txt"
JJ commit -m B b.txt >/dev/null 2>&1 || die "commit B failed"
TARGET=$(JJ log --no-graph -r '@-' -T 'commit_id')
[ -n "$TARGET" ] || die "could not read commit B's id"
result 1-commit-A-B "commits=2"

JJ abandon '@-' >/dev/null 2>&1 || die "jj abandon failed"
result 2-abandon-B "abandoned=B"

G gc --prune=now >/dev/null 2>&1
result 3-git-gc-prune-now "cmd=git-gc-prune-now"

JJ util gc --expire=now >/dev/null 2>&1 || die "jj util gc --expire=now failed"
result 4-util-gc-expire-now "cmd=jj-util-gc-expire-now"

# The operations that can reference B are the operations before the one this command runs in; the
# 0.45.1 help documents the range form `..<operation ID>` (operation and all its ancestors).
OPS_REF=$(JJ op log --no-graph -T 'id ++ " " ++ description.first_line() ++ "\n"' | grep -c -F -- "$TARGET")
JJ op abandon '..@-' >/dev/null 2>&1 || die "jj op abandon '..@-' failed"
JJ util gc --expire=now >/dev/null 2>&1 || die "jj util gc --expire=now (after op abandon) failed"
result 5-op-abandon-util-gc-expire-now "op_range=..@- ops_naming_target=$OPS_REF"

# --- repository 2: controls --------------------------------------------------------------------
CTRL=$BASE/control
mkdir -p "$CTRL"
D=$CTRL
jj "${JJCFG[@]}" git init --colocate "$CTRL" >/dev/null 2>&1 || die "jj git init --colocate failed in $CTRL"

printf 'c\n' >"$D/c.txt"
JJ commit -m C c.txt >/dev/null 2>&1 || die "commit C failed"
printf 'd\n' >"$D/d.txt"
JJ commit -m D d.txt >/dev/null 2>&1 || die "commit D failed"
TARGET=$(JJ log --no-graph -r '@-' -T 'commit_id')
[ -n "$TARGET" ] || die "could not read commit D's id"
JJ abandon '@-' >/dev/null 2>&1 || die "jj abandon (control) failed"

FUTURE_RC=0
FUTURE_OUT=$(JJ util gc --expire=tomorrow 2>&1) || FUTURE_RC=$?
case "$FUTURE_OUT" in
  *"only accepts"*) FUTURE_CLASS=rejected ;;
  *) FUTURE_CLASS=accepted ;;
esac
result 6-future-expire-control "expire=tomorrow rc=$FUTURE_RC $FUTURE_CLASS"

JJ util gc >/dev/null 2>&1 || die "jj util gc (default threshold) failed"
result 7-default-expire-control "cmd=jj-util-gc-default-2weeks"

JJ util gc --expire=now >/dev/null 2>&1 || die "jj util gc --expire=now (control) failed"
result 8-control-expire-now "cmd=jj-util-gc-expire-now"

