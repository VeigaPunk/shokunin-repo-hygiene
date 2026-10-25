STATUS: PASS

Seat: L1Souji22.DraftEntryNoCopy (scribe). Item: draft the lane-format knowledge
entry for the no-clobber staging primitive, adapted from
`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md`;
draft in this report; no corpus file created.

Two files were written, both absolute under the lane root and both named by the item:

- `.ufo/waves/round-22/attempt2/w1/evidence/DraftEntryNoCopy.md` — receipts + the draft
  entry verbatim (draft begins after the line `<!-- rule: everything below is the draft
  entry, verbatim -->`).
- `.ufo/waves/round-22/attempt2/w1/DraftEntryNoCopy.md` — this report.

No probe was executed, no move/delete was performed, no git/jj write was run, no
registry row was added, and the target entry path was not touched (it already exists at
HEAD, see Finding 6).

## 1. What was read this round (executed: `read`/`bash` only)

Sources actually opened, bytes read, not just cited:

| path | used for |
|---|---|
| shokuknow `merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md` | the staged entry being adapted (54 lines) |
| shokuknow `lanes/souji/round2/evidence/noreplace_probe.py` | the probe's actual protocol (ctypes/renameat2, three steps, five dirs) |
| shokuknow `lanes/souji/round2/evidence/noreplace-probe.out` | the five device rows |
| `census/round-22/attempt2/sources/vendor-noreplace-probe.out` | the lane's vendored copy; row counts |
| `census/round-22/attempt2/sources/man7-rename.2.txt` | RENAME_NOREPLACE, the EXCHANGE exclusion, support schedule, EEXIST/EINVAL |
| `census/round-22/attempt2/sources/man7-mv.1.txt` | `--no-copy`, `--exchange`, `-n, --no-clobber` |
| `corpus/SOURCES.md` | rows S109/S110/S111 (mapping targets) |
| `corpus/QUALITY.md` | Q1–Q53 admission bar; Q4 fixture-path rule |
| `corpus/knowledge/quarantine-origin-record-fields-r24.md` | lane frontmatter shape |
| `tools/souji-gate-check.py` | the frozen predicate as implemented (checks 1–6, slice) |
| `.deepresearch/20261024_064146_r9-tierrules/final_turn_001.md:118` | the rejected row, verbatim |
| shokuknow `lanes/souji/round2/evidence/r23-trigger-prune.out` | rejection check (0 matches) |

## 2. Executed receipts

```
$ sha256sum census/round-22/attempt2/sources/vendor-noreplace-probe.out \
            /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace_probe.py \
            /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace-probe.out
1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5  census/round-22/attempt2/sources/vendor-noreplace-probe.out
11df88f1f5687e9af93526943d875514d4c6b8e891a998edcc0aab73f1d4739f  /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace_probe.py
1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5  /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace-probe.out

$ cmp census/round-22/attempt2/sources/vendor-noreplace-probe.out \
      /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace-probe.out && echo BYTE_IDENTICAL
BYTE_IDENTICAL

$ awk -F'\t' 'NF>1 && $2 ~ /^fstype=/{n++} END{print n}' census/round-22/attempt2/sources/vendor-noreplace-probe.out
5
$ grep -c 'NOREPLACE_new=0(ok)'           <vendor out>   -> 5
$ grep -c 'NOREPLACE_existing=-1(EEXIST)' <vendor out>   -> 5
$ grep -c 'plain_overwrite=0(ok)'         <vendor out>   -> 5
$ grep -c 'fstype=btrfs' <vendor out> -> 3 ; 'fstype=tmpfs' -> 1 ; 'fstype=xfs' -> 1
$ grep '^kernel:' <vendor out>
kernel: 7.2.11-arch1-1

$ uname -r
7.2.11-arch1-1
$ /usr/bin/mv --version | head -1
mv (GNU coreutils) 9.12
$ pacman -Qo /usr/bin/mv
/usr/bin/mv is owned by coreutils 9.12-2
$ /usr/bin/mv --help | grep -n -E 'no-copy|exchange|no-clobber'
13:      --exchange
14:        exchange source and destination
19:  -n, --no-clobber
22:      --no-copy
49:'none' is like the --no-clobber option, in that no files in the

$ type -a mv
mv is a shell builtin
mv is /usr/bin/mv
$ mv --version
mv 0.8.0                       # the harness shell's builtin, NOT coreutils

$ grep -n "man-pages-6.19" census/round-22/attempt2/sources/man7-rename.2.txt
382: This page was obtained from the tarball man-pages-6.19.tar.gz
$ grep -n "coreutils-9.11" census/round-22/attempt2/sources/man7-mv.1.txt
184: from the tarball coreutils-9.11.tar.xz fetched from
192:GNU coreutils 9.11 April 2026 MV(1)
$ grep -n "EEXIST\|EINVAL" census/round-22/attempt2/sources/man7-rename.2.txt
314: EEXIST flags contains RENAME_NOREPLACE and newpath already exists.
316: EINVAL An invalid flag was specified in flags.
318: EINVAL Both RENAME_NOREPLACE and RENAME_EXCHANGE were specified in
321: EINVAL Both RENAME_WHITEOUT and RENAME_EXCHANGE were specified in
324: EINVAL The filesystem does not support one of the flags in flags.

$ sed -n '118p' /home/vgpnk/Projects/shokuknow/.deepresearch/20261024_064146_r9-tierrules/final_turn_001.md
| `souji` / round2 / S123 | `lanes/souji/round2/evidence/r23-trigger-prune.out` | `git worktree prune [-n] [-v] [--expire <expire>]` |
$ grep -c "worktree" /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.out
0
$ ls /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.sh
ls: cannot access '.../evidence/r23-trigger-prune.sh': No such file or directory   # exit 2

$ git cat-file -e HEAD:census/round-22/attempt2/sources/man7-rename.2.txt      -> ok
$ git cat-file -e HEAD:census/round-22/attempt2/sources/man7-mv.1.txt          -> ok
$ git cat-file -e HEAD:census/round-22/attempt2/sources/vendor-noreplace-probe.out -> ok
```

