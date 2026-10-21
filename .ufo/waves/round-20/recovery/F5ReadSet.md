# F5 read-set and source-binding spotcheck

## Observation boundary

Observed lane `HEAD`: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. At that observation, working-byte SHA-256 values were:

- `corpus/knowledge/process-residue-observations.md`: `5031c5cbebe1dd9907299e30550c6fec1e53177d5d8742a8fd889cf001a29f34`
- `corpus/QUALITY.md`: `f93e535c2e6c99f74d55fb89100fcb979fd54428e486309958bf5884c66cc4e4`
- `corpus/SOURCES.md`: `199c06c9a57e692d010bda0578ae9f8a47bbe6fe2ef34bdbc802996e3b95a500`

Read-only. No test, fixture, census, or target-code execution. The bounded code-file list for this item did not include the F5 implementation files, so the code/fixture digests below are recorded claims from the entry, not independently recomputed by this seat.

## Observed facts

- The appended Round-20 correction at `corpus/knowledge/process-residue-observations.md:101-105` explicitly supersedes the preceding broad read/enumeration wording, names S082/S086-S088 and S075/S076, pins baseline `12516f7...`, and gives a `sha256sum` recheck for the tool, fixture, and counter. Its table at `:111-115` records SHA-256 values for exactly those three paths. The complete asserted read set at `:117-122` includes proc listing, uptime, boot_id, stat, status, cmdline, cwd, fd directory/link names and wchan; it states no environ read, narrows coverage to eligible readable own-uid candidates, and notes skipped/racing data. The redaction caveat and reason-field concern are explicitly bounded at `:124-127`; other-uid and reap boundaries are explicit at `:129-133`.
- Q42 at `corpus/QUALITY.md:101` now explicitly supersedes Q32's incomplete read-set/per-process wording while preserving Q33. It names the same read set and the same eligibility, skip, redaction, other-uid, and no-reap limits. Thus the former Q32 omission of `status` is no longer presented as the current read-set (`QUALITY.md:81,101`).
- S086-S088 at `corpus/SOURCES.md:106-108` are append-only corrections to the S083-S085 teaches cells and each names the knowledge entry as `used-by`. Their corrected teachings match the public pages for fd link/type content, wchan meaning/access, and status formatting/state values. I reopened the three man7 pages read-only: `proc_pid_fd(5)` DESCRIPTION, `proc_pid_wchan(5)` DESCRIPTION, and `proc_pid_status(5)` DESCRIPTION. S086's page also explicitly documents the ptrace access check for dereferencing/reading fd links; S087 documents the corresponding wchan access check; S088 states the parseable stat/statm summary and the seven State letters.
- The historical wave note `.ufo/waves/round-19/w1/ScribeProcSkillRow.md:90-92` lists tool read sites, the P1-P19 fixture and P7 syscall-trace check, and the counter path. The permitted round-19 fleet-report excerpt at `/home/vgpnk/Projects/shokunin/.ufo/reports/round-19/souji.md:264-269` independently records the tool and counter digests matching the new table; it does not record the fixture digest. These are historical receipts, not fresh execution or a fresh byte-to-hash comparison.

## Calibration finding / OPEN

`corpus/knowledge/process-residue-observations.md:18-20` retains the fd assertion “The same ptrace permission rule applies,” still tagged `(S083)`. The Round-20 appendix says to use S086-S088 instead of the superseded S083-S085 teaches claims (`:107`), but S086's corrected `teaches` cell at `corpus/SOURCES.md:106` summarizes only the symlink and `type:[inode]` facts and the removed path-shaped-target inference; it does not bind that retained ptrace assertion. The actual `proc_pid_fd(5)` page does support the assertion, so this is not a demonstrated factual error. It is a precise claim-to-row gap: after the supersession, the knowledge text's fd permission statement is not represented in S086's corrected teaching summary.

Concrete oracle change: require the F5 source check to map every retained kernel-documentation sentence to its corrected row; specifically, add the fd-link `PTRACE_MODE_READ_FSCREDS` statement to an append-only S086 correction (or a separately scoped source row) and point the retained knowledge sentence to it. Keep this distinct from the already-correct S087 access-rule teaching.

The code/fixture binding is well specified as an asserted path-plus-SHA table at `process-residue-observations.md:103-118`, but this seat did not verify that those three hashes match current file bytes; the fixture hash also lacks corroboration in the allowed historical report excerpt. No claim about actual live procfs behavior or universal redaction is supported here. Confidence: high for the documentary mismatch and read-set/Q42 comparison; unverified for code/fixture byte correspondence.