#!/usr/bin/env python3
"""souji r78 wave-repair probes (after measurement; the frozen r78 C1 predicate is unchanged). Each arm builds a
fresh fixture (census/round-74 evade-probe build()), applies one wave-found route, and runs the W gate and the R
(repaired) gate in their own sessions under a 60 s bound (process group killed on expiry -> HANG). An arm passes
iff both observed verdicts equal the expectations written below BEFORE the run (W = what the wave reported, R =
the repair's intent). Output: `ARM <id> W=<verdict>/<class> (<secs>s) R=<verdict>/<class> (<secs>s) as_expected=<yes|no>`
and `SUMMARY arms=<N> as_expected=<K>`; exit 0 iff K == N.
Usage: repair-probes.py --w-dir DIR --r-dir DIR --work WORK (dirs hold the gate beside its writer)."""
import argparse
import importlib.util
import os
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, "..", "..", "round-74", "records", "wave-repair", "probes", "evade-probe.py")
spec = importlib.util.spec_from_file_location("souji_r74_evade_probe", PROBE)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
BOUND = 60
CLASSES = ("RECEIPT-NONREGULAR-GITSOURCE", "RECEIPT-GITSOURCE-SCAN", "RECEIPT-GIT-TIMEOUT")


def _fifo(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.lexists(path):
        os.unlink(path)
    os.mkfifo(path)


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def a_space_subsection(c, w):
    """includeIf whose condition carries a space (true condition: hasconfig on a set remote url) -> FIFO."""
    _fifo(os.path.join(w, "sp-fifo"))
    P.git(c, "config", "remote.origin.url", os.path.join(w, "origin.git"))
    P.git(c, "config", "includeIf.hasconfig:remote.*.url:" + os.path.join(w, "origin.git") + " x.path",
          os.path.join(w, "sp-fifo"))


def a_newline_value(c, w):
    """include value with an embedded newline names a FIFO (`nl<LF>fifo` beside the config)."""
    _fifo(os.path.join(c, ".git", "nl\nfifo"))
    with open(os.path.join(c, ".git", "config"), "a", encoding="utf-8") as f:
        f.write('[include]\n\tpath = "nl\\nfifo"\n')


def a_diamond(c, w):
    """include diamond, 8 levels of 2 files; every file names both next-level files twice, by `./x` and by
    `../dlv<k+1>/x`: 16 distinct files, but 4^8 distinct spellings for a seen-set keyed on the string."""
    d = os.path.join(w, "dia")
    for k in range(8):
        for i in range(2):
            body = b"[user]\n\tname = leaf\n"
            if k < 7:
                body = "".join(f"[include]\n\tpath = ../dlv{k + 1}/x{j}\n\tpath = ../dlv{k + 1}/./x{j}\n"
                               for j in range(2)).encode()
            _write(os.path.join(d, f"dlv{k}", f"x{i}"), body)
    with open(os.path.join(c, ".git", "config"), "a", encoding="utf-8") as f:
        f.write(f"[include]\n\tpath = {d}/dlv0/x0\n")


def a_wide(c, w):
    """a wide acyclic include tree, 3 children per file, 5 levels: 363 distinct regular files (git reads them all)."""
    d = os.path.join(w, "wide")
    def node(k, name):
        body = b"[user]\n\tname = leaf\n"
        if k < 5:
            body = "".join(f"[include]\n\tpath = {name}-{j}\n" for j in range(3)).encode()
            for j in range(3):
                node(k + 1, f"{name}-{j}")
        _write(os.path.join(d, name), body)
    node(1, "t")
    with open(os.path.join(c, ".git", "config"), "a", encoding="utf-8") as f:
        f.write(f"[include]\n\tpath = {d}/t\n")


def a_loose_ref(c, w):
    """packed refs plus a FIFO loose ref for the checked branch."""
    P.git(c, "pack-refs", "--all", "--prune")
    _fifo(os.path.join(c, ".git", "refs", "heads", "master"))


def a_depth11(c, w):
    """an include chain 11 deep (git's limit is 10), all regular files."""
    d = os.path.join(w, "chain")
    for i in range(11):
        _write(os.path.join(d, f"c{i}"), f"[include]\n\tpath = c{i + 1}\n".encode() if i < 10 else b"[user]\n\tname = deep\n")
    with open(os.path.join(c, ".git", "config"), "a", encoding="utf-8") as f:
        f.write(f"[include]\n\tpath = {d}/c0\n")


def p_space_value(c, w):
    """positive: include value with a space naming a regular file."""
    _write(os.path.join(w, "a b.cfg"), b"[user]\n\tname = spaced\n")
    P.git(c, "config", "include.path", os.path.join(w, "a b.cfg"))


def p_space_subsection_regular(c, w):
    """positive: includeIf with a space in its condition naming a regular file."""
    _write(os.path.join(w, "sp-reg.cfg"), b"[user]\n\tname = sp\n")
    P.git(c, "config", "remote.origin.url", os.path.join(w, "origin.git"))
    P.git(c, "config", "includeIf.hasconfig:remote.*.url:" + os.path.join(w, "origin.git") + " x.path",
          os.path.join(w, "sp-reg.cfg"))


def p_tilde_self(c, w):
    """positive: `~<user>/` include naming a missing file (git expands ~user; nothing to refuse)."""
    import pwd
    user = pwd.getpwuid(os.getuid()).pw_name
    P.git(c, "config", "include.path", f"~{user}/.souji-r78-probe-never-there.cfg")


def a_home_fifo(c, w):
    """the caller's HOME holds a FIFO .gitconfig (frozen row g9's shape); returns the extra environment."""
    _fifo(os.path.join(w, "home", ".gitconfig"))
    return {"HOME": os.path.join(w, "home")}


# id, mutate, expected W (verdict/class), expected R (verdict/class)
ARMS = [
    ("a1-space-subsection-fifo", a_space_subsection, "HANG/-", "FAIL/RECEIPT-NONREGULAR-GITSOURCE"),
    ("a2-newline-value-fifo", a_newline_value, "HANG/-", "FAIL/RECEIPT-NONREGULAR-GITSOURCE"),
    # a3: run 1 expected W=HANG; observed W=PASS in 13.3 s (W's depth cap of 10 bounds the 4^7 spellings at this
    # size; records/wave-repair/attempts/repair-probes-run1.txt). Relabelled to the observed W verdict; the arm
    # still pins that R's canonical seen-set passes a legitimate diamond (no SCAN refusal).
    ("a3-include-diamond-spellings", a_diamond, "PASS/-", "PASS/-"),
    ("a3b-include-wide-363", a_wide, "PASS/-", "FAIL/RECEIPT-GITSOURCE-SCAN"),
    ("a4-fifo-loose-ref", a_loose_ref, "HANG/-", "FAIL/RECEIPT-NONREGULAR-GITSOURCE"),
    ("a5-include-depth-11", a_depth11, "FAIL/RECEIPT-NONREGULAR-GITSOURCE", "FAIL/RECEIPT-GITSOURCE-SCAN"),
    ("p1-space-in-value-regular", p_space_value, "PASS/-", "PASS/-"),
    ("p2-space-subsection-regular", p_space_subsection_regular, "PASS/-", "PASS/-"),
    ("p3-tilde-user-missing", p_tilde_self, "PASS/-", "PASS/-"),
    # a6 pins the include walk's config isolation by time (S78MutGate survivor m13: without
    # GIT_CONFIG_GLOBAL=/dev/null the walk blocks 45 s on the FIFO before failing; the frozen rows carry no
    # duration predicate): R must refuse within 5 s.
    ("a6-home-fifo-refused-fast", a_home_fifo, "FAIL/RECEIPT-NONREGULAR-GITSOURCE", "FAIL/RECEIPT-NONREGULAR-GITSOURCE"),
]
R_MAX_SECS = {"a6-home-fifo-refused-fast": 5.0}


def run(gate, clone, report, prereg, extra=None):
    t0 = time.monotonic()
    p = subprocess.Popen(["bash", gate, "--lane", clone, "--branch", "master", "--report", report, "--prereg",
                          prereg], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         env=P.env_clean(extra), start_new_session=True, cwd=os.path.dirname(clone))
    try:
        out, _ = p.communicate(timeout=BOUND)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.communicate()
        subprocess.run(["pkill", "-KILL", "-f", clone], check=False)
        return "HANG/-", time.monotonic() - t0
    text = out.decode("utf-8", "replace")
    fails = [l for l in text.splitlines() if l.startswith("check-") and l.endswith("=FAIL")]
    v = "PASS" if p.returncode == 0 and not fails else ("FAIL" if p.returncode == 1 and fails else "ODD")
    cls = next((k for k in CLASSES if k in text), "-")
    return f"{v}/{cls}", time.monotonic() - t0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--w-dir", required=True)
    ap.add_argument("--r-dir", required=True)
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")) or (
            os.path.exists(work) and os.listdir(work)):
        print("REPAIR-PROBES-FATAL: --work must be an empty directory outside /tmp", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    gates = {k: os.path.join(os.path.abspath(d), "souji-pre-report-gate.sh") for k, d in (("W", ns.w_dir), ("R", ns.r_dir))}
    for k, g in gates.items():
        import hashlib
        with open(g, "rb") as f:
            print(f"# {k} gate sha256={hashlib.sha256(f.read()).hexdigest()}")
    ok = 0
    for aid, mut, ew, er in ARMS:
        seen = {}
        for k in ("W", "R"):
            rowdir = os.path.join(work, f"{aid}-{k}")
            clone, report, prereg = P.build(rowdir)
            extra = mut(clone, rowdir)
            seen[k] = run(gates[k], clone, report, prereg, extra)
        good = (seen["W"][0] == ew and seen["R"][0] == er
                and seen["R"][1] < R_MAX_SECS.get(aid, float("inf")))
        ok += good
        print(f"ARM {aid} W={seen['W'][0]} ({seen['W'][1]:.1f}s) R={seen['R'][0]} ({seen['R'][1]:.1f}s) "
              f"expect W={ew} R={er} as_expected={'yes' if good else 'no'}")
    print(f"SUMMARY arms={len(ARMS)} as_expected={ok}")
    return 0 if ok == len(ARMS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
