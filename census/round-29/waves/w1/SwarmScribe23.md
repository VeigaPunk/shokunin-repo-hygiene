## Status

STATUS: PASS — the F3 identity entry is drafted at the assigned delivery path, with all three sources opened live this run, every Gate quote copied from those bytes, and `souji-gate-check.py` returning `entries=1 ok=1 fail=0` over those exact snapshot bytes in a scratch root. Remaining work is landing (snapshots, SOURCES rows S216-S218, slice/verdicts), which is the L1's scope and is itemised in Findings.

## Evidence

Lane revision: HEAD `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (preregistration freeze), lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, branch master. Contract read first: `census/round-29/records/preregistration.txt` (C1/C2/C3, counters, kill rules, controls, Q59).

1. Sources fetched by me this run (scratch `/var/tmp/souji-r29-SwarmScribe23.JfYRWr`, since removed):
   `curl -fsSL -o statx.2.html https://man7.org/linux/man-pages/man2/statx.2.html` and the same for `link.2.html` and the Broder PDF at `https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf`, then `pdftotext broder97resemblance.pdf broder97resemblance.txt`.
   `sha256sum` output:
   `2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e  statx.2.html`
   `9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9  link.2.html`
   `da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b  broder97resemblance.pdf`
   `3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d  broder97resemblance.txt` (plain `pdftotext`, no flags)
   Editions read from the pages themselves: statx footline `Linux man-pages 6.19  2026-02-08` (statx.2.html:587), link footline `Linux man-pages 6.19  2026-02-11` (link.2.html:310).

2. DOI probe (task said 202/0; re-measured, not assumed):
   `curl -sS -o /dev/null -w 'status=%{http_code} size=%{size_download}' -L https://doi.org/10.1109/SEQUEN.1997.666900` → `DOI status=202 size=0 final=https://ieeexplore.ieee.org/document/666900/`. Recorded in the S217 source line as the reason the Princeton mirror is the opened edition.

3. Quote check before writing: 16 candidate spans tested against whitespace-collapsed bytes of the three files with `re.sub(r'\s+',' ',…)`. 15 matched; 1 did not — `STATX_MNT_ID_UNIQUE Want unique stx_mnt_id (since Linux 6.8)` fails inside the HTML because `</b>` sits between the constant and the text (statx.2.html:257), so the delivered quote starts after the tag: `Want unique stx_mnt_id (since Linux 6.8)`.

4. Gate verification over the same bytes, in a scratch root (`$R` = `/var/tmp/souji-r29-SwarmScribe23.JfYRWr/probe`, sources copied to `$R/census/round-29/sources/`, stub `$R/corpus/SOURCES.md` rows S216-S219, empty slice/verdicts):
   `python3 -B tools/souji-gate-check.py --root "$R" --round-date 2026-10-25 --entries entries/entry.md --snapshot-dir census/round-29/sources --slice census/slice --slice-verdicts census/verdicts.tsv`
   → `entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0`, rc 0. Local audit of the delivered Gate: 14 quotes, max 23 words, 0 containing `|`.

5. Same command at the lane root, to characterise what landing still needs:
   `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries .ufo/waves/round-29/w1/deliver-entry-identity.md --snapshot-dir census/round-29/sources --slice census/round-29/records/slice --slice-verdicts census/round-29/records/slice-verdicts.tsv`
   → `entries=1 ok=0 … fail=19`, rc 1: `check4-snapshot-missing-line-{8,8,9,9,10,11,12,13,14,15,16,17,18,19}`, `check3-no-located-quote-with-snapshot`, `check5-dangling-source: S216/S217/S218`, `slice slice-missing`.

