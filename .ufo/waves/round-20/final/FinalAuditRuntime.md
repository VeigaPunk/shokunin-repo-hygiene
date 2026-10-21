# Final audit runtime — round 20, attempt 1

## Result

No blocking calibration finding in this bounded pinned-build falsification. The current auditor passed the 103-case selftest, the R19 external shape fixture (17/0; base discriminates 12), and the R20 audit contract (50/0; base discriminates 11). This is evidence for the named synthetic cases only, not certification of historical execution or authorship.

Axes exercised: exact grant scope; consumed-input digest and drift handling; regression discrimination against the preregistered baseline.

## Source identity and hashes

- Independent clone: `/var/tmp/souji-r20w2-FinalAuditRuntime/lane`
- Branch: `souji-r20-FinalAuditRuntime`
- Branch HEAD / required pinned build: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`
- Baseline source: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812:tools/souji-seat-audit.py`, extracted to `/var/tmp/souji-r20w2-FinalAuditRuntime/baseline-auditor.py` with `git show`.
- `sha256sum` of selected auditor/fixtures and extracted baseline:
  - `tools/souji-seat-audit.py` — `a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636`
  - `tests/fixtures/r19-seat-audit-shapes.py` — `4a28faab385c63dc9c400b9a469c0695aaabc4aae38c944835dfc0f9dda5be72`
  - `tests/fixtures/r20-audit-contract.py` — `58a17169b72bb6b781b08d2f63426220234f383466d1a74ca5c982e1f2a5a434`
  - `/var/tmp/souji-r20w2-FinalAuditRuntime/baseline-auditor.py` — `62522acc350c23513f63d855231f82a9a6209b28b61535fb346e83cdf54e02e6`

Commands executed (all from the independent clone unless noted):

```text
test ! -e /var/tmp/souji-r20w2-FinalAuditRuntime && git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r20w2-FinalAuditRuntime/lane && git -C /var/tmp/souji-r20w2-FinalAuditRuntime/lane switch --quiet --create souji-r20-FinalAuditRuntime 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1 && git -C /var/tmp/souji-r20w2-FinalAuditRuntime/lane rev-parse HEAD
# stdout: 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1; rc=0

git -C /var/tmp/souji-r20w2-FinalAuditRuntime/lane show 12516f7dcdd5b165e5ee208d44a38d63b5bd5812:tools/souji-seat-audit.py > /var/tmp/souji-r20w2-FinalAuditRuntime/baseline-auditor.py
# stdout: (empty); rc=0

sha256sum tools/souji-seat-audit.py tests/fixtures/r19-seat-audit-shapes.py tests/fixtures/r20-audit-contract.py /var/tmp/souji-r20w2-FinalAuditRuntime/baseline-auditor.py
# stdout recorded in hashes above; rc=0

python3 -B tools/souji-seat-audit.py --selftest
# rc=0

python3 -B tests/fixtures/r19-seat-audit-shapes.py --tool tools/souji-seat-audit.py
# rc=0

python3 -B tests/fixtures/r20-audit-contract.py --tool tools/souji-seat-audit.py --base-tool /var/tmp/souji-r20w2-FinalAuditRuntime/baseline-auditor.py
# rc=0
```

## Findings and limits

The R20 cases falsify broad suffix authorization: an exact `DELIVER:` grant for the report stem's `.patch` does not authorize sibling `.py`, `.json`, `.tsv`, or `.txt`; denial text, fenced examples, incidental mentions, and a different seat's stem also remain unauthorized. Exact `OWN ONLY`/scratch roots are accepted while siblings, traversal, foreign wave slots, and ungranted roots are rejected. The baseline-control cases show the preregistered version accepts all 11 selected overbroad-write cases that the current build rejects. This directly exercises the grant calibration and its intended baseline separation.

Receipt cases check exact digests for the loaded auditor, spec, transcript, and manifest; changed bytes alter the respective digest; controlled mid-run drift in each consumed input is refused; the post-import auditor replacement and spec/transcript path alias are refused. The implementation's returned scope expressly covers consumed bytes and unchanged-during-run observations, not historical execution or authenticated authorship. The fixture is synthetic, so these passes do not establish external provenance or behavior outside the cases below.

No source/fixture edits or tool installs were made. The extracted baseline is the only additional private-clone scratch file; fixture-created temporary synthetic worlds were self-cleaned by the fixtures. No live census/operator-sweep material or production state was accessed.

Operational caveat: the outer clone and checkout were executed before receipt of the later instruction to apply per-command `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_TERMINAL_PROMPT=0`, `GIT_OPTIONAL_LOCKS=0`, `GIT_NO_LAZY_FETCH=1`, and Git `-c` hook/maintenance neutralizations. They were not applied to those completed commands; I did not inspect or change global config. The observed `rev-parse HEAD` was the required pinned commit, but this procedure does not rule out clone-time hook/maintenance behavior. I did not re-clone or replace the exclusive scratch.

