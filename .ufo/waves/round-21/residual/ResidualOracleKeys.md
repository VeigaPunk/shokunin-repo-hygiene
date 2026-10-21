# ResidualOracleKeys (SoujiR21.ResidualOracleKeys-2)

STATUS: PASS — 14/14 residual call keys independently labelled; expected FLAG set is empty; the auditor predicate agrees on all 14 rows; the extra key is a `bash` call, not a `grep` call.

## Inputs (named only)
- `census/round-21/oracle-residual-input.json` — sha256 `376771c4…3067`, byte-identical in the working tree and `git show 54eb2d0fb81e9cb5cf5b30430bcfa4b67ddc84ec:` (HEAD = 54eb2d0…).
- Rules: `.ufo/waves/round-21/preregistration.txt` (C1), `clarification-before-measurement.txt` (`grep(PATTERN in PATH)` = explicit path), `full-corpus-restoration.txt` (all three export directories; byte-identical cross-export reuse only with provenance).
- Transcripts: each file sha256 is identical across the working tree, HEAD 54eb2d0 and universe commit 522dcd7:
  - `final/InputCase13.txt` `3ac76323…06d0`
  - `final/MutateRepeatedRead.txt` `1ec87071…389d`
  - `recovery/ReceiptTranscript.txt` = `recovery-final/ReceiptTranscript.txt` `94b9ce66…fd9f` (the two exports are whole-file identical)
  - `final/AuditCase24.txt` `95a58392…0b25`

## Method and order
1. I read every physical line in its named file: lines 47–50 of InputCase13, lines 47–57 and 128–131 of MutateRepeatedRead, lines 45–64 of both ReceiptTranscript exports, and lines 76–83 of AuditCase24. Each line matched the input's `call` string; the transcript also carries the renderer's trailing ` · N lines`.
2. I labelled every row from the C1 text plus its clarifications and wrote `ResidualOracleKeys.tsv` **before** opening `tools/souji-seat-audit.py`.
3. Only after that did I read the predicate (`implicit_root_read`, lines 377–402, and its call site, lines 455–458; auditor sha256 `e1298b93…687c` at HEAD = working tree).

The two `recovery-final` rows are labelled from their own lines. Their bytes are also identical to the `recovery` rows, which I disclose as provenance rather than use as a label transfer.

## Labels
Label meanings: `FLAG` = a V-READ-ROOT hit. `OK` = the target is visible and is never V-READ-ROOT. `UNSEEN` = not flagged because the target is not fully visible (the truncation lower-bound rule).

| Key | Label | Basis |
|---|---|---|
| InputCase13:49 read | OK | `artifact://36867` (selector stripped) is a URI |
| MutateRepeatedRead:49 grep | OK | `PATTERN @ /var/tmp/…/souji-seat-audit.py` is an absolute path |
| MutateRepeatedRead:50,55,56 read | OK | absolute `/var/tmp/…` paths |
| MutateRepeatedRead:130 read | OK | absolute path; the `:-14` selector does not matter |
| ReceiptTranscript:47,48,49 read (both exports) | OK | absolute lane paths |
| ReceiptTranscript:63 grep (both exports) | UNSEEN | args cut by `…`; no ` @ `; path not visible |

Totals: FLAG 0, OK 12, UNSEEN 2. Expected V-READ-ROOT set over these 14 keys: ∅.

## Auditor comparison (after labelling)
The predicate agrees on all 14 rows, so on this residual set tp=0, fp=0, fn=0, missing=0 and extra=0.
- **Read rows:** the selector regex `:(?:raw|img|conflicts|[-\d,+hms]+)…$` strips `:385-482` and `:-14`. The remaining targets start with `/` or match `^[a-z][a-z0-9+.-]*://`, so they return None.
- **MutateRepeatedRead:49:** the ` @ ` split gives an absolute target, so it returns None.
- **ReceiptTranscript:63:** there is no ` @ `, but the pattern contains ` in ` (`for item in spec`, `for name in result`). The historical-renderer branch therefore takes `rsplit(" in ",1)[1]`, which is `result\["missin…`. That component contains `…`, so it is skipped and the function returns None. The result matches UNSEEN, but only because of the truncation.

## Extra key disposition: `final/AuditCase24.txt:80` proposed as `grep`
Reject the extra key as a grep key. Line 80 is `→ bash(cd /home/vgpnk/Projects/shokunin/souji-shokunin && C=1988860e… && git grep -n -e 'single…) ⇒ ok · 11 lines`.
- `CALL_RE` (`^→ ([A-Za-z_][\w.-]*)\(`) captures the tool as `bash`. The word `grep` appears only as a `git grep` subcommand inside the shell command.
- C1 limits V-READ-ROOT to the tools {read, grep, glob}. This call is therefore outside the V-READ-ROOT universe and must not appear as a grep row.
- Its only valid key is `(final/AuditCase24.txt, 80, bash)`, which is judged by the bash classes, not by this oracle.
- In that file, the only actual read/grep/glob invocations are line 40 `read(skill://godspeed)` and line 60 `read(artifact://36974:raw:1-4)`. Both are URIs, so both are never V-READ-ROOT, and neither is one of the 14 residual keys.

## Counterexample / residual risk (not a defect on these keys)
The ` in ` historical branch runs whenever a modern grep has no ` @ ` and its pattern contains ` in `. If such a pattern is **complete**, the target becomes the pattern tail. Two failure cases follow:
- **False negative:** a tail starting with `/` (for example `x in /etc`) is treated as absolute, or a tail like `souji-shokunin/x` resolves inside the lane. Either way the call goes unflagged, although C1 says "no ` @ ` and complete args → FLAG".
- **Wrong target text:** any other tail still flags, but with a misreported target.

These 14 keys are not affected, because the only ` in `-bearing grep is truncated.
- **Impacted axis:** C1 recall/precision fidelity.
- **Smallest safe correction:** accept ` in ` only when the right-hand side is path-shaped, or only for the historical renderer era. That is a ruling for the judge, not an edit here.

I did not search the wider corpus for a live instance, because corpus-root searches are out of scope for this seat.

## Limitations
- The UNSEEN rows are a disclosed lower bound. The real call at ReceiptTranscript:63 may have omitted its path (an implicit-root read), but the transcript cannot show that.
- I executed no target code, builds or tests. My only git operations were `git show` and `git rev-parse`, which are read-only. I installed no tools. I made no edits to the corpus or the implementation.
- After the auditor read, I corrected one wording slip in the TSV notes for the line-63 rows (it had said ` in ` was absent). Both labels were unchanged by the correction.
