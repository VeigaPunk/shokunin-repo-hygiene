#!/usr/bin/env python3
"""locate_quotes.py -- locate quotes in the tag-stripped git doc captures and
emit quotes.tsv with byte offsets, then verify every row by re-slicing.

Inputs (same directory):
  git-environment.txt   (sha256 recorded below)
  git-config.txt

Output:
  quotes.tsv   TSV, header row, columns:
      source  quote  byte_offset  txt_sha256  access_date_utc  http_status
      line_no  section  block_offset  block_text

  `quote` is ALWAYS a single verbatim line of the txt (byte-identical to the
  slice at `byte_offset`, no trailing newline).  `block_text` is the
  surrounding definitional block, also verbatim, with LF encoded as the
  two-character sequence "\\n" so the TSV stays one row per line.

Verification (run by --verify): for every row the bytes at
[byte_offset, byte_offset+len(quote)) must equal quote.encode("utf-8"), and
the bytes at [block_offset, block_offset+len(block_bytes)) must equal the
block with "\\n" decoded back to LF.  Any mismatch is a hard error.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ACCESS_DATE = "2026-11-05T15:03:48Z"
HTTP_STATUS = "200"

SOURCES = {
    "git-environment": {
        "txt": "git-environment.txt",
        "url": "https://git-scm.com/docs/git",
        "http_status": HTTP_STATUS,
    },
    "git-config": {
        "txt": "git-config.txt",
        "url": "https://git-scm.com/docs/git-config",
        "http_status": HTTP_STATUS,
    },
}

# (source, line_no, section, block_first_line, block_last_line)
ROWS = [
    # --- git(1) ENVIRONMENT VARIABLES -------------------------------------
    ("git-environment", 1048, "ENVIRONMENT VARIABLES (section heading)", 1048, 1048),
    ("git-environment", 1081, "GIT_OBJECT_DIRECTORY", 1081, 1085),
    ("git-environment", 1082, "GIT_OBJECT_DIRECTORY", 1081, 1085),
    ("git-environment", 1086, "GIT_ALTERNATE_OBJECT_DIRECTORIES", 1086, 1096),
    ("git-environment", 1089, "GIT_ALTERNATE_OBJECT_DIRECTORIES", 1086, 1096),
    ("git-environment", 1281, "GIT_CONFIG_GLOBAL / GIT_CONFIG_SYSTEM", 1281, 1289),
    ("git-environment", 1283, "GIT_CONFIG_GLOBAL / GIT_CONFIG_SYSTEM", 1281, 1289),
    ("git-environment", 1286, "GIT_CONFIG_GLOBAL / GIT_CONFIG_SYSTEM", 1281, 1289),
    ("git-environment", 1290, "GIT_CONFIG_NOSYSTEM", 1290, 1296),
    ("git-environment", 1291, "GIT_CONFIG_NOSYSTEM", 1290, 1296),
    ("git-environment", 1413, "GIT_NO_REPLACE_OBJECTS", 1413, 1415),
    ("git-environment", 1414, "GIT_NO_REPLACE_OBJECTS", 1413, 1415),
    ("git-environment", 400, "-c <name>=<value> option", 400, 402),
    ("git-environment", 401, "-c <name>=<value> option", 400, 402),
    # --- git-config(1) ---------------------------------------------------
    ("git-config", 768, "ENVIRONMENT / GIT_CONFIG_GLOBAL, GIT_CONFIG_SYSTEM", 768, 771),
    ("git-config", 770, "ENVIRONMENT / GIT_CONFIG_GLOBAL, GIT_CONFIG_SYSTEM", 768, 771),
    ("git-config", 772, "ENVIRONMENT / GIT_CONFIG_NOSYSTEM", 772, 774),
    ("git-config", 773, "ENVIRONMENT / GIT_CONFIG_NOSYSTEM", 772, 774),
    ("git-config", 776, "ENVIRONMENT / GIT_CONFIG_COUNT, GIT_CONFIG_KEY_<n>, GIT_CONFIG_VALUE_<n>", 776, 786),
    ("git-config", 777, "ENVIRONMENT / GIT_CONFIG_COUNT, GIT_CONFIG_KEY_<n>, GIT_CONFIG_VALUE_<n>", 776, 786),
    ("git-config", 778, "ENVIRONMENT / GIT_CONFIG_COUNT, GIT_CONFIG_KEY_<n>, GIT_CONFIG_VALUE_<n>", 776, 786),
    ("git-config", 779, "ENVIRONMENT / GIT_CONFIG_COUNT, GIT_CONFIG_KEY_<n>, GIT_CONFIG_VALUE_<n>", 776, 786),
    ("git-config", 784, "ENVIRONMENT / GIT_CONFIG_COUNT ... precedence of git -c", 776, 786),
    ("git-config", 785, "ENVIRONMENT / GIT_CONFIG_COUNT ... precedence of git -c", 776, 786),
    ("git-config", 786, "ENVIRONMENT / GIT_CONFIG_COUNT ... precedence of git -c", 776, 786),
    ("git-config", 717, "FILES / -c option mentioned", 715, 718),
    ("git-config", 718, "FILES / -c option mentioned", 715, 718),
    ("git-config", 724, "FILES / read order precedence", 724, 726),
    ("git-config", 746, "SCOPES / command scope", 734, 751),
    ("git-config", 747, "SCOPES / command scope", 734, 751),
    ("git-config", 749, "SCOPES / command scope", 734, 751),
    ("git-config", 2469, "core.excludesFile", 2469, 2475),
    ("git-config", 2470, "core.excludesFile", 2469, 2475),
    ("git-config", 2472, "core.excludesFile", 2469, 2475),
]


def load(name):
    path = os.path.join(HERE, name)
    with open(path, "rb") as fh:
        data = fh.read()
    sha = hashlib.sha256(data).hexdigest()
    lines = data.split(b"\n")
    offsets = []
    off = 0
    for ln in lines:
        offsets.append(off)
        off += len(ln) + 1  # + LF
    return data, sha, lines, offsets


def esc(s):
    return s.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t")


def unesc(s):
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            if n == "n":
                out.append("\n")
                i += 2
                continue
            if n == "t":
                out.append("\t")
                i += 2
                continue
            if n == "\\":
                out.append("\\")
                i += 2
                continue
        out.append(c)
        i += 1
    return "".join(out)


def build():
    cache = {}
    for src, meta in SOURCES.items():
        cache[src] = load(meta["txt"])

    out = []
    for src, lineno, section, b0, b1 in ROWS:
        data, sha, lines, offsets = cache[src]
        raw = lines[lineno - 1]
        quote = raw.decode("utf-8")
        if quote.strip() == "":
            raise SystemExit("empty line %s:%d" % (src, lineno))
        block_bytes = b"\n".join(lines[b0 - 1:b1])
        out.append({
            "source": src,
            "quote": quote,
            "byte_offset": offsets[lineno - 1],
            "txt_sha256": sha,
            "access_date_utc": ACCESS_DATE,
            "http_status": meta["http_status"],
            "line_no": lineno,
            "section": section,
            "block_offset": offsets[b0 - 1],
            "block_text": block_bytes.decode("utf-8"),
        })
    return out


HEADER = ["source", "quote", "byte_offset", "txt_sha256", "access_date_utc",
          "http_status", "line_no", "section", "block_offset", "block_text"]


def write_tsv(rows, path):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(HEADER) + "\n")
        for r in rows:
            fh.write("\t".join([
                r["source"],
                esc(r["quote"]),
                str(r["byte_offset"]),
                r["txt_sha256"],
                r["access_date_utc"],
                r["http_status"],
                str(r["line_no"]),
                esc(r["section"]),
                str(r["block_offset"]),
                esc(r["block_text"]),
            ]) + "\n")


def verify(path):
    cache = {}
    with open(path, encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        if header != HEADER:
            raise SystemExit("header mismatch: %r" % (header,))
        n = 0
        bad = 0
        for raw in fh:
            raw = raw.rstrip("\n")
            if not raw:
                continue
            n += 1
            f = raw.split("\t")
            if len(f) != len(HEADER):
                raise SystemExit("row %d: expected %d fields, got %d" % (n, len(HEADER), len(f)))
            src, quote, byte_offset, sha, acc, status, lineno, section, block_offset, block_text = f
            if src not in cache:
                cache[src] = load(SOURCES[src]["txt"])
            data, real_sha, lines, offsets = cache[src]
            if real_sha != sha:
                raise SystemExit("row %d: sha mismatch for %s" % (n, src))
            if int(byte_offset) != offsets[int(lineno) - 1]:
                raise SystemExit("row %d: offset != line offset" % n)
            q = unesc(quote)
            if data[int(byte_offset):int(byte_offset) + len(q.encode("utf-8"))] != q.encode("utf-8"):
                raise SystemExit("row %d: quote slice mismatch" % n)
            bt = unesc(block_text)
            bb = bt.encode("utf-8")
            if data[int(block_offset):int(block_offset) + len(bb)] != bb:
                raise SystemExit("row %d: block slice mismatch" % n)
            if len(q.split()) > 25:
                raise SystemExit("row %d: quote exceeds 25 words" % n)
        sys.stderr.write("verify: %d rows, all offsets re-sliced and byte-compared OK\n" % n)
        return n


def main(argv):
    out = os.path.join(HERE, "quotes.tsv")
    if "--verify" in argv:
        verify(out)
        return 0
    rows = build()
    write_tsv(rows, out)
    verify(out)
    sys.stderr.write("wrote %s (%d rows)\n" % (out, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
