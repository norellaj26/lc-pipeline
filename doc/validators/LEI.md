| Gate | Check | API needed? | Example |
|------|-------|-------------|---------|
| 1 | Is it present? | No | `None` → stop |
| 2 | Is it 20 chars? | No | `TOOSHORT123` → stop |
| 3 | Does format match regex? | No | `INVALID!!LEI##CODE99` → stop |
| 4 | Does GLEIF know this LEI? | YES | `HWUPKR0MPOU8FGXBT394` → call API |
| 5 | Is it active in GLEIF? | YES | Valid but lapsed → flag |

def __init__(self) -> None:                                                                                         
  Constructor — runs when you create a LeiValidator() instance.                                                       
                                                                                                                      
  ---                                                                                                                 
  super().__init__()                                                                                                  
  Calls BaseValidator.__init__() — runs the parent class setup first (initializes self._errors = [] and anything else
  BaseValidator sets up). You must call this or the parent's state won't exist, and methods like _add_error() would
  break.

  ---
  self._gleif_client = GleifClient()
  Creates one GleifClient instance and attaches it to this validator. This means:
  - One shared cache across all LEI lookups this validator does
  - The validator owns the client — it's an internal tool, hence the _ prefix

  ---
  So the full picture:

  validator = LeiValidator()
  # → BaseValidator.__init__() runs (sets up _errors list)
  # → GleifClient() is created and stored as _gleif_client

  When validate() is later called, self._gleif_client.lookup(lei) hits the API (or cache) to check if the LEI is real.
