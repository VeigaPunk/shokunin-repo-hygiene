#!/bin/bash
# S62SentinelScope probes. Scratch only; the lane is read-only; every fixture repo is `git -C "$D"`.
export S=/fast/scratch/hyaku/souji-r62/S62SentinelScope
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
BASEW=$LANE/tools/souji-receipt-write.py
CANDW=$S/cand.py
mkdir -p "$S/receipts" "$S/r60work" || exit 1

cat > "$S/build-cand.py" <<'PY'
import os
S = os.environ["S"]
src = open("/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-receipt-write.py", encoding="utf-8").read()
anchor = "    # behaviour 7: clean lane tree unless --allow-dirty\n"
assert src.count(anchor) == 1, "anchor"
block = (
    "    # C1 candidate (round 62): index-flag concealment, unconditional\n"
    "    fl = git(root, \"ls-files\", \"-v\", \"-z\")\n"
    "    if fl.returncode != 0:\n"
    "        refuse(f\"cannot read index flags of {root}: {fl.stderr.decode('utf-8', 'replace').strip()}\")\n"
    "    for rec in fl.stdout.split(b\"\\0\"):\n"
    "        if not rec:\n"
    "            continue\n"
    "        tag = rec[:1]\n"
    "        if tag != b\"H\":\n"
    "            path = rec[2:].decode(\"utf-8\", \"replace\")\n"
    "            refuse(f\"RECEIPT-INDEX-FLAG-CONCEALED: {path} carries index tag {tag.decode('ascii', 'replace')}; worktree state is not verifiable\")\n"
)
open(os.path.join(S, "cand.py"), "w", encoding="utf-8").write(src.replace(anchor, block + anchor))
print("cand built")
PY

cat > "$S/fsm.sh" <<'FSM'
#!/bin/sh
# fsmonitor hook protocol v2: consume stdin, emit a token and zero changed paths
cat >/dev/null
printf 'tok\000'
FSM
chmod +x "$S/fsm.sh"

cat > "$S/flip.sh" <<'FLIP'
#!/bin/sh
# usage: flip.sh ROOT MODE ; mutates the lane AFTER the writer's clean-tree check, during the command
R=$1
case "$2" in
  flags) git -C "$R" update-index --skip-worktree tools/counter.py && printf 'forged\n' > "$R/tools/counter.py" ;;
  dirty) printf 'notes v3\n' >> "$R/notes.md" ;;
  instr) printf '#!/bin/sh\necho forged\n' > "$R/tools/instr.sh" ;;
esac
echo cmd-done
FLIP

mk() {
  local D
  D=$(mktemp -d -p "$S" "$1.XXXX") || return 1
  git -C "$D" init -q || return 1
  if [ "$(git -C "$D" rev-parse --show-toplevel)" != "$D" ]; then echo "TOPLEVEL-MISMATCH $D" >&2; return 1; fi
  mkdir -p "$D/tools"
  printf '#!/bin/sh\necho instrument-selftest-ok\n' > "$D/tools/instr.sh"
  chmod +x "$D/tools/instr.sh"
  printf 'print("counter v1")\n' > "$D/tools/counter.py"
  printf 'notes v1\n' > "$D/notes.md"
  git -C "$D" add -A || return 1
  git -C "$D" -c user.name=S62Sentinel -c user.email=s62-sentinel@example.invalid commit -qm base || return 1
  printf '%s\n' "$D"
}

# wr WRITER ROOT [writer args]; env: INSTR (default tools/instr.sh), CMD (default echo), WRENV (extra env assignments)
wr() {
  local W=$1 D=$2; shift 2
  local rev O out rc verdict
  rev=$(git -C "$D" rev-parse HEAD) || return 1
  O=$(mktemp -d -p "$S" out.XXXX)
  out=$(env $WRENV python3 -B "$W" --root "$D" --rev "$rev" --instrument "${INSTR:-tools/instr.sh}" --out "$O/r.txt" --allow-outside --command "${CMD:-echo cmd-ok}" "$@" 2>&1); rc=$?
  verdict=REFUSE; [ "$rc" -eq 0 ] && verdict=ACCEPT
  printf '  %-7s rc=%s writer=%s root=%s args=[%s] :: %s\n' "$verdict" "$rc" "$(basename "$W")" "$(basename "$D")" "$*" "$(printf '%s' "$out" | tr '\n' ' ' | cut -c1-240)"
  if [ "$rc" -eq 0 ] && [ -f "$O/r.txt" ]; then cp "$O/r.txt" "$S/receipts/$(basename "$D")-$(basename "$W").$RANDOM.txt"; fi
  return 0
}

