# R42w2critic02 — attack on the landed C2 tool (`tools/souji-freeze-check.py`)

Seat: R42w2critic02 (critic, wave 2, falsify). Judged on: operability. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Tip under attack: `3105a63b23481fccf7df58e74d14a6681e0ea0c8`.
No lane, census, corpus, tool or fixture file was written. Scratch used: `/fast/scratch/hyaku/souji-r42/R42w2critic02` (deleted at the end of the run). Seat outputs: `.ufo/waves/round-42/w2/R42w2critic02/`.

## Subject identity

- `tools/souji-freeze-check.py` at the tip: 375 lines, sha256 `9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6` (read with `git show 3105a63b…:tools/souji-freeze-check.py`; copied to scratch). The lane working-tree file hashes identically (`sha256sum tools/souji-freeze-check.py`, same digest), so the working tree and the tip agree.
- `census/round-42/c2-counter.py` at the tip: sha256 `fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1`, equal to the pin in `census/round-42/preregistration.txt`.
- Tools: system `python3` 3.14.8, `git` 2.56.0. No tool was installed or upgraded.

## Method

1. Expectations were written first, in one pass, into `attack.py` (this seat), before any scenario ran. Each expectation is `exit code` plus the multiset of `CLAIM CLASS` findings. Sources: the grammar, classes, exit codes, FREEZE-REV and DISPATCH rules in the `c2-counter.py` docstring. The grammar point the docstring does not state (block end, Round field, symlink Control, fenced blocks, Unicode digits, digest case, Base abbreviations) is written as the literal reading and carries a `contested` note in the table.
   Disclosure: in the same session I had already read the tool source before writing those expectations, so the derivation was docstring-first, not strictly docstring-alone.
2. 152 synthetic git repositories were built under scratch (`git -C <dir>` everywhere; `rev-parse --show-toplevel` asserted equal to the fixture dir before any commit). Each was run through the tip tool as `python3 -B TOOL --root D --prereg P --rev R`, with a 180 s timeout. Exit code, `FINDING` lines and the `SUMMARY` line were recorded; a `Traceback` on stderr is a crash; a timeout is a hang.
3. Classes: `ok` (exit and multiset match); `false green` (expected finding or refusal not produced, or a missing finding on any exit); `false finding` (extra finding, or a refusal where clean was expected, and so on); `crash`; `hang`.

