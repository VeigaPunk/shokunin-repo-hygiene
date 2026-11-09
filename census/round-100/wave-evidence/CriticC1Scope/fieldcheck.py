import os
def stat_fields(pid):
    with open(f"/proc/{pid}/stat","rb") as f: data=f.read()
    return data.rsplit(b")",1)[1].split()
for pid in [os.getpid(),1]:
    f=stat_fields(pid)
    print(f"pid={pid} idx0-6={[x.decode() for x in f[:7]]} os.getsid(self)={os.getsid(os.getpid())}")
