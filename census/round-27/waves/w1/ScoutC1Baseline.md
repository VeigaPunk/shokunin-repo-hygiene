# ScoutC1Baseline — C1 baseline reproduction at e78ac7c (souji round 27)

## Status

STATUS: PASS — C1 baseline reproduced exactly (`findings=2` with `--fleet-root`, `findings=5` without); both LG-DANGLING-PTR rows and their exact triggering tokens identified; the two-row `corpus/pointer-exemptions.tsv` mechanism was empirically shown to reach `findings=0` in an isolated scratch clone, and one ATTACK-class over-match trap was found and characterised.

Lane base read from `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt:5` (frozen before any after-data). No lane writes except this report and the receipt draft named in this report. No `git add/commit/push/stash/checkout/reset` in the lane; no `jj` mutation; nothing under `/home/vgpnk/Projects/shokunin/.scratch/`, `.ufo/state/`, `.ufo/watchdog.log`, `MANIFEST.json`, fleet `scripts/`/`templates/`, sibling lane repos, or `/home/vgpnk/Projects/shokuknow` was read-modified or written (shokuknow was not opened at all — C1 needed no external source).

## Evidence

### E1 — C1 counter WITH `--fleet-root` (the frozen counter command)

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev e78ac7c4837b81b634db4a927605a751a7f006ba --round 27 \
    --fleet-root /home/vgpnk/Projects/shokunin
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at e78ac7c4837b
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at e78ac7c4837b
SUMMARY	findings=2	checked_reg=50	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-27/ at e78ac7c4837b81b634db4a927605a751a7f006ba
RC=2
```

Revision: `e78ac7c4837b81b634db4a927605a751a7f006ba` (lane `HEAD`, branch master). The SUMMARY line and both rows match the preregistration's `before=2` exactly.

JSON sidecar `/var/tmp/souji-r27-ScoutC1Baseline/base-fleet.json` (scratch, removed at end) added `checked_ptrs=828`, `ptr_exempt=4`, `ptr_fleet=3`, `exit=2`.

### E2 — C1 counter WITHOUT `--fleet-root` (the 5-finding output)

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev e78ac7c4837b81b634db4a927605a751a7f006ba --round 27
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at e78ac7c4837b
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at e78ac7c4837b
LG-DANGLING-PTR	.ufo/waves/hyaku/jj-w1/reports/	corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at e78ac7c4837b
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at e78ac7c4837b
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at e78ac7c4837b
SUMMARY	findings=5	checked_reg=50	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-27/ at e78ac7c4837b81b634db4a927605a751a7f006ba
RC=2
```

The three extra rows are the fleet-escape rows. With `--fleet-root /home/vgpnk/Projects/shokunin` all three resolve into the `fleet` classification bucket (`base-fleet.json` → `fleet[]` lists `.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` and `JjAuditSouji.md` from `corpus/README.md:217`, and `.ufo/waves/hyaku/jj-w1/reports/` from `corpus/knowledge/jj-colocation-receipts.md:148`), so they are classified, not findings. **Only the two internal QUALITY.md rows are C1's target; the other three are fleet-owned and out of C1 scope.**

### E3 — the two flagged tokens, with file:line and verbatim source quote

Both rows originate in `corpus/QUALITY.md` at the frozen base; the finding detail's `file:line` is the *citing* line, and the flagged token is the *cited* string.

**Finding 1 — `corpus/knowledge/registry`**