## Commands actually run

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2critic02/attack.py   # run 1, first pass
# run 1 deviations were two errors on my side: G02 wrote the prereg bytes without placeholder substitution (its findings are harness noise, not a tool defect); C12 omitted the NO-CLAIMS that the grammar also produces. Both were fixed (put() substitutes bytes; C12 expectation corrected). Run 1 table kept as run1-results.tsv.
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2critic02/attack.py > .../run2-console.txt   # run 2, final
TOTAL scenarios=152 false finding=4 false green=3 ok=145
TMPDIR=<scratch>/tmp python3 -B <scratch>/tool/souji-freeze-check.py --selftest   -> SELFTEST cases=31 pass=31 fail=0 (exit 0)
git -C <scratch>/repos/E03 ls-tree HEAD census/control.txt   -> 120000 blob a321ef98edf19213dc7b838a0fa5b33e6e2dd199	census/control.txt
git -C <scratch>/repos/E03 cat-file -p HEAD:census/control.txt   -> EXIT=1   (no newline)
grep -c Traceback .../raw/*.out   -> 0 (no crash in any of 152 runs)
```

Reproduce: write the tip blob to `/fast/scratch/hyaku/souji-r42/R42w2critic02/tool/souji-freeze-check.py` with `git show 3105a63b23481fccf7df58e74d14a6681e0ea0c8:tools/souji-freeze-check.py`, then run `attack.py` as above. The scratch repos were removed after the run; the raw per-scenario outputs are kept in `raw/`.

## Result counts (run 2, final)

| class | count |
|---|---|
| ok | 145 |
| false green | 3 |
| false finding | 4 |
| crash | 0 |
| hang | 0 |
| harness-error | 0 |
| **total** | **152** |

Every one of the 7 non-ok rows is marked `contested`: none is a clear violation of a literal docstring sentence. They are fail-open (false green) or fail-closed (false finding) readings the docstring does not settle. The 145 ok rows include several literal-clean results that are weak in operation (see Limits).

## Findings (what each attacks)

**F1 — false green, fail-open (E03). Attacks: the Control leg of the C2 freeze check (`CONTROL-NOT-RED`).** A Control path stored as a git symlink whose target text is `EXIT=1` is read as the blob `EXIT=1`, judged red, and the prereg is clean (`SUMMARY claims=1 findings=0`, exit 0). The tool's symlink guard (`COUNTER-SYMLINK`, `POPULATION-SYMLINK`) covers only Counter and Population; Control has none, so a forged "red receipt" passes. Evidence: `raw/E03.out`; `git ls-tree` shows mode `120000`. Contested only by analogy with the docstring's own rationale for COUNTER-SYMLINK ("the link text is not the counter"). Smallest named limit for L1: a CONTROL-SYMLINK check mirroring COUNTER-SYMLINK.

**F2 — false green, fail-open (A21, A22). Attacks: the DISPATCH-BEFORE-FREEZE rule, through the Round field.** `Round: 042` (zero-padded) and `Round: ４２` (fullwidth digits, `\d` matches them) both move the dispatch scan to a directory that is not `.ufo/waves/round-42/`, so a `w1-dispatch.json` added before freeze in round-42 is never reported: clean, exit 0. Control: scenario A02 uses the same repository shape with `Round: 42` and gives `C0 DISPATCH-BEFORE-FREEZE`, exit 1. Evidence: `raw/A21.out`, `raw/A22.out`, `raw/A02.out`; the A21 prereg text and its tree (`.ufo/waves/round-42/w1-dispatch.json`) are reproducible from `attack.py`. Contested only in that the docstring says `round-<N>` and does not say whether N may be zero-padded or non-ASCII.

**F3 — false green, literal-clean (C09). Attacks: claim-block parsing, silent claim loss.** A heading `## C — b` (no digit) ends the claim block, opens no claim, and gets no finding; a complete second claim beneath it is dropped without trace. Output: `SUMMARY claims=1 findings=0` for a prereg that visibly has two headings. The docstring grammar (`C`, optional spaces, a digit) makes this clean, so the expectation is clean and the row is `ok`; it is listed here because it is a silent claim loss on the fail-open side. Evidence: `raw/C09.out`. Related, the same mechanism with a tab, NBSP or leading space (`##\tC2`, `##\u00a0C2`, ` ## C2`, scenarios C06-C08) absorbs the second claim into the first; those are red only because the absorbed keys duplicate. A fully distinct second claim behind `##\tC2` would be silently green: **[INFERENCE, not run]**.

**F4 — false finding, fail-closed (D01, D02). Attacks: digest parsing.** A digest of the correct bytes written in upper case is `COUNTER-DIGEST` / `POPULATION-DIGEST`, because the regex is lower-case only. Operability cost, not a safety hole.

**F5 — false finding, fail-closed (F16, F17). Attacks: Base resolution.** A 7-character abbreviation or an upper-case full sha of a real ancestor is `BASE-UNRESOLVED`, because `FULL40` requires lower-case 40 hex, though git resolves both to the same commit. Operability cost.

## Limits (literal-clean scenarios that are weak in operation)

- **A27 (fail-open for "freeze before data"):** a draft at another path names the counter's edited digest; the counter is edited between draft and rename-in to `prereg.txt`; the rename-in commit is the freeze (oldest adding commit); clean. The edit precedes the freeze the tool records. Literal reading of FREEZE-REV, so `ok`, but a real gap for the rule the freeze check exists to enforce.
- **A20:** a dispatch file on a side branch merged after freeze is clean (graph-order rule, not wall-clock).
- **B19 / C10 / B15:** a `## Notes` heading inside a claim hides a later key (red by absence, not by content); `### C2` keys fall into C1 (red by duplication); a BOM before a key makes it missing (red).
- Duplicate `Round:` lines, a duplicate claim number (C11) and a `Round: 42` plus `Round: 42` pair have no class; clean by docstring.
- Fenced `## C1` examples (C14) and `##C9` in a fence (C15) are parsed as claims and headings: the docstring has no fence rule, so the tool is consistent with it, but an operator who documents the grammar in a prereg gets findings.

No crash, no hang, no SUMMARY count mismatch in 152 runs; `--selftest` passes 31 of 31 (exit 0). The counter's 37 cases do not contain any scenario above: the landed claim is green on its own population and silent on F1-F3.

## Full scenario table (run 2)

| scenario | expected | observed | class | attack / contested note |
|---|---|---|---|---|
| A01 | exit 0 · no findings | exit 0 · no findings | ok | dispatch-named file after freeze at depth 3 stays clean |
| A02 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | dispatch file before freeze at depth 2 |
| A03 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | w1-spec.json before freeze at depth 3 |
| A04 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | .ready.partial before freeze (basename contains .ready) |
| A05 | exit 0 · no findings | exit 0 · no findings | ok | *-dispatch-attempts.txt after freeze |
| A06 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | *-dispatch-attempts.txt before freeze |
| A07 | exit 0 · no findings | exit 0 · no findings | ok | spec.json (no hyphen before spec) is not a dispatch name |
| A08 | exit 0 · no findings | exit 0 · no findings | ok | w1-results.json.bak does not end -results.json |
| A09 | exit 0 · no findings | exit 0 · no findings | ok | dispatch file of round-41 is out of scope for round-42 |
| A10 | exit 0 · no findings | exit 0 · no findings | ok | round-420 directory is not round-42 (prefix trap) |
| A11 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | dispatch basename with a space |
| A12 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | dispatch basename with unicode |
| A13 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | dispatch basename with a double quote (git-quoted in log output) |
| A14 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | dispatch basename with a newline (git-quoted in log output) |
| A15 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | dispatch name that is a symlink, before freeze |
| A16 | exit 0 · no findings | exit 0 · no findings | ok | -dispatch in a directory name only; file basename clean |
| A17 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | dispatch added before freeze and deleted after |
| A18 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | dispatch added before freeze and renamed after |
| A19 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | dispatch on a side branch merged before the freeze commit |
| A20 | exit 0 · no findings | exit 0 · no findings | ok | dispatch on a side branch merged AFTER freeze (graph-order reading) [contested: docstring defines 'ancestor of FREEZE-REV'; wall-clock order not in scope] |
| A21 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 0 · no findings | false green | Round: 042 (zero-padded) with round-42 dispatch before freeze [contested: round number 42 written 042; docstring says round-<N>] |
| A22 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 0 · no findings | false green | Round: ４２ (fullwidth digits) with round-42 dispatch before freeze [contested: Unicode digits; round is 42] |
| A23 | exit 1 · C0 FIELD-MISSING | exit 1 · C0 FIELD-MISSING | ok | lowercase 'round:' key [contested: Round check is tool-side (r41 hardening); docstring lists FIELD-MISSING, not the Round field] |
| A24 | exit 0 · no findings | exit 0 · no findings | ok | two Round lines, both 42 [contested: duplicate Round line has no class in the docstring] |
| A25 | exit 1 · C0 FIELD-MISSING | exit 1 · C0 FIELD-MISSING | ok | no Round line at all [contested: missing Round is prereg-wide FIELD-MISSING C0 (docstring names the class, not the field)] |
| A26 | exit 1 · C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE | ok | draft at other path, dispatch between draft and rename-in to prereg.txt |
| A27 | exit 0 · no findings | exit 0 · no findings | ok | draft names the counter's EDITED digest; counter edited between draft and rename-in [contested: FREEZE-REV is the oldest ADDING commit: the rename-in is the freeze (limit)] |
| B01 | exit 0 · no findings | exit 0 · no findings | ok | same claim keys in two claims (not a duplicate) |
| B02 | exit 1 · C1 KEY-DUPLICATE | exit 1 · C1 KEY-DUPLICATE | ok | Base key twice, differing |
| B03 | exit 1 · C1 KEY-DUPLICATE | exit 1 · C1 KEY-DUPLICATE | ok | Base key three times |
| B04 | exit 1 · C1 KEY-DUPLICATE | exit 1 · C1 KEY-DUPLICATE | ok | Counter key twice, identical value |
| B05 | exit 1 · C1 KEY-DUPLICATE | exit 1 · C1 KEY-DUPLICATE | ok | Target key twice, second empty |
| B06 | exit 1 · C1 KEY-DUPLICATE; C1 FIELD-MISSING | exit 1 · C1 FIELD-MISSING; C1 KEY-DUPLICATE | ok | duplicate Base plus missing Kill |
| B07 | exit 1 · C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING | exit 1 · C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING | ok | every key tab-indented |
| B08 | exit 1 · C1 FIELD-MISSING | exit 1 · C1 FIELD-MISSING | ok | Target key with leading space |
| B09 | exit 1 · C1 FIELD-MISSING | exit 1 · C1 FIELD-MISSING | ok | key with space before colon ('Target :') |
| B10 | exit 1 · C1 FIELD-MISSING | exit 1 · C1 FIELD-MISSING | ok | lowercase key 'target:' |
| B11 | exit 0 · no findings | exit 0 · no findings | ok | trailing spaces on a value |
| B12 | exit 0 · no findings | exit 0 · no findings | ok | no space after colon ('Target:x') [contested: docstring writes `Key: value`; lenient reading is clean] |
| B13 | exit 0 · no findings | exit 0 · no findings | ok | tab after colon |
| B14 | exit 0 · no findings | exit 0 · no findings | ok | whole prereg CRLF |
| B15 | exit 1 · C1 FIELD-MISSING | exit 1 · C1 FIELD-MISSING | ok | BOM in front of the first key of a claim [contested: docstring silent on BOM; literal column-0 key rule] |
| B16 | exit 0 · no findings | exit 0 · no findings | ok | BOM in front of the Round line |
| B17 | exit 1 · C1 FIELD-EMPTY | exit 1 · C1 FIELD-EMPTY | ok | empty value after whitespace |
| B18 | exit 1 · C1 FIELD-MISSING | exit 1 · C1 FIELD-MISSING | ok | Kill key in the preamble, not in the claim |
| B19 | exit 1 · C1 FIELD-MISSING | exit 1 · C1 FIELD-MISSING | ok | Kill after a '## Notes' heading inside the claim [contested: block end at any '## ' line is the r41 grammar (tool docstring), not counter text] |
| B20 | exit 0 · no findings | exit 0 · no findings | ok | Kill after a '### ' sub-heading inside the claim |
| B21 | exit 1 · C1 FIELD-MISSING | exit 1 · C1 FIELD-MISSING | ok | Kill as a bullet '- Kill: ...' |
| B22 | exit 0 · no findings | exit 0 · no findings | ok | near-duplicate 'Target : other' next to Target [contested: near-duplicate is not a key line; silent by grammar] |
| B23 | exit 1 · C1 KEY-DUPLICATE | exit 1 · C1 KEY-DUPLICATE | ok | Target example repeated inside a fenced block in the claim |
| C01 | exit 1 · C0 HEADING-MALFORMED; C0 NO-CLAIMS | exit 1 · C0 HEADING-MALFORMED; C0 NO-CLAIMS | ok | '## C1: claim' colon form |
| C02 | exit 0 · no findings | exit 0 · no findings | ok | '## C01 — claim' zero-padded number is a valid heading |
| C03 | exit 1 · C0 HEADING-MALFORMED; C0 NO-CLAIMS | exit 1 · C0 HEADING-MALFORMED; C0 NO-CLAIMS | ok | '## C1.' trailing dot |
| C04 | exit 1 · C0 HEADING-MALFORMED | exit 1 · C0 HEADING-MALFORMED | ok | '## C1.' followed by valid C2: claim C1 silently dropped |
| C05 | exit 1 · C0 HEADING-MALFORMED | exit 1 · C0 HEADING-MALFORMED | ok | '##  C2' double space |
| C06 | exit 1 · C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE | exit 1 · C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE | ok | '##\tC2' tab after ## with a full C2 body [contested: tab is not 'optional spaces'; C2 absorbed into C1 (six duplicate keys)] |
| C07 | exit 1 · C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE | exit 1 · C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE | ok | '##\u00a0C2' no-break space with a full C2 body [contested: NBSP is not 'optional spaces'] |
| C08 | exit 1 · C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE | exit 1 · C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE | ok | ' ## C2' leading space (not column 0) [contested: column-0 rule; not malformed by grammar] |
| C09 | exit 0 · no findings | exit 0 · no findings | ok | '## C — b' has no digit: silent block end, C2 body dropped [contested: literal grammar: no digit means not a claim heading] |
| C10 | exit 1 · C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE | exit 1 · C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE; C1 KEY-DUPLICATE | ok | '### C2' is a sub-heading: body keys fall into C1 |
| C11 | exit 0 · no findings | exit 0 · no findings | ok | two complete claims both numbered C1 [contested: duplicate claim number has no class in the docstring] |
| C12 | exit 1 · C0 HEADING-MALFORMED; C0 NO-CLAIMS | exit 1 · C0 HEADING-MALFORMED; C0 NO-CLAIMS | ok | '## C1' followed by a tab [contested: trailing tab after a valid heading; grammar says space or EOL] |
| C13 | exit 0 · no findings | exit 0 · no findings | ok | '## C1' followed by spaces |
| C14 | exit 1 · C1 BASE-UNRESOLVED; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING | exit 1 · C1 BASE-UNRESOLVED; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING; C1 FIELD-MISSING | ok | '## C1' example inside a fence, Base 0x40, then the real claim [contested: docstring has no fence rule; the fenced example is parsed as a claim] |
| C15 | exit 1 · C0 HEADING-MALFORMED | exit 1 · C0 HEADING-MALFORMED | ok | malformed '##C9' inside a fence [contested: fence-unaware, per docstring] |
| C16 | exit 0 · no findings | exit 0 · no findings | ok | two claims, CRLF |
| C17 | exit 1 · C0 NO-CLAIMS | exit 1 · C0 NO-CLAIMS | ok | only a '## C — b' heading with keys: no claim |
| C18 | exit 0 · no findings | exit 0 · no findings | ok | heading text contains '## C2' mid-line |
| C19 | exit 0 · no findings | exit 0 · no findings | ok | '## C１' fullwidth digit one [contested: Unicode digit; docstring says 'a digit'] |
| D01 | exit 0 · no findings | exit 1 · C1 COUNTER-DIGEST | false finding | Counter digest in upper case, correct bytes [contested: same digest value in another case; docstring says <64 hex>] |
| D02 | exit 0 · no findings | exit 1 · C1 POPULATION-DIGEST | false finding | Population digest in upper case, correct bytes [contested: same digest value in another case] |
| D03 | exit 1 · C1 COUNTER-DIGEST | exit 1 · C1 COUNTER-DIGEST | ok | Counter digest of 63 hex digits |
| D04 | exit 1 · C1 COUNTER-DIGEST | exit 1 · C1 COUNTER-DIGEST | ok | Counter digest of 65 hex digits |
| D05 | exit 1 · C1 COUNTER-DIGEST | exit 1 · C1 COUNTER-DIGEST | ok | Counter path without sha256= at all |
| D06 | exit 0 · no findings | exit 0 · no findings | ok | Counter path with spaces |
| D07 | exit 0 · no findings | exit 0 · no findings | ok | Counter path with quotes |
| D08 | exit 0 · no findings | exit 0 · no findings | ok | Counter path with unicode |
| D09 | exit 1 · C1 COUNTER-MISSING | exit 1 · C1 COUNTER-MISSING | ok | Counter path absolute '/census/c1.py' |
| D10 | exit 1 · C1 COUNTER-MISSING | exit 1 · C1 COUNTER-MISSING | ok | Counter path 'census/../census/c1.py' [contested: same file by normalisation; docstring says repo path] |
| D11 | exit 0 · no findings | exit 0 · no findings | ok | Counter path './census/c1.py' [contested: same file; git resolves ./ relative to cwd] |
| D12 | exit 1 · C1 COUNTER-MISSING | exit 1 · C1 COUNTER-MISSING | ok | Counter path with trailing slash 'census/c1.py/' |
| D13 | exit 1 · C1 COUNTER-MISSING | exit 1 · C1 COUNTER-MISSING | ok | Counter path is a directory |
| D14 | exit 1 · C1 COUNTER-MISSING; C1 POPULATION-MISSING; C1 CONTROL-MISSING | exit 1 · C1 CONTROL-MISSING; C1 COUNTER-MISSING; C1 POPULATION-MISSING | ok | census is a symlink to a directory: Counter, Population and Control all behind it |
| D15 | exit 1 · C1 COUNTER-SYMLINK | exit 1 · C1 COUNTER-SYMLINK | ok | Counter is a symlink, digest of the link text |
| D16 | exit 1 · C1 COUNTER-SYMLINK | exit 1 · C1 COUNTER-SYMLINK | ok | Counter is a symlink to an absolute path |
| D17 | exit 1 · C1 COUNTER-MISSING | exit 1 · C1 COUNTER-MISSING | ok | Counter is a gitlink (submodule entry) |
| D18 | exit 1 · C1 FROZEN-EDITED | exit 1 · C1 FROZEN-EDITED | ok | Counter regular at freeze, symlink after freeze |
| D19 | exit 1 · C1 COUNTER-SYMLINK | exit 1 · C1 COUNTER-SYMLINK | ok | Counter symlink at freeze, regular after (COUNTER-SYMLINK alone by docstring) |
| D20 | exit 1 · C1 POPULATION-SYMLINK | exit 1 · C1 POPULATION-SYMLINK | ok | Population is a symlink |
| D21 | exit 0 · no findings | exit 0 · no findings | ok | Population with header and one data line (2 non-blank lines) |
| D22 | exit 1 · C1 POPULATION-EMPTY | exit 1 · C1 POPULATION-EMPTY | ok | Population header only |
| D23 | exit 1 · C1 POPULATION-EMPTY | exit 1 · C1 POPULATION-EMPTY | ok | Population whitespace-only data lines |
| D24 | exit 0 · no findings | exit 0 · no findings | ok | Population with invalid UTF-8 and NUL, two lines |
| D25 | exit 0 · no findings | exit 0 · no findings | ok | Population with CR-only line endings |
| D26 | exit 1 · C1 POPULATION-EMPTY | exit 1 · C1 POPULATION-EMPTY | ok | Population whose only line is 'id' plus U+2028 |
| E01 | exit 1 · C1 CONTROL-MISSING | exit 1 · C1 CONTROL-MISSING | ok | Control path is a directory |
| E02 | exit 1 · C1 CONTROL-NOT-RED | exit 1 · C1 CONTROL-NOT-RED | ok | Control is a symlink to a red receipt file [contested: no Control-symlink class in docstring; COUNTER-SYMLINK rationale applied by analogy] |
| E03 | exit 1 · C1 CONTROL-NOT-RED | exit 0 · no findings | false green | Control is a symlink whose LINK TEXT is 'EXIT=1' (no receipt file exists) [contested: by analogy with COUNTER-SYMLINK rationale: link text is not the receipt] |
| E04 | exit 1 · C1 CONTROL-NOT-RED | exit 1 · C1 CONTROL-NOT-RED | ok | Control last line EXIT=0 after an EXIT=1 line |
| E05 | exit 0 · no findings | exit 0 · no findings | ok | Control with trailing blank lines after EXIT=1 |
| E06 | exit 1 · C1 CONTROL-NOT-RED | exit 1 · C1 CONTROL-NOT-RED | ok | Control last line EXIT=-1 [contested: '-1' is nonzero but not digits] |
| E07 | exit 0 · no findings | exit 0 · no findings | ok | Control last line EXIT=01 |
| E08 | exit 1 · C1 CONTROL-NOT-RED | exit 1 · C1 CONTROL-NOT-RED | ok | Control empty |
| E09 | exit 0 · no findings | exit 0 · no findings | ok | Control CRLF with EXIT=1 |
| E10 | exit 1 · C1 CONTROL-MISSING | exit 1 · C1 CONTROL-MISSING | ok | Control absent |
| E11 | exit 1 · C1 CONTROL-NOT-RED | exit 1 · C1 CONTROL-NOT-RED | ok | Control lower-case 'exit=1' |
| E12 | exit 0 · no findings | exit 0 · no findings | ok | Control EXIT with a 26-digit code |
| E13 | exit 0 · no findings | exit 0 · no findings | ok | Control path with a space |
| F01 | exit 2 · no findings | exit 2 · no findings | ok | prereg renamed after freeze: absent at rev |
| F02 | exit 1 · C1 COUNTER-DIGEST; C1 FROZEN-EDITED | exit 1 · C1 COUNTER-DIGEST; C1 FROZEN-EDITED | ok | counter edited after freeze, prereg deleted and re-added naming the edited digest |
| F03 | exit 1 · C1 COUNTER-DIGEST; C1 FROZEN-EDITED | exit 1 · C1 COUNTER-DIGEST; C1 FROZEN-EDITED | ok | same as F02 with a forged older committer date on the re-add (linear history) |
| F04 | exit 0 · no findings | exit 0 · no findings | ok | prereg added, removed, re-added byte-identical after freeze |
| F05 | exit 1 · C1 FROZEN-EDITED | exit 1 · C1 FROZEN-EDITED | ok | counter edited, prereg re-added with the ORIGINAL digest |
| F06 | exit 1 · C1 COUNTER-MISSING | exit 1 · C1 COUNTER-MISSING | ok | counter added after the prereg (not present at freeze) |
| F07 | exit 0 · no findings | exit 0 · no findings | ok | counter edited after freeze then reverted |
| F08 | exit 0 · no findings | exit 0 · no findings | ok | counter mode change only after freeze [contested: blob unchanged; exec bit change is not a content edit] |
| F09 | exit 1 · C1 FROZEN-EDITED | exit 1 · C1 FROZEN-EDITED | ok | counter deleted after freeze |
| F10 | exit 1 · C1 FROZEN-EDITED | exit 1 · C1 FROZEN-EDITED | ok | population changed after freeze |
| F11 | exit 2 · no findings | exit 2 · no findings | ok | --rev is the base commit (prereg not yet added) |
| F12 | exit 1 · C1 FROZEN-EDITED | exit 1 · C1 FROZEN-EDITED | ok | merge brings a post-freeze counter edit from a side branch |
| F13 | exit 0 · no findings | exit 0 · no findings | ok | prereg frozen on a side branch, merged into main later |
| F14 | exit 1 · C1 BASE-NOT-ANCESTOR | exit 1 · C1 BASE-NOT-ANCESTOR | ok | Base is a commit that is not an ancestor (orphan) |
| F15 | exit 1 · C1 BASE-NOT-ANCESTOR | exit 1 · C1 BASE-NOT-ANCESTOR | ok | Base is a side-branch commit (not an ancestor of freeze) |
| F16 | exit 0 · no findings | exit 1 · C1 BASE-UNRESOLVED | false finding | Base is a 7-character abbreviation [contested: abbreviation resolves in git; docstring says FULL40 only for --rev, Base unspecified] |
| F17 | exit 0 · no findings | exit 1 · C1 BASE-UNRESOLVED | false finding | Base is the full sha in upper case [contested: resolves in git; same commit] |
| F18 | exit 1 · C1 BASE-UNRESOLVED | exit 1 · C1 BASE-UNRESOLVED | ok | Base is 40 zeros |
| F19 | exit 1 · C1 BASE-UNRESOLVED | exit 1 · C1 BASE-UNRESOLVED | ok | Base is non-hex 'xyz' |
| F20 | exit 0 · no findings | exit 0 · no findings | ok | Base with trailing spaces |
| F21 | exit 0 · no findings | exit 0 · no findings | ok | Base is an annotated tag object id that peels to the base commit [contested: resolves to the base commit via ^{commit}] |
| F22 | exit 0 · no findings | exit 0 · no findings | ok | prereg path with a space |
| F23 | exit 0 · no findings | exit 0 · no findings | ok | prereg in a subdirectory |
| F24 | exit 2 · no findings | exit 2 · no findings | ok | --prereg '../prereg.txt' |
| F25 | exit 2 · no findings | exit 2 · no findings | ok | --prereg '/prereg.txt' absolute |
| F26 | exit 2 · no findings | exit 2 · no findings | ok | --rev in upper-case hex |
| F27 | exit 2 · no findings | exit 2 · no findings | ok | --rev abbreviated to 12 characters |
| F28 | exit 2 · no findings | exit 2 · no findings | ok | --rev is an annotated tag name |
| F29 | exit 2 · no findings | exit 2 · no findings | ok | --rev is 41 characters |
| F30 | exit 2 · no findings | exit 2 · no findings | ok | --root is not a git repository |
| F31 | exit 2 · no findings | exit 2 · no findings | ok | --root does not exist |
| F32 | exit 2 · no findings | exit 2 · no findings | ok | --root is an empty repository |
| F33 | exit 2 · no findings | exit 2 · no findings | ok | --rev is a side branch without the prereg |
| G01 | exit 1 · C1 COUNTER-MISSING | exit 1 · C1 COUNTER-MISSING | ok | NUL inside the Counter path |
| G02 | exit 0 · no findings | exit 0 · no findings | ok | non-UTF-8 byte in a Target value |
| G03 | exit 0 · no findings | exit 0 · no findings | ok | 1 MB Target value |
| G04 | exit 0 · no findings | exit 0 · no findings | ok | 500 claims |
| G05 | exit 1 · C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE | exit 1 · C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE; C0 DISPATCH-BEFORE-FREEZE | ok | 300 dispatch files before freeze at depth 1 |
| G06 | exit 1 · C0 NO-CLAIMS; C0 FIELD-MISSING | exit 1 · C0 FIELD-MISSING; C0 NO-CLAIMS | ok | empty prereg file [contested: missing Round is FIELD-MISSING C0 (tool-side reading)] |
| G07 | exit 1 · C0 NO-CLAIMS | exit 1 · C0 NO-CLAIMS | ok | Round line only |
| G08 | exit 1 · C0 NO-CLAIMS; C0 FIELD-MISSING | exit 1 · C0 FIELD-MISSING; C0 NO-CLAIMS | ok | whitespace-only prereg [contested: missing Round is FIELD-MISSING C0 (tool-side reading)] |
| G09 | exit 1 · C1 BASE-UNRESOLVED | exit 1 · C1 BASE-UNRESOLVED | ok | NUL byte at the end of a Base value |
| G10 | exit 0 · no findings | exit 0 · no findings | ok | Target value containing '## C2' mid-line |
| G11 | exit 0 · no findings | exit 0 · no findings | ok | unknown key 'Foo:' in a claim |

## Run history (kept for audit)

- Run 1 (`run1-results.tsv`): 152 scenarios, ok 143, false finding 6, false green 3. Of the 6 false findings, 2 were my own errors (G02 harness placeholder bug; C12 expectation missing NO-CLAIMS), so run 1 was not a clean measurement; the same 3 false greens appear in both runs.
- Run 2 (`results.tsv`, `run2-console.txt`, `raw/`): 152 scenarios, ok 145, false finding 4, false green 3, crash 0, hang 0.

## Artifacts (seat)

- `attack.py`: the harness and all 152 scenario expectations (written before the first run; `put()` and C12 corrected between runs as above).
- `results.tsv`: final table with class, contested note, expected and observed exit/findings, attack text, last stderr line.
- `run1-results.tsv`, `run2-console.txt`, `raw/<scenario>.out`: tool stdout and stderr per scenario.
- `_head.md`, `_table.md`, `_tail.md`: the parts this report was assembled from (removed after assembly).

## Verdict

**Falsified in part.** Operability of the landed C2 tool holds for crashes and hangs and for its own `--selftest` (31/31, exit 0), and it is correct on the common grammar, the r41 cases and the digest, symlink, dispatch-name and Base paths the docstring names. It fails open on three paths the docstring does not close:

1. **F1 (E03):** a Control stored as a git symlink, link text `EXIT=1`, passes as a red receipt; exit 0. Attacks CONTROL-NOT-RED (no Control symlink rule exists).
2. **F2 (A21, A22):** `Round: 042` or fullwidth digits silently move the dispatch scan away from round-42; a pre-freeze dispatch file is then clean, against the same repository with `Round: 42` red (A02).
3. **F3 (C09):** a `## C — b` heading silently drops the claim beneath it: `claims=1 findings=0` for two headings.

Plus one named gap that is literal-clean: **A27**, a counter edited between a draft and its rename-in to `prereg.txt` is not detected, because the rename-in commit becomes the freeze.

The two fail-closed deviations (D01/D02 upper-case digests; F16/F17 abbreviated or upper-case Base) are operability costs, not safety holes.

Recommendation for the L1, without editing any frozen file: name F1, F2, F3 and A27 as limits in the round-42 lesson (or route them as defects for round 43). The landed C2 counter's 37 cases contain none of these scenarios, so the target `SUMMARY cases=37 pass=37` is silent on them.

Scratch `/fast/scratch/hyaku/souji-r42/R42w2critic02` is removed after this report; the expectations and raw outputs live in the seat directory.
