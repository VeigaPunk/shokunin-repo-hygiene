# S90Scribe — souji round 90, seat S90Scribe (drafts for the L1 to integrate)

Lane `souji-shokunin` (lane id `souji`), lane base `bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2`; lane tip read at
`fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (commit F — the preregistration alone). Frozen contract read FIRST:
`census/round-90/preregistration.txt`.

**Seat role:** drafts only. Four deliverables for the L1 to integrate: the **S353 SOURCES row**, the
**`corpus/knowledge/nel-byte-character-pair.md` entry**, the **Q165 QUALITY criterion**, and the
**`corpus/lessons/round-90.md` `## Mistakes`** row.

**All four deliverables were landed by the L1 while this seat was drafting** (the S353 row, the knowledge entry, the
`## Mistakes` M1 and the Q165 criterion). This seat's four draft files are therefore the **working papers and the
verification record** for those landed files, plus the exact reproducer for the one defect (the r89 wave-evidence
durability) that the L1's landed M1 covers.

**Nothing was committed, pushed, or mutated.** No `git add`/`commit`/`push`/`checkout`/`reset`/`stash`, no
`jj write`, no fleet-root or sibling-lane file touched, no edit to `MANIFEST.json`, `.ufo/state/*`, `.scratch/*` or
`.ufo/watchdog.log`. Only git **read-only** commands were used (`rev-parse`, `log`, `ls-files`, `ls-tree`,
`check-ignore`, `status`, `clone` + `checkout` inside a scratch fixture clone). Everything I wrote is under
`.ufo/waves/round-90/w1/S90Scribe/` plus this report file.

## Deliverables (paste-ready, no placeholder text)

| # | draft | file | state vs the L1's landed work |
|---|---|---|---|
| 1 | the 11-cell SOURCES row + the quote verification command and its output | `.ufo/waves/round-90/w1/S90Scribe/draft-sources-row-S353.md` | **the L1 has landed the row**; this seat's file is now a cell-by-cell comparison + the offset reconciliation (the recommendation: keep the landed row, optionally add the S348 pointer to `teaches`) |
| 2 | `corpus/knowledge/nel-byte-character-pair.md` | `.ufo/waves/round-90/w1/S90Scribe/draft-knowledge-nel-byte-character-pair.md` | **the L1 has landed an entry** (66 lines); this seat's is the 35-line version the brief bounds |
| 3 | the Q165 QUALITY criterion + the `## Round 90 criteria` section header | `.ufo/waves/round-90/w1/S90Scribe/draft-quality-Q165.md` | **the L1 has LANDED it** — `## Round 90 criteria` at `corpus/QUALITY.md:412`, the Q165 row at `:416`, and the landed row is this seat's rewritten draft **verbatim** (the A1 clause, the discriminating-measurement requirement, the doubled-spelling conjunct, the cell-not-row-count clause, the direct cell comparison as the evidence, and the limits including the raw-window cut and the grep-and-load dead-code clause) |
| 4 | `## Mistakes` for `corpus/lessons/round-90.md` | `.ufo/waves/round-90/w1/S90Scribe/draft-lesson-mistakes.md` | **the L1 has landed an M1** covering the same defect; this seat's file is now the comparison, and it records where the L1's row is more accurate than this seat's draft (the six-file count, the jj-colocated fix) and where this seat's draft adds the exact reproducer |

## The one substantive finding for the L1 (now RESOLVED by the L1's landed row — and my measurement adds to it)

**The S353 offset was ambiguous because the number depends on BOTH the stripper rule AND whether the offset is a
character or a byte offset. The L1 has resolved it by quoting no offset at all, which is correct. My measurement
refines the record of WHY, and it corrects the scout's "3-byte slip" reading for one metric.**

The preregistration (`census/round-90/preregistration.txt:128`) cites the quote's tag-stripped offset **82360**.
Here is the complete picture for this one quote in this one capture, every row measured by this seat:

| normalizer | metric | offset of the FULL quote ("The NL class …") |
|---|---|---|
| the lane's committed r63 stripper (tags → SPACE, blank-line runs collapsed) — reproduces `census/round-63/sources/s294-git-fast-import.txt` **byte-identically** (65861 bytes) and its documented offset 31053 / line 796 | character | **71402** (line 1803) |
| the scout's rule (`drop tags, '\n\t'→' '`, no entity unescape) — `.ufo/waves/round-90/w1/S90ScoutSources/receipts/verify.out:26` | byte | **82357** |
| the scout's rule | byte, of the sentence **minus its leading "The"** | 82360 |
| the variant this seat found (`script/style`→space, comments kept, tags→**EMPTY**, entities unescaped, whitespace **not** collapsed) | **character** | **82360** |
| the same variant | byte | 82555 |

