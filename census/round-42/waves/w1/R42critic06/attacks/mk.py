import csv
rows = [l.rstrip("\n").split("\t") for l in open("/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c1-items.tsv")][1:]
out = ["line\ttoken\tclass\tresolved_to"]
for r in rows:
    out.append("%s\t%s\tunresolved\t-" % (r[0], r[1]))
open("/fast/scratch/hyaku/souji-r42/R42critic06/c1partial/register-all-unresolved.tsv", "w").write("\n".join(out) + "\n")
print("rows", len(rows))
