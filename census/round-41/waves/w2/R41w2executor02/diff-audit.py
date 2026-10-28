#!/usr/bin/env python3
"""Differential audit: run N unseen scenarios over six freeze-check candidates, report disagreement.
usage: diff-audit.py SCRATCH   (all repos built under SCRATCH)"""
import hashlib, os, subprocess, sys, random, json, shutil

W1 = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1"
TOOLS = {n: "%s/R41executor%02d/souji-freeze-check.py" % (W1, n) for n in range(7, 13)}
SC = os.path.abspath(sys.argv[1])
ENV = {"PATH": os.environ["PATH"], "TMPDIR": SC, "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0",
       "GIT_AUTHOR_NAME": "f", "GIT_AUTHOR_EMAIL": "f@x.invalid",
       "GIT_COMMITTER_NAME": "f", "GIT_COMMITTER_EMAIL": "f@x.invalid"}
rnd = random.Random(4141)
def rname(): return "".join(rnd.choice("abcdefghjkmnpqrstuvwxyz") for _ in range(6))
def sha(b): return hashlib.sha256(b if isinstance(b, bytes) else b.encode()).hexdigest()

class R:
    def __init__(s, name):
        s.d = os.path.join(SC, name); os.makedirs(s.d)
        s.g("init", "-q", "-b", "main", s.d)
        assert os.path.realpath(s.g("rev-parse", "--show-toplevel")) == os.path.realpath(s.d)
    def g(s, *a, check=True):
        p = subprocess.run(["git", "-C", s.d] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, text=True)
        if check and p.returncode: raise RuntimeError("git %s: %s" % (a, p.stderr))
        return p.stdout.strip()
    def w(s, rel, data):
        f = os.path.join(s.d, rel); os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "wb").write(data if isinstance(data, bytes) else data.encode())
    def rm(s, rel): os.remove(os.path.join(s.d, rel))
    def c(s, msg="c"):
        s.g("add", "-A"); s.g("commit", "-q", "--allow-empty", "-m", msg); return s.g("rev-parse", "HEAD")
    def head(s): return s.g("rev-parse", "HEAD")

CTR = "print('c')\n"; POP = "id\tn\n1\ta\n2\tb\n"; CON = "SUMMARY x\nEXIT=1\n"
def prereg(base, ctr="census/c.py", pop="census/p.tsv", con="census/ctl.txt", rnum="41", nl="\n",
           claims=1, head="## C%d — claim", extra=None, ctrsha=None, popsha=None, keysep=": ", hdr=True):
    L = ["# prereg"]
    if rnum is not None: L.append("Round: %s" % rnum)
    L.append("")
    for i in range(1, claims + 1):
        L.append(head % i if "%d" in head else head)
        L += ["Base%s%s" % (keysep, base),
              "Counter%s%s sha256=%s" % (keysep, ctr, ctrsha or sha(CTR)),
              "Population%s%s sha256=%s" % (keysep, pop, popsha or sha(POP)),
              "Control%s%s" % (keysep, con), "Target%sT" % keysep, "Kill%sK" % keysep]
        if extra: L += extra
        L.append("")
    return nl.join(L) + nl

def std(r, **kw):
    """base + census files + prereg(freeze). returns dict"""
    base = r.c("base"); return base
def files(r, ctr="census/c.py", pop="census/p.tsv", con="census/ctl.txt", ctext=CTR, ptext=POP, context=CON):
    r.w(ctr, ctext); r.w(pop, ptext); r.w(con, context)

S = {}
def sc(f): S[f.__name__] = f; return f
def out(r, rev=None, prereg="prereg.txt", root=None): return dict(root=root or r.d, rev=rev or r.head(), prereg=prereg)

