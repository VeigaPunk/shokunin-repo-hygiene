STATUS: DONE — minimal LG-DANGLING-PTR grammar and implementation sketch delivered; calibrated at b576341: 7 finding rows / 2 distinct paths, both routed real defects, 0 false positives after 3 exact exemption rows. Two integration items must be scheduled before the round tip can be green: the Q25(b) r14 `measured_commit` finding, and the base-rev counting command (the CLI exits 2 there by design).

# Verdict

- **Grammar: holds.** A five-prefix token grammar plus three exact exemption rows catches both known defects and nothing else on the b576341 tree. The two cruder alternatives measured (any `.ufo/` path; whole-LOG scan) each add only false positives.
- **Sketch: minimal.** One new regex, one tuple, one helper, one new finding id, three counters, no new CLI flag, no new subprocess, no new import. Historical replays stay identical because the branch is gated `round >= 18` and its counters are serialized conditionally.
- **Calibration: holds.** At b576341, after the proposed TSV is applied, every unresolved citation is `census/round-17/gate-replays-ddb7347.json` or `census/round-17/jj-receipts-ddb7347.txt`. Precision 7/7 rows (2/2 distinct paths), recall 2/2. The six deliberate citations in the same tree are suppressed by three exact TSV rows, not by prose.
- **C2 as a whole: partial until F1/F2 are fixed.** F1 (r14 measured_commit) makes the changed gate red at round 18 even after the two pointer fixes; F2 is a measurement-protocol problem, not a code problem.

# 1. Normative grammar (the whole rule set)

## G0 — Surface

At REV, scan exactly:

| source | selection | absence |
|---|---|---|
| fixed authority | `SKILL.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md` | `EvalError` (exit 2): a declared authority surface must not silently shrink |
| knowledge | every `corpus/knowledge/*.md` blob in the REV tree | zero files is allowed; the `checked_ptrs` counter exposes it |
| lesson | `corpus/lessons/round-<N>.md` if present at REV | absent = zero tokens (pre-landing revisions) |
| LOG | every `##` section whose heading matches `\bround <N>\b` (case-insensitive), each ending at the next `##`; `###` subsections stay inside | no matching section = zero tokens |

LOG line numbers stay **absolute file lines** (scan the full `LOG.md` blob and select line ranges, or pass an offset). My first sweep reported `LOG.md:3` for the section-relative line; the correct report is `LOG.md:946` (section starts at 944). That is a reporting bug, not a count bug.

`corpus/knowledge/*.tsv` is deliberately not scanned: the spec says `*.md`; the only `.tsv` (`obsidian-ledger.tsv`) yields zero prefixed tokens at b576341, so the exclusion changes nothing today and keeps the rule exact.

## G1 — Token

