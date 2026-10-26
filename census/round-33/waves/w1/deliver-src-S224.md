# deliver-src-S224 — POSIX.1-2024 pathname resolution registry row (round 33, w1, SwarmScribe38)

Seat: SwarmScribe38 (leaf, read-only for the lane). Nothing was run in the lane repo; every
command below ran in `/fast/scratch/hyaku/souji-r33/SourcePOSIX/` and that directory was removed
after this file and the reports were written.

Base: `6017a482e7068d5afb7617640198fbb0fe743357`; list-rev (preregistration)
`2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. `corpus/SOURCES.md` at that commit is byte-identical
to `6017a48`'s (`cmp` clean, 254 lines, 117584 bytes).

## 1. Fetch receipts (live, 2026-10-26, all HTTP 200)

| artifact (in this wave dir) | URL | HTTP | bytes | sha256 |
|---|---|---|---|---|
| `src-S224.html` | https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap04.html | 200 | 70370 | `3cb91dff5e1f07b9a21e0ab7318560019b0401709c68cb8f6581e334f067dc6f` |
| `src-S224-chap03.html` | https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap03.html | 200 | 182262 | `0037b423cc292c3cd7c55d347a2273407d156be2a161e56771b08c1c0d421d5a` |
| `src-S225-path_resolution.7.html` | https://man7.org/linux/man-pages/man7/path_resolution.7.html | 200 | 19215 | `94e3dcca3161a98b0425aba98b32e6bf083a74d10243c548dce18b4a7a2184b4` |
| `src-S224-screened-issue7-chap04.html` | https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap04.html | 200 | 48919 | `8d7b4aa78fa9dea540e79ec1a6f68ebf570d6b6d218c607829b0832426317b2c` |

Fetch command shape (cwd the scratch dir, `curl -sS --max-time 60 -o <file> -w 'HTTP %{http_code} bytes %{size_download}'`).
Neither snapshot is committed by this seat; they are copies in `.ufo/waves/round-33/w1/`.

Line citations below are line numbers of the saved files, HTML entities unescaped and runs of
whitespace collapsed to one space, which is how every quote was matched (`python3 -B`, substring
test against the unescaped text: all five quotes `present: True`).

## 2. Row to append — `S224` (mined)

Append immediately after the `S223` line inside the `## Registry` table (before the blank line that
precedes `## Paths`). Eleven columns, `NF=13`, counted by the validator below.

```
| S224 | IEEE Std 1003.1-2024 (POSIX.1-2024) Base Definitions · §4.16 Pathname Resolution — https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap04.html | spec | A | what POSIX.1-2024 requires of repeated and trailing <slash> characters in a pathname: successive characters count as one, except that exactly two leading ones are the implementation-defined case, and a trailing one forces the last component to resolve to a directory; not a Linux kernel traversal rule, not the meaning an implementation may give the two-leading-slash case, and not the tempfile TMPDIR search order that the mechanism source documents | §4.16 Pathname Resolution in V1_chap04.html :697-702 (one or more trailing <slash>) and :729-732 (single <slash>, null pathname, two successive leading, more than two leading); §3.254 Pathname in V1_chap03.html :1513-1518 (multiple successive <slash>); IEEE Std 1003.1-2024 / The Open Group Base Specifications Issue 8; HTTP 200 on both, 70 370 bytes sha256 3cb91dff5e1f07b9a21e0ab7318560019b0401709c68cb8f6581e334f067dc6f (chap04) and 182 262 bytes sha256 0037b423cc292c3cd7c55d347a2273407d156be2a161e56771b08c1c0d421d5a (chap03); fetched 2026-10-26; snapshots .ufo/waves/round-33/w1/src-S224.html and src-S224-chap03.html | multiple successive <slash> characters are the same character as one, so a scratch path joined from a TMPDIR that ends in "/" plus a "/"-prefixed child names the same directory and not a different one; the exception is exactly two leading <slash> characters, whose meaning is implementation-defined; a trailing <slash> is not decoration, since a pathname ending in one resolves only if the last component resolves to an existing directory, or to a directory entry about to be created | mined | 2026-10-26 | 365d | corpus/lessons/round-33.md |
```

## 3. Rejected candidate row — `S225` (rejected, kept for curation)

