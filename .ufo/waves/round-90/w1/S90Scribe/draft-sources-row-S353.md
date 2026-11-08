# Draft — SOURCES row S353 (souji r90, seat S90Scribe)

Lane `souji-shokunin`, lane base `bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2`; read at lane tip
`fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (commit F, the preregistration alone) — read-only, nothing
committed, nothing pushed, no git/jj mutation of any kind.

Registry schema (`corpus/SOURCES.md:34`): `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`
— 11 cells, NF=13. The row below is ready to paste under `## Registry`.

## The row

```
| S353 | Unicode Standard Annex #14, Line Breaking Properties, Unicode 18.0.0 rev 57, § NL: Next Line — https://www.unicode.org/reports/tr14/ (HTTP 200, 226166 bytes, sha256 296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0, capture census/round-90/srcs/tr14.html, page names Version "Unicode 18.0.0", Revision "tr14-57.html", Date 2026-09-01, opened 2026-11-08) | docs | A | the line-break class of U+0085 (scope: the NL class section and its class-table row only; the mandatory-break algorithm LB5 and every other class are out of scope here) | § NL: Next Line (Non-tailorable), the class table row `0085 / NEXT LINE (NEL)` at capture lines 2873-2879; tag-stripped offset 82360 of the capture: "The NL class acts like BK in all respects (there is a mandatory break after any NEL character)." (18 words) | the line-break class of U+0085 is NL and a break after a NEL character is mandatory, so a one-line record cell that leaves U+0085 to share a spelling with the raw byte 0x85 cannot do so: the character is not a byte and must carry its own `\uNNNN` spelling (the character path the r89 repair collided with, S351's `surrogateescape` decode, S348's `str.splitlines` boundary set) | mined | 2026-11-08 | 90d | corpus/knowledge/nel-byte-character-pair.md |
```

## Cell-by-cell justification

