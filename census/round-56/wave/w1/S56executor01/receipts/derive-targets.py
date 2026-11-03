#!/usr/bin/env python3
"""Independent T1-T5 derivation over the two committed C1 matrix TSVs.

No counter code, no fixture builder, no import of counter logic: plain TSV
parse. Prints one literal evidence line per assertion.
"""
import sys

V4 = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-56/records/c1-matrix-v4.tsv"
V5 = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-56/records/c1-matrix-v5.tsv"


def load(path):
    rows = {}
    with open(path, "rb") as fh:
        raw = fh.read().decode("utf-8")
    lines = raw.splitlines()
    hdr = lines[0].split("\t")
    assert hdr == ["fixture", "counter", "rev", "base", "exit", "finding", "SUMMARY"], hdr
    for ln in lines[1:]:
        c = ln.split("\t")
        assert len(c) == 7, c
        rows[c[0]] = {"exit": int(c[4]), "finding": c[5], "summary": c[6], "line": ln}
    return rows


v4, v5 = load(V4), load(V5)
assert set(v4) == set(v5), (set(v4) ^ set(v5))
names = sorted(v4)

fails = []


def check(tid, cond, evidence):
    print("%s %s %s" % (tid, "PASS" if cond else "FAIL", evidence))
    if not cond:
        fails.append(tid)


# T1: {v4 exit 0 and v5 exit != 0} EXACTLY {F24,F26,F28} with prescribed findings
t1 = sorted(n for n in names if v4[n]["exit"] == 0 and v5[n]["exit"] != 0)
want1 = ["F24-PAIR-HIDDEN-FILING", "F26-INDENT4-COMMENT-OPENER", "F28-NUL-CORRECTION-UNCHANGED"]
want1_finding = {
    "F24-PAIR-HIDDEN-FILING": "UNFILED-SOURCES-ANNOTATION",
    "F26-INDENT4-COMMENT-OPENER": "UNFILED-SOURCES-ANNOTATION",
    "F28-NUL-CORRECTION-UNCHANGED": "CORRECTION-FILE-BINARY",
}
print("T1 SET %s" % ",".join(t1))
check("T1", t1 == want1, "want_set=%s got_set=%s" % (",".join(want1), ",".join(t1)))
for n in want1:
    check("T1", v5[n]["finding"] == want1_finding[n],
          "%s v4_exit=%d v5_exit=%d v5_finding=%s want=%s" %
          (n, v4[n]["exit"], v5[n]["exit"], v5[n]["finding"], want1_finding[n]))
    check("T1", v5[n]["exit"] != 0, "%s v5_exit=%d (must be non-zero)" % (n, v5[n]["exit"]))
# F24 also prints PAIR-FILING-HIDDEN: the matrix keeps only the first FINDING
# line, so the pair-hidden print is asserted from the counter's SUMMARY flag.
check("T1", "pairhidden=1" in v5["F24-PAIR-HIDDEN-FILING"]["summary"],
      "F24 v5 SUMMARY flag pairhidden=1 present=%s" %
      ("pairhidden=1" in v5["F24-PAIR-HIDDEN-FILING"]["summary"]))
print("T1 LITERAL_V5_F24 %s" % v5["F24-PAIR-HIDDEN-FILING"]["line"])
print("T1 LITERAL_V5_F26 %s" % v5["F26-INDENT4-COMMENT-OPENER"]["line"])
print("T1 LITERAL_V5_F28 %s" % v5["F28-NUL-CORRECTION-UNCHANGED"]["line"])
print("T1 LITERAL_V4_F24 %s" % v4["F24-PAIR-HIDDEN-FILING"]["line"])
print("T1 LITERAL_V4_F26 %s" % v4["F26-INDENT4-COMMENT-OPENER"]["line"])
print("T1 LITERAL_V4_F28 %s" % v4["F28-NUL-CORRECTION-UNCHANGED"]["line"])

# T2: F27 v5 exit 1 first finding DELETIONS-UNREADABLE-BINARY
n = "F27-BINARY-NUMSTAT"
check("T2", v5[n]["exit"] == 1 and v5[n]["finding"] == "DELETIONS-UNREADABLE-BINARY",
      "%s v5_exit=%d v5_finding=%s want=1/DELETIONS-UNREADABLE-BINARY" %
      (n, v5[n]["exit"], v5[n]["finding"]))
print("T2 LITERAL_V5 %s" % v5[n]["line"])
print("T2 LITERAL_V4 %s" % v4[n]["line"])

# T3: F7-FF2 v5 exit 1 first finding CORRECTION-IN-FENCE
n = "F7-FF2"
check("T3", v5[n]["exit"] == 1 and v5[n]["finding"] == "CORRECTION-IN-FENCE",
      "%s v5_exit=%d v5_finding=%s want=1/CORRECTION-IN-FENCE" %
      (n, v5[n]["exit"], v5[n]["finding"]))
print("T3 LITERAL_V5 %s" % v5[n]["line"])

# T4: {v4 exit != 0 and v5 exit 0} EXACTLY {F29}
t4 = sorted(n for n in names if v4[n]["exit"] != 0 and v5[n]["exit"] == 0)
want4 = ["F29-PROSE-COMMENT-MENTION"]
check("T4", t4 == want4, "want_set=%s got_set=%s" % (",".join(want4), ",".join(t4)))
print("T4 LITERAL_V4 %s" % v4[want4[0]]["line"])
print("T4 LITERAL_V5 %s" % v5[want4[0]]["line"])
# honest over-hide states remain exit 0 under both
for n in ("F17-INDENT4-FENCE", "F18-BTINFO-FENCE", "F19-PAIR-IN-FENCE"):
    check("T4", v4[n]["exit"] == 0 and v5[n]["exit"] == 0,
          "%s v4_exit=%d v5_exit=%d (both 0)" % (n, v4[n]["exit"], v5[n]["exit"]))

# T5: every other fixture identical exit and first finding
covered = set(want1) | {"F27-BINARY-NUMSTAT", "F7-FF2"} | set(want4)
rest = [n for n in names if n not in covered]
print("T5 ROWS n=%d %s" % (len(rest), ",".join(rest)))
for n in rest:
    ok = v4[n]["exit"] == v5[n]["exit"] and v4[n]["finding"] == v5[n]["finding"]
    check("T5", ok, "%s v4=%d/%s v5=%d/%s" % (n, v4[n]["exit"], v4[n]["finding"],
                                              v5[n]["exit"], v5[n]["finding"]))
# 33 fixtures minus the 6 covered by T1/T2/T3/T4 = 27; the prereg T5 enumeration
# (F1-F23, F7-FF, F12b, F12c, F8b) is the same 27-row complement.
check("T5", len(rest) == 27, "complement_rows=%d want=27" % len(rest))
print("T5 POPULATION rows_v4=%d rows_v5=%d" % (len(v4), len(v5)))

print("OVERALL %s" % ("PASS" if not fails else "FAIL:" + ",".join(sorted(set(fails)))))
sys.exit(0 if not fails else 1)
