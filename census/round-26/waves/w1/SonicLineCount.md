# SonicLineCount — mechanical checks at 89e0fce (round 26, w1)

## Status
STATUS: PASS — all four assigned mechanical checks re-derived at lane commit
89e0fceeefcf28db313c94120be6d25e03c60094; (a) 254 as expected, (b) byte range
established, (c) 5, (d) 4 H3 headings. One boundary note recorded (F1): the
assigned end line 229 stops at the `---` separator; preregistration amendment 2
deletes through blank line 230 (one byte further, strict superset).

## Evidence

Revision: `89e0fceeefcf28db313c94120be6d25e03c60094` (verified by
`git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 89e0fce` →
`89e0fceeefcf28db313c94120be6d25e03c60094`). Blob size
`git cat-file -s 89e0fce:SCORECARD.md` → `42296`.

### (a) line count
```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show 89e0fceeefcf28db313c94120be6d25e03c60094:SCORECARD.md | wc -l
254
```
Byte cross-check (same bytes written to /var/tmp): `LC_ALL=C awk` cumulative
length sum = `42296`, i.e. `wc -c` == `git cat-file -s`, file is newline-
terminated, 254 newlines.

### (b) byte offset range of base lines 170-229
Method: `git show 89e0fce:SCORECARD.md > $D/SCORECARD.md`;
`LC_ALL=C awk 'BEGIN{s=0}{if(NR==170){printf "start_line170_0based=%d\n", s} s+=length($0)+1; if(NR==229){printf "end_line229_excl=%d\n", s}} END{printf "file_total_bytes=%d\n", s}'`
```
start_line170_0based=26465
end_line229_excl=37992
file_total_bytes=42296
```
Cross-check with byte offsets reported by grep (`LC_ALL=C grep -bn`):
```
172:26467:Insert the table below directly above `### Round 23 measurements` (newest first, matching the file's order). Leave the Axes table scores unchanged: no score move is claimed (see Findings 6).
229:37988:---
231:37993:### Round 25 measurements (2026-10-25; base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe)
174:26659:```markdown
208:33420:```
212:33524:```markdown
215:35318:```
224:35806:```markdown
227:37983:```
```
First bytes at 26465 (`dd ... | cat -A`) → two blank lines then the instruction:
```
$
$
Insert the table below directly above `### Round 23 measurements` (newest first, matching the file's order). Leave the
```
Last bytes ending at 37992 (`dd skip=$((37992-24)) count=24 | od -c`):
```
0000000   l   d   s       u   n   c   h   a   n   g   e   d   .  \n   `
0000020   `   `  \n  \n   -   -   -  \n
```

**Exact range, base lines 170-229 (inclusive):**
- 0-based byte offsets `26465 .. 37991` (first byte of line 170 through last
  byte of line 229) — half-open `[26465, 37992)`.
- Length `11527` bytes, `60` newlines (`dd ... | wc -l` → `60`).
- sha256 of that span:
  `de7b2cbbfc6f83a75cf1e2e37060c0fdc1571d53cd823b3112fb52be22578840`.

Variants (for the integrator; both measured on the same bytes):
| definition | span | bytes | sha256 |
|---|---|---|---|
| 170-229 as assigned (incl. 2 blank lines 170-171 + `---` 229) | `[26465, 37992)` | 11527 | `de7b2cbb…8840` |
| 172-229, scaffold content only (instruction → `---`) | `[26467, 37992)` | 11525 | `42365fc6…a636` |
| 170-230, amendment 2 delete range (adds blank line 230) | `[26465, 37993)` | 11528 | `8a4dcdb6…e52` |

Line layout of the span (base):
- 168 blank, 169 `None.` (end of `## Retired`), 170 blank, 171 blank
- 172 instruction line ("Insert the table below…")
- 173 blank; 174 ` ```markdown `; 175 `### Round 24 measurements …` … 208 ` ``` `
- 209 blank; 210 "Capabilities rows (append at the end of `## Capabilities`,
  after `record agreement audit (r23)`):"; 211 blank; 212 ` ```markdown ` … 215 ` ``` `
- 216 blank; 217-220 "Optional same-landing correction …" paragraph; 221 blank
- 222 "Planned (append after the existing …)"; 223 blank; 224 ` ```markdown `;
  225 r24 bullet; 226 r25 bullet; 227 ` ``` `; 228 blank; 229 `---`
- 230 blank, 231 `### Round 25 measurements …`

Hexdump of the boundary lines (`sed -n '169p;170p;171p;229p;230p' | od -c`):
```
0000000   N   o   n   e   .  \n  \n  \n   -   -   -  \n  \n
```

