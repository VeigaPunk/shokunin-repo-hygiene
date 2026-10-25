STATUS: PASS

# RevSliceVerif — independent second pass over the souji absent-defect slice (8 rows)

Lane: `souji` (掃除). Round 22, attempt 2 (hyaku), wave 1. Leaf seat: no subagent
dispatch. Base lane revision `4edb25dfe262515d0da63224bbba71e02e36cba5` read only.
Access date for every fetch/read below: **2026-10-25**.

Axes named: **calibration** (are the register's classes true of primary bytes),
**operability** (is every row's verdict re-derivable by a reader with the cited
artifact), **coverage** (all 8 rows, no row skipped). No axis was harmed: both
repos read-only, one report plus one TSV written under the named paths only.

## 1. Slice derivation (executed) — and a defect in the frozen-command claim

The preregistration (line 96) says the slice is *"produced by the frozen awk
command in the round report"*. No such awk exists. Executed search:

```
$ grep -rn -E "awk .*(souji|payload-absent)|awk -F'\|'" \
    .ufo/waves/round-22 corpus/lessons/round-22*.md | grep -v w1-spec | grep -v w1-dispatch
(no slice-generating command; only per-seat extractions in w1/evidence)
```

The preregistration itself contains no awk either (independently confirmed by
`Slice123.md` § "Row under test"). I therefore derived the slice by the
field-4 id rule the seat prompts prescribe, over both register tables:

```
$ awk -F'|' '/^\| `souji` \|/{gsub(/`/,"",$4); if ($4!="") print $4}' \
    /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
S114
S123
S124
S126
S131
S133
S138
S118
```

Committed slice ids (`census/round-22/attempt2/quarantine-slice`), same 8:
`S114 S123 S124 S126 S131 S133 S138 S118``. The committed eighth id carries a
stray trailing backtick because the register's never-checked table has a
malformed id cell (`S118`` `) and a prose class cell. The id **set** matches;
the derivation is reproducible only by field-4 selection, not by a frozen
command. Recorded as finding F1.

## 2. Method

- Web: `curl -fsSL -m 30`, each source saved under
  `.ufo/waves/round-22/attempt2/w1/evidence/rev-*` (see §4 for hashes).
  Follow-up status probe: all six content URLs `http=200`; the S118 DOI chain
  ends `http=202 bytes=0`.
- Local payloads: read under `/home/vgpnk/Projects/shokuknow/lanes/souji/`
  (read-only), sha256 recorded.
- Matching: whitespace-collapsed literal containment; for HTML also a
  tag-strip **without** inserting separators (so inline `<code>` spans join as
  the reader sees them). The separator-inserting strip is what makes the web
  forms look different from the man-page forms; it is a measurement artifact,
  not a payload difference.
- Man pages: `man … | col -b` on git 2.56.0 (2026-09-27), and the man7 HTML
  for `rename(2)` (Linux man-pages 6.19).

## 3. Per-row verification (executed)

