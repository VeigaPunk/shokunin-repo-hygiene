#!/usr/bin/env python3
"""souji r72 C2: build the five frozen writer mutants (battery members) from the writer at the round
base 0bf098dde7e6eafb62a9ce62b7c16a6291ee1e8e (tools/souji-receipt-write.py, sha256 b7790001...244d).
Each member is ONE exact single-occurrence string edit (count asserted == 1). The edits re-express
the r71 seat mutants S71MutWriter W3/W4/W5/W8 (census/round-71/records/wave-w1/seats/S71MutWriter.md)
on the repaired writer, plus WM6, the reverse of the r71 S71Reviewer F1 repair (value exemption).
Writes census/round-72/battery/{WM3,WM4,WM5,WM6,WM8}.py, SHA256SUMS and census/round-72/battery-manifest.tsv.
Usage (from the lane root): python3 -B census/round-72/make-battery.py"""
import hashlib, subprocess, sys
BASE = "0bf098dde7e6eafb62a9ce62b7c16a6291ee1e8e"
src = subprocess.run(["git", "show", f"{BASE}:tools/souji-receipt-write.py"], check=True,
                     capture_output=True).stdout.decode("utf-8")
assert hashlib.sha256(src.encode()).hexdigest().startswith("b7790001"), "unexpected writer bytes"
EDITS = [
    ("WM3", "pre-run witness refusal deleted (S71MutWriter W3)",
     "    pre_msg = _witness_refusal(top)\n    if pre_msg:\n        refuse(pre_msg)\n",
     "    pre_msg = None\n"),
    ("WM4", "post-run witness refusal deleted (S71MutWriter W4)",
     "    post_msg = _witness_refusal(top)\n    if post_msg:\n        refuse(post_msg)\n",
     "    post_msg = None\n"),
    ("WM5", "process drivers no longer looked up (S71MutWriter W5)",
     '        for key in ("clean", "process"):\n', '        for key in ("clean",):\n'),
    ("WM6", "boolean-state filter values exempted again (reverse of the r71 S71Reviewer F1 repair; S71MutWriter W6)",
     "    for val in sorted(values):\n",
     '    for val in sorted(values - {b"set", b"unset", b"unspecified"}):\n'),
    ("WM8", "check-attr reads index attributes only (S71MutWriter W8)",
     '    ca = git(top, "check-attr", "--stdin", "-z", *WITNESS_ATTRS, input=ls.stdout)\n',
     '    ca = git(top, "check-attr", "--cached", "--stdin", "-z", *WITNESS_ATTRS, input=ls.stdout)\n'),
]
sums, man = [], ["mutant\texpected_outcome"]
for name, desc, old, new in EDITS:
    n = src.count(old)
    if n != 1:
        sys.exit(f"{name}: anchor count {n} != 1")
    data = src.replace(old, new, 1).encode("utf-8")
    with open(f"census/round-72/battery/{name}.py", "wb") as f:
        f.write(data)
    sums.append(f"{hashlib.sha256(data).hexdigest()}  {name}.py")
    man.append(f"{name}\tforgery")
    print(f"{name} sha256={hashlib.sha256(data).hexdigest()} desc={desc}")
open("census/round-72/battery/SHA256SUMS", "w").write("\n".join(sums) + "\n")
open("census/round-72/battery-manifest.tsv", "w").write("\n".join(man) + "\n")