## 3. Conformance of the draft to the frozen per-entry predicate (measured)

The evidence file is laid out so the draft's `## Gate` is the last `## ` section, which lets
the real tool read it directly:

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries .ufo/waves/round-22/attempt2/w1/evidence/DraftEntryNoCopy.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
FAIL .ufo/waves/round-22/attempt2/w1/evidence/DraftEntryNoCopy.md check5-no-source-citation
entries=1 ok=0 slice_verdicts=8 slice_total=8 fail=1
rc=1
```

Exactly one failure, and it is the expected one: the item requires `S-NEW-<slug>`
placeholders, and the checker's `SOURCE_RE` matches `S<digits>` only
(`^source:\s*(S\d{3,})`). Every other check passes as written; independently re-derived with
the tool's own regexes (`gc.squash`, `QUOTE_RE`, `LOCATOR_RE`, `SNAPSHOT_RE`):

```
line 7:  words=14 locator=yes inside_snapshot_dir=True verbatim_in_snapshot=True  (rename.2 refusal)
line 8:  words=7  locator=yes inside_snapshot_dir=True verbatim_in_snapshot=True  (support precondition)
line 9:  words=7  locator=yes inside_snapshot_dir=True verbatim_in_snapshot=True  (EXCHANGE exclusion)
line 10: words=8  locator=yes inside_snapshot_dir=True verbatim_in_snapshot=True  (EEXIST)
line 11: words=6  locator=yes inside_snapshot_dir=True verbatim_in_snapshot=True  (mv --no-copy)
quote_rows 5 problems []
ADMIT_rows 5 REJECT_rows 1 reject_has_reason [True]
cited_by_SOURCE_RE []            # placeholders, as instructed
repoint_targets_present {'S109': True, 'S110': True, 'S111': True}
```

Post-repoint simulation (same predicate, placeholders substituted in memory; no file written):

```
post_repoint_cited ['S109','S110','S111'] quote_rows 5 fails [] ok True
```

Slice side observed only (not my item): `slice_verdicts=8 slice_total=8`, i.e. the frozen
8-id slice has all 8 verdict rows in `census/round-22/attempt2/slice-verdicts.tsv`.

**Landing instruction for L1 (the only remaining step this draft cannot do):** replace
`S-NEW-noreplace-probe` → `S109`, `S-NEW-rename2` → `S110`, `S-NEW-mv1` → `S111`. Those
three rows already exist (`corpus/SOURCES.md:129-131`) and name this exact entry, so no row
is added and the preregistration's "cited, not duplicated" rule holds. After that swap the
per-entry predicate is satisfied by the measured simulation above.

## 4. The draft (verbatim; identical to the evidence file from the rule marker on)

````
source: S-NEW-noreplace-probe — own-work probe lanes/souji/round2/evidence/noreplace_probe.py (sha256 11df88f1f5687e9af93526943d875514d4c6b8e891a998edcc0aab73f1d4739f) and its output lanes/souji/round2/evidence/noreplace-probe.out (sha256 1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5), byte-identical to census/round-22/attempt2/sources/vendor-noreplace-probe.out; kernel 7.2.11-arch1-1, produced 2026-10-23; read this round, not re-executed in this lane
source: S-NEW-rename2 — https://man7.org/linux/man-pages/man2/rename.2.html — § DESCRIPTION flags, § ERRORS — snapshot census/round-22/attempt2/sources/man7-rename.2.txt (man-pages-6.19.tar.gz)
source: S-NEW-mv1 — https://man7.org/linux/man-pages/man1/mv.1.html — § OPTIONS --no-copy, --exchange — snapshot census/round-22/attempt2/sources/man7-mv.1.txt (coreutils-9.11 page)
verified-at: 2026-10-25 — both snapshots opened this round; host /usr/bin/mv = GNU coreutils 9.12-2 (pacman -Qo /usr/bin/mv); kernel 7.2.11-arch1-1 (uname -r)
recheck: 90d — re-open both snapshots and vendor-noreplace-probe.out, and confirm /usr/bin/mv --help still lists --no-copy; re-run the probe only when the mount set or the kernel changes
ground: F4 — restorable quarantine (the staging primitive: no-clobber rename)

# A no-clobber staging rename exists on all five probed devices, and `mv --no-copy` is the portable fallback

## Claim (F4: sourced semantics, one vendored fleet measurement)

The lane's audit rule is dry-run by default, quarantine before delete. A staging
move that can overwrite an existing quarantine artifact breaks that rule before
any deletion decision is taken, so the primitive has to be a refusal, not a best
effort. Two spellings of that refusal are documented, and one of them has been
measured on this host's filesystem set.

1. **The kernel flag is specified as a refusal, with an explicit per-filesystem
   precondition.** (S-NEW-rename2) § DESCRIPTION, `flags` argument: "Don't
   overwrite newpath of the rename. Return an error if newpath already exists."
   (snapshot lines 148-150.) The same section states the precondition —
   "RENAME_NOREPLACE requires support from the underlying filesystem." — and then
   lists the schedule: ext4 (Linux 3.15); btrfs, tmpfs and cifs (3.17); xfs (4.0);
   many other filesystems in 4.9 (snapshot lines 155-167). § ERRORS names the
   refusal: "EEXIST flags contains RENAME_NOREPLACE and newpath already exists."
   (snapshot line 314.) That is a support *schedule*, not a fact about any host.
2. **The two flags cannot be combined.** § DESCRIPTION: "RENAME_NOREPLACE can't be
   employed together with RENAME_EXCHANGE." (snapshot lines 152-153; § ERRORS
   repeats it as an EINVAL case at snapshot line 318.) A staging design that uses
   the no-clobber rename cannot also use the atomic swap in the same call.
3. **`mv --no-copy` is the portable spelling of the same refusal.** (S-NEW-mv1)
   § OPTIONS `--no-copy`: "do not copy if renaming fails" (snapshot lines 90-91).
   Without it GNU `mv` may fall back to copy+remove, which turns a staging move
   into a copy the lane cannot verify atomically. The option is present in the
   installed binary: `/usr/bin/mv --help | grep -n -E 'no-copy|exchange|no-clobber'`
   prints lines 13-14 (`--exchange`), 19 (`-n, --no-clobber`) and 22 (`--no-copy`)
   on GNU coreutils 9.12-2. (A bare `mv --version` in this harness's shell reports
   a builtin, `mv 0.8.0`; name the binary.)
4. **The fleet side was measured once, by another lane, and is vendored here.**
   The probe calls `renameat2(AT_FDCWD, a, AT_FDCWD, b, RENAME_NOREPLACE)` through
   `ctypes` (`libc.renameat2.argtypes`, `RENAME_NOREPLACE = 1`) and runs three
   steps per directory: rename onto a non-existent target, rename onto an existing
   target with the flag, then a plain `renameat2(..., 0)` onto that same existing
   target. It derives each filesystem type with `stat -f -c %T` and prints
   `platform.release()`. Its five rows are counted in the next section.

## The fleet measurement (vendored output, read this round, not re-executed)

`census/round-22/attempt2/sources/vendor-noreplace-probe.out` is byte-identical to
the shokuknow payload output `lanes/souji/round2/evidence/noreplace-probe.out`:
both are `sha256 1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5`
(`sha256sum` over both paths; `cmp` exits 0). The five rows are:

```
/var/tmp	fstype=btrfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
/home/vgpnk/Projects/shokunin	fstype=btrfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
/home/vgpnk/Projects/shokuknow	fstype=btrfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
/dev/shm	fstype=tmpfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
/tmp	fstype=xfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
kernel: 7.2.11-arch1-1
```

- Five device rows: `awk -F'\t' 'NF>1 && $2 ~ /^fstype=/{n++} END{print n}'
  census/round-22/attempt2/sources/vendor-noreplace-probe.out` prints `5`.
- Five successes on a free target: `grep -c 'NOREPLACE_new=0(ok)' …` prints `5`.
- Five refusals on an occupied target: `grep -c 'NOREPLACE_existing=-1(EEXIST)' …`
  prints `5`.
- Five plain overwrites: `grep -c 'plain_overwrite=0(ok)' …` prints `5`.
- Three filesystems: btrfs ×3, tmpfs ×1, xfs ×1. All three are on the man page's
  supported list (btrfs and tmpfs since 3.17, xfs since 4.0), so the measurement
  agrees with the documented schedule rather than extending it.
- The plain-overwrite column is the control: the same call with flags 0 succeeds on
  the same occupied target, so the `EEXIST` is attributable to the flag and not to
  the harness.
- One of the btrfs rows is the mount this lane's repository tree sits under
  (`/home/vgpnk/Projects/shokunin`). That is a statement about that mount on
  2026-10-23 — not about the repository, not about a container root, and not about
  any mount added later.

Point-in-time: five directories, one kernel (the output's `kernel:` line is
7.2.11-arch1-1, the same kernel `uname -r` reported on 2026-10-25), produced
2026-10-23, not re-executed in this lane.

## What this does NOT establish

- **The probe is a point-in-time measurement** of five directories on one kernel.
  A filesystem mounted later, a different mount namespace, or a container with a
  different root could differ. A tool must still degrade explicitly rather than
  assume the flag.
- **`RENAME_NOREPLACE` is not `RENAME_EXCHANGE`**, and the two cannot be combined
  (S-NEW-rename2). Nothing here establishes that an exchange-based staging design
  is available.
- The probe does not test **`RENAME_WHITEOUT`**, overlayfs semantics, or behaviour
  on a filesystem where the flag is unsupported (the expected failure there is
  `EINVAL`, snapshot line 324).
- It says nothing about the **per-item origin record** a staging step would need;
  that is `corpus/knowledge/quarantine-origin-record-fields-r24.md`.
- **This lane did not execute the probe.** Digest equality proves the vendored copy
  holds the same bytes as the shokuknow payload output; it does not prove
  authorship, currency of the mounted filesystems, or reproducibility today.
- **`mv --no-copy` was verified as an option present in the installed binary's
  help, not as exercised behaviour.** This lane ran no refusal case, and the
  cross-device copy fallback the option suppresses is untested here.
- **Re-running the payload probe is not a Q4-conforming fixture run.** It creates
  and unlinks `probe-a`/`probe-b` inside each probed directory, including two live
  repository roots (`/home/vgpnk/Projects/shokunin`,
  `/home/vgpnk/Projects/shokuknow`). This entry reads the recorded output and does
  not re-execute it; a future re-run needs a scratch-only variant.
- **No staging tool is changed by this entry**, and no move or deletion authority
  is created. It removes a precondition question; the operator change and its
  receipts are separate.

## Lane link and consequence

F4's next step named "`mv --no-copy` staging" as an operator tool change. The
blocker was never the semantics — S-NEW-rename2 and S-NEW-mv1 hold those — but
whether the primitive exists on the filesystems the lane works on. On the five
vendored devices it does, and the plain-overwrite control shows the refusal comes
from the flag. So the change can proceed without a degraded path, and what remains
is the record format, not the primitive.

## Gate

url: https://man7.org/linux/man-pages/man2/rename.2.html
snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
opened: 2026-10-25

- ADMIT: "RENAME_NOREPLACE Don't overwrite newpath of the rename. Return an error if newpath already exists." — § DESCRIPTION flags — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "RENAME_NOREPLACE requires support from the underlying filesystem." — § DESCRIPTION flags — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "RENAME_NOREPLACE can't be employed together with RENAME_EXCHANGE." — § DESCRIPTION flags — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "EEXIST flags contains RENAME_NOREPLACE and newpath already exists." — § ERRORS — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "do not copy if renaming fails" — § OPTIONS --no-copy — snapshot: census/round-22/attempt2/sources/man7-mv.1.txt
- REJECT: campaign row `souji/round2/S123` (`.deepresearch/20261024_064146_r9-tierrules/final_turn_001.md` line 118) cites `lanes/souji/round2/evidence/r23-trigger-prune.out` for the git-worktree prune synopsis — reason: this round `grep -c worktree` over that payload prints 0 and no `r23-trigger-prune.sh` exists in that directory, so the row is a wrong-source citation rather than a fact about the payload; flip: re-cite the synopsis against git-worktree(1) and keep the payload for its own PASS lines.
````

## 5. What changed relative to the two parents (source-inferred, both files read in full)

vs the staged original (`shokuknow …/quarantine-staging-no-copy-r23.md`):

1. Ids are placeholders with a documented mapping instead of the campaign's S124/S116/S115.
2. The fleet figure is pinned to the lane's `vendor-noreplace-probe.out` **and** to the
   shokuknow payload, with the digest-identity measurement stated as identity, not re-execution.
3. `verified-at` carries a measured host version (`/usr/bin/mv` 9.12-2, `pacman -Qo`) instead
   of a bare "coreutils 9.12"; the harness-builtin trap is disclosed.
4. The RENAME_EXCHANGE exclusion and the EEXIST error get their own rows (5 ADMITs, not 3).
5. `recheck` is read-only (re-open snapshots/output, re-check the option); the original told
   the reader to re-run a probe that writes into live repo roots.
6. Title narrowed from "every device this fleet uses" to "all five probed devices" — the
   measurement covers 5 directories / 3 filesystems, not the fleet's device set.
7. `## Gate` added (required by the frozen C2 per-entry predicate).
8. Limits kept from the original (point-in-time, EXCHANGE≠NOREPLACE, no WHITEOUT/overlayfs/
   EINVAL-unsupported, nothing about the origin record) plus three this lane owes: the
   probe was not executed here, `mv --no-copy` was not exercised, and the payload probe is
   not a Q4-conforming fixture.

