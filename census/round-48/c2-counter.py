#!/usr/bin/env python3
"""C2 counter (souji round 48): the census conf-name host adapter receipt.

Frozen predicate: census/round-48/preregistration.txt (C2).
Validates census/round-48/records/census-runner-output.txt at --rev — the raw
output of `bash tools/souji-census-run.sh --fleet-root <fleet> --lane <lane>`
— against census/round-48/c2-targets.tsv (columns: id, lane, form,
expected-rc, expected-ok-label, note):
  - exactly one PROVENANCE line `# fleet-script sha256=<64hex> path=...`;
  - CONF-FORM BEGIN/END and DIR-FORM BEGIN/END sections, in order;
  - the conf form's section carries a `<lane>\tmissing\t...` row and the
    population's expected rc (the documented host state: 2 — never masked);
  - the dir form's rc equals the population's expected rc (0), its section
    carries exactly one ok-line `<ok-label>\tok\t...`;
  - the final line `CENSUS-RUN lane=<lane> conf_rc=<n> dir_rc=<n>` agrees
    with the population's lane id and both expected rcs;
  - both sections nonempty (the raw fleet TSV is the evidence).
Exit 0: CENSUS-RUN forms=2 findings=0. Exit 1: any finding. Exit 2:
could-not-evaluate. Reads committed bytes at --rev by default; --file reads a
disk receipt (junk-arm control mode, never claim evidence).
"""
import argparse
import os
import re
import subprocess
import sys

RECEIPT = 'census/round-48/records/census-runner-output.txt'
TARGETS = 'census/round-48/c2-targets.tsv'
HEX64 = re.compile(r'^[0-9a-f]{64}$')


def git(root, *args):
    e = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
         'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
         'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
         'GIT_OPTIONAL_LOCKS': '0'}
    p = subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                       env=e, timeout=120)
    if p.returncode:
        raise ValueError('git input unavailable: %s' % args[0])
    return p.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', required=True)
    ap.add_argument('--rev', default=None)
    ap.add_argument('--file', default=None,
                    help='disk receipt (control arms only; never claim evidence)')
    ns = ap.parse_args()
    try:
        root = ns.root
        if ns.file:
            with open(ns.file, 'rb') as fh:
                raw = fh.read().decode('utf-8', 'replace')
            with open(os.path.join(root, TARGETS), 'rb') as fh:
                tgts = fh.read().decode('utf-8', 'replace')
        else:
            if not ns.rev or not re.fullmatch(r'[0-9a-f]{40}', ns.rev):
                raise ValueError('full 40-hex --rev required without --file')
            try:
                raw = git(root, 'show', ns.rev + ':' + RECEIPT).decode('utf-8', 'replace')
            except ValueError:
                print('CENSUS-RUN forms=0 findings=1')
                print('FINDING RECEIPT-ABSENT %s' % RECEIPT)
                return 1
            tgts = git(root, 'show', ns.rev + ':' + TARGETS).decode('utf-8', 'replace')
        pop = {}
        for line in tgts.splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            f = line.split('\t')
            if len(f) < 5 or not all(x.strip() for x in f[:5]):
                raise ValueError('malformed population row: %r' % line)
            pop[f[0]] = {'lane': f[1], 'form': f[2], 'rc': f[3], 'ok': f[4]}
        findings = []
        lines = raw.splitlines()
        prov = [l for l in lines if l.startswith('# fleet-script sha256=')]
        if len(prov) != 1 or not HEX64.match(prov[0].split('sha256=')[1].split(' ')[0]):
            findings.append('PROVENANCE-MISSING-OR-MALFORMED')

        def section(name):
            try:
                a = lines.index(name + ' BEGIN')
                b = lines.index(name + ' END', a + 1)
                return lines[a + 1:b]
            except ValueError:
                return None

        conf_sec = section('CONF-FORM')
        dir_sec = section('DIR-FORM')
        t1 = pop.get('T1-conf-name')
        t2 = pop.get('T2-lane-dir')
        if t1 is None or t2 is None:
            findings.append('POPULATION-ROWS-MISSING')
        else:
            lane = t1['lane']
            if t1['rc'] != '2':
                findings.append('POPULATION-CONF-RC-UNEXPECTED %s' % t1['rc'])
            if conf_sec is None:
                findings.append('CONF-SECTION-MISSING')
            else:
                if not any(l.startswith(lane + '\tmissing\t') for l in conf_sec):
                    findings.append('CONF-SECTION-NO-MISSING-ROW')
            if dir_sec is None:
                findings.append('DIR-SECTION-MISSING')
            else:
                ok_lines = [l for l in dir_sec
                            if re.match(r'^[a-z0-9][a-z0-9-]*\tok\t', l)]
                if len(ok_lines) != 1:
                    findings.append('DIR-OK-LINES %d' % len(ok_lines))
                elif t2['ok'] != '-' and not ok_lines[0].startswith(t2['ok'] + '\t'):
                    findings.append('DIR-OK-LABEL %s' % ok_lines[0].split('\t')[0])
                if not any('\tW04\t' in l for l in dir_sec):
                    findings.append('DIR-W04-ABSENT')
            final = [l for l in lines if l.startswith('CENSUS-RUN lane=')]
            if len(final) != 1:
                findings.append('FINAL-LINE %d' % len(final))
            else:
                m = re.match(r'^CENSUS-RUN lane=([a-z0-9-]+) conf_rc=(\d+) dir_rc=(\d+)$',
                             final[0])
                if not m:
                    findings.append('FINAL-LINE-MALFORMED %r' % final[0])
                else:
                    if m.group(1) != lane:
                        findings.append('FINAL-LANE %s' % m.group(1))
                    if m.group(2) != t1['rc']:
                        findings.append('FINAL-CONF-RC %s' % m.group(2))
                    if t2 is not None and m.group(3) != t2['rc']:
                        findings.append('FINAL-DIR-RC %s' % m.group(3))
        nforms = 2 if (conf_sec is not None and dir_sec is not None) else 0
        print('CENSUS-RUN forms=%d findings=%d' % (nforms, len(findings)))
        for x in findings:
            print('FINDING ' + x)
        return 0 if not findings else 1
    except (OSError, ValueError, TypeError, subprocess.SubprocessError,
            UnicodeError) as exn:
        print('COULD-NOT-EVALUATE ' + str(exn), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
