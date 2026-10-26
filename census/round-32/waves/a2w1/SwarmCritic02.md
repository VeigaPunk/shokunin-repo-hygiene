# SwarmCritic02 — C1 landed rows N06–N11 (round 32, attempt 2, wave a2w1)

## Status

STATUS: PASS — six of six landed rows at `9e8982b7a6ac57dffa415f9db43cf7cd6e829c93` are HONEST: each of the five `field:` integers re-derives exactly from the cell's own cited r21 record, and the `withdrawn:` reason is true under the frozen rules (no admissible observable exists; the value is nevertheless measured, see F3). No row needs correction. Two non-blocking notes (F4, F5) and one counter gap reproduced (F6).

## Evidence

Scratch: `/fast/scratch/hyaku/souji-r32/AuditC1N06N11/` (clone of the lane, `origin` removed, detached at the C1 landing commit `9e8982b7a6ac57dffa415f9db43cf7cd6e829c93`; second clone at base `85b61a151923986e7e6b48f7084b9122561b5f3d` for counter probes). Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`, item list `3ec84fc81b3243429c834a051880b0bcde06291c`, lane tip at audit time `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`. All lane Python ran as `python3 -B`.

### E1 — frozen counter v2 over the six items (required invocation)

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c1-counter-v2.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 \
  --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
  --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
  --only N06,N07,N08,N09,N10,N11 --scratch /fast/scratch/hyaku/souji-r32/AuditC1N06N11/cnt
```

```
ITEM	N06	SCORECARD.md:159	literal=oracle2372 keys	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.labelled=2372
ITEM	N07	SCORECARD.md:159	literal=files 192	binding=field	MATCH	census/round-21/oracle-acceptance.json files=192
ITEM	N08	SCORECARD.md:159	literal=tp 3	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.tp=3
ITEM	N09	SCORECARD.md:159	literal=fp 0	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.fp=0
ITEM	N10	SCORECARD.md:159	literal=fn 0	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.fn=0
ITEM	N11	SCORECARD.md:159	literal=401 tuples	binding=withdrawn	WITHDRAWN	No observable in the cited census/round-21/oracle-acceptance.json holds 401 as a JSON integer; the 401 old tuples survive only as the length of the prior_verdicts list plus a sha256 digest, while the text record that prints count=401 is oracle-acceptance.txt, a basename the base line does not cite.
SUMMARY items=6 bound_run=0 bound_record=0 bound_field=5 withdrawn=1 unbound=0 mismatches=0 partial=1 rev=9e8982b7a6ac57dffa415f9db43cf7cd6e829c93
```

exit 0. The v1 counter (`census/round-32/c1-counter.py`, same arguments) prints the same six ITEM lines and the same SUMMARY, exit 0 — the six rows hold under both counters.

### E2 — independent re-derivation of all five integers from pinned r21 blobs

Blobs extracted at `4eb2fda51c9917abd734c7e411f98cbb59c5c0fe` (`census/round-21/count-read-root.py` = `62e9cf31c9fb70d267e4e27c216cbdeb6aec73c2`, `tools/souji-seat-audit.py` = `6cf3a85b01b6ca883a1e6ea226cdec65278da0f4`), run against the clone's `census/round-20/transcripts/{final,recovery,recovery-final}` and `census/round-21/read-root-oracle.tsv` (both unchanged from `4eb2fda` to the landing commit; `git diff --stat 4eb2fda 9e8982b -- census/round-20/transcripts` empty):

```
PRIOR-VERDICTS	count=401	sha256=4fa1fadcd8db4cd236086dcbadf23c697a7a5a1a88ee785049e4e6c7843c8273
ORACLE	tp=3	fp=0	fn=0	labelled=2372	missing=0	extra=0
CLASS	V-READ-ROOT	3
SUMMARY	files=192	calls=3539	read_root=3
```

exit 0. Every field the five rows bind is reproduced byte-for-byte by the committed r21 script over the committed r21 inputs. This closes the wave-1 delivery's own stated limit ("do not re-run `count-read-root.py`").

### E3 — the cited record is that run's output, not spliced

