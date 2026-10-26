# SwarmExecutor10 — C3 append block: mirror build and validation

## Status

STATUS: PASS — the four normalized rows S216–S219 and their two citing entries were built
in a scratch mirror and the append block clears
`sources-census.sh validate` with exit 0 (`ok`, one expected new W04, no E finding); the
block is delivered paste-ready, so a registry write can proceed after the entries land with
it. Preregistration read first; no predicate, target or counter was touched.

## Evidence

Project card, lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e` (branch master);
preregistration `souji-shokunin/census/round-29/records/preregistration.txt` read at the
start of the run; item 10 (*Scratch transformation and validation*) read from
`shokunin/.ufo/prompts/souji-round-29.md:494-545` (the lane copy
`souji-shokunin/.ufo/prompts/souji-round-29.md` does not exist — `ls` reports
`No such file or directory`).

Four campaign rows located by the assigned pattern in
`shokuknow/merge/souji/SOURCES.append.md`:

```
$ grep -nE '^\| S(117|118|122|136) ' /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md
15:| S117 | statx(2) — ... https://man7.org/linux/man-pages/man2/statx.2.html ...
16:| S118 | On the resemblance and containment of documents — https://doi.org/10.1109/SEQUEN.1997.666900 ...
20:| S122 | link(2) — ... https://man7.org/linux/man-pages/man2/link.2.html ...
34:| S136 | cmp(1) — ... https://man7.org/linux/man-pages/man1/cmp.1.html ...
```

Stripped recheck prose (the registry rows carry `365d`; the campaign cells are recorded here
and in the append-block delivery):

- campaign S117 → lane S216: `on-release — re-read the man-pages 6.x statx(2) page`
- campaign S118 → lane S217: `365d — re-resolve the DOI and re-read § 2`
- campaign S122 → lane S218: `on-release — re-read the man-pages 6.x link(2) page`
- campaign S136 → lane S219: `365d — re-fetch the man7 cmp(1) page`

Re-grounding (every source re-opened by this seat on 2026-10-25; bytes kept in scratch and
digested):

```
statx.2.html   200 33125   sha256 2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e
link.2.html    200 19883   sha256 9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9
cmp.1.html     200  9791   sha256 5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3
broder97resemblance.pdf 200 254930  sha256 da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b
```

All four digests equal the sibling delivery
`.ufo/waves/round-29/w1/sources/SHA256SUMS` — independent fetch, byte-identical result.

DOI probe (the reason the Broder row cites the author-hosted PDF):

```
$ curl -sS -L --max-time 60 -o doi.body -D doi.head -w '%{http_code} %{size_download}' https://doi.org/10.1109/SEQUEN.1997.666900
202 0
HTTP/2 302 -> location: http://ieeexplore.ieee.org/document/666900/
HTTP/1.1 301 -> Location: https://ieeexplore.ieee.org/document/666900/
HTTP/2 202, content-length: 0
```

Mirror (`/var/tmp/souji-r29-C3MirrorValidate/validate`, removed before yield): `corpus/`
copied from the lane (139 registry rows), four rows appended after S215, two placeholder
knowledge files written at their repo-relative paths, `tools/souji-size-census.py` mirrored
(see finding 1).

```
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /var/tmp/souji-r29-C3MirrorValidate/validate/corpus/SOURCES.md
file	W04	S035 ... (35 pre-existing W04 lines omitted here, all reproduced verbatim in the delivery txt)
file	W04	S216 duplicate url man7.org/linux/man-pages/man2/statx.2.html across scopes
file	ok	/var/tmp/souji-r29-C3MirrorValidate/validate/corpus/SOURCES.md
RC=0
```

```
$ bash .../sources-census.sh validate /var/tmp/souji-r29-C3MirrorValidate/validate
RC=0   W04_count=36   validate	ok	.../corpus/SOURCES.md
$ bash .../sources-census.sh census  /var/tmp/souji-r29-C3MirrorValidate/validate
FLEET	rows	143   tier.A 135   tier.B 6   tier.C 2   status.mined 119
```

Row-shape and citation checks on the appended bytes:

```
$ awk -F'|' '/^ {0,3}\| S21[6-9] /{printf "%s NF=%d cells=%d\n",$2,NF,NF-2}' SOURCES.md
 S216  NF=13 cells=11     S217  NF=13 cells=11     S218  NF=13 cells=11     S219  NF=13 cells=11