@sc
def s01_clean(): 
    r = R("s01"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("freeze"); return out(r)
@sc
def s02_random_names():
    r = R("s02"); b = r.c("b"); n = [rname() for _ in range(4)]
    ctr, pop, con = "%s/%s.py" % (n[0], n[1]), "%s/%s.tsv" % (n[0], n[2]), "%s/%s.txt" % (n[3], n[2])
    files(r, ctr, pop, con); pn = "%s/%s.txt" % (rname(), rname())
    r.w(pn, prereg(b, ctr, pop, con)); r.c("freeze"); return out(r, prereg=pn)
@sc
def s03_crlf_prereg():
    r = R("s03"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, nl="\r\n")); r.c("f"); return out(r)
@sc
def s04_crlf_control():
    r = R("s04"); b = r.c("b"); files(r, context="SUMMARY x\r\nEXIT=1\r\n"); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s05_crlf_population_only_header():
    r = R("s05"); b = r.c("b"); p = "id\tn\r\n\r\n"; files(r, ptext=p); r.w("prereg.txt", prereg(b, popsha=sha(p))); r.c("f"); return out(r)
@sc
def s06_crlf_everything():
    r = R("s06"); b = r.c("b"); p = POP.replace("\n", "\r\n"); con = CON.replace("\n", "\r\n"); ct = CTR.replace("\n", "\r\n")
    files(r, ctext=ct, ptext=p, context=con); r.w("prereg.txt", prereg(b, nl="\r\n", ctrsha=sha(ct), popsha=sha(p))); r.c("f"); return out(r)
@sc
def s07_space_in_paths():
    r = R("s07"); b = r.c("b"); ctr = "census dir/my counter.py"; files(r, ctr=ctr)
    r.w("pre reg/prereg file.txt", prereg(b, ctr=ctr)); r.c("f"); return out(r, prereg="pre reg/prereg file.txt")
@sc
def s08_space_prereg_path_only():
    r = R("s08"); b = r.c("b"); files(r); r.w("a b/p.txt", prereg(b)); r.c("f"); return out(r, prereg="a b/p.txt")
@sc
def s09_round_missing_no_dispatch():
    r = R("s09"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, rnum=None)); r.c("f"); return out(r)
