# S90ScoutSources — souji round 90, scout seat (sources)

Lane `souji-shokunin` (id `souji`). Lane base `bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2`;
lane HEAD at check time `fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (commit F, the preregistration alone).
Seat scope: open the round's source, verify the capture, open ONE reject candidate, run the lane's
sources census. **No commit, no push, no git/jj mutation, no edit to any lane file outside my seat
directory.** Every git call below is read-only.

Scratch used: `/fast/scratch/hyaku/souji-r90/S90ScoutSources/` — **deleted before this yield**
(`rm -rf` of the whole subdir); receipts were copied into the seat dir first. Nothing left behind.

---

## 1. Fetch table (live, today 2026-11-08)

Command (`receipts/verify.sh` §1):

```
curl -sS -L -o <name> -w "$u http=%{http_code} bytes=%{size_download} effective=%{url_effective}\n" "$u"
```

| URL | HTTP | bytes | sha256 | capture match |
|---|---|---|---|---|
| `https://www.unicode.org/reports/tr14/` | **200** | **226166** | `296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0` | **YES** — `cmp` byte-identical to `census/round-90/srcs/tr14.html` (tracked at HEAD) |
| `https://www.unicode.org/Public/UCD/latest/ucd/LineBreak.txt` | **200** | **266206** | `ae8cf1970c73f3f1a12d77852df96c4b2b1723ca8b388e36bb5739250c6849de` | **YES** — `cmp` byte-identical to `census/round-90/srcs/LineBreak.txt` (tracked at HEAD) |
| `https://www.unicode.org/reports/tr13/` (reject candidate) | **200** | **6348** | `bfa7f97b94c13c0764d99140388f88b20cbce62957d5e7174fab63d29a667c78` | **YES** — `cmp` byte-identical to the working-tree file `census/round-90/srcs/tr13.html`, **which is UNTRACKED in git** (see §6, integration note) |

No redirect (`url_effective` equals the requested URL for all three).

**Capture metadata (from the capture itself, not from the lane's prose):**

`census/round-90/srcs/tr14.html` header table (lines 44–68):
- **Version: Unicode 18.0.0** (line 47)
- **Date: 2026-09-01** (line 55)
- **This Version: `https://www.unicode.org/reports/tr14/tr14-57.html`** (lines 58–61)
- **Revision 57** (line 4603: `<p><b>Revision 57:</b></p>` — "Reissued for Unicode 18.0")

`https://www.unicode.org/reports/tr14/tr14-57.html` fetched separately: HTTP 200, 226166 bytes,
sha256 `296df533…acc7c0` — **byte-identical to `/reports/tr14/`**, so the live URL and the versioned
URL are the same document today.

`census/round-90/srcs/LineBreak.txt` header:
- `# LineBreak-18.0.0.txt`
- `# Date: 2026-08-07, 14:59:16 GMT`

**The preregistration's SOURCE paragraph** (`census/round-90/preregistration.txt` lines 124–130)
states: *"Unicode 18.0.0 rev 57, § NL: Next Line — capture census/round-90/srcs/tr14.html (HTTP 200,
226166 bytes, sha256 296df533…, opened 2026-11-08)"*. Every element of that statement — HTTP status,
byte count, sha256, Unicode version, revision number, date — **re-verifies against the live capture
and the live fetch.** ✔

---

## 2. The quote the prereg uses

Quote (verbatim, as printed in the prereg line 127–128 and in the S353 registry row
`corpus/SOURCES.md:292`):

> The NL class acts like BK in all respects (there is a mandatory break after any NEL character).

**Location** — `census/round-90/srcs/tr14.html`, § **NL: Next Line (Non-tailorable)**:

- line **2870**: `<h3 …><a name="NL" href="#NL">NL</a>: Next Line (Non-tailorable)</h3>`
- lines **2872–2877**: the class table; `<td class="nb-la">0085</td>` at **2874**, `<td class="nb-lb">NEXT LINE (NEL)</td>` at **2875**
- line **2878**: `<p>The <a class="charclass" href="#NL">NL</a> class acts like <a class="charclass" href="#BK">BK</a>`
- line **2879**: `	in all respects (there is a mandatory break after any NEL character).`
- lines 2880–2882 continue: *"It cannot be tailored, but implementations are not required to support the NEL character; see the discussion under BK."*

**Word count: 18** — `printf '…' | wc -w` → `18`; Python whitespace split → 18.
The prereg says "(18 words)"; the S353 row says "(18 words)". ✔

