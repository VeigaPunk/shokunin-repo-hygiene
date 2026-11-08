# R91ScoutSources — round 91 source gate

Seat: R91ScoutSources (scout, leaf — no dispatch). Lane `souji-shokunin`, lane base
681f6c72b242d410d0e8654efadb2a1553fb111d. Read-only on the lane: nothing committed, no git/jj state
touched, no filed instrument modified. All receipts below live in this seat dir
(`.ufo/waves/round-91/w1/R91ScoutSources/`); scratch `/fast/scratch/hyaku/souji-r91/R91ScoutSources`
was deleted before yield. Date of all observations: **2026-11-08** (local 13:20:59-0300 /
2026-11-08T16:20:59Z UTC).

VERDICT: **source gate PASSES.** The filed capture is byte-identical to a live re-fetch, the S354 row's
quote cells (lines, 25 words, occurrence count 1) are correct, the reject candidate is rejected with a
flip condition, and the lane registry validates clean with no duplicate of the RFC 3629 URL. **No
artifact of this seat falsifies a sentence or number of C1 or C2.**

---

## 1. Re-fetch and byte comparison

| URL | HTTP | bytes | sha256 (observed) | capture match |
|---|---|---|---|---|
| https://www.rfc-editor.org/rfc/rfc3629.txt | **200** (GET, `http_code=200`; HEAD `HTTP/2 200`) | **33856** | **a2a3a39457d30420c812f87a38cc2b9194832f6982ef17e619de7d816879d6a6** | `cmp` → **IDENTICAL** to `census/round-91/srcs/rfc3629.txt` |

- Access date observed: **2026-11-08** (`utc_date: 2026-11-08T16:20:59Z`, `local_date:
  2026-11-08T13:20:59-0300`). Two independent GETs (13:19:54Z and 16:20:59Z) returned byte-identical
  payloads, both sha `a2a3a394…`.
- Response headers recorded: `content-type: text/plain;charset=utf-8`, `etag:
  W/"4f24eee655af129dc58e2936e6595fce"`. The HEAD response carried **no** `content-length` and **no**
  `last-modified`; the size evidence is the GET `size_download=33856` plus the byte count of the saved
  body, which equals the capture exactly.
- Byte shape of the capture: 787 newlines, **0 CRLF**, 0 bare CR, 0 non-ASCII bytes, 14 form feeds,
  final bytes `[Page 14]\n\x0c\n`. So byte offsets equal character offsets and the file is plain ASCII —
  the "lines" in the registry row are unambiguous.
- Registry row `S354` (`corpus/SOURCES.md:293`) records exactly `HTTP 200, 33856 bytes, sha256
  a2a3a3945…, capture census/round-91/srcs/rfc3629.txt, opened 2026-11-08`. **Every one of those cells
  re-verified against the live fetch. No drift.**
- Receipts: `fetch-receipt.txt`, `refetch-hash.txt`, byte copy `rfc3629-refetch-20261108.txt`
  (33856 bytes, sha a2a3a394…).

## 2. Quote location, occurrence count, word count

Prereg target quote: `In a sequence of n octets, n>1, the initial octet has the n higher-order bits set
to 1, followed by a bit set to 0.`

- **Location in the capture: lines 183-185** (§3 UTF-8 definition, page 3). Verbatim:
  - `183|   the remaining 7 bits being used to encode the character number.  In a`
  - `184|   sequence of n octets, n>1, the initial octet has the n higher-order`
  - `185|   bits set to 1, followed by a bit set to 0.  The remaining bit(s) of`
  The quote therefore *starts mid-line-183* ("In a") and ends mid-line-185. The registry row's
  "capture lines 183-185" is correct.
- **Occurrence count: 1** (de-wrapped text, `\s+`→space, `str.count` = 1).
- **Word count: 25** (whitespace tokens, de-wrapped); 115 characters raw. Split across the wrap:
  14 words on the 183-184 visual run, 11 on the 185 tail.
