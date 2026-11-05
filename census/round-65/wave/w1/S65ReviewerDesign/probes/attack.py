import sys, importlib.util, os, subprocess, shutil
spec = importlib.util.spec_from_file_location("c1c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c1-counter.py")
c1c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1c)
S65 = "/fast/scratch/hyaku/souji-r65/S65ReviewerDesign"
NEW = os.path.join(S65, "writer-landed.py")
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASEV = "4a43a4d919c5b51ae9be859a1266ce4b11337b0b"
BB = os.path.join(S65, "base-all.py")
subprocess.run(["git","-C",LANE,"show",f"{BASEV}:tools/souji-receipt-write.py"], stdout=open(BB,"wb"), check=True)

def mkfix(tag, specd, extra_config=None, post=None):
    rep, rev = c1c.build_case(os.path.join(S65, "atk", tag), tag if len(tag)<=3 else "A"+"x", "both", specd) if False else (None,None)
    return None

# generic direct builder to avoid build_case tag weirdness
def direct(tag, specd, extra_cmds=(), env_extra=None, rootsub=None, allow=None, instrument="tools/instr.sh", out_pre=None):
    rep, rev = c1c.build_case(os.path.join(S65, "atk"), tag, "one", specd)
    outdir = os.path.join(os.path.dirname(rep), "out"); out = os.path.join(outdir, "r.txt")
    if out_pre is not None:
        with open(out, "wb") as f: f.write(out_pre)
    for c in extra_cmds: subprocess.run(c, cwd=rep, check=True)
    root = os.path.join(rep, rootsub) if rootsub else rep
    a = [sys.executable, "-B", NEW, "--root", root, "--rev", rev, "--instrument", instrument,
         "--out", out, "--allow-outside"]
    if (allow if allow is not None else specd.get("allow_dirty")): a.append("--allow-dirty")
    a += ["--", "/bin/echo", "hi"]
    env = c1c.clean_env(env_extra)
    p = subprocess.run(a, cwd=S65, capture_output=True, env=env, timeout=120)
    rc = p.returncode
    verdict = "accept" if rc==0 and os.path.isfile(out) else ("refuse" if rc==2 and not os.path.lexists(out) else f"error({rc})")
    print(f"[{tag}] {verdict} :: {p.stderr.decode()[:135].strip()}")
    return verdict

# ---- 1. V-class: status.showUntrackedFiles=normal (not no) + untracked file present
direct("V-normal-attr", {"name":"VnormC"})            # clean baseline (should accept)
direct("V-normal-att2", {"name":"VnormU","untracked_file":"tools/hidden.txt"})
# now with config normal:
def direct_cfg(tag, specd, cfgval):
    rep, rev = c1c.build_case(os.path.join(S65, "atk"), tag, "one", specd)
    subprocess.run(["git","-C",rep,"config","status.showUntrackedFiles",cfgval], check=True)
    out = os.path.join(os.path.dirname(rep), "out", "r.txt")
    a = [sys.executable, "-B", NEW, "--root", rep, "--rev", rev, "--instrument", "tools/instr.sh",
         "--out", out, "--allow-outside", "--", "/bin/echo", "hi"]
    p = subprocess.run(a, cwd=S65, capture_output=True, env=c1c.clean_env(), timeout=120)
    rc = p.returncode
    verdict = "accept" if rc==0 and os.path.isfile(out) else ("refuse" if rc==2 and not os.path.lexists(out) else f"error({rc})")
    print(f"[{tag} cfg={cfgval}] {verdict} :: {p.stderr.decode()[:130].strip()}")
direct_cfg("V-normal-cfg", {"name":"VnormC2","untracked_file":"tools/hidden.txt"}, "normal")
direct_cfg("V-no-dir-cfg", {"name":"Vnd","untracked_dir":"tools/extra"}, "no")