Append directly after `S224`. One candidate was opened and rejected for the same teaching, per the
seat item; a second candidate was screened and is recorded in §4, not as a row.

```
| S225 | path_resolution(7) — https://man7.org/linux/man-pages/man7/path_resolution.7.html | docs | A | the trailing-<slash> rule as Linux man-pages states it, screened as a second source for the round-33 repeated-slash teaching; not the successive-<slash> equivalence, which the page does not state | § Trailing slashes, page lines 184-190; page footer "Linux man-pages 6.19"; HTTP 200, 19 215 bytes, sha256 94e3dcca3161a98b0425aba98b32e6bf083a74d10243c548dce18b4a7a2184b4; grep -c slash = 2 and both occurrences are in that section; fetched 2026-10-26 | rejected: the page states only that a pathname ending in "/" forces the preceding component to resolve as a directory, and never says successive <slash> characters are one, so it cannot ground the round-33 scratch-path mechanism; flip if the page gains that equivalence sentence | rejected | 2026-10-26 | 365d | — |
```

## 4. Gate block entry (for `corpus/lessons/round-33.md` § Gate)

Same five-column shape as the round-32 Gate table.

| Candidate | Decision | Source reopened | Located quote / evidence | Reason / flip |
|---|---|---|---|---|
| `S224` IEEE Std 1003.1-2024 (POSIX.1-2024) Base Definitions — §4.16 Pathname Resolution with §3.254 Pathname | ADMIT (new row, mined) | https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap04.html — HTTP 200, 70 370 bytes, sha256 `3cb91dff…dc6f`, fetched 2026-10-26; §3.254 opened on https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap03.html — HTTP 200, 182 262 bytes, sha256 `0037b423…1d5a`; snapshots `.ufo/waves/round-33/w1/src-S224.html`, `src-S224-chap03.html` | chap03 :1516-1517 — "Multiple successive <slash> characters are considered to be the same as one <slash>" (13 words); chap04 :731-732 — "more than two leading <slash> characters shall be treated as a single <slash> character" (14 words); chap04 :697-699 — "ends with one or more trailing <slash> characters shall not be resolved successfully" (13 words); chap04 :729-730 — "A pathname consisting of a single <slash> shall resolve to the root directory of the process." (16 words) | Admit: the standard states the equivalence the C2 repairs rest on, and the exactly-two-leading-slash carve-out, and the trailing-slash directory requirement, all in the current edition. Flip: none needed; a next edition supersedes this row rather than amending it. |
| `S225` path_resolution(7) — man7.org | REJECT (row kept, status `rejected`) | https://man7.org/linux/man-pages/man7/path_resolution.7.html — HTTP 200, 19 215 bytes, sha256 `94e3dcca…84b4`, fetched 2026-10-26; snapshot `.ufo/waves/round-33/w1/src-S225-path_resolution.7.html` | lines 184-190 — "If a pathname ends in a '/', that forces resolution of the preceding component" (14 words); `grep -c slash` = 2, lines 184 and 187, both inside § Trailing slashes | Rejected as insufficient scope: the page carries the trailing-slash rule only and never states that successive `<slash>` characters are equivalent to one, so it cannot ground a scratch path whose components are joined across a duplicated separator. Flip: admit if the page gains that sentence. |
| POSIX.1-2008 (Issue 7) §4.13 Pathname Resolution — same two sentences under the superseded edition | SCREENED OUT, no row | https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap04.html — HTTP 200, 48 919 bytes, sha256 `8d7b4aa7…7b2c`, fetched 2026-10-26; snapshot `.ufo/waves/round-33/w1/src-S224-screened-issue7-chap04.html` | :450-452 — "If a pathname begins with two successive <slash> characters, the first component following the leading <slash> characters may be interpreted in an implementation-defined manner" (24 words); :454 binds the same rules to POSIX.1-2017 | No row: it teaches the same rules but binds them to POSIX.1-2017 (:454), and a row whose scope names a superseded edition would date the claim the lane just measured on current behavior. No flip; the current edition row `S224` supersedes the need. |

## 5. Validation (validator output pasted, command and exit code included)