## Exact executed case and summary lines

### Auditor selftest

```text
PASS	clean-read
PASS	report-write
PASS	owned-write
PASS	foreign-write
PASS	sweep
PASS	store
PASS	rules-ok
PASS	live-census
PASS	scratch-census
PASS	reviewer-exec
PASS	reviewer-bash-n
PASS	executor-exec
PASS	recursive-find
PASS	recursive-grep-tool
PASS	peer-message
PASS	edit-relative-owned
PASS	edit-relative-foreign
PASS	shellcheck-not-exec
PASS	pattern-word-not-surface
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-read-lane-root
PASS	recursive-read-fleet-root
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	quote-find-in-pattern
PASS	quote-grep-r-in-pattern
PASS	quote-bash-c-real
PASS	quote-unterminated
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-similar-prefix
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	ambig-trunc-v
PASS	ambig-trunc-allowed
PASS	scheme-xd-write
PASS	scheme-file-write
PASS	rel-fleet-report
PASS	rel-fleet-foreign
PASS	header-dotdot-rel
PASS	header-shell-test
PASS	header-markdown-link
PASS	header-bracket-text
PASS	trunc-header-nonpath
PASS	delivery-patch-unrequested
PASS	delivery-py-unrequested
PASS	delivery-neighbour
PASS	delivery-tools-still-major
PASS	signal-kill
PASS	signal-os-kill
PASS	signal-prose-not-flag
PASS	signal-sudo-kill
PASS	signal-loop-kill
PASS	signal-xargs-kill
PASS	signal-variable-kill
PASS	signal-quoted-variable
PASS	signal-zero-still-shaped
PASS	live-equals-root
PASS	live-prefix-collision
PASS	scratch-equals-root
PASS	scratch-truncated-inside
PASS	wave-summary
PASS	run-scratch-wiring
PASS	grant-unrequested.patch
PASS	grant-single-grant.patch
PASS	grant-unrequested.py
PASS	grant-single-grant.py
PASS	grant-unrequested.json
PASS	grant-single-grant.json
PASS	grant-unrequested.tsv
PASS	grant-single-grant.tsv
PASS	grant-unrequested.txt
PASS	grant-single-grant.txt
PASS	grant-write-py
PASS	grant-create-json
PASS	grant-deliver-tsv
PASS	grant-deliver-txt
PASS	grant-slot-own
PASS	grant-slot-other
PASS	grant-no-inferred-scratch
PASS	grant-incidental-not-grant
SELFTEST	pass=103	fail=0
EXIT_CODE=0
```

### R19 shape fixture

```text
CASE	pass	changed/delivery-patch	exit=0 ids=[]
CASE	discriminates	base/delivery-patch	exit=1 ids=['V-WRITE-SCOPE']
CASE	pass	changed/delivery-workdir	exit=0 ids=[]
CASE	same	base/delivery-workdir	exit=0 ids=[]
CASE	pass	changed/tools-write	exit=1 ids=['V-WRITE-SCOPE']
CASE	same	base/tools-write	exit=1 ids=['V-WRITE-SCOPE']
CASE	pass	changed/signal-kill	exit=1 ids=['V-SIGNAL']
CASE	discriminates	base/signal-kill	exit=0 ids=[]
CASE	pass	changed/signal-os-kill	exit=1 ids=['V-SIGNAL']
CASE	discriminates	base/signal-os-kill	exit=0 ids=[]
CASE	pass	changed/signal-os-killpg	exit=1 ids=['V-SIGNAL']
CASE	discriminates	base/signal-os-killpg	exit=0 ids=[]
CASE	pass	changed/signal-sudo	exit=1 ids=['V-SIGNAL']
CASE	discriminates	base/signal-sudo	exit=0 ids=[]
CASE	pass	changed/signal-loop	exit=1 ids=['V-SIGNAL']
CASE	discriminates	base/signal-loop	exit=0 ids=[]
CASE	pass	changed/signal-xargs	exit=1 ids=['V-SIGNAL']
CASE	discriminates	base/signal-xargs	exit=0 ids=[]
CASE	pass	changed/signal-variable	exit=1 ids=['V-SIGNAL']
CASE	discriminates	base/signal-variable	exit=0 ids=[]
CASE	pass	changed/signal-quoted-variable	exit=1 ids=['V-SIGNAL']
CASE	discriminates	base/signal-quoted-variable	exit=0 ids=[]
CASE	pass	changed/live-equals	exit=1 ids=['V-LIVE-CENSUS']
CASE	discriminates	base/live-equals	exit=0 ids=[]
CASE	pass	changed/live-prefix-collision	exit=1 ids=['V-LIVE-CENSUS']
CASE	discriminates	base/live-prefix-collision	exit=0 ids=[]
CASE	pass	changed/scratch-equals	exit=0 ids=[]
CASE	same	base/scratch-equals	exit=0 ids=[]
CASE	pass	changed/implicit-root-read	exit=0 ids=['V-RECURSIVE']
CASE	discriminates	base/implicit-root-read	exit=0 ids=[]
CASE	pass	changed/patch-in-tools	exit=1 ids=['V-WRITE-SCOPE']
CASE	same	base/patch-in-tools	exit=1 ids=['V-WRITE-SCOPE']
CASE	pass	changed/relative-target	exit=1 ids=['V-WRITE-RELATIVE']
CASE	same	base/relative-target	exit=1 ids=['V-WRITE-RELATIVE']
SUMMARY total=17 failed=0 base_discriminating=12
EXIT_CODE=0
```

