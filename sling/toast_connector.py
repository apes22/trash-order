"""
Toast API client — adapted from the mrkt project.

Handles authentication and order fetching for Toast POS integration.
Base URL: https://ws-api.toasttab.com
"""

import os
import time
import requests
from datetime import date, datetime
from typing import Optional

from dotenv import load_dotenv

from sling.config import TOAST_BASE_URL, TOAST_AUTH_URL, TOAST_ORDERS_URL

load_dotenv()

# Token cache: {guid: (token, expires_at_timestamp)}
_token_cache = {}


class ToastConnector:
    """Client for the Toast POS API."""

    def __init__(self, client_id=None, client_secret=None, guid=None):
        """Initialize with API credentials.

        Args:
            client_id: Toast API client ID. If None, reads from env.
            client_secret: Toast API client secret. If None, reads from env.
            guid: Toast restaurant GUID. If None, reads from env.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.guid = guid
        self._token = None
        self._token_expires = 0

    def authenticate(self, client_id=None, client_secret=None, guid=None):
        """Get a bearer token from Toast.

        Args:
            client_id: Override client_id.
            client_secret: Override client_secret.
            guid: Override guid.

        Returns:
            str: Bearer access token.
        """
        cid = client_id or self.client_id
        csecret = client_secret or self.client_secret
        g = guid or self.guid

        if not all([cid, csecret, g]):
            raise ValueError("client_id, client_secret, and guid are all required")

        # Check cache
        cached = _token_cache.get(g)
        if cached and cached[1] > time.time():
            return cached[0]

        resp = requests.post(
            TOAST_AUTH_URL,
            json={
                "clientId": cid,
                "clientSecret": csecret,
                "userAccessType": "TOAST_MACHINE_CLIENT",
            },
            headers={
                "Toast-Restaurant-External-ID": g,
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        token = data["token"]["accessToken"]

        # Cache for 25 minutes (tokens last 30)
        _token_cache[g] = (token, time.time() + 25 * 60)

        return token

    def _make_headers(self, client_id=None, client_secret=None, guid=None):
        """Build authenticated headers for Toast API calls."""
        cid = client_id or self.client_id
        csecret = client_secret or self.client_secret
        g = guid or self.guid

        token = self.authenticate(cid, csecret, g)
        return {
            "Authorization": f"Bearer {token}",
            "Toast-Restaurant-External-ID": g,
        }

    def fetch_orders(self, guid=None, client_id=None, client_secret=None,
                     business_date=None):
        """Fetch all orders for a single business date.

        Handles pagination and rate limiting with exponential backoff.

        Args:
            guid: Toast restaurant GUID.
            client_id: Toast API client ID.
            client_secret: Toast API client secret.
            business_date: date object or str (YYYY-MM-DD or YYYYMMDD).

        Returns:
            list[dict]: Parsed orders with keys: order_id, business_date,
                        closed_at, hour, day_of_week, total_amount,
                        item_count, guests.
        """
        g = guid or self.guid
        cid = client_id or self.client_id
        csecret = client_secret or self.client_secret

        if isinstance(business_date, str):
            # Handle both YYYY-MM-DD and YYYYMMDD
            business_date = business_date.replace("-", "")
        elif isinstance(business_date, date):
            business_date = business_date.strftime("%Y%m%d")

        all_orders = []
        page = 1

        while True:
            headers = self._make_headers(cid, csecret, g)
            params = {"businessDate": business_date, "pageSize": 100, "page": page}

            # Retry with backoff on rate limits
            for attempt in range(5):
                try:
                    resp = requests.get(
                        TOAST_ORDERS_URL,
                        headers=headers,
                        params=params,
                        timeout=60,
                    )
                except requests.exceptions.Timeout:
                    wait = 2 ** attempt
                    time.sleep(wait)
                    continue

                if resp.status_code == 429:
                    wait = 2 ** attempt
                    time.sleep(wait)
                    continue
                break

            resp.raise_for_status()
            orders = resp.json()

            if not orders:
                break

            for order in orders:
                parsed = self._parse_order(order)
                if parsed:
                    all_orders.append(parsed)

            if len(orders) < 100:
                break
            page += 1

        return all_orders

    @staticmethod
    def _parse_toast_timestamp(raw) -> Optional[datetime]:
        """Parse a Toast timestamp (ISO string or epoch millis)."""
        if isinstance(raw, str):
            cleaned = raw.replace("+0000", "+00:00").replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(cleaned)
            except (ValueError, TypeError):
                try:
                    return datetime.strptime(raw[:19], "%Y-%m-%dT%H:%M:%S")
                except (ValueError, TypeError):
                    return None
        elif isinstance(raw, (int, float)):
            return datetime.fromtimestamp(raw / 1000)
        return None

    @staticmethod
    def _parse_order(order: dict) -> Optional[dict]:
        """Extract scheduling-relevant fields from a raw Toast order."""
        if order.get("voided") or order.get("deleted"):
            return None

        closed_raw = (order.get("closedDate")
                      or order.get("paidDate")
                      or order.get("createdDate"))
        if not closed_raw:
            return None

        closed_dt = ToastConnector._parse_toast_timestamp(closed_raw)
        if not closed_dt:
            return None

        # Parse business date
        business_date = order.get("businessDate")
        if isinstance(business_date, int):
            bd_str = str(business_date)
            business_date = f"{bd_str[:4]}-{bd_str[4:6]}-{bd_str[6:]}"
        elif isinstance(business_date, str) and len(business_date) == 8:
            business_date = f"{business_date[:4]}-{business_date[4:6]}-{business_date[6:]}"

        # Total from checks
        total_amount = 0.0
        item_count = 0
        for check in order.get("checks", []):
            total_amount += check.get("totalAmount", 0.0) or 0.0
            for selection in check.get("selections", []):
                item_count += selection.get("quantity", 1) or 1

        return {
            "order_id": order.get("guid", ""),
            "business_date": business_date,
            "closed_at": closed_dt.isoformat(),
            "hour": closed_dt.hour,
            "day_of_week": closed_dt.strftime("%A"),
            "total_amount": round(total_amount, 2),
            "item_count": item_count,
            "guests": order.get("numberOfGuests"),
        }
