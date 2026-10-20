# BoundaryReviewCompare: round 14 w1, C2 `--compare`

Seat: SoujiR14.BoundaryReviewCompare (reviewer, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Target: /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh (827 lines, read snapshot tag #5156).
Scope: `--compare` direct, alias and stdin input interactions; malformed-baseline ordering; whether any input file access can read credentials.

## Evidence status
- Exercised evidence: none. The seat ran no commands and no builds, tests, or fixtures.
- Code inspection: all findings below come from reading tools/souji-census.sh and the round-14 w1-spec.json entry for CensusBoundary (CensusBoundary requires a compare-alias isolation test).
- `[INFERENCE]` marks behavior derived from bash, coreutils, and `test` semantics that has not been observed.
- Real credential paths, the operator-sweep directories, and live census were not touched.
- Tools installed or upgraded by this seat: none.

## Current ordering, as coded
1. Flag loop, lines 797-814. `--compare` needs a following argument (805-807). An empty value is accepted. `--compare=` (808) is accepted the same way.
2. `--selftest`, line 816. Exits before `--compare` is looked at, so a combined `--selftest --compare X` silently ignores the baseline.
3. git and du presence checks, lines 818-819.
4. `if [ -n "$COMPARE" ]`, line 821. Empty COMPARE falls through to a plain census.
5. emit_compare, lines 415-416: `load_census "$COMPARE"`. Inside: `[ -f "$file" ]` at 365, read loop 367-385, header check 370-375, row checks 377-384 (empty repo, duplicate repo only).
6. `mktemp` at 418, then `emit_census > "$tmp"` at 419. Root directory check at 345-346, enumeration via `list_repos` at 352 and 316-341.
7. Diff at 423-464, exit 3 at 466.

No stage canonicalizes COMPARE, checks it against a credential boundary, checks its basename, checks its link count, or checks readability. The guard that the spec requires for compare alias does not exist yet.

## Findings

### F1. HIGH (operability/calibration). An empty `--compare` silently becomes a plain census with exit 0
- Lines 806-807 accept `--compare ""`. Line 808 accepts `--compare=`. Line 821 tests `[ -n "$COMPARE" ]`, which is false for empty. Line 822 is skipped and emit_census prints a census TSV with exit 0.
- A wrapper whose baseline variable is unset therefore receives a non-diff document and exit 0, which looks like a clean compare to a caller that checks only the exit code.
- Fix: record presence with `COMPARE_SET=1`. Reject an empty value with usage_err (exit 2) before anything else.

### F2. HIGH (C2 boundary). `--compare` reads any path with no credential or alias guard
- Line 365 `[ -f "$file" ]` and line 385 `done < "$file"` use the raw string. No `canon_path` (line 95) is applied. Symlinks are followed (`-f` and `<` both follow them).
- No link-count check. A hardlink to a credential file passes name and canonical checks [INFERENCE: same-filesystem constraint; same class as round-13 SafetyPaths SP-G3].
- No secret-shaped basename or component check. The `secret_comp` rules at 170-178 apply only to census file listing, not to the baseline.
- No refusal of census/operator-sweep-* paths, although the round Goal forbids operator-sweep access.
- Content is read before any refusal could apply. At minimum the first line is read at 367 before the header check at 371. If the header matches, every line is read and repo/field values are echoed to stdout (438, 443, 459-461).
- The header comment at 4-5 ("never reads secret-shaped files") is false for the `--compare` path.
- Required: a guard in main, before the emit_compare branch and before the `[ -f ]` at 365. It must do lexical and canonical (`readlink -m`, plus `readlink -f` for existing links) checks against the credential store. For COMPARE it must also refuse: symlinks whose target is inside the store, `st_nlink != 1` [`stat -c %h`], secret-shaped components, census/operator-sweep-* paths, non-regular files, and unreadable files. The spec's compare-alias isolation case depends on this.

### F3. MEDIUM (malformed-baseline ordering). Only the header is validated; data rows are not
- Lines 377-384 check only an empty repo and duplicate repos. There is no column-count check, no numeric check on worktrees, unpushed, dirty, or scratch_bytes, and no check on mtime_iso or verdict tokens.
- `field_at` (389-401) has a side effect. When no tab remains, `rest=${rest#*$'\t'}` leaves `rest` unchanged, so a short row returns the same value for fields 2-6. A truncated row therefore produces spurious diffs with exit 3, not exit 2. Corrupt baseline is classed as drift.
- The comment at 358-361 says a "malformed" baseline is a hard error. That is true only for the header.
- Silent no-diff risk: none found. Census fields cannot contain tabs (`sanitize_field`, 97-103), so an identical `rest` implies a well-formed row.
- Fix: after the header, validate every non-blank row: exactly 6 tabs, `^[0-9]+$` for the four numeric columns, mtime_iso empty or ISO-8601, verdict tokens from the documented set. Report the line number and exit 2. Do this before `mktemp` (418).

### F4. MEDIUM (operability). Usage text is printed to stdout, which is the compare channel
- `usage()` (88-91) runs `sed -n '2,68p' "$SELF" | sed ...` with no redirect, so help goes to stdout. `usage_err` (93) calls it. All load_census errors (365, 372, 380, 382, 386) therefore emit about 68 lines of help on stdout before exit 2.
- A consumer that parses stdout as diff TSV receives help text, not an error it can classify.
- Usage text on line 9 (rendered via 89) names `tools/souji-census.impl-33.sh`. The real script is `tools/souji-census.sh`.
- Fix: send usage to stderr (`>&2`), and omit the help block for baseline errors.

### F5. MEDIUM (operability/doc). Temp file leaks on compare failure; header claim contradicted
- Lines 418-421: `mktemp` creates a file, then `emit_census` runs in the same shell. Its `exit 1` (346) or any `set -e` failure exits before `rm -f` (421). There is no trap.
- Example: `--root <nonexistent> --compare <valid>` leaves an empty `souji-census-now.*` in `${TMPDIR:-/tmp}`.
- The header at 4-5 says the tool "never writes outside a --selftest mktemp". The compare path violates that.
- Fix: check the root before `mktemp`, and add a cleanup trap. Alternatively, keep the census in a variable and avoid the file entirely.

### F6. LOW-MEDIUM (exit contract). Unreadable baseline exits 1, not 2 [INFERENCE]
- Line 365 tests existence only. If the file exists but is unreadable, the redirect at 385 fails. Under `set -e` that is a shell redirection error with exit 1 and a raw bash message, not the documented exit 2 path.
- Fix: `[ -r "$file" ] || usage_err "compare file not readable: $file"`.

### F7. LOW (stdin and pipes). Pipes and stdin are rejected with a misleading message
- `-` is not special. `/dev/stdin` fed by a pipe, and `<(...)` process substitution, are FIFOs, so `-f` is false and the script exits 2 with "compare file not found" although the file exists.
- A regular file redirected into stdin is accepted through `/dev/stdin` [INFERENCE].
- No hang on pipes, because `-f` runs before the open.
- TOCTOU, low: if the path is swapped to a FIFO between 365 and 385, the open blocks [INFERENCE].
- Fix: either reject explicitly ("compare baseline must be a regular file; stdin and pipes are refused") or support stdin explicitly. Prefer rejection, since the round does not need stdin. Open the fd once and test that fd to close the race.

### F8. LOW (operability). Silent last-wins and silent ignores
- Repeated `--compare` (805-807) or `--root` (801-803) silently keeps the last value.
- `--selftest` with `--compare` exits at 816 and ignores the baseline without a message.
- Fix: reject duplicates, and reject `--selftest` combined with `--compare`, with usage_err.

### F9. LOW (calibration). Compare output echoes baseline-derived strings
- Lines 438, 443, and 459-461 print repo keys and before-values taken from the baseline.
- Safe today only because the header must match first. Once F2 is in place this is bounded. Consider printing only census-side values or validated fields.

## Checked, no defect found
- CRLF header accepted (369).
- Blank lines after the header are skipped (377).
- Empty, blank-led, blank-before-header, and bad-header baselines all exit 2 (370-375, 386).
- Duplicate repos exit 2 (381-383).
- Exit 3 survives `set -e` at 822.
- Keys match across alias roots: both baseline and census keys are canonical (`canon_path` at 245 and 345).
- COMPARE is only read, never written, so there is no truncate-alias hazard between the baseline and the temp file.
- A FIFO baseline does not hang, because `-f` at 365 is checked first.

## Proposed ordering for CensusBoundary to implement
1. Flags: reject empty, duplicate, and `--selftest`+`--compare` (F1, F8).
2. Boundary guard for ROOT and COMPARE, lexical and canonical, before any read or enumeration. COMPARE also gets basename/component secret-shape, operator-sweep, link-count, regular-file, and readability checks (F2, F6, F7).
3. Baseline load with full row validation (F3). Usage errors go to stderr only (F4).
4. Root directory check, then root boundary guard, then `list_repos` (320, 324, 352). The guard must precede enumeration.
5. `mktemp` with cleanup (F5).
6. Census, diff, exit codes.

## Final L1 commands (seats do not run these)
All fixtures use synthetic paths under /var/tmp, with HOME overridden. No real credential path, operator-sweep path, or live census is touched.
- `bash -n /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh`
- `shellcheck /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh`. If absent, install with `sudo pacman -S --needed --noconfirm shellcheck` and record the version and reason.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh --selftest`
- Fixture per spec: `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh`, with a synthetic HOME under /var/tmp.
- Empty-compare regression. Expect exit 2 and empty stdout after the F1 fix. Current behavior is exit 0 with a census TSV: `--root /var/tmp/<synthetic> --compare ""; echo $?`
- Stdout purity on malformed baseline. Expect 0 bytes on stdout after the F4 fix: `--compare /var/tmp/<bad>.tsv 2>/dev/null | wc -c`
- Unreadable baseline (`chmod 000` on a /var/tmp file). Expect exit 2 after the F6 fix.
- FIFO baseline: `mkfifo /var/tmp/<x>.fifo; timeout 5 <tool> --compare /var/tmp/<x>.fifo; echo $?`. Expect exit 2 quickly.
- Symlink and hardlink to a synthetic "credential" file under /var/tmp/<fake-home>. Expect refusal after the F2 fix.
- Temp leak: `--root /var/tmp/<nonexistent> --compare <valid>`, then `ls ${TMPDIR:-/tmp}/souji-census-now.*`. Expect nothing after the F5 fix.
- Short row and 8-column row baselines. Expect exit 2 after the F3 fix.
- The existing selftest malformed-baseline block (756-769) does not cover missing file, unreadable file, FIFO, short rows, or wide rows. Add those cases to the fixture.

## Exit codes (current and as-found)
- 0: census, or compare with no change. Note: empty `--compare` also exits 0 today (F1).
- 1: root not a directory; git or du missing; unreadable baseline [INFERENCE] (F6).
- 2: usage error; baseline missing, header bad, empty repo, duplicate repo.
- 3: compare with at least one changed row.

## Residual risk and gaps
- Hardlinks and bind mounts cannot be detected lexically. F2's link-count check covers only the baseline file. Root-side mount aliasing is out of this seat's slice.
- The TOCTOU in F7 is low but real. The fix is to open once.
- Line citations are against snapshot #5156. Re-read before editing.

## Post-landing re-review of C2 compare path (static parse only; nothing executed)

Re-read tools/souji-census.sh as landed (1458 lines). Status against F1-F9:

- F1 empty --compare: FIXED. COMPARE_SET at 1430-1431; `--compare ""` and `--compare=` rejected by usage_err at 1442-1443, exit 2, before any guard or git.
- F2 credential/alias guard: FIXED for --compare. guard_path runs at 926 before `[ -f ]`, and again in main at 1447. The resolved path is what -f, -r, stat and the read use. Symlink hops are walked (353-370). nlink>1 is refused (938-942). Residual: resolve-then-open is not atomic, as CensusBoundary states.
- F3 row validation: FIXED for tab count (955-959) and numeric columns 2-5 (963-968). Columns 6 (mtime_iso) and 7 (verdict_flags) are not validated. LOW residual.
- F4 usage to stderr: FIXED (usage_err at 139 writes usage to stderr).
- F5 temp leak and root-before-mktemp: FIXED. Root guarded at 1005-1006 before mktemp at 1008; trap at 1009; cleanup at 1012-1014.
- F6 unreadable baseline: FIXED (932, exit 2).
- F7 pipes and stdin: PARTIAL. /dev/stdin and /dev/fd/* resolve through /proc and are refused with an explicit message (927-929). A named FIFO path and `--compare -` still reach "compare file not found" (931), exit 2, no hang, but the message is misleading. The open-once TOCTOU fix is not implemented.
- F8 repeated flags and --selftest+--compare: NOT FIXED. Repeated --compare/--root remain last-wins. `--selftest --compare X` still exits at 1439 and silently ignores the baseline.
- F9 echoed baseline strings: PARTIAL. Numeric fields are now validated. The baseline repo key is still raw text; the census side is canonical. A baseline key naming a protected path is echoed as a string and never opened. Cosmetic residual.

New observations:

- N1 pin stale: CensusBoundary.md pins tools/souji-census.sh at 1453 lines. The file as read has 1458 lines (last line `exit 0`). I did not verify the sha256 (no execution). L1 must re-pin after confirming the hash.
- N2 ordering confirmed: the baseline is loaded at 1007 before mktemp and before any census enumeration. Stdout is empty until both loads finish; the diff header is printed at 1016. A malformed baseline therefore never triggers git, find or du.
- N3 set -e propagation: guard_path results are assigned with plain `x=$(...)` after a separate `local x` declaration (924/926, 1004/1005, 382/384), so a protected_fail exit 2 inside the substitution is not masked.
- N4 key canonicalization: a baseline written with a symlinked root spelling gives added/removed rows and exit 3 (drift), not a silent pass. Low.

Final L1 checks for the compare path, in addition to CensusBoundary's list (synthetic /var/tmp paths, HOME overridden):

- `--compare ""` expects exit 2 and empty stdout.
- `--compare /dev/stdin` fed from a pipe, and `--compare /dev/fd/0`, expect exit 2 quickly with stdout empty. Run with `timeout 5`.
- A named FIFO under /var/tmp with `timeout 5` expects exit 2, with stdout empty.
- A hardlinked synthetic baseline expects exit 2 with `hardlinked-compare`.
- A baseline with a 5-column row and a non-numeric worktrees value expects exit 2, with stdout empty.
- `--selftest --compare <file>` documents the F8 residual. Expect it to be silent, so the check should record it as known rather than pass it.
