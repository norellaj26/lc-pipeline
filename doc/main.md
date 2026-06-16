---                                                                                                                             
  total_errors = sum(len(errs) for errs in results.values())                                                                      
  results is a dict: { transaction_id: [list of errors] }.                                                                        
  results.values() gives you all the error lists.                                                                                 
  len(errs) counts errors in each transaction.
  sum(...) adds them all up → total number of errors across all transactions.

  ---
  flagged = sum(1 for errs in results.values() if errs)
  For each transaction, if its error list is not empty (if errs), count it as 1.
  Sum of all 1s → how many transactions have at least one error.

  ---
  clean = sum(1 for errs in results.values() if not errs)
  Same idea, opposite condition — if not errs means the error list is empty.
  → how many transactions passed with zero errors.

  ---
  The big picture: Step 5 just computes 3 summary numbers from the validation results dict — total errors, flagged transactions,
  clean transactions.
  



 if __name__ == '__main__':                                                                                        
    main()                                                                                                                        
                                                                                
                                                                                                                                  
● Every Python file has a built-in variable called __name__. Its value depends on how the file is run:                            
                                                                                                                                  
  ---                                                                                                                             
  When you run it directly (python main.py):                                                                                      
  __name__ == '__main__'   ← Python sets this automatically                                                                       
  So the condition is True → main() gets called → pipeline runs.                                                                

  ---
  When another file imports it (from main import something):
  __name__ == 'main'       ← the module's own name, NOT '__main__'
  So the condition is False → main() is NOT called → nothing runs automatically.

  ---
  Why does this matter?

  Without this guard, importing anything from main.py would accidentally run the whole pipeline. With it, the file is safe to
  import from.

  Simple analogy: it's like saying "only run this if YOU are the one being executed, not if someone else is borrowing you."