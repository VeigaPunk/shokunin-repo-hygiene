# SwarmReviewer41 — C3 located-quote verification against live pages

## Status
STATUS: PASS — every quote assigned to this seat is matchable under the lane gate's
whitespace-collapsed raw-byte rule against pages fetched live this run, and those live bytes
hash-equal the staged snapshots. Two *additional* quoted strings in
`deliver-sources-append-block.md` are not matchable; byte-exact fixes given and proven
red-before/green-after with `tools/souji-gate-check.py`.

## Evidence

Fetch (lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; lane HEAD at review time
`b8cb4b3` = prereg commit; no lane file written except this report):

```
curl -sSL -o <name>.html -w '%{http_code} %{size_download} <name>\n' https://man7.org/linux/man-pages/man2/statx.2.html   -> 200 33125
                                                                        .../man2/link.2.html    -> 200 19883
                                                                        .../man1/cmp.1.html     -> 200 9791
sha256sum: statx 2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e
           link  9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9
           cmp   5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3
```

All three digests are identical to the staged snapshots
`.ufo/waves/round-29/w1/sources/{statx.2,link.2,cmp.1}.html`, so the gate over the landed
snapshot sees exactly the bytes I verified. Page identity strings in the fetched bytes also
match the row metadata: `Linux man-pages 6.19            2026-02-08` (statx), `Linux man-pages
6.19            2026-02-11` (link), `diffutils 3.12.26-bbc1         August 2026` with
`diffutils.git⟩ on 2026-08-03` (cmp).

Gate rule checked (`tools/souji-gate-check.py:118-121`): snapshot is read, `squash()`-ed
(`re.sub(r"\s+", " ", text).strip()`), and `squash(quote) in body` decides. Raw HTML tags and
entities are **not** stripped, so `<b>`/`</b>` inside a quoted span blocks the match.

End-to-end, real tool, both delivered entries, staged snapshots copied to
`census/round-29/sources/` inside a scratch root (scratch, never the lane):

```
python3 -B tools/souji-gate-check.py --root <scratch>/gate-root --round-date 2026-10-25 \
  --entries corpus/knowledge/duplicate-verdict-identity.md corpus/knowledge/duplicate-verdict-byte-equality.md \
  --snapshot-dir census/round-29/sources --slice ... --slice-verdicts ...
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0   (rc=0)
```

## Findings

1. **Assigned quote set — all match (`gate-matchable-verbatim: yes`).** Locations in raw bytes
   are line numbers of the fetched pages.

   | # | page:line | quote | raw literal | squash match |
   |---|---|---|---|---|
   | 1 | statx.2.html:335 | `The inode number of the file.` | yes | yes |
   | 2 | statx.2.html:323 | `The number of hard links on a file.` | yes | yes |
   | 3 | statx.2.html:356 | `The file's creation timestamp.` (literal ASCII apostrophe) | yes | yes |
   | 4 | statx.2.html:379-380 | `If using STATX_MNT_ID_UNIQUE, this is the unique mount ID of the mount containing the file.` | no (newline after `mount ID`) | yes |
   | 5 | statx.2.html:97 | `stx_ino; /* Inode number */` | no (9 spaces) | yes |
   | 6 | statx.2.html:93 | `stx_nlink; /* Number of hard links */` | no (7 spaces) | yes |
   | 7 | statx.2.html:106 | `stx_btime; /* Creation */` | no (2 spaces) | yes |
   | 8 | statx.2.html:120 | `stx_mnt_id; /* Mount ID */` | no (6 spaces) | yes |
   | 9 | link.2.html:95-96 | `creates a new link (also known as a hard link) to an existing file` | no (newline after `an`) | yes |
   | 10 | link.2.html:102-103 | `impossible to tell which name was the` | no (newline after `name`) | yes |
   | 11 | cmp.1.html:113-114 | `Exit status is 0 if inputs are the same, 1 if different, 2 if trouble.` | no (newline after `is`) | yes |

   Raw byte-exact forms, where the literal differs from the quote:
   `               __u64 stx_ino;         /* Inode number */`;
   `               __u32 stx_nlink;       /* Number of hard links */`;
   `               struct statx_timestamp stx_btime;  /* Creation */`;
   `               __u64 stx_mnt_id;      /* Mount ID */`.
   No `&amp;`, `&quot;`, `&#39;` or `&lt;` occurs inside any quoted span; the only `&amp;`
   hits on the statx page are the `STATX_TYPE`/`STATX_MODE` mask lines (239-240), unquoted.

