self.cache is a dictionary that stores API results so you don't call GLEIF repeatedly for the same LEI.             
                                                                                                                      
  self.cache: Dict[str, dict] = {}                                                                                    
  #           ^key    ^value                                                                                          
  #           LEI     API response JSON                                                                               
                                                                                                                    
  So the first time you look up "LEI_ABC123", it hits the API and stores the result:
  cache = {"LEI_ABC123": {"status": "ACTIVE", "name": "Some Corp"}}

  The second time you look up the same LEI, you return from cache instead of making another HTTP call. This is called
  memoization — trade memory for speed.


● try:                                                                                                                
      response = requests.get(url, timeout=GLEIF_TIMEOUT_SECONDS)                                                   
  except requests.RequestException as e:                                                                              
      result = {'status': 'ERROR', 'detail': str(e)}                                                                  
      self._cache[lei] = result                                                                                       
      return result                                                                                                   
                  
  try block — attempt the risky thing: make an HTTP call. This can fail for many reasons (no internet, server down,
  timeout, DNS error).
  requests.get(url, timeout=...) — makes an HTTP GET call. The timeout prevents hanging forever if GLEIF is down.
  From your settings.py: 10 seconds.


  except requests.RequestException as e — catch any network-related error. RequestException is the base class for all
  requests errors, so this catches:
  - ConnectionError — can't reach the server
  - Timeout — took longer than GLEIF_TIMEOUT_SECONDS
  - HTTPError — bad HTTP response
  - ...and more

  as e — binds the exception object to the variable e, so you can read the error message with str(e).

  Inside the except block:
  1. Build a result dict with 'status': 'ERROR' and the error message as 'detail'
  2. Cache it — so if the same LEI is looked up again, you don't hammer a broken API
  3. Return it — the caller gets a clean dict instead of a crash

  The key idea: instead of letting the program crash with an unhandled exception, you catch the failure and return a
  structured result that the rest of the pipeline can handle normally.
  
                                                                                                                  
● if response.status_code == 404                                                                                      
                                                                                                                    
  The server responded "not found" — the LEI doesn't exist in the GLEIF database at all. Build a result with          
  NOT_FOUND.                                                                                                          
                                                                                                                      
  ---                                                                                                                 
  elif response.status_code == 200

  The server responded "OK" — the LEI was found. Now parse the JSON to get the registration status.

  data = response.json()
  Converts the raw HTTP response body into a Python dict.

  ---
  The chained .get() calls:

  data.get('data', {})
      .get('attributes', {})
      .get('registration', {})
      .get('status', 'UNKNOWN')

  This is navigating the nested JSON structure the GLEIF API returns. It looks like this:

  {
    "data": {
      "attributes": {
        "registration": {
          "status": "ACTIVE"
        }
      }
    }
  }

  Each .get(key, default) step goes one level deeper.

  ---
  Why {} as the default?

  .get('data', {}) means: "if 'data' key doesn't exist, return an empty dict instead."

  Without {}, if any key is missing you'd get None, and calling .get() on None would crash:
  None.get('attributes')  # → AttributeError!

  With {} as the default, a missing key just returns an empty dict, and the next .get() safely returns its own default
   — the chain never crashes.

  The final .get('status', 'UNKNOWN') uses 'UNKNOWN' as default (a string, not {}) because that's the actual value we
  want if status is missing.
  
ISSUED = active — GLEIF's term for a valid, current LEI. Anything else (LAPSED, RETIRED, ANNULLED) means inactive

  - ISSUED — active and valid                                                                                         
  - LAPSED — expired, not renewed                                                                                     
  - PENDING_VALIDATION — submitted but not yet approved                                                               
  - RETIRED — permanently deactivated
  - DUPLICATE — duplicate record, replaced by another
