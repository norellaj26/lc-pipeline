#%%
from validators.lc_validator import LcValidator

lc = LcValidator()

# LC001: Missing LC number
errors = lc.validate(field='lc_number', value=None)
print("Missing LC number:", errors)

# LC004: Invalid form
errors = lc.validate(field='lc_number', value='LC-2026-100',
                     lc_form='INVALID_FORM',
                     available_with='BY PAYMENT',
                     confirmation_status='CONFIRMED',
                     confirming_bank_swift='BARCGB22')
print("Invalid form:", errors)

# LC008: MAYBE status
errors = lc.validate(field='lc_number', value='LC-2026-100',
                     lc_form='STANDBY',
                     available_with='BY PAYMENT',
                     confirmation_status='MAYBE',
                     confirming_bank_swift=None)
print("MAYBE status:", errors)

# LC007: CONFIRMED but no bank
errors = lc.validate(field='lc_number', value='LC-2026-100',
                     lc_form='STANDBY',
                     available_with='BY PAYMENT',
                     confirmation_status='CONFIRMED',
                     confirming_bank_swift=None)
print("CONFIRMED no bank:", errors)

# Clean transaction — no errors
errors = lc.validate(field='lc_number', value='LC-2026-100',
                     lc_form='IRREVOCABLE',
                     available_with='BY NEGOTIATION',
                     confirmation_status='UNCONFIRMED',
                     confirming_bank_swift=None)
print("Clean:", errors)