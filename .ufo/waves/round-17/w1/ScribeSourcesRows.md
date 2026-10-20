STATUS: DONE — SOURCES registry contract, next id, W04/E04 duplicate rules, rejected-row rules and lesson Gate checklist located and quoted; nothing run.

# ScribeSourcesRows — souji round 17 (wave 1)

Scope: read-only. Sources read: `/home/vgpnk/Projects/shokunin/CORPUS.md` (section `SOURCES.md — where a shokunin learns`, lines 64–128 and 163–178), `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md` (whole file, 98 lines), `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (the enforcing validator, read by grep), `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md` (Q5, line 29), and `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-16.md` (Gate, lines 16–35). No command was executed. No file was edited other than this report. No tool was installed or updated.

## 1. Registry column order and allowed values

Header (CORPUS.md:86, SOURCES.md:13), 11 cells, NF=13 once the leading and trailing pipes are counted:

```
| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
```

awk field map used by the census (`sources-census.sh:626-628`): `$2`=id, `$3`=source, `$4`=kind, `$5`=tier, `$6`=scope, `$7`=anchor, `$8`=teaches, `$9`=status, `$10`=opened, `$11`=recheck, `$12`=used-by.

| column | rule | allowed values (source) |
|---|---|---|
| id | `S` + 3 or more digits, never reused | `^S[0-9]{3,}$` (`sources-census.sh:640`; CORPUS.md:89) |
| source | title — canonical URL or DOI; repo path or command for own-work | free text, no `\|` |
| kind | enum | `spec` `docs` `paper` `code` `tool` `dataset` `talk` `book` `community` `own-work` (CORPUS.md:91-92; `sources-census.sh:655`, E05) |
| tier | scoped to `scope`; `community` never A | `A` `B` `C` only (CORPUS.md:93-97; `sources-census.sh:657`, E06; E10 at `:668`) |
| scope | the claim or topic the tier applies to | free text; compared as an exact trimmed string (`sources-census.sh:626`, `:643`) |
| anchor | section/heading/page/line plus revision; never a bare homepage | free text (CORPUS.md:99-100) |
| teaches | one grounded benefit; rejected rows read `REJECTED: <reason>; flip: <what would change the verdict>` | free text (CORPUS.md:101-102); W02 warns when shorter than 8 chars (`sources-census.sh:671-672`) |
| status | enum | `queued` `mined` `rejected` only (CORPUS.md:103-104; E07 at `sources-census.sh:658-659`). `watch` is not a status (`sources-census.sh:4`) |
| opened | ISO `YYYY-MM-DD`, past or present | E08 if invalid or after today (`sources-census.sh:660-662`) |
| recheck | ISO date, `NNd`, or a symbolic cadence | census accepts `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`, `^[0-9]+d$`, or `^[A-Za-z][A-Za-z0-9 _-]*$` (`sources-census.sh:582`, `:663-666`, E09). Values in use in the registry: `on-release` (most rows), `on-change` (S039), `on-correction` (S041), `90d` (S011), `180d` (S014, S015), `365d` (S017, S022, S027, S028, S029, S030, S048). Contract cadences in CORPUS.md:105-106: `90d`, `180d`, `on-release` |
| used-by | repo-relative paths of citing knowledge entries or lessons, comma-separated, or `—` | `mined` requires at least one path and each must exist on disk (W03 at `:673-674`; E11 at `:566-567`); `—` allowed for queued and rejected rows (CORPUS.md:107-108) |

Note on `recheck` values: the census accepts any single-word symbolic cadence. `annual` appears only in a census fixture (`sources-census.sh:149`). Use the in-use set above.

Row shape example (S041, `SOURCES.md:55`, abbreviated): `| S041 | … | own-work | A | … | … | … | mined | 2026-10-20 | on-correction | corpus/lessons/round-15.md |`

## 2. Next free id

Last row: **S050** (`SOURCES.md:64`, Python `compile()`). Registry ids run S001–S050 with no gaps and no reuse. **Next free id: S051.** Rows S044 and S048 are rejected rows; their ids are retained and not reusable.

## 3. Duplicate URLs across scopes (W04) and same-scope duplicates (E04)

URL normalization (`sources-census.sh:600-605`, `url_of`): the first `http(s)://…` token in the `source` cell is taken; a `#fragment` is removed; the trailing `/` is removed; the scheme is removed; the host part is lowercased; the path is kept case-sensitive. So `https://DUP.example/source` and `https://dup.example/source/` are the same URL (fixture `sources-census.sh:358-359`). Query strings are not stripped.

