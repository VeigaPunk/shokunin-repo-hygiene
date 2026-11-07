#!/bin/bash
# hang stub: record pid/parent/args, then sleep far past the test window
printf '%s\t%s\t%s\n' "$$" "$PPID" "$*" >> "$SOUJI_S80_STUB_LOG"
exec sleep 600