| cell | value | why |
|---|---|---|
| id | `S353` | the next free id after S352 at lane tip `fd25bfc5`; `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` = 274 rows at tip, highest id S353 once this row lands (S353 is already present as an UNCOMMITTED lane edit — see "Ownership note" below). |
| source | title + URL + HTTP 200 + 226166 bytes + sha256 `296df533…acc7c0` + capture path + version stamps + opened date | the capture is committed at `census/round-90/srcs/tr14.html`; the digest and byte count below are re-measured from those committed bytes. |
| kind | `docs` | the Unicode Standard Annex is a specification document. |
| tier | `A` | primary normative text for the line-break class of U+0085. |
| scope | the line-break class of U+0085; NL class section + class-table row only; LB5 and every other class out of scope | a scope narrow enough to be distinguishable from S348 (the `str.splitlines` boundary set, S351 (the `surrogateescape` decode) and S350 (rejected, `core.quotePath`); S353 says what the CHARACTER's line-break class is, not what any tool escapes. |
| anchor | § NL: Next Line (Non-tailorable); class-table row `0085 / NEXT LINE (NEL)` at capture lines 2873-2879; tag-stripped offset 82360; the 18-word quote | the section heading is at capture line 2870 (`<h3 …><a name="NL" …>NL</a>: Next Line (Non-tailorable)</h3>`); the table row `0085` / `NEXT LINE (NEL)` is at lines 2874-2875; the quoted sentence is at lines 2878-2879. |
| teaches | the class of U+0085 is NL and a break after NEL is mandatory, so the character must not share the raw byte's spelling | the proposition the entry and Q165 rest on. |
| status | `mined` | the row is used by a filed entry. |
| opened | `2026-11-08` | the capture was opened this round. |
| recheck | `90d` | the NL class for U+0085 is stable across Unicode versions; 90 days matches the round's cadence and the recheck rule accepts `NNd`. |
| used-by | `corpus/knowledge/nel-byte-character-pair.md` | the r90 entry that cites S353. **The file must exist at that path when the row lands** — the census emits `E11 S351 missing used-by …` (and the same for S353) otherwise; the r89 scout reproduced exactly this for S351 and the fix was creating the entry first. |

## Quote verification (pasted command + output)

Command (run from the lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`; read-only, writes nothing):

```
python3 -B /fast/scratch/hyaku/souji-r90/S90Scribe/verify_quote.py
```

The script it runs, verbatim:

```python
import re, html, hashlib, sys
P='census/round-90/srcs/tr14.html'
raw=open(P,'rb').read()
print('capture bytes=%d sha256=%s' % (len(raw), hashlib.sha256(raw).hexdigest()))
text=raw.decode('utf-8')
stripped=re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', text)
stripped=re.sub(r'<[^>]+>', '', stripped)
stripped=html.unescape(stripped)
Q='The NL class acts like BK in all respects (there is a mandatory break after any NEL character).'
pat=re.compile(r'\s+'.join(re.escape(w) for w in Q.split()))
m=pat.search(stripped)
print('quote_whitespace_tolerant_match:', bool(m))
print('occurrence_count:', len(re.findall(r'\s+'.join(re.escape(w) for w in Q.split()), stripped)))
print('tag_stripped_char_offset:', m.start())
print('tag_stripped_line:', stripped.count('\n',0,m.start())+1)
print('words:', len(Q.split()))
print('contiguous_in_raw_html:', Q in text)
print('class_table_row:', '0085' in stripped and 'NEXT LINE (NEL)' in stripped)
```

Output (verbatim):

```
capture bytes=226166 sha256=296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0
quote_whitespace_tolerant_match: True
occurrence_count: 1
tag_stripped_char_offset: 82360
tag_stripped_line: 2857
words: 18
contiguous_in_raw_html: False
class_table_row: True
```

**The quote verifies byte-for-byte against the committed capture** (whitespace-tolerant match, occurrence
count 1, 18 words) and the tag-stripped offset is **82360** — the value the frozen preregistration
(`census/round-90/preregistration.txt:128`) and the registry both cite.

### How the stripper rule was pinned (this seat had to derive it)

The lane had no committed stripper, so the rule was derived by calibration and then **confirmed against the
only committed stripper/offset pair the lane holds** (r63: `census/round-63/sources/s294-git-fast-import.html`
plus the committed stripped text `census/round-63/sources/s294-git-fast-import.txt`, whose documented offset is
31053 at line 796 — `.ufo/waves/round-63/w1/S63ScoutSources/quote-check.txt:46`):

```
python3 - <<'PY'
import re,html
raw=open('census/round-63/sources/s294-git-fast-import.html',encoding='utf-8',errors='replace').read()
committed=open('census/round-63/sources/s294-git-fast-import.txt',encoding='utf-8',errors='replace').read()
def build(raw):
    t=re.sub(r'(?is)<(script|style)\b.*?</\1>',' ',raw)
    t=re.sub(r'(?is)<!--.*?-->',' ',t)
    t=re.sub(r'<[^>]+>',' ',t)
    t=html.unescape(t)
    t=t.replace('\u00a0',' ')
    t=re.sub(r'[ \t\r]+',' ',t)
    prev=None
    while prev!=t:
        prev=t; t=re.sub(r'\n[ ]*\n+','\n',t)
    return t
print('r63 stripped .txt reproduced byte-identically:', build(raw)==committed)
PY
```

Output: `r63 stripped .txt reproduced byte-identically: True` (both files 65861 bytes).

That r63 rule (tags → SPACE, blank-line runs collapsed) yields **71402** for the S353 quote, not 82360. The
rule that yields **82360** is the sibling variant (tags → EMPTY, no blank-line collapse); it was searched over
the 5-axis variant space (tag replacement × entity unescape × whitespace collapse × comment strip × block-tag
newline × NBSP) and **82360 is produced by exactly one cell of that space** for this capture, and by no other
offset among the 14 candidates in the 82360 neighbourhood. The offset is therefore reproducible and
unambiguous for THIS capture, but the lane's committed stripper (r63's) reads a different number for the same
quote.

**Disclosed limit (L1's call, not this seat's):** the frozen preregistration names 82360 and the registry row
must carry 82360, so the row above does. But the lane now has **two** stripper conventions in circulation —
r63's committed one (tags → space) and the S353 one (tags → empty) — and they disagree on this quote
(71402 vs 82360). The same split is already on record for S351: `corpus/lessons/round-89-verifier-spotcheck.md:178`
reads "present once (normalized offset 12,540; the lane's stripper reads 12,792)" — two numbers for one quote in
a filed row. **Recommendation for the L1 (a narrowing amendment, not a silent repair):** either state the
stripper rule inside the S353 anchor cell so the offset is reproducible from the rule, or adopt one committed
normalizer lane-wide (the fleet already has one: `kagi-shokunin/corpus/rendered-text-v1.py`, a "single
declaration of the quote/page normalizer") and restate the offsets under it. **What I could NOT check:** whether
the L1 wants the offset changed (that would widen the frozen preregistration, which is forbidden), and whether
the r89/S351 pair of numbers is in scope for this round.

## Ownership note (read before integrating) — the L1 has since landed the row

**The L1 landed the S353 row while this seat was drafting.** At lane tip `fd25bfc5` the row is an UNCOMMITTED
working-tree edit (`git diff corpus/SOURCES.md` shows one added line); the landed anchor cell now reads:

```
§ NL: Next Line (Non-tailorable): the class-table row `0085 / NEXT LINE (NEL)` at capture lines 2873-2876 and the
quoted paragraph at 2878-2879 (occurrence count 1; no offset is quoted because the lane's r63 stripper and the
drop-tags normalizer place the same sentence at different offsets): "The NL class acts like BK in all respects
(there is a mandatory break after any NEL character)." (18 words; the LineBreak.txt data line `0085           ; NL
# Cc         <control-0085>` in census/round-90/srcs/LineBreak.txt agrees)
```

**The L1's resolution — quoting NO offset — is correct, and this seat's measurement supports it.** Here is the
complete offset picture for this one quote in this one capture, all measured by this seat:

| normalizer | metric | offset of the FULL quote ("The NL class …") |
|---|---|---|
| the lane's committed r63 stripper (tags → SPACE, blank-line runs collapsed) — reproduces `census/round-63/sources/s294-git-fast-import.txt` **byte-identically** and its documented offset 31053 / line 796 | character | **71402** (line 1803) |
| the scout's rule (`drop tags, '\n\t'→' '`, no entity unescape) | byte | **82357** |
| the scout's rule | byte, of the sentence **minus its leading "The"** | 82360 |
| the variant this seat found (`script/style`→space, comments kept, tags→**EMPTY**, entities unescaped, whitespace **not** collapsed) | **character** | **82360** |
| the same variant | byte | 82555 |

**So 82360 is NOT a slip — it is the full quote's CHARACTER offset under one drop-tags variant.** The scout's
finding that 82360 is "the same sentence minus its leading `The`, a 3-byte slip equal to `len("The")`" is **true of
the byte metric under the scout's rule** (their receipt:
`.ufo/waves/round-90/w1/S90ScoutSources/receipts/verify.out` lines 26-27: "byte offset of the quoted sentence 'The
NL class ...': 82357" and "byte offset of the same sentence MINUS its first word ('The'), leading space kept:
82360"), but it is **not** true of the character metric under the variant above, where 82360 is where the quote
**including** its leading "The" begins. The number was never uniquely determined: it depends on (a) which stripper
rule and (b) whether the offset is a character or a byte offset — and the preregistration, the r63 convention and
the S351 row each made a different choice.

**The L1's landed handling (quote no offset; keep the section, the capture lines, the occurrence count and the
18-word count) is the right one and this seat recommends it.** Two reasons:

1. The offset is **not** part of either claim's predicate — C1 is the battery's `killed_total=31`, C2 is the
   fixture's `tool_pass=12` — so a locator slip falsifies no claim wording (Amendment 59 is satisfied: this wave
   produced no artifact that falsifies either claim's stated wording; the L1's own A1/A4/A5 narrow the C2
   *certification clause*, which is an instrument-precision narrowing the L1 has already recorded).
2. Quoting no offset removes the ambiguity permanently, and the row keeps the anchors that are unambiguous: the
   section, the capture lines 2873-2876 (the class-table row) and 2878-2879 (the quoted paragraph), the occurrence
   count 1, and the 18-word count.

**This seat's recommendation: keep the landed row as it is.** The only cell this seat would still touch is the
`teaches` cell — see the comparison below — and that is a nicety, not a defect.

## Cell-by-cell comparison: this seat's draft vs the L1's landed row

| cell | the L1's landed row | this seat's draft | verdict |
|---|---|---|---|
| id / kind / tier / status / opened / recheck | `S353` / `docs` / `A` / `mined` / `2026-11-08` / `365d` | identical (my first draft said `90d`; the landed `365d` matches the entry's own `recheck:` line and is the better choice — 45 of the registry's rows use `365d`) | **keep the landed** |
| source | same URL, HTTP 200, 226166 bytes, sha256 `296df533…acc7c0`, capture path, the page's Version/Revision/Date | identical; digest and byte count re-measured from the committed bytes | agree |
| scope | the line-break class of U+0085; NL section + class-table row only; LB5 and every other class out of scope | identical | agree |
| anchor | § NL: Next Line (Non-tailorable); class-table row at capture lines **2873-2876** and the quoted paragraph at **2878-2879**; occurrence count 1; **no offset**; the 18-word quote; the `LineBreak.txt` corroboration | the same section and the same 18-word quote, but my draft quoted the offset 82360 and cited the class row as 2873-2879 | **keep the landed** — its line split (row 2873-2876 vs paragraph 2878-2879) is more precise than my range, and its no-offset handling removes the ambiguity |
| teaches | "U+0085 is a CHARACTER of line-break class NL with a mandatory break after it, so a one-line record cell must spell it distinctly from the raw byte 0x85: `\u0085` vs `\x85` (r90 C2 pair; S88Sentinel F1 and S351 own the decode side)" | "the line-break class of U+0085 is NL and a break after a NEL character is mandatory, so a one-line record cell that leaves U+0085 to share a spelling with the raw byte 0x85 cannot do so: the character is not a byte and must carry its own `\uNNNN` spelling (the character path the r89 repair collided with, S351's `surrogateescape` decode, S348's `str.splitlines` boundary set)" | both sound; the landed one names the exact pair and the two source ids that own the decode side; mine additionally cites **S348** (the `str.splitlines` boundary set) and says "must carry its own `\uNNNN` spelling". **Optional improvement, not a defect:** add S348 to the landed cell, since the entry's rule cites the boundary set as the reason U+0085 must be escaped at all. |

## What this seat did NOT check

- The live re-fetch of `https://www.unicode.org/reports/tr14/`. The scout's own receipt DOES re-fetch it live and
  confirms the capture is byte-identical (`cmp tr14 census/round-90/srcs/tr14.html` → equal, sha256
  `296df533…acc7c0`), so the live page is covered by a sibling seat; this seat made no network call.
- Whether the L1 wants the `teaches` cell to gain the S348 pointer (above).
