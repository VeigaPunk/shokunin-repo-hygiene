import hashlib, os
_o = hashlib.sha256
def _w(*a, **k):
    with open("/fast/scratch/hyaku/souji-r42/R42w2executor02/c2/self.hash", "a") as h: h.write("sha256\n")
    return _o(*a, **k)
hashlib.sha256 = _w
