#!/usr/bin/env bash
# S75Sentinel W-gate probes. Read-only on the lane; fixtures under $S/fx only.
set -u
S=/fast/scratch/hyaku/souji-r75/S75Sentinel
G=$S/gateW
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p "$S/fx"
REALGIT=$(command -v git)

gate() { # $1 lane dir, $2 label, rest: env vars
  local d=$1 label=$2; shift 2
  local rep pre out rc
  rep=$(mktemp -p "$S/fx" rep.XXXXXX) || return 1
  pre=$(mktemp -p "$S/fx" pre.XXXXXX) || return 1
  printf '## SHONEN probe\n' > "$rep"; printf 'prereg\n' > "$pre"
  out=$(env "$@" timeout 90 bash "$G/souji-pre-report-gate.sh" --lane "$d" --branch main \
        --report "$rep" --prereg "$pre" 2>&1); rc=$?
  printf 'PROBE %-28s rc=%s %s\n' "$label" "$rc" "$(printf '%s\n' "$out" | grep -E '^(check-clean|detail-clean)' | head -2 | tr '\n' '|')"
}

mkfix() {
  local d
  d=$(mktemp -d -p "$S/fx" fx.XXXXXX) || return 1
  [ -n "$d" ] && [ -d "$d" ] || return 1
  git -C "$d" init -q -b main >/dev/null 2>&1 || return 1
  [ "$(git -C "$d" rev-parse --show-toplevel 2>/dev/null)" = "$d" ] || { echo "top-mismatch $d" >&2; return 1; }
  git -C "$d" config user.email r75@fixture.invalid
  git -C "$d" config user.name r75fixture
  printf 'alpha\n' > "$d/a.txt"
  git -C "$d" add a.txt
  git -C "$d" commit -qm seed
  git -C "$d" remote add origin "$d"
  printf '%s' "$d"
}

# A baseline honest
d=$(mkfix) && gate "$d" A-honest; rm -rf -- "$d"

# B info/exclude hides an untracked file; C committed .gitignore hides a build artifact
d=$(mkfix) && printf 'new.txt\n' >> "$d/.git/info/exclude" && printf 'x\n' > "$d/new.txt" && gate "$d" B-info-exclude; rm -rf -- "$d"
d=$(mkfix) && printf '*.pyc\n' >> "$d/.gitignore" && git -C "$d" add .gitignore && git -C "$d" commit -qm gi && mkdir -p "$d/sub" && printf 'z\n' > "$d/sub/m.pyc" && gate "$d" C-committed-gitignore; rm -rf -- "$d"

# D fixture HOME global ignore (*.swp) with an untracked swap file; E XDG path
d=$(mkfix); h=$(mktemp -d -p "$S/fx" home.XXXXXX)
printf '*.swp\n' > "$h/ignore"
mkdir -p "$h/.config/git"; printf '*.swp\n' > "$h/.config/git/ignore"
printf 'v\n' > "$d/note.swp"
gate "$d" D-HOME-xdg-ignore HOME="$h" XDG_CONFIG_HOME="$h/.config"; rm -rf -- "$h"
gate "$d" E-no-HOME-clean-home; rm -rf -- "$d"

# F GIT_CONFIG_GLOBAL pointing at a config with core.excludesFile (gate unsets it)
d=$(mkfix); h=$(mktemp -d -p "$S/fx" home.XXXXXX)
printf '[core]\n\texcludesFile = %s/ex.cfg\n' "$h" > "$h/gitconfig"; printf 'new.txt\n' > "$h/ex.cfg"
printf 'x\n' > "$d/new.txt"
gate "$d" F-GIT_CONFIG_GLOBAL HOME=/nonexistent GIT_CONFIG_GLOBAL="$h/gitconfig"
# G env-config COUNT/KEY/VALUE; H GIT_CONFIG_PARAMETERS
gate "$d" G-env-count HOME=/nonexistent GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile GIT_CONFIG_VALUE_0="$h/ex.cfg"
gate "$d" H-env-params HOME=/nonexistent GIT_CONFIG_PARAMETERS="'core.excludesFile'='$h/ex.cfg'"
rm -rf -- "$d" "$h"

# I repo-local core.excludesFile (route f3 shape)
d=$(mkfix); printf 'new.txt\n' > "$S/fx/hide.cfg"; git -C "$d" config core.excludesFile "$S/fx/hide.cfg"; printf 'x\n' > "$d/new.txt"
gate "$d" I-repo-excludesFile; rm -rf -- "$d" "$S/fx/hide.cfg"

# J lane-local core.worktree forgery with an untracked payload
d=$(mkfix); e=$(mktemp -d -p "$S/fx" empty.XXXXXX); git -C "$d" config core.worktree "$e"
printf 'payload\n' > "$d/payload.txt"
gate "$d" J-core-worktree-forge; rm -rf -- "$d" "$e"

