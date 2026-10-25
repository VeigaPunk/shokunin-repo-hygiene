#!/usr/bin/env bash
# Build the cand-g1-* candidates from the installed S17-patched tools.
#
# Each candidate is the installed tool verbatim with one splice: the cluster-G
# guard is sourced after the tool's function definitions and before its main
# dispatch. The guard's own cases are injected into the inherited selftest so
# they share the same pass/fail accounting and summary line.
set -euo pipefail

HERE=$(cd -- "$(dirname -- "$BASH_SOURCE[0]")" && pwd -P)
GUARD="$HERE/cand-g1-guard.sh"
[ -f "$GUARD" ] || { printf 'missing %s\n' "$GUARD" >&2; exit 1; }

build() { # $1 installed basename, $2 kind, $3 output basename
  local src=$HERE/$1 kind=$2 out=$HERE/$3
  [ -f "$src" ] || { printf 'missing %s\n' "$src" >&2; exit 1; }
  python3 - "$src" "$kind" "$out" <<'PY'
import sys
from pathlib import Path

src, kind, out = sys.argv[1], sys.argv[2], sys.argv[3]
text = Path(src).read_text()
guard_ref = 'cand-g1-guard.sh'
assert guard_ref not in text, 'already spliced'

sel_line = 'if [ "$SELFTEST" = 1 ]; then run_selftest; fi'
sel_multi = 'if [ "$SELFTEST" = 1 ]; then\n  run_selftest || exit 1\n  exit 0\nfi'
if text.count(sel_line) == 1:
    anchor, replacement = sel_line, sel_line
elif text.count(sel_multi) == 1:
    anchor, replacement = sel_multi, sel_multi
else:
    raise SystemExit('selftest dispatch not found exactly once')

prelude = (
    f'CAND_G1_KIND={kind}\n'
    f'CAND_G1_GUARD="$SCRIPT_DIR/{guard_ref}"\n'
    'if [ -f "$CAND_G1_GUARD" ]; then\n'
    '  . "$CAND_G1_GUARD"\n'
    'else\n'
    f'  printf "souji: missing {guard_ref} (ship it beside this tool)\\n" >&2\n'
    '  exit 1\n'
    'fi\n'
)
text = text.replace(anchor, prelude + replacement, 1)

# Inject the guard cases immediately before the selftest summary line.
marker = '  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"'
assert text.count(marker) == 1, 'selftest summary not found exactly once'
text = text.replace(marker, '  cand_g1_selftest\n  cand_g2_selftest\n' + marker, 1)

# Quarantine's guard wraps emit/second_check, both defined before the splice
# point, so the inherited definitions are renamed and the guard supplies the
# live names (each wrapper calls its renamed base).
if kind == 'quarantine':
    for name in ('emit', 'second_check'):
        defn = f'{name}() {{'
        assert text.count(defn) == 1, f'{name} definition not found once'
        text = text.replace(defn, f'cand_base_{name}() {{', 1)

Path(out).write_text(text)
print('built', out)
PY
  chmod +x "$out"
  bash -n "$out" || { printf 'syntax error in %s\n' "$out" >&2; exit 1; }
}

build souji-verify.sh verify cand-g1-verify.sh
build souji-vault-verify.sh vault cand-g1-vault.sh
build souji-census.sh census cand-g1-census.sh
build souji-quarantine.sh quarantine cand-g1-quarantine.sh

printf 'done\n'
