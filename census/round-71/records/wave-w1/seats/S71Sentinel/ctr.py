import importlib.util, os, tempfile, sys
S="/fast/scratch/hyaku/souji-r71/S71Sentinel"
spec=importlib.util.spec_from_file_location("ctr","/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-71/c1-counter.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
b=tempfile.mkdtemp(prefix="bat.",dir=S); assert b and os.path.isdir(b)
open(os.path.join(b,"M1.py"),"wb").write(b"print(1)\n")
import hashlib
sha=hashlib.sha256(b"print(1)\n").hexdigest()
open(os.path.join(b,"SHA256SUMS"),"w").write(f"{sha}  M1.py\n")
print("F3/F4 member-name traversal against verify_members:")
for name in ["../M1","M1/../M2","/etc/passwd","a/b","",".M1","..",".","M1 ","M1\n","M1", "M1.py/../../x"]:
    got=m.verify_members(b,[name])
    print(f"  name={name!r:20s} -> {'ACCEPTED '+str(list((got[0] or {}).keys())[:2]) if got[0] else 'REJECTED: '+got[1]}")
# SHA256SUMS traversal entry
print("SHA256SUMS traversal entries:")
for entry in ["../M1.py","./M1.py","a/M1.py",".hidden.py","M1.py","M1.py.py"]:
    open(os.path.join(b,"SHA256SUMS"),"w").write(f"{sha}  {entry}\n")
    got=m.verify_members(b,["M1"])
    print(f"  sums entry={entry!r:14s} -> {'ACCEPTED' if got[0] else 'REJECTED: '+got[1]}")