# ---- 2. -c config on the CALLER's environment (env GIT_CONFIG_COUNT/GIT_CONFIG_KEY_0/VALUE_0)
def direct_env_cfg(tag, specd, key, val, envpair=True):
    rep, rev = c1c.build_case(os.path.join(S65, "atk"), tag, "one", specd)
    out = os.path.join(os.path.dirname(rep), "out", "r.txt")
    a = [sys.executable, "-B", NEW, "--root", rep, "--rev", rev, "--instrument", "tools/instr.sh",
         "--out", out, "--allow-outside"] + (["--allow-dirty"] if specd.get("allow_dirty") else []) + ["--", "/bin/echo", "hi"]
    env = c1c.clean_env()
    if envpair:
        env["GIT_CONFIG_COUNT"]="1"; env["GIT_CONFIG_KEY_0"]=key; env["GIT_CONFIG_VALUE_0"]=val
    p = subprocess.run(a, cwd=S65, capture_output=True, env=env, timeout=120)
    rc = p.returncode
    verdict = "accept" if rc==0 and os.path.isfile(out) else ("refuse" if rc==2 and not os.path.lexists(out) else f"error({rc})")
    print(f"[{tag} env-cfg {key}={val}] {verdict} :: {p.stderr.decode()[:130].strip()}")
direct_env_cfg("V-envcfg-hidden", {"name":"Veh","untracked_file":"tools/hidden.txt"}, "status.showUntrackedFiles", "no")
direct_env_cfg("V-envcfg-dir", {"name":"Ved","untracked_dir":"tools/extra"}, "status.showUntrackedFiles", "no")

# ---- 3. Mode granularity: setuid, sticky, and mode flip on untracked-dir file in run
def direct_mode(tag, seed_mode, inrun_target=None, inrun_mode=None, untracked=False):
    specd = {"name": tag, "allow_dirty": True, "dirty": True}
    if untracked: specd["untracked_dir"] = "tools/extra"
    rep, rev = c1c.build_case(os.path.join(S65, "atk"), tag, "one", specd)
    target = os.path.join(rep, inrun_target)
    os.chmod(target, seed_mode)
    wrapped = [sys.executable, "-c", f"import os,sys; os.chmod(sys.argv[1], {oct(inrun_mode)})", target] if inrun_mode else ["/bin/echo", "hi"]
    out = os.path.join(os.path.dirname(rep), "out", "r.txt")
    a = [sys.executable, "-B", NEW, "--root", rep, "--rev", rev, "--instrument", "tools/instr.sh",
         "--out", out, "--allow-outside", "--allow-dirty", "--", *wrapped]
    p = subprocess.run(a, cwd=S65, capture_output=True, env=c1c.clean_env(), timeout=120)
    rc = p.returncode
    verdict = "accept" if rc==0 and os.path.isfile(out) else ("refuse" if rc==2 and not os.path.lexists(out) else f"error({rc})")
    print(f"[{tag}] {verdict} :: {p.stderr.decode()[:130].strip()}")
direct_mode("MOD-setuid-flip", 0o4755, "tools/notes.txt", 0o5755)   # setuid survives, perms flip
direct_mode("MOD-sticky-flip", 0o1755, "tools/notes.txt", 0o2755)   # sticky - sticky
direct_mode("MOD-untracked-flip", 0o644, "tools/extra/keep.txt", 0o600, untracked=True)
direct_mode("MOD-stable-setuid", 0o4755, "tools/notes.txt", None)   # setuid snapshot stable, honest accept?

# ---- 4. Symlink rule: outside-repo, dangling, in-run swap for regular file, symlinked dir
def direct_link(tag, kind):
    specd = {"name": tag, "allow_dirty": True, "untracked_dir": "tools/extra"}
    rep, rev = c1c.build_case(os.path.join(S65, "atk"), tag, "one", specd)
    extra = os.path.join(rep, "tools", "extra")
    link = os.path.join(extra, "link")
    if kind == "outside": os.symlink("/etc/hostname", link)
    elif kind == "dangling": os.symlink("no-such-path-anywhere", link)
    elif kind == "swapdir": os.symlink("/etc", link)
    wrapped = ["/bin/echo", "hi"]
    if kind == "swapregular":
        os.symlink("../notes.txt", link)
        wrapped = [sys.executable, "-c",
                   "import os,sys,shutil; p=sys.argv[1]; os.unlink(p); open(p,'wb').write(b'now-regular')",
                   link]
    out = os.path.join(os.path.dirname(rep), "out", "r.txt")
    a = [sys.executable, "-B", NEW, "--root", rep, "--rev", rev, "--instrument", "tools/instr.sh",
         "--out", out, "--allow-outside", "--allow-dirty", "--", *wrapped]
    p = subprocess.run(a, cwd=S65, capture_output=True, env=c1c.clean_env(), timeout=120)
    rc = p.returncode; kindstr = kind
    # for swapregular the link must first exist — wrapped handles it
    verdict = "accept" if rc==0 and os.path.isfile(out) else ("refuse" if rc==2 and not os.path.lexists(out) else f"error({rc})")
    print(f"[{tag} {kindstr}] {verdict} :: {p.stderr.decode()[:130].strip()}")
