-- Screening heuristic ONLY: same supplier/requester/business need within 3 days,
-- each request <= approval threshold, combined total > threshold.
-- This is not proof of purposeful transaction splitting or fraud.
SELECT a.request_id AS first_request_id, b.request_id AS second_request_id,
       a.supplier_id, s.supplier_name, a.business_need_id, a.requester_id,
       a.amount AS first_amount, b.amount AS second_amount,
       (a.amount + b.amount) AS combined_amount,
       a.requested_on AS first_date, b.requested_on AS second_date
FROM purchase_requests a
JOIN purchase_requests b
  ON a.request_id < b.request_id
 AND a.supplier_id = b.supplier_id
 AND a.requester_id = b.requester_id
 AND a.business_need_id = b.business_need_id
JOIN suppliers s ON s.supplier_id = a.supplier_id
WHERE a.amount <= ?
  AND b.amount <= ?
  AND (a.amount + b.amount) > ?
  AND ABS(JULIANDAY(a.requested_on) - JULIANDAY(b.requested_on)) <= 3
ORDER BY a.request_id, b.request_id;
