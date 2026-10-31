#!/usr/bin/env python3
from pathlib import Path
import sqlite3
ROOT=Path(__file__).resolve().parents[1]
with sqlite3.connect(ROOT/'grc_stage1.sqlite') as c:
    print('Counts:')
    for t in ('purchase_requests','invoices','payments'):
        print(f'  {t}: {c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]}')
    print('\nInvoice INV-0003 through request and payment records:')
    for r in c.execute('''
        SELECT pr.request_id, i.invoice_id, p.payment_id, p.paid_amount, p.payment_status
        FROM purchase_requests pr JOIN invoices i ON i.request_id=pr.request_id
        JOIN payments p ON p.invoice_id=i.invoice_id
        WHERE i.invoice_id='INV-0003' ORDER BY p.payment_id
    '''):
        print(' ',r)
    print('\nHigh-value requests:')
    for r in c.execute('''
        SELECT pr.request_id, pr.amount, pr.approval_status, e.role
        FROM purchase_requests pr LEFT JOIN employees e ON pr.approved_by=e.employee_id
        WHERE pr.amount>100000 ORDER BY pr.request_id
    '''):
        print(' ',r)
