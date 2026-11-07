# CritC2Attack — round 27 C2 attack review

## Status

STATUS: PASS — C2 is attacked and fails its own frozen counter as packaged: the three staged rows (S152/S210/S211) are E01-malformed on admission, and after schema repair they still collide E04 (S152/S210 duplicate URL+scope). No do-nothing control trips all counters; the gate/census do tie rows to entries, but the frozen claim is internally unsatisfiable without amending rows, scope cells, or the 135-row target.

## Evidence

Base, lane `e78ac7c4837b81b634db4a927605a751a7f006ba` (master, ahead=0):
- `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `132`
- `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l` → `2` (quarantine-origin-record-fields-r24.md, quarantine-staging-no-copy-r23.md)
- `scripts/sources-census.sh validate --file souji-shokunin/corpus/SOURCES.md` → rc `0`, zero `E[0-9]+` lines (baseline clean).

Executed mirror runs (`/var/tmp/souji-r27-CritC2Attack/`):
1. Lane SOURCES.md + package rows S152/S210/S211 inserted verbatim into `## Registry` → validate rc `1`:
   `file	E01	S152 fields=13`, `file	E01	S210 fields=12`, `file	E01	S211 fields=14` (each row also `E12` when appended outside the Registry section).
2. Same rows with inner `\|` sequences neutralized → rc `1`: `file	E09	S152 recheck=365d — re-fetch ...` and E09 for S210/S211 (free-text recheck cells).
3. Schema-clean reconstruction of the three rows (exact URLs, scope `A`, status `mined`, recheck `365d`, real used-by paths) → rc `1`: `file	E04	S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c within scope A`.
4. Minimal same-URL/same-scope pair controls reproduced E04 (S901 flagged), confirming validator behavior.

Validator source read (`scripts/sources-census.sh`): E01 field check lines 635-639; E04 condition lines 644-649 `if (u!="" && (scope_key in url_scopes) && status!="rejected" && url_scope_nonrejected[scope_key] && teaches !~ /supersedes S[0-9]{3}/)`; E09 recheck grammar lines 663-667; E11 used-by existence lines 566-568. Gate (`tools/souji-gate-check.py`): entry-missing line 68-69; check1-no-gate 73-74; check5-dangling-source 123-128 (cited ids must resolve in corpus/SOURCES.md); ok=0 unless every entry passes, rc 1 (line 196).

## Findings

1. **F4 writer ground is genuinely uncovered — no duplicate claim by r24.** `corpus/knowledge/quarantine-origin-record-fields-r24.md` declares `ground: F4 — restorable quarantine (the read side of a per-item origin record)` and explicitly disclaims the writer/record-format side ("This still does not specify souji's record format"; "gio trash is not necessarily the mechanism"). No lane entry cites GLib source (`gio/glocalfile.c` / `glib/gfileutils.c`); the two drafts' grounding lines (writer guarantees; mechanism set O_EXCL/rollback/temp-rename) are new cells, not restatements.
2. **S152/S210 duplicate one page inside one scope — E04 error, not a warning.** Both rows cite the same URL `https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c`, tier A, scope A, status mined, no `supersedes S\d{3}` teaches token. After the malformation fix, validate terminates rc 1 on this pair. `scripts/sources-census.sh` line 646: `(scope_key in url_scopes) && status!="rejected" && url_scope_nonrejected[scope_key]` → E04. The claimed `sources-census rc 0` is unreachable with both rows admitted.
3. **Rows S152/S210/S211 are campaign-staged and packaging-broken; citing them cannot add rows as-is.** Each staged row embeds `|` inside cells (`O_CREAT \| O_EXCL`; recheck `365d — curl ... | grep -F ...`), and the validator splits on every literal pipe (`-F'|'`, line 580). Result: E01 NF mismatch for all three (13/12/14 fields vs required 13 → 11 columns). The repaired rows then trip E09 (recheck cell carries free text after `365d —`). MERGE-REPORT.md's own "used-by pointers corrected at packaging time" section (lines 105-123) shows the campaign's row text is not gate-clean at rest.
4. **Writer (r27) vs mechanism-set (r33): substantive but partially overlapping.** r33 restates r27's O_EXCL-create and rollback facts verbatim in claim form ("the exclusive create ... the rollback is the g_unlink") and then adds genuinely new content: exclusively-created descriptor closed unused, content-by-path under `G_FILE_SET_CONTENTS_ONLY_EXISTING`, `O_EXCL` belonging to the temp file (`g_mkstemp_full`), and the exists-empty window. Duplicate claim segments exist; the epistemic delta is real (not a copy). Verdict: overlap is not harmful, but it inflates the row budget: S210 exists only to serve r33's re-reading of r27's own file.
5. **Do-nothing control (rows, no entries) cannot trip the counters.** Grounded-F4 grep stays 2 (needs 4); gate prints `entry-missing` twice and rc 1; if the bare rows carry used-by naming the absent entries, E11 (`if [ ! -e "$dir/$path" ]`) fails sources-census; if used-by is `—`, W03 is warning-only but the other two counters still fail. Residual hole: W03 is not an error and nothing forces row-used-by == the entry that cites the row, so a disjoint "rows+entries" patch could pass structurally; the frozen counter chain is one-directional on that point.
6. **Frozen claim is internally unsatisfiable.** To reach 135 rows exactly three rows must be appended; the only GLib writer material yields two rows on one URL/scope (E04) and the third on a second URL; while the packaged text fails E01/E09. The only repairs — merging S210 into S152 (rows 134), inventing a scope discriminator for S210, or rewriting recheck cells — each alter the frozen row set or counter targets, i.e. they require an L1 amendment, not execution.

## Attack log

- Attack 1 (ground already claimed): REJECTED — r24 is read-side only; writer ground is uncovered.
- Attack 2 (campaign rows, knowledge vs rows): PARTIAL — entries carry new knowledge, but S152/S210 are the same page split into two rows to pad 132→135, contrary to CORPUS rule 4; worse, that split is a hard E04 failure.
- Attack 3 (writer vs mechanism-set duplication): PARTIAL — overlap confirmed on create/rollback statements; novel content keeps the entries distinct, but r33 should cite S152 instead of a second same-page row.
- Attack 4 (do-nothing control): REJECTED — gate/census tie rows to entries on both sides (E11, check5); appending rows alone fails ground-count and gate ok. Residual W03-only warning leaves a small, non-fatal gap.

Smallest safe correction (for the L1): drop S210 and let r33 cite S152 (rows 132→134, adjust the 135 target), or give S210 a distinct scope cell with L1 approval; rewrite all three rows with no `|` inside cells and pure `NNd` recheck cells; only then does `sources-census rc 0` become achievable.
