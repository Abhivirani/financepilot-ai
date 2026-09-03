# Reconciliation Rules

This document outlines the deterministic rules used by the reconciliation engine to match records across the Invoice, Gateway, Settlement, and Bank datasets.

## 1. Exact Match Rule
- **Description:** A perfectly reconciled transaction where records exist across all datasets and amounts align.
- **Criteria:** 
  - `transaction_id` matches across Invoice, Gateway, Settlement, and Bank.
  - Gateway `gross_amount` == Invoice `total_amount`.
  - Gateway `status` == `SUCCESS` and Invoice `status` == `PAID`.
  - Settlement `net_amount` == Gateway `gross_amount` - Gateway `fee`.
  - Bank `amount` == Settlement `net_amount`.
- **Severity:** N/A (Success)
- **AI Explanation Required:** No

## 2. Amount Mismatch Rule
- **Description:** Records link correctly via `transaction_id`, but the financial figures do not align.
- **Criteria:** 
  - `transaction_id` matches.
  - Gateway `gross_amount` != Invoice `total_amount` OR
  - Bank `amount` != Settlement `net_amount` OR
  - Settlement `net_amount` != (Gateway `gross_amount` - Settlement `fee_deducted`).
- **Severity:** High
- **AI Explanation Required:** Yes (AI will explain where the discrepancy occurred and calculate the variance).

## 3. Missing Settlement Rule
- **Description:** A successful payment exists in the Gateway ledger, but there is no corresponding settlement report or bank deposit within the expected timeframe (e.g., T+2 days).
- **Criteria:** 
  - Gateway `status` == `SUCCESS`.
  - No matching `transaction_id` in Settlement or Bank datasets.
- **Severity:** High
- **AI Explanation Required:** Yes (AI will flag the missing funds and suggest checking gateway hold statuses).

## 4. Missing Invoice Rule
- **Description:** A payment was received and settled to the bank, but no corresponding internal invoice exists.
- **Criteria:**
  - `transaction_id` exists in Gateway, Settlement, and Bank.
  - `transaction_id` is missing from the Invoice dataset.
- **Severity:** Medium
- **AI Explanation Required:** Yes (AI will flag an unaccounted payment).

## 5. Duplicate Detection Rule
- **Description:** The same `transaction_id` appears multiple times where it shouldn't.
- **Criteria:**
  - Multiple rows with the same `transaction_id` in Gateway (with `SUCCESS` status), Settlement, or Bank.
- **Severity:** High
- **AI Explanation Required:** Yes (AI will explain the duplicate occurrence and suggest refunding one if both settled).

## 6. Status Mismatch Rule
- **Description:** The internal system believes a transaction is unpaid, but the gateway and bank show it as successful (or vice versa).
- **Criteria:**
  - `transaction_id` matches.
  - Gateway `status` == `SUCCESS` but Invoice `status` != `PAID`, OR
  - Gateway `status` == `FAILED` but Bank `amount` was received.
- **Severity:** Medium
- **AI Explanation Required:** Yes

## 7. Orphan Record Rule
- **Description:** A record exists in only one dataset without any links to others.
- **Criteria:**
  - A `transaction_id` appears in only one dataset (e.g., a Bank statement line item with no corresponding invoice or gateway record).
- **Severity:** Low to Medium (depending on amount)
- **AI Explanation Required:** Yes (AI will attempt to match based on amount and date if deterministic ID matching fails).

## 8. Late Settlement Rule
- **Description:** Detects settlements occurring after the allowed Service Level Agreement (SLA) (e.g., T+2 days).
- **Criteria:**
  - `settlement_date` - Gateway `date` > Allowed SLA (e.g., 2 days).
  - Gateway `status` == `SUCCESS`.
- **Severity:** Medium
- **AI Explanation Required:** Yes

## 9. Fee Mismatch Rule
- **Description:** Detects when the fee calculated by the Gateway differs from the actual fee deducted during Settlement.
- **Criteria:**
  - Gateway `fee` != Settlement `fee_deducted`.
- **Severity:** Medium
- **AI Explanation Required:** Yes

## 10. Refund Verification Rule
- **Description:** Detects transactions where the Gateway processed a refund, but the Bank settlement does not reflect the refunded amount.
- **Criteria:**
  - Gateway `status` == `REFUNDED`.
  - No matching debit entry in Bank dataset, or Settlement report does not show a negative adjustment for the refunded amount.
- **Severity:** High
- **AI Explanation Required:** Yes
