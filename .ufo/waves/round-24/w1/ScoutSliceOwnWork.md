# ScoutSliceOwnWork — round 24 wave 1 (quarantine slice, own-work rows)

## Status
STATUS: PASS — all 4 own-work rows (S123 S124 S131 S133) verdict `present`. Cited paths exist and are tracked in shokuknow, all 7 named digests match `sha256sum`, and the claimed figures are in the bytes. Only S124's payload `.out` is in lane bytes, so S123, S131 and S133 are `not lane-re-derivable`.

## Evidence
Revisions read: lane HEAD `f9db2181647d91470a724a12d626bd6106805076`; shokuknow HEAD `8b94c5c12c0521e4cd9ed8e5b6939afd8518c715`. All cited files were last committed at shokuknow `d9583b5a` (2026-10-23), and `git status --porcelain` on `lanes/souji/round{2,3}` is empty, so the working tree matches the committed bytes. Host: git 2.56.0, kernel 7.2.11-arch1-1. Everything was read-only. No scratch was created, and no tool was installed or updated.

Own-work selection. Of the eight slice ids, only these four register rows cite a `lanes/souji/...` path; S114, S118, S126 and S138 cite URLs.
- `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md` lines 172, 173, 175 and 176 (`souji`, class `payload-absent`, cited source `lanes/souji/round{2,3}/evidence/*.out`).
- `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` lines 21, 22, 29 and 31 have kind `own-work`. The Read tool refused this file even with offset and limit (the file is 170331 B), so the rows were printed with `sed -n 'Np'`.

`find /home/vgpnk/Projects/shokuknow -name ...` found all 7 cited files, and `git ls-files --error-unmatch` shows all 7 tracked.

`sha256sum` (full digest) compared with the prefix each row names:

| row | file | full sha256 | row prefix | match |
|---|---|---|---|---|
| S123 | lanes/souji/round2/evidence/r23-trigger-prune.out | 510722c11a97f6bca8f93e49b8a279f1f109d0222e40f675d001058768e069b4 | 510722c1… | yes |
| S123 | lanes/souji/round2/fixtures/r23-trigger-prune.sh | 11c136aa71066733d50d226d344df9125401780aa81836f8ca9ca68a9997e65a | (none named) | n/a |
| S124 | lanes/souji/round2/evidence/noreplace-probe.out | 1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5 | 1634d206… | yes |
| S124 | lanes/souji/round2/evidence/noreplace_probe.py | 11df88f1f5687e9af93526943d875514d4c6b8e891a998edcc0aab73f1d4739f | 11df88f1… | yes |
| S131 | lanes/souji/round2/evidence/r23-worktree-census.out | 1ac71c4f7199a134c204b45f339aadfc7e90c84b2d640cbed181b3577b9392fd | 1ac71c4f… | yes |
| S133 | lanes/souji/round3/evidence/r24-renameat2-probe.out | a53f1e301d0c6969d589f9071b8a3bac9db8f6e1d3ebbb0ace42c300904b0809 | a53f1e30… | yes |
| S133 | lanes/souji/round3/fixtures/r24-renameat2-probe.py | a4506492cfcf48d6ca7d0810708104770687f83a215266571a63ee35557e922c | a4506492… | yes |

Running `git show HEAD:<path> | sha256sum` on the committed blobs gives the same prefixes.

Byte checks with `grep -F`, run against the cited `.out` files (the gate quotes come from `lanes/souji/round{2,3}/SOURCES-PROPOSED.md`):
- FOUND: `id=SOUJI-R23-TRIGGER-fetch case=fetch before=2 after=1 expect=1 verdict=PASS`, plus the `fetch-auto-off` and `fresh` lines. The file has `verdict=PASS` 8 times: 7 cases plus the SUMMARY line.
- ABSENT: the S124 gate quote `/home/vgpnk/Projects/shokunin<TAB>fstype=btrfs<TAB>NOREPLACE_existing=-1(EEXIST)<TAB>plain_overwrite=0(ok)`.
- FOUND: the same line with `NOREPLACE_new=0(ok)` restored between the fstype and NOREPLACE_existing fields. The file has 5 device lines and 5 `EEXIST`.
- FOUND: `default expiry (3.months.ago):      (no output — none prunable)` in r23-worktree-census.out.
- FOUND: `SUMMARY: every writable mount implements RENAME_NOREPLACE` at line 11 of r24-renameat2-probe.out. The file has 8 lines ending ` ok`.
- ABSENT: the S133 fleet-path gate quote in its exact form. It has 33 spaces after `/home/vgpnk` where the file has 32; only whitespace differs.

The upstream companion quotes were checked against the installed man pages (`man git-worktree` and `man 2 rename`, `col -b`, whitespace squeezed). All four were found, each 1 match:
- `git worktree prune [-n] [-v] [--expire <expire>]`
- `With prune, do not remove anything; just report what it would remove.`
- `Keep the worktree locked after creation.`
- `Don't overwrite newpath of the rename. Return an error if newpath already exists.` (rename.2, line 70)

