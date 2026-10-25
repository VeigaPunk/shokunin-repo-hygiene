#!/usr/bin/env bash
# Seat S48 assignment name. Runners discover tools/souji-census.impl-48.sh.
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec "$here/souji-census.impl-48.sh" "$@"
