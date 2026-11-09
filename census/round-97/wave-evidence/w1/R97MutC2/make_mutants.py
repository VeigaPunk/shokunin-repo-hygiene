#!/usr/bin/env python3
"""Generate one-edit mutants (probe + counter) under scratch/mutants/; print sha256 for each."""
import hashlib, os, sys

SC = "/fast/scratch/hyaku/souji-r97/R97MutC2"
LC = "/home/vgpnk/Projects/shokunin/souji-shokunin"

def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def mutate(src, old, new, name):
    n = src.count(old)
    assert n == 1, f"{name}: target occurs {n} times:\n{old!r}"
    return src.replace(old, new, 1)

probe_path = f"{LC}/census/round-97/c2-forgery-probe.py"
counter_path = f"{LC}/census/round-97/c2-setup-arms.py"
probe_src = load(probe_path)
counter_src = load(counter_path)

P = f"{SC}/mutants/probe"
C = f"{SC}/mutants/counter"
os.makedirs(P, exist_ok=True)
os.makedirs(C, exist_ok=True)

probe_mutants = {
    # PM1: returncode-wait -> pipe-EOF wait (communicate) after group kill
    "PM1-prc-wait": ("    p.wait()", "    p.communicate()"),
    # PM2: timeout branch killpg dropped
    "PM2-no-timeout-killpg": (
        "            try:\n"
        "                os.killpg(p.pid, signal.SIGKILL)\n"
        "            except ProcessLookupError:\n"
        "                pass\n"
        "            break",
        "            break",
    ),
    # PM3: over-cap Fatal not raised
    "PM3-no-overcap-fatal": (
        '                raise Fatal(f"{label} exceeded --max-output {max_output} bytes; its process group was killed")',
        "                pass",
    ),
    # PM4: Fatal handler returns verdict 1
    "PM4-fatal-as-verdict": ("    except Fatal as exc:", "    except Fatal as exc:\n        return 1"),
    # PM5: cli() OSError handler returns verdict 1 (unique two-line anchor)
    "PM5-oserror-as-verdict": (
        '    except OSError as exc:\n        print(f"C2-FORGERY-FATAL: I/O error: {exc}", file=sys.stderr)',
        '    except OSError as exc:\n        return 1\n        print(f"C2-FORGERY-FATAL: I/O error: {exc}", file=sys.stderr)',
    ),
    # PM6: --timeout <= 0 -> < 0
    "PM6-timeout-check": ("    if ns.timeout <= 0:", "    if ns.timeout < 0:"),
    # PM7: drop p.wait()
    "PM7-drop-pwait": ("    p.wait()", ""),
    # PM8: output total never accumulated
    "PM8-no-total-accum": ("            total += len(chunk)", "            pass"),
    # PM10: cli() generic-internal-error handler returns verdict 1
    "PM10-internal-as-verdict": (
        "    except Exception as exc:  # an internal error is not a verdict: never exit 1 for it\n        print(f\"C2-FORGERY-FATAL: internal error {type(exc).__name__}: {exc}\", file=sys.stderr)",
        "    except Exception as exc:  # an internal error is not a verdict: never exit 1 for it\n        return 1\n        print(f\"C2-FORGERY-FATAL: internal error {type(exc).__name__}: {exc}\", file=sys.stderr)",
    ),
    # PM11: timeout-branch killpg -> kill (process, not group); first occurrence only in the timeout branch
    "PM11-kill-not-killpg": (
        "            try:\n                os.killpg(p.pid, signal.SIGKILL)\n            except ProcessLookupError:\n                pass\n            break",
        "            try:\n                os.kill(p.pid, signal.SIGKILL)\n            except ProcessLookupError:\n                pass\n            break",
    ),
    # PM9: Fatal print loses stderr stream
    "PM9-fatal-wrong-stream": (
        '        print(f"C2-FORGERY-FATAL: {exc}", file=sys.stderr)',
        '        print(f"C2-FORGERY-FATAL: {exc}")',
    ),
}

counter_mutants = {
    # CM1: T1 reap ignores before-snapshot (identity set)
    "CM1-reap-ignores-before": (
        "                if st is None or (pid, st, boot) in before:",
        "                if st is None or (pid, st, boot) in set():",
    ),
    # CM2: T1 reap kill -> pass (counter never reaps; counting stays honest)
    "CM2-no-reap": ("                    os.kill(pid, signal.SIGKILL)", "                    pass"),
    # CM3: stream selection always stdout
    "CM3-stream-stdout": ("        stream = se if line == FATAL else so", "        stream = so"),
    # CM4: arm-timeout default 300 -> 17
    "CM4-armtimeout-17": (
        '    ap.add_argument("--arm-timeout", type=int, default=300)',
        '    ap.add_argument("--arm-timeout", type=int, default=17)',
    ),
    # CM5: T3 want inverted
    "CM5-T3-want-inverted": (
        '        ("T3", fpass, tool, before, a("T3"), 2, FATAL),',
        '        ("T3", fpass, tool, before, a("T3"), 0, PASS8),',
    ),
    # CM6: stream selection always stderr
    "CM6-stream-stderr": ("        stream = se if line == FATAL else so", "        stream = se"),
    # CM7: T1 reap matches by substring, not exact token
    "CM7-reap-substring": (
        "                if not any(x == fx.encode() for x in argv):",
        "                if not any(fx.encode() in x for x in argv):",
    ),
    # CM8: conform and -> or
    "CM8-conform-or": ("        ok = rc == want and has", "        ok = rc == want or has"),
}

def emit(base_src, mutants, dest, label):
    for name, (old, new) in mutants.items():
        out = mutate(base_src, old, new, name)
        out_path = f"{dest}/{name}.py"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"{label} {name}: {out_path} sha256={sha(out_path)}")

print(f"pristine probe   sha256={sha(probe_path)}")
print(f"pristine counter sha256={sha(counter_path)}")
emit(probe_src, probe_mutants, P, "PROBE-MUTANT")
emit(counter_src, counter_mutants, C, "COUNTER-MUTANT")