```python
DANGLING_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])"
    r"((?:\.\./)*(?:census|tests|tools|corpus|\.ufo/waves)/"
    r"[^\s`'\"()\[\]|;:#?=]+)"
)
```

- The five prefixes are the whole namespace; nothing else is a pointer claim.
- The negative lookbehind blocks mid-word matches. After the match, reject a **bare** match (does not start with `../`) whose preceding character is `/`; that removes `souji-shokunin/census/...`, `fleet-census/scripts/...`, and URL path segments without a URL parser.
- `:` is a terminator. That is the entire `path:line` rule: `:12`, `:15-16`, `:18-19, 22-24, 31-32`, `:167,180,185` all stop at the colon. No line-list grammar, no line-range validation.
- Strip trailing `,`/`.` while braces are balanced. This handles a comma after a table cell or sentence; it does not touch `{base5fa6017,ddb7347}.txt`.
- Deduplicate `(citing_file, line, token)` for both counters and findings. At b576341 this removes repeated same-line mentions such as `tools/souji-verify.sh` in `SKILL.md:145`; unique citations are 346 (Surface B), expanded occurrences 360.

## G2 — Skip

Skip, without evaluation, a token that:

1. contains `<`, `>`, `*`, or `$` (placeholders, globs, shell variables);
2. contains the literal `round-N`;
3. has unbalanced `{`/`}`;
4. contains `..` **after stripping leading `../`** unless it matches a round range (`round-{a..b}` or `round-a..b`).

Measured at b576341: 10 occurrences / 6 forms in Surface B (9 / 6 in Surface A). Exact forms: `census/round-14/verification*.json`, `census/round-17/jj-receipts-*.txt`, `census/round-<N>/`, `census/round-<N>/seat-audit-<wave>.json`, `census/round-N/<new>.json`, `tools/<tool>.sh`.

## G3 — Expand

Only two expansions exist:

1. round range, braced or bare, **inside a captured token**: `round-{1..11}` / `round-6..11` -> consecutive integers. Scope: `round-a..b` only. The prose ranges `round-17..22` and `round-14..53` in `SKILL.md:79,182` are not path tokens and are never captured; no special prose guard is needed.
2. one simple `{a,b}` level, body containing no `..` and no nested braces. `{one.txt,inner/keep.txt}` splits textually; slashes in alternatives are fine.

Do **not** expand generic numeric ranges (`{seat-01..64.json,...}`). At b576341 the only such form is in the whole-LOG round-3 entry and is unbalanced; expanding it would invent 64 phantom paths.

Measured: 5 raw tokens expand to 18 paths (Surface B): the two round ranges (11+6), `jj-receipts-{base5fa6017,ddb7347}`, `seat-audit-r16-replay-{base5fa6017,4f48343}`, and `{one.txt,inner/keep.txt}`. All 18 resolve.

## G4 — Normalize

- A token beginning with one of the five prefixes is **repo-root-relative** regardless of which authority file cites it.
- A token beginning with `../` is resolved relative to the citing file's directory with `os.path.normpath`. If the result still starts with `..`, it escapes the lane and is a fleet candidate. This is what makes `corpus/README.md:216` (`../census/round-17/jj-receipts-ddb7347.txt`) a real finding rather than a skip.
- `./` is not supported; zero occurrences at b576341. If it appears later, it is a finding until the rule is extended.

## G5 — Resolve

A normalized path resolves iff it is a blob in the REV tree **or** a directory prefix derived from the REV tree. Directory citations are legitimate: 22 unique citations (17 distinct tokens) resolve only as directories in Surface B (e.g. `corpus/knowledge/`, `census/round-16/transcripts`, `tests/fixtures/r13-cert-frozen/`). A file-only rule would produce 22 false-positive rows. No content read, no line-range check, no symlink/submodule special case.

## G6 — Exempt

Read `corpus/pointer-exemptions.tsv` from the REV tree if present; absent = empty set. Format:

- `#`-leading lines and blank lines ignored;
- every other line must be exactly `<path>\t<reason>` (one literal TAB), both non-empty;
- path must be relative, no `..`, no absolute; trailing `/` ignored on both sides;
- a malformed row is `EvalError` (exit 2), never a silent skip;
- matching is exact on the normalized path, after lane resolution fails and before fleet classification. No prefix or glob matching.

## G7 — Fleet

`fleet_root = os.path.dirname(os.path.abspath(root))`. After a lane miss (and after exemption), if `os.path.exists(os.path.join(fleet_root, path))`, count the citation as `fleet`; do not emit a finding. No git read of the fleet repo, no HEAD binding. Fleet classification is advisory: it changes no exit code, and `ptr_fleet` makes the demotion visible. Measured: 4 unique citations / 3 distinct paths at b576341 (Surface B), all under `.ufo/waves/hyaku/jj-w1/reports/`.

## G8 — Finding

```
LG-DANGLING-PTR<TAB>citing-authority-file<TAB>line <N>: <token> absent at <rev12>
```

One row per unique `(file, line, token)` citation. The citing file is the path field (consistent with `LG-SEAT-UNCARRIED`, which reports the report file and puts the line in the detail). Any finding makes the gate exit 1. A missing/renamed authority file, an unreadable blob, or a malformed TSV is exit 2.

## G9 — Gating, counters, replay safety

- Run only when `round_no >= 18`.
- Add three counters only when the branch ran: `checked_ptrs` (unique citations evaluated), `ptr_exempt`, `ptr_fleet`. A zero `checked_ptrs` means the surface was not exercised, never that it passed.
- Serialize them conditionally: append to `SUMMARY` and add to the `--json` `summary` object only when `checked_ptrs is not None`. Round < 18 output is byte-identical.
- `census/round-17/gate-replays.py:174-184` compares process/exit + the exact `(id, path)` finding multiset, so new SUMMARY fields would not break it anyway; conditional serialization additionally keeps the gate's own `cli-summary-exact` selftest (`tools/souji-landing-gate.py:948`) and the r16 fixture's substring checks (`tests/fixtures/r16-landing-gate.py:236,488`) untouched.
- `FINDING_IDS` (`tools/souji-landing-gate.py:115`) is unread; do not extend it with the new id. The module docstring and the `SKILL.md` registry row are the id authorities. Deleting the dead tuple is a safe separate simplification.

