#!/usr/bin/env bash
# S75Sentinel driver 4: isolated new-block error, HOME-only set logic, root-FIFO gate hang, real-lane cost.
set -u
S=/fast/scratch/hyaku/souji-r75/S75Sentinel
G=$S/gateW
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p "$S/fx"
REALGIT=$(command -v git)
mkfix() {
  local d
  d=$(mktemp -d -p "$S/fx" fx.XXXXXX) || return 1
  [ -n "$d" ] && [ -d "$d" ] || return 1
  git -C "$d" init -q -b main >/dev/null 2>&1 || return 1
  [ "$(git -C "$d" rev-parse --show-toplevel 2>/dev/null)" = "$d" ] || return 1
  git -C "$d" config user.email r75@fixture.invalid; git -C "$d" config user.name r75fixture
  printf 'alpha\n' > "$d/a.txt"; git -C "$d" add a.txt; git -C "$d" commit -qm seed
  git -C "$d" remote add origin "$d"; printf '%s' "$d"
}
gate() {
  local d=$1 label=$2; shift 2
  local rep pre out rc
  rep=$(mktemp -p "$S/fx" rep.XXXXXX); pre=$(mktemp -p "$S/fx" pre.XXXXXX)
  printf '## SHONEN p\n' > "$rep"; printf 'p\n' > "$pre"
  out=$(env "$@" timeout 90 bash "$G/souji-pre-report-gate.sh" --lane "$d" --branch main --report "$rep" --prereg "$pre" 2>&1); rc=$?
  printf 'PROBE %-34s rc=%s %s\n' "$label" "$rc" "$(printf '%s\n' "$out" | grep -E '^(check-clean|detail-clean)' | head -2 | tr '\n' '|')"
}

# 1. isolated new-block git error (shim fails only --others calls)
shim=$(mktemp -d -p "$S/fx" shim.XXXXXX)
cat > "$shim/git" <<EOF
#!/usr/bin/env bash
for a in "\$@"; do case \$a in --others) exit 3 ;; esac; done
exec "$REALGIT" "\$@"
EOF
chmod +x "$shim/git"; d=$(mkfix)
gate "$d" Z1-newblock-git-error PATH="$shim:$PATH"; rm -rf -- "$d" "$shim"

# 2. HOME-only global ignore: raw set difference (no repo excludesFile)
d=$(mkfix); h=$(mktemp -d -p "$S/fx" home.XXXXXX); mkdir -p "$h/.config/git"
printf '*.swp\n' > "$h/.config/git/ignore"; printf 'v\n' > "$d/note.swp"
std=$(HOME="$h" XDG_CONFIG_HOME="$h/.config" "$REALGIT" -C "$d" --no-optional-locks ls-files -z --others --ignored --exclude-standard | tr '\0' '\n')
per=$(HOME="$h" XDG_CONFIG_HOME="$h/.config" "$REALGIT" -C "$d" --no-optional-locks ls-files -z --others --ignored --exclude-per-directory=.gitignore | tr '\0' '\n')
printf 'SET-HOME std=[%s] per=[%s] hidden=[%s]\n' "$std" "$per" "$(comm -23 <(printf '%s\n' "$std" | sort) <(printf '%s\n' "$per" | sort) | tr '\n' ' ')"
rm -rf -- "$d" "$h"

# 3. gate hang on root .gitignore FIFO hidden by info/exclude (pre-existing status read)
d=$(mkfix); printf '/.gitignore\n' >> "$d/.git/info/exclude"; mkfifo "$d/.gitignore"
rep=$(mktemp -p "$S/fx" rep.XXXXXX); pre=$(mktemp -p "$S/fx" pre.XXXXXX); printf '## SHONEN p\n' > "$rep"; printf 'p\n' > "$pre"
timeout 15 bash "$G/souji-pre-report-gate.sh" --lane "$d" --branch main --report "$rep" --prereg "$pre" >/dev/null 2>&1; rc=$?
printf 'PROBE Z3-gate-root-fifo rc=%s (124=hang)\n' "$rc"; rm -rf -- "$d" "$rep" "$pre"

# 4. real-lane cost of the new block's two listings + its verdict
start=$(date +%s%N)
"$REALGIT" -C "$LANE" --no-optional-locks -c core.fsmonitor=false ls-files -z --others --ignored --exclude-standard > "$S/fx/lane-std.bin"; rc1=$?
t1=$(( ($(date +%s%N) - start) / 1000000 ))
start=$(date +%s%N)
"$REALGIT" -C "$LANE" --no-optional-locks -c core.fsmonitor=false ls-files -z --others --ignored --exclude-per-directory=.gitignore > "$S/fx/lane-per.bin"; rc2=$?
t2=$(( ($(date +%s%N) - start) / 1000000 ))
python3 - "$S/fx/lane-std.bin" "$S/fx/lane-per.bin" <<'PY'
import sys
a = set(open(sys.argv[1], "rb").read().split(b"\0")) - {b""}
b = set(open(sys.argv[2], "rb").read().split(b"\0")) - {b""}
h = a - b
print("LANE std=%d per=%d hidden=%d sample=%r" % (len(a), len(b), len(h), sorted(h)[:3]))
PY
printf 'LANE timing std=%sms per=%sms rc=%s/%s\n' "$t1" "$t2" "$rc1" "$rc2"
rm -f "$S/fx/lane-std.bin" "$S/fx/lane-per.bin"
