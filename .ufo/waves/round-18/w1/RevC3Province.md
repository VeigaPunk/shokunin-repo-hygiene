STATUS: PARTIAL — province boundary reviewed; the C3 implementation was not present at the inspected path.

# C3 process-residue province review

**Axis reviewed: coverage.**

## Verdict

Process residue is not a grant of general process ownership to souji. A narrowly scoped, read-only/list-only census of orphaned-process residue can fit souji's hygiene province as a dry-run census and removal-list *evidence* surface (souji `PROVINCE.md:6-17`). It must not act on the process. The current adjacency wording says souji "acts on artifacts and never on processes" (`PROVINCE.md:44-49`); read literally, that excludes even this detection-only census. Refine that wording explicitly before treating C3 as in-province.

## Overlapping claims and boundaries

- **Host maintenance / OS state — tsukuroi:** Tsukuroi owns the OS substrate and host operability, retains OS diagnoses, and its findings authorize no repair (`tsukuroi-shokunin/PROVINCE.md:3-8,25-28,37-42`). Its host-memory/kill-event signals are OS triage, while fleet attribution goes to mori (`:30-33`); ADJ-04 likewise routes kill-signal/liveness/progress correlation to mori (`:49`). C3 should not claim host health, OS repair, or fleet/wave attribution. Its distinct claim is only to inventory the specified residue for hygiene evidence.
- **Processes / fleet observability — mori:** Souji's current adjacency assigns fleet-health observation/reporting to mori and says souji never acts on processes (`souji-shokunin/PROVINCE.md:46-47`). Tsukuroi's explicit split sends census/kill-event fleet correlation to mori (`tsukuroi-shokunin/PROVINCE.md:30-33,49`). Keep process lifecycle, liveness, kill/OOM interpretation and fleet/wave correlation outside C3. A bounded own-UID residue list is compatible only as detection, not remediation or a competing host census.
- **Credentials in argv — kagi:** Kagi owns secrets/vault ops and credential-hygiene evidence (`kagi-shokunin/PROVINCE.md:3-6`); souji expressly routes credential-shaped findings to kagi and limits itself to paths/modes without reading secret content (`souji-shokunin/PROVINCE.md:36-37,50-51`). Tsukuroi's sanitized handoff rule says never copy credentials or raw argv (`tsukuroi-shokunin/PROVINCE.md:62-64`). Therefore do not emit raw argv: redact command/argv text (including credential values), report only the minimum sanitized residue/path evidence, and route any credential-shaped finding to kagi. Kagi's cited Province does not itself state an argv-specific rule; the no-raw-argv evidence is tsukuroi's handoff rule plus kagi's credential ownership.

## Boundary wording for C3

Recommended Province clarification: **Souji may perform a read-only, list-only census of current-UID processes matching the defined orphaned-temp-path/deleted-cwd residue predicates, solely as hygiene evidence. It never signals, kills, or otherwise changes processes. Any kill/remediation is operator-owned and requires operator approval; process health and fleet/wave attribution remain mori/tsukuroi concerns. Displayed argv/command text is truncated and redacted so credentials are never recorded; credential-shaped findings route to kagi.** This preserves C3's narrow surface without transferring process remediation, OS maintenance, or credential custody.

**Smallest fix:** replace the absolute "never on processes" phrase in souji `PROVINCE.md:46-47` with the explicit detection-only exception and the no-signal/operator-approval boundary above; add the argv-redaction/routing sentence next to the existing kagi adjacency. Keep the current prohibition on touching the OS (`:48-49`) but clarify that read-only residue observation is not OS remediation.

## Evidence checked / gaps

- Read the requested files: souji `PROVINCE.md` and `SKILL.md:1-12`; tsukuroi `PROVINCE.md`; kagi `PROVINCE.md`. Also read mori `PROVINCE.md` for the fleet-observability boundary cited by tsukuroi.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- PROVINCE.md SKILL.md tools/souji-proc-census.sh` → no output.
- Read `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-proc-census.sh` → path not found. Thus this review assesses the declared C3 boundary, not implementation behavior; no implementation or fixture claims are verified here.
- No tools were installed or updated.

This is an advisory boundary recommendation, not an admission.