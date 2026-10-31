-- GRC Risk Monitor Stage 1: portable SQL for SQLite and PostgreSQL.
-- Domain: fictional procurement, NOT genuine company transactions.
-- Business rules exceeding simple table constraints are tested in Stage 2.

CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    department TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Staff','ProcurementOfficer','Manager'))
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id TEXT PRIMARY KEY,
    supplier_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS purchase_requests (
    request_id TEXT PRIMARY KEY,
    requested_on DATE NOT NULL,
    requester_id TEXT NOT NULL REFERENCES employees(employee_id),
    supplier_id TEXT NOT NULL REFERENCES suppliers(supplier_id),
    category TEXT NOT NULL,
    business_need_id TEXT NOT NULL,
    amount NUMERIC(12,2) NOT NULL CHECK(amount > 0),
    approval_status TEXT NOT NULL CHECK(approval_status IN ('Approved','Pending','Rejected')),
    approved_by TEXT REFERENCES employees(employee_id),
    approval_on DATE
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE REFERENCES purchase_requests(request_id),
    supplier_invoice_number TEXT NOT NULL,
    invoiced_on DATE NOT NULL,
    invoice_amount NUMERIC(12,2) NOT NULL CHECK(invoice_amount > 0)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL REFERENCES invoices(invoice_id),
    paid_on DATE NOT NULL,
    paid_amount NUMERIC(12,2) NOT NULL CHECK(paid_amount > 0),
    payment_status TEXT NOT NULL CHECK(payment_status IN ('Completed','Pending','Cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_invoices_request ON invoices(request_id);
CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_id);
CREATE INDEX IF NOT EXISTS idx_requests_supplier_need ON purchase_requests(supplier_id,business_need_id);
