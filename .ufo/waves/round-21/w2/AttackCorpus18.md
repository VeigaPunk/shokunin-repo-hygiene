STATUS: PARTIAL — The complete corpus yields 112 visible calls, but seven tail calls were recovered only after the pinned predicate had been opened: recovery/ConsumerSkill.txt lines 76 and 80, and recovery/InputR14Frozen.txt lines 81, 82, 86, 90, and 91. I labeled these seven directly from the frozen contract without using the predicate result, but the required “label every call before classifier” ordering cannot be retroactively satisfied. The other 105 rows were labeled before classifier inspection.

# AttackCorpus18 — C1 classifier falsification

## Independent labels

Oracle sources read first: `.ufo/waves/round-21/preregistration.txt`, `clarification-before-measurement.txt`, and `full-corpus-restoration.txt`. Call extraction used the exact transcript paths in the assignment, including error-status attempts. The TSV uses physical line numbers and records each call found across `final/`, `recovery-final/`, and `recovery/`.

Observed label totals in the delivered TSV: **99 OK, 13 UNSEEN, 0 FLAG (112 rows)**. UNSEEN rows are cut targets or cut patterns without a visible target; the TSV explains each case. Error-status reads remain labeled attempts. No source-code execution occurred.

## Pinned predicate comparison

Searched the pinned source with:

`git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n implicit_root_read 522dcd768ca90afe166532d37d306d3df70aeea5 -- tools/souji-seat-audit.py`

It located `implicit_root_read` at line 377 and its caller at line 456. Static inspection of the pinned function body (lines 377–404) shows:

- For `grep`, it selects the rightmost ` @ ` target first, then the legacy rightmost ` in ` target; with neither separator, complete args map to implicit `.` and args containing `…` return no finding.
- It splits targets on `;`, trims components, and skips empty or ellipsis-containing components.
- For `read`, it strips trailing documented line/raw/conflicts selectors before classification.
- Absolute and `~` paths are excluded; URI matching uses `re.IGNORECASE`.
- Other visible relative components are joined to `fleet`, normalized lexically, and reported only when outside the normalized lane root.

Against all 112 rows, complete visible targets are absolute paths or URIs, so the predicate returns no outside-lane relative component. Cut targets/patterns map to its lower-bound skip/no-finding behavior and remain UNSEEN in the TSV rather than being treated as observed OK. I found **no predicate disagreement**. The seven late-discovered rows were labeled from the frozen contract independently of the already-inspected predicate; the temporal independence requirement remains unmet for them.

## Calibration gaps / confidence

- **Observed:** the complete exact-file search yields 112 matched tool-call lines, reconciling the advertised count. Seven tail lines were initially omitted from the displayed search result and were added from direct per-file results.
- **Observed:** this subset contains no visible complete relative target and no complete grep call with neither ` @ ` nor legacy ` in `; it therefore does not exercise a positive V-READ-ROOT case. The three cut-pattern/no-visible-target grep cases are UNSEEN, not evidence that the implicit-cwd branch is correct.
- **Observed:** no legacy `grep(PATTERN in PATH)` row, semicolon-separated target, `:conflicts` selector, or mixed-case URI occurs in the TSV. The inspected code has the stated legacy precedence, per-component split, selector, and case-insensitive URI predicates, but these cases are not exercised here.
- **Confidence:** high for the manually visible call labels and static predicate comparison; reduced for calibration by the post-inspection labeling sequence of seven rows and by absent positive-relative, implicit-cwd, legacy, multi-target, selector, and case-variation edge coverage.

Report: `.ufo/waves/round-21/w2/AttackCorpus18.md`
DELIVER: `.ufo/waves/round-21/w2/AttackCorpus18.tsv`