- Cited by: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md:143` (row `Q59`), column "criterion".
- Verbatim quote (7 words, no `|`): `a corpus/knowledge/registry change is a coverage surface`
- Trigger: the row enumerates the three surface classes of the axis taxonomy. The token is ordinary prose — `corpus/knowledge/registry` is a *category name* ("a corpus / knowledge / registry change"), not a file path. No such file or directory exists in the tree at base: `git ls-tree -r --name-only e78ac7c... | grep -c '^corpus/knowledge/registry'` → `0`.
- The real registry is `corpus/SOURCES.md` (`corpus/` contains `QUALITY.md`, `README.md`, `SOURCES.md`, `knowledge/`, `lessons/`, `pointer-exemptions.tsv`); the lane never had a `corpus/knowledge/registry` file.

**Finding 2 — `corpus/lessons/round-24.md:232:S118`**

- Cited by: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md:141` (row `Q57`), column "check".
- Verbatim quote (16 words, no `|`): `The current site list is explicit and must be extended when a new citation is found`
- The flagged token sits in the same cell, in the enumerated site list: `corpus/lessons/round-24.md:240 corpus/lessons/round-24.md:232:S118 LOG.md:1692 SCORECARD.md:181`
- The underlying artefact is real: `corpus/lessons/round-24.md:232` is the S118 table row, whose evidence cell reads (17 words, no `|`): `DOI → IEEE 202, 0 bytes, twice; quote in IEEE staging + PDF mirror; venue cell wrong`. The *composite* `path:line:S-row-id` triple is what the pointer regex captured.

### E4 — why the parser matches these two as paths (gate source, read-only)

`tools/souji-landing-gate.py:141-146`:

