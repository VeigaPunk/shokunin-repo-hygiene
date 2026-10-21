# C1 V-READ-ROOT oracle labels

Source: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/recovery-final/OracleAcceptance.txt`; rules: `.ufo/waves/round-21/preregistration.txt`, section C1. I used the required `grep` pattern `→ (read|grep|glob)\(` on the exact transcript and inspected relevant transcript ranges for complete versus truncated targets. I did not read or run auditor code.

The TSV contains 132 matching call lines: **FLAG 0, OK 104, UNSEEN 28**. No visible complete relative target, and no complete `grep` call missing the ` @ ` separator, was present. Complete absolute paths and URIs are OK under C1; calls with an elided target suffix are UNSEEN, the stated lower-bound treatment.

Ambiguous line adjudication:

> `248:→ grep(print\(.*PASS|print\(.*CASE|SELFTEST @ /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:1338-22…) ⇒ ok · 49 lines`

The absolute file target `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py` is fully visible; the ellipsis follows the file name in the line-range selector (`:1338-22…`). I labelled it **OK** because the resolved target itself is complete and absolute. If the truncated selector is treated as part of the path portion rather than a selector, this line could instead be considered UNSEEN; that interpretation is the remaining ambiguity.

The labels and notes are in `LabelReadRoot02.tsv` at the requested DELIVER path. No execution, build, test, lint, or formatter was run; no tools were installed.
