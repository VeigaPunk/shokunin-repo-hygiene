#!/usr/bin/env bash
# r32 C3 fixture — the abandoned object's own mtime clock (F1 frontier).
#
# Round 31 measured the keepers that outlive a dropped `refs/jj/keep` ref and named one keeper as
# sourced, not measured: any object whose own modification time is newer than git's prune date is
# kept "along with everything reachable from it" (git-gc.adoc), which is why an unreachable B can
# survive a default `git gc` with every ref and reflog entry gone. This fixture isolates that
# clock: five jj-colocated repositories under $TMPDIR, one per arm of the frozen contract, each
# built the same way — A, then B on A (and, for `mixed` and `nocruft`, a second abandoned commit C
# on A, never on B, so that a recent C cannot hold B through ancestry) — then:
#
#   abandon   `jj abandon` on each tracked commit;
#   drop      `git -C "$D" update-ref -d` on every keep ref whose target is a tracked commit or a
#             descendant of one (the wider deletion round 31's wave-2 correction found necessary);
#   expire    `git -C "$D" reflog expire --expire=now --expire-unreachable=now --all`.
#
# After that, B (and C) are unreachable from every git root, and their objects are loose; the
# fixture asserts both before it prints `step=start`. It then backdates the *old* commit's objects
# by `touch -d '30 days ago'` on the loose commit, tree and blob files, and runs the arm's git
# housekeeping. Nothing in the fixture predicts the outcome: every `where` and `object_present`
# field is read back from git after the step, so the record states what git did.
#
# Arms and steps (steps are from the frozen contract's enumerated set):
#   recent   start, gc-default                         B recent, `git gc` defaults
#   old      start, backdate, gc-default               B old, `git gc` defaults
#   mixed    start, backdate, gc-prune-never, gc-default
#            B old and C recent, `git gc --prune=never` (one cruft pack, per-object .mtimes), then
#            `git gc` defaults
#   never    start, backdate, gc-pruneexpire-never     B old, `git -c gc.pruneExpire=never gc`
#   nocruft  start, backdate, gc-cruft-disabled        B old, C recent, `git -c gc.cruftPacks=false gc`
#
# Prints, and nothing else on stdout:
#   jj-version: <jj --version>
#   git-version: <git --version>
#   RESULT arm=<recent|old|mixed|never|nocruft> step=<start|backdate|gc-prune-never|gc-default|gc-pruneexpire-never|gc-cruft-disabled> obj=<B|C> mtime=<recent|old> where=<loose|cruft|pack|absent> object_present=<yes|no>
#
#   mtime          the fixture's label for the object's own clock at that step: `recent` until the
#                  backdate step touches it, `old` from then on (C in `mixed`/`nocruft` stays
#                  recent: only B is backdated).
#   where          `absent` when `git cat-file -e` fails; else `loose` when the object file exists
#                  under objects/xx/; else `cruft` when the object is listed in a pack that has a
#                  `.mtimes` file beside it; else `pack`.
#   object_present the exit status of `git cat-file -e <commit>` (0 => yes).
#
# No commit id, path, timestamp or other per-run varying token reaches a RESULT line, so repeated
# runs print identical RESULT lines even though jj hashes the commit time into each commit id.
#
# Tool calls: `jj`, `git` and `touch` are always resolved through PATH by bare name (never an
# absolute binary path), so a PATH shim can log and forward or neuter them. Every git call names
# the repository with `git -C "$D"`, and every jj call names it with `-R "$D"`, except the single
# repo-creating `jj git init --colocate "$D"` at the start of each arm (`-R` needs a repo that does
# not exist yet; that call carries the destination as its own argument).
#
# Refuses (exit 2) when TMPDIR is unset or empty, is not a directory, or resolves inside the lane
# (/home/vgpnk/Projects/shokunin/souji-shokunin) or the fleet root (/home/vgpnk/Projects/shokunin),
# when jj, git or touch is not on PATH, and when mktemp's base lands in either root.
set -u

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

