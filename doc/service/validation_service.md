| Step | What | Who |
|------|------|-----|
| 1 | Check amounts | AmountValidator |
| 2 | Check LEI codes | LeiValidator |
| 3 | Check SWIFT codes | SwiftValidator |
| 4 | Check dates | DateValidator |
| 5 | Check party fields | PartyValidator |
| 6 | Check cross-field rules | CrossValidator |
| 7 | Collect ALL errors | ValidationService || Step | What | Who |
|------|------|-----|
| 1 | Check amounts | AmountValidator |
| 2 | Check LEI codes | LeiValidator |
| 3 | Check SWIFT codes | SwiftValidator |
| 4 | Check dates | DateValidator |
| 5 | Check party fields | PartyValidator |
| 6 | Check cross-field rules | CrossValidator |
| 7 | Collect ALL errors | ValidationService |

| Pattern | Relationship | Example |
|---------|-------------|---------|
| Inheritance | AmountValidator IS A BaseValidator | Child class |
| Composition | ValidationService HAS validators | Uses them |

 Because confirming_bank_swift is optional — it only exists when confirmation_status is "Confirmed". For unconfirmed LCs, that   
  column may not exist in the row at all.                                                                                         
                                                                                                                                  
  - row['confirming_bank_swift'] → raises KeyError if the column is missing                                                       
  - row.get('confirming_bank_swift') → returns None if the column is missing, safely                                              
                                                                                                                                  
  So .get() is a defensive move: it says "give me this value if it exists, otherwise give me None" — and None is exactly what the
  validator expects to receive when the field is absent (gate 1 in check_confirmation will catch it).

  All other fields use row['...'] because they are required columns that must always be present in the CSV.
  
● extend() adds all items from one list into another list, one by one.                                                            
                                                                                                                                
  all_errors = ['A', 'B']                                                                                                         
  new_errors = ['C', 'D']                                                                                                       
                                                                                                                                  
  all_errors.extend(new_errors)                                                                                                   
  # all_errors → ['A', 'B', 'C', 'D']

  Compare with append(), which adds the list itself as a single item:

  all_errors.append(new_errors)
  # all_errors → ['A', 'B', ['C', 'D']]  ← nested list, wrong

  ---
  In your code, each validator returns a list of ValidationError objects. extend() merges them all into one flat all_errors list:

  all_errors.extend(self._lc_validator.validate(...))   # adds LC errors
  all_errors.extend(self._swift_validator.validate(...)) # adds SWIFT errors
  # result: one flat list of all errors from all validators