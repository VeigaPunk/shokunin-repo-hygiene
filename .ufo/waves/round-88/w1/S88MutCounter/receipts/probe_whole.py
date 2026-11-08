import importlib.util, sys
sys.dont_write_bytecode = True
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
P = load("counter.py", "pc")
src = open("counter.py", encoding="utf-8").read()
old = "        before_ok = i == 0 or line[i - 1] not in PATHCH"
new = "        before_ok = i == 0 or not line[i - 1:i].isalnum()  # m18b"
assert src.count(old) == 1
open("counter_m18b.py", "w", encoding="utf-8").write(src.replace(old, new))
M = load("counter_m18b.py", "pc_m18b")
TOK = b"tests/vault/vadv54-run/p/p6repo/.git"
TGT = b".ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/git-stub"
print("_whole(TOKEN) predecessor table (line = '- ' + pre + TOKEN + '; slot ' + TGT + '.')")
for label, pre in [("line-start", b""), ("tab", b"\t"), ("space", b" "), ("slash", b"vendor/"),
                   ("dot", b"vendor."), ("underscore", b"vendor_"), ("dash", b"vendor-"),
                   ("at", b"vendor@"), ("plus", b"vendor+"), ("tilde", b"vendor~"), ("alnum", b"vendorx")]:
    line = b"- " + pre + TOK + b"; slot " + TGT + b".\n"
    print(f"  before={label:10s} pristine={P._whole(TOK, line)!s:5s} m18b-alnum-only={M._whole(TOK, line)!s:5s}")
print("PATHCH =", bytes(sorted(P.PATHCH)))