@sc
def s10_round_missing_dispatch_before():
    r = R("s10"); b = r.c("b"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("early"); files(r)
    r.w("prereg.txt", prereg(b, rnum=None)); r.c("f"); return out(r)
@sc
def s11_round_present_dispatch_before():
    r = R("s11"); b = r.c("b"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("early"); files(r)
    r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s12_same_commit_dispatch():
    r = R("s12"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("f+d"); return out(r)
@sc
def s13_same_commit_ready():
    r = R("s13"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.w(".ufo/waves/round-41/w1/x.ready", ""); r.c("f+d"); return out(r)
@sc
def s14_dispatch_after():
    r = R("s14"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("d"); return out(r)
@sc
def s15_dispatch_other_round():
    r = R("s15"); b = r.c("b"); r.w(".ufo/waves/round-40/w1-dispatch.json", "{}"); r.c("early"); files(r)
    r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s16_dispatch_nested_ready():
    r = R("s16"); b = r.c("b"); r.w(".ufo/waves/round-41/w1/seat/deep/z.ready", ""); r.c("early"); files(r)
    r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s17_merged_freeze_dispatch_on_main_before_merge():
    r = R("s17"); b = r.c("b"); r.g("checkout", "-q", "-b", "side"); files(r); r.w("prereg.txt", prereg(b)); r.c("freeze-on-side")
    r.g("checkout", "-q", "main"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("dispatch-main")
    r.g("merge", "-q", "--no-ff", "-m", "merge", "side"); return out(r)
@sc
def s18_merged_freeze_dispatch_on_side_after_freeze():
    r = R("s18"); b = r.c("b"); r.g("checkout", "-q", "-b", "side"); files(r); r.w("prereg.txt", prereg(b)); r.c("freeze")
    r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("d"); r.g("checkout", "-q", "main"); r.w("m.txt", "m"); r.c("m")
    r.g("merge", "-q", "--no-ff", "-m", "merge", "side"); return out(r)
@sc
def s19_dispatch_on_unrelated_branch_merged_after():
    r = R("s19"); b = r.c("b"); r.g("checkout", "-q", "-b", "other"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("d-other")
    r.g("checkout", "-q", "main"); files(r); r.w("prereg.txt", prereg(b)); r.c("freeze")
    r.g("merge", "-q", "--no-ff", "-m", "merge", "other"); return out(r)
@sc
def s20_prereg_added_both_branches():
    r = R("s20"); b = r.c("b"); r.g("checkout", "-q", "-b", "side"); files(r); r.w("prereg.txt", prereg(b)); r.c("freeze-side")
    r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("d-side")
    r.g("checkout", "-q", "main"); files(r); r.w("prereg.txt", prereg(b)); r.c("freeze-main")
    r.g("merge", "-q", "--no-ff", "-m", "merge", "side", check=False)
    r.g("checkout", "-q", "--ours", "."); r.c("merge") if r.g("status", "--porcelain") else None
    return out(r)
@sc
def s21_prereg_deleted_readded():
    r = R("s21"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); r.rm("prereg.txt"); r.c("del")
    r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("d"); r.w("prereg.txt", prereg(b)); r.c("re-add"); return out(r)
@sc
def s22_prereg_renamed():
    r = R("s22"); b = r.c("b"); files(r); r.w("old.txt", prereg(b)); r.c("f"); r.g("mv", "old.txt", "prereg.txt"); r.c("mv"); return out(r)
@sc
def s23_prereg_edited_after_freeze():
    r = R("s23"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); r.w("prereg.txt", prereg(b, claims=2)); r.c("edit"); return out(r)
@sc
def s24_rev_is_freeze_vs_older():
    r = R("s24"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); f = r.c("f"); r.w("z", "z"); r.c("later"); return out(r, rev=f)
@sc
def s25_rev_before_prereg():
    r = R("s25"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r, rev=b)
@sc
def s26_rev_short():
    r = R("s26"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); h = r.c("f"); return out(r, rev=h[:12])
@sc
def s27_rev_branchname():
    r = R("s27"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r, rev="main")
@sc
def s28_rev_tag_annotated():
    r = R("s28"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); h = r.c("f"); r.g("tag", "-a", "-m", "t", "v1")
    return out(r, rev=r.g("rev-parse", "v1"))
@sc
def s29_rev_tree_id():
    r = R("s29"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r, rev=r.g("rev-parse", "HEAD^{tree}"))
@sc
def s30_rev_uppercase():
    r = R("s30"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); h = r.c("f"); return out(r, rev=h.upper())
@sc
def s31_root_not_dir():
    r = R("s31"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); h = r.c("f"); return out(r, root=os.path.join(r.d, "nonexist"))
@sc
def s32_root_not_git():
    r = R("s32"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); h = r.c("f"); e = os.path.join(SC, "s32-empty"); os.makedirs(e); return out(r, root=e, rev=h)
@sc
def s33_root_subdir():
    r = R("s33"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); h = r.c("f"); return out(r, root=os.path.join(r.d, "census"), rev=h, prereg="prereg.txt")
@sc
def s34_prereg_dotslash():
    r = R("s34"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r, prereg="./prereg.txt")
@sc
def s35_prereg_empty():
    r = R("s35"); b = r.c("b"); r.w("prereg.txt", ""); r.c("f"); return out(r)
@sc
def s36_prereg_bom():
    r = R("s36"); b = r.c("b"); files(r); r.w("prereg.txt", b"\xef\xbb\xbf" + prereg(b).encode()); r.c("f"); return out(r)
@sc
def s37_prereg_latin1():
    r = R("s37"); b = r.c("b"); files(r); t = prereg(b).replace("claim", "cl\u00e4im").replace("\u2014", "-").encode("latin-1"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s38_prereg_directory():
    r = R("s38"); b = r.c("b"); files(r); r.w("prereg.txt/x", "x"); r.c("f"); return out(r)
@sc
def s39_header_variants():
    r = R("s39"); b = r.c("b"); files(r); t = prereg(b, claims=1, head="## C%d")
    r.w("prereg.txt", t + "\n## C1a — nope\nBase: x\n## C10-x\n" + "\n".join(prereg(b).splitlines()[3:]) + "\n"); r.c("f"); return out(r)
@sc
def s40_header_noSpace():
    r = R("s40"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, head="##C%d claim")); r.c("f"); return out(r)
@sc
def s41_header_h3():
    r = R("s41"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, head="### C%d claim")); r.c("f"); return out(r)
@sc
def s42_header_lowercase():
    r = R("s42"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, head="## c%d claim")); r.c("f"); return out(r)
@sc
def s43_header_c0_and_c01():
    r = R("s43"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, head="## C0%d claim")); r.c("f"); return out(r)
@sc
def s44_key_lowercase():
    r = R("s44"); b = r.c("b"); files(r); t = prereg(b).replace("Base:", "base:").replace("Kill:", "kill:"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s45_key_nospace():
    r = R("s45"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, keysep=":")); r.c("f"); return out(r)
@sc
def s46_key_tabsep_trailing_ws():
    r = R("s46"); b = r.c("b"); files(r); t = prereg(b, keysep=":\t").replace("Kill:\tK", "Kill:\tK   ").replace("T\n", "T \t\n"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s47_key_indented():
    r = R("s47"); b = r.c("b"); files(r); t = prereg(b).replace("\nTarget:", "\n  Target:"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s48_key_bulleted():
    r = R("s48"); b = r.c("b"); files(r); t = prereg(b).replace("\nTarget:", "\n- Target:").replace("\nKill:", "\n**Kill:**"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s49_duplicate_key_second_bad():
    r = R("s49"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, extra=["Base: " + "0" * 40])); r.c("f"); return out(r)
@sc
def s50_duplicate_key_first_bad():
    r = R("s50"); b = r.c("b"); files(r); t = prereg(b).replace("Base: " + b, "Base: " + "0" * 40 + "\nBase: " + b); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s51_key_inside_fence():
    r = R("s51"); b = r.c("b"); files(r); t = prereg(b).replace("\nKill: K", "\n```\nKill: K\n```"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s52_key_before_first_header():
    r = R("s52"); b = r.c("b"); files(r); r.w("prereg.txt", "Base: %s\n" % b + prereg(b)); r.c("f"); return out(r)
@sc
def s53_after_non_c_header():
    r = R("s53"); b = r.c("b"); files(r); t = prereg(b).replace("Kill: K", "## notes\nKill: K"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s54_base_short():
    r = R("s54"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b[:12])); r.c("f"); return out(r)
@sc
def s55_base_upper():
    r = R("s55"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b.upper())); r.c("f"); return out(r)
@sc
def s56_base_is_freeze_parent_merge():
    r = R("s56"); b = r.c("b"); r.g("checkout", "-q", "-b", "side"); r.w("s", "s"); sd = r.c("side"); r.g("checkout", "-q", "main")
    r.w("m", "m"); r.c("m"); r.g("merge", "-q", "--no-ff", "-m", "mg", "side"); files(r); r.w("prereg.txt", prereg(sd)); r.c("f"); return out(r)
@sc
def s57_base_equals_freeze():
    r = R("s57"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); f = r.c("f"); r.w("z", "z"); r.c("z"); r.w("prereg.txt", prereg(f)); r.c("rewrite"); return out(r)
@sc
def s58_base_tag_annotated():
    r = R("s58"); b = r.c("b"); r.g("tag", "-a", "-m", "t", "bt"); tg = r.g("rev-parse", "bt"); files(r); r.w("prereg.txt", prereg(tg)); r.c("f"); return out(r)
@sc
def s59_base_tree_or_blob_id():
    r = R("s59"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(r.g("rev-parse", "HEAD^{tree}"))); r.c("f"); return out(r)
@sc
def s60_base_later_than_freeze():
    r = R("s60"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); l = r.c("later"); r.w("prereg.txt", prereg(l)); r.c("edit"); return out(r)
@sc
def s61_counter_sha_upper():
    r = R("s61"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, ctrsha=sha(CTR).upper())); r.c("f"); return out(r)
@sc
def s62_counter_sha_short():
    r = R("s62"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, ctrsha=sha(CTR)[:40])); r.c("f"); return out(r)
@sc
def s63_counter_no_sha():
    r = R("s63"); b = r.c("b"); files(r); t = prereg(b).replace(" sha256=" + sha(CTR), ""); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s64_counter_extra_tokens():
    r = R("s64"); b = r.c("b"); files(r); t = prereg(b).replace("sha256=" + sha(CTR), "sha256=" + sha(CTR) + " (frozen)"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s65_counter_backtick():
    r = R("s65"); b = r.c("b"); files(r); t = prereg(b).replace("Counter: census/c.py sha256=" + sha(CTR), "Counter: `census/c.py` sha256=" + sha(CTR)); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s66_counter_added_after_freeze():
    r = R("s66"); b = r.c("b"); files(r); r.rm("census/c.py"); r.w("prereg.txt", prereg(b)); r.c("f"); r.w("census/c.py", CTR); r.c("later"); return out(r)
@sc
def s67_counter_deleted_after_freeze():
    r = R("s67"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); r.rm("census/c.py"); r.c("del"); return out(r)
@sc
def s68_counter_edited_then_reverted():
    r = R("s68"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); r.w("census/c.py", "x"); r.c("e"); r.w("census/c.py", CTR); r.c("rev"); return out(r)
@sc
def s69_counter_path_traversal():
    r = R("s69"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, ctr="../etc/passwd")); r.c("f"); return out(r)
@sc
def s70_counter_is_directory():
    r = R("s70"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, ctr="census")); r.c("f"); return out(r)
@sc
def s71_counter_absolute_path():
    r = R("s71"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, ctr="/census/c.py")); r.c("f"); return out(r)
@sc
def s72_counter_dotslash():
    r = R("s72"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, ctr="./census/c.py")); r.c("f"); return out(r)
@sc
def s73_pop_header_only_blank_lines():
    r = R("s73"); b = r.c("b"); p = "id\n\n   \n\t\n"; files(r, ptext=p); r.w("prereg.txt", prereg(b, popsha=sha(p))); r.c("f"); return out(r)
@sc
def s74_pop_one_line_no_newline():
    r = R("s74"); b = r.c("b"); p = "id"; files(r, ptext=p); r.w("prereg.txt", prereg(b, popsha=sha(p))); r.c("f"); return out(r)
@sc
def s75_pop_two_lines_no_trailing_nl():
    r = R("s75"); b = r.c("b"); p = "id\n1"; files(r, ptext=p); r.w("prereg.txt", prereg(b, popsha=sha(p))); r.c("f"); return out(r)
@sc
def s76_pop_empty_file():
    r = R("s76"); b = r.c("b"); p = ""; files(r, ptext=p); r.w("prereg.txt", prereg(b, popsha=sha(p))); r.c("f"); return out(r)
@sc
def s77_pop_cr_only_lines():
    r = R("s77"); b = r.c("b"); p = "id\r1\r2\r"; files(r, ptext=p); r.w("prereg.txt", prereg(b, popsha=sha(p))); r.c("f"); return out(r)
@sc
def s78_pop_binary():
    r = R("s78"); b = r.c("b"); p = b"\xff\xfe\x00\x01\n\xff\n"; files(r, ptext=p); r.w("prereg.txt", prereg(b, popsha=sha(p))); r.c("f"); return out(r)
@sc
def s79_control_exit_variants():
    r = R("s79"); b = r.c("b"); files(r, context="SUMMARY\nEXIT=1 \n\n\n"); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s80_control_exit0():
    r = R("s80"); b = r.c("b"); files(r, context="EXIT=0\n"); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s81_control_exit_00():
    r = R("s81"); b = r.c("b"); files(r, context="EXIT=00\n"); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s82_control_exit_leading_space():
    r = R("s82"); b = r.c("b"); files(r, context="x\n  EXIT=2\n"); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s83_control_exit_not_last():
    r = R("s83"); b = r.c("b"); files(r, context="EXIT=1\nSUMMARY\n"); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s84_control_empty():
    r = R("s84"); b = r.c("b"); files(r, context=""); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s85_control_with_comment_tokens():
    r = R("s85"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, con="census/ctl.txt (do-nothing stub)")); r.c("f"); return out(r)
