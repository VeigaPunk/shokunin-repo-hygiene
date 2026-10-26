#!/usr/bin/env python3
"""sweep-c2-suppressions.py — quantify what the r31 C2 tokenizer rules suppress
on real lane content (rounds 18-30, the rounds whose pointer pass runs).

Usage:
  python3 -B sweep-c2-suppressions.py --root <lane> --rev <full40> \
      --gate <path to tools/souji-landing-gate.py> [--json OUT]

The gate module is imported by path and its own regexes/predicates are used,
so every class below is the gate's decision, not a paraphrase of it.

Classes counted (occurrence and distinct source:line:token):
  S1 prose     — absent token whose every component is letters-only: the tip
                 gate suppresses it silently (`_prose_pointer`).
  S2 ellipsis  — whole token skipped because it holds `…` (base rule) or `...`
                 (r31 rule). For each, the sweep tests whether the token minus
                 its dots resolves: a real citation the rule hides.
  S3 text      — token whose `:<text>` suffix the r31 trim removes. If the
                 removed suffix itself starts with a pointer root (or contains
                 `/` and an extension) it is a dropped second path.
  S4 printf    — token skipped by TEMPLATE_POINTER_RE's r31 widening (%d/...).
Quotation marks are excluded by the gate regex, so no pipe/quote handling here.
"""
import argparse
import collections
import importlib.util
import json
import os
import re
import sys

ROOT_RE = re.compile(
    r"(?<![A-Za-z0-9_./<>*])(?:(?:\.\./)+|\./)?"
    r"(?:census|tests|tools|corpus|\.ufo/waves|\.ufo/quarantine)/[^\s`\"'()\[\]]+"
)
TEXT_SUFFIX_RE = re.compile(r":(?![0-9])[^:\s]*$")
TEMPLATE_NEW_RE = re.compile(r"%[-+ #0]*\d*(?:\.\d+)?[diouxXeEfFgGaAcsp%]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--gate", required=True)
    ap.add_argument("--json")
    ap.add_argument("--from-round", type=int, default=18)
    ap.add_argument("--to-round", type=int, default=30)
    args = ap.parse_args()

    spec = importlib.util.spec_from_file_location("gt", args.gate)
    gt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gt)

    root = args.root
    rev = gt.resolve_commit(root, args.rev)
    tree = gt.list_tree(root, rev)
    tree_paths = set(tree)
    for path in tree:
        parent = os.path.dirname(path)
        while parent:
            tree_paths.add(parent)
            parent = os.path.dirname(parent)

    seen = set()
    classes = collections.defaultdict(list)
    for round_no in range(args.from_round, args.to_round + 1):
        sources = {
            p for p in (
                "SKILL.md", "SHONEN.md", "SCORECARD.md", "PROVINCE.md",
                "corpus/QUALITY.md", "corpus/README.md",
                "corpus/lessons/round-%d.md" % round_no,
                "corpus/lessons/round-%d-verifier-spotcheck.md" % round_no,
            ) if p in tree
        }
        sources.update(
            p for p in tree
            if p.startswith("corpus/knowledge/") and p.count("/") == 2
            and p.endswith(".md")
        )
        lines = []
        for source in sorted(sources):
            text = gt.blob_by_oid(root, tree[source]).decode("utf-8", "replace")
            lines.extend((source, n, line) for n, line in enumerate(text.splitlines(), 1))
        if "LOG.md" in tree:
            log_text = gt.blob_by_oid(root, tree["LOG.md"]).decode("utf-8", "replace")
            lines.extend(("LOG.md", n, line) for n, line in gt._round_log_lines(log_text, round_no))

        for source, line_no, line in lines:
            key = (source, line_no)
            if key in seen:
                continue
            seen.add(key)
            for match in gt.POINTER_PATH_RE.finditer(line):
                raw = match.group(0)
                rid = "%s:%d" % (source, line_no)

                # S2 ellipsis (whole token)
                if "…" in raw or "..." in raw:
                    stripped = raw.replace("…", "").rstrip(".")
                    exists = gt._path_exists_in_tree(stripped, tree_paths) if stripped else False
                    tail = stripped.rsplit("/", 1)[-1] if stripped else ""
                    basename_hits = [
                        p for p in tree
                        if tail and p.endswith("/" + tail)
                    ]
                    classes["S2-ellipsis"].append({
                        "id": rid, "raw": raw, "stripped": stripped,
                        "stripped_exists": exists,
                        "basename_matches": basename_hits[:3],
                        "rule": "dots" if "..." in raw else "char",
                    })
                    continue

                # split at commas outside braces (gate's rule)
                parts, depth, start = [], 0, 0
                for index, char in enumerate(raw):
                    if char == "{":
                        depth += 1
                    elif char == "}":
                        depth -= 1
                    elif char == "," and depth == 0:
                        parts.append(raw[start:index])
                        start = index + 1
                parts.append(raw[start:])
                for part in parts:
                    if TEXT_SUFFIX_RE.search(part):
                        suffix = TEXT_SUFFIX_RE.search(part).group(0)[1:]
                        base = gt._trim_pointer_token(part)
                        suffix_pathlike = bool(ROOT_RE.search(suffix) or (
                            "/" in suffix and "." in suffix.rsplit("/", 1)[-1]
                        ))
                        if suffix:
                            classes["S3-text"].append({
                                "id": rid, "part": part, "kept": base,
                                "dropped": suffix,
                                "dropped_pathlike": suffix_pathlike,
                                "dropped_exists": gt._path_exists_in_tree(suffix, tree_paths),
                                "kept_exists": gt._path_exists_in_tree(base, tree_paths),
                            })
                    if TEMPLATE_NEW_RE.search(part):
                        classes["S4-printf"].append({"id": rid, "part": part})
                    path = gt._trim_pointer_token(part)
                    if not path or TEMPLATE_NEW_RE.search(path):
                        continue
                    normalized = gt._normalize_pointer_path(path, source)
                    exists = gt._path_exists_in_tree(normalized, tree_paths) or any(
                        gt._path_exists_in_tree(c, tree_paths)
                        for c in gt._pointer_candidates(normalized)
                    )
                    if not exists and gt._prose_pointer(normalized):
                        classes["S1-prose"].append({
                            "id": rid, "path": normalized,
                            "multiplied": normalized.count("/") > 1,
                        })

    summary = {}
    for name in sorted(classes):
        rows = classes[name]
        distinct = {(r["id"], r.get("raw") or r.get("part")) for r in rows}
        summary[name] = {"occurrences": len(rows), "distinct": len(distinct)}
        print("%-12s occurrences=%-4d distinct=%d" % (name, len(rows), len(distinct)))
        for row in rows:
            print("   ", json.dumps(row, ensure_ascii=False, sort_keys=True))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"rev": rev, "classes": {k: v for k, v in classes.items()},
                       "summary": summary}, fh, indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
