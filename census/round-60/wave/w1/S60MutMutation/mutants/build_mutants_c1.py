#!/usr/bin/env python3
"""Generate C1 mutants (full files) from the --substance arm candidate bytes.

Every mutation is an exact single-occurrence replacement; the generator aborts
unless each anchor occurs exactly once, so no mutant can silently equal the
pristine file.
"""
import hashlib
import os
import sys

PRISTINE = sys.argv[1]
OUTDIR = sys.argv[2]

DIGEST_BLOCK = '''    if counter_blob is not None:
        isum = first("instrument_sha256=")
        want = hashlib.sha256(counter_blob).hexdigest()
        if isum is None:
            out.append((label, "CONTROL-INSTRUMENT-MISSING", "%s has no instrument_sha256= line" % path))
        elif isum != want:
            out.append((label, "CONTROL-INSTRUMENT-MISMATCH",
                        "%s instrument_sha256=%r is not the Counter digest %s" % (path, isum, want)))
'''

INSTR_NAME = '''    elif inst != counter_path:
        out.append((label, "CONTROL-INSTRUMENT-MISMATCH",
                    "%s instrument=%r is not the declared Counter %r" % (path, inst, counter_path)))
'''

CMD_MISMATCH = '''    elif counter_path not in cmd:
        out.append((label, "CONTROL-COMMAND-MISMATCH",
                    "%s command=%r does not mention Counter %r" % (path, cmd, counter_path)))
'''

MUTANTS = []


def mutant(name, why, *repls):
    MUTANTS.append((name, why, repls))


mutant("c1-m1-digest-skipped",
       "keeps the instrument_sha256= presence check but never compares it to the Counter digest",
       (DIGEST_BLOCK,
        '''    if counter_blob is not None:
        isum = first("instrument_sha256=")
        if isum is None:
            out.append((label, "CONTROL-INSTRUMENT-MISSING", "%s has no instrument_sha256= line" % path))
'''))

mutant("c1-m2-digest-self",
       "compares instrument_sha256= against itself (receipt-internal consistency), not the Counter bytes",
       ('        want = hashlib.sha256(counter_blob).hexdigest()\n', '        want = isum\n'))

mutant("c1-m3-rev-at-freeze",
       "drops the strictness of the rev test, so the freeze commit itself counts as before-freeze",
       ('        elif cid == freeze or not repo.is_ancestor(cid, freeze):\n',
        '        elif not repo.is_ancestor(cid, freeze):\n'))

mutant("c1-m4-command-skipped",
       "never checks that command= mentions the declared Counter path",
       (CMD_MISMATCH, ''))

mutant("c1-m5-instrument-name-ignored",
       "never checks that instrument= equals the declared Counter path",
       (INSTR_NAME, ''))

mutant("c1-m6-command-missing-skipped",
       "does not refuse a receipt that lacks a command= line entirely",
       ('''    if cmd is None:
        out.append((label, "CONTROL-COMMAND-MISSING", "%s has no command= line" % path))
    elif counter_path not in cmd:
''', '''    if cmd is not None and counter_path not in cmd:
'''))

mutant("c1-m7-rev-missing-skipped",
       "does not refuse a receipt that lacks a rev= line entirely",
       ('''    rv = first("rev=")
    if rv is None:
        out.append((label, "CONTROL-REV-MISSING", "%s has no rev= line" % path))
    else:
''', '''    rv = first("rev=")
    if rv is not None:
'''))

mutant("c1-m8-rev-invalid-skipped",
       "treats an unresolvable rev= as acceptable instead of CONTROL-REV-INVALID",
       ('''        if cid is None:
            out.append((label, "CONTROL-REV-INVALID", "%s rev=%r does not resolve to a commit" % (path, rv)))
        elif cid == freeze or not repo.is_ancestor(cid, freeze):
''', '''        if cid is None:
            pass
        elif cid == freeze or not repo.is_ancestor(cid, freeze):
'''))


def main():
    with open(PRISTINE, "rb") as f:
        src = f.read().decode("utf-8")
    os.makedirs(OUTDIR, exist_ok=True)
    print("pristine=%s sha256=%s" % (PRISTINE, hashlib.sha256(src.encode()).hexdigest()))
    for name, why, repls in MUTANTS:
        cur = src
        for old, new in repls:
            n = cur.count(old)
            if n != 1:
                sys.exit("ANCHOR %s: %r occurs %d times (want 1)" % (name, old[:60], n))
            cur = cur.replace(old, new)
        if cur == src:
            sys.exit("mutant %s is byte-identical to pristine" % name)
        path = os.path.join(OUTDIR, name + ".py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(cur)
        os.chmod(path, 0o755)
        print("%s sha256=%s why=%s" % (name, hashlib.sha256(cur.encode()).hexdigest(), why))


if __name__ == "__main__":
    main()
