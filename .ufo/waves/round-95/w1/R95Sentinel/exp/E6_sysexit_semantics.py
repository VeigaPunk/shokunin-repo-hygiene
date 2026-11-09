#!/usr/bin/env python3
"""E6: what the sentinel's SystemExit leg does to ordinary SystemExit semantics.

Cases (each a separate main script run with the frozen hook on PYTHONPATH):
  A  sys.exit(main()) at module level, main returns 1        -> declared exit, status 1
  B  def main(): sys.exit(2); sys.exit(main())              -> raised inside a main-script function
  C  helper raises SystemExit(3), caught at module level      -> reached the main script's top level
  D  helper raises SystemExit(3), caught inside the helper    -> never reached the top level
  E  helper in an IMPORTED module raises SystemExit(4)       -> raised outside the main script
  F  helper raises SystemExit(5) (unhandled), then the script
     catches it at module level and exits 0                    -> sticky foreign flag?
  G  two SystemExits: an unhandled one from a helper, then a
     module-level sys.exit(0) in a try/except                 -> sticky foreign flag?
"""
import os
import subprocess
import sys
import time

PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))

CASES = {
    "A module-level sys.exit(main())": """import sys
def main():
    return 1
sys.exit(main())
""",
    "B sys.exit inside main()": """import sys
def main():
    sys.exit(2)
sys.exit(main())
""",
    "C helper raises, caught at module level": """import sys
def helper():
    raise SystemExit(3)
try:
    helper()
except SystemExit:
    pass
sys.exit(0)
""",
    "D helper raises, caught inside helper": """import sys
def helper():
    try:
        raise SystemExit(3)
    except SystemExit:
        pass
    return 0
sys.exit(helper())
""",
    "E imported module raises": """import sys
import helper_mod
sys.exit(0)
""",
    "F unhandled-in-helper then caught at module": """import sys
def helper():
    raise SystemExit(5)
try:
    helper()
except SystemExit:
    pass
sys.exit(0)
""",
    "G helper raises inside try, module sys.exit(0)": """import sys
def helper():
    raise SystemExit(6)
try:
    helper()
except SystemExit:
    pass
sys.exit(0)
""",
}

HELPER_MOD = """import sys
def raise_it():
    raise SystemExit(4)
"""


def main():
    hook_dir = sys.argv[1]
    base = dict(os.environ)
    hooked = dict(base)
    hooked["PYTHONPATH"] = hook_dir + (os.pathsep + base["PYTHONPATH"] if base.get("PYTHONPATH") else "")
    with open(os.path.join(HERE, "helper_mod.py"), "w", encoding="utf-8") as f:
        f.write(HELPER_MOD)
    for label, src in CASES.items():
        path = os.path.join(HERE, "child_se.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        for mode, env in (("plain", base), ("hooked", hooked)):
            p = subprocess.run([PY, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=30)
            err = p.stderr.decode(errors="replace").strip().replace("\n", " | ")
            print(f"[{mode:6}] {label:42} rc={p.returncode} stderr={err[:150]!r}")


if __name__ == "__main__":
    main()
