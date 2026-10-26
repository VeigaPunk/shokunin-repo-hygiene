#!/usr/bin/env bash
# r31 C3 fixture — object lifetime behind a dropped `refs/jj/keep` ref.
#
# Round 30 measured when a keep ref goes and left object removal unmeasured ("Ref removal is
# measured; object removal is not"). This fixture asks the next question: once the keep ref that
# names the abandoned commit B is gone, what still keeps B's object in the git store, and what
# finally removes it? Three jj-colocated repositories under $TMPDIR, each its own arm:
#
#   solo        A, then B on A; B abandoned; nothing was placed on top of B by hand.
#   descendant  A, B on A, C on B; B abandoned, C left alive through the assigned steps.
#   reflog-only control: A, then B on A; B abandoned, then every keep ref naming B or a descendant
#               of B is deleted, so only the HEAD reflog entry jj wrote still names B.
#
# Why the descendant arm abandons B only, and abandons C in its own final step: steps 1-4 exist to
# test whether a *surviving descendant keep ref* holds B. Abandoning C up front would drop the
# descendant's keep ref and delete the variable under test; C is therefore abandoned only in the
# last step, where its removal is what lets B go.
#
# Why a third repository: the assigned order expires every reflog entry naming B at step 4, before
# any descendant keep ref is dropped, so no ordering of the assigned steps can show whether a
# reflog entry on its own holds the object. The control drops the refs first and keeps the reflog.
#
# Steps. The four assigned steps run first in `solo` and `descendant`, each followed by a cat-file
# check of B:
#   abandon                   `jj abandon <B>`
#   pack-and-util-gc          `git pack-refs --all`, then `jj util gc --expire=now`
#   git-gc-prune-now          `git gc --prune=now`
#   reflog-expire-then-prune  `git reflog expire --expire=now --expire-unreachable=now --all`,
#                             then `git gc --prune=now`
# Those four never remove B in either arm, so further steps find what does:
#   op-abandon-and-util-gc    `jj op abandon ..@-`, then `jj util gc --expire=now`
# and then:
#   solo       delete-descendant-keep-refs-and-prune
#              `git update-ref -d` on every keep ref that names a descendant of B, then
#              `git gc --prune=now` — the refs jj recreates and no jj command removes.
#   descendant abandon-descendant-and-op-abandon-and-util-gc
#              `jj abandon <C>`, `jj op abandon ..@-`, `jj util gc --expire=now`, then
#              `git gc --prune=now` as `git-gc-prune-now-again`.
#   reflog-only abandon, drop-keep-refs-naming-target, git-gc-prune-now,
#              reflog-expire-then-prune
#
# Prints, and nothing else:
#   jj-version: <jj --version>
#   git-version: <git --version>
#   RESULT arm=<solo|descendant|reflog-only> step=<step> keep_refs=<n> target_keep=<yes|no> \
#          reflog_hits=<n> object_present=<yes|no>
#
# keep_refs      count of `refs/jj/keep/*` (git for-each-ref).
# target_keep    whether any keep ref's name still contains B's commit id.
# reflog_hits    count of `git reflog --all` entries whose commit (%H) is B.
# object_present `git cat-file -e <B>` (exit 0 => yes).
#
# No commit id, reflog date or other per-run varying token reaches a RESULT line, so repeated runs
# print identical RESULT lines even though jj commit ids hash the commit time.
#
# Tool calls: `jj` and `git` are always resolved through PATH by bare name (never an absolute
# binary path), so a PATH shim can log and forward them. Every jj call names the repository with
# `-R "$D"` and carries a throwaway identity through `--config`; every git call names it with
# `git -C "$D"`.
set -u

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

