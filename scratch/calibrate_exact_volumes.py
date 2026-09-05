import json

target_bank_total = 468600.81
target_settlement_total = 447827.04
target_unmatched_total = 88954.94

# Matched Bank Sum = 468600.81 - 88954.94 = 379645.87
matched_bank_target = round(target_bank_total - target_unmatched_total, 2)

# 38 matched transactions:
avg_bank_matched = matched_bank_target / 38
matched_bank_amounts = [round(avg_bank_matched, 2)] * 38
diff_m = round(matched_bank_target - sum(matched_bank_amounts), 2)
matched_bank_amounts[-1] = round(matched_bank_amounts[-1] + diff_m, 2)

# Unmatched bank amounts (12 txns summing to 88954.94)
# Specific values for prompt examples: TXN1045: 1316.99, TXN1046: 9410.00, TXN1047: 15455.99, TXN1043: 11941.24, TXN1042: 7453.00
unmatched_bank_amounts = [
    7453.00, 8000.00, 8100.00, 8200.00, # TXN1039-1042 Amount Mismatch
    11941.24, 7000.00,                 # TXN1043-1044 Fee Mismatch
    1316.99, 9410.00,                  # TXN1045-1046 Missing Settlement
    15455.99, 3500.00,                 # TXN1047-1048 Duplicate Gateway
    4500.00,                           # TXN1049 Missing Invoice
    4077.72                            # TXN1050 Settlement Delay
]

diff_u = round(target_unmatched_total - sum(unmatched_bank_amounts), 2)
unmatched_bank_amounts[-1] = round(unmatched_bank_amounts[-1] + diff_u, 2)

# For matched transactions: gross = bank_amount / 0.98, fee = gross - bank_amount, net = bank_amount
# For unmatched transactions with settlement (TXN1039-1044, TXN1047-1048, TXN1049-1050):
# Settlement net amounts sum to target_settlement_total - sum(matched_net)
matched_settlement_total = sum(matched_bank_amounts) # net credited to bank
unmatched_settlement_target = round(target_settlement_total - matched_settlement_total, 2)

print(f"Target Bank Total: {target_bank_total}")
print(f"Calculated Bank Total: {round(sum(matched_bank_amounts) + sum(unmatched_bank_amounts), 2)}")
print(f"Target Unmatched Volume: {target_unmatched_total}")
print(f"Calculated Unmatched Volume: {round(sum(unmatched_bank_amounts), 2)}")
print(f"Target Settlement Total: {target_settlement_total}")
print(f"Target Unmatched Settlement Total: {unmatched_settlement_target}")