Lane bytes, using `git ls-files -z | xargs -0 sha256sum` against the 7 digests: only `1634d206…` matches, at two tracked lane paths, `census/round-22/attempt2/sources/vendor-noreplace-probe.out` (commit a211e4d1) and `.ufo/waves/round-22/attempt2/w1/evidence/slice124-noreplace-probe.out`. No other cited file is in lane bytes.

## Findings
1. **S123 `present` (not lane-re-derivable).** The row's figures are in the bytes.
   - The row claims "fetch, pull, merge and rebase each take a stale worktree registration 2 -> 1 with no souji receipt" (SOURCES.append.md:21). The `.out` confirms it with fetch, pull, merge and rebase at `before=2 after=1`, and auto-off, locked and fresh at `2 -> 2`.
   - The row's recheck says to expect "7 PASS and exit 0". The 7 PASS lines are present, but no exit code is recorded in the `.out`; only `SUMMARY verdict=PASS` is.
   - The row names no digest for the fixture `.sh`.
   - The register's quote `git worktree prune [-n] [-v] [--expire <expire>]` (register:172) is git-worktree(1) SYNOPSIS, which the proposed gate attributes to the upstream companion URL, not to the payload. This is an attribution false positive, not a fabrication.
2. **S124 `present`, with one quote defect (payload is lane-resident).** Both named digests match.
   - The row claims "RENAME_NOREPLACE is implemented on every device the lane touches" (SOURCES.append.md:22). The 5 device lines all show `NOREPLACE_existing=-1(EEXIST)` and `plain_overwrite=0(ok)`.
   - The gate's own-work quote (register:173) is elided: it drops the field `NOREPLACE_new=0(ok)`, so it is not verbatim. The meaning is unchanged, but the quote needs correcting before append.
   - The second register quote is rename(2) prose, which is present in the installed page.
   - The payload `.out` is byte-identical in lane bytes at two tracked paths. The probe script `noreplace_probe.py` (11df88f1…) is not in the lane, so the figure can be checked from lane bytes but cannot be regenerated from them.
3. **S131 `present` (not lane-re-derivable).** The row claims "the fleet repo has 5 registrations, 0 prunable and 0 locked" (SOURCES.append.md:29).
   - The census lists 5 `worktree` registrations and `worktree list count after: 5`. The four linked registrations carry `locked=no`, and all three dry-run expiries print `(no output — none prunable)`.
   - The register's quote (register:175) is git-worktree(1) OPTIONS `-n, --dry-run` text, which is present in the man page. Same attribution false positive as S123.
   - The figure is a 2026-10-23 point-in-time reading of the live fleet. Re-deriving it would mean a live fleet census, which is outside this seat.
4. **S133 `present` (not lane-re-derivable).** Both named digests match, and `SUMMARY: every writable mount implements RENAME_NOREPLACE` is at `.out` line 11. All 8 mount lines show `NOREPLACE_existing=EEXIST EXCHANGE=ok WHITEOUT=ok ok`.
   - The row says "8 paths over btrfs/tmpfs/xfs". The bytes hold 8 mount entries but only 7 distinct path labels, because `/fast` appears twice (fstype=btrfs and fstype=xfs). "8 paths" overstates this slightly.
   - The fleet-path gate quote differs from the file by one space.
   - The register quote (register:176) is rename(2) prose, present in the installed page.
5. **Agreement with round 22.** `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-22/attempt2/slice-verdicts.tsv` already records S123, S124, S131 and S133 as `accepted`, with corrections that agree with findings 1–4. For example: "correction: quote belongs to git-worktree(1), not the payload". No disagreement found.
6. **Not lane-re-derivable.** For S123, S131 and S133, the evidence lives only in shokuknow bytes (commit d9583b5a). The lane holds only prose excerpts in round-22 seat reports. Per preregistration line 129, these rows are "not appendable as-is" without relocating or re-citing the payload. S124 is the exception (finding 2).

## Attack log
- **A1 — the register class is mislabeled for own-work rows.** The register defines `payload-absent` as "the fabrication class" and says "companion URLs and local artifacts were all checked". Yet the absent quotes for S123, S131 and S133, and S124's second fragment, are upstream man-page text that the proposed gates attach to a separate "Upstream semantics" URL. All four are present in the installed git 2.56.0 and rename(2) man pages. [INFERENCE] The checker's companion-URL fold did not match these spans. The only real verbatim defect is the elided S124 payload quote. Treating `payload-absent` as fabrication would have wrongly refused 4 rows.
- **A2 — digest binding is weak.** The rows name only 8-hex (32-bit) sha256 prefixes, and S123 names no fixture digest. The prefixes matched here, but the row bytes cannot verify a full digest. The full digests are in the table above.
