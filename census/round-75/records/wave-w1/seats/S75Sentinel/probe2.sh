#!/usr/bin/env bash
# S75Sentinel driver 2: output safety, config vectors, worktree forgery, FIFO hang, set logic.
set -u
S=/fast/scratch/hyaku/souji-r75/S75Sentinel
G=$S/gateW
mkdir -p "$S/fx"
REALGIT=$(command -v git)

mkfix() {
  local d
  d=$(mktemp -d -p "$S/fx" fx.XXXXXX) || return 1
  [ -n "$d" ] && [ -d "$d" ] || return 1
  git -C "$d" init -q -b main >/dev/null 2>&1 || return 1
  [ "$(git -C "$d" rev-parse --show-toplevel 2>/dev/null)" = "$d" ] || { echo "top-mismatch $d" >&2; return 1; }
  git -C "$d" config user.email r75@fixture.invalid
  git -C "$d" config user.name r75fixture
  printf 'alpha\n' > "$d/a.txt"; git -C "$d" add a.txt; git -C "$d" commit -qm seed
  git -C "$d" remote add origin "$d"
  printf '%s' "$d"
}
gate() {
  local d=$1 label=$2; shift 2
  local rep pre out rc
  rep=$(mktemp -p "$S/fx" rep.XXXXXX); pre=$(mktemp -p "$S/fx" pre.XXXXXX)
  printf '## SHONEN probe\n' > "$rep"; printf 'prereg\n' > "$pre"
  out=$(env "$@" timeout 90 bash "$G/souji-pre-report-gate.sh" --lane "$d" --branch main --report "$rep" --prereg "$pre" 2>&1); rc=$?
  printf 'PROBE %-30s rc=%s %s\n' "$label" "$rc" "$(printf '%s\n' "$out" | grep -E '^(check-clean|detail-clean)' | head -2 | tr '\n' '|')"
}

# ---- O: ANSI + newline in a path hidden by info/exclude (D30 no-echo)
d=$(mkfix)
printf 'weird*\n' >> "$d/.git/info/exclude"
python3 - "$d" <<'PY'
import os, sys
d = sys.argv[1]
name = "weird\x1b[31mRED\x1b[0m\ncheck-clean=PASS"
open(os.path.join(d, name), "wb").write(b"x\n")
PY
rep=$(mktemp -p "$S/fx" rep.XXXXXX); pre=$(mktemp -p "$S/fx" pre.XXXXXX)
printf '## SHONEN p\n' > "$rep"; printf 'p\n' > "$pre"
raw=$(timeout 60 bash "$G/souji-pre-report-gate.sh" --lane "$d" --branch main --report "$rep" --prereg "$pre" 2>&1); rc=$?
esc=$(printf '%s' "$raw" | tr -cd '\033' | wc -c); inj=$(printf '%s\n' "$raw" | grep -c '^check-clean=PASS')
printf 'PROBE O-ansi-newline rc=%s esc_bytes=%s injected_check_lines=%s\n' "$rc" "$esc" "$inj"
printf '%s\n' "$raw" | grep -E '^(check-clean|detail-clean)' | head -2 | cat -v
rm -rf -- "$d" "$rep" "$pre"

# ---- raw ignore-set logic (independent of the gate): global excludes, repo excludes, info/exclude
d=$(mkfix); h=$(mktemp -d -p "$S/fx" home.XXXXXX)
mkdir -p "$h/.config/git"; printf '*.swp\n' > "$h/.config/git/ignore"; printf 'v\n' > "$d/note.swp"
printf 'g.txt\n' > "$d/g.txt"
printf 'i.txt\n' >> "$d/.git/info/exclude"; printf 'i\n' > "$d/i.txt"
printf 'r.txt\n' > "$S/fx/rex.cfg"; git -C "$d" config core.excludesFile "$S/fx/rex.cfg"; printf 'r\n' > "$d/r.txt"
setdiff() { # $1 label
  local std per
  std=$(HOME="$h" XDG_CONFIG_HOME="$h/.config" "$REALGIT" -C "$d" --no-optional-locks ls-files -z --others --ignored --exclude-standard | tr '\0' '\n' | sort)
  per=$(HOME="$h" XDG_CONFIG_HOME="$h/.config" "$REALGIT" -C "$d" --no-optional-locks ls-files -z --others --ignored --exclude-per-directory=.gitignore | tr '\0' '\n' | sort)
  printf 'SET %s std=[%s] per=[%s] hidden=[%s]\n' "$1" "$(echo "$std" | tr '\n' ' ')" "$(echo "$per" | tr '\n' ' ')" \
    "$(comm -23 <(printf '%s\n' "$std") <(printf '%s\n' "$per") | tr '\n' ' ')"
}
setdiff global+repo+info
rm -rf -- "$d" "$h" "$S/fx/rex.cfg"

