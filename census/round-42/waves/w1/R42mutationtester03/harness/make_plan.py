#!/usr/bin/env python3
"""R42mutationtester03 plan writer. Stage A: every mutant on the three core inputs (absent fixture, the
two committed stubs) and the identity reference M00 on every input. Stage B: each mutant on the inputs
that exercise the branch it changes (TARGET). Writes plan-A.txt and plan-B.txt into the seat harness dir."""
import json
import os

HARNESS = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester03/harness"
SEAT = os.path.dirname(HARNESS)
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42mutationtester03"
CORE = ["IN01-ABSENT", "IN02-ALLPASS", "IN03-SNIFF"]
SKIP = {"M58"}  # byte-identical to M10 (same sha256 prefix in mutants.json)
TARGET = {
    "M01": ["IN05-RC2"], "M02": ["IN08-FAIL0"], "M03": ["IN06-TB"], "M04": ["IN10-INCONS"],
    "M05": ["IN08-FAIL0"], "M06": ["IN13-TBCLEAN"], "M07": ["IN11-TWO"], "M09": ["IN12-SLOW"],
    "M11": ["IN06-TB"], "M13": ["IN07-NOSUM"], "M21": ["IN09-TWELVE"],
    "M23": ["IN08-FAIL0", "IN10-INCONS"], "M25": ["IN16-PRIORGONE"], "M26": ["IN15-PRIORFAIL"],
    "M28": ["IN20-SYNTHMET"], "M29": ["IN20-SYNTHMET"], "M33": ["IN17-ANCHORDIG"],
    "M36": ["IN19-SHORTREV"], "M37": ["IN21-BADREV"], "M42": ["IN14-PRIORKILL"],
    "M43": ["IN14-PRIORKILL"], "M53": ["IN16-PRIORGONE"], "M61": ["IN22-FAILRC0"],
    "M52": ["IN15-PRIORFAIL"], "M10": ["IN06-TB", "IN13-TBCLEAN"], "M27": ["IN18-TOOLDIFF"],
    "M19": ["IN21-BADREV"], "M20": ["IN21-BADREV"], "M14": ["IN04-PARTIAL"],
    "M15": ["IN14-PRIORKILL"], "M16": ["IN14-PRIORKILL"], "M22": ["IN02-ALLPASS"],
    "M24": ["IN03-SNIFF"], "M35": ["IN09-TWELVE"], "M34": ["IN11-TWO"], "M38": ["IN18-TOOLDIFF"],
    "M39": ["IN18-TOOLDIFF"], "M71": ["IN18-TOOLDIFF"], "M41": ["IN04-PARTIAL"],
}


def main():
    with open(os.path.join(SCRATCH, "inputs.json")) as h:
        inputs = sorted(json.load(h))
    with open(os.path.join(SEAT, "harness", "mutants.json")) as h:
        muts = [m["id"] for m in json.load(h) if m["id"] not in SKIP]
    a = ["M00 " + i for i in inputs] + ["%s %s" % (m, i) for m in muts if m != "M00" for i in CORE]
    b = []
    for m, targets in TARGET.items():
        for i in targets:
            if i not in CORE:
                b.append("%s %s" % (m, i))
    with open(os.path.join(SEAT, "harness", "plan-A.txt"), "w") as h:
        h.write("\n".join(a) + "\n")
    with open(os.path.join(SEAT, "harness", "plan-B.txt"), "w") as h:
        h.write("\n".join(sorted(set(b))) + "\n")
    print("plan-A cells=%d plan-B cells=%d" % (len(a), len(set(b))))


if __name__ == "__main__":
    main()
