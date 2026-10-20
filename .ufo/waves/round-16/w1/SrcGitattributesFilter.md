# SrcGitattributesFilter — gitattributes(5) `filter` section, bound-filter status skip

Seat: SoujiR16.SrcGitattributesFilter (scout, leaf). Item: open gitattributes docs, extract the
`filter` attribute section and a ≤25-word quote grounding the bound-filter status skip; read
`corpus/SOURCES.md` and draft the row. No edits outside this report.

## Axes (godspeed)

- A1 coverage — the `filter` section's execution points (checkin/checkout/process), the
  no-op-passthru and `required` rules, and the attributes-source precedence the census guard
  depends on.
- A2 calibration — separate what the page says from what the guard assumes. The page does **not**
  say `git status` re-hashes through the clean driver; two full-text sweeps (gitattributes 2.56.0,
  git-status 2.53.0) located no such sentence. The skip is a deliberate conservative guard, not a
  documented status behaviour.

## Access record

- URL: https://git-scm.com/docs/gitattributes
- Access date: 2026-10-20.
- Served version line (page header, version selector): `Latest version ▾ … gitattributes last
  updated in 2.56.0`; the 2.56.0 entry is stamped `2026-09-28`. No older/newer stamp on the body.
- Section read: `## EFFECTS` → `### Checking-out and checking-in` → `#### filter`, including
  `#### Long Running Filter Process`, `#### Delay`, and `#### Interaction between checkin/checkout
  attributes`; plus `## DESCRIPTION` (precedence), `## NOTES` (symlink), `## EXAMPLES`.

## Observed facts (quotes verbatim, whitespace normalized; word counts = whitespace tokens)

1. **Filter driver shape and direction.** "A filter driver consists of a `clean` command and a
   `smudge` command, either of which can be left unspecified." Clean is checkin-direction, smudge
   is checkout-direction.
2. **Primary grounding quote for the bound-filter status skip (13 words):**
   > "In the check-in codepath, the worktree file is first converted with `filter` driver"
   With the doc's own continuation, 19 words: "In the check-in codepath, the worktree file is
   first converted with `filter` driver (if specified and corresponding driver defined)".
   This is the shortest sentence that grounds "worktree content is handed to a config-named
   program before Git hashes it".
3. **Checkout direction (15 words):** "Upon checkout, when the `smudge` command is specified, the
   command is fed the blob object" (doc continues: "…from its standard input, and its standard
   output is used to update the worktree file").
4. **Process precedence (19 words):** "If a long running `process` filter is configured then it
   always takes precedence over a configured single blob filter".
5. **Failure is passthru unless required (19 words, ellipsis marked):** "A missing filter driver
   definition in the config … is not an error but makes the filter a no-op passthru." The page adds
   that `filter.<driver>.required=true` makes non-usable content an error.
6. **Status shows what checkin conversion would change (6-word comment):** the CRLF example script reads
   `$ git status        # Show files that will be normalized`; the following paragraph says files
   that "should not be normalized show up in *git status*". This is the only place the page links
   status to the check-in conversion, and it is about `text`, not `filter`.
7. **Order of conversions:** checkin = `filter` → `ident` → `text`; checkout = `text` → `ident` →
   `filter` (`#### Interaction between checkin/checkout attributes`).
8. **Attributes precedence used by the guard:** "Git consults `$GIT_DIR/info/attributes` file
   (which has the highest precedence)", then `.gitattributes` from the path's directory up to the
   toplevel, then global (`core.attributesFile`, default `$XDG_CONFIG_HOME/git/attributes`), then
   system; checkout uses the index copy first, then the worktree copy.
9. **Symlink note (15 words):** "Git does not follow symbolic links when accessing a
   `.gitattributes` file in the working tree." (`## NOTES`).

## Calibration findings

- **The page does not document a status-time driver run.** A full-text sweep of the served
  gitattributes page for `status` returns the nav link plus lines 457/461 of the fetched text (the
  CRLF example above); the `filter` section never mentions `git status`. The served git-status page
  (its header: "git-status last updated in 2.53.0", opened 2026-10-20 for this check only) contains
  no `clean`/`filter`/`re-?hash` text; its `BACKGROUND REFRESH` section documents only that status
  refreshes and writes the index. [INFERENCE] A worktree-vs-index comparison of a filtered path
  must reproduce the check-in conversion to be meaningful, so a bound `clean` can be executed by
  status-like consumers; the census guard's response is to not run status at all, which is safe
  regardless. Do not upgrade this to a documented claim without a source that says it.
- **The guard is stricter than the passthru rule.** Per fact 5, a defined driver that exits
  non-zero is a no-op passthru, so skipping status is over-conservative — but the command text is
  still executed, so the skip is the only guarantee that no config-named program runs. Fine as a
  restriction; not evidence that the filter's output would change any count.