escaped_pipes_in_new_rows=0
duplicate-verdict-identity cites: S216 S217 S218
duplicate-verdict-byte-equality cites: S219 S217 S218
```

C1-direction check (K1, over a scratch commit `f915b2a2be22610b8fd8c7235f008bcd4d825a9b`
in `/var/tmp/souji-r29-C3MirrorValidate/gitcheck`):

```
SUMMARY k1=6 k2=0 mismatches=6 rev=f915b2a2be22610b8fd8c7235f008bcd4d825a9b
new_ids_in_findings=0
```

The six K1 rows are the pre-existing base disagreements (S215 used-by-no-cite; S075, S076,
S022, S024, S025 cited-not-in-used-by); **none** names S216–S219 or either new entry, so the
append block adds zero K1 debt. `k2=0` is vacuous by construction (comment-only stale-list
fixture — the stale-statement repair is C1, not this seat) and is labelled as such in the
delivery, not reported as green.

Id collision check (0–3 leading-space pattern, item 10):

```
reg=139 staged=134 collisions=31
S216 in_lane_registry=0 in_staged=1   (same for S217, S218, S219)
```

No pacman transaction was run (guard respected); no tool install or upgrade was needed.
Revisions cited: lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e` (read-only), scratch
commit `f915b2a2…`; nothing was committed, staged or mutated in the lane, the fleet root or
`shokuknow`.

## Findings

1. **A corpus-only mirror is not a valid `validate` target when existing rows cite
   `tools/`.** Location: `shokunin/scripts/sources-census.sh:495-503` (`--file` sets the
   `used-by` base to `dirname(file)/..` at line 501) and `:538-573` (`usedby_findings`). With only
   `corpus/` copied, the mirror reported `E11 S120 missing used-by tools/souji-size-census.py`
   and `E11 S122 missing used-by tools/souji-size-census.py`, exit 1. Mirroring that one
   target (sha256 copied from the lane) produced exit 0. A seat that mirrors only `corpus/`
   and sees E11 should suspect mirror truncation before suspecting the rows.
2. **The campaign's DOI locator for Broder is unusable as a recheck.** Location:
   `merge/souji/SOURCES.append.md:16` and its recheck cell "365d — re-resolve the DOI and
   re-read § 2". The DOI resolves 302 → 301 → `HTTP 202`, `content-length: 0`, 0 bytes
   (probe above), so the recheck step is unexecutable. The lane row cites the author-hosted
   PDF instead and records the probe in its anchor; the stripped prose is in the delivery.
3. **`link(2)`'s page date is 2026-02-11, not the campaign row's 2026-02-08.** Location:
   the fetched page footer (`Linux man-pages 6.19 2026-02-11 link(2)`) vs
   `merge/souji/SOURCES.append.md:20`. The campaign row carries the tarball date of the
   earlier statx page; the normalized row uses the page's own date in the source and anchor
   cells. Same tarball (6.19), so tier and scope are unaffected.
4. **S216 is a same-URL admission, and E04 alone would not catch a dishonest one.**
   Location: `shokunin/scripts/sources-census.sh`, the E04 branch keyed on
   `scope_key = u SUBSEP scope`.
   S216 reuses S114's statx URL (`corpus/SOURCES.md:135`) under a different scope string, so
   only W04 fires — by design and consistent with the 35 pre-existing W04 rows. But because
   the scope comparison is exact string equality, any same-URL row can be admitted by
   rewording its scope. Here the two subjects genuinely differ (duplicate-verdict identity
   vs per-item origin record), and the honesty of that difference rests on the admitted
   entry's Gate quote, not on the validator.
5. **A cheaper curation exists for entry 1's statx evidence.** The identity entry could cite
   the existing S114 instead of a new same-URL row, which would avoid one W04 and one row of
   growth. The assignment fixes S216, so the row is delivered as specified; flagged for the
   L1's curation judgement, not changed unilaterally.
6. **`365d` is a tightening of two `on-release` cadences.** Location: campaign recheck cells
   for S117 and S122. `on-release` never reports overdue; `365d` is due 2027-10-25 and enters
   the overdue report on/after that date. Delivered as instructed, and recorded so the
   change is not mistaken for a relaxation.
7. **Rows and entries must land in one commit.** The four `used-by` paths are the two new
   knowledge files; landing the rows first yields E11 on all four. The mirror used minimal
   placeholders (marked `PLACEHOLDER (scratch mirror only)`, `ground: F3`) because the real
   entries are another seat's deliverable — the placeholders are not corpus material and are
   not offered for landing.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-sources-append-block.md` — the four rows, byte-identical
  to the validated mirror rows (`diff` clean), with the renumber map, stripped recheck prose,
  Gate quotes and expected validator result.
- `.ufo/waves/round-29/w1/deliver-mirror-validate.txt` — commands and untrimmed verbatim
  output for every check above.
- `.ufo/waves/round-29/w1/SwarmExecutor10.md` — this report.