direct_link("SY-outside", "outside")
direct_link("SY-dangling", "dangling")
direct_link("SY-to-dir", "swapdir")
direct_link("SY-swap-regular", "swapregular")

# ---- 5. False-refusal probes on%（ base-accepted shapes ）
# 5a. .gitignore'd file in untracked dir (ignored files are NOT untracked — writer sees nothing)
def direct_ignored(tag, nested=True):
    specd = {"name": tag, "allow_dirty": True}
    rep, rev = c1c.build_case(os.path.join(S65, "atk"), tag, "one", specd)
    with open(os.path.join(rep, ".gitignore"), "wb") as f: f.write(b"*.ign\n")
    if nested:
        os.makedirs(os.path.join(rep, "tools/extra"))
        with open(os.path.join(rep, "tools/extra/x.ign"), "wb") as f: f.write(b"ign\n")
    else:
        with open(os.path.join(rep, "tools/extra.ign"), "wb") as f: f.write(b"ign\n")
    with open(os.path.join(rep, "tools/notes.txt"), "ab") as f: f.write(b"dirty\n")
    out = os.path.join(os.path.dirname(rep), "out", "r.txt")
    p = subprocess.run([sys.executable, "-B", NEW, "--root", rep, "--rev", rev, "--instrument",
                        "tools/instr.sh", "--out", out, "--allow-outside", "--allow-dirty",
                        "--", "/bin/echo", "hi"], cwd=S65, capture_output=True, env=c1c.clean_env(), timeout=120)
    rc = p.returncode
    verdict = "accept" if rc==0 and os.path.isfile(out) else ("refuse" if rc==2 and not os.path.lexists(out) else f"error({rc})")
    print(f"[{tag}] {verdict} :: {p.stderr.decode()[:130].strip()}")
direct_ignored("IG-ignore-nested", True)
direct_ignored("IG-ignore-flat", False)
# 5b. honest non-dirty with ignored file (base A vs new A WITH gitignore present → base/ new both: does new writer's -c all change visibility? ignored files stay ignored even with untrackedFiles=all)
def direct_ignored_clean(tag):
    rep, rev = c1c.build_case(os.path.join(S65, "atk"), tag, "one", {"name": tag})
    with open(os.path.join(rep, ".gitignore"), "wb") as f: f.write(b"notes.ign\n")
    with open(os.path.join(rep, "tools/notes.ign"), "wb") as f: f.write(b"ign\n")
    out = os.path.join(os.path.dirname(rep), "out", "r.txt")
    for slotname, slot in (("base", BB), ("new", NEW)):
        o = os.path.join(os.path.dirname(rep), "out", f"r-{slotname}.txt")
        p = subprocess.run([sys.executable, "-B", slot, "--root", rep, "--rev", rev, "--instrument",
                            "tools/instr.sh", "--out", o, "--allow-outside", "--", "/bin/echo", "hi"],
                           cwd=S65, capture_output=True, env=c1c.clean_env(), timeout=120)
        verdict = "accept" if p.returncode==0 and os.path.isfile(o) else ("refuse" if p.returncode==2 else f"error({p.returncode})")
        print(f"[{tag} {slotname}] {verdict} :: {p.stderr.decode()[:110].strip()}")
direct_ignored_clean("IG-clean-both")
