## Status

STATUS: PASS — `deliver-duplicate-verdict-byte-equality.md` is written and its Gate verifies green (`entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, rc 0) against the exact snapshot bytes and appended rows the L1 will land; against the lane as it stands the same gate run is red only on land-order (snapshots, rows S216–S219, slice records not yet landed), which is the L1's integration step. Build seat, not an attack seat.

## Evidence

Contract read first, frozen before data: `census/round-29/records/preregistration.txt` (C3 line 9: two entries, four rows S216–S219, Gate with located quote ≤25 words + committed snapshot). Revision: HEAD detached at `b8cb4b31ce80e2e3314b88e85d40ea9873180804`, `refs/heads/master` = same, parent `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; prereg file clean in `git status --porcelain`.

Sources fetched by me this run (scratch `/var/tmp/souji-r29-SwarmScribe24`, removed at the end):

```
$ curl -sS -L --max-time 60 -o cmp.1.raw   -w '%{http_code} %{size_download}\n' https://man7.org/linux/man-pages/man1/cmp.1.html
200 9791        sha256 5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3
$ curl -sS -L --max-time 60 -o link.2.raw  -w '%{http_code} %{size_download}\n' https://man7.org/linux/man-pages/man2/link.2.html
200 19883       sha256 9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9
$ curl -sS -L --max-time 120 -o broder97resemblance.pdf -w '%{http_code} %{size_download}\n' https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf
200 254930      sha256 da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b  (9 pages)
$ pdftotext broder97resemblance.pdf out.txt   # poppler 26.08.0, plain, no -layout
                sha256 3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d  (21669 B)
```

`cmp.1.raw` and `link.2.raw` are byte-identical (`sha256sum`) to the staged snapshots `.ufo/waves/round-29/w1/sources/cmp.1.html` and `link.2.html`; the plain `pdftotext` decode is byte-identical to the staged `broder97resemblance.txt`. My first decode used `pdftotext -layout` (24930 B, different digest) — the committed snapshot is the plain decode, so every Broder quote below was re-checked against that decode, not against my first one.

Quote match, whitespace-collapsed, against the staged snapshots (the gate checker's own rule):

```
OK    6 words cmp.1.html                 Compare two files byte by byte.
OK   15 words cmp.1.html                 Exit status is 0 if inputs are the same, 1 if different, 2 if trouble.
OK   21 words link.2.html                This new name may be used exactly as the old one for any operation; both names refer to the same file
OK   23 words broder97resemblance.txt    resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of …
OK   19 words broder97resemblance.txt    2.1 million clusters contained only identical documents (5.3 million documents). The remaining …
(no pipe character in any quoted span)
```

Gate, staged in `/var/tmp` (lane `corpus/SOURCES.md` + the four rows of `deliver-sources-append-block.md` inserted after S215; `w1/sources/*` copied to `census/round-29/sources/`; `w1/assimilation/quarantine-slice` and `w1/deliver-slice-verdicts.tsv` copied to `census/round-29/records/`):

```
$ python3 -B tools/souji-gate-check.py --root /var/tmp/souji-r29-SwarmScribe24/gate --round-date 2026-10-25 \
    --entries entries/byte-equality.md entries/identity.md --snapshot-dir census/round-29/sources \
    --slice census/round-29/records/quarantine-slice --slice-verdicts census/round-29/records/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0        rc=0
```

Same entries against the lane as it stands (read-only; nothing landed yet):

```
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=18       rc=1
  5x check4-snapshot-missing-line-…, check3-no-located-quote-with-snapshot,
  check5-dangling-source: S219 / S218 / S217 (byte-equality), S216/S217/S218 (identity), slice-missing
```

Base counters re-read at `691dd29` (no new measurement of the lane): `git grep -lE '^ground: F3' 691dd29 -- corpus/knowledge/ | wc -l` → `0`; `git show 691dd29:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → `139`. Both match the prereg's stated base; my delivery is one of the two F3 entries and cites three of the four rows.

DOI probe for the Broder paper's registered locator (my own run, not quoted from a sibling):

```
$ curl -sS -o doi.body -D doi.headers -L -w 'code=%{http_code} bytes=%{size_download}\n' https://doi.org/10.1109/SEQUEN.1997.666900
code=202 bytes=0     (302 → 301 → HTTP/2 202, content-length: 0)
```

No tool was installed or upgraded; `pdftotext` 26.08.0 was already on the host. No pacman transaction was run.

## Findings

1. **The cmp(1) exit-status sentence is tag-free inside a single `<pre>` and wraps between "is" and "0".** Raw bytes at `.ufo/waves/round-29/w1/sources/cmp.1.html:113-114` are `If a FILE is '-' or missing, read standard input.  Exit status is` / `0 if inputs are the same, 1 if different, 2 if trouble.` — no element, entity or non-breaking space between words, so the whitespace-collapsed match holds and the 15-word quote is safe. This is the check my item asked for; it differs from pages where markup sits inside the sentence.
2. **`cmp(1)` has no `EXIT STATUS` section.** The section bar at `cmp.1.html:41` lists only NAME, SYNOPSIS, DESCRIPTION, AUTHOR, REPORTING_BUGS, COPYRIGHT, SEE_ALSO, COLOPHON; the exit contract is the closing paragraph of DESCRIPTION (line 113). The entry says so, and cites `§ DESCRIPTION` rather than a section that does not exist.
3. **The link(2) identity paragraph does carry markup, so the quoted span was chosen to avoid it.** `link.2.html:95` has `<b>link</b>()` and `:98` has `<i>newpath</i>`; the quoted span (lines 100-101, `This new name … both names refer to the same file`) contains no tag, which is why it survives whitespace-collapsed matching. `link.2.html:310` dates the page `Linux man-pages 6.19  2026-02-11`; `cmp.1.html:156` identifies `diffutils 3.12.26-bbc1  August 2026`.
4. **The Broder PDF natively supports "vocabulary, not threshold".** `broder97resemblance.txt:53-56` records that one chosen threshold — "a 50% resemblance" — produced 2.1M clusters of only identical documents and a further 1.5M clusters of "a mixture of exact duplicates and similar". The threshold is therefore a parameter someone sets, which is exactly the operator-decision boundary the entry preserves.
5. **A prior draft occupied my delivery path and was superseded.** `.ufo/waves/round-29/w1/deliver-duplicate-verdict-byte-equality.md` held 4891 B (mtime 21:43) with no `## Lane link` section — required by my item — and a `recheck:` line naming "both man7 pages" for a three-source entry. It is replaced by a 9018 B entry that carries `## Lane link`, five located quotes (two cmp, one link, two Broder — the prior draft carried three) all re-verified by me above, the same ADMIT/REJECT duty, and one REJECT taken from the staged F3-adjacent set (`near-duplicate-relations-r29.md`, which I opened: it argues near-duplicate relations and whether the canonical fuzzy measure admits a threshold at all — out of byte-identical scope). A second REJECT names `duplicate-receipt-class-decision-r25.md`, which I also opened: it states the lane's current receipt taxonomy and what a ruling would have to touch, i.e. a decision record.
6. **The staged lead's ids could not be reused.** `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/duplicate-verdict-taxonomy-r24.md` cites S136/S118/S122 (campaign ids, S118 through the DOI). I re-grounded every claim on lane ids S219 (cmp), S218 (link), S217 (Broder via the author-hosted PDF) opened this run; the DOI locator answers `202` with `content-length: 0` (Finding evidence above), so the PDF is the only usable locator. The lead's substance (three-valued exit, two measures, inode identity, no threshold proposed) survived re-grounding; its citations did not.
7. **The entry is land-order dependent, and only that.** `.ufo/waves/round-29/w1/deliver-duplicate-verdict-byte-equality.md` names `census/round-29/sources/{cmp.1.html,link.2.html,broder97resemblance.pdf,broder97resemblance.txt}`, which do not exist in the lane yet (staged at `.ufo/waves/round-29/w1/sources/`, digests identical to mine); it cites S217/S218/S219, which `corpus/SOURCES.md` does not carry yet (registry ends at S215, line 160). With both landed plus the slice records, the gate is green; without them it reports 18 land-order failures and no entry defect.
8. **Nothing in this delivery changes a lane rule or a claim.** `SKILL.md:85-86` (`cmp` drift rule) and `corpus/knowledge/dupe-finders-detect-then-act.md:34` (`cmp` byte equality, designated original, act-time re-check) are cited as the rule the source now grounds; neither is edited, weakened or superseded, and no threshold, receipt class or tool change is proposed.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-duplicate-verdict-byte-equality.md` — the C3 knowledge entry, ready to land at `corpus/knowledge/duplicate-verdict-byte-equality.md` together with the S216–S219 rows and the four snapshots.

No other file was written; scratch `/var/tmp/souji-r29-SwarmScribe24` was removed.
