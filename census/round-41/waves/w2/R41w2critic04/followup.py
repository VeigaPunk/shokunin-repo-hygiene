import json, os, shutil, signal, subprocess, sys, time

sys.path.insert(0, "/fast/scratch/hyaku/souji-r41/R41w2critic04")
import kill_matrix as km  # reuses the same shim, modes() and session helpers

S, FIX, TOOL, SHIM = km.S, km.FIX, km.TOOL, km.SHIM
ENV = dict(km.BASE_ENV, SHIM_SLEEP="0.5")
out = {}

# F1: SIGKILL leftover, then STRICT shutil.rmtree (no ignore_errors) must succeed.
w = S + "/F1 strict-rmtree work"
os.makedirs(w, exist_ok=True)
p = subprocess.Popen(["python3", "-B", FIX, "--tool", SHIM, "--work", w], stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, env=ENV, start_new_session=True)
time.sleep(1.5)
os.killpg(p.pid, signal.SIGKILL)
p.communicate()
before = km.modes(w)
try:
    shutil.rmtree(w)
    strict = "shutil.rmtree strict: OK"
except Exception as ex:
    strict = "shutil.rmtree strict: FAIL %r" % ex
out["F1"] = dict(leftover_before=before[:3] + ["..."] + [b for b in before if "denied" in b or "/ro" in b], strict=strict,
                 gone=not os.path.exists(w))

# F2: kill ONLY the fixture pid (not its group). Does its shim child keep running and touch W after cleanup?
w2 = S + "/F2 parent-only-kill work"
os.makedirs(w2, exist_ok=True)
p2 = subprocess.Popen(["python3", "-B", FIX, "--tool", SHIM, "--work", w2], stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE, text=True, env=ENV, start_new_session=True)
time.sleep(1.5)
os.kill(p2.pid, signal.SIGKILL)
p2.communicate()
alive_children = km.session_members(p2.pid)
shutil.rmtree(w2, ignore_errors=True)  # cleanup happens while the shim child is still alive
time.sleep(2.5)
recreated = os.path.exists(w2) and km.modes(w2)
alive_after = km.session_members(p2.pid)
out["F2"] = dict(children_alive_after_parent_kill=alive_children, children_alive_after_2_5s=alive_after,
                 recreated_under_W_after_cleanup=recreated, gone=not os.path.exists(w2))
for pid in alive_after:
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass

# F3: two concurrent runs share one --work; kill run A, run B must still PASS and cleanup of A's tree must not touch B.
w3 = S + "/F3 shared-kill work"
os.makedirs(w3, exist_ok=True)
pa = subprocess.Popen(["python3", "-B", FIX, "--tool", SHIM, "--work", w3], stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE, text=True, env=ENV, start_new_session=True)
pb = subprocess.Popen(["python3", "-B", FIX, "--tool", TOOL, "--work", w3], stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE, text=True, env=dict(km.BASE_ENV), start_new_session=True)
time.sleep(1.0)
os.killpg(pa.pid, signal.SIGKILL)
pa.communicate()
ob, eb = pb.communicate(timeout=300)
summ_b = [l for l in ob.splitlines() if l.startswith("SUMMARY")]
out["F3"] = dict(b_rc=pb.returncode, b_summary=summ_b, b_err=eb[-200:], work_after=sorted(os.listdir(w3)))

# F4: strace presence (to check fixture writes only under --work)
out["F4-strace"] = shutil.which("strace") or "absent"

with open(S + "/logs/followup.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
