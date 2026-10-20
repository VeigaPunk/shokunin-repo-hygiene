STATUS: DONE — targeted redaction probe found three credential-shaped argv values emitted verbatim.

## Attacked claim

C3 (`tools/souji-proc-census.sh`): redaction of command arguments in the process-residue census.

## Findings

### HIGH — Authorization, AWS-shaped, and Slack-shaped secrets are not redacted

`tools/souji-proc-census.sh:186-211` redacts `--token=…`, `ghp_…`, `sk-…`, `password=…`, and URL userinfo, then outputs the result. There is no redaction for Authorization/Bearer header values, `AKIA…`, or `xoxb-…` values. The isolated live probe produced these command fields verbatim:

- `-H Authorization: Bearer x`
- `AKIA1234567890123456`
- `xoxb-test`

The other requested patterns were masked in that probe: `--token=abc` → `--token= [REDACTED]`; `ghp_xxx` → `ghp_[REDACTED]`; `sk-test` → `sk-[REDACTED]`; `https://user:pass@host` → `https://[REDACTED] @host`; `password=sample` → `password= [REDACTED]`.

The current P6 fixture at `tests/fixtures/r18-proc-census.sh:317-319,437-450` exercises only a `--password=` canary and checks that canary is absent plus a generic redaction marker; it does not catch these three leaking forms.

**Smallest fix:** add masking for the Authorization/Bearer argument sequence and the AWS/Slack token forms to `redact_command`, then add distinct fixture argv cases asserting their values do not appear in `cmd`.

## Commands and observed output

Prepared the detached clone at the assigned commit:

```text
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18w2-RevRedactionLanded/lane && git -C /var/tmp/souji-r18w2-RevRedactionLanded/lane checkout --quiet --detach 5efb519f00075d958c3d1109ef6fcb24c487eb87
git -C /var/tmp/souji-r18w2-RevRedactionLanded/lane rev-parse HEAD
5efb519f00075d958c3d1109ef6fcb24c487eb87
```

The synchronized harness command was:

```sh
python3 -c 'import os, signal, subprocess
root="/var/tmp/souji-r18w2-RevRedactionLanded"
cases=[("token","--token=abc"),("github","ghp_xxx"),("openai","sk-test"),("url","https://user:pass@host"),("password","password=sample"),("authorization","-H","Authorization:","Bearer","x"),("aws","AKIA1234567890123456"),("slack","xoxb-test")]
procs=[]
try:
 for i,case in enumerate(cases,1):
  d=f"{root}/deleted-{i}"
  os.mkdir(d)
  p=subprocess.Popen(["python3","-c","import time; time.sleep(600)",*case[1:]],cwd=d)
  procs.append((case[0],p))
  os.rmdir(d)
 r=subprocess.run([root+"/lane/tools/souji-proc-census.sh","--prefix",root],text=True,capture_output=True,timeout=20)
 print("CENSUS_STATUS="+str(r.returncode))
 rows={line.split("\t",1)[0]:line for line in r.stdout.splitlines() if line and not line.startswith("#") and not line.startswith("pid\t")}
 for label,p in procs:
  print(label+"\t"+rows.get(str(p.pid),"<missing row>"))
 print("CENSUS_STDERR="+r.stderr.replace("\n","\\n"))
finally:
 for label,p in procs:
  try: os.kill(p.pid,signal.SIGKILL)
  except ProcessLookupError: pass
  p.wait()
 print("SLEEPERS_CLEANED="+str(len(procs)))'
```
Started eight Python sleeper processes, one per fake pattern, with each process's cwd in a distinct `/var/tmp/souji-r18w2-RevRedactionLanded/deleted-N` directory; removed each directory after `Popen` established the cwd. Ran the cloned census tool with `--prefix /var/tmp/souji-r18w2-RevRedactionLanded`, captured stdout/stderr, then SIGKILLed and waited on the eight recorded PIDs. The exact census invocation and target rows were:

```text
/var/tmp/souji-r18w2-RevRedactionLanded/lane/tools/souji-proc-census.sh --prefix /var/tmp/souji-r18w2-RevRedactionLanded
CENSUS_STATUS=0
CENSUS_STDERR=
-H Authorization: Bearer x
AKIA1234567890123456
xoxb-test
SLEEPERS_CLEANED=8
```

All eight rows appeared, including the five masked cases listed above. An initial harness attempt raced directory removal against the worker's `cd` (`cd: i/o error`), started no sleeper, and is not used as evidence; the synchronized retry above is the result.

## Verdict

**Fails** the tested redaction expectation: the Authorization bearer value, AWS-shaped value, and Slack-shaped value leak to the census output. No source files were modified. The fixture was inspected but not executed; only the explicitly authorized census-tool probe was run. No tools were installed.

LSP availability check: `read xd://lsp` returned “No such tool” and listed the mounted devices without an LSP device; references/definition/diagnostics therefore were unavailable.