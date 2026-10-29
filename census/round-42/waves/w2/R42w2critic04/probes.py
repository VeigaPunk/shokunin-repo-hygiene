#!/usr/bin/env python3
"""R42w2critic04 differential probes for the survey mutants that no committed fixture kills.

Each scenario builds identical inputs under a fresh work directory and runs the pristine tool and one
survey mutant on them. A mutant is non-equivalent when some scenario's normalised outcome (exit code,
stdout, stderr, the --json file's mode and parsed content, and a fast/slow timing class) differs from the
pristine outcome. Byte-only and stderr-text-only differences are recorded separately.
Scratch: /fast/scratch/hyaku/souji-r42/R42w2critic04/probe/<variant>/<scenario> (deleted after each run).
"""
import concurrent.futures
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import time

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2critic04"
S = "/fast/scratch/hyaku/souji-r42/R42w2critic04"
PATH = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
GENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
        "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
        "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid"}
ROW = "REPO\tr\tregs=1\tprunable=0\n"


def env_for(work):
    e = dict(GENV)
    e.update({"PATH": PATH, "TMPDIR": work, "HOME": work})
    return e


def sh(args, cwd, work):
    subprocess.run(args, cwd=cwd, env=env_for(work), check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=60)


def ginit(path, work, bare=False, commit=False):
    os.makedirs(path, exist_ok=True)
    sh(["git", "init", "-q"] + (["--bare"] if bare else []) + [path], work, work)
    if commit:
        top = subprocess.run(["git", "-C", path, "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, env=env_for(work), check=True).stdout.strip()
        assert top == os.path.realpath(path), "fixture toplevel mismatch: %s" % top
        sh(["git", "-C", path, "commit", "-q", "--allow-empty", "-m", "init"], work, work)
    return path


def write(path, data):
    b = data if isinstance(data, bytes) else data.encode("utf-8")
    with open(path, "wb") as h:
        h.write(b)
    return path


def fleet(W, commit=False):
    root, out = os.path.join(W, "root"), os.path.join(W, "out")
    os.makedirs(root)
    os.makedirs(out)
    ginit(os.path.join(root, "r"), W, commit=commit)
    return root, out


def tool(t, W, args, cwd=None):
    t0 = time.monotonic()
    try:
        p = subprocess.run(["python3", "-B", t] + args, cwd=cwd or W, env=env_for(W), capture_output=True,
                           timeout=90)
        rc, out, err = p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        rc, out, err = None, "", "PROBE-TIMEOUT"
    return {"rc": rc, "out": out, "err": err, "secs": round(time.monotonic() - t0, 2)}


def jinfo(path):
    if path is None or not os.path.lexists(path):
        return None
    try:
        st = os.stat(path)
        mode = oct(stat.S_IMODE(st.st_mode))
        if not stat.S_ISREG(st.st_mode):
            return {"mode": mode, "kind": "nonregular"}
        data = open(path, "rb").read()
    except OSError as exc:
        return {"err": type(exc).__name__}
    return {"mode": mode, "raw": data.decode("utf-8", "replace")}


def base(t, W, rec, extra=(), skip=True, pre=None, root_override=None, cwd=None, jpath=None):
    root, out = fleet(W)
    if pre:
        pre(root, out, W)
    recp = out + "/rec"
    if rec is not None:
        write(recp, rec)
    ex = extra(root, out) if callable(extra) else list(extra)
    args = ["--root", root_override or root, "--record", recp] + (["--skip-unrecorded"] if skip else []) + ex
    return {"res": tool(t, W, args, cwd=cwd), "json": jinfo(jpath(root, out) if jpath else None)}


def s_clean(t, W):
    return base(t, W, ROW)


def s_regs_drift(t, W):
    return base(t, W, "REPO\tr\tregs=2\tprunable=0\n")


def s_missing_record(t, W):
    return base(t, W, None)


def s_fifo_record(t, W):
    return base(t, W, None, pre=lambda r, o, w: os.mkfifo(o + "/rec"))


def s_crlf(t, W):
    return base(t, W, b"REPO\tr\tregs=1\tprunable=0\r\n")


def s_comments_blank(t, W):
    return base(t, W, "# note\n\nREPO\tr\tregs=1\tprunable=0\n")


def s_duplicate(t, W):
    return base(t, W, ROW + ROW)


def s_big_3000(t, W):
    return base(t, W, "".join("REPO\tx%04d\tregs=1\tprunable=0\n" % i for i in range(3000)))


def s_total_repos_small(t, W):
    return base(t, W, ROW + "TOTAL\trepos=0\tregs=1\tprunable=0\n")


def s_total_regs_big(t, W):
    return base(t, W, ROW + "TOTAL\trepos=1\tregs=5\tprunable=0\n")


def s_total_prunable_small(t, W):
    return base(t, W, "REPO\tr\tregs=1\tprunable=1\nTOTAL\trepos=1\tregs=1\tprunable=0\n")


def s_total_junk(t, W):
    return base(t, W, ROW + "TOTAL\trepos=1\tregs=1\tprunable=0x\n")


def s_repo_junk(t, W):
    return base(t, W, "REPO\tr\tregs=1\tprunable=0x\n")


def s_space_name(t, W):
    return base(t, W, "REPO\tmy repo\tregs=1\tprunable=0\n", pre=lambda r, o, w: ginit(os.path.join(r, "my repo"), w))


def s_empty_regs(t, W):
    return base(t, W, "REPO\tr\tregs=\tprunable=0\n")


def s_timeout_float(t, W):
    return base(t, W, ROW, extra=["--timeout", "1.5"])


def s_timeout_zero(t, W):
    return base(t, W, ROW, extra=["--timeout", "0"])


def s_json_inside_root(t, W):
    return base(t, W, ROW, extra=lambda r, o: ["--json", r + "/x.json"], jpath=lambda r, o: r + "/x.json")


def s_json_under_root_nonrepo(t, W):
    return base(t, W, ROW, pre=lambda r, o, w: os.makedirs(r + "/notes"),
                extra=lambda r, o: ["--json", r + "/notes/o.json"], jpath=lambda r, o: r + "/notes/o.json")


def s_json_sibling_prefix(t, W):
    return base(t, W, ROW, pre=lambda r, o, w: os.makedirs(w + "/rootX"),
                extra=lambda r, o: ["--json", os.path.dirname(r) + "/rootX/o.json"],
                jpath=lambda r, o: os.path.dirname(r) + "/rootX/o.json")


def s_json_empty(t, W):
    return base(t, W, ROW, extra=["--json", ""])


def s_json_mode(t, W):
    return base(t, W, ROW, extra=lambda r, o: ["--json", o + "/m.json"], jpath=lambda r, o: o + "/m.json")


def s_json_devnull(t, W):
    return base(t, W, ROW, extra=["--json", "/dev/null"], jpath=lambda r, o: "/dev/null")


def s_json_dir(t, W):
    return base(t, W, ROW, pre=lambda r, o, w: os.makedirs(o + "/d"), extra=lambda r, o: ["--json", o + "/d"],
                jpath=lambda r, o: o + "/d")


def s_json_missing_dir(t, W):
    return base(t, W, ROW, extra=lambda r, o: ["--json", o + "/nodir/x.json"])


def s_json_is_record(t, W):
    return base(t, W, ROW, extra=lambda r, o: ["--json", o + "/rec"], jpath=lambda r, o: o + "/rec")


def s_json_is_record_symlink(t, W):
    root, out = fleet(W)
    rec = write(out + "/rec", ROW)
    os.symlink(rec, out + "/recl")
    res = tool(t, W, ["--root", root, "--record", out + "/recl", "--json", out + "/rec", "--skip-unrecorded"])
    return {"res": res, "json": jinfo(rec)}


def s_json_unicode_name(t, W):
    return base(t, W, "REPO\trép\tregs=1\tprunable=0\n".encode("utf-8"),
                pre=lambda r, o, w: ginit(os.path.join(r, "rép"), w),
                extra=lambda r, o: ["--json", o + "/u.json"], jpath=lambda r, o: o + "/u.json")


def s_json_relative(t, W):
    return base(t, W, ROW, extra=["--json", "rel.json"], jpath=lambda r, o: os.path.dirname(r) + "/rel.json")


def s_json_overwrite_long(t, W):
    return base(t, W, ROW, pre=lambda r, o, w: write(o + "/old.json", "x" * 5000),
                extra=lambda r, o: ["--json", o + "/old.json"], jpath=lambda r, o: o + "/old.json")


def s_rel_root_named(t, W):
    root, out = os.path.join(W, "root"), os.path.join(W, "out")
    os.makedirs(out)
    ginit(root, W)
    rec = write(out + "/rec", "REPO\troot\tregs=1\tprunable=0\n")
    return {"res": tool(t, W, ["--root", ".", "--record", rec, "--skip-unrecorded"], cwd=root)}


def s_rel_root_discover(t, W):
    root, out = os.path.join(W, "root"), os.path.join(W, "out")
    os.makedirs(out)
    ginit(root, W)
    rec = write(out + "/rec", "REPO\tother\tregs=1\tprunable=0\n")
    return {"res": tool(t, W, ["--root", ".", "--record", rec], cwd=root)}


def s_root_symlink(t, W):
    os.symlink(W + "/root", W + "/lnk")
    return base(t, W, ROW, root_override=W + "/lnk")


def s_root_unreadable(t, W):
    root, out = fleet(W)
    rec = write(out + "/rec", ROW)
    os.chmod(root, 0)
    try:
        res = tool(t, W, ["--root", root, "--record", rec])
    finally:
        os.chmod(root, 0o755)
    return {"res": res}


def s_timeout_fifo_head(t, W):
    root, out = fleet(W)
    ginit(root + "/t", W)
    os.remove(root + "/t/.git/HEAD")
    os.mkfifo(root + "/t/.git/HEAD")
    rec = write(out + "/rec", "REPO\tt\tregs=1\tprunable=0\n")
    res = tool(t, W, ["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"])
    res["fast"] = res["secs"] < 10
    res.pop("secs")
    return {"res": res}


def s_gitdir_symlink(t, W):
    root, out = fleet(W)
    os.makedirs(W + "/outside")
    ginit(W + "/outside/gd", W, bare=True)
    g = root + "/g"
    os.makedirs(g)
    os.symlink(W + "/outside/gd", root + "/gdlink")
    write(g + "/.git", "gitdir: " + root + "/gdlink\n")
    rec = write(out + "/rec", "REPO\tg\tregs=1\tprunable=0\n")
    return {"res": tool(t, W, ["--root", root, "--record", rec, "--skip-unrecorded"])}


def s_regs_up(t, W):
    root, out = fleet(W, commit=True)
    sh(["git", "-C", root + "/r", "worktree", "add", "-q", "--detach", root + "/wt"], W, W)
    rec = write(out + "/rec", ROW)
    return {"res": tool(t, W, ["--root", root, "--record", rec, "--skip-unrecorded"])}


def s_prunable_down(t, W):
    return base(t, W, "REPO\tr\tregs=1\tprunable=1\n")


def s_stale_worktree(t, W):
    root, out = fleet(W, commit=True)
    sh(["git", "-C", root + "/r", "worktree", "add", "-q", "--detach", root + "/wt"], W, W)
    shutil.rmtree(root + "/wt")
    rec = write(out + "/rec", ROW)
    return {"res": tool(t, W, ["--root", root, "--record", rec, "--skip-unrecorded"])}


def s_root_not_repo_named(t, W):
    root, out = os.path.join(W, "root"), os.path.join(W, "out")
    os.makedirs(root)
    os.makedirs(out)
    rec = write(out + "/rec", "REPO\troot\tregs=1\tprunable=0\n")
    return {"res": tool(t, W, ["--root", root, "--record", rec, "--skip-unrecorded"])}


def s_unrecorded_root_repo(t, W):
    root, out = os.path.join(W, "root"), os.path.join(W, "out")
    os.makedirs(out)
    ginit(root, W)
    ginit(os.path.join(root, "zz"), W)
    rec = write(out + "/rec", "REPO\tother\tregs=1\tprunable=0\n")
    return {"res": tool(t, W, ["--root", root, "--record", rec])}


def s_unrecorded_gitfile(t, W):
    root, out = fleet(W, commit=True)
    sh(["git", "-C", root + "/r", "worktree", "add", "-q", "--detach", root + "/wt"], W, W)
    rec = write(out + "/rec", ROW)
    return {"res": tool(t, W, ["--root", root, "--record", rec])}


def s_record_gitfile(t, W):
    root, out = fleet(W, commit=True)
    sh(["git", "-C", root + "/r", "worktree", "add", "-q", "--detach", root + "/wt"], W, W)
    rec = write(out + "/rec", "REPO\twt\tregs=2\tprunable=0\n")
    return {"res": tool(t, W, ["--root", root, "--record", rec, "--skip-unrecorded"])}


def s_many_unrecorded(t, W):
    root, out = fleet(W)
    for n in ("b", "a", "c"):
        ginit(os.path.join(root, n), W)
    write(root + "/f", "plain file\n")
    rec = write(out + "/rec", ROW)
    return {"res": tool(t, W, ["--root", root, "--record", rec])}


def s_json_hardlink_outside(t, W):
    root, out = fleet(W)
    os.makedirs(W + "/outside")
    orig = write(W + "/outside/orig.json", "{}\n")
    os.link(orig, out + "/hl.json")
    rec = write(out + "/rec", ROW)
    res = tool(t, W, ["--root", root, "--record", rec, "--skip-unrecorded", "--json", out + "/hl.json"])
    return {"res": res, "json": jinfo(out + "/hl.json"), "orig": jinfo(orig)}


def s_alias_hardlink_record(t, W):
    root, out = fleet(W)
    rec = write(out + "/rec", ROW)
    os.link(rec, out + "/hl.json")
    res = tool(t, W, ["--root", root, "--record", rec, "--skip-unrecorded", "--json", out + "/hl.json"])
    return {"res": res, "json": jinfo(rec)}


SCEN = [
    ("clean", s_clean), ("regs-drift", s_regs_drift), ("missing-record", s_missing_record),
    ("fifo-record", s_fifo_record), ("crlf", s_crlf), ("comments-blank", s_comments_blank),
    ("duplicate", s_duplicate), ("big-3000", s_big_3000), ("total-repos-small", s_total_repos_small),
    ("total-regs-big", s_total_regs_big), ("total-prunable-small", s_total_prunable_small),
    ("total-junk", s_total_junk), ("repo-junk", s_repo_junk), ("space-name", s_space_name),
    ("empty-regs", s_empty_regs), ("timeout-float", s_timeout_float), ("timeout-zero", s_timeout_zero),
    ("json-inside-root", s_json_inside_root), ("json-under-root-nonrepo", s_json_under_root_nonrepo),
    ("json-sibling-prefix", s_json_sibling_prefix), ("json-empty", s_json_empty), ("json-mode", s_json_mode),
    ("json-devnull", s_json_devnull), ("json-dir", s_json_dir), ("json-missing-dir", s_json_missing_dir),
    ("json-is-record", s_json_is_record), ("json-is-record-symlink", s_json_is_record_symlink),
    ("json-unicode-name", s_json_unicode_name), ("json-relative", s_json_relative),
    ("json-overwrite-long", s_json_overwrite_long), ("rel-root-named", s_rel_root_named),
    ("rel-root-discover", s_rel_root_discover), ("root-symlink", s_root_symlink),
    ("root-unreadable", s_root_unreadable), ("timeout-fifo-head", s_timeout_fifo_head),
    ("gitdir-symlink", s_gitdir_symlink), ("regs-up", s_regs_up), ("prunable-down", s_prunable_down),
    ("stale-worktree", s_stale_worktree), ("root-not-repo-named", s_root_not_repo_named),
    ("unrecorded-root-repo", s_unrecorded_root_repo), ("unrecorded-gitfile", s_unrecorded_gitfile),
    ("record-gitfile", s_record_gitfile), ("many-unrecorded", s_many_unrecorded),
    ("json-hardlink-outside", s_json_hardlink_outside), ("alias-hardlink-record", s_alias_hardlink_record),
]


def jnorm(j, W):
    """Scrub the per-run work path from a --json file, then hash and parse the scrubbed bytes."""
    if not isinstance(j, dict) or "raw" not in j:
        return j
    raw = j["raw"].replace(W, "<W>")
    out = {k: v for k, v in j.items() if k != "raw"}
    out["sha"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    try:
        out["parsed"] = json.loads(raw)
    except ValueError:
        out["parsed"] = "UNPARSED"
    return out


def normal(o, W, prog):
    """Comparable outcome: scrub the per-run work path and the tool's file name, drop raw seconds, keep the timing class."""
    if "error" in o:
        return {"error": o["error"]}
    res = o["res"]
    scrub = lambda s: s.replace(W, "<W>").replace(prog, "tool.py")
    out = {"rc": res["rc"], "out": scrub(res["out"]), "err": scrub(res["err"]),
           "json": jnorm(o.get("json"), W), "orig": jnorm(o.get("orig"), W), "fast": res.get("fast")}
    if "secs" in res:
        out["slow"] = res["secs"] >= 10
    return out


def run_one(job):
    variant, name, fn = job
    t = os.path.join(S, "fx", "tool.py") if variant == "PRISTINE" else os.path.join(S, "mutd", variant, "tool.py")
    W = os.path.join(S, "probe", variant, name)
    shutil.rmtree(W, ignore_errors=True)
    os.makedirs(W)
    try:
        o = fn(t, W)
    except Exception as exc:  # a scenario that cannot be built is recorded, never silently skipped
        o = {"error": "%s: %s" % (type(exc).__name__, exc)}
    finally:
        for dp, dn, fn_ in os.walk(W):
            os.chmod(dp, 0o755)
        shutil.rmtree(W, ignore_errors=True)
    return variant, name, normal(o, W, os.path.basename(t))


def main(argv):
    mutants = argv or []
    variants = ["PRISTINE"] + mutants
    jobs = [(v, n, f) for v in variants for n, f in SCEN]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(run_one, jobs))
    table = {}
    for v, n, o in results:
        table.setdefault(v, {})[n] = o
    base_ = table["PRISTINE"]
    errors = [(n, o["error"]) for n, o in base_.items() if "error" in o]
    diffs = {}
    for v in mutants:
        rows = []
        for n, _f in SCEN:
            m, p = table[v][n], base_[n]
            if m == p:
                continue
            kinds = []
            if "error" in m or "error" in p:
                kinds.append("ERROR")
            else:
                if m["rc"] != p["rc"]:
                    kinds.append("rc %s->%s" % (p["rc"], m["rc"]))
                if m["out"] != p["out"]:
                    kinds.append("stdout")
                if m["err"].strip() != p["err"].strip():
                    kinds.append("stderr-class")
                elif m["err"] != p["err"]:
                    kinds.append("stderr-text-only")
                if m["json"] != p["json"]:
                    pj = (p["json"] or {}).get("parsed") if isinstance(p["json"], dict) else None
                    mj = (m["json"] or {}).get("parsed") if isinstance(m["json"], dict) else None
                    if pj != mj or (p["json"] or {}).get("mode") != (m["json"] or {}).get("mode") \
                            or (p["json"] or {}).get("kind") != (m["json"] or {}).get("kind") \
                            or (p["json"] or {}).get("err") != (m["json"] or {}).get("err"):
                        kinds.append("json-content/mode")
                    else:
                        kinds.append("json-bytes-only")
                if m.get("orig") != p.get("orig"):
                    kinds.append("orig-file")
                if m.get("fast") != p.get("fast") or m.get("slow") != p.get("slow"):
                    kinds.append("timing")
            rows.append((n, kinds or ["other"]))
        diffs[v] = rows
    with open(os.path.join(SEAT, "probes-results.json"), "w", encoding="utf-8") as h:
        json.dump({"pristine": base_, "mutants": {v: table[v] for v in mutants}, "diffs": diffs,
                   "scenario_errors_on_pristine": errors}, h, indent=1, sort_keys=True, default=str)
    print("PRISTINE scenarios=%d errors=%s" % (len(SCEN), errors))
    for n, _f in SCEN:
        o = base_[n]
        if "error" in o:
            print("  PRISTINE %-24s ERROR %s" % (n, o["error"]))
        else:
            print("  PRISTINE %-24s rc=%s out=%r err=%r json=%s" % (
                n, o["rc"], o["out"][-90:], o["err"].strip()[-110:],
                (o["json"] or {}).get("mode") if o["json"] else None))
    for v in mutants:
        print("MUTANT %s differing=%s" % (v, [(n, k) for n, k in diffs[v]]))


if __name__ == "__main__":
    main(sys.argv[1:])
