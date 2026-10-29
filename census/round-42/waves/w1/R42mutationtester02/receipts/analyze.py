import os, re, json
S = "/fast/scratch/hyaku/souji-r42/R42mutationtester02/out"
W = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester02/mutants"
ids = [l.strip() for l in open(os.path.join(W, "manifest.tsv"), encoding="utf-8").read().splitlines()[1:] if l.strip()]
ids = [l.split("\t")[0] for l in ids]
def load(tag):
    try:
        out = open(os.path.join(S, tag + ".out"), encoding="utf-8").read()
    except FileNotFoundError:
        return None
    rc = open(os.path.join(S, tag + ".rc")).read().strip()
    err = open(os.path.join(S, tag + ".err"), encoding="utf-8").read()
    return {"out": out, "rc": rc, "err": err}
def kv(line):
    return dict(re.findall(r"(\w+)=(\S+)", line))
def fields(text):
    res = {}
    for line in text.splitlines():
        if line.startswith("case-"):
            name, rest = line.split("=", 1)
            res[name] = rest
        elif line.startswith("SUMMARY"):
            res["SUMMARY"] = kv(line)
        elif re.match(r"^(real|retro|retro_clean|selftest) ", line):
            res[line.split(" ")[0]] = line
        else:
            res.setdefault("other", []).append(line)
    return res
def diff(base, mut):
    """returns (verdict_changes, text_changes) lists of strings"""
    vc, tc = [], []
    if base["rc"] != mut["rc"]:
        vc.append("rc %s->%s" % (base["rc"], mut["rc"]))
    fb, fm = fields(base["out"]), fields(mut["out"])
    for k in sorted(set(fb) | set(fm)):
        if k == "SUMMARY":
            sb, sm = fb.get(k, {}), fm.get(k, {})
            for f in sorted(set(sb) | set(sm)):
                if sb.get(f) != sm.get(f):
                    vc.append("SUMMARY.%s %s->%s" % (f, sb.get(f), sm.get(f)))
        elif k == "other":
            if fb.get(k) != fm.get(k):
                vc.append("extra-lines")
        elif k.startswith("case-"):
            vb, vm = fb.get(k), fm.get(k)
            if vb is None or vm is None:
                vc.append("%s missing" % k); continue
            sb, sm = vb.split(" ", 1)[0], vm.split(" ", 1)[0]
            if sb != sm:
                vc.append("%s %s->%s" % (k, sb, sm))
            elif vb != vm:
                tc.append("%s detail" % k)
        else:
            if fb.get(k) != fm.get(k):
                if fb.get(k) and fm.get(k) and fb[k].split(" ")[1] == fm[k].split(" ")[1] and fb[k].split(" ")[1] in ("ok","red","FAIL"):
                    tc.append(k + " detail")
                else:
                    vc.append("%s %s->%s" % (k, (fb.get(k) or "")[:40], (fm.get(k) or "")[:40]))
    if base["err"] != mut["err"]:
        tc.append("stderr")
    return vc, tc
base = {"base": load("base-base"), "stub": load("base-stub")}
rows = []
for mid in ids:
    res = {}
    for t in ("base", "stub"):
        m = load(mid + "-" + t)
        if m is None:
            res[t] = ("MISSING", [], [])
            continue
        vc, tc = diff(base[t], m)
        res[t] = ("ok", vc, tc)
    killed_v = any(res[t][1] for t in res if res[t][0] == "ok")
    killed_t = any(res[t][2] for t in res if res[t][0] == "ok")
    rows.append({"id": mid, "verdict": killed_v, "text": killed_t,
                 "base": res["base"], "stub": res["stub"]})
out = []
for r in rows:
    k = "killed" if r["verdict"] else ("killed-text" if r["text"] else "survived")
    def fmt(x):
        if x[0] != "ok": return x[0]
        return "; ".join(x[1] + x[2]) or "-"
    out.append("%s\t%s\tbase: %s\tstub: %s" % (r["id"], k, fmt(r["base"]), fmt(r["stub"])))
print("\n".join(out))
print("TOTAL", len(rows), "verdict-killed", sum(r["verdict"] for r in rows), "text-only", sum((not r["verdict"]) and r["text"] for r in rows), "survived", sum((not r["verdict"]) and (not r["text"]) for r in rows))