`census/round-21/oracle-acceptance.json` is `8c03a568052172e6aadb413b596aea9063b87db9` at `4eb2fda`, at the base and at the landing commit (single writer: `git log -- census/round-21/oracle-acceptance.json` names `4eb2fda` only). Hash of every `inputs` entry against committed bytes at `9e8982b`: 194 entries, 193 match, 1 mismatch — `tools/souji-seat-audit.py`, whose recorded hash `e1298b9348f42406af59be885dcfac146c8939c8d389fd2109532b9fe397687c` equals `sha256(cat-file blob 4eb2fda:tools/souji-seat-audit.py)`; the tool blob changed after r21 (`a9cd8598…` at the landing commit), so the record is the r21 run against the r21 tool.

### E4 — append-only and survival at the lane tip

`git diff 85b61a1 9e8982b -- SCORECARD.md` deletions: 0. The C1 landing commit touches one file (`SCORECARD.md`, 43 insertions). The six rows are byte-identical at `9e8982b` and at tip `4e56c48` (`md5 d8f027d60ab29ee603b2c2d27522c159` both), and `SCORECARD.md` at the tip still begins with the base bytes (81245 → 91433 bytes).

## Findings

1. **N06 HONEST** — `census/round-21/oracle-acceptance.json` `oracle.labelled=2372`; the cell says "oracle2372 keys" (`SCORECARD.md:159` at the base). `count-read-root.py:80` sets `labelled` to `len(keys)` over the TSV rows, and the TSV holds exactly 2372 unique keys (duplicates raise, `:59-60`); E2 reproduces 2372. Same round (r21), same measurement, same commit as the cell — not a coincidental match; 2372 occurs in the record only once (`=2372` in `oracle-acceptance.txt:6`).
2. **N07 HONEST** — `files=192` is the run's transcript-file counter (`count-read-root.py:38` increments per `*.txt`); 64+64+64 files in the three r20 transcript dirs at the landing commit. It is the only 192 in the record. See F4 for a wording caveat about what the 192 counts.
3. **N08 HONEST** — `oracle.tp=3` is `len(selected & expected)` (`count-read-root.py:80`), reproduced by E2. The value 3 is not unique in the record (`read_root=3`, `classes.V-READ-ROOT=3`), but the bound key is the one the cell names ("tp3"), so the match is the quantity, not a like number.
4. **N09 / N10 HONEST** — `oracle.fp=0` / `oracle.fn=0` are measured set differences of the same run (`:80`), reproduced as 0/0 by E2; the unit word in the key (`fp`, `fn`) rules out the three other zero-valued keys (`oracle.extra`, `oracle.missing`). Measured zeros, not unmeasured absences.
5. **N11 HONEST (withdrawal reason true)** — every clause checks out: no `401` at digit boundaries anywhere in the cited blob (the sole `401` byte run sits inside the sha256 at line 26; `grep -c '401'` = 1 line, `\b401\b` = 0); `prior_verdicts` is a 401-element list plus `prior_verdicts_sha256`; `oracle-acceptance.txt` is not on base line 159 (line 159 has no `*` token and does not contain that basename). Reproduced refusals in the Attack log. The integer set for N11 is `{401}` with units `all,tuples`, and no admissible shape expresses it. **Caveat for the ledger (not a wrong withdrawal):** an observable *does* exist in the same round — E2 prints `PRIOR-VERDICTS count=401` from `oracle-acceptance.txt:5` — so this withdrawal records a citation-scope refusal, not an absent measurement; the row's reason text says exactly that.
6. **F4 — N07's cell wording, not the binding.** The 2372 labelled keys span **139** distinct transcript paths (`read-root-oracle.tsv`, recount: `keys 2372 distinct paths 139`), while `files=192` counts all transcript files scanned, of which 53 contribute no read/grep/glob call. "oracle2372 keys over192 files" therefore reads as if 192 files carry keys; the integer 192 is correctly the run's `files` counter. No binding change proposed — the row binds the right quantity, the phrase is loose.
7. **F5 — wave-1 delivery provenance slip, outside any landed row.** `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-c1-bind-N06-N11.md` states "the same commit added ... and `census/round-21/count-read-root.py`". `git log --diff-filter=A -- census/round-21/count-read-root.py` names `f2248c0` (08:58, ancestor of `4eb2fda` at 10:18), not `4eb2fda`. No effect: the script blob at `4eb2fda` exists and is the one used in E2, and the landed rows cite only the JSON.
8. **F6 — counter gap, reproduced, not exploitable on this line.** (a) The frozen literal rule never requires the literal to occur in the base cell: `lit in row_text` is False for `files 192`, `tp 3`, `fp 0`, `fn 0`, `401 tuples` and True only for `oracle2372 keys`; all six pass because the rule checks integer count plus a unit substring. (b) `cited()` accepts any candidate basename as a substring of the row text, so a pre-existing census record named after a word in the cell would count as cited. At line 159 this is not reachable: no `*` token, and of 113 eligible record blobs under `census/round-16/20/21/` exactly one (the JSON) is cited; a manufactured blob is refused by `record-not-unchanged-base-blob` (the rule requires the same blob at base and REV). Stricter-only wording is the L1's call; no row depends on the gap.
9. **Axis reading** — none of the six rows harms calibration, and none changes C2's item set or C3's surface set (they are SCORECARD appends only; the C1 landing commit's stat shows one file). The round's C1 target is still MISSED on the other items (unbound=6 mismatches=17 per `census/round-32/records/amendments.txt`), which is outside this seat.

## Attack log

- **A1 — can the `.txt` record serve N11?** `| N11 | SCORECARD.md:159 | 401 tuples | record: census/round-21/oracle-acceptance.txt:5 | … |` in a base-derived scratch commit `d2dacffc546f7b11e80c23af9e763183475a350a`: v2 → `BAD-ROW(A0a-not-cited)`, mismatches=1; v1 → `RECORD-MISMATCH` (the line holds `count=401` but no `all`/`tuples`). Second refusal route confirmed.
- **A2 — can the list length be a field?** `field: census/round-21/oracle-acceptance.json prior_verdicts=401` at `4a9d6499e5e74aac07208a221c0c7bd08337dc8c` → `BAD-ROW(field-shape)`, mismatches=1; `resolve()` only accepts a JSON integer, and no key carries `all`/`tuples`.
- **A3 — the one 401 substring line as a record.** `record: census/round-21/oracle-acceptance.json:26` at `4c4c0f77b517388f894890503962c765b31562c3` → `RECORD-MISMATCH` (substring `4019`, not digit-bounded; no unit word on the line).
- **A4 — is there a `run:` route?** Enumerated all 234 `tools/` + `tests/fixtures/` basename stems at the base and tested `stem in base_line_159`: zero hits, so no `run:` binding is admissible for any of the six items (matches the delivery's claim of 234).
- **A5 — is any other record blob "cited" on line 159?** Enumerated 113 record-eligible blobs under `census/round-16/20/21/` (no `waves`/`transcripts`/`sources` component, no `.py/.sh/.html/.htm/.raw`) and matched basenames against the row text: exactly one, `census/round-21/oracle-acceptance.json`. `read-root-oracle-provenance.json` (51k lines) is not cited and holds no `401` anyway (`\b401\b` count 0).
- **A6 — stale record?** Recomputed sha256 for all 194 recorded inputs at the landing commit: 193 match, the sole mismatch is the post-r21 tool blob whose recorded hash equals the r21 blob's sha256 (E3). The record is not stale relative to the committed transcripts.
- **A7 — is the delivery's row block what landed?** Extracted the six rows from the delivery code block and from `9e8982b:SCORECARD.md`: `diff` empty (6 lines each, IDENTICAL).
- **A8 — did any later commit edit the rows?** md5 of the six landed rows is identical at `9e8982b` and at tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`; SCORECARD remains append-only at the tip.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/a2w1/SwarmCritic02.md` (this report).

Scratch `/fast/scratch/hyaku/souji-r32/AuditC1N06N11/` removed after the report was written; no lane mutation, no `git add/commit/push` in the lane, no jj call, no pacman transaction, no tool installed.
