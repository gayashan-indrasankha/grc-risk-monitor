# Stage 1 Data Dictionary

All names and transactions are **fictional**. Currency: LKR.

| Entity | Primary key | Meaning | Important relationships |
|---|---|---|---|
| employees | employee_id | People who request or approve spending | purchase_requests.requester_id / approved_by |
| suppliers | supplier_id | Companies that sell goods/services | purchase_requests.supplier_id |
| purchase_requests | request_id | Internal purchase request and approval | requester, supplier, approver |
| invoices | invoice_id | Invoice for a given approved/requested purchase | request_id, unique in this simplified model |
| payments | payment_id | Actual payment attempt/record | invoice_id; **not unique** (can be paid twice) |

## Fictional control policy

1. A purchase above **LKR 100,000** must be approved by an employee whose `role` is `Manager` before a payment is completed.
2. No payment should be completed while the purchase's approval status is pending or rejected.
3. A single invoice should normally not receive two **completed full-value payments**. Legitimate partial payments, refunds and corrections require further logic in a production system.
4. Multiple nearby requests for the same `business_need_id`, supplier and requester may suggest an attempt to split spending below an approval threshold. They are **investigation leads**, not confirmed misconduct.

## Table attributes

**employees:** `employee_id`, `full_name`, `department`, `role`.

**suppliers:** `supplier_id`, `supplier_name`.

**purchase_requests:** `request_id`, `requested_on`, `requester_id` (FK), `supplier_id` (FK), `category`, `business_need_id`, `amount`, `approval_status`, `approved_by` (nullable FK), `approval_on`.

**invoices:** `invoice_id`, `request_id` (unique FK), `supplier_invoice_number`, `invoiced_on`, `invoice_amount`.

**payments:** `payment_id`, `invoice_id` (FK), `paid_on`, `paid_amount`, `payment_status`.

## Why these tables are separate

- A supplier can receive many purchase requests.
- An employee can create and approve many requests (with policy restrictions enforced in the application).
- A purchase request has one invoice in this **simplified** model.
- An invoice can have many payment records; this is necessary to detect accidental duplicate payments.
- `business_need_id` groups related purchases so possible split requests can be investigated.

## Planted cases in the dataset

The validation-only file `ground_truth_FOR_TESTS_ONLY.csv` labels four deliberate patterns:
- `PAY-0003` + `PAY-0021`: two completed payments on invoice `INV-0003`.
- `PR-0006`: LKR 165,000 payment with pending approval.
- `PR-0014`: LKR 145,000 purchase approved by a procurement officer, not a manager.
- `PR-0009` + `PR-0010`: a shared business need with amounts LKR 60,000 and 65,000.

Avoid reading the ground-truth file in the future detection engine; use it only to **test** that your rules find the planted cases.
