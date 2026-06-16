What is GLEIF?

The Global Legal Entity Identifier Foundation — they maintain the worldwide database of LEI codes.

GET https://api.gleif.org/api/v1/lei-records/{LEI}

Outcome                   Error              CodeMeaning
404 response              LEI004             LEI doesn't exist
Found but inactive        LEI005             LEI expired/lapsed
Connection/timeout error  LEI006             API failed, not our fault

requests library for HTTP calls
Try/except for network errors
Caching (don't call the API twice for the same LEI)
Respecting rate limits