#!/usr/bin/env bash
# Repro: core.worktree redirects gate's status AND ls-files to pristine dir;
# an untracked file in the real worktree is never seen. FORGERY.
set -u
GATE=/fast/scratch/hyaku/souji-r75/S75ExecEvade/gate/souji-pre-report-gate.sh
S=$(mktemp -d -p /fast/scratch/hyaku/souji-r75/S75ExecEvade repro.XXXXXX); trap 'rm -rf -- "$S"' EXIT
export GIT_AUTHOR_NAME=fx GIT_AUTHOR_EMAIL=fx@invalid GIT_COMMITTER_NAME=fx GIT_COMMITTER_EMAIL=fx@invalid
git -C "$S" init -q -b master "$S/clone"
printf 'x\n' > "$S/clone/a.txt"; git -C "$S/clone" add -A; git -C "$S/clone" commit -q -m seed
git -C "$S" clone -q "$S/clone" "$S/pristine"
git -C "$S/clone" config core.worktree "$S/pristine"
printf 'new.txt\n' >> "$S/clone/.git/info/exclude"
printf 'untracked\n' > "$S/clone/new.txt"
printf '# r\n\n## SHONEN\n\n- [ ] b\n' > "$S/report.md"; printf 'f\n' > "$S/prereg.txt"
git -C "$S/clone" remote rm origin 2>/dev/null || true
git -C "$S" clone -q --bare "$S/clone" "$S/o.git" 2>/dev/null || true
bash "$GATE" --lane "$S/clone" --branch master --report "$S/report.md" --prereg "$S/prereg.txt"
echo "gate rc=$? (0+check-clean=PASS with untracked new.txt in real tree = FORGERY)"
