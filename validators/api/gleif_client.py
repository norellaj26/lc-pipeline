import requests #  third-party Python library for making HTTP calls
from typing import Optional, Dict
from config.settings import (
    GLEIF_API_BASE,
    GLEIF_TIMEOUT_SECONDS,
)

class GleifClient:
    """Client for GLEIF LEI validation API."""

    def __init__(self) -> None:
        self._cache: Dict[str, dict] = {}

    def lookup(self, lei: str) -> dict:
        """Look up an LEI in GLEIF database.

        Returns dict with:
            'status': 'ACTIVE', 'INACTIVE', 'NOT_FOUND', or 'ERROR'
            'detail': extra info from API
        """

        # Step 1: Check cache first
        if lei in self._cache:
            return self._cache[lei]

        # Step 2: Call the API
        url = f"{GLEIF_API_BASE}/lei-records/{lei}"

        try:
            response = requests.get(url, timeout=GLEIF_TIMEOUT_SECONDS)
        except requests.RequestException as e:
            result = {'status': 'ERROR', 'detail': str(e)}
            self._cache[lei] = result
            return result

        # Step 3: Handle response
        if response.status_code == 404:
            result = {'status': 'NOT_FOUND', 'detail': 'LEI not in GLEIF database'}

        elif response.status_code == 200:
            data = response.json()
            entity_status = (
                data.get('data', {})
                .get('attributes', {})
                .get('registration', {})
                .get('status', 'UNKNOWN')
            )

            if entity_status == 'ISSUED':
                result = {'status': 'ACTIVE', 'detail': entity_status}
            else:
                result = {'status': 'INACTIVE', 'detail': entity_status}

        else:
            result = {'status': 'ERROR', 'detail': f'HTTP {response.status_code}'}

        # Step 4: Cache and return
        self._cache[lei] = result
        return result







