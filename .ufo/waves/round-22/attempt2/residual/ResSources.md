STATUS: PARTIAL

# ResSources — S109–S114 registry rows against committed snapshots + registry validate

Scope executed: read `corpus/SOURCES.md` rows S109–S114 at the lane tip (HEAD `c9f1fe3`, worktree clean for
`corpus/SOURCES.md` and `census/round-22/attempt2/`), whitespace-collapse each named snapshot, test the
`teaches` and `anchor` claims, resolve every `used-by` path, then run the frozen conformance command.
Read-only; no installs; no git/jj writes. Evidence: `evidence/ResSources-checks.tsv`,
`evidence/ResSources-validate.out`.

## 1. Executed checks

### 1.1 Frozen conformance command (prereg C2 target clause)

```
$ cd /home/vgpnk/Projects/shokunin && bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
... (30 W04 lines, highest id S108) ...
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
EXIT=0
```

- Exit code: **0**.
- E-codes: **none** (`grep -c $'\tE' → 0`).
- W04: **30** warnings, all on historical ids S035…S108; **none** on S109–S114 and no duplicate-URL
  warning for rename.2 / mv.1 / gio.1 / File.trash / statx.2 (the five new URLs are first occurrences).
- This satisfies the prereg's "registry conformance … exit 0" clause for C2.

### 1.2 Committed-bytes status

`git ls-files` shows all five `.txt` snapshots plus `vendor-noreplace-probe.out` tracked; `git status --short`
is empty for `corpus/SOURCES.md` and `census/round-22/attempt2/`; `git show HEAD:corpus/SOURCES.md` contains
the same S109–S114 rows (S111 anchor identical at HEAD). Rows and snapshots are landed, not staged.

### 1.3 Whitespace-collapsed claim tests

Full receipts in `evidence/ResSources-checks.tsv`. Summary:

| row | teaches claim tested | result |
|---|---|---|
| S109 | five paths, EEXIST on existing target, plain overwrite ok, kernel | carried by probe output |
| S109 | "3 filesystems" | carried (btrfs, tmpfs, xfs) |
| S109 | "4 distinct devices" | **not in output**; live `stat -c %d` → 32/56/56/33/66308 (4 distinct) |
| S110 | "Return an error if newpath already exists"; ext4 3.15 / btrfs,tmpfs,cifs 3.17 / xfs 4.0 / others 4.9 | carried (`man7-rename.2.txt` ll. 148–167) |
| S111 | "do not copy if renaming fails"; "exchange source and destination" | carried |
| S111 | "cross-device … instead of a copy+remove" | **not carried** (0 hits: cross-device / copy+remove / different file system / EXDEV) |
| S111 | anchor "§ OPTIONS" | **section does not exist** (0 line-initial OPTIONS in `.txt`, 0 "OPTIONS" tokens in `.raw`; options sit under DESCRIPTION, line 60) |
| S112 | "List files in the trash with their original locations"; "A URI beginning with trash:// is expected here"; § COMMANDS | carried (`arch-gio.1.txt` ll. 563, 568–569; COMMANDS at l. 97) |
| S113 | recoverable; can return G_IO_ERROR_NOT_SUPPORTED when trashing disabled for system mounts; § Description | carried (`gtk-filetrash.txt` ll. 405–411; heading l. 395) |
| S114 | stx_ino, stx_nlink, stx_btime, stx_mnt_id as distinct struct fields; § DESCRIPTION struct statx | carried (`man7-statx.2.txt` ll. 74–106) |