vs the entry already landed at `a211e4d` (`corpus/knowledge/quarantine-staging-no-copy-r23.md`):
same three sources and same vendored digest; my draft adds the host `mv` option measurement,
the EXCHANGE-exclusion and EEXIST rows, a separate fleet-measurement section, the Q4 limit,
and a REJECT row that names the rejected row's file and line instead of describing it. The
landed file's pluralism is otherwise preserved.

## 6. Findings (bounded)

1. **Digest identity, executed.** The lane's vendored probe output and the shokuknow payload
   output are the same bytes (1634d206…bb5, `cmp` exit 0). The probe script's digest
   (11df88f1…739f) is recorded in the draft's first `source:` line.
2. **Counts, executed.** 5 device rows; 5 `NOREPLACE_new=0(ok)`; 5
   `NOREPLACE_existing=-1(EEXIST)`; 5 `plain_overwrite=0(ok)`; 3 btrfs + 1 tmpfs + 1 xfs;
   kernel line 7.2.11-arch1-1 = `uname -r`.
3. **Harness shell shadows `mv` with a builtin (observed, not a lane defect).** `type -a mv`
   → `mv is a shell builtin` then `/usr/bin/mv`; bare `mv --version` → `mv 0.8.0`. Any re-run
   of the version/help receipt must use `/usr/bin/mv`; the earlier `mv 0.8.0` reading in this
   seat's own first probe attempt was the builtin, and is superseded by the `/usr/bin/mv`
   measurement above.
