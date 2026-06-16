what does @pytest.fixture() do ?                                                                                    

                                                                                                                      
● It marks a function as a setup helper that pytest automatically runs and injects into your tests.                 
                                                                                                                      
  Instead of repeating setup code in every test:                                                                      
  def test_valid():                                                                                                   
      validator = AmountValidator()  # repeated                                                                       
      ...                                                                                                           

  def test_invalid():
      validator = AmountValidator()  # repeated
      ...

  You define it once as a fixture:
  @pytest.fixture()
  def validator():
      return AmountValidator()

  def test_valid(validator):      # pytest sees the param name,
      ...                         # finds the fixture, runs it,
  def test_invalid(validator):    # and passes the result in
      ...

  pytest matches the parameter name in the test function to the fixture function name — that's how it knows what to
  inject.


@pytest.fixture — think of it like a factory method for tests. 
Instead of writing validator = AmountValidator() in every single test function, the fixture creates a fresh one automatically. 
Any test that has validator as a parameter gets a new instance.

❯ assert errors[0].error_code == 'AMT001'  can u explain this                                                                    
  
                                                                                                                                
● This line is asserting that the first validation error found has the error code 'AMT001'.                                   
                                                                                                                                
  Breaking it down:                                                                                                             
   
  - errors — a list of ValidationError objects returned by the AmountValidator                                                  
  - errors[0] — the first error in the list                                                                                   
  - .error_code — the error_code field on the ValidationError dataclass                                                         
  - == 'AMT001' — asserts it matches this specific code

  So the test is saying: "when I run the validator on this input, the first error it raises should be AMT001."

  To see what AMT001 actually means, it'll be defined in config/validation_rules.py under AMOUNT_RULES.

             
● AMT001 means "Amount zero" with CRITICAL severity — defined at config/validation_rules.py:51.                                 
            
  So the full picture: the test is checking that when the validator encounters a zero amount, the first error it reports is     
  AMT001 (the "Amount zero" critical error). 
  
New pattern: any() — instead of errors[0].error_code, we use any() because some tests might produce multiple errors. 
For example, 9999999999.99 triggers AMT003 (exceeds max) but might also trigger other checks. 
any() says: "I don't care about the rest, just make sure AMT003 is in there somewhere."