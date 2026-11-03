#!/usr/bin/env python3
# do-nothing control for C2 (round 57): a gate that always reports clean.
# Committed before any official after receipt. It meets the AFTER target
# (findings=0) by construction and so fails the BEFORE target (findings=1 on
# the r56 receipt), which is why the claim's target is the PAIR of manifests,
# not the after count alone. Also scored by the counter selftest, whose
# control line must read FALSE-GREEN-REJECTED.
print('SUMMARY receipts=0 findings=0')
raise SystemExit(0)
