#!/usr/bin/env python3
"""PM3 twin fixture: 25 MB emitted at full speed.
A probe that holds ALL output in memory until EOF (PM3 mutant, since its
cap-kill only SIGKILLs without exiting) must peak in probe RSS; the
pristine probe refuses promptly with exit 2 + FATAL."""
import sys

sys.stdout.write("w" * (25 * 1024 * 1024))
sys.stdout.flush()
print("SUMMARY cases=1 tool_pass=1 before_pass=0", flush=True)
sys.exit(0)