# 2. Calibration at b576341

Tree: `git ls-tree -r --name-only -z b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`.
Scanner: in-memory Python over `git show b576341:<authority>`; no repo tool executed, no writes.

Two surfaces:

- **A — the surface `--round 18` actually selects at b576341:** five fixed files + seven `corpus/knowledge/*.md`; no `corpus/lessons/round-18.md` and no round-18 LOG section exist at this rev.
- **B — surface A plus the round-17 lesson and the round-17 LOG section substituted**, to exercise the lesson/LOG rules with the most recent real authority. This is the calibration superset; it yields the same findings.

| surface | files | raw | skipped | expanded occ | unique cit. | lane | unresolved | exempt | fleet | findings | distinct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A (round-18 at b576341) | 12 | 306 | 9 | 314 | 300 | 288 | 9 | 2 | 3 | 7 | 2 |
| B (round-17 lesson+LOG added) | 14 | 352 | 10 | 360 | 346 | 329 | 13 | 6 | 4 | 7 | 2 |

`unique cit. = lane + unresolved + fleet` on both rows.

## The 7 findings after the proposed TSV (all true defects; 0 false positives)

| # | citing file | line | token | resolves to |
|---|---:|---|---|---|
| 1 | `SKILL.md` | 163 | `census/round-17/gate-replays-ddb7347.json` | absent at REV |
| 2 | `SKILL.md` | 165 | `census/round-17/gate-replays-ddb7347.json` | absent at REV |
| 3 | `corpus/README.md` | 216 | `../census/round-17/jj-receipts-ddb7347.txt` | `census/round-17/jj-receipts-ddb7347.txt`, absent |
| 4 | `corpus/knowledge/jj-colocation-receipts.md` | 2 | `census/round-17/jj-receipts-ddb7347.txt` | absent at REV |
| 5 | `corpus/knowledge/jj-colocation-receipts.md` | 44 | `census/round-17/jj-receipts-ddb7347.txt` | absent at REV |
| 6 | `corpus/knowledge/jj-colocation-receipts.md` | 126 | `census/round-17/jj-receipts-ddb7347.txt` | absent at REV |
| 7 | `corpus/knowledge/jj-colocation-receipts.md` | 148 | `census/round-17/jj-receipts-ddb7347.txt` | absent at REV |

Distinct defect paths: 2. Both are the C2/R2 routed defects. No third path is unresolved after exemptions.

## What the 6 exempt citations are

| exempt path | occurrences (Surface B) | where |
|---|---:|---|
| `tests/vault/vadv54-run/p/p6repo/.git` | 3 | `SKILL.md:110`, `corpus/lessons/round-17.md:16`, `LOG.md:946` |
| `census/operator-sweep-20261019/` | 2 | `corpus/README.md:81`, `corpus/lessons/round-17.md:91` |
| `census/verify/vault/quarantine` | 1 | `corpus/lessons/round-17.md:80` (bare prose shorthand for three tool selftests) |

Surface A exempts only the first (1) and second (1): 2 occurrences. This is why the two surfaces have different unresolved/exempt counts but identical findings.

## Fleet rows (Surface B; 4 unique citations, 3 distinct paths)

- `corpus/README.md:217` -> `.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`
- `corpus/README.md:217` -> `.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md`
- `corpus/knowledge/jj-colocation-receipts.md:148` -> `.ufo/waves/hyaku/jj-w1/reports/`
- `corpus/lessons/round-17.md:16` -> `.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md`

All four exist under `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/`. Surface A has the first three.

## Reconciliation with L1's 281 tokens / 18 unresolved

Numbers differ because the token set and the surface differ, not because the tree differs:

- L1's 281 is closest to Surface A's 306 raw occurrences. My token set adds bare-prose occurrences and `{a,b}`/range expansion; it removes mid-word matches and runtime `.ufo/*` paths. The 25-occurrence gap is consistent with the tokenization/surface differences in the dropped-rules table below; I did not reproduce L1's exact regex [INFERENCE].
- L1's 18 unresolved include classes this grammar deliberately excludes or reclassifies:
  - `.ufo/state`, `.ufo/watchdog.log`, `.ufo/scopes/...`, `.ufo/quarantine/...` — outside the five prefixes (runtime/operator/untracked surfaces, never repo-relative claims);
  - `.ufo/waves/hyaku/...` — fleet, counted and not a finding;
  - whole-LOG historical pointers (round-15 `ConfigRepair.md`, round-16 `build/`, round-21, round-3 seat rollup, round-10 cert lines) — outside the round-N section;
  - glob/placeholder tokens — skipped by G2.