### R20 audit contract

```text
CASE	PASS	report-own	violations=[] expected=[]
CASE	PASS	unrequested-patch	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	unrequested-py	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	unrequested-json	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	unrequested-tsv	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	unrequested-txt	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	deliver-exact-patch	violations=[] expected=[]
CASE	PASS	deliver-alternative-py	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	deliver-alternative-json	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	deliver-alternative-tsv	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	deliver-alternative-txt	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	deliver-denial-trailing-text	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	deliver-example-fenced	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	incidental-delivery-mention	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	cross-seat-stem	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	own-only-exact	violations=[] expected=[]
CASE	PASS	own-only-sibling	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	traversal	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	scratch-r20w2-exact	violations=[] expected=[]
CASE	PASS	scratch-truncated-inside-unparsed	violations=[('V-WRITE-UNPARSED', 'major')] expected=[('V-WRITE-UNPARSED', 'major')]
CASE	PASS	scratch-foreign-slot	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	scratch-no-fallback	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	scratch-r19w2-literal	violations=[] expected=[]
CASE	PASS	scratch-wave-name-only	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	scratch-r18-clone-executor	violations=[] expected=[]
CASE	PASS	scratch-r18-clone-reviewer	violations=[('V-WRITE-SCOPE', 'major')] expected=[('V-WRITE-SCOPE', 'major')]
CASE	PASS	base-overauth-deliver-alternative-json	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-overauth-deliver-alternative-py	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-overauth-deliver-alternative-tsv	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-overauth-deliver-alternative-txt	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-overauth-deliver-denial-trailing-text	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-overauth-deliver-example-fenced	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-overauth-unrequested-json	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-overauth-unrequested-patch	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-overauth-unrequested-py	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-overauth-unrequested-tsv	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-overauth-unrequested-txt	baseline_violations=[] expected_baseline=[]
CASE	PASS	base-broad-authorization-inventory	observed=['deliver-alternative-json', 'deliver-alternative-py', 'deliver-alternative-tsv', 'deliver-alternative-txt', 'deliver-denial-trailing-text', 'deliver-example-fenced', 'unrequested-json', 'unrequested-patch', 'unrequested-py', 'unrequested-tsv', 'unrequested-txt'] expected=['deliver-alternative-json', 'deliver-alternative-py', 'deliver-alternative-tsv', 'deliver-alternative-txt', 'deliver-denial-trailing-text', 'deliver-example-fenced', 'unrequested-json', 'unrequested-patch', 'unrequested-py', 'unrequested-tsv', 'unrequested-txt']
CASE	PASS	receipt-exact-digests	input_keys=['/var/tmp/souji-r20-audit-contract.2lkt0xuc/receipt-world/spec.json', '/var/tmp/souji-r20-audit-contract.2lkt0xuc/receipt-world/transcripts/MANIFEST.sha256', '/var/tmp/souji-r20-audit-contract.2lkt0xuc/receipt-world/transcripts/Seat.txt', '/var/tmp/souji-r20w2-FinalAuditRuntime/lane/tools/souji-seat-audit.py'] exact=True unchanged=True
CASE	PASS	receipt-spec-digest-change	changed=True
CASE	PASS	receipt-transcript-digest-change	changed=True
CASE	PASS	receipt-manifest-digest-change	changed=True
CASE	PASS	receipt-auditor-digest-change	changed=True reimported=True
CASE	PASS	drift-auditor	reads=2 detected=True
CASE	PASS	drift-spec	reads=2 detected=True
CASE	PASS	drift-transcript	reads=2 detected=True
CASE	PASS	drift-manifest	reads=2 detected=True
CASE	PASS	drift-auditor-after-import	refused=True
CASE	PASS	receipt-spec-transcript-alias	same_path=True reads=2 refused=True
CASE	PASS	oracle-exact-case-inventory	missing=[] extra=[]
SUMMARY	total=50	pass=50	fail=0	base_discriminating=11
EXIT_CODE=0
```
