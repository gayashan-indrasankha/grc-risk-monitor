-- Run in SQLite or PostgreSQL after loading the data.

-- 1) Count business records.
SELECT 'purchase_requests' AS entity, COUNT(*) AS records FROM purchase_requests
UNION ALL SELECT 'invoices', COUNT(*) FROM invoices
UNION ALL SELECT 'payments', COUNT(*) FROM payments;

-- 2) Follow one invoice through request -> invoice -> payment.
SELECT pr.request_id, s.supplier_name, pr.amount AS request_amount,
       pr.approval_status, e.full_name AS approver,
       i.invoice_id, p.payment_id, p.paid_amount, p.payment_status
FROM purchase_requests AS pr
JOIN suppliers AS s ON s.supplier_id=pr.supplier_id
LEFT JOIN employees AS e ON e.employee_id=pr.approved_by
JOIN invoices AS i ON i.request_id=pr.request_id
JOIN payments AS p ON p.invoice_id=i.invoice_id
WHERE i.invoice_id='INV-0003'
ORDER BY p.payment_id;

-- 3) Show high-value requests and their assigned approvers.
SELECT pr.request_id, pr.amount, pr.approval_status,
       pr.approved_by, e.role AS approver_role
FROM purchase_requests AS pr
LEFT JOIN employees AS e ON e.employee_id=pr.approved_by
WHERE pr.amount > 100000
ORDER BY pr.request_id;

-- 4) View the two requests linked to the same business need.
SELECT request_id, requested_on, requester_id, supplier_id,
       business_need_id, amount
FROM purchase_requests
WHERE business_need_id='NEED-SPLIT-01'
ORDER BY requested_on;
