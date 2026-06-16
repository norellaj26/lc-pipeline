#%%
from validators.lei_validator import LeiValidator

lei = LeiValidator()

# LEI001: Missing
errors = lei.validate(field='applicant_lei', value=None)
print("Missing:", errors)

# LEI003: Bad format
errors = lei.validate(field='applicant_lei', value='INVALID!!LEI##CODE99')
print("Bad format:", errors)

# LEI004: Valid format but not in GLEIF
errors = lei.validate(field='applicant_lei', value='AAAABBBBCCCCDDDD0000')
print("Not found:", errors)

# Active LEI (Apple)
errors = lei.validate(field='applicant_lei', value='HWUPKR0MPOU8FGXBT394')
print("Apple (active):", errors)

