import os
S = os.environ["S"]
src = open("/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-receipt-write.py", encoding="utf-8").read()
anchor = "    # behaviour 7: clean lane tree unless --allow-dirty\n"
assert src.count(anchor) == 1, "anchor"
block = (
    "    # C1 candidate (round 62): index-flag concealment, unconditional\n"
    "    fl = git(root, \"ls-files\", \"-v\", \"-z\")\n"
    "    if fl.returncode != 0:\n"
    "        refuse(f\"cannot read index flags of {root}: {fl.stderr.decode('utf-8', 'replace').strip()}\")\n"
    "    for rec in fl.stdout.split(b\"\\0\"):\n"
    "        if not rec:\n"
    "            continue\n"
    "        tag = rec[:1]\n"
    "        if tag != b\"H\":\n"
    "            path = rec[2:].decode(\"utf-8\", \"replace\")\n"
    "            refuse(f\"RECEIPT-INDEX-FLAG-CONCEALED: {path} carries index tag {tag.decode('ascii', 'replace')}; worktree state is not verifiable\")\n"
)
open(os.path.join(S, "cand.py"), "w", encoding="utf-8").write(src.replace(anchor, block + anchor))
print("cand built")
