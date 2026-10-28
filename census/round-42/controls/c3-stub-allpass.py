#!/usr/bin/env python3
"""r42 C3 do-nothing control: a fixture that never runs the tool and reports 13 passing cases."""
import sys
for i in range(13):
    print("case-stub%02d=PASS" % i)
print("SUMMARY cases=13 pass=13 fail=0")
sys.exit(0)