| id | class | cited source | located span / locator | verdict basis |
|---|---|---|---|---|
| S114 | `accepted` | `https://git-scm.com/docs/git-prune` | man `git-prune(1)` **DESCRIPTION** lines 22–23: `Note that unreachable, packed objects will remain. If this is not desired, see git-repack(1).` | Fetched page 200, 27870 B: raw `<p>… see <a href='/docs/git-repack'>git-repack[1]</a>.</p>`. The claimed string is verbatim in the installed manual (the Gate's own label: "installed man page git 2.56.0, § DESCRIPTION"), and differs on the page only in the asciidoc reference token `(1)`→`[1]`. Correction stated: cite the man-page form, or write `[1]` when quoting the URL. |
| S123 | `accepted` | `lanes/souji/round2/evidence/r23-trigger-prune.out` | `git-worktree(1)` **SYNOPSIS** line 12; page `https://git-scm.com/docs/git-worktree` **§ SYNOPSIS** | Claimed span `git worktree prune [-n] [-v] [--expire <expire>]` → **0 matches** in the cited `.out` (sha256 `510722c1…`) and 0 in the fixture `.sh`; **verbatim** in the man page and on the page (no-separator tag strip). The Gate named this URL as "upstream semantics"; the register collapsed the citation onto its local `URL:` field. Correction: re-cite to `git-worktree(1)` § SYNOPSIS (the Gate says § OPTIONS — wrong section). |
| S124 | `accepted` | `lanes/souji/round2/evidence/noreplace-probe.out` | `.out` line 2; `rename(2)` **DESCRIPTION** `RENAME_NOREPLACE` | Claimed line as written is **not contiguous**: the real line is `/home/vgpnk/Projects/shokunin\tfstype=btrfs\tNOREPLACE_new=0(ok)\tNOREPLACE_existing=-1(EEXIST)\tplain_overwrite=0(ok)` — the quote drops `NOREPLACE_new=0(ok)`. Second fragment `Don't overwrite newpath…` is verbatim in man7 `rename(2)` (200, 23571 B), absent from the payload. Correction: restore the intervening field; attribute fragment 2 to `rename(2)` § DESCRIPTION. |
| S126 | `present` | `https://docs.gtk.org/gio/method.File.trash.html` | **Description**, first paragraph | `Sends file to the “Trashcan”, if possible. This is similar to deleting it, but the user can recover it before emptying t` is a **verbatim prefix** of the page sentence (the register's truncation ends mid-word). No correction needed; the register's `payload-absent` is contradicted. |
| S131 | `accepted` | `lanes/souji/round2/evidence/r23-worktree-census.out` | `git-worktree(1)` **OPTIONS `-n, --dry-run`**, rendered lines 217–218 | Claimed span → **0 matches** in the cited census (sha256 `1ac71c4f…`); verbatim in the installed man page. The web page renders it as `-n --dry-run` (two separate `<dt>` nodes, comma not rendered), so the man page is the exact home. The census's own line `prune --dry-run --expire now: (no output — none prunable)` supports the row's claim. Correction: cite `git-worktree(1)` OPTIONS. |
| S133 | `accepted` | `lanes/souji/round3/evidence/r24-renameat2-probe.out` | `rename(2)` **DESCRIPTION `RENAME_NOREPLACE`** | Claimed span → **0 matches** in the probe (sha256 `a53f1e30…`); **verbatim** in man7 `rename(2)` (whitespace-collapsed, two spaces after "Don't"). The probe's `SUMMARY: every writable mount implements RENAME_NOREPLACE` supports the row's claim. Correction: re-cite the prose to `rename(2)` § DESCRIPTION. |
| S138 | `present` | `https://qiita.com/koseki/items/f1af58f1ec1693f0536a` | item markdown body **line 11**; rendered page `<h2>` | `## gc.auto (6700)` is **verbatim at line 11** of the item's `body` returned by `https://qiita.com/api/v2/items/f1af58f1ec1693f0536a` (200, 16825 B). The HTML render (200, 129655 B) carries `gc.auto (6700)` under `<h2>` and no `##` marker. The quoted bytes are the article's own markdown source, so no correction to the quote is required. |
| S118 | `unverifiable` | `https://doi.org/10.1109/SEQUEN.1997.666900` | — | DOI → `ieeexplore.ieee.org/document/666900`, final **HTTP 202, content-length 0**, `x-amzn-waf-action: challenge`; body sha256 `e3b0c442…` (empty). No quote was ever checkable; unreachable is not fabrication. |

All eight ids carry one frozen class. Classes: 5 `accepted`, 2 `present`,
1 `unverifiable`, 0 `refused`.

## 4. Snapshots (sha256, executed)

| file under `w1/evidence/` | bytes | sha256 |
|---|---|---|
| `rev-git-scm.com_docs_git-prune.html` | 27870 | `5d3dcd3b6588ce51b3cd0afee20f9a17e9f1f071f768e438244e7320fc34de88` |
| `rev-git-worktree.html` | 98918 | `fa25690b04900cfc1f1b52bb6b23a85d63f8b763477cca71e655434adbfc63d2` |
| `rev-man7-rename.2.html` | 23571 | `8772946a809a0db54f4854f200908f10bee758ea452e8df5efd955bc3b8e6e57` |
| `rev-docs.gtk.org_gio_method.File.trash.html.html` | 19401 | `a5af1920b16444e0a03d30fcf77de0389533bcedb7243175c915b34c38c21cf3` |
| `rev-qiita.com_koseki_items_f1af58f1ec1693f0536a.html` | 129655 | `ecefaf6c7249630ab0a8abd4c496d4be04f2169e705b1bd67445067cf1cbd496` |
| `rev-qiita-item.json` | 16825 | `bf7ddd62859a309b6da3e5304a8f6d029689cc4b52ceb452d48bbbc6824ca68a` |
| `rev-doi-S118.headers` / `.body` | 1749 / 0 | `40b24280…f346` / `e3b0c442…b855` |

Payload hashes (read-only): `r23-trigger-prune.out` `510722c1…e069b4`,
`noreplace-probe.out` `1634d206…be8bb5`, `r23-worktree-census.out` `1ac71c4f…9392fd`,
`r24-renameat2-probe.out` `a53f1e30…4b0809`. Two of my fetches reproduce
first-pass snapshots byte-for-byte (`git-prune` and `rename(2)`), i.e. the
sources are stable across independent fetches.

## 5. First-pass comparison (recorded after my own derivation)

Reports exist for all 8 rows (`Slice114.md`, `Slice123.md`, `Slice124.md`,
`Slice126.md`, `Slice131.md`, `Slice133.md`, `Slice138.md`, `Slice118.md`);
`Slice114.md` appeared at 03:48 after the rest of the wave.

| id | first-pass report | committed `slice-verdicts.tsv` | mine | relation |
|---|---|---|---|---|
| S114 | `accepted` | `accepted` | `accepted` | **agree** |
| S123 | `refused` | `refused` | `accepted` | **disagree** |
| S124 | `accepted` | `accepted` | `accepted` | **agree** |
| S126 | `present` | `present` | `present` | **agree** |
| S131 | `refused` | `accepted` | `accepted` | **disagree with report; agree with TSV class** |
| S133 | `accepted` | `accepted` | `accepted` | **agree** |
| S138 | `present` | `accepted` | `present` | **disagree with TSV; agree with report** |
| S118 | `unverifiable` | `unverifiable` | `unverifiable` | **agree** |

### S123 — `accepted` is right, `refused` is wrong

The first-pass report itself establishes the fact that decides it: the span is
"verbatim in both sources" (`git-worktree(1)` and
`https://git-scm.com/docs/git-worktree`), and it calls the defect "a
citation-class defect, **not a fabrication**". It then refuses. That is
internally inconsistent: `refused` is the class for **payload absent / a
citation that cannot be repaired within the row's own Gate**; here the row's
own Gate names `https://git-scm.com/docs/git-worktree` as the span's source,
and I re-fetched that URL and found the span verbatim in § SYNOPSIS. The
register's note "the quote is in none of them" is therefore false — the
register, not the row, is wrong. `accepted` (correction = re-cite § SYNOPSIS,
not § OPTIONS) records exactly that. Majority is irrelevant; the bytes decide.

### S131 — `accepted` is right; the report's `refused` contradicts its sibling

`Slice131.md` argues that `accepted` is unavailable because the *quote text*
needs no correction, only the citation. `Slice133.md` — same defect shape
(man-page prose cited against a local probe) — accepts on exactly that ground
("the row's quote stands unchanged; correction stated"). Both cannot be right.
The sibling is right: the frozen `accepted` covers "quote corrected, correction
stated", and re-pointing the citation while stating it is a correction of the
row's evidence claim; refusing would assert an absence that primary bytes
disprove (`git-worktree(1)` OPTIONS lines 217–218). Note the committed TSV
already carries `accepted`; the committed TSV and the seat report disagree, so
the class in the committed artifact is not the class its own report supports.

### S138 — `present` is right; the TSV's `accepted` overstates a correction

The exact quoted string is line 11 of the item's markdown `body` (official API,
same item id). No textual correction is needed, so `accepted` (which implies
one) is the wrong label; `present` is exact. The only mismatch is between the
markdown marker `##` and the rendered `<h2>` — a matcher limitation, not a quote
defect. If one insists the cited source is only the rendered HTML, `accepted`
would be arguable, but then S114's `accepted` and S138's `present` would be
labelled by different standards (S114 is accepted even though the man page,
not the URL, carries its exact form). `present` is the consistent choice.

## 6. Findings (severity order)

**F1 — MEDIUM (calibration/operability).** The preregistration claims the slice
is produced by "the frozen awk command in the round report"; no such command
exists in `corpus/lessons/round-22.md`, the preregistration, or
`.ufo/waves/round-22` (executed grep). C2's slice is re-derivable only by
field-4 id selection, not by a frozen command. A third party cannot reproduce
the derivation without inventing the command. Fix: record the awk in the round
report (or drop the "frozen" claim).

**F2 — MEDIUM (calibration).** First-pass classes are inconsistent across
identical defect shapes, and the committed TSV disagrees with two of its own
seat reports: `S131` report `refused` vs TSV `accepted`; `S138` report
`present` vs TSV `accepted`. The slice predicate counts any of the four
classes, so the gate counter is unaffected (`slice_verdicts=8/8` stays true),
but the committed TSV is not a faithful transcription of the hand-checks it
cites. Fix: reconcile the two rows from the seat reports and state the
accepted/refused boundary once, in the preregistration.

**F3 — LOW (calibration).** All seven `payload-absent` labels in this slice are
contradicted by primary bytes: the quoted text exists in the cited source
(S126, S138), in the row's Gate-named companion (S123, S124 span 2, S131, S133),
or in the cited URL modulo one reference token (S114). The register's
"fabrication class" produced 7/7 false positives here. The register's own
legend says a candidate is "not a verdict"; this slice is the proof. Do not
promote register classes into a verdict without a hand-check.

**F4 — LOW (coverage).** The register's never-checked table is malformed: the
S118 row has a stray backtick in the id cell and a prose class cell, so the
committed slice carries `S118`` and any extractor keyed on field 4 must strip
backticks. My derivation (strip) and the committed file (no strip) differ in
the eighth id token only.

**F5 — LOW (calibration).** S114's quote cell duplicates the same sentence
twice, inflating the register's ABSENT quote count for one row (2 quotes, 1
row). S126's quote is truncated mid-word (`…emptying t`), which is what the
quote-lint display produced; the truncation is a display artifact, not a bad
quote.

**F6 — LOW (operability).** Locator drift one level below the register:
`SOURCES-PROPOSED.md:44` (S123) says § OPTIONS for a **SYNOPSIS** line;
`SOURCES-PROPOSED.md` S131 Gate says § OPTIONS correctly for the man page, but
the web page's § OPTIONS renders the option as two `<dt>` nodes (`-n`,
`--dry-run`) so the comma in the quote is not present there. Cite the man page
when quoting man-page text.

**F7 — INFO.** `[INFERENCE]` The census's matcher appears to (a) strip tags
with a separator, so inline `<code>` joins gain spaces, and (b) strip tags but
not markdown heading markers. That would explain every row's ABSENT signal. I
did not inspect or run the fold implementation (`absent-defect-register.py`),
so this is inference, not a measured cause.

## 7. Residual risk and verification gaps

- I did not run `tools/souji-gate-check.py`. The C2 counter and the
  `slice_verdicts` count are outside this seat's assignment; my TSV is evidence,
  not the committed verdicts file.
- I did not re-derive the eleven folds of the quote census, so F7 is inference.
- The `git-worktree` web page is the same document as the installed man page but
  not byte-identical; my claim that the S123 span is "verbatim on the page"
  rests on the no-separator tag strip and on the raw `<code>` nodes (the raw
  HTML fragment for S131 shows the `<dt>` split, which is why the comma is
  absent there). Both are recorded in the snapshots.
- S118's unreachability is publisher-side (WAF challenge), not a transient
  network fault; a future reader should re-try, but no re-try can be promised to
  succeed. `unverifiable` remains the only honest class.

## 8. Compliance

Read-only on `/home/vgpnk/Projects/shokuknow` and on the lane repo outside the
two named write paths. Writes: this report,
`.ufo/waves/round-22/attempt2/w1/RevSliceVerif.md`, and the named evidence file
`.ufo/waves/round-22/attempt2/w1/evidence/RevSliceVerif.tsv` (8 rows, 3
columns, classes `accepted|present|unverifiable` only), plus web snapshots
under the same evidence directory. No git/jj writes, no commit, no index or
`.ufo/state`/`watchdog.log`/`MANIFEST.json`/`templates`/`scripts` writes, no
sibling-repo writes, no signals, no deletion authority created, no campaign
tool run in `shokuknow`. No tool installed or upgraded.