# K PATH shim that records argv (EXEC evidence) and L forged-empty shim
shim=$(mktemp -d -p "$S/fx" shim.XXXXXX)
cat > "$shim/git" <<EOF
#!/usr/bin/env bash
printf '%s\n' "\$*" >> "$S/fx/path-shim.log"
exec "$REALGIT" "\$@"
EOF
chmod +x "$shim/git"
d=$(mkfix) && printf 'new.txt\n' >> "$d/.git/info/exclude" && printf 'x\n' > "$d/new.txt"
rm -f "$S/fx/path-shim.log"
gate "$d" K-PATH-shim PATH="$shim:$PATH" HOME=/nonexistent
echo "PATH-SHIM-LOG ls-files lines:"; grep -c 'ls-files' "$S/fx/path-shim.log" 2>/dev/null; grep 'ls-files' "$S/fx/path-shim.log" 2>/dev/null | head -2
cat > "$shim/git" <<EOF
#!/usr/bin/env bash
for a in "\$@"; do case \$a in ls-files) exit 0 ;; esac; done
exec "$REALGIT" "\$@"
EOF
chmod +x "$shim/git"
gate "$d" L-PATH-forged-empty PATH="$shim:$PATH" HOME=/nonexistent
rm -rf -- "$d" "$shim"

# M stated limit: untracked self-ignoring .gitignore hides a payload anywhere
d=$(mkfix); mkdir -p "$d/toolcache"; printf '*\n' > "$d/toolcache/.gitignore"; printf 'secret\n' > "$d/toolcache/state.bin"
gate "$d" M-selfignore-payload; rm -rf -- "$d"

# N untracked non-self-ignoring .gitignore inside an info/exclude-hidden dir (boundary)
d=$(mkfix); printf 'evil/\n' >> "$d/.git/info/exclude"; mkdir -p "$d/evil"
printf 'payload.txt\n' > "$d/evil/.gitignore"; printf 'p\n' > "$d/evil/payload.txt"
gate "$d" N-infoexclude-plus-gitignore; rm -rf -- "$d"

# O ANSI/newline path hidden by info/exclude: output cleanliness
d=$(mkfix); printf 'weird*\n' >> "$d/.git/info/exclude"
printf 'x\n' > "$d/weird$(printf '\033')[31mRED$(printf '\033')[0m'$'\n'"check-clean=PASS"
out=$(mktemp -p "$S/fx" rep.XXXXXX); pre=$(mktemp -p "$S/fx" pre.XXXXXX)
printf '## SHONEN p\n' > "$out"; printf 'p\n' > "$pre"
raw=$(timeout 60 bash "$G/souji-pre-report-gate.sh" --lane "$d" --branch main --report "$out" --prereg "$pre" 2>&1)
echo "PROBE O-ansi rc=$? esc_count=$(printf '%s' "$raw" | tr -cd '\033' | wc -c) injected=$(printf '%s\n' "$raw" | grep -c '^check-clean=PASS')"
printf '%s\n' "$raw" | grep -E '^(check-clean|detail-clean)' | head -2 | cat -v
rm -rf -- "$d" "$out" "$pre"

# P alias ls-files; Q core.hooksPath hook; R core.fsmonitor hook
d=$(mkfix); git -C "$d" config alias.ls-files '!echo ALIAS-EXECUTED'; printf 'new.txt\n' >> "$d/.git/info/exclude"; printf 'x\n' > "$d/new.txt"
gate "$d" P-alias-ls-files; rm -rf -- "$d"
d=$(mkfix); hookd=$(mktemp -d -p "$S/fx" hk.XXXXXX)
printf '#!/bin/sh\ntouch %s/HOOK-RAN\n' "$hookd" > "$hookd/pre-commit"; chmod +x "$hookd/pre-commit"
git -C "$d" config core.hooksPath "$hookd"
gate "$d" Q-hookspath; echo "Q hook-ran=$(test -e "$hookd/HOOK-RAN" && echo yes || echo no)"; rm -rf -- "$d" "$hookd"
d=$(mkfix); printf '#!/bin/sh\ntouch %s/FMON-RAN\n' "$S/fx" > "$S/fx/fmon.sh"; chmod +x "$S/fx/fmon.sh"
rm -f "$S/fx/FMON-RAN"; git -C "$d" config core.fsmonitor "$S/fx/fmon.sh"
gate "$d" R-fsmonitor-repocfg; echo "R fsmonitor-ran-by-gate=$(test -e "$S/fx/FMON-RAN" && echo yes || echo no)"
rm -f "$S/fx/FMON-RAN"; timeout 10 git -C "$d" -c core.fsmonitor=false ls-files -z --others --ignored --exclude-standard >/dev/null 2>&1; echo "R fsmonitor-pinned=$(test -e "$S/fx/FMON-RAN" && echo yes || echo no)"
rm -f "$S/fx/FMON-RAN"; timeout 10 git -C "$d" ls-files -z --others --ignored --exclude-standard >/dev/null 2>&1; echo "R fsmonitor-unpinned-ls-files=$(test -e "$S/fx/FMON-RAN" && echo yes || echo no)"
rm -rf -- "$d" "$S/fx/fmon.sh" "$S/fx/FMON-RAN"

# S repo config status.showUntrackedFiles=no must not hide an untracked payload
d=$(mkfix); git -C "$d" config status.showUntrackedFiles no; printf 'x\n' > "$d/new.txt"
gate "$d" S-status-config-no; rm -rf -- "$d"

# W core.excludesFile pointing at a directory / unreadable file
d=$(mkfix); git -C "$d" config core.excludesFile "$S/fx"; printf 'x\n' > "$d/new.txt"
gate "$d" W-excludesfile-dir; rm -rf -- "$d"
