import subprocess,hashlib
R="/home/vgpnk/Projects/shokunin/souji-shokunin"
def g(*a): return subprocess.run(["git","-C",R]+list(a),capture_output=True)
targets={}
pref={"65817d0d":"L14","09bb8e0d":"L92"}
# all blobs in all history
objs=g("rev-list","--objects","--all").stdout.decode().splitlines()
print("objects listed",len(objs))
oids=[l.split()[0] for l in objs]
# batch-check for blobs
chk=subprocess.run(["git","-C",R,"cat-file","--batch-check"],input="\n".join(oids).encode(),capture_output=True).stdout.decode().splitlines()
blobs=[(l.split()[0],int(l.split()[2])) for l in chk if l.split()[1]=="blob"]
path={}
for l in objs:
    p=l.split(" ",1)
    if len(p)==2: path.setdefault(p[0],p[1])
print("blobs",len(blobs))
pr=subprocess.Popen(["git","-C",R,"cat-file","--batch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
import threading
def feed():
    for o,_ in blobs: pr.stdin.write((o+"\n").encode())
    pr.stdin.close()
threading.Thread(target=feed,daemon=True).start()
hits=[]
for o,sz in blobs:
    hdr=pr.stdout.readline(); data=pr.stdout.read(sz+1)[:sz]
    h=hashlib.sha256(data).hexdigest()
    if h in targets: hits.append((targets[h],"FULL",o,path.get(o)))
    for p,n in pref.items():
        if h.startswith(p): hits.append((n,"PREFIX",h,o,path.get(o)))
print(hits)
