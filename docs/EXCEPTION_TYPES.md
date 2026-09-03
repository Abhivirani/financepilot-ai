# Exception Types Catalog

This document provides a catalog of all financial exception types detected by FinancePilot AI during the reconciliation process.

## 1. AMOUNT_MISMATCH
- **Description:** The monetary value recorded in one dataset does not mathematically align with the corresponding value in another linked dataset.
- **Possible Causes:** Partial refunds not recorded internally, incorrect fee application by the gateway, dynamic currency conversion differences, or manual entry errors.
- **Detection Rule:** `Amount Mismatch Rule`
- **Recommended User Action:** Review the invoice against the gateway dashboard to verify if a partial refund or discount was applied post-purchase.
- **AI Explanation:** Yes

## 2. MISSING_SETTLEMENT
- **Description:** A payment was successfully processed by the gateway, but the funds have not been deposited into the bank account within the standard settlement window.
- **Possible Causes:** Gateway risk holds, weekend/holiday delays, incorrect bank account configuration in the gateway, or settlement batching issues.
- **Detection Rule:** `Missing Settlement Rule`
- **Recommended User Action:** Check the payment gateway portal for active holds on the transaction or contact gateway support.
- **AI Explanation:** Yes

## 3. UNACCOUNTED_PAYMENT (MISSING_INVOICE)
- **Description:** Funds were received and settled, but there is no corresponding invoice or order record in the internal system.
- **Possible Causes:** System sync failures during order creation, test transactions, or out-of-band manual payments.
- **Detection Rule:** `Missing Invoice Rule`
- **Recommended User Action:** Investigate the `transaction_id` in the gateway to identify the customer, then manually create the missing invoice.
- **AI Explanation:** Yes

## 4. DUPLICATE_TRANSACTION
- **Description:** Multiple successful records exist for a single `transaction_id`.
- **Possible Causes:** User clicking "Pay" multiple times, webhook retry storms causing duplicate internal records, or data export anomalies.
- **Detection Rule:** `Duplicate Detection Rule`
- **Recommended User Action:** Verify if the customer was charged twice. If so, initiate a refund for the duplicate charge.
- **AI Explanation:** Yes

## 5. STATUS_DISCREPANCY
- **Description:** The transaction status is inconsistent across platforms (e.g., marked FAILED in gateway but funds arrived in bank, or marked SUCCESS in gateway but UNPAID internally).
- **Possible Causes:** Dropped webhooks, manual status overrides, or delayed bank confirmations.
- **Detection Rule:** `Status Mismatch Rule`
- **Recommended User Action:** Update the internal invoice status to match the ground truth (Gateway/Bank).
- **AI Explanation:** Yes

## 6. ORPHAN_BANK_DEPOSIT
- **Description:** A credit exists on the bank statement that cannot be linked to any gateway settlement or invoice.
- **Possible Causes:** Direct bank transfers from customers, merchant cash advances, interest payouts, or unrelated business income.
- **Detection Rule:** `Orphan Record Rule`
- **Recommended User Action:** Manually reconcile against non-gateway accounting records.
- **AI Explanation:** Yes (AI will highlight potential matches based on amount/date proximity if available).

## 7. LATE_SETTLEMENT
- **Description:** A settlement occurred, but it was processed after the allowed Service Level Agreement (SLA) time frame (e.g., beyond T+2 days).
- **Possible Causes:** Bank holidays, gateway technical delays, or risk-related holding periods.
- **Detection Rule:** `Late Settlement Rule`
- **Recommended User Action:** Monitor for systemic gateway delays and negotiate SLA credits with the payment provider if recurring.
- **AI Explanation:** Yes

## 8. FEE_MISMATCH
- **Description:** The fee amount captured by the gateway at the time of the transaction does not match the actual fee deducted during the final settlement.
- **Possible Causes:** Tiered pricing errors, tax calculation differences (e.g., GST changes), or delayed cross-border markup applications.
- **Detection Rule:** `Fee Mismatch Rule`
- **Recommended User Action:** Review the gateway pricing agreement and dispute the incorrect fee deductions with the provider.
- **AI Explanation:** Yes

## 9. REFUND_NOT_SETTLED
- **Description:** A transaction was marked as refunded in the gateway, but the bank account has not been debited for the refund amount, or the settlement batch does not reflect the negative balance.
- **Possible Causes:** Stuck gateway processing, delayed batching, or a failed API call to the issuing bank.
- **Detection Rule:** `Refund Verification Rule`
- **Recommended User Action:** Escalate to gateway support to ensure the customer receives their refunded money and internal ledgers align.
- **AI Explanation:** Yes
