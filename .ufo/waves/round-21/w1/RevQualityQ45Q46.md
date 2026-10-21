# Q45/Q46 wording review against the round-21 preregistration

## Findings

### Minor — Q45 needs an additive C1 extension, not a relaxation

`corpus/QUALITY.md` line 104 already prohibits bare reads of the lane/fleet/census root when an operator-owned subtree is excluded, requires metadata-only exposure to be disclosed, and specifies the existing exact-root `V-RECURSIVE` check. C1 in `.ufo/waves/round-21/preregistration.txt` adds a distinct minor `V-READ-ROOT` classification: visible complete relative `read`/`grep`/`glob` targets resolve from the fleet-root working directory and are flagged when they resolve outside the lane; a complete `grep` without the ` @ ` separator implicitly targets that root. Targets resolving inside the lane are not flagged by this new class. Absolute, `~`, URI, and truncated targets are out of this *new class* only; C1 explicitly leaves `V-RECURSIVE` untouched. This extends the auditor's coverage beyond exact root calls and does not authorize access to any protected or operator-owned subtree.

Exact additive sentence for Q45:

> `V-READ-ROOT supplements, and does not replace or relax, V-RECURSIVE: for read, grep and glob calls, each visible complete relative target is resolved from the fleet-root working directory and flagged when that resolution is outside the lane; a grep with complete arguments and no ` @ ` path separator targets the fleet root, while a target resolving inside the lane is not flagged by V-READ-ROOT.`

The sentence should be read with C1's explicit exclusions: absolute paths, `~` paths, URIs and truncated targets are not `V-READ-ROOT` findings, but this is not permission to read them. Existing `V-RECURSIVE` findings remain governed by Q45.

### Minor — C3 supersedes Q46's source-level/routing sentence

Q46 line 105 currently says: “A source-level reason-field exposure defect is marked explicitly and routed for operator/Kagi assessment; no private-value probe is inferred from a list-only surface.” C3 replaces that disposition with a synthetic-only reason-field redaction and 160-byte-bound canary, using a `/proc`-free `--reason-only` entry point. The original sentence's no-private-value-probe boundary remains correct; its source-level/inference and operator/Kagi-routing wording is the part made stale. Q46's preceding sentence remains accurate: cmd canaries alone do not establish reason-path redaction or a secret-free read.

Exact replacement sentence for that Q46 sentence:

> Reason-field redaction and the 160-byte bound are tested only with fabricated canaries through the `/proc`-free `--reason-only` entry point; this synthetic result does not establish historical live exposure or a secret-free read, and no private-value probe is inferred from the list-only surface.

This is a required scope boundary, not a claim that the canary fixture has been run or passed.

## Q42/Q43 consistency

No conflict identified. Q42 line 101 expressly leaves reason-field redaction concern as inference unless a harmless synthetic witness establishes it, and separately warns that reading raw argv before output redaction is not proof of a secret-free read or universal output redaction. C3's fabricated canary is the bounded synthetic witness contemplated there; it does not turn into evidence about historical live exposure or secret-free reads. Its reason-only interface consumes synthetic input and is required to exit before `/proc` or `boot_id` reads. Q43 line 102 limits exclusion claims to the implementation's recognized bounded parent-chain snapshot and says documentary correction authorizes no fresh process scan or private-value probe. C3 changes neither that process-coverage boundary nor any reap authority.

## Residual risk and verification gaps

This review compares the frozen contract with the exact Q42–Q46 text only; it does not establish that the C1/C3 implementation or acceptance fixtures meet the contract. No build, test, or target-code execution was performed. No LSP device is mounted here (`xd://lsp` returned “No such tool”), so no LSP status/references/definition/diagnostics results are available; conclusions above are grounded in the cited exact text, not grep as semantic proof. No tools were installed.