# --- refuse to run outside scratch -------------------------------------------------------------
[ -n "${TMPDIR:-}" ] || die "TMPDIR is unset or empty; refusing to run"
[ -d "${TMPDIR:-}" ] || die "TMPDIR=${TMPDIR:-} is not a directory; refusing to run"
case "$(cd "$TMPDIR" && pwd -P)" in
  /home/vgpnk/Projects/shokunin/souji-shokunin|/home/vgpnk/Projects/shokunin/souji-shokunin/*)
    die "TMPDIR=$TMPDIR is inside the lane; refusing to run" ;;
  /home/vgpnk/Projects/shokunin|/home/vgpnk/Projects/shokunin/*)
    die "TMPDIR=$TMPDIR is inside the fleet root; refusing to run" ;;
esac
command -v jj >/dev/null 2>&1 || die "jj is not on PATH"
command -v git >/dev/null 2>&1 || die "git is not on PATH"
command -v touch >/dev/null 2>&1 || die "touch is not on PATH"

printf 'jj-version: %s\n' "$(jj --version)"
printf 'git-version: %s\n' "$(git --version)"

BASE=$(mktemp -d "$TMPDIR/r32-jj-mtime-clock.XXXXXX") || die "mktemp failed under $TMPDIR"
case "$(cd "$BASE" && pwd -P)" in
  /home/vgpnk/Projects/shokunin/souji-shokunin|/home/vgpnk/Projects/shokunin/souji-shokunin/*|/home/vgpnk/Projects/shokunin|/home/vgpnk/Projects/shokunin/*)
    rm -rf "$BASE"; die "BASE=$BASE is inside the lane or the fleet root; refusing to run" ;;
esac
cleanup() { rm -rf "$BASE"; }
trap cleanup EXIT
trap 'exit 2' INT TERM

NAME=r32-mtime-clock
EMAIL=r32-mtime-clock@example.invalid
JJCFG=(--color=never --config ui.paginate=never --config "user.name=$NAME" --config "user.email=$EMAIL")

D=
ID_B=
ID_C=
MT_B=recent
MT_C=recent

JJ() { ( cd "$D" && jj -R "$D" "${JJCFG[@]}" "$@" ); }
G() { git -C "$D" -c maintenance.auto=false -c gc.auto=0 "$@"; }

loose_path() {
  local oid=$1 gd
  gd=$(G rev-parse --absolute-git-dir) || return 1
  printf '%s/objects/%s/%s' "$gd" "${oid:0:2}" "${oid:2}"
}

present() { if G cat-file -e "$1" 2>/dev/null; then printf 'yes'; else printf 'no'; fi; }

where() {
  local oid=$1 p i mode=''
  G cat-file -e "$oid" 2>/dev/null || { printf 'absent'; return; }
  p=$(loose_path "$oid") || { printf 'absent'; return; }
  if [ -f "$p" ]; then printf 'loose'; return; fi
  for i in "$(G rev-parse --absolute-git-dir)"/objects/pack/*.idx; do
    [ -e "$i" ] || continue
    if G verify-pack -v "$i" 2>/dev/null | grep -q "^$oid "; then
      if [ -f "${i%.idx}.mtimes" ]; then printf 'cruft'; return; else mode=pack; fi
    fi
  done
  if [ -n "$mode" ]; then printf 'pack'; return; fi
  printf 'absent'
}

emit() { # $1 = arm, $2 = step, $3 = obj
  local arm=$1 step=$2 obj=$3 oid mt
  case "$obj" in
    B) oid=$ID_B; mt=$MT_B ;;
    C) oid=$ID_C; mt=$MT_C ;;
    *) die "emit: unknown obj $obj" ;;
  esac
  printf 'RESULT arm=%s step=%s obj=%s mtime=%s where=%s object_present=%s\n' \
    "$arm" "$step" "$obj" "$mt" "$(where "$oid")" "$(present "$oid")"
}

arm_begin() { # $1 = path
  D=$1
  ID_B=; ID_C=; MT_B=recent; MT_C=recent
  mkdir -p "$D" || die "mkdir $D failed"
  jj "${JJCFG[@]}" git init --colocate "$D" >/dev/null 2>&1 \
    || die "jj git init --colocate failed in $D"
}

assert_oid() { # $1 = id, $2 = label
  case "$1" in
    ????????????????????????????????????????) : ;;
    *) die "could not read $2's commit id (got '$1')" ;;
  esac
}

make_A() {
  printf 'a\n' >"$D/a.txt"
  JJ commit -m A a.txt >/dev/null 2>&1 || die "$D: commit A failed"
}

make_B() {
  printf 'b\n' >"$D/b.txt"
  JJ commit -m B b.txt >/dev/null 2>&1 || die "$D: commit B failed"
  ID_B=$(JJ log --no-graph -r '@-' -T 'commit_id') || die "$D: jj log failed"
  assert_oid "$ID_B" B
}

make_C() {
  printf 'c\n' >"$D/c.txt"
  JJ commit -m C c.txt >/dev/null 2>&1 || die "$D: commit C failed"
  ID_C=$(JJ log --no-graph -r '@-' -T 'commit_id') || die "$D: jj log failed"
  assert_oid "$ID_C" C
}

abandon_wc() {
  JJ abandon '@-' >/dev/null 2>&1 || die "$D: jj abandon '@-' failed"
}

# Keep refs whose target is one of the given ids or a descendant of one.
drop_keep_refs() {
  local r o id
  for r in $(G for-each-ref --format='%(refname)' 'refs/jj/keep/*'); do
    o=$(G rev-parse "$r") || continue
    for id in "$@"; do
      if [ "$o" = "$id" ] || G merge-base --is-ancestor "$id" "$o" 2>/dev/null; then
        G update-ref -d "$r" || die "$D: git update-ref -d $r failed"
        break
      fi
    done
  done
}

assert_unreachable() {
  local id c reach
  reach=$(G rev-list --all --reflog 2>/dev/null) || die "$D: git rev-list --all --reflog failed"
  for id in "$@"; do
    for c in $(island_commits "$id"); do
      if printf '%s\n' "$reach" | grep -qx "$c"; then
        die "$D: a ref or reflog still reaches $c after the drop and expire"
      fi
    done
  done
}

seal() { # drop keep refs naming the given ids or descendants, expire every reflog, assert roots
  drop_keep_refs "$@"
  G reflog expire --expire=now --expire-unreachable=now --all >/dev/null 2>&1 \
    || die "$D: git reflog expire failed"
  assert_unreachable "$@"
}

# Every commit object in the repository (loose or packed).
all_commits() {
  G cat-file --batch-all-objects --batch-check='%(objectname) %(objecttype)' \
    | awk '$2 == "commit" {print $1}'
}

# The unreachable commits that have this commit as an ancestor: the abandoned commit itself plus
# the rewritten working-copy commits jj left behind when it rebased descendants onto B's parents.
# A recent member of this island would hold B through reachability no matter what B's own clock
# says (r31's descendant keeper), so the old arm backdates the whole island.
island_commits() { # $1 = commit id
  local c
  for c in $(all_commits); do
    if G merge-base --is-ancestor "$1" "$c" 2>/dev/null; then printf '%s\n' "$c"; fi
  done
}

# Touch the loose object files git considers this commit's own new objects (commit, tree, blob).
backdate_commit() { # $1 = commit id
  local oid=$1 obj p
  for obj in $(G rev-list --objects "$oid" --not "$oid^" | awk '{print $1}'); do
    p=$(loose_path "$obj") || die "$D: cannot resolve the object path for $obj"
    [ -f "$p" ] || die "$D: object $obj is not loose at start (looked for $p)"
    touch -d '30 days ago' "$p" || die "$D: touch -d failed on $p"
  done
}

backdate_island() { # $1 = abandoned commit id
  local c
  for c in $(island_commits "$1"); do
    backdate_commit "$c"
  done
}

# --- arm recent: B recent, `git gc` defaults ---------------------------------------------------
arm_begin "$BASE/recent"
make_A
make_B
abandon_wc
seal "$ID_B"
emit recent start B
G gc >/dev/null 2>&1 || die "recent: git gc failed"
emit recent gc-default B

# --- arm old: B old, `git gc` defaults ---------------------------------------------------------
arm_begin "$BASE/old"
make_A
make_B
abandon_wc
seal "$ID_B"
emit old start B
backdate_island "$ID_B"
MT_B=old
emit old backdate B
G gc >/dev/null 2>&1 || die "old: git gc failed"
emit old gc-default B

# --- arm mixed: B old, C recent, `git gc --prune=never`, then `git gc` defaults -----------------
arm_begin "$BASE/mixed"
make_A
make_B
abandon_wc
make_C
abandon_wc
seal "$ID_B" "$ID_C"
emit mixed start B
emit mixed start C
backdate_island "$ID_B"
MT_B=old
emit mixed backdate B
emit mixed backdate C
G gc --prune=never >/dev/null 2>&1 || die "mixed: git gc --prune=never failed"
emit mixed gc-prune-never B
emit mixed gc-prune-never C
G gc >/dev/null 2>&1 || die "mixed: git gc failed"
emit mixed gc-default B
emit mixed gc-default C

# --- arm never: B old, `git -c gc.pruneExpire=never gc` ----------------------------------------
arm_begin "$BASE/never"
make_A
make_B
abandon_wc
seal "$ID_B"
emit never start B
backdate_island "$ID_B"
MT_B=old
emit never backdate B
G -c gc.pruneExpire=never gc >/dev/null 2>&1 || die "never: git gc failed"
emit never gc-pruneexpire-never B

# --- arm nocruft: B old, C recent, `git -c gc.cruftPacks=false gc` -----------------------------
arm_begin "$BASE/nocruft"
make_A
make_B
abandon_wc
make_C
abandon_wc
seal "$ID_B" "$ID_C"
emit nocruft start B
emit nocruft start C
backdate_island "$ID_B"
MT_B=old
emit nocruft backdate B
emit nocruft backdate C
G -c gc.cruftPacks=false gc >/dev/null 2>&1 || die "nocruft: git gc failed"
emit nocruft gc-cruft-disabled B
emit nocruft gc-cruft-disabled C

exit 0
