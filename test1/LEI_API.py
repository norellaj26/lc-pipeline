#%%
from validators.api.gleif_client import GleifClient

client = GleifClient()

# Test 1: Real active LEI (Apple Inc)
result = client.lookup('HWUPKR0MPOU8FGXBT394')
print("Apple LEI:", result)

# Test 2: Fake LEI (should be NOT_FOUND)
result = client.lookup('FAKEFAKEFAKEFAKE00')
print("Fake LEI:", result)

# Test 3: Cache hit (should be instant)
result = client.lookup('HWUPKR0MPOU8FGXBT394')
print("Cached:", result)

# Test 4: Check cache size
print(f"Cache entries: {len(client._cache)}")