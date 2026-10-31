#!/usr/bin/env python3
from pathlib import Path
import sqlite3
ROOT=Path(__file__).resolve().parents[1]
with sqlite3.connect(ROOT/'grc_stage1.sqlite') as c:
    c.execute('PRAGMA foreign_keys=ON')
    counts={t:c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('purchase_requests','invoices','payments')}
    assert counts=={'purchase_requests':20,'invoices':20,'payments':21},counts
    assert c.execute("SELECT COUNT(*) FROM payments WHERE invoice_id='INV-0003' AND payment_status='Completed'").fetchone()[0]==2
    assert c.execute("SELECT COUNT(*) FROM purchase_requests WHERE request_id='PR-0006' AND approval_status='Pending'").fetchone()[0]==1
    assert c.execute("SELECT COUNT(*) FROM purchase_requests WHERE business_need_id='NEED-SPLIT-01'").fetchone()[0]==2
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
print('PASS: table counts, duplicate fixture, pending approval, split fixture, foreign keys.')