- Reproducibility note for the ledger: a **per-line** grep for the whole sentence returns **0** because
  the sentence wraps at "higher-order". The count is only correct on de-wrapped text; a future validator
  that counts line-wise would report a false absence. (This is a measurement note, not a defect in the
  filed row: the row states "occurrence count 1", which is what de-wrapped counting gives.)
- **Following-octet sentence (the tail rule, grounded end to end)** — capture **lines 187-189**:
  - `187|   encoded.  The following octet(s) all have the higher-order bit set to`
  - `188|   1 and the following bit set to 0, leaving 6 bits in each to contain`
  - `189|   bits from the character to be encoded.`
  De-wrapped: "The following octet(s) all have the higher-order bit set to 1 and the following bit set to
  0, leaving 6 bits in each to contain bits from the character to be encoded." — 32 words, occurrence
  count 1. Corroborated by §4's ABNF at line 291: `UTF8-tail   = %x80-BF` (9 occurrences of `UTF8-tail`
  in the document). So §3 supplies both halves of the rule C2 needs: the initial octet's role (183-185)
  and the tail octets' role (187-189) — the cut-legality rule is grounded, not half-quoted.
- **Terminology observation (paraphrase, not a falsification).** The string `continuation` occurs **0**
  times in RFC 3629. The prereg's C2 sentence says "a sequence is an initial octet plus its
  *continuation octets*"; RFC 3629 §3 spells the same octets "the initial octet" and "The following
  octet(s)", and §4 calls them `UTF8-tail`. The substance is identical (the tail octets carry the
  `1`+`0` high-bit prefix, i.e. exactly the continuation octets), so **this does not falsify the C2
  wording** — it is a vocabulary provenance note. Flip condition: if a later round quotes the C2
  sentence as verbatim RFC text, or writes "RFC 3629 calls them continuation octets", that becomes a
  `FALSIFIES-WORDING` item; today the sentence is a paraphrase of §3 and says so.
- Receipt: `quote-receipt.txt` (verbatim numbered lines 180-189, counts, ABNF line).

## 3. One reject candidate — RFC 3629 §10 Security Considerations