- After G0-G7, the residual is 9 (Surface A) or 13 (Surface B) occurrences, 5 distinct paths; the 3 exemption rows remove 2 or 6 occurrences respectively, leaving exactly the 2 true defect paths.

# 3. Rules dropped, measured, and why

Counts are Surface B unless a row says otherwise.

| # | Rule dropped | Measured effect at b576341 | Why drop |
|---|---|---|---|
| D1 | Match any `.ufo/` path (or any path-like token) | Adding all-`.ufo` to Surface B: +5 unresolved rows / +4 distinct paths (`.ufo/quarantine/round-17/…`, `.ufo/quarantine/…/dot-git-empty-stub` twice, `.ufo/state/\`, `.ufo/quarantine/round-17/`). No true defect gained. | These are runtime, operator, quarantine, or untracked surfaces. They are not claims about committed lane files. The spec's fifth prefix is `.ufo/waves/`, not `.ufo/`. |
| D2 | Scan the whole of `LOG.md` | +4 net unresolved rows (5 additions, 1 line-renumber: the same `.git` citation is reported at absolute 946 instead of section-relative 3): `LOG.md:556,745` operator-sweep, `LOG.md:796` `.ufo/waves/round-16/build/`, `LOG.md:916` the ddb replay record in the round-16 correction entry, plus the renumbered `.git` row. All historical; zero true defects lost (SKILL/README/knowledge still catch both). | LOG is append-only history. Re-checking every older round makes every transient seat artifact a permanent finding and punishes corrections for citing the very records they discuss. The spec says the round-N section. |
| D3 | Backtick-only extraction | Loses 43 of 352 occurrences (12.2%) on Surface B; only 1 of them is unresolved (the `census/verify/vault/quarantine` prose shorthand), so it would save one TSV row but stop seeing bare future drift. | Prose citations are claims too. The extraction rule is already exact enough with boundaries; code-span state adds parser complexity for no precision. |
| D4 | Explicit `:line` suffix stripping and line-range validation | 0 effect on the 7 findings. Colon termination already handles `:12`, `:15-16`, `:18-19, 22-24, 31-32`, `:167,180,185`. | Line numbers are content-relative and drift independently of existence. A pointer claim is "this path exists at REV"; validating line counts would add stale-content findings the tool cannot adjudicate. |
| D5 | Expand/resolve globs (`*`, `**`) | 2 glob forms, 3 occurrences skipped (the other 7 skips are placeholders, D6). Expanding `census/round-17/jj-receipts-*.txt` would match two existing receipts and hide the missing ddb one; expanding `verification*.json` would invent a matching rule. | A glob is not a claim about one path. Skipping cannot hide the two defects because both are also cited concretely (SKILL, knowledge, README). |
| D6 | Resolve placeholders (`<N>`, `<tool>`, `round-N`) | 4 placeholder/round-N forms, 7 occurrences skipped; no defect hidden. | They are unresolvable by construction. |
| D7 | Expand generic numeric ranges (`{seat-01..64.json,...}`) | 0 canonical occurrences; the only sighting is an unbalanced whole-LOG rollup. Naive expansion would create 64 paths and up to 64 findings. | Not a pointer; a historical shard naming pattern. Only `round-a..b` is declared and exercised. |
| D8 | Require a file extension / resolve blobs only | 22 unique citations (17 distinct tokens) resolve only as directories (Surface B). File-only would emit 22 false-positive rows. | Directory citations are legitimate pointers (`corpus/knowledge/`, `census/round-16/transcripts/`, frozen fixture dirs). Tree-prefix resolution is exact. |
| D9 | Treat an unbalanced brace as a path | 0 canonical occurrences; defensive only. | A malformed brace cannot be expanded; testing it as a literal would guarantee a false finding. |
| D10 | Join tokens across line breaks | One known instance at `LOG.md:916-917` (`.ufo/waves/round-16/w1/` + newline + `ConnLogConvention.md:385`), outside the round-17 section. Zero canonical effect. | Joining arbitrary prose lines is ambiguous and would require markdown block parsing for no measured gain. Disclosed blind spot, not a claimed pass. |
| D11 | Bind fleet classification to the fleet git tree/HEAD | 4 unique fleet citations / 3 paths; filesystem classification gets all 4 right. | The fleet repo is not a declared input; its HEAD is a second moving authority. The classification is advisory and never suppresses a lane finding. |
| D12 | Prefix/glob exemptions in the TSV | 3 exact rows cover 6 occurrences; a prefix rule could hide any future dangling pointer under `census/`. | The TSV is an explicit exception list, not a policy engine. Exact match keeps each suppression auditable. |
| D13 | Flag stale exemption rows | 0 stale rows: all three exempted paths are absent at REV by design. | An exemption for an existing path is inert; a stale check would false-fail when an operator-owned directory lands. |
| D14 | Symlink/submodule/case/Unicode normalization | 0 occurrences in the authority set. The only non-ASCII path-like sighting (`.ufo/quarantine/round-17/…`) is outside the narrow prefix set. | `list_tree` gives exact blob paths; normalization would invent matches. |
| D15 | `./` prefix support | 0 occurrences. | No evidence it is used; adding it now is unexercised surface. If it appears, the gate reports it, which is the correct fail-closed default. |
| D16 | Extend the dead `FINDING_IDS` tuple | 0 readers of `FINDING_IDS` (`tools/souji-landing-gate.py:115`; the r16 transcript already recorded it as unused). | It is a third id copy with no consumer. Adding the new id there repeats the defect; deleting the tuple is the simplification. |

Not dropped, deliberately kept: the two-line `../` normalization (it catches the README citation of the jj defect), directory resolution (22 citations / 17 distinct tokens), the `round-a..b` expansion (two authority citations), and the TSV comment/blank handling (needed for a readable committed list and to reject malformed rows).

# 4. Implementation sketch

Reuse `_git` / `list_tree` / `blob_by_oid` (`tools/souji-landing-gate.py:157-188`); no new git calls.

```python
DANGLING_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])"
    r"((?:\.\./)*(?:census|tests|tools|corpus|\.ufo/waves)/"
    r"[^\s`'\"()\[\]|;:#?=]+)"
)
DANGLING_AUTHORITY = (
    "SKILL.md", "SCORECARD.md", "PROVINCE.md",
    "corpus/QUALITY.md", "corpus/README.md",
)
POINTER_EXEMPTIONS = "corpus/pointer-exemptions.tsv"
ROUND_RANGE_RE = re.compile(r"round-(?:\{(\d+)\.\.(\d+)\}|(\d+)\.\.(\d+))")


