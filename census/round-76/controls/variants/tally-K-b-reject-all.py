#!/usr/bin/env python3
"""souji r76 C2 control K-b (blanket): a tally that rejects every receipt set. Same CLI as
census/round-75/c2-kill-counter.py; prints a SUMMARY line and exits 1 always."""
import sys
print("SUMMARY mutants=0 killed=0 survived=0 unread=0 pristine=FAIL blanket=REJECT-ALL")
sys.exit(1)
