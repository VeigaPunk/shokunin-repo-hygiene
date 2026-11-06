#!/usr/bin/env python3
"""Build single-edit mutants of the r74 stage-W gate check 4 and of _truth_refusal in the writer."""
import os
import shutil
import sys

S = "/fast/scratch/hyaku/souji-r74/S74MutGate"
GATE = open(os.path.join(S, "gate-orig.sh"), "rb").read().decode()
WRITER = open(os.path.join(S, "writer-orig.py"), "rb").read().decode()
M = os.path.join(S, "m")

BLOCK = '''  elif truth=$(python3 -B - "$gate_dir/souji-receipt-write.py" "$lane" 2>&1 <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("souji_receipt_write", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
msg = mod._truth_refusal(sys.argv[2])
if msg:
    print(msg)
    sys.exit(1)
PY
  ); then check clean PASS
  else check clean FAIL; printf 'detail-clean: byte truth: %s\\n' "${truth:-no output}" >&2; fi'''

PYBODY = '''import importlib.util, sys
spec = importlib.util.spec_from_file_location("souji_receipt_write", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
msg = mod._truth_refusal(sys.argv[2])
if msg:
    print(msg)
    sys.exit(1)
'''

GATE_MUTS = {
    "G01_drop_truth_call": (BLOCK, "  else check clean PASS; fi"),
    "G02_ignore_python_rc": ('''  ); then check clean PASS
  else check clean FAIL; printf 'detail-clean: byte truth: %s\\n' "${truth:-no output}" >&2; fi''',
                             '''  ); then check clean PASS
  else check clean PASS; fi'''),
    "G03_invert_msg": ("if msg:\n    print(msg)", "if not msg:\n    print(msg)"),
    "G04_import_lane_writer": ('"$gate_dir/souji-receipt-write.py"', '"$lane/tools/souji-receipt-write.py"'),
    "G05_import_cwd_writer": ('"$gate_dir/souji-receipt-write.py"', '"$PWD/tools/souji-receipt-write.py"'),
    "G06_swallow_exceptions": ("spec.loader.exec_module(mod)\nmsg = mod._truth_refusal(sys.argv[2])",
                               "try:\n    spec.loader.exec_module(mod)\n    msg = mod._truth_refusal(sys.argv[2])\nexcept BaseException:\n    sys.exit(0)"),
    "G07_first_status_line": ("if [[ -n $status ]]; then check clean FAIL",
                              "if [[ -n ${status%%$'\\n'*} ]]; then check clean FAIL"),
    "G08_invert_status_test": ("if [[ -n $status ]]; then check clean FAIL", "if [[ -z $status ]]; then check clean FAIL"),
    "G09_truth_fail_prints_pass": ('''  else check clean FAIL; printf 'detail-clean: byte truth: %s\\n' "${truth:-no output}" >&2; fi''',
                                   '''  else check clean PASS; printf 'detail-clean: byte truth: %s\\n' "${truth:-no output}" >&2; fi'''),
    "G10_gate_dir_dot": ('gate_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || gate_dir=', 'gate_dir=.'),
    "G11_empty_heredoc": (PYBODY, ""),
}

SYM = '''        if mode == b"120000":
            if not os.path.islink(full):
                bad.append(path)
                continue
            target = os.readlink(full)
            h = hashlib.new(algo, b"blob %d\\0" % len(target) + target).hexdigest().encode()
            if h != oid:
                bad.append(path)'''
WRITER_MUTS = {
    "W01_skip_symlink": (SYM, '        if mode == b"120000":\n            continue'),
    "W02_trust_matching_size": ("        else:\n            files.append((path, oid))",
                                '        else:\n            if os.path.getsize(full) == int(git(top, "cat-file", "-s", oid.decode("ascii")).stdout or b"-1"):\n                continue\n            files.append((path, oid))'),
    "W03_missing_is_clean": ("        if not os.path.lexists(full):\n            bad.append(path)\n            continue",
                             "        if not os.path.lexists(full):\n            continue"),
    "W04_eq_eq": ("if h != oid)", "if h == oid)"),
}


def apply(text, old, new, tag):
    n = text.count(old)
    if n != 1:
        sys.exit(f"BAD SEARCH {tag}: count={n}")
    return text.replace(old, new, 1)


shutil.rmtree(M, ignore_errors=True)
os.makedirs(M)
made = []
for mid, (old, new) in GATE_MUTS.items():
    d = os.path.join(M, mid)
    os.makedirs(d)
    open(os.path.join(d, "gate.sh"), "w", encoding="utf-8").write(apply(GATE, old, new, mid))
    shutil.copyfile(os.path.join(S, "writer-orig.py"), os.path.join(d, "souji-receipt-write.py"))
    made.append(mid)
for mid, (old, new) in WRITER_MUTS.items():
    d = os.path.join(M, mid)
    os.makedirs(d)
    shutil.copyfile(os.path.join(S, "gate-orig.sh"), os.path.join(d, "gate.sh"))
    open(os.path.join(d, "souji-receipt-write.py"), "w", encoding="utf-8").write(apply(WRITER, old, new, mid))
    made.append(mid)
# pristine baseline and lane-base control
d = os.path.join(M, "B00_pristine")
os.makedirs(d)
shutil.copyfile(os.path.join(S, "gate-orig.sh"), os.path.join(d, "gate.sh"))
shutil.copyfile(os.path.join(S, "writer-orig.py"), os.path.join(d, "souji-receipt-write.py"))
open(os.path.join(S, "gate-base.sh"), "wb").write(
    __import__("subprocess").run(["git", "-C", "/home/vgpnk/Projects/shokunin/souji-shokunin",
                                  "show", "43cd74bba84bb498b57a74377ccb0567d10864d5:tools/souji-pre-report-gate.sh"],
                                 check=True, stdout=-1).stdout)
d = os.path.join(M, "B01_base_gate")
os.makedirs(d)
shutil.copyfile(os.path.join(S, "gate-base.sh"), os.path.join(d, "gate.sh"))
shutil.copyfile(os.path.join(S, "writer-orig.py"), os.path.join(d, "souji-receipt-write.py"))
print("\n".join(made + ["B00_pristine", "B01_base_gate"]))
