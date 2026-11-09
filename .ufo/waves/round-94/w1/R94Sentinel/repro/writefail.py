"""Make --work unwritable AFTER the probe's setup checks, so the forgery-loop write fails.
Expected discipline: exit 2 + C2-FORGERY-FATAL. Observed: unhandled traceback + exit 1 (verdict code)."""
import os, subprocess, sys, time, shutil, threading
S="/fast/scratch/hyaku/souji-r94/R94Sentinel/c2"; LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
work=os.path.join(S,"wf-work"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
p=subprocess.Popen([sys.executable,"-B",os.path.join(LANE,"census/round-94/c2-forgery-probe.py"),
  "--fixture",os.path.join(LANE,"tests/fixtures/r93-k4-flagfail.py"),
  "--tool",os.path.join(LANE,"tools/souji-record-agreement.py"),
  "--before",os.path.join(LANE,"census/round-92/controls/c2-before-tool.py"),
  "--work",work],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
def adv():
    for _ in range(600):
        if os.path.exists(os.path.join(work,"positive")): break
        time.sleep(0.05)
    os.chmod(work, 0o555)   # read-only: the forgery loop's open(path,"w") now fails
threading.Thread(target=adv).start()
out,err=p.communicate(timeout=300)
print("PROBE EXIT:",p.returncode)
print("--- stderr tail ---"); print(err.decode()[-700:])
print("--- any C2-FORGERY-FATAL on stderr? ---", "C2-FORGERY-FATAL:" in err.decode())
