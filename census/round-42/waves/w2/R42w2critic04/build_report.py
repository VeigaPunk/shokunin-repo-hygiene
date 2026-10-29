#!/usr/bin/env python3
"""R42w2critic04: assemble the report from report-body.md and table.tsv (the 77-row joined table)."""
import os

SEAT = os.path.dirname(os.path.abspath(__file__))
REPORT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2critic04.md"


def md_table(tsv_path):
    rows = [line.rstrip("\n").split("\t") for line in open(tsv_path, encoding="utf-8")]
    head, body = rows[0], rows[1:]
    out = ["| " + " | ".join(["mutant", "change", "killed by (landed / prior / none)", "equivalent?", "probe"]) + " |",
           "|---|---|---|---|---|"]
    for r in body:
        assert len(r) == 5, r
        out.append("| " + " | ".join(c.replace("|", "\\|") for c in r) + " |")
    return "\n".join(out)


def main():
    body = open(os.path.join(SEAT, "report-body.md"), encoding="utf-8").read()
    assert body.count("<<TABLE>>") == 1
    text = body.replace("<<TABLE>>", md_table(os.path.join(SEAT, "table.tsv")))
    with open(REPORT, "w", encoding="utf-8") as h:
        h.write(text)
    print("WROTE %s bytes=%d" % (REPORT, len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