@sc
def s86_control_edited_after_freeze():
    r = R("s86"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); r.w("census/ctl.txt", "EXIT=0\n"); r.c("e"); return out(r)
@sc
def s87_control_exit_big():
    r = R("s87"); b = r.c("b"); files(r, context="EXIT=999999999999999999999\n"); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s88_target_whitespace_only():
    r = R("s88"); b = r.c("b"); files(r); t = prereg(b).replace("Target: T", "Target:   "); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s89_target_empty_nospace():
    r = R("s89"); b = r.c("b"); files(r); t = prereg(b).replace("Target: T", "Target:"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s90_five_claims_mixed():
    r = R("s90"); b = r.c("b"); files(r); t = prereg(b, claims=5).replace("## C3 — claim\nBase: " + b, "## C3 — claim\nBase: " + "1" * 40); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s91_duplicate_claim_labels():
    r = R("s91"); b = r.c("b"); files(r); t = prereg(b, claims=2).replace("## C2", "## C1"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s92_claims_out_of_order():
    r = R("s92"); b = r.c("b"); files(r); t = prereg(b, claims=3).replace("## C1", "## C9").replace("## C2", "## C2").replace("## C3", "## C1"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s93_dispatch_filename_variants():
    r = R("s93"); b = r.c("b"); r.w(".ufo/waves/round-41/dispatch.json", "{}"); r.w(".ufo/waves/round-41/w1/ready", ""); r.w(".ufo/waves/round-41/w1/a.ready.bak", ""); r.c("early")
    files(r); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s94_dispatch_exact_names():
    r = R("s94"); b = r.c("b"); r.w(".ufo/waves/round-41/-dispatch.json", "{}"); r.c("early"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s95_dispatch_outside_ufo():
    r = R("s95"); b = r.c("b"); r.w("waves/round-41/w1-dispatch.json", "{}"); r.w("x/.ufo/waves/round-41/q.ready", ""); r.c("early"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); return out(r)
@sc
def s96_dispatch_preexisting_deleted_then_readd():
    r = R("s96"); b = r.c("b"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("early"); r.rm(".ufo/waves/round-41/w1-dispatch.json"); r.c("del")
    files(r); r.w("prereg.txt", prereg(b)); r.c("f"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("readd"); return out(r)
@sc
def s97_round_leading_zero():
    r = R("s97"); b = r.c("b"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("early"); files(r); r.w("prereg.txt", prereg(b, rnum="041")); r.c("f"); return out(r)
@sc
def s98_round_spaces_trailing():
    r = R("s98"); b = r.c("b"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("early"); files(r); t = prereg(b).replace("Round: 41", "Round:   41  "); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s99_round_crlf_dispatch_before():
    r = R("s99"); b = r.c("b"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("early"); files(r); r.w("prereg.txt", prereg(b, nl="\r\n")); r.c("f"); return out(r)
@sc
def s100_round_text_not_number():
    r = R("s100"); b = r.c("b"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("early"); files(r); r.w("prereg.txt", prereg(b, rnum="41 (r41)")); r.c("f"); return out(r)
@sc
def s101_round_two_lines():
    r = R("s101"); b = r.c("b"); r.w(".ufo/waves/round-40/w1-dispatch.json", "{}"); r.c("early"); files(r); t = prereg(b).replace("Round: 41", "Round: 40\nRound: 41"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s102_round_indented_or_in_header():
    r = R("s102"); b = r.c("b"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("early"); files(r); t = prereg(b).replace("Round: 41", "# Round 41"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s103_symlink_counter():
    r = R("s103"); b = r.c("b"); files(r); os.remove(os.path.join(r.d, "census/c.py")); os.symlink("p.tsv", os.path.join(r.d, "census/c.py"))
    r.w("prereg.txt", prereg(b, ctrsha=sha("p.tsv"))); r.c("f"); return out(r)
@sc
def s104_work_tree_dirty_differs():
    r = R("s104"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); r.w("prereg.txt", "garbage"); r.w("census/c.py", "dirty"); return out(r)
@sc
def s105_shallow_clone_rev():
    r = R("s105"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); h = r.c("f"); r.w("a", "a"); h = r.c("g")
    cl = os.path.join(SC, "s105-clone"); subprocess.run(["git", "clone", "-q", "--depth=1", "file://" + r.d, cl], env=ENV, check=True, stderr=subprocess.DEVNULL)
    return out(r, root=cl, rev=h)

@sc
def s106_bom_first_line_header():
    r = R("s106"); b = r.c("b"); files(r); t = "\n".join(prereg(b).splitlines()[3:]) + "\n"; r.w("prereg.txt", b"\xef\xbb\xbf" + ("Round: 41\n\n" + t).encode()); r.c("f"); return out(r)
@sc
def s107_unicode_linesep_in_value():
    r = R("s107"); b = r.c("b"); files(r); t = prereg(b).replace("Target: T", "Target: T\u2028Kill: smuggled\x0c## C9 phantom"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s108_formfeed_line():
    r = R("s108"); b = r.c("b"); files(r); t = prereg(b).replace("Target: T", "Target: T\x0cKill: K2"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s109_merge_commit_freeze_dispatch_in_side_before_freeze():
    r = R("s109"); b = r.c("b"); r.g("checkout", "-q", "-b", "side"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("d-side")
    r.g("checkout", "-q", "main"); files(r); r.w("prereg.txt", prereg(b)); r.c("freeze"); r.g("merge", "-q", "--no-ff", "-m", "mg", "side"); return out(r)
@sc
def s110_dispatch_side_merged_before_freeze():
    r = R("s110"); b = r.c("b"); r.g("checkout", "-q", "-b", "side"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("d-side")
    r.g("checkout", "-q", "main"); r.w("m", "m"); r.c("m"); r.g("merge", "-q", "--no-ff", "-m", "mg", "side"); files(r); r.w("prereg.txt", prereg(b)); r.c("freeze"); return out(r)
@sc
def s111_freeze_is_merge_commit_adding_prereg():
    r = R("s111"); b = r.c("b"); r.g("checkout", "-q", "-b", "side"); r.w("s", "s"); r.c("side"); r.g("checkout", "-q", "main"); r.w("m", "m"); r.c("m")
    r.g("merge", "-q", "--no-commit", "--no-ff", "side"); files(r); r.w("prereg.txt", prereg(b)); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("evil merge"); return out(r)
@sc
def s112_dispatch_in_freeze_merge_only_via_side_commit_after():
    r = R("s112"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("freeze"); r.g("checkout", "-q", "-b", "side"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("d")
    r.g("checkout", "-q", "main"); r.g("merge", "-q", "--no-ff", "-m", "mg", "side"); return out(r)
@sc
def s113_round_crlf_only_no_dispatch():
    r = R("s113"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b, nl="\r\n")); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("f+d"); return out(r)
@sc
def s114_round_bare_cr_line():
    r = R("s114"); b = r.c("b"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("early"); files(r); t = prereg(b).replace("\n", "\r"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s115_mixed_crlf_round_line_only():
    r = R("s115"); b = r.c("b"); r.w(".ufo/waves/round-41/w1-dispatch.json", "{}"); r.c("early"); files(r); t = prereg(b).replace("Round: 41\n", "Round: 41\r\n"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s116_many_random_claims_random_paths():
    r = R("s116"); b = r.c("b"); ns = [rname() for _ in range(3)]; ctr = "%s/%s.py" % (ns[0], ns[1]); pop = "%s/%s.tsv" % (ns[1], ns[2]); con = "%s.txt" % ns[2]
    files(r, ctr, pop, con); r.w("prereg.txt", prereg(b, ctr, pop, con, claims=12)); r.c("f"); return out(r)
@sc
def s117_prereg_with_leading_blank_and_trailing_nonl():
    r = R("s117"); b = r.c("b"); files(r); r.w("prereg.txt", "\n\n" + prereg(b).rstrip("\n")); r.c("f"); return out(r)
@sc
def s118_control_path_crlf_in_prereg_only_control_key():
    r = R("s118"); b = r.c("b"); files(r); t = prereg(b).replace("Control: census/ctl.txt\n", "Control: census/ctl.txt\r\n"); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s119_base_trailing_cr_only():
    r = R("s119"); b = r.c("b"); files(r); t = prereg(b).replace("Base: %s\n" % b, "Base: %s\r\n" % b); r.w("prereg.txt", t); r.c("f"); return out(r)
@sc
def s120_population_utf8_nbsp_only_line():
    r = R("s120"); b = r.c("b"); p = "id\n\u00a0\n"; files(r, ptext=p); r.w("prereg.txt", prereg(b, popsha=sha(p))); r.c("f"); return out(r)
@sc
def s121_unrelated_histories_prereg():
    r = R("s121"); b = r.c("b"); files(r); r.w("prereg.txt", prereg(b)); r.c("f"); r.g("checkout", "-q", "--orphan", "o"); r.g("rm", "-rqf", "."); r.w("o", "o"); r.c("orph")
    r.g("merge", "-q", "--allow-unrelated-histories", "-m", "mg", "main", check=False); return out(r)

def run(tool, spec):
    cmd = ["python3", "-B", tool, "--root", spec["root"], "--prereg", spec["prereg"], "--rev", spec["rev"]]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, timeout=60, cwd=SC)
    except subprocess.TimeoutExpired:
        return dict(rc="TIMEOUT", out=[], err="")
    o = p.stdout.decode("utf-8", "replace").splitlines(); e = p.stderr.decode("utf-8", "replace").strip()
    return dict(rc=p.returncode, out=o, err=e)

def norm(res, spec_rev):
    """normalize volatile hashes (12/40-hex) so differences are semantic, keep first 12 of rev positions"""
    import re
    def n(s): return re.sub(r"\b[0-9a-f]{12,40}\b", lambda m: "H%d" % len(m.group(0)), s)
    return dict(rc=res["rc"], out=[n(x) for x in res["out"]], err=n(res["err"]).splitlines()[0] if res["err"] else "",
                crash="Traceback" in res["err"])

def classes(res):
    return sorted(" ".join(l.split()[1:3]) for l in res["out"] if l.startswith("FINDING"))

def main():
    results = {}
    for name, f in S.items():
        try: spec = f()
        except Exception as ex:
            print("BUILD-FAIL", name, ex); continue
        results[name] = {"spec": spec, "tools": {n: run(t, spec) for n, t in TOOLS.items()}}
    json.dump(results, open(os.path.join(SC, "raw.json"), "w"), indent=1, default=str)
    nd = 0
    for name, r in results.items():
        sig = {n: (v["rc"], tuple(classes(v)), bool(v["err"] and v["rc"] != 2), "Traceback" in v["err"]) for n, v in r["tools"].items()}
        groups = {}
        for n, s in sig.items(): groups.setdefault(s, []).append(n)
        agree = len(groups) == 1
        if not agree: nd += 1
        print("%s %s" % ("AGREE   " if agree else "DISAGREE", name))
        for s, ns in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            rc, cl, _, tb = s
            print("   %-16s rc=%s%s %s" % (",".join("%02d" % x for x in ns), rc, " CRASH" if tb else "", list(cl)))
        if not agree:
            # also show summary/err line of 07
            v = r["tools"][7]; print("   07-stderr:", v["err"].splitlines()[0] if v["err"] else "-", "| 07-summary:", [x for x in v["out"] if x.startswith("SUMMARY")])
    print("TOTAL scenarios=%d disagree=%d" % (len(results), nd))
main()
