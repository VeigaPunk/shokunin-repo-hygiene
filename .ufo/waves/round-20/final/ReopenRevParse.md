# ReopenRevParse: round-20 final falsifier for S091 (git-rev-parse) and S090 (git-filter-branch reject)

Scope: read-only. Exact public URL https://git-scm.com/docs/git-rev-parse, fetched as reader text (method native) and as raw HTML (method raw). Pinned corpus read only with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:corpus/SOURCES.md` and `...:corpus/lessons/round-20.md`. No page commands run. No private, census, operator-tree or fleet source opened. No registry edits. No tool installed or updated (none needed).

Axes checked: quote exactness; actual page version; scope precision; page fact versus lane policy; S090 retention and provenance; used-by.

Verdicts:
- S091: agree on the quote, version, one-parameter and emit-or-error behaviour, and the negative scope. Disagree on wording: the existence attribution, the dropped SHA-1 qualifier, and the used-by convention. All non-blocking.
- S090: agree that the rejection and its flip are retained and not invented. Not verified here: the page quote and version claim. Not traceable: the "round-20 cleanup candidate" label. All non-blocking.
- Blocking findings: none.

## 1. Access record

| Field | Value |
|---|---|
| Exact URL | https://git-scm.com/docs/git-rev-parse (reader text; raw HTML of the same URL) |
| Access date | 2026-10-21. Reader fetch in the first batch; raw fetch in a later batch; UTC clock read 09:55:25Z in the second batch |
| Actual page version | "git-rev-parse last updated in 2.56.0" (reader line 162; raw line 1329). Version table: 2.56.0, 2026-09-28 (raw line 1362) |
| Section located | OPTIONS › Options for Output › `--verify` (raw `<dt>` anchor `Documentation/git-rev-parse.txt---verify`, raw line 2717) |

## 2. Located quote (7 words)

“Verify that exactly one parameter is provided”: OPTIONS › `--verify`, first paragraph (raw line 2719; reader line 332). Exact match to the pinned S091 Gate row (round-20.md line 40).

Other page wording used below (each under 25 words, exact after tag removal):
- “can be turned into a raw 20-byte SHA-1” (raw 2720; reader 333)
- “emit it to the standard output; otherwise, error out.” (raw 2721–2722; reader 334–335)
- “make sure that the output actually names an object” (raw 2724; reader 337)
- “you can add the ^{type} peeling operator to the parameter” (raw 2726; reader 339)
- “wise to use --end-of-options so that the name argument is not mistaken” (raw 2735; reader 344)

## 3. S091 check

Pinned registry row (SOURCES.md line 111): tier A; scope "one parameter resolving to an object; no durable-ref or measured-byte claim"; anchor "last updated 2.56.0 (2026-09-28), reopened 2026-10-21; OPTIONS --verify"; status mined; opened 2026-10-21; recheck on-release; used-by corpus/lessons/round-20.md.

| # | Pinned claim | Page evidence | Verdict |
|---|---|---|---|
| 1 | Gate quote "Verify that exactly one parameter is provided" (round-20.md line 40) | Exact (raw 2719) | Agree (high) |
| 2 | Version 2.56.0 (2026-09-28); Gate cell "git2.56.0" | Label "last updated in 2.56.0"; table entry 2.56.0, 2026-09-28 | Agree (high). Gate cell lacks a space; cosmetic |
| 3 | Tier A | Official git-scm.com manual; consistent with other git-scm rows (S001–S003, S079–S081) | Agree (medium). The tier contract (SOURCES-CONTRACT-v1) was not opened; the item did not name it |
| 4 | Status mined; opened and reopened 2026-10-21; recheck on-release | Not page content | Agree with round-20.md lines 46 and 59–61 |
| 5 | Used-by: round-20.md only | The lesson uses S091 at lines 40, 46 and 59–61. Lines 140–141 say "the current helper cites S089/S091–S093"; the helper is not named in this item, so it was not opened | Agree for the lesson. Possibly incomplete if tool source notes count as uses. S079 has the same pattern, so this is a convention question, not an S091-only defect |
| 6 | Scope "one parameter resolving to an object" | Page: exactly one parameter, convertible to a raw 20-byte SHA-1, emitted or error out (raw 2719–2722). The existence and type assurance is attributed to the `^{type}` / `^{object}` peel: "make sure that the output actually names an object" (raw 2724–2729) | Disagree on wording; non-blocking. Plain `--verify` is documented as conversion, not existence. Narrow the scope to the page's wording |
| 7 | Teaches "emits its object id or errors" | Page: "raw 20-byte SHA-1" (raw 2720); "error out" (raw 2722) | Agree on behaviour. Precision loss: "object id" drops the SHA-1 qualifier. S079 (SOURCES line 99) flagged the 20-byte wording as predating SHA-256 repositories; S091 dropped that caveat. The page's separate `--output-object-format=(sha1|sha256|storage)` (reader 398–403) does not say which form plain `--verify` emits in a SHA-256 repository |
| 8 | "durable reachability, full-ID policy and working-tree equality are lane implementation policy, not guarantees of this option" | The page is silent on ref reachability and worktree equality. Default output is the full raw 20-byte SHA-1; abbreviation is the separate `--short` option (reader 367–369) | Agree; correctly labelled as policy. Full-length output is the option's default. A full-ID requirement on inputs belongs to the caller, and the page states none |
| 9 | Gate: "resolving an object is not durable-ref or byte-equality proof" | The page is silent. This is an inference from its narrower sentence | Agree as a scoped negative. Mark it as lane inference, not page text |
| 10 | "supersedes S079" | S079 (SOURCES line 99) keeps "raw object id" and the 20-byte caveat. S091 narrows without the caveat | Note: supersession dropped the SHA-1 qualifier (row 7) |
| 11 | Page facts absent from S091 | `--end-of-options` for names from an untrusted source (raw 2734–2736; reader 343–345). `--quiet` exits non-zero silently (reader 349–354) | Non-blocking omission. `--end-of-options` bears on C2's caller-input boundary if any caller passes untrusted names to `--verify`. Callers were not inspected |

