#!/usr/bin/env bash
# probe-env.sh — S74Sentinel: environment vectors against the stage-W gate's
# check-4 python child, on a stat-cache-forged fixture lane (baseline check-clean=FAIL).
#   E1 BASH_ENV          : a non-interactive bash child sources it before line 1
#   E2 PATH python3      : `python3` is not pinned; a shim exits 0
#   E3 PYTHONHOME        : interpreter init breaks
#   E4 PYTHONSTARTUP     : only read by an interactive interpreter
#   E5 PYTHONINSPECT     : drops to interactive only with a tty
#   E6 PYTHONSAFEPATH    : removes '' (the CWD) from sys.path — hardening, not a bypass
# Usage: probe-env.sh <SCRATCH> <gate-dir>
set -u
S=${1:?scratch}; GATE_DIR=${2:?gate dir}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
MK="$HERE/mkfixture.py"
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"

fresh() { local r=$1; rm -rf "$r"; python3 -B "$MK" --root "$r" --forge >/dev/null
  printf '# Report\n\n## SHONEN\n[~] box `a`\n' > "$r/report.md"; printf 'prereg\n' > "$r/prereg.txt"; }

run() {  # run <root> <out> [env assignments...]
  local r=$1 o=$2; shift 2
  ( cd "$r/lane" && env "$@" timeout 60 bash "$GATE_DIR/gate-w.sh" --lane "$r/lane" \
      --branch master --report "$r/report.md" --prereg "$r/prereg.txt" ) > "$o" 2>&1
  echo "exit=$?"
  grep -E '^check-clean=' "$o" || echo "check-clean=<absent>"
}

echo "########## E0 baseline ##########"
R="$S/v0"; fresh "$R"; run "$R" "$R/out.txt"

echo; echo "########## E1 BASH_ENV ##########"
R="$S/v1"; fresh "$R"
cat > "$R/be.sh" <<'SH'
printf 'E1-BASH_ENV-PWNED\n' >&2
printf 'check-clean=PASS\n'
exit 0
SH
run "$R" "$R/out.txt" BASH_ENV="$R/be.sh"

echo; echo "########## E2 PATH-shadowed python3 ##########"
R="$S/v2"; fresh "$R"; mkdir -p "$R/bin"
printf '#!/bin/sh\nexit 0\n' > "$R/bin/python3"; chmod +x "$R/bin/python3"
run "$R" "$R/out.txt" PATH="$R/bin:/usr/bin:/bin"

echo; echo "########## E3 PYTHONHOME=/nonexistent ##########"
R="$S/v3"; fresh "$R"; run "$R" "$R/out.txt" PYTHONHOME=/nonexistent

echo; echo "########## E4 PYTHONSTARTUP=<payload> ##########"
R="$S/v4"; fresh "$R"
printf 'open(".pwned","w").write("E4")\n' > "$R/su.py"
run "$R" "$R/out.txt" PYTHONSTARTUP="$R/su.py"
echo "marker: $(cat "$R/lane/.pwned" 2>/dev/null || echo ABSENT)"

echo; echo "########## E5 PYTHONINSPECT=1 ##########"
R="$S/v5"; fresh "$R"; run "$R" "$R/out.txt" PYTHONINSPECT=1

echo; echo "########## E6 PYTHONSAFEPATH=1 (hardening check) ##########"
R="$S/v6"; fresh "$R"
printf 'import sys\nsys.exit(0)\n' > "$R/lane/subprocess.py"
printf 'subprocess.py\n' >> "$R/lane/.git/info/exclude"
run "$R" "$R/out.txt" PYTHONSAFEPATH=1

echo; echo "########## E7 PYTHONSAFEPATH unset, same injection (control) ##########"
R="$S/v7"; fresh "$R"
printf 'import sys\nsys.exit(0)\n' > "$R/lane/subprocess.py"
printf 'subprocess.py\n' >> "$R/lane/.git/info/exclude"
run "$R" "$R/out.txt"
