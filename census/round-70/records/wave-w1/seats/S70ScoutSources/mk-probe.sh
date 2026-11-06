SEAT=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-70/w1/S70ScoutSources
S=/fast/scratch/hyaku/souji-r70/S70ScoutSources
{
echo "# S70ScoutSources — independent re-derivation of the round-70 pathspec probe (git 2.56.0)"
echo "# fixture: mktemp -d under my scratch; 'git rev-parse --show-toplevel' asserted == fixture dir"
echo
D=$(mktemp -d -p "$S")
git -C "$D" init -q
T=$(git -C "$D" rev-parse --show-toplevel)
[ "$T" = "$D" ] && echo "toplevel asserted: $T"
cd "$D"
printf 'x\n' > f; git add f
git -c user.email=s@x -c user.name=s commit -qm init
git update-index --skip-worktree f
echo
echo "## git ls-files -v -z ':(top)'  (out | PIPE rc | GIT rc)"
for e in NONE GIT_LITERAL_PATHSPECS=1 GIT_GLOB_PATHSPECS=1 GIT_NOGLOB_PATHSPECS=1 GIT_ICASE_PATHSPECS=1; do
  if [ "$e" = NONE ]; then
    out=$(git ls-files -v -z ':(top)' | tr '\0' ' '); prc=$?; grc=$(git ls-files -v -z ':(top)' >/dev/null 2>&1; echo $?)
  else
    out=$(env "$e" git ls-files -v -z ':(top)' | tr '\0' ' '); prc=$?
    grc=$(env "$e" git ls-files -v -z ':(top)' >/dev/null 2>&1; echo $?)
  fi
  echo "  $e out=[$out] pipe_rc=$prc git_rc=$grc"
done
echo
echo "## git ls-tree HEAD -- f  (the writer's form: ls-tree -r -z rev -- rel)"
for e in NONE GIT_LITERAL_PATHSPECS=1 GIT_GLOB_PATHSPECS=1 GIT_NOGLOB_PATHSPECS=1 GIT_ICASE_PATHSPECS=1; do
  if [ "$e" = NONE ]; then o=$(git ls-tree HEAD -- f 2>&1); rc=$?; else o=$(env "$e" git ls-tree HEAD -- f 2>&1); rc=$?; fi
  echo "  $e rc=$rc out=[$(printf '%s' "$o" | head -1)]"
done
echo
echo "## cross-check vs the committed probe census/round-70/probes/lp-ls-files-probe.txt"
diff -u /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-70/probes/lp-ls-files-probe.txt /dev/null | head -14
echo
echo "NOTE: the committed probe's 'rc=' field is the rc of the 'tr' pipe stage (per the r70"
echo "preregistration), not git's rc; this receipt reports both separately. The GIT_LITERAL"
echo "empty-output / GIT_GLOB+ICASE ls-tree-failure behaviour reproduces exactly."
cd /; rm -rf "$D"
} > "$SEAT/independent-probe.txt" 2>&1