```python
POINTER_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./<>*])"
    r"(?:(?:\.\./)+|\./)?"
    r"(?:census|tests|tools|corpus|\.ufo/waves|\.ufo/quarantine)/"
    r"""[^\s`"'()\[\]]+"""
)
```

- **Why `corpus/knowledge/registry` matches:** the regex is anchored on a *root prefix*, not on a path shape. Any whitespace-delimited run beginning `corpus/` is captured verbatim, with no requirement that the remainder be a filename, that the path exist, or that it be inside a backtick span. `a corpus/knowledge/registry change is a coverage surface` contains the run `corpus/knowledge/registry`, which the alternation `(?:census|tests|tools|corpus|…)/` picks up and `[^\s…]+` swallows to the next space. `_normalize_pointer_path` (`:801`) leaves it unchanged (no `../`/`./` prefix, no `.`/`..` component), and `_safe_pointer_path` (`:865`) accepts it — `registry` is a legal path component. The existence test then fails. The prose sense of "corpus / knowledge / registry" is invisible to the parser: it is a whitespace-delimited `corpus/`-rooted run, indistinguishable from a real citation.
- **Why `corpus/lessons/round-24.md:232:S118` matches:** the capture class `[^\s`"'()\[\]]+` excludes only whitespace and a few quoting characters, so `:` and letters are absorbed. The whole composite `path:line:S-row-id` is captured as one token. `_trim_pointer_token` (`:795`) strips a *trailing* `:digits` or `:digits-digits` suffix only — `:232:S118` ends in `S118`, not digits, so nothing is trimmed. Note the same cell also contains `corpus/lessons/round-24.md:240`, whose trailing `:240` *is* trimmed by `_trim_pointer_token` to `corpus/lessons/round-24.md`, which resolves — hence only one of the two enumerated round-24 sites is flagged.
- The `:232:S118` token is a *composite* — a path plus a line plus an S-row identifier in one string — and there is no path in the tree named `corpus/lessons/round-24.md:232:S118`, so it can never resolve.

### E5 — the mechanism reaches `findings=0` (isolated scratch clone, read-only w.r.t. the lane)

Scratch repo `/var/tmp/souji-r27-ScoutC1Baseline/repo`, created with `git init` + `git fetch` of the lane's base commit; `git -C "$D" rev-parse --show-toplevel` printed `$D` before any commit there. The lane repo was not mutated. Baseline reproduced in the clone first (identical two rows, `findings=2`).

Appending exactly two rows to `corpus/pointer-exemptions.tsv` (path TAB reason, matching the loader's shape at `:876-903`):

```
corpus/knowledge/registry<TAB>QUALITY.md Q59 prose token: the axis/surface-class taxonomy names "a corpus/knowledge/registry change" as a class of surface; no file of that path exists or is cited.
corpus/lessons/round-24.md:232:S118<TAB>QUALITY.md Q57 enumerated-site composite token: file:line:S118 site id concatenated to the path; the row itself lives at corpus/lessons/round-24.md:232.
```

Result at the scratch tip:

```
SUMMARY	findings=0	checked_reg=50	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
```

Adding a benign round-27 report (so the carry check no longer aborts the run) at the same tip:

```
SUMMARY	findings=0	checked_reg=50	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=1	carry_heading=0	checked_reports=1
RC=0
```

So the frozen counter's `after=0` is reachable with exactly the two preregistered rows, and `rc=0` requires a `.md` report under `.ufo/waves/round-27/` to exist at the tip (otherwise the gate exits 2 with `COULD-NOT-EVALUATE` even at `findings=0`).

### E6 — ATTACK probe: the exemption must be the composite token, not the bare path

The preregistration's C1 kill rule reads (`.ufo/waves/round-27/preregistration.txt:5`, verbatim): `an exemption that over-matches a real citation break (a path whose absence is a true defect cleared silently)`. Two variants were measured.

**Variant A — exempt the composite token (recommended).** Rows exactly as in E5. Deleting the *real* cited file `corpus/lessons/round-24.md` from the scratch tree still produced three separate `LG-DANGLING-PTR` findings naming `corpus/lessons/round-24.md` (from `SCORECARD.md:201` and twice from `corpus/QUALITY.md:141`), because the exemption key is the composite string `corpus/lessons/round-24.md:232:S118` and the *bare* path token is a different key. The composite exemption does not mask a genuine absence of the lesson file.

**Variant B — exempt the bare path `corpus/lessons/round-24.md` (gameable, rejected).** At the tip this did **not** reach `findings=0`: the composite token `corpus/lessons/round-24.md:232:S118` remained a live finding, and the bare-path row was additionally reported as stale:

```
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at 0e4d3298904a
LG-DANGLING-PTR-EXEMPT-STALE	corpus/lessons/round-24.md	exemption does not suppress an unresolved pointer or dangling measured_commit at 0e4d3298904a
SUMMARY	findings=2	...
```

With the real lesson file *also* deleted, Variant B fell to `findings=1` — the bare-path exemption had swallowed the genuine `corpus/lessons/round-24.md` breakage that Variant A still caught in triplicate. Variant B therefore both fails the counter and violates the kill rule. The L1 must use the composite key.

**Variant C — stale-exemption trap.** Creating a file at `corpus/knowledge/registry/` in the scratch tree made the pointer resolve, so the exemption no longer suppressed anything and the gate reported `LG-DANGLING-PTR-EXEMPT-STALE corpus/knowledge/registry`. The exemption file must not name a path that will come into existence. `corpus/knowledge/registry` is not a real registry file in this lane (the registry is `corpus/SOURCES.md`), so the risk is low, but the L1 should confirm no round-27 change creates that path.

### E7 — receipt draft (findings=2) for the L1's `c1-before.tsv`

Draft written to `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/ScoutC1Baseline-c1-before.tsv` (TSV, matching the existing `.ufo/waves/round-27/records/c1-before.tsv` column set: `rev`, `gate_sha256`, `findings`, `checked_reg`, `rc`).

**Note for the L1 — the existing `records/c1-before.tsv` `gate_sha256` field does not hold a sha256.** Its value is `e67810d130817879fddd71c5ceeb5d5fd37e6ea8`, which is 40 hex characters and is exactly `git rev-parse e78ac7c4837b81b634db4a927605a751a7f006ba:tools/souji-landing-gate.py` — the git *blob OID* (sha1), not the file's sha256. The file's actual sha256 is `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd` (`sha256sum tools/souji-landing-gate.py`, identical for the committed blob via `git show … | sha256sum`). The column name says `sha256`; the value is a sha1 blob id. The draft I deliver records the **true sha256** in that column, with the blob OID kept in a separate `gate_blob_oid` column. The L1 must decide which convention the frozen receipt uses before consuming it — flagging as ATTACK-class, see F5.

## Findings

**F1 — C1 baseline is exactly `findings=2` at base `e78ac7c4837b81b634db4a927605a751a7f006ba`, and the preregistration's `before=2` is correct.** Two `LG-DANGLING-PTR` rows, both citing `corpus/QUALITY.md`; `checked_reg=50`, `checked_pins=13`, `checked_measured=3`. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt:5` (claim C1, `before=2`); command output in E1.

**F2 — the two flagged tokens and their file:line.** (i) `corpus/knowledge/registry`, cited at `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md:143` (row Q59, criterion column) — quote: `a corpus/knowledge/registry change is a coverage surface`. (ii) `corpus/lessons/round-24.md:232:S118`, cited at `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md:141` (row Q57, check column) — the site list reads `corpus/lessons/round-24.md:240 corpus/lessons/round-24.md:232:S118 LOG.md:1692 SCORECARD.md:181`, and the criterion states: `The current site list is explicit and must be extended when a new citation is found`. Both tokens occur exactly once each across the gate's 22 source files / 2919 source lines (measured by replaying the gate's own source set and `_pointer_paths` over it); there is no other occurrence to worry about.

**F3 — why the parser matches them (the mechanism the L1 must reason about).** `tools/souji-landing-gate.py:141-146` (`POINTER_PATH_RE`) captures any whitespace-delimited run beginning with `census/`, `tests/`, `tools/`, `corpus/`, `.ufo/waves/`, `.ufo/quarantine/`; the capture class `[^\s`"'()\[\]]+` swallows `:` and letters, so the Q57 composite `path:line:S-id` is captured whole. `_trim_pointer_token` (`:795`) strips only a trailing numeric `:N`/`:N-M` suffix, which is why `…round-24.md:240` resolves to an existing file but `…round-24.md:232:S118` does not. Neither token can resolve because neither names a real path in the tree — confirmed by `git ls-tree -r --name-only e78ac7c… | grep -c '^corpus/knowledge/registry'` → `0`, and by the Q57 composite not being a filename. **This is the parse-level truth the exemption must target: an exemption keyed on the captured string, not on the underlying artefact.**

**F4 — the two-row mechanism reaches `after=0`, and the composite key is the only compliant key.** Measured in an isolated scratch clone (`git init` in `/var/tmp/souji-r27-ScoutC1Baseline/repo`, `rev-parse --show-toplevel` verified before the first commit): the two rows listed in E5 give `SUMMARY findings=0`, and with a round-27 `.md` report present `rc=0`. Variant B (bare-path key) instead produced `LG-DANGLING-PTR-EXEMPT-STALE corpus/lessons/round-24.md` and left the composite token live (`findings=2`), and with the real lesson file deleted it fell to `findings=1`, swallowing a genuine breakage — that is exactly the preregistered kill-rule violation. **Recommendation to the L1: key both rows on the exact captured strings `corpus/knowledge/registry` and `corpus/lessons/round-24.md:232:S118`.**

**F5 — ATTACK: the `gate_sha256` column of the existing `records/c1-before.tsv` holds a sha1 blob OID, not a sha256.** `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/records/c1-before.tsv:2` carries `e67810d130817879fddd71c5ceeb5d5fd37e6ea8` under the header `gate_sha256`. That string is 40 hex chars and equals `git rev-parse e78ac7c4837b81b634db4a927605a751a7f006ba:tools/souji-landing-gate.py`; the gate file's real sha256 is `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`. A reader who takes the column at its name would pin the wrong digest of the frozen counter. The gate blob OID is still a valid *identity* pin for the gate, so this is a labelling defect rather than a wrong-measurement defect — but the frozen counter's instrument identity should be unambiguous. My delivered draft records the true sha256 and keeps the blob OID in its own column so both are recoverable.

**F6 — INFO: the counter's exit code is 2 at base, and 0 only once a round-27 `.md` report exists at the tip.** At base the gate prints `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-27/ at e78ac7c4837b81b634db4a927605a751a7f006ba` and exits 2, *after* printing the `SUMMARY findings=2` line. This is by design (the pointer check runs before the carry check, `tools/souji-landing-gate.py:1063-1078`), so the preregistered counter reads the `SUMMARY findings=N` literal, not the exit code. The L1 should read the counter off the SUMMARY literal for `before=2`/`after=0`; the exit code at the landing tip will be 0 only if a round-27 `.md` report is committed.

**F7 — INFO: the carry check will add findings at the landing tip unless failures are carried.** Measured in the scratch clone: a round-27 seat report whose status line is in the failure vocabulary produced `LG-SEAT-UNCARRIED .ufo/waves/round-27/w1/ProbeSeat.md line 5: STATUS: FAIL …` (`findings=3`), and the lesson must carry it under `## Seat-reported failures` with an `open` or `resolved@<rev>` token, else `LG-OPEN-ADMITTED` fires. Since C1's counter is the *total* `SUMMARY findings=N`, the C1 landing tip can only read 0 if the wave's own reports carry their failures into `corpus/lessons/round-27.md`. This is a wave-wide constraint on the L1, not a C1-specific one, and it is independent of the two exemption rows.

**F8 — INFO: the three fleet rows are not C1's business.** Without `--fleet-root` the run reports `../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` and `../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` (both from `corpus/README.md:217`) and `.ufo/waves/hyaku/jj-w1/reports/` (from `corpus/knowledge/jj-colocation-receipts.md:148`). With `--fleet-root /home/vgpnk/Projects/shokunin` these resolve into the `fleet` bucket, not findings — the files exist at `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/`. The frozen C1 counter passes `--fleet-root`, so these three are out of scope and must not be "fixed" by exemption.

## Attack log

**A1 — bare-path exemption would over-match a real citation break (C1 kill rule).** Measured, not inferred. Variant B in E6: exempting `corpus/lessons/round-24.md` instead of the composite token left `LG-DANGLING-PTR corpus/lessons/round-24.md:232:S118` live *and* raised `LG-DANGLING-PTR-EXEMPT-STALE corpus/lessons/round-24.md`; with the real lesson file deleted it fell to `findings=1`, versus Variant A's `findings=3` for the same deletion. Both counter failure and kill-rule violation. **Mitigation: key on the captured composite string.**

**A2 — a stale exemption becomes a new finding.** Measured in the scratch clone: with `corpus/knowledge/registry` created as a real path, the pointer resolved and the gate reported `LG-DANGLING-PTR-EXEMPT-STALE corpus/knowledge/registry` (`findings=1`). The exemption file is not a static allowlist — every row must keep suppressing an unresolved pointer at the landing tip. **Mitigation: confirm no round-27 change introduces `corpus/knowledge/registry`.**

**A3 — the `gate_sha256` receipt column is mislabelled.** See F5. **Mitigation: my draft records the true sha256 and preserves the blob OID separately; the L1 must pick a convention before freezing `c1-before.tsv`.**

## Delivery files

- This report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/ScoutC1Baseline.md`
- Receipt draft (`findings=2`): `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/ScoutC1Baseline-c1-before.tsv`

Both are inside this seat's own report directory; nothing else in the lane was written. Scratch under `/var/tmp/souji-r27-ScoutC1Baseline/` was removed after the runs.

## Tooling

No tool was installed, upgraded or modified this run. The only tools used were the lane's own `python3` (3.x, `python3 -B` throughout, no `__pycache__` written), `git` (read-only against the lane; `init`/`fetch`/`commit` confined to the scratch clone under `/var/tmp/souji-r27-ScoutC1Baseline/`), and `bash`/`grep`/`sed` for reading. No `pacman`, `uv`, `npm`, or `cargo` transaction was performed.