6. Recheck command exercised verbatim (it is the one in the entry's `recheck:` line):
   `bash -c '… mktemp -d /var/tmp/souji-r29-recheck.XXXXXX; curl …; pdftotext …; sha256sum …; curl … doi; rm -r $d'` → the four hashes from Evidence 1 in order, then `doi 202 0`. Wall time 3.07 s.

7. C3 baseline measured at the committed tip, not quoted from the preregistration:
   `git grep -l '^ground: F3' HEAD -- corpus/knowledge/ | wc -l` → `0`; `git show HEAD:corpus/SOURCES.md | grep -c '^| S[0-9]'` → `139`; rows S216-S219 absent (`grep -n 'S216\|S217\|S218\|S219' corpus/SOURCES.md` → no output; last row is S215).

## Findings

1. **Staged front matter would have cited the wrong ids and an unusable locator.** The staged package (`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/duplicate-verdict-identity.md`) names S117/S118/S122 and the DOI URL. Re-grounded to S216 (statx), S217 (Broder), S218 (link); the DOI answers 202 with a zero-byte body (Evidence 2), so it cannot carry a located quote and the Princeton PDF mirror is the admitted edition. Location: staged file front matter vs delivered entry front matter.

2. **Staged closing sentence cites a file that does not exist.** It ends "… recorded in `CANNOT-ANSWER.md`."; `ls CANNOT-ANSWER.md` at lane root → `No such file or directory` (also no match under any name outside `.jj`). Refused in the delivered Gate's REJECT line. Location: staged file, last sentence; lane root at b8cb4b3.

3. **The staged btime caveat is not grounded on the page as worded.** The staging says the man page "marks other fields with 'support varies by filesystem'". That tag exists only for `STATX_DIOALIGN`, `STATX_SUBVOL`, `STATX_WRITE_ATOMIC`, `STATX_DIO_READ_ALIGN` (statx.2.html:256, :259, :264, :266); `btime` appears only at :106 (struct), :251-:252 (constants, the second inside `STATX_ALL`) and :355 (description), none of which carries that tag. The correct grounding for btime unavailability is the general mask clause at :289-295 — "If a filesystem does not support a field or if it has an unrepresentable value … the mask bit corresponding to that field will be cleared". The entry states it that way, quoted. Location: `census/round-29/sources/statx.2.html` (to be landed).

4. **The staged Broder clustering sentence was locatable, so it was admitted, not rejected.** `We calculated our clusters based on a 50% resemblance` and `a mixture of exact duplicates and similar` sit at broder97resemblance.txt:54-55 and :58; the two-population reading is quoted, not paraphrased. Location: snapshot `census/round-29/sources/broder97resemblance.txt` (decode sha256 3ba1e117…).

5. **Snapshot prerequisites are absent and must be landed for the Gate to verify.** `census/round-29/sources/` does not exist on disk and is not in the HEAD tree (`git ls-tree -r --name-only HEAD census/round-29/` lists only `c2-counter.py`, `controls.sh`, `stale-statements.tsv`, `records/*`); wave-evidence capture at the final tip is C2's job. The L1 must commit these exact bytes at these paths: `census/round-29/sources/statx.2.html` (2a47fe31…), `link.2.html` (9cb197a7…), `broder97resemblance.txt` (3ba1e11…, produced by plain `pdftotext <pdf> <txt>`; the PDF itself is da122799… if also kept). With them plus rows S216-S218, Evidence 4's green result transfers to the lane root; without them it fails exactly as in Evidence 5.

6. **Rows S216-S219 do not exist yet.** `corpus/SOURCES.md` ends at S215 (139 rows). C1's K1 later requires each cited id's `used-by` to name the landing path `corpus/knowledge/duplicate-verdict-identity.md`, so the row text and the entry must land together. This seat cannot write the registry.

7. **A sibling already delivered the same entry under a different filename.** `.ufo/waves/round-29/w1/deliver-duplicate-verdict-identity.md` exists (5797 B, 21:43) and independently records the same three URLs and the same three HTTP sha256s plus the same plain-pdftotext decode hash 3ba1e117… — two independent fetches agreeing, which I treat as corroboration, not as my evidence. My assigned path is `deliver-entry-identity.md`. They are not identical: the sibling has no separate `## Lane link` heading (the assigned shape requires one) and it rejects two unrelated staged files instead of the staged wording. The L1 should land exactly one entry from these two drafts.

8. **One claim is labelled `[INFERENCE]` in the entry by design.** The equation of the lane's existing `stat -c '%d:%i'` guard with statx's (device, inode) pair is labelled inference because stat(1) was not opened this run; the two halves are quote-backed separately (statx :97 `stx_ino` and :366 device description; the guard's existence is in `corpus/knowledge/dupe-finders-detect-then-act.md`, read this run).

9. **The lane working tree carries one modification that is not mine.** `git status --porcelain` at the end of this seat reports exactly one entry, ` M .ufo/waves/round-26/w1/ScribeGateDraft.md`. This seat wrote no tracked file; both deliveries are ignored by `.gitignore:1:.ufo/waves/`. The modification is recorded for the jar's provenance, not acted on.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-entry-identity.md` — the entry draft (103 lines; front matter S216/S217/S218 with URL, section anchors and editions; `verified-at: 2026-10-25`; `recheck: 365d` with the exercised command; `ground: F3 — duplicate verdicts`; sections Claim, What this does NOT establish, Lane link, Gate).
- `.ufo/waves/round-29/w1/SwarmScribe23.md` — this report.

Out of scope for this seat (L1): landing the entry, the three snapshots, SOURCES rows S216-S219, the assimilation slice/verdicts, `corpus/lessons/round-29.md` and any commit. No files were written outside `.ufo/waves/round-29/w1/`; nothing outside `souji-shokunin/` was touched; scratch removed. No tools installed. No subagents dispatched.
