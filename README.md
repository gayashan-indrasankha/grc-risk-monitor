# GRC Risk Monitoring — Stage 1: Understand the Business & Database

This is a beginner-friendly, **fully synthetic** demonstration for a future Power BI + Power Automate risk monitoring project. It is not a finished GRC system.

## Business story

A fictional Sri Lankan company purchases goods from suppliers. An employee creates a purchase request; an authorized employee approves it; a supplier sends an invoice; finance creates a payment. Internal audit needs to monitor whether purchasing rules are followed.

`Employee requests purchase -> Approval -> Supplier invoice -> Payment -> Exception monitoring -> Human review`

## Fictional purchasing policies

- Purchases over LKR 100,000 require a **manager's** approval before payment.
- Payments must not complete if approval is pending or rejected.
- Full payment of the same invoice more than once needs investigation.
- Several related purchases just under a threshold may need investigation.

## Data model

```text
employees --(requester_id / approved_by)--> purchase_requests <--(supplier_id)-- suppliers
                                             |
                                             | 1 to 1 (simplified)
                                             v
                                           invoices
                                             |
                                             | 1 to many
                                             v
                                           payments
```

See `docs/data_dictionary.md` and `sql/schema.sql`.

## What you get

- 6 employee records, 5 suppliers
- 20 purchase requests
- 20 invoices
- 21 payment records (one duplicate payment deliberately planted)
- 4 planted scenarios, labeled in `data/ground_truth_FOR_TESTS_ONLY.csv`
- Schema and read-only SQL exploration queries

## Try it locally (Python 3; no external packages)

```bash
python scripts/generate_sample_data.py
python scripts/setup_local.py
python scripts/check_stage1.py
```

This creates `grc_stage1.sqlite`, a local SQL database. Open it in DB Browser for SQLite, or use your IDE's database explorer. `setup_local.py` **deletes and recreates** only this demo database file; do not point it at business data.

You can run `sql/first_queries.sql` against the local database; a Python query runner is also provided:

```bash
python scripts/run_queries.py
```

## For PostgreSQL later

Use the same `sql/schema.sql` to create the tables in an empty PostgreSQL database, then import CSV files in this order: employees, suppliers, purchase_requests, invoices, payments. For example with psql after creating the tables:

```text
\copy employees FROM 'data/employees.csv' CSV HEADER
\copy suppliers FROM 'data/suppliers.csv' CSV HEADER
\copy purchase_requests FROM 'data/purchase_requests.csv' CSV HEADER
\copy invoices FROM 'data/invoices.csv' CSV HEADER
\copy payments FROM 'data/payments.csv' CSV HEADER
```

These paths are relative to the current working directory of `psql`. Python + SQLite is enough for Stage 1.

## Your Stage 1 completion criteria

1. Explain what a purchase request, invoice, payment and approver are.
2. Explain the fictional LKR 100,000 control policy.
3. Run the scripts and confirm counts 20 / 20 / 21.
4. Follow invoice `INV-0003` through its request and **two payments**.
5. Explain why `invoice_id` is **not unique** in the payments table.
6. Explain why a flagged exception does not automatically prove fraud.

**Next stage:** write SQL/Python rules to flag the four planted exception scenarios, without referring to the ground-truth labels during detection. Then validate detected results against the labels.
