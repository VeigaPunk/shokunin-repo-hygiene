#!/usr/bin/env python3
"""absences.py -- mechanical absence check for needles that the round-66
C1 rows depend on but that are NOT defined in the captured man pages.

For each (needle, doc) pair this script searches the *tag-stripped text*
(the same bytes quotes.tsv anchors into) and the *raw HTML* (both with tags
stripped via the same recipe, and raw) and records the counts.  A needle
with count 0 in the stripped text is reported ABSENT; the script never
paraphrases a needle into a substitute sentence.

Output: absences.tsv
    needle  source  stripped_text_count  raw_html_count  status  note
"""

import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

DOCS = {
    "git-environment": ("git-environment.txt", "git-environment.html",
                        "https://git-scm.com/docs/git"),
    "git-config": ("git-config.txt", "git-config.html",
                   "https://git-scm.com/docs/git-config"),
}

# needles the round-66 C1 rows name, plus the neighbours the task asks for
NEEDLES = [
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_KEY_",
    "GIT_CONFIG_VALUE_",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_CONFIG_SYSTEM",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_REPLACE_REF_BASE",
    "GIT_NO_REPLACE_OBJECTS",
    "core.excludesFile",
]

NOTES = {
    ("GIT_CONFIG_PARAMETERS", "git-environment"): (
        "not defined in git(1); upstream it exists only as an internal "
        "propagation channel (environment.h CONFIG_DATA_ENVIRONMENT, "
        "config.h git_config_append_parameter, RelNotes/2.31.0.adoc:129)"),
    ("GIT_CONFIG_PARAMETERS", "git-config"): (
        "not defined in git-config(1); upstream it exists only as an "
        "internal propagation channel (environment.h CONFIG_DATA_ENVIRONMENT, "
        "config.h git_config_append_parameter, RelNotes/2.31.0.adoc:129)"),
    ("GIT_REPLACE_REF_BASE", "git-environment"): (
        "not defined in git(1); upstream it is only in RelNotes/2.6.0.adoc:44 "
        "and in the source (refs.c:149 comment, environment.h "
        "GIT_REPLACE_REF_BASE_ENVIRONMENT)"),
    ("GIT_REPLACE_REF_BASE", "git-config"): (
        "not defined in git-config(1); upstream it is only in "
        "RelNotes/2.6.0.adoc:44 and in the source (refs.c:149 comment, "
        "environment.h GIT_REPLACE_REF_BASE_ENVIRONMENT)"),
    ("GIT_CONFIG_COUNT", "git-environment"): (
        "not defined in git(1); defined only in git-config(1) ENVIRONMENT"),
    ("GIT_CONFIG_KEY_", "git-environment"): (
        "not defined in git(1); defined only in git-config(1) ENVIRONMENT"),
    ("GIT_CONFIG_VALUE_", "git-environment"): (
        "not defined in git(1); defined only in git-config(1) ENVIRONMENT"),
}


def strip_html(raw):
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    import html
    return html.unescape(raw)


def main():
    rows = []
    cache = {}
    for src, (txtname, htmlname, url) in DOCS.items():
        with open(os.path.join(HERE, txtname), "rb") as fh:
            tb = fh.read()
        with open(os.path.join(HERE, htmlname), "rb") as fh:
            hb = fh.read()
        stripped = strip_html(hb.decode("utf-8", "replace"))
        cache[src] = (tb.decode("utf-8"), stripped, hashlib.sha256(tb).hexdigest(),
                      hashlib.sha256(hb).hexdigest(), url)

    for needle in NEEDLES:
        for src in DOCS:
            txt, stripped, tsha, hsha, url = cache[src]
            n_txt = txt.count(needle)
            n_html = stripped.count(needle)
            status = "PRESENT" if n_txt else "ABSENT"
            note = NOTES.get((needle, src), "")
            rows.append((needle, src, n_txt, n_html, status, note, tsha, hsha))

    out = os.path.join(HERE, "absences.tsv")
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write("needle\tsource\tstripped_text_count\traw_html_tagstripped_count\tstatus\tnote\ttxt_sha256\thtml_sha256\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    for r in rows:
        if r[4] == "ABSENT":
            sys.stderr.write("ABSENT %-34s %s\n" % (r[0], r[1]))
    sys.stderr.write("wrote %s (%d rows)\n" % (out, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
