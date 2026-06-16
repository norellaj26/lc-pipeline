import pandas as pd
from typing import List, Dict
from models.validation_error import ValidationError
from validators.amount_validator import AmountValidator
from validators.lei_validator import LeiValidator
from validators.swift_validator import SwiftValidator
from validators.date_validator import DateValidator
from validators.party_validator import PartyValidator
from validators.cross_validator import CrossValidator
from validators.lc_validator import LcValidator
from validators.shipment_validator import ShipmentValidator
from utils.logger import get_logger

logger = get_logger('validation')
class ValidationService:
    """Orchestrates all validators for a transaction."""

    def __init__(self) -> None:
        self._amount_validator = AmountValidator()
        self._lei_validator = LeiValidator()
        self._swift_validator = SwiftValidator()
        self._date_validator = DateValidator()
        self._party_validator = PartyValidator()
        self._cross_validator = CrossValidator()
        self._lc_validator= LcValidator()
        self._shipment_validator = ShipmentValidator()

# Notice — this is NOT a validator. It doesn't extend `BaseValidator`. It **uses** validators.
# That's the difference between inheritance ("I am a") and composition ("I have a").

    def validate_transaction(self, row: pd.Series) -> List[ValidationError]:
        """Run all validators on one transaction. Returns all errors found."""
        all_errors: List[ValidationError] = []

        # 1. Amount
        all_errors.extend(self._amount_validator.validate( # .extend() method adds all errors from each validator into the master list
            field='amount',
            value=row['amount'],
            currency=row['currency']
        ))

        # 2. LEI codes (both parties)
        for party in ['applicant', 'beneficiary']:
            all_errors.extend(self._lei_validator.validate(
                field=f'{party}_lei',
                value=row[f'{party}_lei']
            ))

        # 3. Swift codes
        swift_fields = ['issuing_bank_swift', 'advising_bank_swift']
        if row['confirmation_status'] == 'CONFIRMED':
            swift_fields.append('confirming_bank_swift')

        for field in swift_fields:
            all_errors.extend(self._swift_validator.validate(
                field=field,
                value=row[field]
            ))

        # 4. Dates
        all_errors.extend(self._date_validator.validate(
            field='issue_date',
            value=row['issue_date'],
            expiry_date=row['expiry_date'],
            shipment_date=row['latest_shipment_date']
        ))

        # 5. Party fields (both parties)
        for party in ['applicant', 'beneficiary']:
            all_errors.extend(self._party_validator.validate(
                field=party,
                value=row[f'{party}_name'],
                address=row[f'{party}_address'],
                country=row[f'{party}_country'],
                city=row[f'{party}_city'],
                postal_code=row[f'{party}_postal_code']
            ))



        # 6. LC document
        all_errors.extend(self._lc_validator.validate(
            field='lc_number',
            value=row['lc_number'],
            lc_form=row['lc_form'],
            available_with=row['available_with'],
            confirmation_status=row['confirmation_status'],
            confirmation_bank_swift=row.get('confirming_bank_swift') # optional

        ))

        #7 Shipment
        all_errors.extend(self._shipment_validator.validate(
            field='incoterm',
            value=row['incoterm'],
            port_of_loading=row.get('port_of_loading'),
            port_of_discharge=row.get('port_of_discharge'),
            partial_shipment=row.get('partial_shipment')

        ))

        # 8. Cross-validation
        all_errors.extend(self._cross_validator.validate(
            field='transaction',
            value=row['transaction_id'],
            applicant_name=row['applicant_name'],
            beneficiary_name=row['beneficiary_name'],
            issuing_bank_country=row['issuing_bank_country'],
            applicant_country=row['applicant_country']
        ))


        return all_errors

    def validate_all(self, df: pd.DataFrame) -> Dict[str, List[ValidationError]]:
        """Run all validators on every transaction. Returns dict: txn_id → errors."""
        results: Dict[str, List[ValidationError]] = {}

        for idx, row in df.iterrows():
            txn_id = row['transaction_id']
            errors = self.validate_transaction(row)
            results[txn_id] = errors

            if (idx + 1) % 50 == 0:
                logger.info(f"  Validated {idx + 1}/{len(df)} transactions...")

        return results

    """ {
    'LC-94874F': [ValidationError(...), ValidationError(...)],
    'LC-ZCOTOH': [],
    'LC-9KWV08': [ValidationError(...)],
    }"""
    # Empty list = clean transaction. List with errors = flagged. Any downstream code can easily check:
    """ for txn_id, errors in results.items():
    if errors:
        flag_it(txn_id)"""















