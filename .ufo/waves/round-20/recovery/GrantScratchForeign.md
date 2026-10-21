# GrantScratchForeign — read-only adversarial review

## Observed state and scope

Observed repository `HEAD`: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (the preregistered baseline). The inspected working tree is modified relative to that baseline. At inspection, `tools/souji-seat-audit.py` had SHA-256 `8f7b16473755215f4f90a85e3c1a9da2e31d47614919fd631866ddf01c31e2c9` and the read tool returned source snapshot `#5B7D`. `tools/souji-rev-pin.py` had SHA-256 `0b9018e52553d6517b8f805f07163b6a4093d6e842fa79314876084d7b64f756`. This is a source-only assessment of those observed bytes, not a claim about later edits or runtime behavior.

Reviewed the named round-20 preregistration and round-19 verifier lesson. No tests, builds, linters, smokes, or target code were run. No LSP device is exposed in the available tool inventory, so no semantic references/definition/diagnostics results are claimed.

## Findings (by severity)

### Low — Prefix-specific `run()` oracle is still missing; no over-clear found statically

**Evidence:** `tools/souji-seat-audit.py:143-168` accepts scratch only when the declared root fully matches the exact seat name, preserving an optional `w<slot>`; `:175-177` makes containment component-bounded (`prefix + os.sep`); and `:249-272` normalizes and checks scratch paths without treating a mere lexical prefix as containment. `delivery_paths()` builds only the current report stem's supported exact suffix candidates (`:129-140`), while `target_verdict()` admits non-truncated allowed files by exact equality (`:268-272`). These predicates do not reveal a foreign-seat or foreign-slot prefix bypass.

The regression oracle does not yet exercise the requested integrated adversarial shape. Direct `audit_seat()` cases cover a similar scratch prefix (`:486-490`), and `run()` covers a different seat writing to another seat's exact scratch root (`:546-565`). The slot grant table checks a different slot (`:587-591`), not a slot whose text extends the granted slot. Delivery tests reject `Other.patch` (`:511-517`), not a foreign report stem that begins with the granted stem. Thus the source currently looks boundary-safe, but the `run()` wiring and same-prefix foreign cases are not established by the checked-in oracle. This is an oracle-coverage finding, not an observed runtime defect.

**Concrete oracle change:** add a `run()` case with items `S` and `Sibling`, each explicitly granted `/var/tmp/souji-r20w2-<Name>`. Have `S` write to `/var/tmp/souji-r20w2-Sibling/out.txt` and `Sibling` write to its own root; expect exactly `S` to have a major violation. In the same table, check `S` writing to `/var/tmp/souji-r20w20-S/out.txt` is major (granted `w2` must not cover `w20`). For delivery, grant `S` only its exact `.../S.patch`, then assert a write to `.../Sibling.patch` remains major. These cases make the preregistered cross-seat-stem and alternate-slot refusals falsifiable at the `run()` boundary.

## Residual risk and verification gaps

This review establishes only predicates visible in the captured source snapshot; it does not authenticate the transcript/spec or test filesystem symlink behavior. The round-20 preregistration (`.ufo/waves/round-20/preregistration.txt:2-3`) explicitly requires exact delivery, cross-seat, and slot refusals; the proposed prefix cases sharpen that oracle rather than broaden authorization. LSP caller/reference and diagnostics checks were unavailable, and no execution-based evidence is claimed.