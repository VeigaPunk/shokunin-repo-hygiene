#!/bin/bash
# #2: no shell expansion of include values; %(prefix) and ~user diverge from git's own expansion.
. "$(dirname "$0")/probe-common.sh"; prep; D=$(mkfix); rm -f "$H/EXPANDED"
printf '[core]\n\trepositoryformatversion = 0\n[include]\n\tpath = "$(touch %s/EXPANDED)"\n[include]\n\tpath = "`touch %s/EXPANDED`"\n[include]\n\tpath = "./*"\n' "$H" "$H" > "$D/.git/config"
PATH="$H/bin:$PATH" T=20 rungate 2>&1 | grep -E 'gitsource'
[[ -e $H/EXPANDED ]] && echo "SHELL-EXEC" || echo "no shell expansion (EXPANDED absent)"
echo "glob ./* expanded to .git/x*? $(ls "$D/.git" | grep -c '^x') files; scan opened none"
for v in '%(prefix)/share/git-core/templates/description' '~root/nonexistent.cfg'; do
  printf '[core]\n\trepositoryformatversion = 0\n[include]\n\tpath = %s\n' "$v" > "$D/.git/config"
  echo "value $v"
  echo "  gate resolves: $(git config --no-includes --file "$D/.git/config" --get include.path) (dir-relative, unchecked)"
  echo "  git resolves:  $(git --no-optional-locks -C "$D" rev-parse --show-toplevel 2>&1 | head -1)"
done
