## Status
STATUS: PARTIAL — K1 and K2 do not fully establish the stated scaffold-removal and ordering conditions.

## Evidence
- At `89e0fceeefcf28db313c94120be6d25e03c60094`, extracted committed `SCORECARD.md` to `/var/tmp/souji-r26-RevC1Counter/SCORECARD_at_89e0.md`; reran the frozen expressions verbatim:
  - `grep -cE '^(Insert the table below directly above|Optional same-landing correction)' SCORECARD_at_89e0.md` → `2`
  - `awk '/^### Round (23|24|25) measurements/{printf "%s ", NR} END{print ""}' SCORECARD_at_89e0.md` → `17 175 231 `
- Requested residue command against that blob: `grep -nE 'Insert|Optional same-landing|Findings 6|newest first' SCORECARD_at_89e0.md` → matches at lines 172 and 217.
- Wider residue scan additionally finds scaffold instructions at lines 210, 222, fenced payloads at 174/212/224, and fence at 208.
- The real Round 24 section exists historically: `git show 315422b:SCORECARD.md | grep -n '^### Round 24 measurements'` → line 174; the frozen 89e0 copy has one occurrence at line 175, inside the scaffold fence. The named r24 receipts checked at 89e0 are present.
- Amendment 2 says: “Everything else from the scaffold block (base lines 170-230: instruction lines, fences, separator) is deleted.” It clarifies protected spans are byte-content spans and requires the payload table in the stated position.

## Findings
1. **K1 is gameable / incomplete.** It counts only two marker prefixes. Removing or rephrasing those marker lines while retaining other scaffold instructions, fences, or payload residue yields K1=0; the wider residue at the frozen commit demonstrates the scaffold contains additional content not counted by K1. Amendment 2's explicit deletion rule is needed to catch residue; K1 alone does not.
2. **K2 counts three matches, but the printed positions are not the stated `(n25,n24,n23)` tuple.** The expression emits matching line numbers in file order and omits round labels. At the frozen file, mapping actual headings gives Round 23 at 17, Round 24 at 175, Round 25 at 231, so output order is `(n23,n24,n25)`, not `(n25,n24,n23)`. Thus the exact-three count is measurable, but the command output alone cannot certify the named ordering; the evaluator must map each line back to its heading. Do not treat the bare ascending triple as proof of newest-first.
3. **A genuine Round 24 table exists.** The r24 landing (`315422b`) already has the heading outside the later scaffold; this is not a hypothetical missing table. At frozen 89e0 the heading occurs only once and inside the fenced template. Removing the fence while preserving/promoting the payload can expose it as the real section; the kill-rule intent is not to preserve the obsolete duplicate template.

## Attack log
- Verdict: **gameable-by-K1 marker removal/rewording; K2's emitted positions are unlabeled and do not themselves prove the specified order.** The exact-three check is still useful, but not sufficient as a standalone ordering certificate. Requested residue grep confirms scaffold text at 172 and 217; broader inspection finds additional scaffold residue.
- No edits to the lane counter or frozen contract were made. No tool installation. Verification commands above were run on the committed blob extracted from 89e0; no checkout or lane mutation was performed.
