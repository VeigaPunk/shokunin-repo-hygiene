# ReopenFdAccess — round-20 final source falsifier (S095, S090)

Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Every corpus read is a `git show` blob at the pin; no working-tree copy was read. Axes: (a) page quote and version fidelity, (b) page-fact versus lane-policy separation, (c) S090 retained-record provenance. Read-only, report only, no registry or lane edits, leaf seat with no dispatch. Author-side advisory; not non-author closure or promotion.

**Verdict.** No blocking finding, so no partial marker is used.

- **S095 — agree on page facts, disagree on one teaches clause.** Access date, version, located quote, anchor and tier agree with the page. The teaches cell carries one lane-policy clause ("this does not authorize a private-value probe or a signal"). The lane's own S086–S088 removed clauses of that kind from teaches cells. Non-blocking correction.
- **S090 — agree that the reject and its flip are retained, consistent and not backdated.** Its basis duplicates S032 (same URL, same refusal ground), and its flip differs from S032's. I did not re-verify the WARNING text, because its URL is not named in this item.

## 1. Primary page record (exact URL)

| Field | Observed |
|---|---|
| URL | https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html |
| Access date | 2026-10-21 (UTC) |
| Fetch modes | reader text and `:raw` HTML; the DESCRIPTION permission paragraph is identical in both |
| Actual version | Linux man-pages 6.19; footline date 2026-02-08 |
| Colophon and render | from man-pages-6.19.tar.gz, fetched 2026-09-09; HTML rendering created 2026-09-09 |
| Located quote (21 words) | "Permission to dereference or read (readlink(2)) the symbolic links in this directory is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check" |
| Quote location | DESCRIPTION, the paragraph beginning "Permission to dereference" (after the /dev/stdin example) |
| Companion quote (16 words) | "those inodes still have permission bits and ownership information distinct from those of the /proc/pid/fd entry" |
| Companion location | DESCRIPTION, the paragraph beginning "Note that for file descriptors referring to inodes" |

The page's example commands were read as text only; none were executed. The page's only "signal" token is `signalfd(2)` in the anon_inode list. The page has no probe or signalling guidance.

## 2. S095: registry and Gate against the page

Pinned SOURCES row S095: tier A; kind docs; status mined; opened 2026-10-21; recheck on-release; used-by `corpus/knowledge/process-residue-observations.md`, `corpus/lessons/round-20.md` (SOURCES line 115).

Pinned Gate row (round-20.md line 44): URL exact; "man-pages6.19 (2026-02-08)"; quote as in §1; decision "admit/mined: fd-link access-mode attribution, not private-content or signal authority".

| Check | Verdict | Basis |
|---|---|---|
| URL | agree | exact in both files |
| Version and date | agree | 6.19 and 2026-02-08 match the footline |
| Anchor | agree | paragraph located as described |
| Gate quote exact | agree | substring present once; 21 words; ASCII; no hidden or special-space codepoints in either file (byte census) |
| Teaches, page clause ("dereferencing or reading these symbolic links is governed by a PTRACE_MODE_READ_FSCREDS ptrace access-mode check") | agree | paraphrase of the page sentence |
| Teaches, policy clause ("this does not authorize a private-value probe or a signal") | **disagree (non-blocking)** | Lane policy, not page text. The page says nothing about probing or signalling. S086, S087 and S088 (all opened 2026-10-21) each removed the same kind of lane-policy clause from a teaches cell ("is lane inference, not page text, and is removed from the row"). S095 reintroduces the pattern. The clause belongs in scope, where the row already limits its use, or in the Gate decision column, which already says "not private-content or signal authority". |
| Scope, "permission to read or dereference fd symlinks" | agree | page sentence |
| Scope, "not permission to inspect arbitrary process contents" | lane limitation; label it as such | The page confines its rule to these links, and "process contents" appears nowhere on it. The companion paragraph (inodes keep their own permission bits) supports a narrow reading, not this exact phrase. |
| Gate decision, "not private-content or signal authority" | lane policy, correctly placed | decision column, not quotation |
| Used-by knowledge entry | not verified | path exists at the pin; contents not opened (outside named scope) |
| Tier A | as recorded | SOURCES-CONTRACT-v1 not opened (outside named scope) |

Gate typography (non-blocking): "man-pages6.19" and "at most25 words" lack a space. The byte census found no hidden characters, so these are literal omissions. The quote itself is unaffected.

