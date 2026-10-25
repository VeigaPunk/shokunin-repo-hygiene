STATUS: PASS

# Slice124 — hand-check of register row S124 (lane `souji`)

Axes: calibration (is the register's class true of primary bytes), operability (verdict in the
frozen enum, no new authority), coverage (one of eight slice rows closed with a locator).
No axis harmed: register, payload and campaign tree read-only; only this report and the two
files under `w1/evidence/` were written. No tool installed or updated (none needed).

## 1. Row extraction (frozen awk, field 4 = id cell)

Command (frozen in `.ufo/prompts/souji-round-22.md:455-457`, reproduced from the round prompt):

```
R=/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
awk -F'|' -v l='souji' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ \
  {print $4, $5}' "$R" | grep -w S124
```

Observed output (exactly one line):

```
 S124   `payload-absent`
```

Full data row (register line 173, read-only, `cat -A` for tab bytes):

```
| `souji` | round2 | S124 | `payload-absent` | lanes/souji/round2/evidence/noreplace-probe.out | `/home/vgpnk/Projects/shokunin^Ifstype=btrfs^INOREPLACE_existing=-1(EEXIST)^Iplain_overwrite=0(ok)`<br>`Don't overwrite newpath of the rename. Return an error if newpath already exists.` | cited source, companion URLs and local artifacts were all checked; the quote is in none of them |
```

## 2. Span 1 — read the payload bytes

Payload: `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace-probe.out`
(530 bytes, 6 lines, mtime 2026-10-23 18:27:32 -0300; read-only, copied out, never edited).

Observed line 2 (tab-separated fields, `od -c` verified):

```
/home/vgpnk/Projects/shokunin	fstype=btrfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
```

Field list: `['/home/vgpnk/Projects/shokunin', 'fstype=btrfs', 'NOREPLACE_new=0(ok)',
'NOREPLACE_existing=-1(EEXIST)', 'plain_overwrite=0(ok)']`.

The claimed span is **not** byte-present as written (`claimed_exact_in_payload: False`) because it
elides the intervening field `NOREPLACE_new=0(ok)`. With that one field restored the span is exact;
no value in the claimed span was altered. Payload line 2 is the only row carrying
`/home/vgpnk/Projects/shokunin` (`grep -nF` -> `2:`).

Corrected quote (payload's real line, line 2 of the file):

> `/home/vgpnk/Projects/shokunin<TAB>fstype=btrfs<TAB>NOREPLACE_new=0(ok)<TAB>NOREPLACE_existing=-1(EEXIST)<TAB>plain_overwrite=0(ok)`

Correction stated: insert the omitted field `NOREPLACE_new=0(ok)` between `fstype=btrfs` and
`NOREPLACE_existing=-1(EEXIST)`. The probe that emits it (`noreplace_probe.py`, same directory)
prints `NOREPLACE_new`, `NOREPLACE_existing`, `plain_overwrite` in that order — so the omission is
a quoting elision, not a payload difference.

## 3. Span 2 — fetched source and locator

Source: `https://man7.org/linux/man-pages/man2/rename.2.html` — fetched 2026-10-25 with
`curl -fsSL -m 30` (HTTP success enforced by `-f`), saved as
`.ufo/waves/round-22/attempt2/w1/evidence/slice124-rename2.html`
(23571 bytes, sha256 `8772946a809a0db54f4854f200908f10bee758ea452e8df5efd955bc3b8e6e57`).
Page identifies itself as `rename(2) - Linux manual page`, `Linux man-pages 6.19`.

Located span (verbatim, whitespace-collapsed; HTML source lines 162–164):

> Don't overwrite newpath of the rename. Return an error if newpath already exists.

Locator: **§ DESCRIPTION, the `flags` list, entry `RENAME_NOREPLACE`** (HTML lines 162–164;
text lines 163–164 where the sentence wraps after "an error if"). Exact-string search over the
whitespace-collapsed page body returns 1 hit — the quote is present, not approximated. The page's
own attribution of this semantics is the same probe that produced the payload (btrfs/tmpfs support
listed at Linux 3.17).