**Occurrence count: 1** — in the tag-stripped capture the sentence occurs exactly once
(`t.count(q) == 1` under every normalizer tried). The knowledge file's "occurrence count 1" ✔.

**Offset — FINDING (LOW, locator only).** The prereg (line 128), the S353 registry row
(`corpus/SOURCES.md:292`) and `corpus/knowledge/nel-byte-character-pair.md` all state
*"tag-stripped offset 82360"*. The prereg does not state which normalizer produced that number, and
**the number does not reproduce under any normalizer I could construct for the quote as printed**:

| normalizer | char offset of the quote as printed | byte offset |
|---|---|---|
| drop tags + `\n\t`→`' '` | **82199** | **82357** |
| drop tags + `\n\t`→`' '`, entity-decoded | 81944 | 82139 |
| drop tags, whitespace collapsed (`\s+`→`' '`) | 68768 | 68926 |
| drop tags, whitespace collapsed, entity-decoded | 68483 | 68640 |
| bs4 / lxml `get_text()`, whitespace collapsed | 68182 | 68339 |
| tags→`' '`, whitespace collapsed | 69082 | — |
| `html.parser` `handle_data` join, `\n\t`→`' '` | 81615 | 81810 |

**82360 is exactly the byte offset of the same sentence with its first word dropped**
(`" NL class acts like BK in all respects (there is a mandatory break after any NEL character)."`,
i.e. one word later) — a **3-byte slip equal to `len("The")`**. A brute-force sweep over
tag-removal × entity-handling × whitespace-normalisation × HTML-parser pipelines
(>50 combinations, plus the archived revisions `tr14-9/32/40/43/47/51/57.html`, whose offsets for the
same quote are 72946/72229/71632/72330/78900/82357) produced **no** combination yielding 82360 for the
quote as printed.

**Assessment: this is a locator slip in a provenance pointer, not a falsification of C1 or C2.**
The quote itself, its 18 words, its occurrence count 1, its section, its capture sha/bytes/status, and
the Unicode version/revision/date all verify exactly. The offset is not part of either claim's
predicate (C1 = the battery's `killed_total=31`; C2 = the fixture's `tool_pass=12`), so no claim
wording is falsified. **Action for the L1 (optional, cheap):** either drop the offset and keep
"occurrence count 1 / § NL: Next Line / capture lines 2873–2879", or state the normalizer alongside it
(`drop tags, '\n\t'→' ', UTF-8 byte offset` → **82357**). If the L1 prefers to keep 82360, it should
say the offset is of the sentence *minus its leading "The"*. This is a **narrowing amendment at
most** (Amendment 59) and needs no repair to any claim.

Minor companion nit (same files): the S353 row's phrase *"the class table row `0085 / NEXT LINE
(NEL)` at capture lines 2873-2879"* spans a range that runs past the row itself — the row is
`<tr>` 2873 / cells 2874–2875 / `</tr>` 2876, the table ends 2877, and the quoted paragraph is
2878–2879. The range contains both, so it is not false; the precise anchors are 2873–2876 (row) and
2878–2879 (quote).

---

## 3. The data-file line for `0085`

From `census/round-90/srcs/LineBreak.txt` (live fetch byte-identical), line **95**:

```
0085           ; NL # Cc         <control-0085>
```

**The class it names is `NL`** (Next Line), general category `Cc` (Other, Control). Neighbours for
contrast: line 94 `0080..0084 ; CM # Cc [5] <control-0080>..<control-0084>` and line 96
`0086..009F ; CM # Cc [26] <control-0086>..<control-009F>` — i.e. U+0085 is the **only** NL
character in that block and is singled out by the data file exactly as UAX #14's § NL singles it out.

