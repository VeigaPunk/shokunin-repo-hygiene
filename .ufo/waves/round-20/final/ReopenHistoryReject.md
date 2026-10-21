# ReopenHistoryReject — round-20 final source falsifier (S090)

STATUS: PARTIAL — S090's rejection outcome agrees with the live page and with PROVINCE.md's refusal. The S090 registry row and the round-20 Gate entry still carry three real defects, and L1 should fix them before S090 serves as the discernment reject: (1) the row's "flip" clause cannot reverse the Souji-side decision; (2) neither the row nor the Gate cites the policy that supports the reject (S032 does); (3) S090 shares S032's URL and reject without saying so, and adds no new page fact. No invented historical reject was found.

Scope: read-only, source-only, author-side advisory. No registry, corpus, wave or census edits; no subagents; no installs; no builds, tests, linters, page commands or target execution.

## 1. Access record

| Field | Value |
|---|---|
| URL | `https://git-scm.com/docs/git-filter-branch` (exact) |
| Access date | 2026-10-21 |
| Access method | `read` (reader rendering); `grep` over the same URL (reader rendering); `grep` over the `:raw` HTML. No raw byte diff was made. |
| Located quote (18 words) | WARNING section, first paragraph: "These safety and performance issues cannot be backward compatibly fixed and as such, its use is not recommended." |
| Gate short form | "its use is not recommended." Exact substring in reader text and raw HTML (raw line 1884; the raw HTML has two spaces after that period, which does not affect the substring). |
| Actual version | Version table: "git-filter-branch last updated in 2.44.0" (2.44.0 dated 2024-02-23) and "2.44.1 → 2.56.0 no changes" (raw lines 1323, 1329). Newest version the page tabulates: 2.56.0. No other version stamp on the page. Served as "Latest version". |
| Not checked | No archived snapshot of the page on the S090 open date; no full raw-HTML diff. |

## 2. Pinned comparison (commit 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1)

Named pinned files read only through `git show <rev>:<path>`. S090 row = `corpus/SOURCES.md:110`; Gate row = `corpus/lessons/round-20.md:39`.

| Field | Page (2026-10-21) | S090 row | Round-20 Gate | Verdict |
|---|---|---|---|---|
| URL | git-scm.com/docs/git-filter-branch | same | same | AGREE |
| Quote | WARNING: "its use is not recommended" | paraphrase: "the official warning does not recommend this tool" | exact: “its use is not recommended.” | AGREE |
| Version | last updated 2.44.0; no change 2.44.1 → 2.56.0 | "last updated 2.44.0, unchanged through 2.56.0" | "last updated2.44.0, unchanged through2.56.0" (spaces missing) | AGREE; typo in Gate |
| Anchor | "## WARNING" | "WARNING" | "WARNING:" | AGREE |
| Tier | official primary doc (n/a) | A | (n/a) | AGREE with lane convention; definition not located (F5) |
| Status | (n/a) | rejected | **reject** | AGREE as curation status |
| Used-by | (n/a) | corpus/lessons/round-20.md | Gate row present at line 39 | AGREE |
| Opened | accessed 2026-10-21 | 2026-10-21 | 2026-10-21 | AGREE |
| Flip | (n/a) | "an operator separately scopes history work to its owner, never a Souji cleanup receipt" | "flip only through separately scoped operator history work to its owner, never a cleanup receipt" | DISAGREE (F2) |
| Policy basis | "not recommended"; no prohibition | none cited | none cited | DISAGREE (F3) |

## 3. Primary page facts vs lane policy

Primary page facts (WARNING section and version table):
- "git filter-branch has a plethora of pitfalls … such abysmal performance".
- "its use is not recommended" (quoted above).
- "Please use an alternative history filtering tool such as git filter-repo."
- "If you still need to use git filter-branch, please carefully read SAFETY (and PERFORMANCE)…" This discourages use and does not prohibit it.
- DESCRIPTION warning, same page: "avoid using it anyway, if a simple single commit would suffice to fix your problem."
- Version facts as in §1.

Lane policy (not on the page; the page never mentions Souji, cleanup, receipts, operators or PROVINCE):
- "history rewriting is outside this lane" rests on PROVINCE.md, "## Refuses": "Git history rewrite in any repo (reset/rebase/amend of published commits) — operator-owned; kura is unminted."
- PROVINCE.md, Adjacent bullet: "Credential-bearing history (git-filter-repo `--sensitive-data-removal`) routes to kagi-shokunin and the operator; souji never rewrites history."
- "never a Souji cleanup receipt", "cleanup candidate", the "rejected" status and tier A are lane vocabulary and decisions.

The reject's strength (refusal, not discouragement) comes from PROVINCE.md. The page alone supports only "not recommended".

## 4. S090: retained rejection, flip, and historical claim

