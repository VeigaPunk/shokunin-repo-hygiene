#!/usr/bin/env python3
"""S16 round-8 pointer sweep — independent token extraction (mechanical).

Sources: .ufo/reports/round-{1..7}/souji.md (fleet root), souji-shokunin/LOG.md,
souji-shokunin/SCORECARD.md. Tokenization + classification are regex-mechanical;
no token list is copied from any prior seat. Output: seat-16-inventory.json
(raw candidates + classification). Verification happens in a second pass.

Rules honored: existence checks only (no file content reads of referenced
targets); .ufo/state and watchdog.log never probed; secret-shaped path
components refused without probing.
"""
import json
import os
import re
import sys

FLEET = "/home/vgpnk/Projects/shokunin"
LANE = FLEET + "/souji-shokunin"

SOURCES = []
for i in range(1, 8):
    SOURCES.append((FLEET + "/.ufo/reports/round-%d/souji.md" % i, "R%d" % i))
SOURCES.append((LANE + "/LOG.md", "LG"))
SOURCES.append((LANE + "/SCORECARD.md", "SC"))

SECRET_RX = re.compile(
    r"(^|/)(?:\.env(\..*)?|\.envrc|.*credential.*|.*secret.*|id_.+|.*\.pem)$",
    re.IGNORECASE,
)
FORBIDDEN_RX = re.compile(r"^\.*/*\.ufo/state(/|$)|watchdog\.log$")

HEX_RX = re.compile(r"\b[0-9a-f]{7,64}(?:\u2026|…)?\b")
REF_RX = re.compile(
    r"\b(?:refs/(?:heads|remotes|tags)/[\w./+-]+|origin/(?:master|main|HEAD))\b"
)
URL_RX = re.compile(r"https?://[^\s)\]>\"'`,]+")
PATH_RX = re.compile(
    r"(?:\.{1,2}|~|\$[A-Z_][A-Z0-9_]*)?/?(?:[\w.@+-]+/)+[\w.@+*?-]*"
)

TRAIL = ".,;:)"

def strip_tok(t):
    t = t.rstrip(TRAIL).rstrip("/")
    if t.endswith("**") and t[-3:-2].isalnum():
        t = t[:-2]  # markdown bold closer, not a glob
    return t

def path_class(tok):
    if "*" in tok or ".." in tok.replace("../", ""):
        return "fs:glob"
    return "fs:path"

def hex_class(tok, line):
    core = tok.rstrip("\u2026…")
    followed_by_ellipsis = (tok + "\u2026") in line or (tok + "…") in line
    if followed_by_ellipsis and len(core) >= 8:
        return "digest"
    if len(core) >= 41:
        return "digest"
    # truncated digest cited next to a 'sha' mention, not a commit context
    if 8 <= len(core) <= 16 and re.search(r"sha", line, re.IGNORECASE):
        return "digest"
    # calendar-date-like substrings that occur inside filenames on this line
    if re.fullmatch(r"20\d{6}", core) and re.search(
            r"[\w.-]*" + core, line) and not re.search(
            r"\bcommit\b.*" + core, line):
        return "nonpointer:date"
    return "git:commit" if 7 <= len(core) <= 40 else "ignore"

MODEL_HEADS = {
    "devin", "openai-codex", "xai-oauth", "zai-coding-plan",
    "opencode-go", "glm", "gpt", "grok",
}
LABEL_RX = re.compile(
    r"^(?:S\d{1,2}|impl-\d+|F\d+|final-\d+|seat-\d+|case-F\d+|"
    r"C\d|O\d+|K\d|V\d(?:-\d)?|D\d|P\d{2}|\d+/\d+|r\d{1,2}|v\d+)$"
)

def classify(tok, line):
    if REF_RX.fullmatch(tok):
        return "git:ref"
    if tok.startswith("github.com/") or URL_RX.fullmatch(tok):
        return "remote:url"
    if re.fullmatch(r"\d+/\d+", tok):
        return "nonpointer:fraction"
    if LABEL_RX.match(tok):
        return "nonpointer:label"
    if "/" not in tok and "." not in tok:
        if HEX_RX.fullmatch(tok):
            return hex_class(tok, line)
        return None
    if "/" in tok:
        head = tok.split("/")[0]
        if any(head.startswith(h) for h in MODEL_HEADS):
            return "nonpointer:model"
        return path_class(tok)
    if HEX_RX.fullmatch(tok):
        return hex_class(tok, line)
    return None

def main():
    tokens = {}  # (kind, token) -> {"locations": [...]}
    for path, tag in SOURCES:
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.rstrip("\n")
                found = set()
                for rx in (REF_RX, URL_RX, PATH_RX, HEX_RX):
                    for m in rx.finditer(line):
                        tok = strip_tok(m.group(0))
                        if tok:
                            found.add(tok)
                for tok in found:
                    kind = classify(tok, line)
                    if kind in (None, "ignore"):
                        continue
                    key = (kind, tok)
                    loc = "%s:%d" % (tag, lineno)
                    tokens.setdefault(key, {"kind": kind, "locations": []})
                    if loc not in tokens[key]["locations"]:
                        tokens[key]["locations"].append(loc)

    inventory = []
    for (kind, tok), meta in sorted(tokens.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        inventory.append({
            "kind": kind,
            "token": tok,
            "locations": meta["locations"],
        })
    out = LANE + "/census/round-8/seat-16-inventory.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({
            "sources": [p for p, _ in SOURCES],
            "token_count": len(inventory),
            "tokens": inventory,
        }, fh, indent=1)
    counts = {}
    for e in inventory:
        counts[e["kind"]] = counts.get(e["kind"], 0) + 1
    print("token_count:", len(inventory))
    for k in sorted(counts):
        print("%-18s %d" % (k, counts[k]))
    print("wrote", out)

if __name__ == "__main__":
    sys.exit(main())
