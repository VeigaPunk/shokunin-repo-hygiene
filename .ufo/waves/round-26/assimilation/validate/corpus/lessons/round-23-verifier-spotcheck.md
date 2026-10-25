# Round 23 verifier spot-check

author: hyaku closure (non-author integrator, @m_flash)

## Conformance

- Lane report `.ufo/reports/round-23/souji.md` is committed in the fleet repo by `souji-shokunin` (`12f6dd2775b63476aa79298a24b75a1356fcd55d`). It contains a `SHONEN` heading and four checklist lines. Report cites lane landing `94fe8094f52098b8d2a27dcdaeba953f6ec1a487`; the dispatch report-close commit `2f96bf4c269c353986178e128ca9711b0e928b8d` and all cited revisions checked are ancestors of `refs/remotes/origin/master`.
- Prompt `.ufo/prompts/souji-round-23.md` is a rendering of the shipped template plus round addendum. It includes the claims/frontier, L2, report, commit/push, scope, L0, and campaign requirements.
- `jj-lane.sh state` reports `ahead=0`; detached lane HEAD is `2f96bf4c269c353986178e128ca9711b0e928b8d`. `git status --porcelain` has one untracked `census/operator-sweep-20261019/`; not round work and excluded by round evidence. No tracked dirty work.
- Sources census command returned `souji ok` with the recorded 30 W04 duplicate-URL notices and no E findings.

## Claim re-checks

| Claim | Re-check command / observed output | Axis verdict |
|---|---|---|
| C1 calibration | `python3 -B tools/souji-record-agreement.py --rev 2f96bf4c269c353986178e128ca9711b0e928b8d --no-worktree` → `keys=4 records=4 occurrences=17 mismatches=0`. Instrument's pinned after receipt identifies its measured revision as `eb1aa49783ae4a0d42e062aa5a61e49a91b0f76a`; re-run at the report's final tip agrees. | improved |
| C2 operability | Committed-tree measurement `git grep -l -E '^tool_sha256=[0-9a-f]{64}$' 2f96bf4c269c353986178e128ca9711b0e928b8d -- census/ | wc -l` → 5. Ran `python3 tools/souji-receipt-run.py verify --root . <receipt>` on all five listed receipt TSVs; each returned `verify=ok`, with its recorded revision/tool digest. | improved |
| C3 coverage | `git show 2f96bf4c269c353986178e128ca9711b0e928b8d:corpus/SOURCES.md | grep -cE '^ {0,3}\\|[[:space:]]*S[0-9]{3,}[[:space:]]*\\|'` → 119; source census `souji ok`. `corpus/README.md` Round 13 current coverage states the three F2 read-side entries (one pre-existing plus two new). The reported entry-gate receipt records `entries=2 ok=2 fail=0`. | improved |

Owned-axis diff: `git diff 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd 2f96bf4c269c353986178e128ca9711b0e928b8d -- SCORECARD.md` adds the three measured claim rows and capability rows; no owned axis is marked harmed. Receipt claims are evidence-verified by the committed receipts and verifier outputs above; C1 and C3 counts were independently re-measured. Gate/selftest tallies are recorded evidence, not rerun here.

## Discernment sample

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| Admit repo-size-census-readonly (S115–S117) | ADMIT | https://git-scm.com/docs/git-count-objects, § OPTIONS `-v/--verbose`; opened live | agree | It defines `garbage` as a count of invalid loose/pack files, `size-garbage` as KiB, and `alternate` paths; these are usable read-side facts. Its distinct fsck/prune cautions are corroborated by the committed source snapshots and entry citations. |
| Reject JA claim that both languages gloss `garbage` alike | REJECT | https://qiita.com/koseki/items/f1af58f1ec1693f0536a; opened live | agree | Reopened page discusses `gc.auto` and its 6700 threshold; it does not explain the `count-objects` `garbage` field. The round lesson's reject rationale matches the source. |
| Reject staged own-work fleet census | REJECT | `census/round-3/garbage-census.out` (lane path) | agree | The source path cannot be reopened: it is absent. The lesson's reason—that evidence outside the lane cannot be re-derived from lane bytes—is verified; requiring a committed, receipted input before flipping is appropriate. |

S115 quote check: the reopened official page says “garbage: the number of files in the object database that are neither valid loose objects nor valid packs”; 19 words, consistent with the registry's ≤25-word quote. S118's reopened source supports the quoted threshold but does not support a garbage-field gloss.

## Trend verdicts

- **expansion — unprovable-but-better.** Two new entries and five new registry rows are evidenced, but F2 already had one entry and LEARNING's `improved` rule requires net entries on ground the map did not hold; F2 remains the same map ground.
- **quality — unprovable-but-better.** The round has new tools and verified receipts, but the trend's observable is corpus-entry re-verification/deepening/supersession; no evidence here establishes that corpus quality criterion.
- **discernment — improved.** Three independent re-opened decisions agree with the gate, including both an admit and reject; the reject rationales match the source/path evidence.

## Routed defects / operator notes

- Lane owes the untracked `census/operator-sweep-20261019/` as previously designated operator-owned material; leave untouched. It does not constitute round work.
- Round report gives C3 `F2 entries 1 → 3`, but the frozen coverage map was not changed to add an explicit entry row for the two new titles; its Round 13 prose does record the three entries. Next round should reconcile the current map table with its own “read side now holds three” prose.
- No lane defect found that blocks the three claim measurements. No promotion marks added; SHONEN promotion remains operator-owned.
