# CritC2Counter — fixture index (round 22, attempt 2, w1)

All fixtures are executed against the lane's own checker, read-only in the lane:

    python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-gate-check.py \
        --root <fx-root> --round-date 2026-10-25 \
        --entries <entry...> --snapshot-dir <snapdir> \
        --slice <slice> --slice-verdicts <verdicts.tsv>

Tool sha256 measured: d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00
(lane HEAD d6a75ba; the counter is unchanged across 3216c19..d6a75ba).

| path | what it is |
|---|---|
| `attack-log.json` | 24 executed cases: argv, rc, stdout/stderr |
| `fx/F0` | fully fabricated root: fabricated SOURCES.md, two entries whose only evidence is an authored snapshot, 8-id slice with 8 `refused` rows and evidence `x` |
| `fx/Q1` | authored snapshot named `man7-rename.2.txt` holding a fabricated quote; Gate cites the real man7 URL + `opened: 2026-10-25` |
| `fx/Q2` | `seam.txt` = committed `man7-mv.1.txt` bytes + `\n` + committed `man7-rename.2.txt` bytes; quote spans the seam (in neither document alone) |
| `fx/Q2c` | `excerpt.txt` = one real line of `man7-mv.1.txt` then one real sentence of `man7-rename.2.txt`; entry quotes the spliced span; `q2c_punct.md` is the same quote with one appended `.` (the discriminating control) |
| `fx/Q3` | quote whose own words contain the locator token `section`; no external locator |
| `fx/Q4` | `ADMIT:` with no quote/locator/snapshot/reason, plus `- REJECT: —` |
| `fx/Q5` | `sources/alias.txt` symlink → `../../../../../../..../CritC2Counter/injected-uncommitted.txt` (outside the snapshot dir, outside the repo, uncommitted) |
| `fx/Q6` | slice variants: `slice-verdicts.tsv` (8 real ids, 8 refused, pointer `x`), `slice-verdicts-7of8.tsv` (missing one row → `fail=0` with exit 1), `slice-verdicts-extra-row.tsv` (invented S999 row), `slice-empty` + `quarantine-slice` cleared for the no-floor case, plus the 4-id and two-ids-on-one-line variants |
| `fx/Q7` | honest double-quoted term `"Path"` inside a REJECT reason that also contains the locator word `heading` |
| `fx/Q8` | `url: https://example.invalid/never-opened` with `opened: 2026-10-25` inside an HTML comment |
| `entries_outside_root/q9.md` | entry at an absolute path outside `--root`, quoting the committed `gtk-filetrash.txt` under the gio(1) URL, scored against the lane's real slice/verdicts |
| `man7-*.html`, `arch-gio.1.html`, `gtk-filetrash.html`, `freedesktop-trash.html` | live fetches (2026-10-25, HTTP 200) used to test whether the cited URL's real text contains the quote |
| `real-slice-copy.txt` | byte copy of `census/round-22/attempt2/quarantine-slice` (sha256 12d3c325…da7e6) used by F0/Q6a |
| `injected-uncommitted.txt` | bytes reachable only through the Q5 symlink |

Provenance cross-check (the check the frozen predicate does not perform): the six
committed `*.raw` snapshots are byte-identical to the live pages fetched today —
`cmp` returned IDENTICAL for all six; `vendor-noreplace-probe.out` sha256 is
1634d206…8bb5, equal to the digest the r23 entry declares.
