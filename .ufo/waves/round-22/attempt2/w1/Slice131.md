STATUS: PASS

# Slice131 — register row S131, lane `souji`, round2 (hand-check, read-only)

Access date: 2026-10-25. Base lane revision: 4edb25dfe262515d0da63224bbba71e02e36cba5.
No tool installed or updated for this item. No lane-repo write outside this report and the
named evidence file. No git/jj writes, no deletion authority created.

## Frozen row (extraction executed, field 4 = id cell)

Command:
```
awk -F'|' 'NR==175 && $4 ~ /S131/ {print $2"|"$3"|"$4"|"$5"|"$6}' \
    /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
```
Output (exit 0):
```
 `souji` | round2 | S131 | `payload-absent` | lanes/souji/round2/evidence/r23-worktree-census.out
```
Registered quote (field 7, verbatim):
`-n, --dry-run With prune, do not remove anything; just report what it would remove.`
Derived slice line (`census/round-22/attempt2/quarantine-slice`, line 5): `` S131   `payload-absent` ``

## Source read (executed)

Cited artifact: `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out`
(43 lines, 1672 bytes; complete verbatim snapshot in the evidence file).
```
sha256 = 1ac71c4f7199a134c204b45f339aadfc7e90c84b2d640cbed181b3577b9392fd
```

Payload test — the claimed span is NOT in the cited artifact:
```
grep -c -- '-n, --dry-run With prune, do not remove anything' <cited>   -> 0   (exit 1)
grep -c 'do not remove anything'                          <cited>   -> 0
python3 whitespace-collapse: norm(quote) in norm(cited)  -> False
```
The payload's only `dry-run` strings are execution lines (`worktree prune --dry-run`,
`--- prune census (dry-run only) ---`, `prune --dry-run --expire now: (no output — none prunable)`);
none carries the option-synopsis sentence.

## Located span (executed, installed primary source)

Package `git 2.56.0-1`; man page `/usr/share/man/man1/git-worktree.1.gz`
(header: Manual Git Manual, Source Git 2.56.0, date 2026-09-27).
```
sha256(gz)                                  = 23a15bc3a5c48284727d665ce09e515a003959eaab706664d634563f51b91111
sha256(zcat - /usr/share/man/man1/git-worktree.1.gz) = 2330c8c82928bdf439fc8cdfac3fd7805fdd6b2cbc243fe9c2285ff13fa32408
sha256(MANWIDTH=100 man -P cat git-worktree) = 25d48384d9b12b4db716d3f49e587f8f27ed3e225c565d54183373f827053986
```
Locator: **section OPTIONS, item `-n, --dry-run`**; rendered lines 189–190 (MANWIDTH=100);
raw roff lines 352–356. `norm(quote) in norm(rendered git-worktree) -> True` (offset 10121).

Exact located span (17 words):
```
-n, --dry-run With prune, do not remove anything; just report what it would remove.
```
Disambiguation (executed): `git-prune(1)` OPTIONS `-n, --dry-run` reads
`Do not remove anything; just report what it would remove.` — it omits `With prune,`, so the
registered span resolves uniquely to `git-worktree(1)`, not `git-prune(1)`.

## Verdict for this row (one frozen class)

**`refused` — citation-class defect, reason stated.**

Reason: the payload is absent from the cited local artifact (0 literal and 0
whitespace-normalized matches), while the same span is verbatim present in the installed
`git-worktree(1)` OPTIONS `-n, --dry-run`. The row cites a local census for text that lives in a
man page; the quote needs no correction, only the citation, which the frozen `accepted`
definition ("quote corrected, correction stated") does not cover. Flip: re-cite the identical
span against `git-worktree(1)` OPTIONS `-n, --dry-run` (git 2.56.0, man page dated 2026-09-27);
then the row is admissible with no textual change.

Slice-verdicts row this item contributes (tab-separated; connector owns the TSV):
```
S131	refused	citation-class defect: payload absent from cited r23-worktree-census.out (0 literal/normalized matches); same span verbatim in git-worktree(1) OPTIONS '-n, --dry-run' (git 2.56.0, man dated 2026-09-27, rendered lines 189-190); flip: re-cite against git-worktree(1); receipt .ufo/waves/round-22/attempt2/w1/evidence/slice131-worktree-census.out sha256 494a80ec71ccd58406f8e3181679d1452fc54f7553578ecc81e844113f168b06
```

## Bounded findings

- **Observed:** register row S131 (lane souji, round2) is field-exact as extracted; the cited
  census does not contain the quote under literal or whitespace-collapsed comparison.
- **Observed:** the quote is verbatim in the installed `git-worktree(1)` man page OPTIONS
  section; `git-prune(1)` has a near-identical but not identical line (no `With prune,`).
- **Divergence to reconcile (observed):** the committed
  `census/round-22/attempt2/slice-verdicts.tsv` from the earlier attempt carries
  `S131 accepted` ("quote is git-worktree(1):218 prose; payload own line … supports the census
  claim"). Its locator 218 corresponds to a narrower render (MANWIDTH=80 places the span near
  line 218; MANWIDTH=100 places it at 189–190). That row states no corrected quote, so it does
  not satisfy the frozen `accepted` definition ("quote corrected, correction stated"); the
  `refused` class above is the class this hand-check supports. Both classes pass the frozen
  slice predicate (class must be one of present|accepted|unverifiable|refused), so the
  slice-verdicts counter is unaffected in count; only the class differs.
- **Not run (out of scope by assignment):** gate-check, sources-census validation, any
  mutation/cleanup, any write to the register, lane index, `.ufo/state`, or sibling repos.
- **Confidence:** high for the absence and the located span (both executed locally and
  digest-recorded); the man-page rendering is host/environment-dependent, so the locator is
  given as a section/option heading rather than a bare line number.

## Evidence files

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/slice131-worktree-census.out`
  — sha256 `494a80ec71ccd58406f8e3181679d1452fc54f7553578ecc81e844113f168b06`
  (cited-source snapshot, absence receipts, man-page extraction and digests).
- This report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/Slice131.md`.
