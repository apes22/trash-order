"""
Sling API client — reusable connector for schedule management.

Handles authentication, user/group lookups, and shift CRUD operations.
Base URL: https://api.getsling.com
Auth: Authorization header with token from .env
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

from sling.config import SLING_BASE_URL

load_dotenv()


class SlingConnector:
    """Client for the Sling scheduling API."""

    def __init__(self, auth_token=None):
        """Initialize with auth token.

        Args:
            auth_token: Sling API token. If None, reads from SLING_AUTH_TOKEN env var.
        """
        self.base_url = SLING_BASE_URL
        self.token = auth_token or os.getenv("SLING_AUTH_TOKEN", "")
        self.headers = {"Authorization": self.token}

    def _get(self, path, params=None):
        """Make an authenticated GET request.

        Args:
            path: API path (e.g., "/v1/users")
            params: Optional query parameters dict.

        Returns:
            Parsed JSON response.

        Raises:
            requests.HTTPError: On non-2xx status codes.
        """
        url = f"{self.base_url}{path}"
        resp = requests.get(url, headers=self.headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path, json_data=None):
        """Make an authenticated POST request.

        Args:
            path: API path.
            json_data: Request body dict.

        Returns:
            Parsed JSON response.
        """
        url = f"{self.base_url}{path}"
        resp = requests.post(url, headers=self.headers, json=json_data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _put(self, path, json_data=None):
        """Make an authenticated PUT request."""
        url = f"{self.base_url}{path}"
        resp = requests.put(url, headers=self.headers, json=json_data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path):
        """Make an authenticated DELETE request."""
        url = f"{self.base_url}{path}"
        resp = requests.delete(url, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.status_code

    # ── Read operations ──────────────────────────────────────────────────

    def authenticate(self):
        """Verify the auth token is valid by fetching the current user.

        Returns:
            dict: Current user info, or raises on invalid token.
        """
        return self._get("/v1/users/me")

    def get_users(self):
        """Fetch all active users in the organization.

        Returns:
            list[dict]: Each user with id, name, lastname, email, etc.
        """
        return self._get("/v1/users")

    def get_groups(self):
        """Fetch all groups (positions and locations).

        Returns:
            dict: {"positions": {id: name}, "locations": {id: name}}
        """
        groups = self._get("/v1/groups")
        positions = {}
        locations = {}
        for g in groups:
            gtype = g.get("type", "")
            gid = g["id"]
            gname = g.get("name", f"Unknown-{gid}")
            if gtype == "position":
                positions[gid] = gname
            elif gtype == "location":
                locations[gid] = gname
        return {"positions": positions, "locations": locations}

    def get_shifts(self, start_date, end_date):
        """Fetch schedule data for a date range.

        Args:
            start_date: Start date (str YYYY-MM-DD or date object)
            end_date: End date (str YYYY-MM-DD or date object)

        Returns:
            list[dict]: Raw calendar/shift entries from Sling.
        """
        if hasattr(start_date, "strftime"):
            start_date = start_date.strftime("%Y-%m-%d")
        if hasattr(end_date, "strftime"):
            end_date = end_date.strftime("%Y-%m-%d")

        return self._get(f"/v1/calendar/{start_date}/{end_date}")

    # ── Write operations ─────────────────────────────────────────────────

    def create_shift(self, date_str, start_time, end_time, user_id,
                     position_id, location_id):
        """Create a new shift in Sling.

        Args:
            date_str: Date string YYYY-MM-DD
            start_time: ISO datetime string for shift start
            end_time: ISO datetime string for shift end
            user_id: Sling user ID (int)
            position_id: Sling position/group ID (int)
            location_id: Sling location/group ID (int)

        Returns:
            dict: Created shift data from Sling.
        """
        payload = {
            "dtstart": start_time,
            "dtend": end_time,
            "type": "shift",
            "status": "draft",
            "user": {"id": user_id},
            "position": {"id": position_id},
            "location": {"id": location_id},
        }
        return self._post("/v1/calendar", json_data=payload)

    def update_shift(self, shift_id, **kwargs):
        """Update an existing shift.

        Args:
            shift_id: Sling shift ID
            **kwargs: Fields to update. Supported:
                - dtstart (str): New start time
                - dtend (str): New end time
                - user_id (int): Reassign to different user
                - position_id (int): Change position
                - status (str): e.g., "published", "draft"

        Returns:
            dict: Updated shift data.
        """
        payload = {}
        if "dtstart" in kwargs:
            payload["dtstart"] = kwargs["dtstart"]
        if "dtend" in kwargs:
            payload["dtend"] = kwargs["dtend"]
        if "user_id" in kwargs:
            payload["user"] = {"id": kwargs["user_id"]}
        if "position_id" in kwargs:
            payload["position"] = {"id": kwargs["position_id"]}
        if "status" in kwargs:
            payload["status"] = kwargs["status"]

        return self._put(f"/v1/calendar/{shift_id}", json_data=payload)

    def delete_shift(self, shift_id):
        """Delete a shift.

        Args:
            shift_id: Sling shift ID

        Returns:
            int: HTTP status code (204 on success).
        """
        return self._delete(f"/v1/calendar/{shift_id}")

    def publish_shifts(self, start_date, end_date):
        """Publish all draft shifts in a date range.

        Args:
            start_date: Start date (str or date)
            end_date: End date (str or date)

        Returns:
            Response from Sling.
        """
        if hasattr(start_date, "strftime"):
            start_date = start_date.strftime("%Y-%m-%d")
        if hasattr(end_date, "strftime"):
            end_date = end_date.strftime("%Y-%m-%d")

        return self._post(f"/v1/calendar/{start_date}/{end_date}/publish")