Rules, quoted from the enforcing code:

- **W04 — same URL across scopes (warning only).** `sources-census.sh:643-645`: `scope_key=u SUBSEP scope`; if the URL was seen before and the `(URL, scope)` pair is new, print `W04 … duplicate url … across scopes`. W04 "does not affect clean lanes" (`sources-census.sh:33`). It is emitted on the later row, and it applies to rejected rows too (the check does not test status).
- **E04 — same URL and scope (failure).** `sources-census.sh:646-649`: fails when the new row is not `rejected`, the `(URL, scope)` pair already has a non-rejected row, and the new row's `teaches` does not contain `supersedes S0NN`. A correction in the same scope must open its `teaches` with `supersedes S0NN —` (CORPUS.md:116-118).
- **Rejected exemption.** Rejected rows never trigger E04 (`:646`), and a non-rejected row after rejected rows of the same pair does not trigger E04, because only non-rejected prior rows set `url_scope_nonrejected` (`:653`). Fixture: `sources-census.sh:366-382` (S017 queued + S030 rejected on the same URL and scope → exit 0; S031 rejected + S032 queued on another URL → exit 0).

Practice in the registry:

- S035 supersedes S005 (same git-repo URL, different scope): W04 for S035 by design; S005 stays queued and is not rewritten (`SOURCES.md:49`, S035 teaches).
- S036 and S049 share `git-scm.com/docs/git` under different scopes (`SOURCES.md:9`, S049 note): W04 expected; no E04.
- S038 supersedes S034 (same timeout URL, different scope): W04 expected (`SOURCES.md:52`).

Rule for L1 adding S051+: a URL reused under a new scope gets a W04 warning, which is acceptable and should be disclosed in the lesson Gate. Re-using a URL under an identical scope requires either a rejected status or `supersedes S0NN —` in `teaches`, or the validator fails with E04.

## 4. Rejected rows

- Kept, never deleted: CORPUS.md:103-104 (`rejected` (kept — a rejection is evidence of taste)); S044, S048 are the round-16 examples.
- Format: `REJECTED: <reason>; flip: <what would change the verdict>` (CORPUS.md:101-102). S030 and S044 show the pattern.
- Status `rejected`; `recheck` a cadence (S030 `365d`, S044 `on-release`, S048 `365d`); `used-by` `—` (no `mined` requirement applies).
- Minimum `teaches` length 8 chars, else W02 (`sources-census.sh:671-672`).
- Rejected rows are exempt from E04 (`:646`) and may share a URL and scope with a later row.
- Round-16 rejected rows were recorded in the Gate with the reason and a flip condition (`round-16.md:27`, `:31`).

## 5. Lesson `## Gate` recording requirements (checklist for S051+)

Sources of the requirements: CORPUS.md:19-20 (every round lesson carries a `## Gate` section — "candidates, admitted, rejected with reasons, spot-check result"), CORPUS.md:112-115 (Rule 1), CORPUS.md:116-118 (Rule 2), CORPUS.md:126-128 (Rule 5), CORPUS.md:176-178 (M089), CORPUS.md:171-175 (`## Mistakes`), CORPUS.md:163-170 (knowledge provenance trio). Example of a compliant Gate: `corpus/lessons/round-16.md:16-37`.

Checklist, for each new row S051+ and for the round:

- [ ] **Lesson file.** `corpus/lessons/round-17.md` contains a `## Gate` heading (CORPUS.md:19-20, :177-178). It is written in the round that opens the source (CORPUS.md:112-113).
- [ ] **Candidates, admitted, rejected with reasons.** Under `## Gate` → `### Claim decisions`, list every candidate row, its admission (`queued`/`mined`) or rejection (with the reason and the flip condition in the REJECTED format), and the scope of the tier (CORPUS.md:19-20, :101-102).
- [ ] **URL, access date, and quote per new row.** For each new row: the canonical URL; the access date (ISO); a quote of **≤25 words** plus its location, grounding `teaches` (CORPUS.md:112-114). Round-16 used `**S0NN** URL (access 2026-10-20; "last updated" line; located quote)` (`round-16.md:24-33`). A row with no located quote is not admitted. The ≤25-word limit is a manual count; the census does not check it.
- [ ] **Open before writing.** The source was opened in this round by the row's author (CORPUS.md:112-113).
- [ ] **Non-author spot-check.** A non-author re-opens a sample (CORPUS.md:114-115). Record the spot-check result in the Gate: which rows, which seat re-derived, agree or disagree and the cause (QUALITY.md Q5, line 29: the Gate "names the re-deriving seat and records agree/disagree with cause").
- [ ] **Registry changes old→new.** Every change to `status`, `recheck` or `used-by` of an existing row is logged old→new in the Gate (CORPUS.md:116-117). Round-16 precedent: `round-16.md:35` (S042 used-by `…` → `…`; S043 … absent → mined, recheck on-release). Immutable cells (source, scope, anchor, teaches, opened) are not edited; a correction is a new row whose `teaches` opens `supersedes S0NN —` (CORPUS.md:116-118).
- [ ] **Registry header note.** Add a `Round-17 provenance:` paragraph to `corpus/SOURCES.md` (precedent `SOURCES.md:5`, `:7`, `:9`) naming the new ids (S051…), the opening date, the lesson that holds their quotes, and any rejected rows.
- [ ] **Search log entry (rule 5).** One prose note per bounded search: question/query, where searched, date, identified / screened / included / excluded counts, exclusion reasons, stop rationale (CORPUS.md:126-128; precedent `SOURCES.md:75-84`). A negative claim carries its sweep.
- [ ] **Leads.** New leads go under `## Leads (unopened)` as bullets and never become rows until opened (CORPUS.md:83). Remove a lead when it is opened.
- [ ] **Mistakes section (if the round mines mistakes).** `## Mistakes`: one row per mistake — class · evidence pointer · captured-by · fix (CORPUS.md:171-175; precedent `round-16.md:5-14`).
- [ ] **Knowledge provenance.** Any knowledge entry citing a new row opens with `source:`, `verified-at:`, `recheck:`, and its `source:` cites the `S0NN` row with URL and anchor (CORPUS.md:163-170). Each knowledge `used-by` path must exist on disk (E11, `sources-census.sh:566-567`) before a row goes `mined`.
- [ ] **Mined rows.** Status `mined` only when `used-by` names at least one existing path (W03 `:673-674`; E11). Tier C with mined status triggers W01 (`:669-670`); tier C is lead only and never sole support (CORPUS.md:96).
- [ ] **Validator run.** Run `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` before any SOURCES edit (record exit code and `sha256sum` of `corpus/SOURCES.md`) and after the edit. Required end state: exit 0, no E-lines; any W04 lines are disclosed in the Gate (round-16 recorded the same: `round-16.md:37`).
- [ ] **Corrections are logged, not rewritten.** Earlier rows keep their immutable cells (`SOURCES.md:9` precedent: "no other existing cell changed").

## 6. Verbatim CORPUS.md lines quoted

Lines 64–68:
> `## SOURCES.md — where a shokunin learns`
> Contract v1 (kaika, 2026-10-19, frozen), carried here in full from
> `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`. A change is a new contract version,
> never an edit to this section.

Lines 70–73:
> Where a shokunin learns. `corpus/knowledge/` holds admitted facts; `corpus/SOURCES.md`
> holds the places they come from — what each teaches, how far to trust it for which
> scope, and when to look again. It is the lane's curated reading list and the standing
> record of its taste. Inputs: `kaika-w1/art-curation.md` (curation and grading practice),