**So 82360 is NOT a slip.** It is the full quote's **character** offset under one drop-tags variant — the variant
where the quote begins *with* its leading "The". The scout's finding is **true of the byte metric** under their
rule (their own receipt: "byte offset of the quoted sentence 'The NL class …': 82357" and "byte offset of the same
sentence MINUS its first word ('The'), leading space kept: 82360"), but it does **not** hold for the character
metric under the variant above. The number was never uniquely determined — it depends on the rule AND the metric,
and the preregistration, the r63 convention and the S351 row each made a different choice (S351 already carries two
numbers for one quote: `corpus/lessons/round-89-verifier-spotcheck.md:178` reads "present once (normalized offset
12,540; the lane's stripper reads 12,792)").

**The L1's landed anchor cell quotes NO offset** and keeps the unambiguous anchors (the section, capture lines
2873-2876 for the class-table row and 2878-2879 for the quoted paragraph, occurrence count 1, the 18-word count,
and the `LineBreak.txt` corroboration). **That is the right resolution and this seat recommends keeping it:**
the offset is not part of either claim's predicate, so the ambiguity falsifies no claim wording, and quoting no
offset removes it permanently.

**The quote itself is safe**, verified by this seat against the committed capture: whitespace-tolerant match True,
occurrence count **1**, **18 words**, contiguous in the raw HTML **False** (the markup splits it, so the quote is
only locatable in the stripped text).

## Draft 1 — the SOURCES row (S353)

Full draft, cell-by-cell justification, and the comparison against the uncommitted working-tree row: in
`.ufo/waves/round-90/w1/S90Scribe/draft-sources-row-S353.md`.

The row (11 cells, `corpus/SOURCES.md:34` schema `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`):

```
| S353 | Unicode Standard Annex #14, Line Breaking Properties, Unicode 18.0.0 rev 57, § NL: Next Line — https://www.unicode.org/reports/tr14/ (HTTP 200, 226166 bytes, sha256 296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0, capture census/round-90/srcs/tr14.html, page names Version "Unicode 18.0.0", Revision "tr14-57.html", Date 2026-09-01, opened 2026-11-08) | docs | A | the line-break class of U+0085 (scope: the NL class section and its class-table row only; the mandatory-break algorithm LB5 and every other class are out of scope here) | § NL: Next Line (Non-tailorable), the class table row `0085 / NEXT LINE (NEL)` at capture lines 2873-2879; tag-stripped offset 82360 of the capture: "The NL class acts like BK in all respects (there is a mandatory break after any NEL character)." (18 words) | the line-break class of U+0085 is NL and a break after a NEL character is mandatory, so a one-line record cell that leaves U+0085 to share a spelling with the raw byte 0x85 cannot do so: the character is not a byte and must carry its own `\uNNNN` spelling (the character path the r89 repair collided with, S351's `surrogateescape` decode, S348's `str.splitlines` boundary set) | mined | 2026-11-08 | 90d | corpus/knowledge/nel-byte-character-pair.md |
```

**Quote verification — the pasted command and its exact output.**

Command (from the lane root; read-only, writes nothing):

```
python3 -B /fast/scratch/hyaku/souji-r90/S90Scribe/verify_quote.py
```

Script (verbatim):

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

**Word count command** (the brief asks for the count to be produced by a pasted command): `words: 18` above is
`len(Q.split())` — **18 words**, inside the ≤25 limit.

**How the stripper rule was pinned** (the lane has no committed stripper, so I calibrated):

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

Output: `r63 stripped .txt reproduced byte-identically: True` (both files 65861 bytes). That r63 rule reads the S353
quote at **71402 / line 1803**; the rule that reads **82360** is the sibling variant (tags → EMPTY, no blank-line
collapse), which is the ONLY cell of the swept variant space that produces 82360 for this capture (the next
candidates are 82037, 82039, 82097, 82159, 82234, 82255, 82294, 82354, 82414, 82452, 82555, 82572, 82615).

**Capture-line facts** (`awk 'NR>=2870 && NR<=2881 {printf "%d: %s\n", NR, $0}' census/round-90/srcs/tr14.html`):
line 2870 = the `NL: Next Line (Non-tailorable)` heading; 2874 = `0085`; 2875 = `NEXT LINE (NEL)`; 2878-2879 = the
quoted sentence. `grep -n "^0085" census/round-90/srcs/LineBreak.txt` → line 95:
`0085           ; NL # Cc         <control-0085>`.

**Ownership note the L1 must read — the row is now LANDED, and this seat recommends keeping it.**
`corpus/SOURCES.md` at tip `fd25bfc5` carries the S353 row as an **uncommitted working-tree edit**
(`git diff corpus/SOURCES.md` shows one added line), and `corpus/knowledge/nel-byte-character-pair.md` exists as an
**untracked** file (66 lines). Both are outside this seat's write scope, so I did not touch either; my draft row is
a **comparison** for the L1, not an overwrite. The landed anchor cell now quotes **no offset** (the resolution
described above), keeps the class-table row at capture lines **2873-2876** and the quoted paragraph at
**2878-2879**, the occurrence count 1, the 18-word count and the `LineBreak.txt` corroboration. Cell-by-cell, the
two agree on id, source, kind, tier, scope, status, opened, used-by. They differ on:

| cell | uncommitted working-tree row | my draft | note |
|---|---|---|---|
| `teaches` | "U+0085 is a CHARACTER of line-break class NL with a mandatory break after it, so a one-line record cell must spell it distinctly from the raw byte 0x85: `\u0085` vs `\x85` (r90 C2 pair; S88Sentinel F1 and S351 own the decode side)" | "the line-break class of U+0085 is NL and a break after a NEL character is mandatory, so a one-line record cell that leaves U+0085 to share a spelling with the raw byte 0x85 cannot do so: the character is not a byte and must carry its own `\uNNNN` spelling (the character path the r89 repair collided with, S351's `surrogateescape` decode, S348's `str.splitlines` boundary set)" | both are sound; the landed one names the exact pair and the two source ids that own the decode side. **Optional improvement, not a defect:** add **S348** to the landed cell, since the entry's rule cites the `str.splitlines` boundary set as the reason U+0085 must be escaped at all |
| `anchor` | the landed cell: § NL: Next Line (Non-tailorable); class-table row at capture lines **2873-2876** and the quoted paragraph at **2878-2879**; occurrence count 1; **no offset**; the 18-word quote; the `LineBreak.txt` corroboration | mine quoted the offset 82360 and gave the class row as 2873-2879 | **keep the landed** — its line split (row 2873-2876 vs paragraph 2878-2879) is more precise than my single range, it names the `LineBreak.txt` corroboration (I verified that line myself: LineBreak.txt line 95), and its no-offset handling removes the ambiguity |
| `recheck` | `365d` | `90d` | the landed row says `365d` and the entry's own `recheck:` line says `365d` — consistent; `90d` is also a legal cadence (14 rows in the registry use it) but would disagree with the entry. **Keep `365d`** |
| `used-by` | `corpus/knowledge/nel-byte-character-pair.md` | same | the path must exist when the row lands or the census emits `E11 S353 missing used-by …` (the r89 scout reproduced exactly this for S351) |

**Recommendation to the L1: keep the landed S353 row and the landed entry as they are.** My row adds no new fact
over the landed one; the only cell this seat would still touch is `teaches` (adding the S348 pointer), and that is
a nicety, not a defect.

## Draft 2 — the knowledge entry

Full draft: `.ufo/waves/round-90/w1/S90Scribe/draft-knowledge-nel-byte-character-pair.md` (the entry block is
**exactly 35 lines**, at the lane's ~116-column wrap; `wc -l` on the extracted block → 35).

What it says, in the lane's schema (`#` title, `source:`, `verified-at:`, `recheck:`, the round line, `##` sections,
`## Gate`), citing **S353, S348, S351** as the brief requires:

- **The byte/character distinction** — a delegated child's stderr arrives as BYTES; `_decode_record` decodes with
  `surrogateescape` (S351), so an invalid byte 0x85 becomes the lone surrogate U+DC85 and `_escape_text` printed it
  `\x85`; a stderr carrying the CHARACTER U+0085 encodes it as the two valid UTF-8 bytes `\xc2\x85`, decodes to the
  real character, and the r89 rule's `o == 0x85` branch printed it `\x85` too — two materially different failures
  shared one cell.
- **Why the surrogate path and the character path collided** — the same `elif` chain served both: the character
  branch tested `o == 0x85` and the surrogate branch printed `o - 0xDC00`; both landed on the spelling `\x85`.
- **The `\u0085` spelling** — the character now takes `\u0085`; the raw byte keeps `\x85`.
- **The pair rule** — raw bytes that are not valid UTF-8: `\xNN` with the original byte value; characters whose
  code point is a documented `str.splitlines()` boundary above 0x7F (U+0085, U+2028, U+2029): `\uNNNN`; a literal
  backslash sequence keeps its backslash doubled.
- **The Gate block** — URL `https://www.unicode.org/reports/tr14/`, opened **2026-11-08** (HTTP 200, 226166 bytes,
  sha256 `296df533…acc7c0`), and the located quote (≤25 words): *"The NL class acts like BK in all respects (there
  is a mandatory break after any NEL character)."* — § NL: Next Line, tag-stripped offset 82360, occurrence count 1.
