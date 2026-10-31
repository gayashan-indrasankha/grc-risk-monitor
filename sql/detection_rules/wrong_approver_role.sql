-- Control: purchases > LKR 100,000 require an employee with role Manager.
-- Placeholder ? is supplied by Python. Check only requests with completed payments.
SELECT pr.request_id, pr.supplier_id, s.supplier_name,
       pr.amount, pr.approved_by,
       COALESCE(e.role, 'Missing approver') AS actual_role
FROM purchase_requests pr
JOIN suppliers s ON s.supplier_id = pr.supplier_id
LEFT JOIN employees e ON e.employee_id = pr.approved_by
WHERE pr.amount > ?
  AND pr.approval_status = 'Approved'
  AND (e.role IS NULL OR e.role <> 'Manager')
  AND EXISTS (
    SELECT 1 FROM invoices i
    JOIN payments p ON p.invoice_id = i.invoice_id
    WHERE i.request_id = pr.request_id AND p.payment_status = 'Completed'
  )
ORDER BY pr.request_id;