**Absent from the payload.** `grep -rn "overwrite newpath"` over
`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/` returns rc=1 (0 matches);
`"overwrite newpath" in payload_bytes` -> `False`. So the row's single `|`-cell quote is **two
sources spliced**: span 1 from the local payload, span 2 from rename(2) prose. The lane itself
attributes span 2 correctly elsewhere — `lanes/souji/round2/SOURCES-PROPOSED.md:51` cites
`https://man7.org/linux/man-pages/man2/rename.2.html — § DESCRIPTION "Don't overwrite newpath of
the rename. Return an error if newpath already exists."` — so the splice happened at register-row
assembly, not at source discovery.

## 4. Frozen verdict for S124

**Verdict: `accepted`** (quote corrected, correction stated).

- Span 1 is present in the cited payload with one elided intervening field -> quoted real line
  above, correction stated.
- Span 2 is verbatim in the companion URL that the lane's own `SOURCES-PROPOSED.md` names, and
  absent from the payload -> citation-class defect, recorded here, not repaired by rewriting the
  register.
- No fabrication: every byte of both spans exists in an authoritative source opened 2026-10-25.

Recommended verdicts-TSV row (pointer for the seat that owns `slice-verdicts.tsv`; this report does
not edit it):

```
S124	accepted	payload .ufo/waves/round-22/attempt2/w1/evidence/slice124-noreplace-probe.out#L2 (intervening NOREPLACE_new field restored) + man7 rename.2 § DESCRIPTION RENAME_NOREPLACE, 2026-10-25, sha256 8772946a809a0db54f4854f200908f10bee758ea452e8df5efd955bc3b8e6e57
```

## 5. Snapshots (sha256)

| file | sha256 | note |
|---|---|---|
| `.ufo/waves/round-22/attempt2/w1/evidence/slice124-noreplace-probe.out` | `1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5` | byte-identical to the read-only payload (same hash re-derived at the source path) |
| `.ufo/waves/round-22/attempt2/w1/evidence/slice124-rename2.html` | `8772946a809a0db54f4854f200908f10bee758ea452e8df5efd955bc3b8e6e57` | identical to the pre-existing `evidence/snap-rename2.raw`, i.e. the fetch is reproducible |

Access date for the fetched source: **2026-10-25**.

## 6. Bounded findings

1. **The register's own class is falsified for this row.** `payload-absent` with reason "the quote
   is in none of them" is contradicted twice: the payload carries span 1 modulo one field, and the
   row's companion URL carries span 2 verbatim. The defect is quote assembly / citation class, not
   fabrication (`refused` would mis-state it as absent).
2. **Elision, not alteration.** Only `NOREPLACE_new=0(ok)` is missing; all four claimed field
   values are byte-equal, and the surrounding rows (`/var/tmp`, `/home/vgpnk/Projects/shokuknow`,
   `/dev/shm`, `/tmp`) carry the same five-field shape, so the omission is not a variant probe.
3. **Two sources in one quote.** Span 2 lives only in rename(2); the `|`-cell attributes both to
   `lanes/souji/round2/evidence/noreplace-probe.out`. Per the frozen rule the correction is stated
   here and the campaign register is left untouched (no edit, no rewrite, no deletion authority).
4. **No axis harmed.** Read-only access to `shokuknow` and the payload; writes limited to
   `w1/Slice124.md` and the two `w1/evidence/` snapshots; no git/jj write, no process signal, no
   cleanup action.
5. **Agreement note (not evidence).** The sheet's existing `S124 accepted` verdict row matches this
   independent hand-check; the verdict above was derived from primary bytes, not from that row.
   Confidence: high for span 1 (byte-level field check) and high for span 2 (exact-string count 1
   on a `-f`-verified fetch); `[INFERENCE]` only in calling the register defect an assembly-time
   splice rather than a deliberate misquote.

Evidence: `.ufo/waves/round-22/attempt2/w1/evidence/slice124-noreplace-probe.out`,
`.ufo/waves/round-22/attempt2/w1/evidence/slice124-rename2.html`.
