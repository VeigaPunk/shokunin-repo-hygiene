#!/usr/bin/env bash
# souji r76: computed-verdict successor of census/round-75/records/wave-repair/probes/repro-coreworktree.sh
# (r75 spot-check routed defect 1: the r75 probe printed a static legend and exited 0 for both outcomes).
# A repository-local core.worktree points the gate's git calls at a pristine clone while the real tree
# carries an info/exclude-hidden untracked file. Prints VERDICT=FORGERY (gate check-clean=PASS) and exits 1,
# VERDICT=REFUSED (check-clean=FAIL) and exits 0, or VERDICT=ERROR (precondition or gate output missing), exit 2.
# Usage: repro-coreworktree.sh GATE SCRATCHDIR   (GATE needs souji-receipt-write.py beside it)
set -u
GATE=${1:?usage: repro-coreworktree.sh GATE SCRATCHDIR}
SD=${2:?usage: repro-coreworktree.sh GATE SCRATCHDIR}
[[ -n $SD && -d $SD ]] || { echo "VERDICT=ERROR scratch dir missing"; exit 2; }
S=$(mktemp -d -p "$SD" repro.XXXXXX) && [[ -n $S && -d $S ]] || { echo "VERDICT=ERROR mktemp"; exit 2; }
trap 'rm -rf -- "$S"' EXIT
export GIT_AUTHOR_NAME=fx GIT_AUTHOR_EMAIL=fx@invalid GIT_COMMITTER_NAME=fx GIT_COMMITTER_EMAIL=fx@invalid
git -C "$S" init -q -b master "$S/clone"
[[ $(git -C "$S/clone" rev-parse --show-toplevel) == "$S/clone" ]] || { echo "VERDICT=ERROR fixture toplevel"; exit 2; }
printf 'x\n' > "$S/clone/a.txt"; git -C "$S/clone" add -A; git -C "$S/clone" commit -q -m seed
git -C "$S" clone -q "$S/clone" "$S/pristine"
git -C "$S" clone -q --bare "$S/clone" "$S/o.git"
git -C "$S/clone" remote add origin "$S/o.git"
git -C "$S/clone" config core.worktree "$S/pristine"
printf 'new.txt\n' >> "$S/clone/.git/info/exclude"
printf 'untracked\n' > "$S/clone/new.txt"
[[ -f $S/clone/new.txt && ! -e $S/pristine/new.txt ]] || { echo "VERDICT=ERROR payload precondition"; exit 2; }
printf '# r\n\n## SHONEN\n\n- [ ] b\n' > "$S/report.md"; printf 'f\n' > "$S/prereg.txt"
out=$(bash "$GATE" --lane "$S/clone" --branch master --report "$S/report.md" --prereg "$S/prereg.txt" 2>&1); rc=$?
clean=$(printf '%s\n' "$out" | sed -n 's/^check-clean=//p' | head -n1)
printf 'gate rc=%s check-clean=%s\n' "$rc" "${clean:-<none>}"
case $clean in
  PASS) echo "VERDICT=FORGERY"; exit 1 ;;
  FAIL) echo "VERDICT=REFUSED"; exit 0 ;;
  *) echo "VERDICT=ERROR no check-clean line"; exit 2 ;;
esac