Everything ran against a scratch tree extracted with
`git -C /home/vgpnk/Projects/shokunin/souji-shokunin archive 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 | tar -x -C tree`
(176 MB, no `.git`, no lane write) so `E11` resolves against real `tools/` and `corpus/` files:
extracting only `corpus/` produced two spurious `E11` lines for `S120`/`S122`
(`tools/souji-size-census.py`), which is why the full tree was used.

### 5a. Control — the base registry, no rows of mine

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $PWD/tree/corpus/SOURCES.base.md > base-validate.txt
BASE_EXIT=0
$ grep -c 'W04' base-validate.txt
36
$ grep -E '	E[0-9]+	' base-validate.txt | wc -l
0
$ grep -E 'S22[45]' base-validate.txt | wc -l
0
```
All 36 lines are `file	W04	<id> duplicate url <host/path> across scopes`, pre-existing at the base
registry; the base file carries no E-code and nothing about `S224` or `S225`.

### 5b. Appended rows, before the round-33 lesson exists (the state the L1 will land in first)

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $PWD/tree/corpus/SOURCES.md
(the same 36 base `W04` lines as 5a, then:)
file	E11	S224 missing used-by corpus/lessons/round-33.md
exit 1
```
The 36 base `W04` warnings are unchanged and none of them names `S224` or `S225`; the single
finding is the `used-by` path this seat was told to write, which does not exist until the lesson
lands. `S225` does not trigger `E11` (rejected rows are not checked) or `W02` (its `teaches` cell is
not thin).

### 5c. Same file with a scratch stand-in for the lesson (proves nothing else is wrong)

```
$ printf 'scratch stub: stands in for the L1 round-33 lesson so E11 can be evaluated\n' > tree/corpus/lessons/round-33.md
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $PWD/tree/corpus/SOURCES.md | grep -Ev 'W04'
file	ok	/fast/scratch/hyaku/souji-r33/SourcePOSIX/tree/corpus/SOURCES.md
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $PWD/tree/corpus/SOURCES.md >/dev/null
STUB_RAW_EXIT=0
```
The stub exists only in the scratch tree and was deleted with it; it is not a delivery.

Row shape: `awk -F'|' '/^\| S22[45] /{print $2, "fields=" NF-2}'` → `S224 fields=11`, `S225 fields=11`.

## 6. Note for the lesson prose (precision, not a contract change)

The seat's summary of the teaching — "multiple successive slashes are treated as one; a trailing
slash means directory" — is correct as far as it goes, but §3.254 carves out one case that a lesson
sentence should not flatten: **exactly two leading** `<slash>` characters are implementation-defined,
and only "more than two" are forced to count as one (chap04 :730-732). For the C2 mechanism the
relevant case is a duplicated separator in the middle of a path (a `TMPDIR` that ends in `/` joined
with a `/`-prefixed child, giving `…//…`), which §3.254 covers without the carve-out; the carve-out
bears only on a pathname that begins with `//`. A lesson sentence that says "any run of slashes is
one, with no exception" would overstate the standard at its first two characters.

## 7. Mined mistake (this run, for the round's mistake entry)

Drafting from §4.16 alone, I first had the rule as "more than two leading slashes are one", which is
all that page says; the general equivalence lives in the §3.254 definition on a different page
(`V1_chap03.html`), and an anchor that cited only `V1_chap04.html` would have left the row unable to
ground the interior double slash the C2 legs exercise. The fix was to open the definitions chapter
and cite both anchors; the row's anchor cell now names both pages and both hashes. Evidence: the two
grep runs that located `tag_04_16` (`src-S224.html:680`) and `tag_03_254` (`src-S224-chap03.html:1513`).

## 8. Limits

- No lane write, no commit, no `git add/commit/push`, no `jj`, no lane tool run. The two rows exist
  only as text in this file and as spliced lines in a scratch tree that was removed.
- `used-by corpus/lessons/round-33.md` cannot validate until the L1 writes that lesson; §5b shows the
  exact one-line finding that remains, and §5c shows the same tree clean once the path exists.
- The validator checks schema, enums, dates, duplicate URLs and `used-by` existence; it does not
  check that the quote is verbatim. The verbatim check is §1's substring test, recorded here.
- `recheck 365d` matches the three existing POSIX rows `S212`-`S214`; it is a cadence, not a claim
  that the standard will change.