## 4. Primary page facts versus lane policy (S091)

Page facts, checked in both reader and raw text:
- Exactly one parameter must be given.
- It must be convertible to a raw 20-byte SHA-1 usable with the object database.
- That SHA-1 is emitted to stdout, or the command errors out.
- `^{type}` and `^{object}` peels provide the existence and type assurance.
- `--quiet` suppresses the message and exits non-zero silently.
- `--end-of-options` is advised for untrusted names.
- `--short` gives a unique-prefix abbreviation, minimum length 4.

Lane policy or inference, not page text:
- Durable reachability as a requirement.
- Full-ID policy.
- Working-tree equality.
- Byte-equality proof.
- The claim that a resolved id is not durable proof. This is derived from the page's silence.

## 5. S090 check

Registry row (SOURCES.md line 110): tier A; status rejected; opened 2026-10-21; recheck on-release; used-by corpus/lessons/round-20.md; flip "an operator separately scopes history work to its owner, never a Souji cleanup receipt".

Retained and consistent (verified in pinned files):
- SOURCES.md line 110: status rejected, with the flip above.
- round-20.md line 39 (Gate): "**reject**", with the same owner-scoped flip in different words; located quote "its use is not recommended."
- SOURCES.md line 139 (search log) and round-20.md lines 46, 61 and 85 agree: one rejected cleanup-authority candidate, S090.

Not invented:
- Pinned SOURCES.md rows with a rejected status: S030 (line 50), S032 (line 52), S044 (line 64), S048 (line 68), S090 (line 110).
- S079 through S089 are all mined (lines 99–109). None carries a reject.
- round-20.md line 50 states that the historical catalogue gap is not repaired by inventing a reject. The pinned text does not do so.

Non-blocking calibration problems:
1. Provenance of the "round-20 cleanup candidate" label (SOURCES line 110, source cell) is not traceable. The pinned lesson names no round-20 proposal to use `git filter-branch`. The search log asks "does a cleanup-source rejection actually exist this round?" (SOURCES line 139). The reject was sought to close the catalogue gap (round-20.md line 19, R20-M4, and line 50), not traced to a documented cleanup attempt. Do not read the label as evidence of a round-20 cleanup attempt.
2. Overlap with S032: same URL, same WARNING wording ("its use is not recommended", S032 line 52), overlapping scope ("git filter-branch as a repository cleanup technique"), and the same policy basis (history rewrite refused). S090 adds the Souji-authority framing and a flip condition. It is a re-scoped row, not a separate page-level rejection.
3. Page basis not re-verified here. The S090 quote and "last updated 2.44.0, unchanged through 2.56.0" were not re-opened, because git-filter-branch is not the URL this item names. S032's round-12 record of the same wording (installed man page 2.55.0, roff line 46) supports the wording's existence in that revision, not the 2.56.0 claim.
4. Page versus policy: the WARNING is the only page-level basis. "Outside this lane", "never a Souji cleanup receipt" and the flip condition are lane policy.

## 6. Recommendations for L1 (not applied; this seat changed no registry)

1. S091 scope: replace "one parameter resolving to an object" with the page's wording: exactly one parameter, convertible to a raw 20-byte SHA-1. Existence or type only with `^{type}` or `^{object}`.
2. S091 teaches: say "raw 20-byte SHA-1" instead of "object id". Restore S079's SHA-256 caveat. Add `--end-of-options` if any caller passes untrusted names (callers not checked here).
3. Settle whether used-by includes tool source notes, and apply the same rule to S079 and S091.
4. S090: either re-open the named git-filter-branch page under a separately authorized scope to verify the quote and version claim, or mark both as unverified. Record the actual origin of the "round-20 cleanup candidate" label, or relabel it as a catalogue-gap reject. Note the overlap with S032.
5. Cosmetic: round-20.md Gate and accounting cells lose spaces ("git2.56.0", "last updated2.44.0", "tierA", "mined+5/rejected+1").

## 7. Confidence and limits

- High: the exact quote, its location, and the page's version. The reader text and the raw HTML agree.
- Medium: tier A (consistency with other rows only); used-by completeness (a convention question).
- Not verified: the S090 page quote and version claim; helper and caller code; SHA-256 behaviour of `--verify`. Source-only; nothing was executed.
- Actions taken: two reads of the exact URL (reader and raw); read-only `git show` of the two pinned files; `date -u`; this one report write. No installs. No page commands. No git writes.

Report path (lane-relative): .ufo/waves/round-20/final/ReopenRevParse.md
