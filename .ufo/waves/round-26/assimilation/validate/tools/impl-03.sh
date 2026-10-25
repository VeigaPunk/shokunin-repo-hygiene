#!/usr/bin/env bash
# Seat S03 round-8 assignment name. Runners discover
# tools/souji-quarantine.impl-03.sh.
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec "$here/souji-quarantine.impl-03.sh" "$@"
