# AttackCorpus19 — C1 classifier corpus attack

**Judged axis:** calibration. **Scope:** the nine assigned committed r20 transcripts only; this is not a claim about the other files in the restored 192-file universe.

## Independent labels

I read the frozen C1 contract and its clarifications first, then classified the transcript call lines from the contract before inspecting `implicit_root_read`. The full-corpus correction includes `recovery/` in addition to `final/` and `recovery-final/`; the assigned set contains one `recovery/` transcript. The TSV records all **112** read/grep/glob calls, with actual tab separators and 1-based physical line numbers: **95 read, 17 grep, 0 glob; 103 OK, 9 UNSEEN, 0 FLAG**.

The nine `UNSEEN` rows are the visibly truncated target components: `final/FinalCallerRuntime.txt` lines 50, 65, 72, 81; `recovery-final/F5Redaction.txt` line 47 (second component of a semicolon-separated target); and `recovery-final/ReceiptSpec.txt` lines 63–66. I did not guess past any cut. All remaining calls are either absolute targets, URI targets, or `final/FinalHeldAuthority.txt:99`, whose relative `souji-shokunin/...` target resolves inside the lane after removing `:3,51:raw`. No visible complete relative target resolves outside the lane. The errored read at `recovery-final/F5Redaction.txt:51` is still an absolute target and therefore OK; its error status does not change this label.

The independent per-call inventory is delivered at `.ufo/waves/round-21/w2/AttackCorpus19.tsv`.

## Pinned predicate comparison (static; no classifier execution)

I inspected `tools/souji-seat-audit.py` at the pinned build. Read-only blob identity check:

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 522dcd768ca90afe166532d37d306d3df70aeea5:tools/souji-seat-audit.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin hash-object -- tools/souji-seat-audit.py
```

Both returned `6cf3a85b01b6ca883a1e6ea226cdec65278da0f4`, confirming the inspected file bytes match that pinned blob.

`implicit_root_read` at `tools/souji-seat-audit.py:377–402` agrees with the frozen rules: it gives ` @ ` precedence over historical ` in ` for grep, treats a complete grep with neither separator as the fleet-root target, splits semicolon-separated target components, removes read selectors before judging, skips visibly cut components, excludes absolute/tilde/URI targets (URI matching is case-insensitive), and lexically resolves relative components against the fleet root before testing lane containment. Its caller at lines 455–458 emits `V-READ-ROOT` for a returned target. I found no predicate/label disagreement among the 103 classifiable rows; the nine cut-target rows are correctly left UNSEEN by the independent oracle and are skipped by the predicate.

## Bounded finding and residual

No counterexample in these nine transcripts produces a complete outside-lane relative read/grep/glob target, so this corpus subset yields no positive FLAG case and cannot demonstrate sensitivity to one. It does test the important exclusions and lower-bound handling, including a relative in-lane target, URI targets, a multi-path cut, and error status. The historical `grep(PATTERN in PATH)` fallback is present in the pinned source, but none of these 112 calls uses that rendering; this subset therefore does not empirically challenge that branch. This is a bounded static comparison, not an executed classifier result or a full-corpus precision/recall claim.

No tests, classifier, or target code were executed; no tools were installed.
