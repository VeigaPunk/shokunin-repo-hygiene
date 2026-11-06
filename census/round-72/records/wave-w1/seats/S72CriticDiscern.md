# S72CriticDiscern — r72 source gate (S312–S314) and the knowledge r72 section

## Verdicts (agree/disagree)
- **S312 `mined` — AGREE.** Capture offset 2608, live page byte-identical (sha256 `6fe0df4e…348d`): "Consider .gitattributes in the index only, ignoring the working tree." Fixture: `git check-attr --cached filter tools/counter.py` → `unspecified`; without `--cached` → `t`; `.gitattributes` itself → `e` vs `unspecified`. The consequence is attributed as measured ("r72 row FWw, battery member WM8 forgery"). Scope correctly disclaims what status/the writer reads. Not `queued`: the quote is used as ground this round and says exactly what the row claims.
- **S313 `mined` — AGREE.** Offset 20533: "defined via filter. <driver> .process then Git can process all blobs with a single filter invocation for the entire life of a single Git command"; the page adds "When Git encounters the first file that needs to be cleaned or smudged, it starts the filter and performs the handshake." The page does **not** say "no `clean` key"; the row marks that half "(measured: r72 row FWp, battery member WM5 forgery)" — page and probe correctly separated. Not `queued`.
- **S314 `mined` — AGREE as filed; DISAGREE with "for status reads".** Offset 5164: "When the .gitattributes file is missing from the work tree, the path in the index is used as a fall-back." The next page sentence: "During checkout process, .gitattributes in the index is used and then the file in the working tree is used as a fall-back." The page never mentions `git status`, and names the reverse order for checkout; the row's scope disclaims checkout and its measured use is the check-attr read. So the fallback rule is grounded, "for status reads" is not the page's statement, and the teaches cell's unconditional "read first" needs the non-checkout qualifier (LOW). Not `queued`.

## Missing source
- Opened the named technical doc (`Documentation/technical/long-running-process-protocol.adoc` @v2.56.0): "Git starts by sending a welcome message …, a list of supported protocol version numbers, and a flush packet"; "Git expects to read a list of desired capabilities, which must be a subset of the supported capabilities list". It adds version negotiation/subset/shutdown, none of which S313 needs (the page already fixes version 2, the capability set and the request/status framing). Optional code row (LOW).
- The source the round did **not** open and the section needs: git `read-cache.c` @v2.56.0 for the size-0 mechanism (no documentation states it): `344-348` ("Racily smudged entry? if (!sd_size) …") and `486-489` (`sd_size != 0` short-circuit vs `ce_modified_check_fs`).

## Knowledge r72 section: unsupported / overstated sentences
1. **MEDIUM** `corpus/knowledge/filter-filemode-witness.md:77` "git re-hashes a size-0 index entry through its filter on every status read" — no S312–S314, receipt or probe supports it, and it is **false as written**. Receipt (FWw shape, 2.2 s after the edit, so not in the racy window): status#1 `filter_hits=1` clean; status#2/#3 `filter_hits=0` clean. The size-0 branch forces a content check on the read that observes the changed stat; the index then caches `size: 50` and later reads trust it. Without the sleep the hits repeat only inside the same-second racy window (1/1/1). The row's conclusion (the edited attribute file reads unmodified) still holds for the writer's first read.
2. **LOW** `:79` "A non-empty committed copy with a different-size worktree edit is reported as modified (stat size check) and needs no attribute witness." — true (non-empty(7) committed, worktree 50: `M .gitattributes`, `filter_hits=0`), but no artifact named in the r72 section measures it; the analogous r71 probe is named only in the r71 part.
3. **LOW** `:74` "S314 the worktree file comes first" — overstated as universal (checkout reverses it); correct for the check-attr read it is used for.
4. **LOW** `:65` "…(`fw-shapes-probe.txt`, `c2-after-battery.txt`, `c2-honest-writer.txt`)" — `c2-honest-writer.txt` is the honest-writer arm (`new_forgeries=0`) and does not bear on the five refusals.

## Size-0 test (git 2.56.0, fixtures under /fast/scratch/hyaku/souji-r72/S72CriticDiscern)
- A size-0 committed `.gitattributes`, worktree copy self-filtered, no sleep: 1/1/1 filter hits, porcelain clean, `hash-object --path=.gitattributes` = `e69de29` (empty blob), index stat size after refresh 50.
- G1 same shape, 2.2 s sleep: 1/0/0 hits, porcelain clean → "every status read" falsified.
- C non-empty(7) committed, worktree longer: 0/0/0 hits, `M .gitattributes` → the stat size check, no attribute witness (as claimed).
- B size-0 committed, worktree not self-filtered: `M .gitattributes` (self-assignment is required).

## Reproduced numbers
`census/round-72/c1-matrix.tsv` 75 data rows (76 lines incl. header); probe 35 lines / 10 `verdict=accept`; exactly one battery member accepts each shape (FWr WM3, FWi WM4, FWp WM5, FWw WM8, FWs WM6); base writer `8b9345b1:tools/souji-receipt-write.py` sha256 `118597e0…e71f`, 0 occurrences of "filter"; live page hashes match the captures (`6fe0df4e…`, `0a1e8015…`).

## Commands
`curl -fsSL https://git-scm.com/docs/{git-check-attr,gitattributes}` + `sha256sum`; `python3 -B size0-receipt.py`; fixture `git -C … check-attr [--cached] filter …`; `git cat-file -p 8b9345b1:tools/souji-receipt-write.py | sha256sum`; `grep -c "PROBE \|verdict=accept"` on the probe txt.

## Files written (seat dir)
`.ufo/waves/round-72/w1/S72CriticDiscern.md`, `.ufo/waves/round-72/w1/S72CriticDiscern/{size0-receipt.py,size0-receipt.txt,read-cache-lines.txt}`.