4. **The payload probe is not Q4-conforming.** `noreplace_probe.py` creates and unlinks
   `probe-a`/`probe-b` in each probed directory, including two live repo roots
   (`/home/vgpnk/Projects/shokunin`, `/home/vgpnk/Projects/shokuknow`); Q4 requires a
   `/var/tmp`-only scratch root. This lane reads the output only. A future fixture re-run
   owes a scratch-only variant or an explicit exemption — routed as an observation, not a
   claim in the entry.
5. **Campaign row `souji/round2/S123` is a wrong-source citation (executed check).** The row
   (`.deepresearch/20261024_064146_r9-tierrules/final_turn_001.md:118`) cites
   `lanes/souji/round2/evidence/r23-trigger-prune.out` for
   ``git worktree prune [-n] [-v] [--expire <expire>]``; `grep -c worktree` over that payload
   is 0 and `r23-trigger-prune.sh` is absent from that directory. Used as this entry's REJECT.
6. **The target path is not absent at HEAD.** `git cat-file -e 4edb25d:corpus/knowledge/
   quarantine-staging-no-copy-r23.md` → fatal (absent at base), but the file exists at HEAD
   and was added by `a211e4d` in this attempt. My deliverable is therefore an adaptation/
   delta, not the first draft; if L1 lands this text it replaces a landed file with the same
   three sources. The one substantive difference is the placeholder ids (Finding 7).