Candidate opened: **§10 Security Considerations, capture lines 523-570** (header `10.  Security
Considerations` at line 523). Quote extracted: "Implementers of UTF-8 need to consider the security
aspects of how they handle illegal UTF-8 sequences." — line **525**, occurrence count **1**, **16
words**; the paragraph continues on 526-527 ("It is conceivable that in some circumstances an attacker
would be able to exploit an incautious UTF-8 parser…", occurrence count 1).

**Verdict for THIS cell (C2's UTF-8 window-boundary rule): REJECT — do not open.** Reason: §10 states
*hazard semantics of illegal sequence handling* — overlong `C0 80` decoded as NUL, the `2F C0 AE 2E 2F`
`/../` bypass, buffer sizing against 5- and 6-byte sequences, and normalization ("same thing"
ambiguity). All four of those facts are present in the section (`C0 80` yes, `5- and 6-byte sequences`
yes, `Unicode Normalization Forms` yes). None of them states an octet-role/sequence-unit rule; the unit
C2 cuts on is already fully stated by §3 (lines 180-189) and §4's ABNF (line 291), which is what S354
carries. §10 would ground a *different* claim (an obligation to reject invalid sequences, or the
security consequence of a mis-parse) and S354's own scope cell already declares "the security
considerations, MIME registration and BOM discussion are out of scope here".

**Flip condition (specific, checkable):** admit §10 as its own row in the same round if, and only if,
one of these becomes true —
(a) a C2 sentence or fixture case asserts a **validity obligation** on the excerpt (e.g. "the excerpt
MUST itself be well-formed UTF-8", or a KFF case demanding the lone `0x85` be *rejected* rather than
kept with its `\xNN` spelling) — C2 currently asserts a *boundary* property only;
(b) a variant or attack item is characterized as a **security-relevant mis-parse** (an attacker-chosen
excerpt changing a decision) rather than as a spelling/cell-collision difference;
(c) the lane starts consuming §10's `2F C0 AE 2E 2F` or normalization material as evidence for any
other artifact.
On flip, open it as a new id with the line-525 quote above (16 words, occurrence 1) and scope it to §10
only.

**Screened alternative (the other candidate the brief named), also rejected — and for a harder
reason.** Python `codecs` page § "IncrementalDecoder Objects" (`https://docs.python.org/3/library/
codecs.html`, live fetch HTTP 200, 181610 bytes — matching S351's recorded size): "The
IncrementalDecoder class is used for decoding an input in multiple steps." That is a *decoder-API*
contract for stateful partial input; the filed tool does a **one-shot** decode —
`raw.decode("utf-8", "surrogateescape")` at `tools/souji-record-agreement.py:213` (grep of the tool
shows no `codecs` import and no incremental/`getstate` use). So the page does not describe the mechanism
under claim. Second, decidable reason: that URL is already carried by **three** registry rows
(S253, S256, S351) — the census emits W04 duplicate-url for S256 and S351 today — so a fourth row adds
another duplicate-URL warning for no grounding gain. Flip: admit only if the tool moves to an
incremental/streaming decode (then the partial-input contract becomes the cited object).
Receipts: `reject-receipt.txt`, `reject-alt-receipt.txt`, `codecs-20261108.html.head` (4 KB pointer,
not a snapshot claim).

## 4. Lane sources census and duplicate-URL check

- Command: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
  /home/vgpnk/Projects/shokunin souji` → **exit code 0**.
- Output shape: **90** finding lines = **89** `W04` duplicate-url warnings + the closing
  `souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`. **0** `E*` (malformed
  row/id/kind/tier/status/date/recheck/community/used-by) lines; no `unlisted` line.
- Row count: `census --root … souji` → `souji	rows	276` (tier.A 263, tier.B 10, tier.C 3; status.mined
  230, queued 14, rejected 32), identical to the FLEET totals (`FLEET rows 276`, `FLEET missing 0`,
  `FLEET tier.invalid 0`, `FLEET status.invalid 0`). Independently, `grep -cE '^\| S[0-9]{3}'
  corpus/SOURCES.md` = **276** data rows.
- **Duplicate URL of `rfc-editor.org/rfc/rfc3629.txt`: NONE.** Exact URL string occurs **1** time in the
  lane registry (row `S354`, line 293); `rfc-editor.org` occurs **1** time; the validate output contains
  **0** W04 lines naming `rfc-editor`; a fleet-wide scan of every `*/corpus/SOURCES.md` finds the URL only
  in `souji-shokunin`. (For contrast, `docs.python.org/3/library/codecs.html` appears 4 times —
  rows S253/S256/S351 plus one prose mention at line 419 — and draws two W04s.)
- Receipts: `census-receipt.txt`, `dupurl-receipt.txt`.

## 5. Falsification statement (Amendment 59)

**FALSIFIES-WORDING: none. FALSIFIES-NUMBER: none.**

Checked against my own artifacts, which are the only ones I may speak for:
- C1's wording and numbers do not touch the source corpus; nothing I measured bears on the battery
  predicate. Unchanged.
- C2's number cells do not touch the source corpus; its prose rests on S354. Every S354 cell I could
  falsify (HTTP 200, 33856 bytes, sha a2a3a394…, capture path, opened 2026-11-08, quote lines 183-185,
  25 words, occurrence count 1) **re-verified true**, and the sequence-boundary rule is grounded in §3
  end to end (initial octet 183-185, following octets 187-189, ABNF tail 291).
- The only wording nuance found is the "continuation octets" paraphrase (§2 above), which is faithful to
  §3 and therefore not a falsification; its flip condition is recorded so a later verbatim-quotation
  claim cannot widen it silently.

## 6. Tooling / hygiene

- No tool installed or upgraded (none was needed); pacman untouched. No host sysctl touched.
- Scratch `/fast/scratch/hyaku/souji-r91/R91ScoutSources` deleted before yield; receipts copied here
  first. No git/jj command was run anywhere in this seat; no lane file was written outside this seat
  dir.