def _tree_dirs(tree):
    dirs = set()
    for path in tree:
        parts = path.split("/")
        for i in range(1, len(parts)):
            dirs.add("/".join(parts[:i]))
    return dirs


def _pointer_skippable(tok):
    core = re.sub(r"^(?:\.\./)+", "", tok)
    return (
        any(c in tok for c in "<>*$")
        or "round-N" in tok
        or tok.count("{") != tok.count("}")
        or (".." in core and not ROUND_RANGE_RE.search(core))
    )


def _pointer_expand(tok):
    m = ROUND_RANGE_RE.search(tok)
    if m:
        a = int(m.group(1) or m.group(3))
        b = int(m.group(2) or m.group(4))
        return [tok[:m.start()] + "round-%d" % i + tok[m.end():]
                for i in range(a, b + 1)]
    m = re.search(r"\{([^{}]*)\}", tok)
    if m and ".." not in m.group(1):
        return [tok[:m.start()] + alt + tok[m.end():]
                for alt in m.group(1).split(",")]
    return [tok]


def _pointer_target(citing_file, tok):
    """Return (kind, repo_path): kind is 'lane' or 'fleet'."""
    if tok.startswith("../"):
        norm = os.path.normpath(os.path.join(os.path.dirname(citing_file), tok))
        if norm.startswith(".."):
            return "fleet", norm[3:]
        return "lane", norm
    return "lane", tok


def _load_pointer_exemptions(root, tree):
    if POINTER_EXEMPTIONS not in tree:
        return {}
    text = blob_by_oid(root, tree[POINTER_EXEMPTIONS]).decode("utf-8", "replace")
    exempt = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        path, tab, reason = line.partition("\t")
        path, reason = path.strip(), reason.strip()
        if (not tab or not path or not reason or path.startswith("/")
                or os.path.normpath(path).startswith("..")):
            raise EvalError("%s:%d: malformed exemption row" % (POINTER_EXEMPTIONS, lineno))
        exempt[path.rstrip("/")] = reason
    return exempt