2. **`deliver-sources-append-block.md` Gate-quotes row S216 § CONSTANTS is not gate-matchable.**
   Location: `.ufo/waves/round-29/w1/deliver-sources-append-block.md:63`. The string
   `STATX_MNT_ID_UNIQUE Want unique stx_mnt_id (since Linux 6.8)` fails because raw bytes are
   `<b>STATX_MNT_ID_UNIQUE    </b>Want unique stx_mnt_id (since Linux 6.8)` (statx.2.html:257),
   so after squash the body reads `STATX_MNT_ID_UNIQUE </b>Want unique ...`. Verdict
   `gate-matchable-verbatim: no`. Fixes (both proven green): use
   `Want unique stx_mnt_id (since Linux 6.8)` (8 words, in the same line after the closing tag),
   or keep the constant's name with
   `STATX_MNT_ID_UNIQUE, this is the unique mount ID of the mount containing the file`
   (15 words, statx.2.html:379-380, plain text).

3. **`deliver-sources-append-block.md` Gate-quotes row S218 is not gate-matchable.**
   Location: `.ufo/waves/round-29/w1/deliver-sources-append-block.md:65`. Raw bytes are
   `it is impossible to tell which name\n       was the "original".` (link.2.html:102-103), so
   `it is impossible to tell which name was the original` (no quotation marks) is absent.
   Verdict `gate-matchable-verbatim: no`. Fix: `it is impossible to tell which name was the`
   (7 words) — proven green. Do **not** "fix" it to
   `which name was the "original"`: that string is in the bytes, but the gate's `QUOTE_RE`
   is `"([^"]{2,400})"`, so a gate line cannot carry an inner literal double quote; the
   matchable span must stop before it (the delivered entry line already does, which is why
   `deliver-duplicate-verdict-identity.md:60` passes).

   Proof, same scratch root, identical entry with only these two strings substituted:

   ```
   FAIL corpus/knowledge/red-before-identity.md check4-quote-absent-from-snapshot-line-7
   FAIL corpus/knowledge/red-before-identity.md check4-quote-absent-from-snapshot-line-9
   entries=1 ok=0 ... fail=2   (rc=1)          # red-before
   entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0   (rc=0)   # with the two fixes
   ```

4. **`stx_btime`'s struct-line comment is `/* Creation */`, not a creation-time phrase.**
   Location: `statx.2.html:106`. A future quote of the struct line must use
   `stx_btime; /* Creation */`; `stx_btime; /* File creation time */` is absent (probed:
   no match). The description sentence `The file's creation timestamp.` (line 356) is the
   safe located form and is what `deliver-quotes.tsv` plans.

5. **Snapshot landing prerequisite (not a defect at base).**
   `census/round-29/sources/` does not exist at lane HEAD `b8cb4b3` (`ls` -> "No such file or
   directory"), so the gate cannot be green until the L1 lands the staged files. The staged
   copies hash-equal the live fetch (Finding 1), so landing them unmodified reproduces the
   `ok=2` run. If the L1 instead re-fetches and man7's bytes have drifted, entry gates 1-11
   must be re-probed, not assumed.

## Attack log
n/a — reviewer seat; no ATTACK filed, no counter or predicate challenged. Findings 2-3 are
delivery-text defects, not gameable counters.

## Residual risk
- Broder `broder97resemblance.txt/.pdf` quotes are outside this seat's assigned scope; the
  `ok=2` gate run did exercise them and they matched the staged decode, but I did not
  re-derive that decode from the PDF ([INFERENCE] that the staged `.txt` is a faithful
  `pdftotext` of the staged `.pdf`).
- Live-byte equality is a snapshot at fetch time (2026-10-25); man7 pages are not
  content-addressed by URL, so the 365d recheck is the only drift control.
- `git status` shows a pre-existing modification to `.ufo/waves/round-26/w1/ScribeGateDraft.md`
  (not mine, untouched).

## Deliveries
- `.ufo/waves/round-29/w1/SwarmReviewer41.md` (this report)

Tooling: no install or upgrade performed (curl, sha256sum, python3 stdlib; all lane Python run
with `python3 -B`). Scratch `/var/tmp/souji-r29-SwarmReviewer41/` removed before this yield;
no `git`/`jj` mutation, no signal, nothing outside `souji-shokunin/` written.