- Plus the Boundary section: one tool's rule for one cell, no universal injectivity claimed, `_escape_record`
  unchanged, `_one_line` deleted.

**Each claim re-measured on committed bytes** (full table in the draft):

| claim | measurement | result |
|---|---|---|
| the byte and the character used to collide | `census/round-90/controls/c2-before-tool.py` (the r89 bytes), `_escape_text`: `elif o < 0x20 or o == 0x7F or o == 0x85: out.append("\\x%02x" % o)` | the r89 rule maps BOTH to `\x85` |
| the filed tool separates them | `tools/souji-record-agreement.py` sha256 `d095b52f…8561`: `elif o in (0x85, 0x2028, 0x2029): … out.append("\\u%04x" % o)` and the surrogate arm `0xDC80 <= o <= 0xDCFF → "\\x%02x" % (o - 0xDC00)` | the character takes `\u0085`; the byte keeps `\x85` |
| the pair is MEASURED | `python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-90/controls/c2-before-tool.py --work <empty>` | `SUMMARY cases=12 tool_pass=12 before_pass=10`, EXIT 0 |
| `_one_line` is gone | `grep -c 'def _one_line(' tools/souji-record-agreement.py` → **0**; the only surviving hits are `_one_line_bytes` (the live helper) and a docstring naming the deleted one | dead code deleted, no caller |

