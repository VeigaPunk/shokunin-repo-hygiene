#!/usr/bin/env bash
# S76Sentinel: adversarial probes for the r76 W gate block (e827d2bf, check 4 ignore-source attribution).
# Read-only wrt the lane: every fixture lives under $S (scratch). Run: bash w-gate-probes.sh <route>
set -u
S=${S:-/fast/scratch/hyaku/souji-r76/S76Sentinel}
G=$S/G
REP=$S/report.md
PRE=$S/prereg.txt
printf '## SHONEN\nx\n' >"$REP"
printf 'prereg body\n' >"$PRE"

mkfx() { # fresh fixture repo at $S/fx.XXXXXX ; prints its path
  local d
  d=$(mktemp -d -p "$S" fx.XXXXXX) || return 1
  [ -n "$d" ] && [ -d "$d" ] || { echo "EMPTY-FIXTURE-PATH" >&2; exit 1; }
  git -C "$d" init -q || exit 1
  [ "$(git -C "$d" rev-parse --show-toplevel)" = "$d" ] || { echo "FIXTURE-TOPLEVEL-MISMATCH $d" >&2; exit 1; }
  printf 'base\n' >"$d/README.md"
  printf '__pycache__/\n' >"$d/.gitignore"
  mkdir -p "$d/sub" "$d/logs"
  printf '*.log\n' >"$d/logs/.gitignore"
  printf 'x\n' >"$d/sub/keep.txt"
  git -C "$d" -c user.name=fx -c user.email=fx@fx add -A || exit 1
  git -C "$d" -c user.name=fx -c user.email=fx@fx commit -q -m base || exit 1
  echo "$d"
}

run_gate() { # $1 = lane ; prints check-clean + detail-clean
  local lane=$1 out rc
  out=$(bash "$G/souji-pre-report-gate.sh" --lane "$lane" --branch main \
        --report "$REP" --prereg "$PRE" 2>&1)
  rc=$?
  printf '%s\n' "$out" | grep -E '^check-(clean|tip|report|prereg)=|^detail-clean:' | sed 's/^/    /'
  printf '    gate-rc=%s\n' "$rc"
}

case ${1:-} in
honest)
  d=$(mkfx); echo "ROUTE honest fixture=$d"; run_gate "$d" ;;
f7-selfignore-dir)
  d=$(mkfx); mkdir -p "$d/cache"
  printf '*\n' >"$d/cache/.gitignore"; printf 'payload\n' >"$d/cache/payload.bin"
  echo "ROUTE f7-selfignore-dir fixture=$d"; run_gate "$d" ;;
f2-committed-broad)
  d=$(mkfx); printf '*\n' >>"$d/.gitignore"; git -C "$d" -c user.name=fx -c user.email=fx@fx commit -qam broad
  mkdir -p "$d/anything"; printf 'payload\n' >"$d/anything/payload.bin"
  echo "ROUTE f2-committed-broad fixture=$d"; run_gate "$d" ;;
symlink-gitignore) # tracked .gitignore is a symlink to untracked rule bytes
  d=$(mkfx)
  rm -f "$d/.gitignore"; printf 'rules.txt\npayload.txt\n' >"$d/rules.txt"
  ln -s rules.txt "$d/.gitignore"
  git -C "$d" -c user.name=fx -c user.email=fx@fx add .gitignore || exit 1
  git -C "$d" -c user.name=fx -c user.email=fx@fx commit -q -m symlink-gitignore || exit 1
  printf 'payload\n' >"$d/payload.txt"
  echo "ROUTE symlink-gitignore fixture=$d"
  echo "  git status (empty means hidden):"
  git -C "$d" --no-optional-locks status --porcelain=v1 --untracked-files=all | sed 's/^/    /'
  echo "  ignored-listing:"
  git -C "$d" ls-files -z --others --ignored --exclude-standard | tr '\0' '\n' | sed 's/^/    /'
  run_gate "$d" ;;
nested-untracked) # untracked sub2/.gitignore (dir sub2 untracked) hiding a file
  d=$(mkfx); mkdir -p "$d/sub2"
  printf '/.gitignore\n/new.txt\n' >"$d/sub2/.gitignore"; printf 'h\n' >"$d/sub2/new.txt"
  echo "ROUTE nested-untracked fixture=$d"; run_gate "$d" ;;
untracked-in-tracked-dir) # the f14 shape
  d=$(mkfx)
  printf '/.gitignore\n/new.txt\n' >"$d/sub/.gitignore"; printf 'h\n' >"$d/sub/new.txt"
  printf 'h\n' >"$d/logs/x.log"
  echo "ROUTE untracked-in-tracked-dir fixture=$d"; run_gate "$d" ;;
repo-local-excludesfile) # repo-local core.excludesFile (no -c override on the listing)
  d=$(mkfx); printf 'hidden.bin\n' >"$d/excl"; git -C "$d" config core.excludesFile "$d/excl"
  printf 'h\n' >"$d/hidden.bin"
  echo "ROUTE repo-local-excludesfile fixture=$d"; run_gate "$d" ;;
info-exclude)
  d=$(mkfx); printf 'hidden.bin\n' >"$d/.git/info/exclude"; printf 'h\n' >"$d/hidden.bin"
  echo "ROUTE info-exclude fixture=$d"; run_gate "$d" ;;
ansi-name) # payload hidden behind an untracked self-ignoring dir named with ESC bytes
  d=$(mkfx); mkdir -p "$d/cache"
  printf '*\n' >"$d/cache/.gitignore"
  n=$(printf 'esc\033[31mred\033[0m.bin'); printf 'h\n' >"$d/cache/$n"
  n2=$(printf 'nl\nname.bin'); printf 'h\n' >"$d/cache/$n2"
  echo "ROUTE ansi-name fixture=$d"; run_gate "$d"
  echo "  path echo check: grep for the raw name in gate output:"
  bash "$G/souji-pre-report-gate.sh" --lane "$d" --branch main --report "$REP" --prereg "$PRE" 2>&1 \
    | LC_ALL=C grep -c 'red' || echo '    0 raw-name occurrences (good)' ;;
embedded-repo) # untracked embedded git repo inside an ignored/untracked area
  d=$(mkfx); mkdir -p "$d/emb"; git -C "$d/emb" init -q; git -C "$d" -c user.name=fx -c user.email=fx@fx add -A >/dev/null 2>&1
  printf 'ign\n' >>"$d/.gitignore"
  echo "ROUTE embedded-repo fixture=$d"
  git -C "$d" ls-files -z --others --ignored --exclude-standard | tr '\0' '\n' | sed 's/^/    ign=/' ;;
*) echo "unknown route ${1:-}" >&2; exit 2 ;;
esac