- **Rejection is retained at the pinned commit** in four committed places: `corpus/SOURCES.md:110` (status rejected; "REJECTED: …"), `corpus/lessons/round-20.md:39` (**reject**), `corpus/SOURCES.md:139` (search log: "rejected 1 cleanup-authority candidate (S090)") and `corpus/lessons/round-20.md:46, 61, 85` (accounting). Confidence: high.
- **No invented historical reject.** Attacked claim: S090 was rejected in an earlier round. Counterexample search: the round-19 Gate records the registry growing from 78 to 85 rows, its later corrections add S086–S088, and round 20 introduces S089 onward, so S090 is absent before round 20. `corpus/lessons/round-19.md` (read in full) has no S090, no filter-branch reference and no source-reject catalogue. The only "Round-19" search-log mention in `corpus/SOURCES.md` is the round-20 disclaimer at line 139. The only earlier reject of this URL is S032 (opened 2026-10-19, `corpus/SOURCES.md:52`). The round-20 lesson states that neither reject is relabelled as a round-19 decision. Confidence: high. Wave reports were out of scope and not read.
- **The flip does not flip.** Attacked claim: S090 has a reversal path. Both copies name a condition that leaves the Souji-side decision unchanged: operator-scoped history work, "never a Souji cleanup receipt". That restates PROVINCE's existing "operator-owned" rule, and PROVINCE names no owner ("kura is unminted"). The only reversal condition retained for this URL is S032's (`corpus/SOURCES.md:52`): "git drops the WARNING and the operator moves history rewrite into souji's province." The WARNING is still on the page on 2026-10-21 (raw lines 1880–1884), so that condition is unmet. Confidence: high on the text; medium on the author's intent.
- **The "cleanup candidate" origin is not traced.** `corpus/lessons/round-20.md` calls it a "cleanup-authority candidate" (lines 46, 61, 85) and cites no seat report, wave file or proposal for it. The search question was "does a cleanup-source rejection actually exist this round?" (`corpus/SOURCES.md:139`), which frames the search around producing a reject. Not invented in the pinned record, but the trigger is unrecorded. Confidence: high that the pinned lesson does not trace it.

## 5. Findings with calibrated confidence

- **F1 — reject outcome: AGREE (high).** The page says "not recommended" and does not prohibit use. The refusal is lane authority in PROVINCE.md. Both sources are needed for a reject; the page alone supports only discouragement.
- **F2 — flip clause: DISAGREE (high).** The S090 flip does not reverse the Souji-side decision (§4). Fix by stating "no Souji-side flip" or by citing S032's real reversal condition.
- **F3 — policy citation: DISAGREE (high).** The S090 row and its Gate entry cite no PROVINCE.md section for "outside this lane". S032 cites "PROVINCE.md § Refuses". The pointer resolves at the pinned commit.
- **F4 — duplicate evidence: DISAGREE on independence (high).** S090 and S032 share one URL, one WARNING and one reject. The lane's same-URL precedents (S049, S057, S059) each state a different scope and disclose the shared source in header provenance; S090 does neither for S032. S090's scope is effectively S032's, and the round-20 header has no provenance paragraph (rounds 13–14 and 16–19 each have one). For the discernment sample, "actual current reject (S090)" re-reads one page and adds no independent evidence.
- **F5 — tier A: AGREE with convention; not verified against a definition (medium-high).** `corpus/SOURCES.md:3` says "Tier definitions live there" (SOURCES-CONTRACT-v1, path not named). `corpus/QUALITY.md:5–6` says tiers "live in `corpus/SOURCES.md` (contract v1)". Neither pinned file defines A/B/C. A matches the other official-doc rows (S001–S004, S032, S035, S079–S081, S089–S093), and S017's A→B demotion shows tiers follow source type.
- **F6 — status and used-by: AGREE (high).** S090 is the fifth rejected row (S030, S032, S044, S048, S090). The used-by target `corpus/lessons/round-20.md` contains the S090 Gate row.
- **F7 — minor typography (high, low impact).** The round-20 Gate omits spaces in places ("updated2.44.0", "through2.56.0", "git2.56.0").
- **F8 — minor, not a defect (high).** The page's alternative, git-filter-repo, is not mentioned in S090. PROVINCE routes credential-bearing filter-repo history to kagi/operator, so there is no contradiction.

## 6. Attack and counterexample record (source-only)

- Attacked: S090 reject outcome; S090 flip; S090 historical-reject claim; S090 tier, status and used-by; the WARNING quote and version.
- Counterexamples searched: a Souji-side reversal clause (none in pinned text); a pre-round-20 S090 reject in `corpus/lessons/round-19.md` and the SOURCES search log (none); a page variant with different WARNING wording (reader and raw HTML agree).
- Not searched: wave reports and census roots (outside this item's named subpaths); other registry rows beyond S032 and S090 (no source-wide search).

## 7. Commands run (all read-only)

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1^{commit}`: exit 0, prints the full hash.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<path>`: exit 0 for `corpus/SOURCES.md`, `corpus/lessons/round-20.md`, `corpus/lessons/round-19.md`, `corpus/QUALITY.md`, `corpus/README.md`, `PROVINCE.md`. `corpus/README.md` gave no contract path.
- Fetches of `https://git-scm.com/docs/git-filter-branch` (reader; `grep`; `grep` over `:raw`). No page command was run.
- Greps over the captured git-show output. No output was written to any repository.
- Pre-write existence check of this report path: not found.

No installs were made. No tool, version or channel is recorded because nothing was installed.

## 8. Suggested L1 actions (not performed; no registry edits made)

1. S090 row and Gate: cite PROVINCE.md § Refuses and the Adjacent bullet as the policy basis, and keep page facts separate from it.
2. Replace the S090 flip with "no Souji-side flip", or use S032's reversal condition.
3. State that S090 shares S032's URL and reject, or choose a non-duplicate reject for the discernment sample.
4. Name the SOURCES-CONTRACT-v1 path, or add the A/B/C definitions in the pinned tree, and align QUALITY.md's pointer with it.
5. Fix the missing spaces in the round-20 Gate rows.