- **`check-attr` is not covered here.** The guard's binding test (`git check-attr -z --stdin
  filter`, tools/souji-census.sh:922-925) and its `-c core.attributesFile` override are
  `git-check-attr(1)` semantics, not claimed by this row; that is SrcGitCheckAttr's scope.

## Guard cross-check (read-only)

Measured file: tools/souji-census.sh, HEAD `cbf688a`, sha256
`fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`.

- Contract comment: `tools/souji-census.sh:98-101` ("A filter.<name>.clean|smudge|process driver
  that an attributes source binds to a tracked path skips status for that repository only
  (status-unverifiable; stderr `status-skipped`); the driver never runs.").
- Inert-driver rationale: `tools/souji-census.sh:643-645`.
- Implementation: `guard_bound_filters` at `:907`, driver-key regex `^filter\..*\.(clean|smudge|process)$`
  at `:911`, empty-value skip at `:913-915`, binding test at `:922-925` (bounded by
  `-c core.attributesFile="$attrs"`), skip path at `:939-943` (`status-skipped`, count
  `unverifiable`), status invocation below it at `:949`.
- Matches facts 1, 4, 8 above. Note `smudge` alone also triggers the skip although status is not a
  checkout path — conservative, not a defect in the guard's stated boundary.

## Proposed registry row (do not apply here; L1 renumbers)

Next free id after S042 is **S043**. One row for this document, following the S042 precedent
(multiple anchors of one document share one row rather than counting subsections as growth).
Siblings may propose the same number; I claim only "this row", L1 assigns the final id.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S043 | gitattributes(5) — https://git-scm.com/docs/gitattributes | docs | A | git 2.56.0 `filter` driver execution points, passthru/required rule and attributes-source precedence, not a statement that `git status` itself runs a driver | § EFFECTS › Checking-out and checking-in › `filter` (clean/smudge, Long Running Filter Process, Delay); § Interaction between checkin/checkout attributes; § DESCRIPTION attributes precedence with `core.attributesFile`; § NOTES symlink rule; web page last updated in 2.56.0 (selector stamp 2026-09-28), opened 2026-10-20 | check-in converts the worktree file with the `filter` driver first (then `ident`, `text`) and check-out feeds the blob to `filter` last; `process` outranks clean/smudge; a missing driver or non-zero exit is a no-op passthru unless `filter.<name>.required`; `$GIT_DIR/info/attributes` outranks tree, global and system attribute files; `.gitattributes` symlinks are not followed | mined | 2026-10-20 | on-release | tools/souji-census.sh `guard_bound_filters` (cbf688a); corpus/lessons/round-16.md (planned) |

- tier/status rationale: primary vendor documentation for a git feature, same channel and tier as
  S042; `mined` because the quoted semantics are located and used by the guard; `recheck:
  on-release` because the page is version-stamped and changes only with git releases.
- `used-by` caveat: `corpus/lessons/round-16.md` did not exist at scout time
  (`ls corpus/lessons/round-16.md` → No such file). L1 must confirm or repoint that cell; the
  script cell is exact at `cbf688a`.
- No second row for git-status: the page was opened only to test the status-re-hash wording and
  found nothing; a git-status(1) row belongs to SrcGitStatusRejected / routed defect R7. Its
  `BACKGROUND REFRESH` wording (status writes the refreshed index by default) corroborates
  S036's explicit "does not forbid mandatory writes" limitation; recorded here, not registered.

## Remaining unknowns

- Whether the installed git 2.55.0 `git status` invokes a bound clean driver, and under which stat
  states. Not answerable from this page; resolving it needs tagged source (`wt-status.c` /
  `read-cache.c`) or an executed probe, and probes are forbidden this wave.
- `git-check-attr(1)` handling of `-c core.attributesFile` and `$GIT_DIR/info/attributes`
  (SrcGitCheckAttr).
- Whether an attributes file reached only through the index fallback (`.gitattributes` absent from
  the worktree) binds a driver the same way in the guard's `check-attr` call — page states the
  fallback, guard reads only the worktree-side effective file.

STATUS: no known failure in this scope; gitattributes 2.56.0 documents no status-time driver
invocation (full-text sweep), so C1's status skip must be described as a conservative guard, not a
doc-mandated re-hash.

## Commands

- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i 'filter' tools/souji-census.sh | sed -n '1,80p'`
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse --short HEAD && sha256sum tools/souji-census.sh`
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'status' artifact://20326 2>/dev/null | sed -n '1,40p'; echo '---'; ls corpus/lessons/round-16.md corpus/QUALITY.md corpus/SOURCES-CONTRACT-v1.md 2>&1`
- `cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'filter\|attributes' tools/souji-census.sh | sed -n '1,60p'; echo '---'; grep -c . corpus/SOURCES.md`
- `cd /tmp && printf '' >/dev/null; curl -fsS https://git-scm.com/docs/git-status -o /var/tmp/souji-r16-srcgitattributesfilter-status.html && python3 - <<'PY' … PY` (last-updated line and regex sweep for `re-?hash|clean filter|stat info|refresh`)
- `cd /var/tmp && python3 - <<'PY' … PY` (full-text sweep of the same file for `hash|clean|filter|convert|stale|racy`)

Residue: `/var/tmp/souji-r16-srcgitattributesfilter-status.html` (the fetched git-status page used
for the negative check only). Left in place because `rm` is outside this seat's allowed command
list; L1 may remove it. Nothing was written inside the repo except this report.
