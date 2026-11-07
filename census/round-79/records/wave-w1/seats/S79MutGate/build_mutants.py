#!/usr/bin/env python3
"""S79MutGate: build one-change mutants of the W1 gate (c8c3fbca). Exact-string replacement,
asserting exactly one occurrence; writes mutants/<id>/g/{gate,writer} and a manifest."""
import hashlib
import os
import shutil
import sys

S = "/fast/scratch/hyaku/souji-r79/S79MutGate"
BASE = os.path.join(S, "base", "g")
SRC = os.path.join(BASE, "souji-pre-report-gate.sh")
WRITER = os.path.join(BASE, "souji-receipt-write.py")

MUTANTS = [
    ("M01-drop-group-kill", "drop the process-group kill in the handler",
     '    kill -KILL -- "-$gate_child" 2>/dev/null\n', ''),
    ("M02-drop-pid-kill", "drop the direct pid kill in the handler",
     '    kill -KILL "$gate_child" 2>/dev/null\n', ''),
    ("M03-exit-code-128", "exit 128 fixed instead of 128+signo",
     '  exit $((128 + $2))', '  exit 128'),
    ("M04-no-cleanup-in-handler", "no gate_cleanup call inside the handler",
     "  gate_cleanup\n  printf 'check-signal=FAIL\\n'", "  printf 'check-signal=FAIL\\n'"),
    ("M05-trap-only-TERM", "trap only TERM; INT and HUP untrapped",
     "trap 'gate_on_signal INT 2' INT\ntrap 'gate_on_signal HUP 1' HUP\n", ''),
    ("M06-gate-child-never-set", "gate_child never assigned",
     '  gate_child=$!\n  wait "$gate_child"; rc=$?', '  wait "$gate_child"; rc=$?'),
    ("M07-signal-line-PASS", "handler prints check-signal=PASS",
     "  printf 'check-signal=FAIL\\n'", "  printf 'check-signal=PASS\\n'"),
    ("M08-find-foreground", "the check-4 find call site runs in the foreground again",
     '  gate_run hits "$gate_timeout" find "$top" -path "$top/.git" -prune -o \\( -name .gitignore -o -name .gitattributes \\) \\\n'
     '           ! -xtype f -printf x || return\n',
     '  hits=$(find "$top" -path "$top/.git" -prune -o \\( -name .gitignore -o -name .gitattributes \\) ! -xtype f -printf x) || return\n'),
    ("M09-no-stdin-restore", "gate_run_file drops <&0 (async children read /dev/null)",
     '  if (( merge )); then timeout -k 5 "$secs" "$@" <&0 >"$gate_tmp/o" 2>&1 &\n'
     '  else timeout -k 5 "$secs" "$@" <&0 >"$gate_tmp/o" 2>/dev/null &\n',
     '  if (( merge )); then timeout -k 5 "$secs" "$@" >"$gate_tmp/o" 2>&1 &\n'
     '  else timeout -k 5 "$secs" "$@" >"$gate_tmp/o" 2>/dev/null &\n'),
    ("M10-no-newline-strip", "gate_run keeps trailing newlines (no strip loop)",
     "  while [[ $data == *$'\\n' ]]; do data=${data%$'\\n'}; done\n", ''),
    ("M11-no-reentrancy-guard", "handler does not ignore TERM/INT/HUP while it runs",
     "  trap '' TERM INT HUP\n", ''),
    ("M12-no-exit-trap", "no EXIT trap for gate_cleanup",
     "trap gate_cleanup EXIT\n", ''),
]


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    with open(SRC, "rb") as f:
        base = f.read().decode()
    print(f"base gate sha256={sha(SRC)} bytes={len(base)}")
    man = []
    for mid, desc, old, new in MUTANTS:
        n = base.count(old)
        if n != 1:
            print(f"FATAL {mid}: pattern occurs {n} times", file=sys.stderr)
            return 2
        text = base.replace(old, new, 1)
        if text == base:
            print(f"FATAL {mid}: no change", file=sys.stderr)
            return 2
        d = os.path.join(S, "mutants", mid, "g")
        os.makedirs(d, exist_ok=True)
        gp = os.path.join(d, "souji-pre-report-gate.sh")
        with open(gp, "w", encoding="utf-8") as f:
            f.write(text)
        os.chmod(gp, 0o755)
        shutil.copyfile(WRITER, os.path.join(d, "souji-receipt-write.py"))
        man.append((mid, desc, sha(gp), len(text)))
        print(f"{mid}\tsha256={sha(gp)}\tbytes={len(text)}\t{desc}")
    with open(os.path.join(S, "mutants", "MANIFEST.tsv"), "w", encoding="utf-8") as f:
        f.write("mutant\tsha256\tbytes\tdescription\n")
        for mid, desc, h, n in man:
            f.write(f"{mid}\t{h}\t{n}\t{desc}\n")
    print(f"built {len(man)} mutants")
    return 0


if __name__ == "__main__":
    sys.exit(main())
