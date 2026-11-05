if r.returncode != 2 or "RECEIPT-ENV-CONFIG-SET" not in r.stderr:
    pass
if r.returncode != 2 or "RECEIPT-ENV-REDIRECT-SET" not in r.stderr:
    pass
