-- Control: NO completed payment while purchase approval is Pending or Rejected.
-- Applies regardless of amount (LKR 100k threshold governs manager approval).
SELECT pr.request_id, pr.supplier_id, s.supplier_name,
       pr.amount, pr.approval_status,
       GROUP_CONCAT(p.payment_id) AS payment_ids
FROM purchase_requests pr
JOIN suppliers s ON s.supplier_id = pr.supplier_id
JOIN invoices i ON i.request_id = pr.request_id
JOIN payments p ON p.invoice_id = i.invoice_id
WHERE pr.approval_status <> 'Approved'
  AND p.payment_status = 'Completed'
GROUP BY pr.request_id, pr.supplier_id, s.supplier_name,
         pr.amount, pr.approval_status
ORDER BY pr.request_id;
