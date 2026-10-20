STATUS: DONE — quote is verbatim (20 words, 6.19/2026-02-08); the recorded anchor ":76-78" is not reproducible (served HTML has it at 78-80) and the S069 row overreaches the exe-only sentence into cwd/fd.

# Reopen S069 — proc_pid_exe(5) deleted annotation

Attacks: C3's only documentation source for the `(deleted)` suffix (round-18 lesson: "C3 on S068, S069"), the SOURCES row that admits S069, and the lesson Gate line that records the quote. Circle to falsify, not to fix lane files.

## Claim under test

- `corpus/lessons/round-18.md:37` @5efb519: quote `"If the pathname has been unlinked, the symbolic link will contain the string ' (deleted)' appended to the original pathname." (§ DESCRIPTION :76-78, 20 words)`.
- `corpus/SOURCES.md:87` @5efb519 (id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by):
  - scope: "the ' (deleted)' suffix on a /proc symlink to an unlinked target; applied to cwd via the kernel's shared d_path, not stated on proc_pid_cwd(5)"
  - anchor: "Linux man-pages 6.19 (2026-02-08), opened 2026-10-20; § DESCRIPTION :76-78; companion proc_pid_cwd(5) has no such sentence"
  - teaches: "a cwd or fd link whose text ends in ' (deleted)' names an unlinked target; the text is ambiguous for a live name ending in ' (deleted)', so the proc census also checks the stripped path"

## Probe (read-only; no lane code executed, no ALLOWED-EXEC item)

```
curl -sS https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html -o s069_exe.html
  # 8377 bytes, sha256 8c9bf02f95a93763ca8bc46a2e165c1c0e173658124e97d4e3d407d0a0b5afdc
curl -sS https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html -o s069_cwd.html
  # 7317 bytes, sha256 c5ec2b4283537f52fd9132e290d8911dc35b891582434f0de54a70488d147f3f
curl -sS -o man-pages-6.19.tar.gz https://mirrors.edge.kernel.org/pub/linux/docs/man-pages/man-pages-6.19.tar.gz
tar -xzf man-pages-6.19.tar.gz man-pages-6.19/man/man5/proc_pid_exe.5
  # 65 lines, sha256 34db09ded0f3dd55e2e84d408d0c7f24119081a6bc3704e849f2899293530419
printf '%s\n' "<quote>" | wc -w        # -> 20
```

Plus `read` ranges on the same URL (`:40-52`, `:72-82`, `:76-78`) and read-only `git show 5efb519:…` for the row, lesson, Q32 and the census. Fetch outputs now retained under `/var/tmp/souji-r18w2-ReopenS069/`; no repo or fleet writes.

## Findings

### 1. Quote — verbatim. AGREE.

Served § DESCRIPTION, first paragraph (raw HTML lines 78-80). Normalized only for the page's hard line wrap (collapse space runs), the lesson string and the served string are **byte-identical** (125 bytes each, `cmp` → IDENTICAL):

```
If the pathname has been unlinked, the symbolic link will contain the string ' (deleted)' appended to the original pathname.
```

ASCII U+0027 apostrophes, one U+0020 space inside the quotes, final period; no non-breaking spaces (`cat -A` showed plain spaces). The pinned roff source confirms the same sentence (`man-pages-6.19/man/man5/proc_pid_exe.5:23-25`, rendered from `\[aq]\ (deleted)\[aq]`).

`wc -w` = **20**; the claimed count is correct.

### 2. Served version / last-updated — AGREE.

- HTML line 123: `Linux man-pages 6.19            2026-02-08                proc_pid_exe(5)` (footer version/date line).
- HTML line 142: `HTML rendering created 2026-09-09`.
- HTML lines 113-116: served from tarball `man-pages-6.19.tar.gz` "fetched … on 2026-09-09".

Row text "Linux man-pages 6.19 (2026-02-08), opened 2026-10-20" is accurate.

### 3. Anchor ":76-78" — DISAGREE.

- Served raw HTML: the quote begins mid-line **78** ("…If the pathname has been"), continues on 79, and ends on **80**. `nl -ba s069_exe.html | sed -n '78,80p'`:
  - 78 `that is being run by process <i>pid</i>.  If the pathname has been`
  - 79 `unlinked, the symbolic link will contain the string`
  - 80 `' (deleted)' appended to the original pathname.  In a`
  Lines 76-78 stop mid-sentence at "If the pathname has been" — 6 of the 20 quoted words; the anchor does not cover the quote.
- man-pages-6.19 roff source: sentence at **23-25**, not 76-78.
- Harness `read` render of the same URL: sentence at **39-41**; `read URL:76-78` returns **COLOPHON body** ("user-space interface documentation) project…"), i.e. the recorded anchor sends a replicator to the wrong place.
- No rendering I can reproduce yields 76-78; the closest is served HTML 78-80. [INFERENCE] Likely a transcription slip (78-80 → 76-78). Sibling man7 rows cite sections only (S066 "§ DESCRIPTION", S068 field numbers, S070 "§ ERRORS"); S064's line span is on a tag-pinned source file. S069's span is renderer-dependent and pinned to no artifact digest.

