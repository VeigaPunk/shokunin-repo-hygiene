# LabelReadRoot10 — C1 V-READ-ROOT oracle labels

Applied only the frozen C1 rules in `.ufo/waves/round-21/preregistration.txt` to the ten assigned round-20 transcript files. I used the requested `→ (read|grep|glob)\(` search separately on each exact file and labelled each matching physical line. No auditor code was read or run; no target code was executed.

## Results

- FLAG: 1
- OK: 99
- UNSEEN: 3
- Total: 103 tool-call lines

The sole FLAG is `recovery-final/CorpusAdmission.txt:45`: `glob(corpus/lessons)` is a complete relative target, resolves from the fleet root, and lies outside the lane. The three UNSEEN rows have target text visibly truncated with `…`; they are not flagged, per C1:

- `final/ReopenRevParse.txt:75`: `→ grep(exactly one parameter|20-byte|last updated|2026-09-28|peeling operator|end-of-options|untrusted source @ artifact://374…) ⇒ ok · 43 lines`
- `final/ReopenTimeout.txt:41`: `→ read(https://web.archive.org/web/20260919212856id_/https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocatio…) ⇒ ok · 148 lines`
- `final/ReopenTimeout.txt:42`: `→ read(https://web.archive.org/web/20260919212856id_/https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocatio…) ⇒ ok · 209 lines`

## Ambiguities

None. Complete relative paths, absolute paths, URIs, grep path separators, and truncated targets are all addressed by the C1 rules. In particular, the absolute path in `recovery-final/ReceiptManifest.txt:49` is outside the lane but is still OK for this class because C1 explicitly excludes absolute paths.

## Evidence and limits

The ten per-file grep results contained, respectively, 1, 2, 10, 1, 3, 18, 7, 21, 16, and 24 matching lines (103 total). For a supplementary count cross-check, I executed `grep -cE '→ (read|grep|glob)\(' /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/final/AuditCase18.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/final/AuditCase24.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/final/FinalAuditRuntime.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/final/InputCase05.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/final/InputCase18.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/final/ReopenRevParse.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/final/ReopenTimeout.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/recovery-final/CorpusAdmission.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/recovery-final/InputAdded.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-20/transcripts/recovery-final/ReceiptManifest.txt`; the shell tool returned those counts but did not surface an exit code. All classifications are source-only oracle judgements; no auditor/verifier result is claimed.

TSV: `.ufo/waves/round-21/w1/LabelReadRoot10.tsv`.