# --- refuse to run outside scratch -------------------------------------------------------------
[ -n "${TMPDIR:-}" ] || die "TMPDIR is unset or empty; refusing to run"
[ -d "${TMPDIR}" ] || die "TMPDIR=$TMPDIR is not a directory; refusing to run"
case "$(cd "$TMPDIR" && pwd -P)" in
  /home/vgpnk/Projects/shokunin|/home/vgpnk/Projects/shokunin/*)
    die "TMPDIR=$TMPDIR is inside the fleet root; refusing to run" ;;
esac
command -v jj >/dev/null 2>&1 || die "jj is not on PATH"
command -v git >/dev/null 2>&1 || die "git is not on PATH"

printf 'jj-version: %s\n' "$(jj --version)"
printf 'git-version: %s\n' "$(git --version)"

BASE=$(mktemp -d "$TMPDIR/r31-jj-object-clock.XXXXXX") || die "mktemp failed under $TMPDIR"
case "$(cd "$BASE" && pwd -P)" in
  /home/vgpnk/Projects/shokunin|/home/vgpnk/Projects/shokunin/*)
    rm -rf "$BASE"; die "BASE=$BASE is inside the fleet root; refusing to run" ;;
esac
cleanup() { rm -rf "$BASE"; }
trap cleanup EXIT
trap 'exit 2' INT TERM

NAME=r31-object-clock
EMAIL=r31-object-clock@example.invalid
JJCFG=(--color=never --config ui.paginate=never --config "user.name=$NAME" --config "user.email=$EMAIL")

D=
TARGET=
JJ() { ( cd "$D" && jj -R "$D" "${JJCFG[@]}" "$@" ); }
G() { git -C "$D" -c maintenance.auto=false -c gc.auto=0 "$@"; }

keep_count() { G for-each-ref --format='%(refname)' 'refs/jj/keep/*' | wc -l | tr -d ' '; }
target_keep() {
  if [ -n "$TARGET" ] && G for-each-ref --format='%(refname)' 'refs/jj/keep/*' | grep -q -F -- "$TARGET"; then
    printf 'yes'
  else
    printf 'no'
  fi
}
reflog_hits() {
  local n
  n=$(G reflog --all --format='%H' 2>/dev/null | grep -c -x -F -- "$TARGET" || true)
  printf '%s' "${n:-0}"
}
present() { if G cat-file -e "$TARGET" 2>/dev/null; then printf 'yes'; else printf 'no'; fi; }
result() {
  printf 'RESULT arm=%s step=%s keep_refs=%s target_keep=%s reflog_hits=%s object_present=%s\n' \
    "$1" "$2" "$(keep_count)" "$(target_keep)" "$(reflog_hits)" "$(present)"
}

# Keep refs whose target is a strict descendant of B (B itself excluded).
desc_keep_refs() {
  local r o out=''
  for r in $(G for-each-ref --format='%(refname)' 'refs/jj/keep/*'); do
    o=$(G rev-parse "$r") || continue
    [ "$o" = "$TARGET" ] && continue
    if G merge-base --is-ancestor "$TARGET" "$o" 2>/dev/null; then out="$out $r"; fi
  done
  printf '%s' "${out# }"
}

# Keep refs whose target is B or a descendant of B.
target_or_desc_keep_refs() {
  local r o out=''
  for r in $(G for-each-ref --format='%(refname)' 'refs/jj/keep/*'); do
    o=$(G rev-parse "$r") || continue
    if [ "$o" = "$TARGET" ] || G merge-base --is-ancestor "$TARGET" "$o" 2>/dev/null; then
      out="$out $r"
    fi
  done
  printf '%s' "${out# }"
}

init_repo() { # $1 = path
  D=$1
  mkdir -p "$D" || die "mkdir $D failed"
  # The only jj call without -R: `-R` needs an existing jj repo, and this call creates it. It
  # still carries the throwaway identity, and it names the repository as its own argument.
  jj "${JJCFG[@]}" git init --colocate "$D" >/dev/null 2>&1 \
    || die "jj git init --colocate failed in $D"
}

# The four assigned steps plus the shared op-abandon step, used by the solo and descendant arms.
assigned_steps() { # $1 = arm
  local arm=$1
  result "$arm" abandon
  G pack-refs --all >/dev/null 2>&1
  JJ util gc --expire=now >/dev/null 2>&1 || die "$arm: jj util gc --expire=now failed"
  result "$arm" pack-and-util-gc
  G gc --prune=now >/dev/null 2>&1
  result "$arm" git-gc-prune-now
  G reflog expire --expire=now --expire-unreachable=now --all >/dev/null 2>&1
  G gc --prune=now >/dev/null 2>&1
  result "$arm" reflog-expire-then-prune
  JJ op abandon '..@-' >/dev/null 2>&1 || die "$arm: jj op abandon ..@- failed"
  JJ util gc --expire=now >/dev/null 2>&1 || die "$arm: jj util gc --expire=now (after op abandon) failed"
  result "$arm" op-abandon-and-util-gc
}

# --- arm solo: A, B on A; abandon B; nothing was placed on top of B by hand --------------------
init_repo "$BASE/solo"
printf 'a\n' >"$D/a.txt"
JJ commit -m A a.txt >/dev/null 2>&1 || die "solo: commit A failed"
printf 'b\n' >"$D/b.txt"
JJ commit -m B b.txt >/dev/null 2>&1 || die "solo: commit B failed"
TARGET=$(JJ log --no-graph -r '@-' -T 'commit_id') || die "solo: jj log failed"
case "$TARGET" in
  ????????????????????????????????????????) : ;;
  *) die "solo: could not read B's commit id (got '$TARGET')" ;;
esac
JJ abandon '@-' >/dev/null 2>&1 || die "solo: jj abandon failed"
assigned_steps solo
# `jj abandon` rewrote the working-copy commit that sat on B, and the pre-rewrite commit keeps a
# keep ref that survives both `jj op abandon` and `jj util gc` (`jj abandon` on it reports it is
# already hidden). Deleting those refs directly is the only lever left.
for r in $(desc_keep_refs); do G update-ref -d "$r" || die "solo: git update-ref -d $r failed"; done
G gc --prune=now >/dev/null 2>&1
result solo delete-descendant-keep-refs-and-prune

# --- arm descendant: A, B on A, C on B; abandon B only, C alive through the assigned steps -----
init_repo "$BASE/descendant"
printf 'a\n' >"$D/a.txt"
JJ commit -m A a.txt >/dev/null 2>&1 || die "descendant: commit A failed"
printf 'b\n' >"$D/b.txt"
JJ commit -m B b.txt >/dev/null 2>&1 || die "descendant: commit B failed"
printf 'c\n' >"$D/c.txt"
JJ commit -m C c.txt >/dev/null 2>&1 || die "descendant: commit C failed"
TARGET=$(JJ log --no-graph -r '@--' -T 'commit_id') || die "descendant: jj log failed"
case "$TARGET" in
  ????????????????????????????????????????) : ;;
  *) die "descendant: could not read B's commit id (got '$TARGET')" ;;
esac
JJ abandon '@--' >/dev/null 2>&1 || die "descendant: jj abandon failed"
assigned_steps descendant
# C is the live descendant that held B through every assigned step; abandoning it and dropping the
# operation views releases B, with no direct ref surgery.
JJ abandon '@-' >/dev/null 2>&1 || die "descendant: jj abandon (C) failed"
JJ op abandon '..@-' >/dev/null 2>&1 || die "descendant: jj op abandon ..@- (after C) failed"
JJ util gc --expire=now >/dev/null 2>&1 || die "descendant: jj util gc --expire=now (after C) failed"
result descendant abandon-descendant-and-op-abandon-and-util-gc
G gc --prune=now >/dev/null 2>&1
result descendant git-gc-prune-now-again

# --- arm reflog-only: control for the keeper question -------------------------------------------
# The assigned four-step order expires the reflog before any descendant keep ref is dropped, so
# neither assigned arm can say whether a reflog entry on its own keeps the object. This control
# repo drops every keep ref that names B or a descendant of B first, which leaves the HEAD reflog
# entry jj wrote when B became the working-copy parent as the only thing naming B, and then runs
# the two git actions.
init_repo "$BASE/reflog-only"
printf 'a\n' >"$D/a.txt"
JJ commit -m A a.txt >/dev/null 2>&1 || die "reflog-only: commit A failed"
printf 'b\n' >"$D/b.txt"
JJ commit -m B b.txt >/dev/null 2>&1 || die "reflog-only: commit B failed"
TARGET=$(JJ log --no-graph -r '@-' -T 'commit_id') || die "reflog-only: jj log failed"
case "$TARGET" in
  ????????????????????????????????????????) : ;;
  *) die "reflog-only: could not read B's commit id (got '$TARGET')" ;;
esac
JJ abandon '@-' >/dev/null 2>&1 || die "reflog-only: jj abandon failed"
result reflog-only abandon
for r in $(target_or_desc_keep_refs); do
  G update-ref -d "$r" || die "reflog-only: git update-ref -d $r failed"
done
result reflog-only drop-keep-refs-naming-target
G gc --prune=now >/dev/null 2>&1
result reflog-only git-gc-prune-now
G reflog expire --expire=now --expire-unreachable=now --all >/dev/null 2>&1
G gc --prune=now >/dev/null 2>&1
result reflog-only reflog-expire-then-prune

exit 0
