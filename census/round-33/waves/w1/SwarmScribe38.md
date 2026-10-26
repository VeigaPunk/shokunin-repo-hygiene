# SwarmScribe38 — S224 POSIX.1-2024 pathname resolution, opened live (round 33, w1)

STATUS: PASS — the source was opened live (HTTP 200 on every URL), its registry row (S224, `mined`) and a rejection row (S225) were drafted in the 11-column shape, the Gate entry names the located quotes, and the row validates clean in scratch; the only validator finding is the one the seat item's own `used-by` of `corpus/lessons/round-33.md` predicts, because that lesson does not exist yet.

## Evidence

All commands ran in `/fast/scratch/hyaku/souji-r33/SourcePOSIX/` with `TMPDIR` set under it; nothing ran in the lane. Read-only lane reads used `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show|archive`.

1. Contract and shapes read first: `preregistration.txt` (254-line freeze note), `git show 2d9bca55…:corpus/SOURCES.md` (254 lines, 117584 bytes; `cmp` equal to `6017a482…`'s copy), header line `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |` plus rows S210–S223 for the current cell style, `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (rules E01–E12, W01–W04, kind enum, `--file` resolving `dir` as the parent of `corpus/`), and the round-32 lesson `## Gate` table.

2. Fetches, 2026-10-26, `curl -sS --max-time 60 -o <file> -w 'HTTP %{http_code} bytes %{size_download}'`:

| file | URL | HTTP | bytes | sha256 |
|---|---|---|---|---|
| `src-S224.html` | https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap04.html | 200 | 70370 | `3cb91dff5e1f07b9a21e0ab7318560019b0401709c68cb8f6581e334f067dc6f` |
| `src-S224-chap03.html` | https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap03.html | 200 | 182262 | `0037b423cc292c3cd7c55d347a2273407d156be2a161e56771b08c1c0d421d5a` |
| `src-S225-path_resolution.7.html` | https://man7.org/linux/man-pages/man7/path_resolution.7.html | 200 | 19215 | `94e3dcca3161a98b0425aba98b32e6bf083a74d10243c548dce18b4a7a2184b4` |
| `src-S224-screened-issue7-chap04.html` | https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap04.html | 200 | 48919 | `8d7b4aa78fa9dea540e79ec1a6f68ebf570d6b6d218c607829b0832426317b2c` |

3. Quotes checked as substrings of the unescaped, whitespace-collapsed bytes (`python3 -B`, all five `present: True`): chap03 :1516-1517 "Multiple successive <slash> characters are considered to be the same as one <slash>" (13 words); chap04 :731-732 "more than two leading <slash> characters shall be treated as a single <slash> character" (14); chap04 :697-699 "ends with one or more trailing <slash> characters shall not be resolved successfully" (13); chap04 :729-730 "A pathname consisting of a single <slash> shall resolve to the root directory of the process." (16); man7 :185-186 "If a pathname ends in a '/', that forces resolution of the preceding component" (14). No quote contains a pipe character.

4. Validation in scratch, on a tree from `git -C <lane> archive 2d9bca55… | tar -x -C tree` (176 MB, 147 registry rows at that commit) with the rows spliced after `S223`:

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $PWD/tree/corpus/SOURCES.md
(the 36 base W04 lines, then:)
file	E11	S224 missing used-by corpus/lessons/round-33.md
exit 1

$ # same file, scratch stand-in for the lesson at tree/corpus/lessons/round-33.md
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $PWD/tree/corpus/SOURCES.md | grep -Ev 'W04'
file	ok	/fast/scratch/hyaku/souji-r33/SourcePOSIX/tree/corpus/SOURCES.md
STUB_RAW_EXIT=0
```

Control on the unmodified base file of the same tree: `BASE_EXIT=0`, `grep -c W04` = 36, E-code lines = 0, lines naming S224/S225 = 0. Census counts: base `rows 147 tier.A 139 status.mined 124 status.rejected 9`; with my rows `rows 149 tier.A 141 status.mined 125 status.rejected 10`, `tier.invalid 0 status.invalid 0`.

5. Delivered rows are byte-identical to the validated ones (`cmp` of the fenced row lines against the spliced source lines: `S224-IDENTICAL`, `S225-IDENTICAL`).

## Findings

1. **S224 opens cleanly.** POSIX.1-2024 §4.16 Pathname Resolution (chap04 :680-734) plus §3.254 Pathname (chap03 :1513-1518) teach exactly the round's subject: successive `<slash>` characters are one, exactly two leading ones are implementation-defined, a trailing one forces directory resolution. No existing row shares either URL or that scope (`grep -i` over the base registry for `slash`, `pathname`, `chap04` returned nothing but the unrelated `proc_pid_fd` and GLib pathname-reservation rows), so no E04 and no W04 fall on my rows. Location: `corpus/SOURCES.md` registry, append after line 168 (the `S223` row).

2. **The frozen round's paraphrase needs one carve-out, and the lesson prose should carry it.** The seat item summarises "multiple successive slashes are treated as one"; the standard makes exactly two leading `<slash>` characters implementation-defined and forces only "more than two" to one (chap04 :730-732, chap03 :1516-1518). The C2 mechanism (a `TMPDIR` ending in `/` joined to a `/`-prefixed child, an interior `//`) is unaffected, but a lesson sentence with no exception would overstate the standard at its first two characters. Location: `corpus/lessons/round-33.md` § Gate, S224 reason cell; the deliverable's §6 states the precise sentence to use.

3. **One rejected candidate, opened and screened out for insufficient scope.** `path_resolution(7)` (man7, Linux man-pages 6.19, 19215 bytes) gives the trailing-slash rule at lines 184-190 and mentions `<slash>` twice in the whole page, both inside that section — it never states the equivalence, so it cannot ground a duplicated separator. Retained as row S225 (`rejected`, `—` used-by) so the rejection is citable. Location: deliverable §3.

4. **A second candidate was screened without a row.** POSIX.1-2008 Issue 7 §4.13 carries the same two sentences but binds them to POSIX.1-2017 (:454); citing it would date a claim measured on current behaviour. Bytes saved and hashed in the Gate table, no registry row. Location: deliverable §4, third row.

5. **Validator trap for seats that copy only `corpus/`.** `--file` resolves `used-by` against the parent of `corpus/`, so a corpus-only copy reports `E11` for S120 and S122 (`tools/souji-size-census.py`) that are false at the real base. Validating the full `git archive` tree removes them and leaves only the genuine S224 `E11`. Location: `scripts/sources-census.sh` § `resolve_targets` and `usedby_findings`; observed in this run's first validation attempt.

6. **`used-by` cannot be green until the lesson lands.** `corpus/lessons/round-33.md` is absent at the base and in the lane working tree (`ls` on the lessons directory in this run; lane tip `fef88f2` per `git log --oneline -3`); the L1's lesson write is the step that clears the single `E11`. No predicate, target, counter or leg was touched. Location: `corpus/lessons/`, `census/round-33/records/`.

## Attack log

Not applicable — this seat is not an attack item. One rule-adjacent observation is recorded as finding 2: the round's one-line paraphrase of the standard is looser than the standard's own two sentences, so a lesson written from the paraphrase alone would overstate it. The frozen C1/C2 predicates are untouched, and the SOURCES row schema is not a frozen predicate (the validator is the lane's existing instrument, run unmodified).

## Deliveries

- `.ufo/waves/round-33/w1/src-S224.html` — chapter 4 bytes as served (below the fold: 70370 bytes, sha256 `3cb91dff…dc6f`).
- `.ufo/waves/round-33/w1/src-S224-chap03.html` — §3.254 anchor bytes (182262 bytes, sha256 `0037b423…1d5a`).
- `.ufo/waves/round-33/w1/src-S225-path_resolution.7.html` — rejected candidate bytes (19215 bytes, sha256 `94e3dcca…84b4`).
- `.ufo/waves/round-33/w1/src-S224-screened-issue7-chap04.html` — screened Issue 7 bytes (48919 bytes, sha256 `8d7b4aa7…7b2c`).
- `.ufo/waves/round-33/w1/deliver-src-S224.md` — S224 and S225 rows ready to append, the Gate entry (admit, reject, screen), fetch receipts, the precision note, the mined mistake, the validator transcripts.
- `.ufo/waves/round-33/w1/SwarmScribe38.md` — this report.

None of the four snapshots is committed by this seat. The scratch tree `/fast/scratch/hyaku/souji-r33/SourcePOSIX/` was removed after these files were written (`ls` returns no such directory). No tool was installed or upgraded this run; `pacman` was not invoked (host-wide pause honoured).