7. **Check 5 is the only blocker to landing, and it is mechanical.** Placeholders do not match
   `SOURCE_RE`; S109/S110/S111 already exist and name this entry. Post-repoint simulation of
   the full predicate: `fails [] ok True`.

## 7. Not done / not claimed

- I did not execute the probe, did not run an `mv --no-copy` refusal case, and did not test
  cross-device copy behaviour. Nothing above should be read as those having been measured.
- I did not run `scripts/sources-census.sh validate` (the C2 registry-conformance target) and
  claim nothing about it; that is L1's gate, and no registry row was added or changed here.
- I did not run the C2 counter against the two real entries (my item is one draft); the
  observed `slice_verdicts=8 slice_total=8` comes from the tool's slice pass on the committed
  slice and verdicts TSV, nothing more.
- I did not create, edit, move, delete, or stage any corpus file, and made no git/jj write.
  `git cat-file -e` and `git log` were read-only.
- C1 (declared-evidence calibration) is out of my item and untouched.
- No tool was installed or upgraded; no package manager was invoked. (Read-only commands
  used: coreutils `sha256sum`/`cmp`/`grep`/`awk`/`sed`/`ls`/`uname`, `pacman -Qo`, `python3`.)

## 8. Working-tree state at report time (observed, not mine)

Two files I read were changed by sibling seats while this seat worked; neither change is
mine and neither changes the draft's claims.