The S353 registry row quotes this line as
`` `0085           ; NL # Cc         <control-0085>` `` — I compared the quoted string to the capture
line **byte for byte: identical** (exact match, not just normalized). ✔
(The knowledge file's `LineBreak.txt` reference is likewise correct.)

---

## 4. Reject candidate — UAX #13 (Unicode Newline Guidelines)

**Opened:** `https://www.unicode.org/reports/tr13/` (HTTP 200, 6348 bytes, sha256 `bfa7f97b…a667c78`).
**What it now serves:** a *supersession tombstone*, not the guideline. Its live text contains, once:

> The material formerly covered by UAX #13: Unicode Newline Guidelines has been incorporated into the
> Core Specification of the Unicode Standard, starting with Version 4.0

(present verbatim, occurrence count 1; **25 words** by `wc -w` — note the lane's uncommitted
knowledge file calls this quote *"(24 words)"*; see §6.)

Because the live URL is a tombstone I also opened the **archived** version it points to,
`https://www.unicode.org/reports/tr13/tr13-9.html` (HTTP 200, 21897 bytes, sha256
`6f38841a84aee71b3da64a6d1147642dc2efe5eb41bc0426189a14937d70333a`), and read its substance. Three
sentences bear on the lane's neighbourhood:

- *"NEL is not actually defined in ASCII: it is defined in ISO 6429 as a C1 control."* (offset 3642)
- *"…on input and in interpretation, treat CR, LF, CRLF, and NEL the same. Only on output do you need
  to distinguish between them."* (offset 6804)
- *"A readline function should stop at NLF, LS, FF, or PS."* (offset 8657)

**VERDICT: REJECT.**

**Reason.** UAX #13 is about **newline *conventions*** — which character a producer used to mean
"new line" (CR / LF / CRLF / NEL / LS / PS), how to interpret one on input, and how to convert it.
The lane's r90 C2 question is different in kind: it is about **how to spell a character in a one-line
record cell so that a character and a raw byte cannot collide**, and its ground is (i) UAX #14's NL
class for U+0085 — mandatory break after NEL, and (ii) Python's `str.splitlines()` boundary set
(S348) for which characters must be escaped at all. UAX #13 adds nothing the lane may act on for
that decision: it never discusses the byte-vs-character distinction, never mentions surrogates or
`surrogateescape`, and its own text says to *treat* NEL as one of several interchangeable newline
flavours on input — the opposite of what the lane needs, which is to *distinguish* U+0085 from the
byte 0x85. The lane's escape set stays exactly as UAX #14 + Python's boundary list define it.
Additionally the live URL is superseded since Unicode 4.0, so citing `tr13/` itself would be citing a
tombstone.

**Flip condition.** Admit UAX #13 (at its versioned/archived URL, or Core Specification §5.8) if the
lane ever has to decide **which newline convention a foreign producer followed** — i.e. normalising
incoming CRLF vs LF vs NEL from another system, or emitting a canonical newline — which is a
different question from *spelling* one. Until then it is inert for this lane's tools.

**Note for the L1.** The lane's own uncommitted knowledge file
`corpus/knowledge/nel-byte-character-pair.md` already reaches the same REJECT with the same URL and
the same tombstone quote — my independent read confirms the verdict and adds the archived content
above. Its word count for that quote should read **25**, not 24 (see §6).

---

## 5. The lane's sources census

Command (exactly as assigned):

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
```

- **exit code: 0**
- **output: 90 lines** — 89 × `W04 … duplicate url … across scopes` + 1 × `souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`
- **E-code lines: 0** (no malformed row, no bad id, no duplicate id, no enum violation, no missing
  `used-by` path — so the newly added **S353** row is census-clean)
- **registry row count: 275** (from `census` mode: `souji rows 275`; tier.A 262 / tier.B 10 /
  tier.C 3; status.mined 229 / queued 14 / rejected 32; FLEET rows 275, missing 0).
  For reference, `HEAD:corpus/SOURCES.md` has **274** rows — the 275th is the uncommitted S353 row.
- **Stability:** my `validate` output is **byte-identical** to the committed pre-freeze receipt
  `census/round-90/records/sources-census-before.txt` (`diff` → identical). So the registry gained no
  new warning and no new error between the pre-freeze census and now, and S353 introduced **zero**
  W-codes and zero E-codes.

---

## 6. Integration notes for the L1 (this seat edits nothing)

These are observations about *uncommitted* lane state that the L1 — the integration owner — must
handle when it lands this round. None of them falsifies C1 or C2.

1. **`census/round-90/srcs/tr13.html` is untracked.** The knowledge file cites
   "capture census/round-90/srcs/tr13.html" with sha256 `bfa7f97b…a667c78`; the file exists in the
   working tree and is byte-identical to the live fetch, but `git ls-files census/round-90/srcs/`
   lists only `LineBreak.txt` and `tr14.html`. If the knowledge file is landed without this capture,
   the citation points at a path absent from the committed tree.
2. **`corpus/knowledge/nel-byte-character-pair.md` is untracked** (`??` in `git status`), and the
   **S353 row is an uncommitted modification** to `corpus/SOURCES.md` (` M`), as is `corpus/README.md`.
   `git log -S'S353' -- corpus/SOURCES.md` returns nothing: S353 has never been committed.
3. **Word count slip in the knowledge file:** the UAX #13 tombstone quote is counted "(24 words)";
   `wc -w` on the quote as printed gives **25**. (The tr14 quote's "18 words" is correct.)
4. **Offset slip in three places** (prereg line 128, `corpus/SOURCES.md:292`, knowledge file): "tag-stripped
   offset 82360" for a quote whose byte offset under `drop tags, '\n\t'→' '` is **82357**; 82360 is the
   offset of the same sentence *without* its leading "The". See §2. Suggested resolution: keep
   "occurrence count 1", "§ NL: Next Line", "capture lines 2873–2879", and either name the normalizer
   with 82357 or drop the offset.

Working-tree state at check time (read-only `git status --porcelain corpus/ census/round-90/`):

```
 M corpus/README.md
 M corpus/SOURCES.md
?? census/round-90/records/c1-after.txt
?? census/round-90/records/c2-after.txt
?? census/round-90/records/prefreeze-c1-both.txt
?? census/round-90/srcs/tr13.html
?? corpus/knowledge/nel-byte-character-pair.md
```

---

## 7. What this seat did NOT check (stated limits)

- I did **not** run either claim's counter (C1 battery, C2 fixture). Those are other seats' scopes; my
  job was the source, the capture, the reject candidate and the census. My census run is the lane's
  `sources-census.sh validate`, not C1/C2.
- I did **not** adjudicate the C1 or C2 predicates, and I make **no** claim that either verifies on
  the strength of this seat's work. This report's bearing on the claims is limited to the SOURCE
  paragraph's factual content, which re-verifies (with one locator slip, §2).
- The offset sweep in §2 covers ~50 normalizer/pipeline combinations I could construct, plus the seven
  archived `tr14` revisions. A normalizer outside that space could in principle produce 82360 for the
  quote as printed; I found none, and I state the reproduction so the L1 can re-run it.
- `tr13-9.html` (the archived UAX #13) was read as text; I did not render the PDF or compare it
  against the Core Specification §5.8 text itself.
- No file in the lane was created, modified or deleted by this seat. No git or jj command mutated
  anything.

---

## 8. Reproducer

`receipts/verify.sh` (in this seat's directory) re-runs every measurement in this report in one
pass; `receipts/verify.out` is its verbatim output. It writes only into
`/fast/scratch/hyaku/souji-r90/S90ScoutSources/` (or `$S`) and reads the lane read-only.

```
bash .ufo/waves/round-90/w1/S90ScoutSources/receipts/verify.sh
```

Key lines of `verify.out`:

```
https://www.unicode.org/reports/tr14/ http=200 bytes=226166 effective=https://www.unicode.org/reports/tr14/
https://www.unicode.org/Public/UCD/latest/ucd/LineBreak.txt http=200 bytes=266206 effective=https://www.unicode.org/Public/UCD/latest/ucd/LineBreak.txt
https://www.unicode.org/reports/tr13/ http=200 bytes=6348 effective=https://www.unicode.org/reports/tr13/
296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0  tr14
ae8cf1970c73f3f1a12d77852df96c4b2b1723ca8b388e36bb5739250c6849de  LineBreak.txt
bfa7f97b94c13c0764d99140388f88b20cbce62957d5e7174fab63d29a667c78  tr13
tr14 == census/round-90/srcs/tr14.html
LineBreak.txt == census/round-90/srcs/LineBreak.txt
tag-stripped (drop tags, '\n\t'->' ') char offset: 82199
  byte offset of the quoted sentence 'The NL class ...': 82357
  byte offset of the same sentence MINUS its first word ('The'), leading space kept: 82360
occurrence count in tag-stripped text: 1
word count (whitespace split): 18
95:0085           ; NL # Cc         <control-0085>
validate EXIT=0
output lines: 90
E-code lines: 0
W-code lines: 89
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
souji	rows	275
validate output IDENTICAL to committed pre-freeze receipt census/round-90/records/sources-census-before.txt
```

**Scratch disclosure:** `/fast/scratch/hyaku/souji-r90/S90ScoutSources/` was removed (`rm -rf`) before
this yield; all receipts were copied into
`.ufo/waves/round-90/w1/S90ScoutSources/receipts/` first. No scratch remains anywhere under
`/fast/scratch/hyaku/`, and nothing was written to `/tmp` or outside the named subdir.