echo "== T0 candidate build and parse"
python3 -B "$S/build-cand.py"; echo "build rc=$?"
python3 -B -c 'import ast,sys; ast.parse(open(sys.argv[1]).read()); print("parse ok")' "$CANDW"; echo "parse rc=$?"
echo "base sha: $(sha256sum "$BASEW" | cut -c1-16)  cand sha: $(sha256sum "$CANDW" | cut -c1-16)"

echo "== M matrix (frozen A-G)"
D=$(mk A); echo "A honest-clean"; wr "$BASEW" "$D"; wr "$CANDW" "$D"
D=$(mk B); printf 'notes v2\n' >> "$D/notes.md"; echo "B honest-allow-dirty"; wr "$BASEW" "$D" --allow-dirty; wr "$CANDW" "$D" --allow-dirty
D=$(mk C); printf 'notes v2\n' >> "$D/notes.md"; echo "C dirty-visible"; wr "$BASEW" "$D"; wr "$CANDW" "$D"
D=$(mk D); git -C "$D" update-index --skip-worktree tools/counter.py; printf 'forged\n' > "$D/tools/counter.py"; echo "D skip-worktree-forged"; wr "$BASEW" "$D"; wr "$CANDW" "$D"
D=$(mk E); git -C "$D" update-index --assume-unchanged tools/counter.py; printf 'forged\n' > "$D/tools/counter.py"; echo "E assume-unchanged-forged"; wr "$BASEW" "$D"; wr "$CANDW" "$D"
D=$(mk F); git -C "$D" update-index --skip-worktree tools/counter.py; echo "F skip-worktree-unmodified"; wr "$BASEW" "$D"; wr "$CANDW" "$D"
D=$(mk G); git -C "$D" update-index --skip-worktree tools/instr.sh; printf '#!/bin/sh\necho forged\n' > "$D/tools/instr.sh"; echo "G instrument-skip-worktree-forged"; wr "$BASEW" "$D"; wr "$CANDW" "$D"

echo "== R60 fixture (candidate, then base)"
R60=$LANE/tests/fixtures/r60-receipt-write.py
python3 -B "$R60" --tool "$CANDW" --work "$S/r60work/cand" > "$S/r60-cand.log" 2>&1; echo "r60 cand rc=$?"; tail -3 "$S/r60-cand.log"
python3 -B "$R60" --tool "$BASEW" --work "$S/r60work/base" > "$S/r60-base.log" 2>&1; echo "r60 base rc=$?"; tail -3 "$S/r60-base.log"

echo "== P1 --allow-dirty + flag"
D=$(mk P1a); git -C "$D" update-index --skip-worktree tools/counter.py; printf 'forged\n' > "$D/tools/counter.py"; printf 'notes v2\n' >> "$D/notes.md"; wr "$CANDW" "$D" --allow-dirty
D=$(mk P1b); git -C "$D" update-index --assume-unchanged tools/instr.sh; printf 'notes v2\n' >> "$D/notes.md"; wr "$CANDW" "$D" --allow-dirty
D=$(mk P1c); git -C "$D" update-index --skip-worktree notes.md; printf 'forged\n' > "$D/notes.md"; wr "$CANDW" "$D" --allow-dirty; wr "$BASEW" "$D" --allow-dirty

echo "== P2 GIT_DIR / GIT_WORK_TREE in env (scrub coverage)"
CLEAN=$(mk P2clean); D=$(mk P2dirty); printf 'notes v2\n' >> "$D/notes.md"
git -C "$CLEAN" update-index --skip-worktree tools/counter.py
( export GIT_DIR="$CLEAN/.git"; wr "$CANDW" "$D"; wr "$BASEW" "$D" )
( export GIT_WORK_TREE="$CLEAN"; wr "$CANDW" "$D" )
D2=$(mk P2b); printf 'forged\n' > "$D2/tools/counter.py"
( export GIT_DIR="$CLEAN/.git"; wr "$CANDW" "$D2"; wr "$BASEW" "$D2" )
echo "  control: git -C D2 ls-files -v with GIT_DIR set to CLEAN (should be H, status M):"
( export GIT_DIR="$CLEAN/.git"; git -C "$D2" ls-files -v | cut -c1-40; git -C "$D2" status --porcelain; echo "  status-rc=$?" )