- `tools/souji-gate-check.py` is dirty (4 insertions / 4 deletions: `check_slice` stops
  appending `verdict-missing:*` to `fail`, and the partial-verdicts selftest line gains the
  `fail=0` expectation). The tool's `check_entry` is untouched by that diff. Re-running the
  conformance command against the current bytes (`sha256
  f2d18e8273d56467a1af29499241348bcfcf90ccac7729bbd424b90d58fd4331`) gives the identical
  result: `check5-no-source-citation`, `entries=1 ok=0 slice_verdicts=8 slice_total=8 fail=1`.
- `corpus/knowledge/quarantine-staging-no-copy-r23.md` is dirty (12 insertions / 4
  deletions): a sibling narrowed the title to "the five devices this fleet's repositories
  live on" (converging independently with this draft's narrowing), added a "What this entry
  is not" pointer to `corpus/knowledge/quarantine-same-filesystem-rename.md` (S025), and
  added `reason:` strings to the Gate's ADMIT rows. Landing this draft is therefore a
  reconcile, not an overwrite: keep that entry's S025 cross-reference and its ADMIT reason
  strings, and add this draft's EXCHANGE-exclusion row, EEXIST row, host `/usr/bin/mv`
  measurement, separate fleet-measurement section, Q4 limit, and file+line-anchored REJECT.

Touched surfaces: `.ufo/waves/round-22/attempt2/w1/evidence/DraftEntryNoCopy.md` and
`.ufo/waves/round-22/attempt2/w1/DraftEntryNoCopy.md`. Nothing else.

Artifact paths:
- evidence: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/DraftEntryNoCopy.md`
- report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/DraftEntryNoCopy.md`

Report: .ufo/waves/round-22/attempt2/w1/DraftEntryNoCopy.md
