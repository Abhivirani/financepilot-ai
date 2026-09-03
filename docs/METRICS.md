# Dashboard Metrics

This document defines the Key Performance Indicators (KPIs) to be displayed on the FinancePilot AI dashboard. These metrics provide a comprehensive view of operational efficiency, financial health, and AI utilization.

## Operational Metrics

### 1. Total Transactions
- **Formula:** `COUNT(Gateway.gateway_txn_id)`
- **Description:** The absolute volume of transactions processed through the payment gateway within the selected time period.
- **Why finance teams care:** Provides a baseline understanding of business volume and scale.

### 2. Total Matched
- **Formula:** `COUNT(Transactions where Reconciliation Status == EXACT_MATCH)`
- **Description:** The number of transactions that successfully reconciled across Invoice, Gateway, Settlement, and Bank datasets without discrepancies.
- **Why finance teams care:** Indicates the volume of "happy path" transactions requiring zero manual intervention.

### 3. Total Exceptions
- **Formula:** `COUNT(Transactions where Exception exists)`
- **Description:** The absolute number of transactions flagged with one or more reconciliation errors (e.g., mismatch, missing settlement).
- **Why finance teams care:** Highlights the current backlog of operational issues that require investigation.

### 4. Match Rate
- **Formula:** `(Total Matched / Total Transactions) * 100`
- **Description:** The percentage of transactions that reconciled perfectly automatically.
- **Why finance teams care:** This is the primary efficiency KPI. A higher match rate means lower operational overhead.

### 5. Duplicate Rate
- **Formula:** `(COUNT(Duplicate Exceptions) / Total Transactions) * 100`
- **Description:** The percentage of transactions processed more than once.
- **Why finance teams care:** High duplicate rates indicate systemic checkout or webhook issues, leading to customer complaints and chargebacks.

### 6. Settlement Success Rate
- **Formula:** `(COUNT(Transactions with Settlement_Status == SETTLED) / Total Transactions) * 100`
- **Description:** The percentage of processed payments that have successfully arrived in the bank account.
- **Why finance teams care:** Crucial for cash flow predictability.

### 7. Settlement Delay Rate
- **Formula:** `(COUNT(Transactions with LATE_SETTLEMENT Exception) / Total Settled Transactions) * 100`
- **Description:** The percentage of settlements that breached the agreed-upon SLA timeline.
- **Why finance teams care:** Identifies gateway unreliability, potentially triggering SLA penalty clauses.

### 8. Average Settlement Time
- **Formula:** `AVERAGE(Settlement Date - Gateway Capture Date)`
- **Description:** The average number of days it takes for a customer's payment to arrive in the bank.
- **Why finance teams care:** Directly impacts working capital and liquidity forecasting.

### 9. Processing Time
- **Formula:** `Total runtime of the reconciliation engine for the batch`
- **Description:** How long the system took to ingest, validate, and reconcile the uploaded datasets.
- **Why finance teams care:** Demonstrates the speed and efficiency of the automated tool vs. manual spreadsheet work.

---

## Financial Metrics

### 1. Total Payment Volume (TPV)
- **Formula:** `SUM(Gateway.gross_amount)`
- **Description:** The gross monetary value of all processed transactions.
- **Why finance teams care:** Top-line revenue indicator for the digital channel.

### 2. Total Gateway Fees
- **Formula:** `SUM(Settlement.fee_deducted)`
- **Description:** The total cost paid to the payment provider for processing the transactions.
- **Why finance teams care:** Cost center tracking to evaluate payment gateway profitability and margins.

### 3. Total Settlement Amount
- **Formula:** `SUM(Settlement.net_amount)`
- **Description:** The actual cash deposited into the bank account (TPV - Fees).
- **Why finance teams care:** The ground truth for cash available to the business.

### 4. Total Pending Settlement
- **Formula:** `SUM(Gateway.gross_amount where Settlement is missing or PENDING)`
- **Description:** The cash value of transactions that have been paid by the customer but are still held by the gateway.
- **Why finance teams care:** Represents accounts receivable from the payment provider.

### 5. Refund Amount
- **Formula:** `SUM(Gateway.gross_amount where status == REFUNDED)`
- **Description:** Total monetary value returned to customers.
- **Why finance teams care:** High refund volumes can indicate product quality issues or fraud, and impact net revenue.

---

## AI Metrics

### 1. AI Explanations Generated
- **Formula:** `COUNT(Exceptions with an AI-generated explanation)`
- **Description:** The total number of discrepancies successfully analyzed and explained by the LLM.
- **Why finance teams care:** Shows the ROI of the AI feature in reducing manual investigation time.

### 2. Manual Reviews Required
- **Formula:** `Total Exceptions - AI Explanations Generated` (or where AI confidence is low).
- **Description:** Exceptions that the AI could not confidently resolve, requiring human intervention.
- **Why finance teams care:** Identifies edge cases and measures the remaining manual workload.

### 3. AI Confidence Score
- **Formula:** `AVERAGE(Confidence Score returned by LLM per explanation)`
- **Description:** An aggregate metric of how certain the AI is about its exception diagnoses.
- **Why finance teams care:** Builds trust in the system. Consistently low scores indicate the AI needs better context or prompts.