echo "== P3 GIT_INDEX_FILE (index identity; both calls honour the same index?)"
D=$(mk P3a); printf 'forged\n' > "$D/tools/counter.py"; cp "$D/.git/index" "$S/p3-clean.index"
git -C "$D" update-index --skip-worktree tools/counter.py; cp "$D/.git/index" "$S/p3-flag.index"
( export GIT_INDEX_FILE="$S/p3-clean.index"; wr "$CANDW" "$D"; wr "$BASEW" "$D" )
( export GIT_INDEX_FILE="$S/nope.index"; wr "$CANDW" "$D"; wr "$BASEW" "$D" )
D=$(mk P3b); printf 'forged\n' > "$D/tools/counter.py"
( export GIT_INDEX_FILE="$S/p3-flag.index"; wr "$CANDW" "$D" )
( export GIT_INDEX_FILE="$S/p3-flag.index"; wr "$BASEW" "$D" )

echo "== P4 config via env: core.fsmonitor hook hides a visible change (pre-existing surface)"
D=$(mk P4); printf 'forged\n' > "$D/tools/counter.py"
echo "  control no-env:"; wr "$CANDW" "$D"
( export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0="$S/fsm.sh"
  echo "  status with fsmonitor hook:"; git -C "$D" status --porcelain; echo "  status-rc=$?"
  echo "  status with fsmonitor off:"; git -C "$D" -c core.fsmonitor=false status --porcelain; echo "  status-rc=$?"
  wr "$BASEW" "$D"; wr "$CANDW" "$D" )

echo "== P5 core.fileMode=false hides mode-only change"
D=$(mk P5); chmod +x "$D/tools/counter.py"
echo "  control no-env:"; wr "$CANDW" "$D"
( export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fileMode GIT_CONFIG_VALUE_0=false; wr "$BASEW" "$D"; wr "$CANDW" "$D" )

echo "== P6 status.showUntrackedFiles=no hides untracked file"
D=$(mk P6); printf 'x\n' > "$D/tools/extra.py"
echo "  control no-env:"; wr "$CANDW" "$D"
( export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=status.showUntrackedFiles GIT_CONFIG_VALUE_0=no; wr "$BASEW" "$D"; wr "$CANDW" "$D" )

echo "== P7 honest sparse-checkout (false-positive check) and config-only sparse"
D=$(mk P7); git -C "$D" sparse-checkout set --cone tools >/dev/null 2>&1; echo "  sparse-checkout rc=$?"; git -C "$D" ls-files -v | cut -c1-40; git -C "$D" status --porcelain; echo "  status-rc=$?"
wr "$BASEW" "$D"; wr "$CANDW" "$D"
D=$(mk P7b); printf 'forged\n' > "$D/tools/counter.py"; git -C "$D" config core.sparseCheckout true; mkdir -p "$D/.git/info"; printf '/*\n!/tools/\n' > "$D/.git/info/sparse-checkout"; echo "  config-only sparse + forged counter:"; wr "$BASEW" "$D"; wr "$CANDW" "$D"

echo "== P8 subdirectory root (candidate scope = cwd-scoped ls-files)"
D=$(mk P8); git -C "$D" update-index --skip-worktree notes.md; printf 'forged\n' > "$D/notes.md"
echo "  git -C tools status (repo-wide view):"; git -C "$D/tools" status --porcelain; echo "  status-rc=$?"
( export INSTR=instr.sh; wr "$BASEW" "$D/tools"; wr "$CANDW" "$D/tools" )
echo "  control: same flagged file with repo top as root:"; ( export INSTR=tools/instr.sh; wr "$CANDW" "$D" )

echo "== P9 symlinks in path"
D=$(mk P9a); git -C "$D" update-index --skip-worktree tools/counter.py; printf 'forged\n' > "$S/forged-counter.py"; rm "$D/tools/counter.py"; ln -s "$S/forged-counter.py" "$D/tools/counter.py"; wr "$BASEW" "$D"; wr "$CANDW" "$D"
D=$(mk P9b); mv "$D/tools" "$D/tools.real"; ln -s tools.real "$D/tools"; echo "  dir-symlink, no flags:"; wr "$BASEW" "$D"; wr "$CANDW" "$D"
D=$(mk P9c); git -C "$D" update-index --skip-worktree tools/instr.sh; rm "$D/tools/instr.sh"; ln -s "$S/forged-counter.py" "$D/tools/instr.sh"; echo "  instr leaf symlink + flag:"; wr "$BASEW" "$D"; wr "$CANDW" "$D"
D=$(mk P9d); git -C "$D" update-index --skip-worktree tools/instr.sh; mv "$D/tools" "$D/tools.real"; ln -s tools.real "$D/tools"; printf '#!/bin/sh\necho forged\n' > "$D/tools.real/instr.sh"; echo "  dir-symlink + flagged instr with forged bytes:"; wr "$BASEW" "$D"; wr "$CANDW" "$D"