def _authority_lines(root, tree, round_no):
    """Yield (citing_file, absolute_lineno, line) for the declared surface."""
    for path in DANGLING_AUTHORITY:
        if path not in tree:
            raise EvalError("authority file %s absent" % path)
        text = blob_by_oid(root, tree[path]).decode("utf-8", "replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            yield path, lineno, line
    for path in sorted(tree):
        if path.startswith("corpus/knowledge/") and path.endswith(".md"):
            text = blob_by_oid(root, tree[path]).decode("utf-8", "replace")
            for lineno, line in enumerate(text.splitlines(), 1):
                yield path, lineno, line
    lesson = "corpus/lessons/round-%d.md" % round_no
    if lesson in tree:
        text = blob_by_oid(root, tree[lesson]).decode("utf-8", "replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            yield lesson, lineno, line
    if "LOG.md" in tree:
        lines = blob_by_oid(root, tree["LOG.md"]).decode("utf-8", "replace").splitlines()
        heading = re.compile(r"^##\s+.*\bround\s+%d\b" % round_no, re.IGNORECASE)
        next_h2 = re.compile(r"^##\s")
        i = 0
        while i < len(lines):
            if heading.match(lines[i]):
                j = i + 1
                while j < len(lines) and not next_h2.match(lines[j]):
                    j += 1
                for k in range(i, j):
                    yield "LOG.md", k + 1, lines[k]
                i = j
            else:
                i += 1


def check_dangling_pointers(root, tree, rev, round_no):
    """Return (findings, counters). Reuses the enumerated tree; no git child."""
    dirs = _tree_dirs(tree)
    exempt = _load_pointer_exemptions(root, tree)
    fleet_root = os.path.dirname(os.path.abspath(root))
    findings, seen = [], set()
    n_checked = n_exempt = n_fleet = 0
    for citing, lineno, line in _authority_lines(root, tree, round_no):
        for m in DANGLING_TOKEN_RE.finditer(line):
            tok = m.group(1)
            if not tok.startswith("../") and m.start() > 0 and line[m.start() - 1] == "/":
                continue
            while tok and tok[-1] in ",." and tok.count("{") == tok.count("}"):
                tok = tok[:-1]
            if not tok or _pointer_skippable(tok):
                continue
            for path in _pointer_expand(tok):
                key = (citing, lineno, path)
                if key in seen:
                    continue
                seen.add(key)
                n_checked += 1
                kind, rel = _pointer_target(citing, path)
                if kind == "lane" and (rel in tree or rel.rstrip("/") in dirs):
                    continue
                if rel.rstrip("/") in exempt:
                    n_exempt += 1
                    continue
                if os.path.exists(os.path.join(fleet_root, rel)):
                    n_fleet += 1
                    continue
                findings.append((
                    "LG-DANGLING-PTR", citing,
                    "line %d: %s absent at %s" % (lineno, path, rev[:12]),
                ))
    return findings, {"checked_ptrs": n_checked, "ptr_exempt": n_exempt,
                      "ptr_fleet": n_fleet}
```

Insertion in `evaluate` (`tools/souji-landing-gate.py:607`), after `list_tree` / `SKILL.md` and before the frozen-pin branch:

```python
if round_no >= 18:
    ptr_findings, ptr_counts = check_dangling_pointers(root, tree, resolved, round_no)
    findings.extend(ptr_findings)
    result.update(ptr_counts)
```

`emit` (`:705`): build the fixed SUMMARY string, then:

```python
summary = "SUMMARY\tfindings=%d\t...checked_reports=%d" % (...)
if result.get("checked_ptrs") is not None:
    summary += "\tchecked_ptrs=%d\tptr_exempt=%d\tptr_fleet=%d" % (
        result["checked_ptrs"], result["ptr_exempt"], result["ptr_fleet"])
print(summary)
```

Add the same three keys only when `checked_ptrs is not None` to the `--json` `summary` payload. The error fallback in `main` needs no change; `.get` returns `None`.

Selftest changes (`:865` onward):

1. Give `check()` a `round_no=16` parameter and pass it to `evaluate`; existing cases stay byte-identical.
2. Add empty `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md`, and `LOG.md` to `_base_files()`; add benign `.ufo/waves/round-18/w1/SeatA.md` and `.ufo/waves/round-17/w1/SeatA.md` reports for the round-18 cases and `pointer-round-gate`.
3. New cases: `dangling-pointer` (SKILL cites an absent path -> exit 1, `LG-DANGLING-PTR`, `checked_ptrs` > 0); `pointer-resolves` (directory, `:12-14`, and both brace alternatives present -> 0); `pointer-exempt` (TSV row -> 0, `ptr_exempt=1`); `pointer-brace` (`{present,ghost}.json` -> 1, names ghost); `pointer-round-range` (`round-{1..2}.md`, one absent -> 1); `pointer-skip-forms` (`<N>`, `*`, `round-N`, unbalanced brace -> 0, `checked_ptrs=0`); `pointer-fleet` (`../fleet-only-<case>.md`, file written under the selftest top dir -> 0, `ptr_fleet=1`); `pointer-malformed-tsv` (exit 2); `pointer-round-gate` (same dangling citation at round 17 -> 0, proving the historical guard).
4. Update `_frozen_world` (`:835-844`): replace `record = {"measured_commit": "0" * 40}` with `record = {}` (see F1), and add a `dangling-measured` case.

Fixture impact: none required for round 16. `tests/fixtures/r16-landing-gate.py` runs round 16 and checks `SUMMARY` substrings (`:236`, `:488`); the new fields are absent there. `census/round-17/gate-replays.py` compares exit + `(id, path)` multiset only (`:174-184`), so the branch being off at rounds 15-17 is what keeps it identical; the counters are not compared.

# 5. Exemption TSV (proposed committed content)

`corpus/pointer-exemptions.tsv`; `\t` below is one literal TAB.

```text
# Exact repo-relative paths that are deliberately not files at any REV.
# <path>\t<reason>; trailing slash ignored; no prefixes or globs.
census/operator-sweep-20261019/\toperator-owned sweep directory; untracked by design and never opened
tests/vault/vadv54-run/p/p6repo/.git\tempty nested gitdir created by the r17 fixture; untrackable and quarantined
census/verify/vault/quarantine\tprose shorthand for the three receipt-tool selftests, not a filesystem path
```

These three rows turn 13 unresolved citations into 7 (Surface B) or 9 into 7 (Surface A). They do not touch either defect path.

# 6. Integration traps (must be scheduled)

## F1 — Q25(b) will flag the r14 frozen record at round 18

`tools/souji-landing-gate.py:538-560` currently treats an unresolvable `measured_commit` as "no measured checks" and emits nothing. Closing Q25(b) requires a finding:

```python
if verify.returncode == 0:
    measured_ok = True
elif round_no >= 18:
    findings.append((
        "LG-FROZEN-MEASURED", exp_path,
        "record.measured_commit %s does not resolve" % measured[:12],
    ))
```

`check_frozen_pins` needs `round_no` passed through. The same `round >= 18` gate is mandatory: without it, historical replays at rounds 15-17 can gain a finding at old revs, violating the C2 identity claim.

Measured: `tests/fixtures/r14-cache-frozen/record.json:6` has
`"measured_commit": "0123456789abcdef0123456789abcdef01234567"`, and
`git -C R cat-file -e 0123456789abcdef0123456789abcdef01234567^{commit}` exits 1 (DANGLING). Therefore the changed gate at `--round 18` over b576341 emits **one extra LG-FROZEN-MEASURED** for `tests/fixtures/r14-cache-frozen/expected.json` even after the two pointer defects are fixed. The round must bind that field to a real measured commit (or drop it) and regenerate the record bytes. The r14 `expected.json` has no `record_sha256`, so the record edit is not pinned; verify the r14 fixture's assertions (it reads `files` / `record` / `verdict`, not the commit).

Also update the selftest placeholder at `tools/souji-landing-gate.py:844` (`record = {"measured_commit": "0" * 40}`): with the new branch, any round-18 case using `_frozen_world` would inherit a guaranteed finding. Use `{}` or a resolvable commit.

`tests/fixtures/r15-preservation-frozen/record.json` has `4f48343...`, which resolves; it is not affected. `tests/fixtures/r13-cert-frozen/expected.json` has no `record` key and is not affected.

## F2 — The base-rev counting command cannot be the gate CLI

The C2 counting says "changed gate `--rev b576341 --round 18` findings before -> 0 at the round tip." At b576341 there is no `.ufo/waves/round-18/` report directory in the REV tree. `check_carry` (`tools/souji-landing-gate.py:368`) raises `EvalError("no .md reports under ...")`, so the CLI exits 2 before findings can be reported; the dangling branch's findings are discarded by the `except EvalError` path. `[INFERENCE]` from the code path; I did not execute the gate under the probe rule.

Working counting protocol:

- **before:** call `check_dangling_pointers` directly over `list_tree(R, b576341)` (the sketch above) with the proposed TSV applied; 7 rows / 2 distinct (Surface A). Without the TSV committed, the same sweep is 9 rows: the 7 defects plus `.git` and `operator-sweep`.
- **after:** run the full gate CLI at the round tip (`--round 18`, with wave reports, lesson, LOG section, TSV and the two missing records committed); expect 0 findings and `checked_ptrs > 0`.
- Do not quote the CLI's base-rev exit as a finding count. If L1 wants a CLI before/after pair, use a temporary tip checkout with the two records absent, not b576341.

## F3 — Do not extend the dead id tuple

`FINDING_IDS` (`:115`) has no reader. Adding `LG-DANGLING-PTR` there recreates the third-copy problem the r16 simplifier already found (`census/round-16/transcripts/w2/SimplifyGate.txt:204`). Leave it alone or delete it; the module docstring and `SKILL.md` registry row are the two id authorities.

# 7. Evidence and probe-rule disclosure

Read-only checks actually run (all against the named lane; no live tool execution, no `jj`, no git writes, no signals, no network):

```text
git -C R rev-parse b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
  -> b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
git -C R ls-tree -r --name-only b576341 -- \
  census/round-17/gate-replays-ddb7347.json census/round-17/jj-receipts-ddb7347.txt
  -> (no output; both absent at REV)
git -C R show b576341:tests/fixtures/r14-cache-frozen/record.json | grep -n measured_commit
  -> 6:  "measured_commit": "0123456789abcdef0123456789abcdef01234567",
git -C R cat-file -e 0123456789abcdef0123456789abcdef01234567^{commit}
  -> exit 1 (DANGLING)
git -C R cat-file -e 4f4834390ad4845b76804e94cc04d8f867ef9b54^{commit}
  -> exit 0 (resolves)
test -d census/operator-sweep-20261019   -> exists (untracked; absent from REV tree)
test -e census/round-17/gate-replays-ddb7347.json -> absent
test -e census/round-17/jj-receipts-ddb7347.txt   -> absent
test -e /home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md -> exists
test -e /home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md -> exists
```

The 352/360/346/13/6/4 counts come from an in-memory Python scan over `git ls-tree` and `git show` output (the `check_dangling_pointers` algorithm in §4). It executed no repository code, wrote no files, and signalled nothing. The scanner is reproducible from the sketch; `git show b576341:<file>` is the only input beyond `ls-tree`.

Probe-rule disclosure: one command was a recursive search —
`grep -rn 'FINDING_IDS' tools tests census` — which is minor `V-RECURSIVE` under the wave rule. It was used only to confirm the dead-tuple claim; the same fact is in the committed r16 transcript and in `tools/souji-landing-gate.py:115` itself. No other recursive filesystem search was run. Directory listings (`ls corpus/knowledge corpus/lessons`) were used only to size the authority set. The eval Python reads are the only non-listed execution; they are read-only computations over allowed git reads, disclosed here for L1's adjudication.

# 8. Smallest fix

1. Add `DANGLING_TOKEN_RE`, `DANGLING_AUTHORITY`, `POINTER_EXEMPTIONS`, `ROUND_RANGE_RE`, `_tree_dirs`, `_pointer_skippable`, `_pointer_expand`, `_pointer_target`, `_load_pointer_exemptions`, `_authority_lines`, `check_dangling_pointers` to `tools/souji-landing-gate.py`.
2. Gate the branch on `round_no >= 18` in `evaluate`; serialize the three counters conditionally in `emit` and `--json`.
3. Commit `corpus/pointer-exemptions.tsv` with the three rows above.
4. Fix the two defects' citation targets (commit the two records or repoint all 7 rows).
5. Pass `round_no` to `check_frozen_pins`; add the dangling-measured finding gated `>= 18`; fix `tests/fixtures/r14-cache-frozen/record.json:6`; update the `_frozen_world` placeholder.
6. Add the selftest cases and run `python3 tools/souji-landing-gate.py --selftest` plus `python3 census/round-17/gate-replays.py --gate-rev 5fa6017 --output <new.json>` once, after all edits land (main agent's verification, not mine).