Primary facts versus lane policy for S095:
- **Page:** dereferencing or reading these links is governed by a PTRACE_MODE_READ_FSCREDS check (see ptrace(2)). Inode entries keep their own permission bits and ownership. A link can be dereferenced while the inode behind it is denied; the page gives this as an example, which I did not execute.
- **Lane:** the probe and signal non-authorization, the "process contents" limitation, the F5 knowledge mapping, recheck and used-by.

## 3. S090: retained reject and flip

| Record | SOURCES row (line 110) | Gate row (round-20.md line 39) | Verdict |
|---|---|---|---|
| Status | rejected | "reject" | agree |
| Tier / opened / recheck | A / 2026-10-21 / on-release | 2026-10-21 | agree |
| Scope | rejection of history rewrite as Souji cleanup authority, not a replacement-tool endorsement | reject as Souji cleanup/history-rewrite authority | agree |
| Flip | an operator separately scopes history work to its owner, never a Souji cleanup receipt | flip only through separately scoped operator history work to its owner, never a cleanup receipt | agree (both phrases byte-present) |
| Quote | teaches paraphrases "does not recommend this tool" | "its use is not recommended." | agree in substance; **page text not re-verified** (URL not named in this item) |
| Search log (SOURCES line 139) | "rejected 1 cleanup-authority candidate (S090)" | none | agree |

Provenance: S090 appears only in round-20 content (SOURCES lines 110 and 139; round-20.md lines 39, 46 and 50), all dated 2026-10-21. It is not an invented historical reject. The round-19 catalogue gap is disclosed in the lesson and was not backfilled.

Calibration notes (non-blocking):
1. S090 uses the same URL as S032 (git-filter-branch, rejected 2026-10-19 in round 12), with the same refusal basis (PROVINCE.md § Refuses). It is a scoped re-decision, not independent new page evidence.
2. The two flips differ. S032 needs the page to drop the WARNING and the operator to take on history work. S090 needs only operator scoping, which no page change can trigger, so its on-release recheck cannot flip it. Both rows coexist without a precedence statement.
3. S090's teaches cell states lane policy ("outside this lane"). That matches S032's reject-row convention, so I do not count it as the S095 defect.

## 4. Requested corrections (non-blocking; L1 decides)

1. S095 teaches: move "this does not authorize a private-value probe or a signal" out of teaches into scope or the Gate decision. Either edit in-round, since the row is new this round, or add a superseding row as S086–S088 did.
2. round-20.md: restore the missing spaces in "man-pages6.19" and "at most25 words". The same pattern recurs in "last updated2.44.0", "unchanged through2.56.0", "git2.56.0", "tierA" and "opened2026-10-21". The byte census shows literal omissions, not hidden characters.
3. Optional: state in S090's row that it re-decides S032's URL under the cleanup scope, and reconcile the two flip conditions.

## 5. Confidence and limits

- **High:** page facts (two renderings agree, quote matched byte-exact against the pinned Gate row), registry presence and cross-file consistency for S090 and S095 (byte-checked).
- **Medium:** the policy-versus-page classification of the teaches clauses. It is judgment, anchored on the page sentence and the S086–S088 precedent.
- **Not assessed (outside the named scope):** the git-scm.com git-filter-branch page, SOURCES-CONTRACT-v1, and the content of `corpus/knowledge/process-residue-observations.md`. S090's WARNING quote and its "unchanged through 2.56.0" claim are registry assertions only.
- The page was read once per mode this session. A later man-pages release would not appear here.
- No runtime, build, test, process or target-code execution. No process content, private configuration, vault material, or census/operator-sweep path was touched.

## 6. Commands and tooling

- `read skill://godspeed`; `read` on the man7 URL in reader and `:raw` modes.
- `bash`: `date -u +%F` (2026-10-21); `git cat-file -t 1988860…` (commit).
- `bash`: `git -C <lane> show 1988860…:corpus/SOURCES.md` and `…:corpus/lessons/round-20.md` (read-only blob reads).
- `eval` (py, read-only): the two blobs re-read via `git show`; codepoint census; exact-substring checks; registry parse (95 rows, no duplicate IDs); token locator; `git cat-file -e` on the two used-by paths (both exit 0).
- Tools installed or updated: none; no install was needed.
- Writes: this report only.