echo "== P10 TOCTOU: change state DURING the command (after check, before write)"
D=$(mk P10a); CMD="sh $S/flip.sh $D flags"; echo "  flags set during run:"; ( export CMD; wr "$BASEW" "$D"; wr "$CANDW" "$D" )
D=$(mk P10b); CMD="sh $S/flip.sh $D dirty"; echo "  visible dirt during run:"; ( export CMD; wr "$BASEW" "$D"; wr "$CANDW" "$D" )
D=$(mk P10c); CMD="sh $S/flip.sh $D instr"; echo "  instrument forged during run:"; ( export CMD; wr "$CANDW" "$D" ); last=$(ls -t "$S/receipts" | head -1); echo "  receipt $last:"; cat "$S/receipts/$last"; echo "  committed instr sha: $(git -C "$D" show HEAD:tools/instr.sh | sha256sum | cut -c1-16)"

echo "== P11 env that could change ls-files -v output or silence the refusal (D has S on counter)"
D=$(mk P11); git -C "$D" update-index --skip-worktree tools/counter.py; printf 'forged\n' > "$D/tools/counter.py"
for X in "GIT_TRACE=1" "GIT_TRACE2_PERF=$S/t2.log" "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.quotePath GIT_CONFIG_VALUE_0=false" "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.sparseCheckout GIT_CONFIG_VALUE_0=false" "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=$S/fsm.sh" "GIT_LITERAL_PATHSPECS=1" "GIT_NO_REPLACE_OBJECTS=1" "GIT_OPTIONAL_LOCKS=1"; do
  echo "  env[$X]:"; ( export $X; git -C "$D" ls-files -v -z | tr '\0' '|' ; echo; WRENV="$X" wr "$CANDW" "$D" )
done
D=$(mk P11b); printf 'x\n' > "$D/tools/extra.py"; echo "  unflagged untracked + cand:"; wr "$CANDW" "$D"
D=$(mk P11c); git -C "$D" update-index --skip-worktree tools/counter.py; printf 'forged\n' > "$D/tools/counter.py"; git -C "$D" mv -f notes.md 'tools/we
ird.py' 2>/dev/null; echo "  filename with newline (renamed, flagged):"; git -C "$D" update-index --skip-worktree 'tools/we
ird.py' 2>/dev/null; printf 'forged\n' > "$D/tools/we
ird.py"; wr "$CANDW" "$D"

echo "== P12 unmerged (stage>0) entry: tag M"
D=$(mk P12); b=$(git -C "$D" hash-object -w tools/counter.py); printf '100644 %s 1\ttools/counter.py\n100644 %s 2\ttools/counter.py\n' "$b" "$b" | git -C "$D" update-index --index-info; git -C "$D" ls-files -v -z | tr '\0' '|'; echo; wr "$BASEW" "$D"; wr "$CANDW" "$D"

echo "== P13 intent-to-add"
D=$(mk P13); printf 'x\n' > "$D/tools/new.py"; git -C "$D" add -N tools/new.py; git -C "$D" ls-files -v | cut -c1-40; wr "$BASEW" "$D"; wr "$CANDW" "$D"

echo "== P14 skip+assume on same path"
D=$(mk P14); git -C "$D" update-index --skip-worktree tools/counter.py; git -C "$D" update-index --assume-unchanged tools/counter.py; printf 'forged\n' > "$D/tools/counter.py"; git -C "$D" ls-files -v | cut -c1-40; wr "$CANDW" "$D"

echo "== SWEEP"
echo "lane HEAD: $(GIT_OPTIONAL_LOCKS=0 git -C "$LANE" rev-parse HEAD)"
echo "lane ls-files -v tags:"; GIT_OPTIONAL_LOCKS=0 git -C "$LANE" ls-files -v | cut -c1 | sort | uniq -c
echo "lane status:"; GIT_OPTIONAL_LOCKS=0 git -C "$LANE" status --porcelain | head -20; echo "status-rc=${PIPESTATUS[0]}"
echo "wave dir:"; ls -la "$LANE/.ufo/waves/round-62/w1/"
echo "lane files newer than w1 (excl .git):"; find "$LANE" -newer "$LANE/.ufo/waves/round-62/w1/swarm-registry.json" -not -path '*/.git/*' 2>/dev/null | head -40
echo "find /tmp (task spec sweep):"; find /tmp -newer /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1 -user vgpnk -maxdepth 2 2>/dev/null | head; echo "find-rc=${PIPESTATUS[0]}"
echo "scratch root:"; ls -la /fast/scratch/hyaku/souji-r62/ 2>&1
echo "PROBES DONE"
