-- An invoice with 2+ COMPLETED full-value payments is a potential duplicate.
-- An invoice may have legitimate partial payments; these are excluded here.
SELECT
    i.invoice_id, i.request_id, pr.supplier_id, s.supplier_name,
    i.invoice_amount, GROUP_CONCAT(p.payment_id) AS payment_ids,
    COUNT(*) AS completed_full_payments
FROM payments p
JOIN invoices i ON i.invoice_id = p.invoice_id
JOIN purchase_requests pr ON pr.request_id = i.request_id
JOIN suppliers s ON s.supplier_id = pr.supplier_id
WHERE p.payment_status = 'Completed'
  AND p.paid_amount = i.invoice_amount
GROUP BY i.invoice_id, i.request_id, pr.supplier_id, s.supplier_name, i.invoice_amount
HAVING COUNT(*) >= 2
ORDER BY i.invoice_id;