Second claim in the anchor cell, "companion proc_pid_cwd(5) has no such sentence" — **AGREE**: the 6.19 cwd page contains 0 occurrences of `deleted` and 0 of `unlink`; its DESCRIPTION documents only the link, the pthread caveat and the ptrace gate.

### 4. Scope cell — overreach.

- The source sentence governs `/proc/pid/exe` only ("this file is a symbolic link containing the actual pathname of the executed command"; "the symbolic link"). The cell widens it to "a /proc symlink", which the quote does not state.
- "via the kernel's shared d_path" is a kernel-internals mechanism absent from the source. `git grep d_path 5efb519 -- corpus` finds no S-row grounding it; the registry nowhere else supports that mechanism. The row is `docs` / tier `A` / `mined`, so the cell reads as sourced.
- The disclosure "(…not stated on proc_pid_cwd(5))" is true, but it sits inside the supported half of the "X; not Y" scope convention used by sibling rows (cf. S068) and does not ground the mechanism or the cwd application. Soft overreach: labelled, but still asserted as mined.

### 5. Teaches cell — overreach plus an implementation overstatement.

- "a cwd or fd link" extends the exe-only sentence to two other links.
- Internal contradiction: if the text is ambiguous "for a live name ending in ' (deleted)'", then the text does not reliably "name an unlinked target"; the first clause is not guaranteed.
- Census check at 5efb519: `tools/souji-proc-census.sh:326-327` reads the cwd link and sets `reason='cwd-deleted'` on the suffix alone — **no suffix strip, no stripped-path test**. Only `find_deleted_fd_path` (`:242-255`) strips (`target=${fd_link%' (deleted)'}`) and requires `top_level_scratch_gone` (`:162-176`, `[[ ! -e $TOP_LEVEL_PATH ]]`; top-level-directory granularity, not exact target).
- Therefore "the proc census also checks the stripped path" is **false for the cwd branch**, which produces the primary `cwd-deleted` reason in C3's claimed ordering. Consequence: a live cwd literally named `… (deleted)` is listed as residue. No fixture covers that case (r18-proc-census.sh P1-P11: P9 deleted stdout fd, P10 nested argv boundary; no live-name-with-suffix case), and the census selftest exercises only a genuinely deleted cwd (`:462-465`).

## Verdict

**PARTIAL — agree on the quote, disagree on the row.**

- AGREE: quote verbatim (byte-identical), 20 words, 6.19/2026-02-08, companion-cwd-page claim true.
- DISAGREE: `:76-78` is wrong/unreproducible (served HTML 78-80; roff 23-25; `read` render 39-41; `read URL:76-78` is COLOPHON). Scope and teaches overreach the exe-only sentence into cwd/fd and into an unsourced `d_path` mechanism. The teaches cell's "checks the stripped path" does not hold for the cwd branch.
- C3's behavioural claim is not falsified here (the suffix does appear on a deleted cwd and the matrix numbers stand as observed), but its cited grounding does not cover cwd/fd, and one recorded implementation claim is inaccurate. Calibration: an A-tier `mined` row should not carry an inference and an unverified implementation claim in its supported cells.

## Smallest fix (doc-only; lane files not touched)

1. `corpus/SOURCES.md:87` anchor → drop the renderer-dependent span, e.g. `§ DESCRIPTION para 1 (served HTML 78-80, sha256 8c9bf02f…; man-pages-6.19 roff 23-25, sha256 34db09de…)`; keep the companion sentence.
2. `corpus/SOURCES.md:87` scope → "the ' (deleted)' suffix on /proc/pid/exe's symlink when the executable pathname is unlinked; cwd/fd use is an inference from shared kernel d_path, not stated in proc_pid_cwd(5), and no S-row grounds d_path."
3. `corpus/SOURCES.md:87` teaches → keep the exe statement, mark cwd/fd as inference, and replace the census clause with "the fd branch strips the suffix and requires the top-level directory gone; the cwd branch is suffix-only (`tools/souji-proc-census.sh:326-327`)".
4. `corpus/lessons/round-18.md:37` → `:78-80 (served HTML)` or remove the line span, as S066/S068/S070 do.
5. Adjacent: `corpus/QUALITY.md:81` (Q32) attributes the cwd suffix to S069 — same extension; add "(inference)" or point at the corrected anchor. The code gap (cwd stripped-path test) is outside this doc scope; route to the census owner.

Tooling record: no installs/upgrades (curl, tar, zcat preinstalled). No lane code run, no git/jj writes, no signalling.
