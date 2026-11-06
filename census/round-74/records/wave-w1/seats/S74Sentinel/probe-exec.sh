#!/usr/bin/env bash
# probe-exec.sh — S74Sentinel: can a caller/worktree-controlled path make the
# stage-W gate execute other code inside its check-4 python child?
#
# Vectors (each on its own fresh forged fixture lane; baseline = clean refusal):
#   V-A  .git/info/exclude hides `subprocess.py` in the gate's CWD (the lane root);
#        the writer's `import subprocess` then runs it. Fail-open: exit 0 => check-clean=PASS.
#   V-B  a planted `tools/__pycache__/souji-receipt-write.cpython-3XX.pyc` beside the
#        gate's writer (the real lane's .gitignore already carries `__pycache__/`);
#        `python3 -B` stops writing bytecode but not reading a valid cached one.
#   V-C  PYTHONPATH carrying a `subprocess.py` shim (env, not worktree).
#
# Usage: probe-exec.sh <SCRATCH> <gate-dir>   (gate-dir holds gate-w.sh + souji-receipt-write.py)
set -u
S=${1:?scratch dir}; GATE_DIR=${2:?gate dir}
test -n "$S" || exit 9; test -d "$S" || exit 9
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
MK="$HERE/mkfixture.py"
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"

runtime() {  # runtime <root> -> prints verdict
  local root=$1
  printf '# Report\n\n## SHONEN\n[~] box `a`\n' > "$root/report.md"
  printf 'prereg\n' > "$root/prereg.txt"
  ( cd "$root/lane" && timeout 120 bash "$GATE_DIR/gate-w.sh" --lane "$root/lane" \
      --branch master --report "$root/report.md" --prereg "$root/prereg.txt" ) > "$root/out.txt" 2>&1
  echo "exit=$?"
  grep -E '^check-clean=' "$root/out.txt" || echo "check-clean=<absent>"
}

echo "########## baseline: forged lane, no injection ##########"
R="$S/e0"; rm -rf "$R"; python3 -B "$MK" --root "$R" --forge >/dev/null
echo "status=$(git -C "$R/lane" status --porcelain=v1 --untracked-files=all | wc -l) lines"
runtime "$R"

echo
echo "########## V-A: .git/info/exclude + subprocess.py in the gate CWD ##########"
R="$S/eA"; rm -rf "$R"; python3 -B "$MK" --root "$R" --forge >/dev/null
cat > "$R/lane/subprocess.py" <<'PY'
import sys
try:
    open(".pwned", "w").write("V-A executed inside the gate's check-4 python\n")
except OSError:
    pass
sys.stderr.write("V-A-PWNED\n")
sys.exit(0)
PY
printf 'subprocess.py\n' >> "$R/lane/.git/info/exclude"
echo "status=$(git -C "$R/lane" status --porcelain=v1 --untracked-files=all | wc -l) lines (exclude hides it)"
runtime "$R"
echo "marker: $(cat "$R/lane/.pwned" 2>/dev/null || echo ABSENT)"
grep -c 'V-A-PWNED' "$R/out.txt" | sed 's/^/pwned_lines=/'

echo
echo "########## V-B: planted __pycache__/*.pyc beside the gate's writer ##########"
R="$S/eB"; rm -rf "$R"; python3 -B "$MK" --root "$R" --forge >/dev/null
G2="$R/gate"; mkdir -p "$G2"
cp "$GATE_DIR/gate-w.sh" "$G2/gate-w.sh"
cp "$GATE_DIR/souji-receipt-write.py" "$G2/souji-receipt-write.py"
python3 - "$G2" <<'PY'
import importlib.util, os, py_compile, struct, sys
g = sys.argv[1]
src = os.path.join(g, "souji-receipt-write.py")
payload = os.path.join(g, "_pwn_payload.py")
open(payload, "w").write(
    "open('.pwned','w').write('V-B executed from cached bytecode\\n')\n"
    "import sys\nsys.stderr.write('V-B-PWNED\\n')\nsys.exit(0)\n")
cache = importlib.util.cache_from_source(src)
os.makedirs(os.path.dirname(cache), exist_ok=True)
py_compile.compile(payload, cfile=cache, doraise=True)
st = os.stat(src)
# timestamp-based pyc header: magic(4) flags(4) mtime(4) size(4)
b = bytearray(open(cache, "rb").read())
print("pyc=%s magic=%r" % (cache, bytes(b[:4])))
struct.pack_into("<I", b, 8, int(st.st_mtime))
struct.pack_into("<I", b, 12, st.st_size & 0xFFFFFFFF)
open(cache, "wb").write(bytes(b))
print("planted %d bytes; source mtime=%d size=%d" % (len(b), st.st_mtime, st.st_size))
PY
cp "$R/gate/souji-receipt-write.py" "$GATE_DIR/../eB-orig-writer.py" 2>/dev/null || true
GATE_DIR_SAVE=$GATE_DIR; GATE_DIR="$G2"
runtime "$R"
echo "marker: $(cat "$R/lane/.pwned" 2>/dev/null || echo ABSENT)"
grep -c 'V-B-PWNED' "$R/out.txt" | sed 's/^/pwned_lines=/'
GATE_DIR=$GATE_DIR_SAVE

echo
echo "########## V-C: PYTHONPATH carries a subprocess.py shim ##########"
R="$S/eC"; rm -rf "$R"; python3 -B "$MK" --root "$R" --forge >/dev/null
I="$R/inj"; mkdir -p "$I"
cat > "$I/subprocess.py" <<'PY'
import sys
open(".pwned", "w").write("V-C executed via PYTHONPATH\n")
sys.stderr.write("V-C-PWNED\n")
sys.exit(0)
PY
printf '# Report\n\n## SHONEN\n[~] box `a`\n' > "$R/report.md"; printf 'prereg\n' > "$R/prereg.txt"
( cd "$R/lane" && PYTHONPATH="$I" timeout 120 bash "$GATE_DIR/gate-w.sh" --lane "$R/lane" \
    --branch master --report "$R/report.md" --prereg "$R/prereg.txt" ) > "$R/out.txt" 2>&1
echo "exit=$?"
grep -E '^check-clean=' "$R/out.txt" || echo "check-clean=<absent>"
echo "marker: $(cat "$R/lane/.pwned" 2>/dev/null || echo ABSENT)"
grep -c 'V-C-PWNED' "$R/out.txt" | sed 's/^/pwned_lines=/'