**My C2 re-run (the frozen command, on the committed bytes), verbatim:**

```
# tool path=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py sha256=d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561
# before path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-90/controls/c2-before-tool.py sha256=f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd
# fixture sha256=d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa
CASE KFF1 tool=pass before=pass
CASE KFF2 tool=pass before=pass
CASE KFF3 tool=pass before=pass
CASE KFF4 tool=pass before=pass
CASE KFF5 tool=pass before=pass
CASE KFC1 tool=pass before=pass
CASE KFC2 tool=pass before=pass
CASE KFF6 tool=pass before=pass
CASE KFF7 tool=pass before=pass
CASE KFF8 tool=pass before=pass
CASE KFF9 tool=pass before=fail
CASE KFF10 tool=pass before=fail
SUMMARY cases=12 tool_pass=12 before_pass=10
EXIT=0
```

**The before-arm control, re-run by this seat** (the r89 bytes as BOTH arms — the prereg's do-nothing control):

```
python3 -B tests/fixtures/r90-k4-flagfail.py --tool census/round-90/controls/c2-before-tool.py --before census/round-90/controls/c2-before-tool.py --work <empty>
```

→ `SUMMARY cases=12 tool_pass=10 before_pass=10`, `R90-FIXTURE-FAIL: the tool under test does not pass every case`,
**EXIT=1** (KFF9 and KFF10 fail on both arms). This matches the committed pre-freeze receipt
`census/round-90/records/prefreeze-c2-control.txt` cell for cell. **The control cannot reach `tool_pass=12`** — so
this is **not** a no-work control that passes the target, and it is not a HIGH finding of that kind.

**Size note for the L1:** the landed entry (untracked) is **66 lines**; my draft is **35** (the brief's bound).
The landed version carries two things mine does not: the `LineBreak.txt` corroboration inside the Gate bullet, and
the S87Sentinel F4 citation for the U+2028/U+2029 precedent. **Recommendation: keep the landed entry** (it is the
L1's own file and it is richer), and treat the ≤35-line bound as the brief's guidance for a NEW draft rather than a
hard gate on the L1's richer entry — I am flagging the 66 vs 35 difference rather than silently rewriting the L1's
file. My 35-line version is on file as the fallback if the L1 wants the bound honoured verbatim.

**One thing the L1's landed entry should not carry over from my draft:** nothing. My draft cites the offset 82360
in two places (the `verified-at:` line and the Gate bullet). **Given the offset ambiguity documented above, the
landed entry's handling — which quotes the capture sha/bytes, the section, the capture lines, the occurrence count
and the word count — is the safer form**, and my draft's offset mentions should NOT be pasted over it.

## Draft 3 — the Q165 criterion

Full draft: `.ufo/waves/round-90/w1/S90Scribe/draft-quality-Q165.md`.

- **Numbering:** the next free id is **Q165** — `grep -o '^| Q1[0-9][0-9] ' corpus/QUALITY.md | sort -u | tail -5`
  reads `Q160 Q161 Q162 Q163 Q164`; `grep -c "Q165" corpus/QUALITY.md` reads **0**.
- **Section:** a NEW `## Round 90 criteria` section appended after `## Round 89 criteria` (which ends at line 410;
  the file is 410 lines), with the lane's 5-column header `| id | criterion | applies-to | test | lesson |`.
- **The criterion** (draft text): *Extends Q164 and Q163 (they stand), and adds the clause A1 of the r90 round
  exposed: a record cell's escaping rule is only injective on a byte/character pair if the MEASUREMENT can separate
  the character from its own escaped literal.* The two paths must reach the cell separately and carry distinct
  spellings (a byte that was not valid UTF-8 arrives as U+DC80-U+DCFF and takes `\xNN` with its ORIGINAL byte
  value; the character that DECODES to those bytes takes `\uNNNN`); **the pair is MEASURED, not asserted — and the
  measurement must DISCRIMINATE**: a bare substring count does not, because the escaped literal `\u0085` CONTAINS
  the substring `\u0085`, so a mutant that doubles the U+0085 branch's backslash passes the r90 fixture 12/12
  (S90Sentinel H1). A population therefore binds the pair only when it also asserts the ABSENCE of the doubled
  spelling and asserts the two cells DIFFER, and when the "one physical line" clause is enforced on the CELL rather
  than on the row count. The injectivity evidence is a direct comparison of the two rendered cells
  (`_escape_text("\u0085")` = `\u0085` vs `_escape_text("\udc85")` = `\x85`), not the count. Stated limits: the
  enumerated pair only (not the whole cell — a stderr differing only inside the elided middle still renders
  identically, and a raw window cut INSIDE the two-byte encoding of U+0085 renders the surviving byte `\x85`);
  `_escape_record` unchanged and byte-based; the dead escape-first `_one_line` is measured by grep and load, NOT by
  the fixture; no universal injectivity claimed.
- The applies-to column: every lane tool that writes a record cell whose escaping rule can receive both an
  undecodable byte and the character that decodes to the same bytes; every escaping rule with a `\xNN` arm; every
  population that claims to bind such a pair. The test column: the frozen C2 command and its target `cases=12
  tool_pass=12 before_pass=10`, the before-both-arms control `tool_pass=10 before_pass=10` EXIT 1, **and the
  explicit statement that this pair is NOT by itself sufficient evidence of injectivity** (the doubled-backslash
  mutant passes it 12/12), with the direct cell comparison named as the evidence that does certify it.
- The lesson pointer is a **file** pointer (`corpus/lessons/round-90.md`), matching the Q163/Q164 convention
  (`corpus/lessons/round-88.md`, `corpus/lessons/round-89.md`), with the knowledge entry and the plan amendments
  cited alongside it because they carry the measurement. **This is what the L1 landed** (verified cell by cell
  against `corpus/QUALITY.md:416`).

**This draft was rewritten after the L1 landed `plans/round-90.md` A1, A4 and A5(c).** My first version of Q165
said the fixture "certifies" the pair — that is exactly what A1 falsifies, so the first version is superseded and
must NOT be used. The rewrite is in `draft-quality-Q165.md`; every clause is traced to a named ground there (the
filed tool's two arms; A1's H1 mutant; A1's routed conjuncts; A4's one-physical-line gap; A4's raw-window
boundary; A5(c)'s dead-code clause; the r89 lesson's "Routed to round 90"; and the two arms' measured outputs).

**LANDED.** The L1 landed the rewritten draft verbatim while this seat was finalising: `## Round 90 criteria` at
`corpus/QUALITY.md:412`, the Q165 row at `:416` (5 columns, `| Q165 | … | applies-to | test | lesson |`, with the
lesson cell `corpus/lessons/round-90.md; corpus/knowledge/nel-byte-character-pair.md; plans/round-90.md A1 and A4;
S353, S348, S351`). **All four deliverables are now landed by the L1** — the S353 row, the knowledge entry, the
`## Mistakes` M1 and the Q165 criterion.

## Draft 4 — the `## Mistakes` row — THE L1 HAS LANDED AN M1 FOR THIS DEFECT

Full draft and comparison: `.ufo/waves/round-90/w1/S90Scribe/draft-lesson-mistakes.md`.

**Status.** The L1 landed `corpus/lessons/round-90.md` with its own **M1** covering exactly this defect, while this
seat was drafting. **My recommendation: keep the landed M1 — it is more accurate than my draft on three of the four
cells.** The cell-by-cell comparison is in the draft file; the three places where the landed row beats my draft:

1. **The six-file count.** The landed row cites `git ls-tree -r 4864129b -- .ufo/waves/round-89` listing **six**
   files. I measured that: `git ls-tree -r --name-only 4864129b -- .ufo/waves/round-89` → 6 files, and `claims.json`
   was added LATER, at `c2ee31ae` (7 files at the closure tip `1786b552`). **My draft listed seven files under the
   `4864129b` citation — a seven-for-six slip of my own, which the landed row gets right.**
2. **The fix is jj-colocated.** The landed row names `jj-lane.sh` and `jj file track --include-ignored`; my draft
   said `git add -f`. The lane is jj-colocated (`scripts/hyaku/jj-lane.sh` is the only writer), so `git add -f`
   names a command the lane does not use. I checked the landed fix's route and it is sound:
   `scripts/hyaku/jj-lane.sh:654-658` carries `--include-ignored` on its `file track` call, and `.ufo/waves/…` is
   NOT on the helper's never-committable list (`.ufo`, `.ufo/state`, `.ufo/state/*`, `.ufo/watchdog.log` —
   `jj-lane.sh:513`).
3. **The `captured-by` rule is sharper.** The landed row states the rule ("it passed on the local tree and failed on
   the pushed bytes, **which is the only place it counts**"); my draft stated it only implicitly.

**What my draft adds that the landed row lacks: the exact reproduction** — the commands and their verbatim outputs,
including the fresh-clone run on the pushed bytes (below). If the L1 wants the reproducer in the lesson, that
section is paste-ready in `draft-lesson-mistakes.md`; if not, this report carries it either way.

**This seat's draft row** (5-column table `| # | class | evidence pointer | captured-by | fix |`, copied from the
r89 file's own `## Mistakes` table at `corpus/lessons/round-89.md:57-65`) — **superseded by the L1's landed M1**;
kept here because it is the source of the reproducer below:

- **class:** wave evidence left gitignored — the round's 12 seat reports and their receipts were never committed,
  so the pushed tip could not resolve the pre-file ledger's artifacts; the ledger itself is committed and complete,
  but every path it names is absent from the tree, and the landed-changes row claimed "wave evidence (12 seat
  reports + receipts + results)" for a commit whose tree contains none of them.
- **evidence pointer:** `corpus/lessons/round-89-verifier-spotcheck.md` §1 ("Wave-evidence durability: DEFECT
  (major, status-neutral)") and §7 item 1; `.gitignore:1` is `.ufo/waves/`; `git ls-tree -r --name-only 4864129b
  -- .ufo/waves/round-89` lists only the 7 top-level files; `git check-ignore -v .ufo/waves/round-89/w1/
  S89Connector.md` reports the ignore; r86/r87/r88 force-added their wave files (209/280/125 files), so r89 is a
  regression.
- **captured-by:** the pre-file gate's **artifact-existence check** — `scripts/hyaku/prefile-falsification.py`,
  `resolve_artifact` → the `artifact-missing` finding. On the local working tree the gate reads
  `PREFILE-FALSIFICATION: pass claims=2 rows=13 attack_seats=7 findings=0`, EXIT 0; on the pushed bytes it reads
  `PREFILE-FALSIFICATION: FAIL claims=2 rows=13 attack_seats=7 findings=13`, EXIT 1, all 13 rows `artifact-missing`.
- **fix:** commit the wave evidence — `git add -f` the round's seat reports and receipts under
  `.ufo/waves/round-<N>/w1/` (or un-ignore that path in the lane's own `.gitignore`), so the ledger's artifacts
  resolve from the pushed lane and not only from the local working tree; and stop writing "N seat reports" in a
  commit message whose tree does not contain them.

**The defect reproduced by this seat (so the row is a reproducer, not an opinion).** All read-only git; the clone is
a scratch fixture under `/fast/scratch/hyaku/souji-r90/S90Scribe/clone/`.

1. `ls .ufo/waves/round-89/w1/*.md | wc -l` → **12** (on disk); `git ls-files .ufo/waves/round-89/w1/ | wc -l` →
   **0** (none tracked); `git check-ignore -v .ufo/waves/round-89/w1/S89MutCounter.md` →
   `.gitignore:1:.ufo/waves/	.uufo/waves/round-89/w1/S89MutCounter.md`.
2. Local gate: `PREFILE-FALSIFICATION: pass claims=2 rows=13 attack_seats=7 findings=0`, EXIT 0.
3. Fresh clone at the r89 closure tip `1786b552`, gate against it:
   `PREFILE-FALSIFICATION: FAIL claims=2 rows=13 attack_seats=7 findings=13`, EXIT 1 — 13 `artifact-missing` rows
   (`.ufo/waves/round-89/w1/S89MutCounter.md`, `S89Sentinel.md`, `S89Reviewer.md`, `S89Simplifier.md`, `S89ExecC2.md`,
   `S89Critic.md`, `S89Scribe.md`, `S89Reviewer.md`, `S89Critic.md`, `S89Sentinel.md`, `S89Labrat.md`, `S89Connector.md`,
   `S89Distiller.md`).
4. `git ls-tree -r --name-only 1786b552 -- .ufo/waves/round-89` → only the 7 top-level files; the clone has no
   `.ufo/waves/round-89/w1/` directory at all.

**The same defect is LIVE in r90 — the L1 must act on this.** At tip `fd25bfc5`:
`ls .ufo/waves/round-90/w1/*.md | wc -l` → **12** (on disk); `git ls-files .ufo/waves/round-90/w1/ | wc -l` → **0**;
`git check-ignore -v .ufo/waves/round-90/w1/S90Scribe.md` → `.gitignore:1:.ufo/waves/	.ufo/waves/round-90/w1/S90Scribe.md`.
`.ufo/waves/round-90/` currently has exactly ONE tracked file (`git ls-files .ufo/waves/round-90` →
`.ufo/waves/round-90/build-spec.py`). **If r90 lands the way r89 landed, r90's pre-file gate will pass locally and
fail on the pushed bytes.** This seat's own report file is inside the ignored path and is therefore not durable
until the L1 force-adds it. The lane already owns the receipt-style route:
`tools/souji-wave-evidence-capture.sh <lane-abs> <round-N>` copies the wave tree into `census/round-<N>/waves/`
with a `manifest.sha256` and re-verifies it (used for rounds 26-45 and 66); rounds 86/87/88 used the `git add -f`
route.

**Is this a HIGH finding (a no-work control that passes the target)? — NO, and the row says so.**
- The round's own control **FAILED** on the pushed bytes (`findings=13`, EXIT 1) — the defect is caught and named.
- The local pass is **not** a no-work control reaching the target: it runs against the working tree, where the files
  DO exist; it proves the ledger is complete and the artifacts are present **on this host**, and nothing about the
  pushed bytes. The lane's own closing judge already drew exactly this distinction ("the same gate fails for
  durability, not for wording", spot-check §2).
- No claim wording is falsified: the ledger's rows are real, the claim verdicts are unchanged ("The defect is named
  and routed; it does not change the claim verdicts"). It is a **durability** defect in the round's bookkeeping —
  which is why it belongs in `## Mistakes` and not in the round's narrowing amendments.

## C1 — the frozen battery, re-run by this seat on the committed bytes

The frozen command, from the lane root:

```
S=/fast/scratch/hyaku/souji-r90/S90Scribe
python3 -B census/round-90/c1-clause-battery.py \
  --counter census/round-87/c1-pointer-counter.py \
  --work "$S/c1work" --only r89,r90 --expect-killed 31
```

Result: **the preregistration's target is met on the committed bytes** — 770.06 s wall. Verbatim tail:

```
MUTANT-PAIR m17b-target-keyed pop=r89 killed=yes mismatches=1 errors=0 exit=1 | pop=r90 killed=yes mismatches=1 errors=0 exit=1
MUTANT m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
MUTANT m17c-no-malformed pop=r90 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0 | pop=r90 killed=yes mismatches=1 errors=0 exit=1
MUTANT m18d-first-only pop=r89 killed=yes mismatches=1 errors=0 exit=1
MUTANT m18d-first-only pop=r90 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m18d-first-only pop=r89 killed=yes mismatches=1 errors=0 exit=1 | pop=r90 killed=yes mismatches=1 errors=0 exit=1
SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31
EXIT=0
```

Both pristine arms green, `killed_r89=15` / `killed_r90=16` / `killed_total=31`, **EXIT 0** — the frozen C1 target.
The load-bearing row behaves exactly as the preregistration's MECHANISM paragraph predicts: the sole survivor
`m17c-no-malformed` is **alive on r89** (`killed=no`) and **killed on r90** by the LD2b row, and the pristine r90
arm stays green (58 rows, 0 mismatches, 0 errors).

**This is not a no-work control that passes the target.** The prereg's own DO-NOTHING CONTROL — the SAME battery,
SAME mutants, the r89 57-row population alone — reads `killed_r89=15` with `m17c-no-malformed pop=r89 killed=no`,
EXIT 0 (committed receipt `census/round-90/records/prefreeze-c1-control.txt`), so the 16/16 and the 31 are
reached only by the delta, which is the row LD2b and nothing else. The frozen C1 wording is therefore **not
falsified** by this wave's own artifacts; this seat measured no artifact that contradicts it.

**Scope note:** this is a re-measurement on the committed bytes, not a landing of the receipt — the L1 owns the
commit, the report and the lane hash for each receipt. The prereg requires the after arms to be re-run after F;
this run was made at tip `fd25bfc5` (F) on the committed instrument bytes, which is what the prereg's "the after
receipts are measured on the COMMITTED tool bytes and the COMMITTED instruments" asks for.

**Instrument pins re-measured from the committed bytes** (`sha256sum …`), every one matching the preregistration
verbatim:

| instrument | sha256 (committed bytes) | prereg pin |
|---|---|---|
| `census/round-87/c1-pointer-counter.py` (counter, unchanged from r87) | `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b` | `fd0a8e24…` ✓ |
| `census/round-90/c1-false-row-harness.py` | `c3664747ffe712fde8f61c34562df2f0e92f2a0378b151bd0b4d74e91d629cbe` | `c3664747…` ✓ |
| `census/round-90/c1-clause-battery.py` | `e7265335e4458e68d2277dd0ad4f36e68999a7ba70363d60dc2155bd9cfa2d39` | `e7265335…` ✓ |
| `census/round-90/c1-mutants.json` (the r89 sixteen, byte-identical) | `392522489bc6f22a9747f64d311dbde7528dd0e8b481159db15d3eb038066dd5` | `39252248…` ✓ |
| `census/round-90/c1-false-rows.tsv` (58 rows = the r89 57 + LD2b) | `d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45` | `d64d7695…` ✓ |

(The r87 counter's digest is the same one the r89 spot-check re-derived as "byte-identical at r87 `77ccef7c`", so
the counter is unchanged across r87→r89→r90 as the prereg's STATED LIMIT (i) claims.)

## What I could NOT check

1. ~~**C1's after-arm.**~~ **DONE — see the section above.** The frozen battery was run to completion by this
   seat and reads `killed_total=31`, EXIT 0. What remains the L1's is landing the receipt and citing the landed
   lane hash; the L1 must also re-run it if any instrument changes before the commit.
2. **The live re-fetch of `https://www.unicode.org/reports/tr14/`.** No network call was made; the capture's digest,
   byte count and version stamps come from the committed bytes. The r89 scout re-opened its own row against the live
   page and found it byte-identical; I did not repeat that for S353.
3. **Whether the L1 wants the stripper/offset divergence (the one substantive finding above) resolved by amendment.**
   That is the L1's call, and the preregistration's offset is frozen.
4. **Whether the L1 prefers my 35-line entry or the untracked 61-line working-tree entry, and my S353 row or the
   uncommitted working-tree row.** Both comparisons are cell-by-cell in the draft files.
5. **The census's verdict on the landed registry** (`scripts/sources-census.sh validate`) — this seat did not edit
   `corpus/SOURCES.md`, so running it now would measure the L1's working tree, not this seat's row. The L1 must run
   it after landing (watch `E11 S353 missing used-by` if the entry is not landed with the row).
6. **The other ten defects the r89 spot-check routed** (report accuracy, the capability-table row, the SCORECARD
   order, the trend token, …) — outside this seat's brief.
7. ~~**`corpus/lessons/round-90.md` does not exist yet.**~~ **RESOLVED — the L1 has landed it** (67 lines, with
   M1-M3 in `## Mistakes`). My draft block is now a comparison, and the recommendation is to keep the L1's landed
   M1. See "Draft 4" above.
8. **The L1's landed A1/A4/A5 narrowing, and what it means for this seat's drafts.** The L1's `plans/round-90.md`
   A1 records that the r90 fixture's kill rule does **not** certify the word "injective" (a mutant that doubles the
   U+0085 branch's backslash passes it 12/12), A4 records that the "one physical line" clause is not enforced and
   that a raw window cut inside U+0085's own encoding renders the surviving byte `\x85`, and A5(c) records that the
   fixture does not bind the dead-code half. **My Q165 draft was rewritten to match** — the criterion now requires a
   measurement that DISCRIMINATES (asserting the absence of the doubled spelling, and a direct comparison of the two
   rendered cells) rather than asserting that the fixture certifies injectivity. **This seat added no narrowing
   amendment of its own:** the L1's A1-A5 already cover the falsifications this wave produced, and Amendment 59
   forbids widening the frozen wording — it only requires that a falsification be recorded, which the L1 has done.

## Scratch, disclosed

All scratch under `/fast/scratch/hyaku/souji-r90/S90Scribe/`: `verify_quote.py` (the quote verifier), `c1work/`
(the C1 battery's `--work` dir), `c2work/` and `c2before/` (the two C2 fixture `--work` dirs), `clone/` (the
r89-pushed-bytes clone + its synthetic fleet root, used to reproduce the durability defect), `entry-body.md` /
`entry-final.md` / `cand*.md` (the entry-length iterations) and `clone/fleet/` (the synthetic fleet root the gate
was pointed at). **The scratch dir is deleted before this seat yields** (`rm -rf /fast/scratch/hyaku/souji-r90/S90Scribe`),
with the receipts copied into this seat dir first — `verify_quote.py` is preserved at
`.ufo/waves/round-90/w1/S90Scribe/verify_quote.py`, and every command + its exact output is pasted in this report
and in the four draft files.

**Nothing was left outside the two permitted paths:** no file outside
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-90/w1/S90Scribe/` and this report file was created
or modified in the lane; nothing in the fleet root, no sibling lane, no `MANIFEST.json`, `.ufo/state/*`, `.scratch/*`
or `.ufo/watchdog.log`.
