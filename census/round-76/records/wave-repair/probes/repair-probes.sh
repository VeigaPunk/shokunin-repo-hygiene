#!/usr/bin/env bash
# souji r76 wave-repair probes (L1), computed verdicts (r75 routed defect 1 rule: a probe must be able to fail).
# Usage: repair-probes.sh GATE_W_DIR GATE_R_DIR SCRATCH LANE_GITIGNORE_W LANE_GITIGNORE_R
#   GATE_*_DIR hold souji-pre-report-gate.sh beside souji-receipt-write.py (W = e827d2bf, R = repair).
# Routes (expected): fsmonitor  W=PASS(forged) R=FAIL      (S76Sentinel HIGH-1)
#                    execpath   W=EXEC        R=NO-EXEC    (S76Sentinel MEDIUM-1)
#                    single     R=FAIL        M09=PASS     (S76MutGate HIGH-1 kill-power; M09 = R with `if undeclared > 1:`)
#                    nested-jj  gitignore-W=PASS gitignore-R=FAIL (S76CriticClaims: unanchored .jj/ hid sub/.jj/)
# Prints one ROW per arm and `SUMMARY arms=<n> as_expected=<k>`; exit 0 iff every arm is as expected, 1 otherwise,
# 2 on usage.
set -u
GW=${1:?usage}; GR=${2:?usage}; SD=${3:?usage}; GIW=${4:?usage}; GIR=${5:?usage}
[[ -f $GW/souji-pre-report-gate.sh && -f $GR/souji-pre-report-gate.sh && -d $SD && -f $GIW && -f $GIR ]] || { echo usage >&2; exit 2; }
S=$(mktemp -d -p "$SD" rp.XXXXXX) && [[ -n $S && -d $S ]] || exit 2
trap 'rm -rf -- "$S"' EXIT
export GIT_AUTHOR_NAME=fx GIT_AUTHOR_EMAIL=fx@invalid GIT_COMMITTER_NAME=fx GIT_COMMITTER_EMAIL=fx@invalid
printf '# r\n\n## SHONEN\n\n- [ ] b\n' > "$S/report.md"; printf 'f\n' > "$S/prereg.txt"
n=0 ok=0
row() { n=$((n+1)); [[ $3 == "$4" ]] && ok=$((ok+1)); printf 'ROW %s arm=%s got=%s expect=%s match=%s\n' "$1" "$2" "$3" "$4" "$([[ $3 == "$4" ]] && echo yes || echo no)"; }
fixture() {  # fixture DIR GITIGNORE_BYTES_FILE
  local d=$1; mkdir -p "$d"; git -C "$d" init -q -b master
  [[ $(git -C "$d" rev-parse --show-toplevel) == "$d" ]] || exit 2
  printf 'base\n' > "$d/README.md"; cp "$2" "$d/.gitignore"
  git -C "$d" add -A; git -C "$d" commit -q -m base
  git -C "$d" clone -q --bare "$d" "$d.git"; git -C "$d" remote add origin "$d.git"
}
clean() { bash "$1/souji-pre-report-gate.sh" --lane "$2" --branch master --report "$S/report.md" --prereg "$S/prereg.txt" 2>/dev/null | sed -n 's/^check-clean=//p'; }

# fsmonitor: a repo-local hook that appends `cache/` to the tracked .gitignore when a `--cached` listing runs.
printf '__pycache__/\n' > "$S/gi-plain"
for arm in W R; do
  d=$S/fsm-$arm; fixture "$d" "$S/gi-plain"
  mkdir -p "$d/cache"; printf '*\n' > "$d/cache/.gitignore"; printf 'payload\n' > "$d/cache/payload.bin"
  cat > "$S/hook-$arm.sh" <<EOF
#!/bin/sh
case "\$(tr '\0' ' ' < /proc/\$PPID/cmdline)" in *--cached*) printf 'cache/\n' >> "$d/.gitignore" ;; esac
printf '2\n%s\0' "\$2"
EOF
  chmod +x "$S/hook-$arm.sh"; git -C "$d" config core.fsmonitor "$S/hook-$arm.sh"
  g=$GW; [[ $arm == R ]] && g=$GR
  row fsmonitor "$arm" "$(clean "$g" "$d")" "$([[ $arm == W ]] && echo PASS || echo FAIL)"
done

# execpath: a caller GIT_EXEC_PATH holding a fake git-remote-https that leaves a marker.
mkdir -p "$S/xp"; printf '#!/bin/sh\ntouch "%s/xp/fired"\nexit 1\n' "$S" > "$S/xp/git-remote-https"; chmod +x "$S/xp/git-remote-https"
for arm in W R; do
  d=$S/xp-$arm; fixture "$d" "$S/gi-plain"; git -C "$d" remote set-url origin https://example.invalid/x.git
  rm -f "$S/xp/fired"; g=$GW; [[ $arm == R ]] && g=$GR
  GIT_EXEC_PATH=$S/xp bash "$g/souji-pre-report-gate.sh" --lane "$d" --branch master --report "$S/report.md" --prereg "$S/prereg.txt" >/dev/null 2>&1
  got=NO-EXEC; [[ -e $S/xp/fired ]] && got=EXEC
  row execpath "$arm" "$got" "$([[ $arm == W ]] && echo EXEC || echo NO-EXEC)"
done

# single: one undeclared path only (a self-ignoring `/.gitignore`), R gate versus the M09 threshold mutant.
mkdir -p "$S/m09"; cp "$GR/souji-receipt-write.py" "$S/m09/"
python3 - "$GR/souji-pre-report-gate.sh" "$S/m09/souji-pre-report-gate.sh" <<'PY' || exit 2
import sys
src = open(sys.argv[1]).read()
old = "    if undeclared:\n"
assert src.count(old) == 1
open(sys.argv[2], "w").write(src.replace(old, "    if undeclared > 1:\n"))
PY
for arm in R M09; do
  d=$S/single-$arm; fixture "$d" "$S/gi-plain"; mkdir -p "$d/pl"; printf '/.gitignore\n' > "$d/pl/.gitignore"
  g=$GR; [[ $arm == M09 ]] && g=$S/m09
  row single "$arm" "$(clean "$g" "$d")" "$([[ $arm == R ]] && echo FAIL || echo PASS)"
done

# nested-jj: the lane's committed .gitignore at W (unanchored .jj/) versus at R (anchored /.jj/), R gate.
for arm in gitignore-W gitignore-R; do
  gi=$GIW; [[ $arm == gitignore-R ]] && gi=$GIR
  d=$S/nj-$arm; fixture "$d" "$gi"; mkdir -p "$d/sub/.jj"; printf 'payload\n' > "$d/sub/.jj/payload"
  row nested-jj "$arm" "$(clean "$GR" "$d")" "$([[ $arm == gitignore-W ]] && echo PASS || echo FAIL)"
done

printf 'SUMMARY arms=%s as_expected=%s\n' "$n" "$ok"
(( ok == n )) && exit 0 || exit 1
