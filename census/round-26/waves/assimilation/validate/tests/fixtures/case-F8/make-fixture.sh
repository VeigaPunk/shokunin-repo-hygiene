#!/usr/bin/env bash
# Compat wrapper for the F1–F6 fixture convention: `make-fixture.sh [OUT_DIR]`,
# also accepting the `--out DIR` form. Builds the case into OUT_DIR (default: a
# fresh mktemp -d) by delegating to setup.sh, then prints on stdout the
# F1-shaped JSON contract followed by the lane's FIXTURE_READY marker line.
set -euo pipefail

case_name=F8
target=.scratch/stale-probe-f8.tmp
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

if [ "${1:-}" = "--out" ]; then
  root=${2:?usage: make-fixture.sh [--out] <OUT_DIR>}
elif [ "$#" -ge 1 ]; then
  root=$1
else
  root=$(mktemp -d "${TMPDIR:-/tmp}/souji-fixture-case-$case_name.XXXXXX")
fi

bash "$here/setup.sh" "$root" >&2
root=$(cd -- "$root" && pwd)

printf '{ "case": "%s", "root": "%s", "targets": ["%s/%s"], "expect": [ {"path": "%s/%s", "verdict": "SAFE", "receipt": "stale"} ] }\n' \
  "$case_name" "$root" "$root" "$target" "$root" "$target"
printf 'FIXTURE_READY %s %s/%s\n' "$case_name" "$root" "$target"
