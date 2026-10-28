# R40w2sentinel02 — C2 hostile input operability

**Attack target:** `census/round-40/docstring-classes.py:37-40, 87-96`; C2 counter entry points at `census/round-40/c2-counter.py:128-142` (load committed analyser) and `:207-` (counter CLI). Landed revision checked: `128e412b0ced3c243dc27c3dd3332054a611bc2e`.

The analyser CLI reads source using strict UTF-8, then AST-parses it. The four hostile cases were created only under the mandated scratch path and passed directly to the committed analyzer file. Exact command:

```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel02; mkdir -p "$S" && trap 'rm -rf -- "$S"' EXIT && python3 -c 'from pathlib import Path; p=Path("/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel02"); (p/"prose.py").write_text("\"\"\"Example CLASS-LIKE TOKEN  description in prose.\"\"\"\n"); (p/"none.py").write_text("x = 1\n"); (p/"long.py").write_text("\"\"\"\nCLASS-LONG  " + "x"*1000000 + "\n\"\"\"\n"); (p/"bad.py").write_bytes(b"\x80\xff\n")' && for f in prose none bad long; do printf '\nCASE=%s\n' "$f"; timeout 5s python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/docstring-classes.py "$S/$f.py"; printf 'exit=%s\n' "$?"; done
```

Real output (long line abbreviated by tool output truncation):

```text
CASE=prose
exit=0

CASE=none
exit=0

CASE=bad
Traceback (most recent call last):
  File "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/docstring-classes.py", line 94, in <module>
    src = handle.read()
  File "<frozen codecs>", line 325, in decode
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x80 in position 0: invalid start byte
exit=1

CASE=long
CLASS-LONG\t[one-million x characters; output line was truncated by tool display]
exit=0
```

Interpretation: prose containing an upper-case hyphenated class-like token is ignored unless matching the actual entry grammar (no false class emitted in this probe); no module docstring is accepted as empty output. Invalid UTF-8 is not handled gracefully: the CLI emits a traceback and exits 1. The one-million-character line completed within the 5-second timeout, but was echoed as an enormous output record; potential output amplification, not a demonstrated hang. C2 counter itself runs analyzer from committed bytes as a Python module rather than this CLI file-reading path, so these CLI outcomes do not establish that its runtime source acquisition has the same decoding behavior.

**Verdict: FALSIFIED (hostile non-UTF-8 source refusal is an uncaught traceback, not a controlled refusal); other tested cases SAFE against false parse/hang at tested size.** Smallest remediation: catch `UnicodeDecodeError` at the CLI input boundary and report a concise error/nonzero exit. No tool installs. Scratch directory removed by EXIT trap; cleanup command included above.