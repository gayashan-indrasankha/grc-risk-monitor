#!/usr/bin/env python3
"""Generate reproducible, synthetic procurement data for the beginner GRC project.
No external packages. ALL data are fictional.
"""
from pathlib import Path
import csv
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
DATA.mkdir(parents=True, exist_ok=True)


def write_csv(name, fieldnames, rows):
    with (DATA / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

employees = [
    {'employee_id':'EMP-001','full_name':'Asha Perera','department':'IT','role':'Staff'},
    {'employee_id':'EMP-002','full_name':'Kavindu Fernando','department':'Procurement','role':'ProcurementOfficer'},
    {'employee_id':'EMP-003','full_name':'Nimali Jayasinghe','department':'Finance','role':'Manager'},
    {'employee_id':'EMP-004','full_name':'Dilan Silva','department':'Operations','role':'Staff'},
    {'employee_id':'EMP-005','full_name':'Tara Rodrigo','department':'HR','role':'Staff'},
    {'employee_id':'EMP-006','full_name':'Ruwan Senanayake','department':'Finance','role':'Staff'},
]
suppliers = [
    {'supplier_id':'SUP-001','supplier_name':'Fictional Office Supplies Ltd'},
    {'supplier_id':'SUP-002','supplier_name':'Fictional Tech Traders Ltd'},
    {'supplier_id':'SUP-003','supplier_name':'Fictional Network Services Ltd'},
    {'supplier_id':'SUP-004','supplier_name':'Fictional Facilities Co Ltd'},
    {'supplier_id':'SUP-005','supplier_name':'Fictional Training Services Ltd'},
]
write_csv('employees.csv',['employee_id','full_name','department','role'], employees)
write_csv('suppliers.csv',['supplier_id','supplier_name'], suppliers)

# 20 unique purchase requests, each linked to one invoice. There are 21 payments
# because a *second* payment was deliberately posted against INV-0003.
amounts = [22000, 76000, 85000, 125000, 42000, 165000, 15000, 92000,
           60000, 65000, 180000, 56000, 33000, 145000, 71000, 120000,
           45000, 38000, 210000, 27000]
requesters = ['EMP-001','EMP-004','EMP-005','EMP-006']
categories = ['Office Supplies','IT Equipment','Software','Facilities','Training']
requests, invoices, payments = [], [], []
base = date(2026,10,1)

for i, amount in enumerate(amounts, start=1):
    request_id=f'PR-{i:04d}'
    invoice_id=f'INV-{i:04d}'
    supplier_id=f'SUP-{((i-1)%5)+1:03d}'
    requester_id=requesters[(i-1)%4]
    category=categories[(i-1)%5]
    requested_on=base+timedelta(days=i-1)
    need_id=f'NEED-{i:04d}'
    approved_by='EMP-003' if amount>100000 else 'EMP-002'
    approval_status='Approved'
    approval_on=(requested_on+timedelta(days=1)).isoformat()

    if i in (9,10):
        # Same business need and supplier within two days; individual values < threshold,
        # sum exceeds threshold. An indicator only, NOT proof of intentional splitting.
        supplier_id='SUP-002'
        requester_id='EMP-001'
        category='IT Equipment'
        need_id='NEED-SPLIT-01'
        requested_on=date(2026,10,9)+timedelta(days=i-9)
        approval_on=(requested_on+timedelta(days=1)).isoformat()
    if i == 6:
        # Intentionally paid while approval is still pending.
        approved_by=''
        approval_status='Pending'
        approval_on=''
    if i == 14:
        # High value incorrectly approved by a procurement officer, not a manager.
        approved_by='EMP-002'

    requests.append(dict(request_id=request_id,requested_on=requested_on.isoformat(),
        requester_id=requester_id,supplier_id=supplier_id,category=category,
        business_need_id=need_id,amount=f'{amount:.2f}',approval_status=approval_status,
        approved_by=approved_by,approval_on=approval_on))
    invoices.append(dict(invoice_id=invoice_id,request_id=request_id,
        supplier_invoice_number=f'BILL-{i:04d}',
        invoiced_on=(requested_on+timedelta(days=2)).isoformat(),
        invoice_amount=f'{amount:.2f}'))
    payments.append(dict(payment_id=f'PAY-{i:04d}',invoice_id=invoice_id,
        paid_on=(requested_on+timedelta(days=4)).isoformat(),
        paid_amount=f'{amount:.2f}',payment_status='Completed'))

payments.append(dict(payment_id='PAY-0021',invoice_id='INV-0003',
    paid_on='2026-10-08',paid_amount='85000.00',payment_status='Completed'))

write_csv('purchase_requests.csv',list(requests[0]),requests)
write_csv('invoices.csv',list(invoices[0]),invoices)
write_csv('payments.csv',list(payments[0]),payments)

# This is for validation/testing only, never for real-time exception detection.
# All case labels were deliberately created, not discovered by a real audit.
truth = [
    {'scenario':'duplicate_payment','record_ids':'PAY-0003;PAY-0021','explanation':'Two completed payments on the same invoice INV-0003.'},
    {'scenario':'unapproved_large_purchase','record_ids':'PR-0006','explanation':'LKR 165000 request pending approval but its invoice has a completed payment.'},
    {'scenario':'wrong_approver_role','record_ids':'PR-0014','explanation':'LKR 145000 approved by ProcurementOfficer rather than Manager.'},
    {'scenario':'potential_split_purchase','record_ids':'PR-0009;PR-0010','explanation':'Same business need, requester and supplier; LKR 60000+65000 exceeds LKR 100000 manager threshold.'},
]
write_csv('ground_truth_FOR_TESTS_ONLY.csv',list(truth[0]),truth)

print('Generated: 6 CSV files, 6 employees, 5 suppliers, 20 requests, 20 invoices, 21 payments.')
print('All records are synthetic and must not be represented as real company data.')