Lines 86–108 (registry header, field rules):
> `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`
> - `id` — `S` + 3 or more digits, the next unused; never reused. No `|` inside any cell.
> - `source` — title — canonical URL or DOI (a repo path or command for `own-work`).
> - `kind` — `spec` · `docs` · `paper` · `code` · `tool` · `dataset` · `talk` · `book` ·
>   `community` · `own-work`.
> - `tier` — scoped to `scope`, never global. **A**: primary or authoritative for that scope
>   (spec, official docs, source code, original paper, maintainer statement, the lane's own
>   re-runnable gate output). **B**: strong secondary (expert write-up with reproducible
>   detail, survey, textbook). **C**: lead only — never sole support for an admitted entry.
>   `community` is never A. Tier is curation, not truth: no NATO/GRADE labels on rows.
> - `scope` — the claim or topic the tier applies to.
> - `anchor` — exact section / heading / page / line plus revision (version, commit, or
>   publication date). Never a bare homepage.
> - `teaches` — one grounded learner benefit. Rejected rows read
>   `REJECTED: <reason>; flip: <what would change the verdict>`.
> - `status` — `queued` (opened, worth mining) · `mined` (cited by ≥1 path in `used-by`) ·
>   `rejected` (kept — a rejection is evidence of taste).
> - `opened` — ISO date the row's author opened the source. `recheck` — ISO date or cadence
>   (`90d`, `180d`, `on-release`).
> - `used-by` — repo-relative paths of the knowledge entries or lessons citing the row,
>   comma-separated, or `—`.

Lines 112–118 (Rules 1–2):
> 1. **A row is a claim.** Write it only after opening the source in the round that writes
>    the row. The round lesson's `## Gate` records, for every new row, the URL, the access
>    date, and a ≤25-word quote with its location grounding `teaches`. Non-author
>    verification re-opens a sample.
> 2. **Append-only.** Only `status`, `recheck` and `used-by` change in place, and each change
>    is logged old→new in the round lesson. A correction is a new row whose `teaches` opens
>    `supersedes S0NN —`.

Lines 123–128 (Rules 4–5):
> 4. **Expansion is knowledge, not rows.** … There is
>    no row quota; a short registry of opened, honestly tiered rows beats a long one.
> 5. **Search log.** PRISMA-inspired, not PRISMA-compliant: question/query, where searched,
>    date, identified / screened / included / excluded counts, exclusion reasons, stop
>    rationale. A negative claim carries its sweep.

Lines 19–20 (lesson Gate requirement):
> Each `knowledge/` entry opens with `source:`, `verified-at:` and `recheck:`;
> each `lessons/round-<N>.md` carries a `## Gate` section (candidates,
> admitted, rejected with reasons, spot-check result). See `LEARNING.md`.

Lines 176–178 (why Gate exists):
> after capture (`mistakes.md` §5), and lanes without a `## Gate` section had
> nowhere to keep a rejection (M089).

Lines 163–165 (knowledge provenance):
> - **A new knowledge entry opens with its provenance trio.** `source:`,
>   `verified-at:` and `recheck:` come first; when the source is external,
>   `source:` cites its `S###` row in `corpus/SOURCES.md` alongside the URL and
>   anchor.

## 7. Findings (advisory)

1. Enforcing validator is `scripts/sources-census.sh`. CORPUS.md:131-148 gives an awk census with the same field map; the enforcing code adds E04/W04 and the symbolic-recheck regex (`sources-census.sh:582`). Where the two differ, the script governs.
2. CORPUS.md:105-106 names recheck examples `90d`, `180d`, `on-release`; the registry also uses `on-change`, `on-correction`, `365d`, and the validator accepts them. The contract text is not updated; disclosed, not changed.
3. W04 is a warning, so a same-URL, new-scope row (S035, S036, S038) passes validation. That is by design in `sources-census.sh:33`.
4. The ≤25-word quote limit is not checked by any script (`CORPUS.md:114`); L1 counts it by hand.

## 8. Commands run

None. Reads and greps only (`_read`, `_grep`). No installs or upgrades.

## 9. Verdict

Holds for the requested items: column order and allowed values (§1), next id S051 (§2), W04/E04 and rejected exemption rules (§3–4), Gate checklist with CORPUS.md lines quoted (§5–6). No registry row was edited.