### (c) superseded-by count
```
$ grep -c 'superseded by SCORECARD' < (git show 89e0fceeefcf28db313c94120be6d25e03c60094:SCORECARD.md)
5
```
Matching line numbers (`grep -n`, same blob) → `250, 251, 252, 253, 254`.
All five are `superseded by SCORECARD.md:<line>; …` (the `.md` suffix does not
affect the pattern).

### (d) every `### ` heading, line numbers at 89e0fce
`LC_ALL=C grep -bn '^### '`:
```
17:### Round 23 measurements (2026-10-25, lane base 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd)
175:### Round 24 measurements (2026-10-25, lane base a65fac98964b445758e94c805728c9a19d302ff8)
231:### Round 25 measurements (2026-10-25; base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe)
241:### Round 25 append-only corrections
```
Exactly 4 ATX H3 headings. The broad pattern `### ` also matches two
*non-heading* occurrences inside body text — line 172 (`…above \`### Round 23
measurements\`…`) and line 226 (a planned bullet quoting `### Frontier (r24)`) —
they are not lines beginning with `### ` and are excluded above.

## Findings

1. **Span boundary is `[26465, 37992)` and ends on the `---` separator, not on
   the blank line before the next heading.** Base line 229 is `---`; line 230 is
   a single empty line before `### Round 25 measurements` (231). The assigned
   span (170-229) and preregistration-amendment-2's delete range ("base lines
   170-230") differ by exactly that one byte: `[26465,37992)` vs
   `[26465,37993)`. No conflict — amendment 2 is a strict superset by 1 byte
   (`0x0a`) — but an exec deleting only 170-229 leaves a *stray blank line*
   where the `---` separator was, directly under `None.`; deleting through 230
   leaves `None.` immediately followed by the next heading. Neither K1 nor K2
   discriminates on that blank, so the executor must decide from amendment 2's
   numbered layout (item 7 ends at base 138-169, i.e. `None.` is the last
   protected line) and keep exactly one `0x0a` after `None.` before the next
   block. Location: SCORECARD.md base lines 169-171 and 229-231.

2. **Byte offsets must be computed in the C locale.** A first pass using
   `awk length($0)` under the UTF-8 locale returned `26380 / 37871`
   (`len=11491`) — 129 bytes short, exactly the file's multibyte surplus
   (42296 bytes vs 42167 characters; the file contains `—`, `§`, `→`). Any
   executor or verifier slicing this file by character offsets would cut
   mid-line at `…ed r13 sites`. `LC_ALL=C` (as in all commands above) and
   `grep -b` agree: 26465 / 37992. Location: SCORECARD.md, whole file.

3. **The Round 24 block sits entirely inside a fence.** Fence markers are
   174/208, 212/215, 224/227; the only `### Round 24 measurements` heading
   (line 175) is between 174 and 208, i.e. inside the first fenced block, and
   the payload bullets 225-226 are inside the third. This is the defect C1
   fixes; the K2 triple target `17 175 231` is confirmed by (d) and the base
   ordering is `17, 175, 231` — not newest-first. Location: lines 174-229.

4. **K2's regex does not pick up line 241.** `^### Round (23|24|25) measurements`
   matches exactly 17/175/231; `### Round 25 append-only corrections` (241) is
   out of scope of the counter, so the "exactly three headings" clause is
   satisfied by the base bytes and cannot be gamed by the corrections heading.
   Location: line 241 vs the K2 command in preregistration.txt.

## Attack log
Not an attack seat (mechanical census assignments only). Two observations
offered as potential gaming vectors, no predicate change proposed:

- A1: the (c) count `5` is matched by any line containing the bare phrase; the
  five are bare (non-list) lines 250-254 appended by r25. A future edit could
  inflate the count by quoting the phrase in the new Round 24 block or in a
  finding — the counter has no anchor. Location: SCORECARD.md 250-254.
- A2: the (b)/(d) line numbers are position literals; after C1 integration the
  protected spans move by construction (amendment 2 already reinterprets them
  as byte-content spans). Any receipt that pins `17/175/231` as post-edit
  evidence would be self-contradictory — the post-edit K2 triple must be a
  *different* ordered triple (n25 < n24 < n23). Location: preregistration.txt
  C1 K2.

## Scope / hygiene
- READ-ONLY seat: the only file written under the lane is this report. No
  `git add/commit/push/stash/checkout/reset`, no `jj`, no signals, nothing
  touched in `/home/vgpnk/Projects/shokunin` outside `souji-shokunin/`, nothing
  read from `.scratch/`, `.ufo/state/`, `MANIFEST.json`, or `/home/vgpnk/Projects/shokuknow`.
- Scratch `/var/tmp/souji-r26-SonicLineCount/` (one file, `SCORECARD.md`, 42296
  bytes) removed at end of run.
- Tools installed/upgraded: none (all commands are coreutils/git already
  present). No pacman transaction attempted.
- Unrun checks: none claimed; every number above is pasted from a command
  executed this run.