S109 vendored-bytes check: `sha256sum` = `1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5`
(matches the row's `1634d206…8bb5`), and `cmp` against
`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace-probe.out` reports byte-identical.
The probe's kernel line matches the running host (`uname -r` = 7.2.11-arch1-1).

### 1.4 used-by resolution

| row | used-by | exists | tracked | cites the id |
|---|---|---|---|---|
| S109–S111 | `corpus/knowledge/quarantine-staging-no-copy-r23.md` | yes | yes | yes (frontmatter `source: S109/S110/S111`) |
| S112–S114 | `corpus/knowledge/quarantine-origin-record-fields-r24.md` | yes | yes | yes (frontmatter `source: S112/S113/S114`) |

No dangling `used-by` path.

## 2. Per-row verdicts

| row | teaches | anchor | used-by | verdict |
|---|---|---|---|---|
| S109 | carried (+F4 device-count derivation) | n/a (own-work) | ok | **PASS**, with provenance nits F3/F4 |
| S110 | carried verbatim-level | carried | ok | **PASS** |
| S111 | half-carried (F2) | **wrong section (F1)** | ok | **FAIL** (locator; teaches claim beyond page) |
| S112 | carried | carried | ok | **PASS** |
| S113 | carried | carried | ok | **PASS** |
| S114 | carried | carried | ok | **PASS** |

No row contains a claim the snapshot **contradicts**; the defects are an uncarried inference (S111) and a
nonexistent section token (S111). All six rows have 11 cells, correct id order after S108, `opened` = 2026-10-25.

## 3. Findings

**F1 (medium) — S111 `anchor` names a section the snapshot does not have.**
`| S111 | … § OPTIONS --no-copy and --exchange; snapshot census/round-22/attempt2/sources/man7-mv.1.txt …`
The page has no OPTIONS heading: `grep -cE '^[[:space:]]*OPTIONS([[:space:]]|$)' man7-mv.1.txt` = 0,
`grep -c 'OPTIONS' man7-mv.1.raw` = 0; `mv`'s option list sits inside DESCRIPTION (`man7-mv.1.txt:60`, with
`--exchange` at l. 75 and `--no-copy` at l. 90). The knowledge entry that cites this row already uses the
correct locator: `corpus/knowledge/quarantine-staging-no-copy-r23.md:32` — "S111, § DESCRIPTION, option
`--no-copy` — the page has no OPTIONS heading". The wave-1 report fixed the entry's citation
(`w1/evidence/CritC2Coverage.md:162`) but not the row. Commit `af73b8b` ("row wording") rewrote S111's
`teaches` and left the anchor unchanged (`git show af73b8b -- corpus/SOURCES.md`). Landed at HEAD; registry
and knowledge entry now disagree on the same locator.

**F2 (low-medium) — S111 `teaches` asserts a mechanism the named page does not carry.**
"…turns a cross-device staging move into a failure instead of a copy+remove". The snapshot carries only
"do not copy if renaming fails" (l. 90–91); `cross-device`, `copy+remove`, `different file system` and
`EXDEV` have 0 hits in `man7-mv.1.txt`/`.raw`. The copy-then-remove behaviour is S025's fact
(`corpus/SOURCES.md:45`), which S111's own scope cell explicitly excludes. The parenthetical
"(page: do not copy if renaming fails)" is honest about the quoted part, but the sentence still presents the
inference as the page's teaching. Round-1 residual wording was "makes mv fail rather than fall back to
copy+remove, on any filesystem" (`w1/RevRows.md:239-242`, finding F7). **Partially fixed**: "on any
filesystem" is gone; the unquoted mechanism remains.

**F3 (low) — S109 source cell cites a path that does not resolve from either repository root.**
`lanes/souji/round2/evidence/noreplace_probe.py and noreplace-probe.out` exists neither at the lane root
(`souji-shokunin/lanes` — absent) nor at `/home/vgpnk/Projects/shokunin/lanes` (absent); it exists at
`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/`. The vendored copy is byte-identical, so the
claim survives, but the row never names the root, and the same entry attributes the probe to the
"corpus-expansion-1 staging lane" while the row calls it "souji round-2". Not E-level (path is not
backticked, so the declared-evidence scanner's class A does not see it).

**F4 (low) — S109 `teaches` reports a device count the probe output cannot re-derive.**
The output records only path, `fstype`, result codes and kernel. "4 distinct devices" is not in those bytes;
it is true today (`stat -c %d`: 32/56/56/33/66308 → 4 distinct; fstypes btrfs/btrfs/btrfs/tmpfs/xfs → 3),
but a later reader of the snapshot cannot reproduce it without the live mounts. Either add `st_dev` to the
probe output or state the device count as the lane's derivation. Round-1 flagged the phrasing "all five
probed devices" (`w1/RevRows.md:238`); the landed wording ("all five probed directories (3 filesystems, 4
distinct devices)") **is fixed** — only the derivation gap remains.

**F5 (low, registry conformance) — no provenance paragraph for S109–S114.**
`corpus/SOURCES.md`'s Provenance list ends at round-22 S108 (line 169); the six new rows are dated
2026-10-25 and cite `census/round-22/attempt2/sources/`, but no bullet records the question, pages screened,
admit/reject split and stop condition, which every earlier round carries. The validator does not check this
(exit 0), so it is invisible to the frozen counter. Whether the round report carries an equivalent record is
outside this assignment's read set.

## 4. Residual risk / verification gaps

- Claims were tested against the committed `.txt` extractions (and `.raw` only for page-version and the
  OPTIONS token); no URL was re-fetched, so live-page drift since capture is unmeasured.
- S109's probe was not re-run (the row states "not re-run in this lane"); only its bytes, hash, fstypes and
  device ids were compared to the current host.
- The `git show af73b8b` history check is a read of the lane repo; no write, no jj, no commit was issued.
- Nothing was installed or upgraded during this review.
