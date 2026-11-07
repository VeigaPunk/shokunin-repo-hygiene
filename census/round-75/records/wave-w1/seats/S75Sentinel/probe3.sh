#!/usr/bin/env bash
# S75Sentinel driver 3: scale (200k ignored files), depth-2000 tree, FIFO inside ignored dir; wall+RSS.
set -u
S=/fast/scratch/hyaku/souji-r75/S75Sentinel
G=$S/gateW
mkdir -p "$S/fx"
REALGIT=$(command -v git)
d=$(mktemp -d -p "$S/fx" fx.XXXXXX); [ -n "$d" ] && [ -d "$d" ] || exit 1
git -C "$d" init -q -b main || exit 1
[ "$(git -C "$d" rev-parse --show-toplevel)" = "$d" ] || { echo TOP-MISMATCH; exit 1; }
git -C "$d" config user.email r75@fixture.invalid; git -C "$d" config user.name r75fixture
printf 'alpha\n' > "$d/a.txt"; printf 'bulk/\ndeep/\n' > "$d/.gitignore"
git -C "$d" add a.txt .gitignore; git -C "$d" commit -qm seed; git -C "$d" remote add origin "$d"

python3 - "$d" <<'PY'
import os, sys, time
d = sys.argv[1]; t = time.time()
# 200k ignored files: 200 dirs x 1000 files
for i in range(200):
    sub = os.path.join(d, "bulk", "d%03d" % i); os.makedirs(sub)
    for j in range(1000):
        open(os.path.join(sub, "f%04d.dat" % j), "wb").close()
print("created 200000 files in %.1fs" % (time.time() - t))
# deep chain, depth 2000, via openat so the creator is not PATH_MAX-bound
p = os.path.join(d, "deep")
os.makedirs(p)
fd = os.open(p, os.O_RDONLY | os.O_DIRECTORY)
depth = 0
try:
    for k in range(2000):
        os.mkdir("d", dir_fd=fd)
        nfd = os.open("d", os.O_RDONLY | os.O_DIRECTORY, dir_fd=fd)
        os.close(fd); fd = nfd; depth += 1
    os.close(os.open("leaf.txt", os.O_WRONLY | os.O_CREAT, 0o644, dir_fd=fd))
except OSError as e:
    print("deep stopped at depth %d: %s" % (depth, e))
finally:
    os.close(fd)
print("deep depth=%d pathlen~%d" % (depth, len(os.path.join(d, "deep") + "/d" * depth + "/leaf.txt")))
PY

rep=$(mktemp -p "$S/fx" rep.XXXXXX); pre=$(mktemp -p "$S/fx" pre.XXXXXX)
printf '## SHONEN p\n' > "$rep"; printf 'p\n' > "$pre"
echo "== gate 200k+deep =="
/usr/bin/time -f 'GATE wall=%e maxrss_kb=%M' timeout 300 bash "$G/souji-pre-report-gate.sh" --lane "$d" --branch main --report "$rep" --prereg "$pre" > "$S/fx/scale.out" 2> "$S/fx/scale.err"; rc=$?
grep -E '^(check-clean|detail-clean)' "$S/fx/scale.out" "$S/fx/scale.err" 2>/dev/null | head -3
grep 'GATE wall' "$S/fx/scale.err"; echo "GATE rc=$rc"
echo "== raw invocations =="
for rule in --exclude-standard --exclude-per-directory=.gitignore; do
  /usr/bin/time -f "RAW $rule wall=%e maxrss_kb=%M" timeout 300 "$REALGIT" -C "$d" --no-optional-locks -c core.fsmonitor=false ls-files -z --others --ignored "$rule" > /dev/null 2> "$S/fx/raw.err"; r=$?
  grep "RAW $rule" "$S/fx/raw.err"; echo "RAW $rule rc=$r"
done
echo "== block replica memory =="
/usr/bin/time -f 'REPL wall=%e maxrss_kb=%M' python3 - "$d" <<'PY'
import resource, subprocess, sys
lane = sys.argv[1]
def ig(*rule):
    p = subprocess.run(["git", "--no-optional-locks", "-C", lane, "-c", "core.fsmonitor=false", "ls-files",
                        "-z", "--others", "--ignored", *rule], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    assert p.returncode == 0, p.returncode
    return set(p.stdout.split(b"\0")) - {b""}
hidden = ig("--exclude-standard") - ig("--exclude-per-directory=.gitignore")
print("REPL hidden=%d maxrss_kb=%d" % (len(hidden), resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
PY
rm -rf -- "$d" "$rep" "$pre" "$S/fx/scale.out" "$S/fx/scale.err" "$S/fx/raw.err"
