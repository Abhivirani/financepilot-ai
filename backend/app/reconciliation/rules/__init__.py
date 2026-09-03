from typing import List, Type
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.rules.amount_mismatch import AmountMismatchRule
from backend.app.reconciliation.rules.duplicate import DuplicateTransactionRule
from backend.app.reconciliation.rules.missing_settlement import MissingSettlementRule
from backend.app.reconciliation.rules.missing_invoice import MissingInvoiceRule
from backend.app.reconciliation.rules.late_settlement import LateSettlementRule
from backend.app.reconciliation.rules.fee_mismatch import FeeMismatchRule
from backend.app.reconciliation.rules.refund import RefundVerificationRule
from backend.app.reconciliation.rules.orphan import OrphanRecordRule
from backend.app.reconciliation.rules.status_mismatch import StatusMismatchRule

# Registry of all available rules
def get_all_rules() -> List[BaseRule]:
    return [
        AmountMismatchRule(),
        DuplicateTransactionRule(),
        MissingSettlementRule(),
        MissingInvoiceRule(),
        LateSettlementRule(),
        FeeMismatchRule(),
        RefundVerificationRule(),
        OrphanRecordRule(),
        StatusMismatchRule()
    ]
