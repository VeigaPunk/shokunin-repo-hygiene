# Population row s5 — the exact SKILL.md writer-rule statement

Source of truth: `census/round-66/c2-statements.tsv` at the frozen instruments commit
`4576f101a9200206de00ef00923dd38a7b2dbc7d`, row `s5`, column `after_pattern` (identical to `base_pattern`
for s5: the wording is stable, the statement is added by the round-66 landing).

Extracted with:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 4576f101a9200206de00ef00923dd38a7b2dbc7d:census/round-66/c2-statements.tsv \
  | awk -F'\t' '$1=="s5"{print $5}'
```

## The s5 `after_pattern` literal, byte-exact (167 bytes)

```
closed for the caller-injected config and object-redirect routes by the `tools/souji-receipt-write.py` refusals `RECEIPT-ENV-CONFIG-SET` and `RECEIPT-ENV-REDIRECT-SET`
```

## STATUS: ALREADY LANDED BY THE L1 — do NOT paste a second copy

The L1 landed the candidate writer AND the s5 SKILL.md statement in one commit:
`c13fbb4e1b563a78278ddc14316c20252e9a6d8d` ("round-66: writer rejects caller-injected GIT_CONFIG_* and
object-redirect env routes; full mode bits; SKILL/QUALITY r66 rows"). The landed SKILL.md line (offset 168966
in the blob at that revision) is:

```
- Env routes, round 66: the writer's `GIT_*` env-route surface is closed for the caller-injected config and object-redirect routes by the `tools/souji-receipt-write.py` refusals `RECEIPT-ENV-CONFIG-SET` and `RECEIPT-ENV-REDIRECT-SET`.
```

Verified this seat against the landed blob at `c13fbb4e`:

- the s5 literal occurs **exactly 1 time** in SKILL.md (no `DUPLICATE-LIVE-WORDING` risk);
- per-row occurrence counts in SKILL.md at `c13fbb4e`: s1 base 1 / after 1 (stable), s2 base 0 / after 1,
  s3 base 0 / after 1, s4 base 1 / after 1 (stable), s5 base 1 / after 1 (stable) — every row resolves to
  exactly one wording;
- `census/round-66/records/c2-after.txt` at that revision: `MARKERS flag=1 inrun=1 env=1 unmerged=1
  envcfg=1 envred=1`, `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0`.

**Do not append the draft sentence below.** s5 is a STABLE row, so a SECOND occurrence of the literal would
still resolve to one wording (the counter's stable branch never reports `DUPLICATE-LIVE-WORDING`) — but it
would put the same claim in SKILL.md twice and make the self-assessment file say one thing twice. The
landed wording already satisfies the population row.

## The draft sentence this seat produced BEFORE the landing (reference only — NOT for pasting)

The counter matches byte-contiguous substrings; a wrapped literal is a silent FAIL (the round-64 M3
lesson), so any statement carrying the s5 literal must be pasted as ONE line:

```
Writer rule, extended in round 66: `tools/souji-receipt-write.py` refuses, before any git call, the presence of the caller-injected config and object-redirect environment routes (`GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_*`, `GIT_CONFIG_VALUE_*`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_GLOBAL`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE`) — closed for the caller-injected config and object-redirect routes by the `tools/souji-receipt-write.py` refusals `RECEIPT-ENV-CONFIG-SET` and `RECEIPT-ENV-REDIRECT-SET` — repoints `GIT_CONFIG_GLOBAL` to the null device with `GIT_CONFIG_NOSYSTEM=1` and `GIT_NO_REPLACE_OBJECTS=1` and pins `-c core.excludesFile=<null device>` on every git call, records the full permission bits (`st_mode & 0o7777`, setuid, setgid and sticky included) in the in-run snapshot, and refuses a same-content symlink retarget with `RECEIPT-STATE-CHANGED-DURING-RUN`.
```

This seat's draft is SUPERSEDED by the L1's landed bullet above. It is kept here for the audit trail
(this seat's own collision check against it is recorded below and is still valid as a check of the L1's
landing).

## Verification (this seat, measured)

- The s5 `after_pattern` is a byte-contiguous substring of the sentence above: **PASS**.
- The sentence contains NO other row's `base_pattern` or `after_pattern` from
  `census/round-66/c2-statements.tsv` (rows s1–s4), so the landed SKILL.md cannot produce
  `DUPLICATE-LIVE-WORDING` on another row. Measured by substring search over all 8 pattern cells of all
  5 rows: **only s5's own literal matched**, zero collisions.
- The claim token s5 resolves to `env_closed`, whose REQUIRED markers are `envcfg`
  (`RECEIPT-ENV-CONFIG-SET`) and `envred` (`RECEIPT-ENV-REDIRECT-SET`). The sentence names both refusal
  classes verbatim, so the statement is true of a writer that emits them.
- s5 is a STABLE row (`base_pattern == after_pattern`): the counter requires the literal PRESENT in the
  SKILL.md blob at the measured revision. At base `045e1034…` the literal is absent from SKILL.md, which is
  why the do-nothing control is red (`FINDING GOVERNED-STATEMENT-UNRESOLVED s5`, `census/round-66/controls/
  c2-do-nothing.txt`). Verified: `base_pattern in SKILL.md(base) == False`, `after_pattern in SKILL.md(base)
  == False`; for s1–s4 the base SKILL.md resolves as expected (s1 and s4 stable-present, s2 and s3 on their
  `after` wording).
- **The L1's landed bullet carries the same literal and is the statement that counts.** This seat's check
  that the landed SKILL.md resolves each of s1–s5 to exactly one wording (occurrence counts above) is the
  operative check on the landing, not on this seat's draft.

## Notes for the L1 (not part of the statement)

- The landed statement is scoped to what the round-66 C1 matrix rows E1–E6, MOD2, MOD3 and SY3 test. The
  L1's landing also carries a SEPARATE "Named limits, not claimed:" bullet naming the ignore routes, the
  empty-value refusal and the lexical C2 read — that is the right place for them, and it keeps the s5
  sentence's scope clean.
- The statement is about the WRITER's behaviour, so it is only true once the candidate writer lands the
  corresponding refusals; landing the sentence before the writer would make C2's live-marker read fail on
  `envcfg`/`envred` (SCOPE-OVERREACH). The L1's landing does both in one commit (`c13fbb4e`), and
  `census/round-66/records/c2-after.txt` shows `envcfg=1 envred=1` at that revision.