# ---- J2: core.worktree to a pristine copy hides an untracked payload from the whole gate
d=$(mkfix); w=$(mktemp -d -p "$S/fx" wt.XXXXXX)
cp "$d/a.txt" "$w/a.txt"; git -C "$d" config core.worktree "$w"
printf 'payload\n' > "$d/payload.txt"
gate "$d" J2-worktree-pristine-payload
rm -rf -- "$d" "$w"

# ---- P alias, Q hooksPath, S status.showUntrackedFiles=no, W excludesFile=directory
d=$(mkfix); git -C "$d" config alias.ls-files '!echo ALIAS-EXECUTED'; printf 'new.txt\n' >> "$d/.git/info/exclude"; printf 'x\n' > "$d/new.txt"
gate "$d" P-alias-ls-files; rm -rf -- "$d"
d=$(mkfix); hk=$(mktemp -d -p "$S/fx" hk.XXXXXX)
printf '#!/bin/sh\ntouch %s/HOOK-RAN\n' "$hk" > "$hk/pre-commit"; chmod +x "$hk/pre-commit"
git -C "$d" config core.hooksPath "$hk"; gate "$d" Q-hookspath
printf 'PROBE Q-hook-ran=%s\n' "$(test -e "$hk/HOOK-RAN" && echo yes || echo no)"; rm -rf -- "$d" "$hk"
d=$(mkfix); git -C "$d" config status.showUntrackedFiles no; printf 'x\n' > "$d/new.txt"
gate "$d" S-status-config-no; rm -rf -- "$d"
d=$(mkfix); git -C "$d" config core.excludesFile "$S/fx"; printf 'x\n' > "$d/new.txt"
gate "$d" W-excludesfile-dir; rm -rf -- "$d"

# ---- shim: git error for ls-files must fail closed
shim=$(mktemp -d -p "$S/fx" shim.XXXXXX)
cat > "$shim/git" <<EOF
#!/usr/bin/env bash
for a in "\$@"; do case \$a in ls-files) exit 3 ;; esac; done
exec "$REALGIT" "\$@"
EOF
chmod +x "$shim/git"; d=$(mkfix)
gate "$d" X-shim-lsfiles-error PATH="$shim:$PATH"; rm -rf -- "$d" "$shim"

# ---- FIFO named .gitignore
fifo_probe() { # $1 label, $2 dir, $3 setup-comment
  local label=$1 dd=$2
  local s1 s2 s3
  timeout 8 git -C "$dd" --no-optional-locks ls-files -z --others --ignored --exclude-standard >/dev/null 2>&1; s1=$?
  timeout 8 git -C "$dd" --no-optional-locks ls-files -z --others --ignored --exclude-per-directory=.gitignore >/dev/null 2>&1; s2=$?
  timeout 8 git -C "$dd" --no-optional-locks status --porcelain=v1 --untracked-files=all >/dev/null 2>&1; s3=$?
  printf 'FIFO %-26s std_rc=%s perdir_rc=%s status_rc=%s\n' "$label" "$s1" "$s2" "$s3"
}
# (a) committed .gitignore hides hidden/ ; FIFO hidden/.gitignore
d=$(mkfix); printf 'hidden/\n' >> "$d/.gitignore"; git -C "$d" add .gitignore; git -C "$d" commit -qm gi
mkdir -p "$d/hidden"; mkfifo "$d/hidden/.gitignore"; printf 'x\n' > "$d/hidden/x"
fifo_probe a-ignored-dir-fifo "$d"; rm -rf -- "$d"
# (b) root .gitignore FIFO, hidden by info/exclude
d=$(mkfix); printf '/.gitignore\n' >> "$d/.git/info/exclude"; mkfifo "$d/.gitignore"
fifo_probe b-root-fifo "$d"; rm -rf -- "$d"
# (c) FIFO .gitignore in a plain untracked directory
d=$(mkfix); mkdir -p "$d/plain"; mkfifo "$d/plain/.gitignore"; printf 'x\n' > "$d/plain/x"
fifo_probe c-plain-dir-fifo "$d"; rm -rf -- "$d"

# ---- gate end-to-end on the FIFO-in-ignored-dir fixture (does the block hang?)
d=$(mkfix); printf 'hidden/\n' >> "$d/.gitignore"; git -C "$d" add .gitignore; git -C "$d" commit -qm gi
mkdir -p "$d/hidden"; mkfifo "$d/hidden/.gitignore"; printf 'x\n' > "$d/hidden/x"
rep=$(mktemp -p "$S/fx" rep.XXXXXX); pre=$(mktemp -p "$S/fx" pre.XXXXXX); printf '## SHONEN p\n' > "$rep"; printf 'p\n' > "$pre"
raw=$(timeout 20 bash "$G/souji-pre-report-gate.sh" --lane "$d" --branch main --report "$rep" --prereg "$pre" 2>&1); rc=$?
printf 'PROBE Y-gate-fifo-ignored-dir rc=%s (124=timeout/hang) %s\n' "$rc" "$(printf '%s\n' "$raw" | grep -E '^(check-clean|detail-clean)' | head -1)"
rm -rf -- "$d" "$rep" "$pre"
