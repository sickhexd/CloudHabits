"""
Module for Telegram Mini Apps authentication
"""

from fastapi import Request, HTTPException, Query
from typing import Optional
import urllib.parse
import hmac
import hashlib
import time
import json
import os


def get_user_id_from_query(request: Request) -> str:
    """
    Gets user_id from query parameters.
    Telegram Mini Apps pass user_id via ?user_id=... parameter
    """
    user_id = request.query_params.get("user_id")
    if not user_id:
        # For development, test ID can be used
        # In production this should be required
        raise HTTPException(
            status_code=401, detail="user_id is required. Please provide ?user_id=... in URL"
        )
    return user_id


def get_user_id_dependency(
    request: Request, user_id: Optional[str] = Query(None, description="Telegram user ID")
):
    """
    Dependency to get user_id from query parameters or Telegram initData.
    Used in FastAPI Depends().

    Tries to extract user_id from:
    1. Query parameter ?user_id=...
    2. Telegram initData in query (?tgWebAppData=...)
    3. Development mode (ALLOW_DEFAULT_USER=true)
    """

    if user_id:
        return user_id

    init_data = request.query_params.get("tgWebAppData")
    if init_data:
        try:
            # Parse Telegram initData
            parsed = urllib.parse.parse_qs(init_data)
            if "user" in parsed:
                user_json = json.loads(parsed["user"][0])
                if "id" in user_json:
                    return str(user_json["id"])
        except Exception:
            pass

    allow_default = os.getenv("ALLOW_DEFAULT_USER", "false").lower() == "true"
    if allow_default:
        return "default_user"

    raise HTTPException(status_code=401, detail="user_id parameter is required")


def validate_telegram_init_data(init_data: str, bot_token: str) -> Optional[dict]:
    try:
        parsed_data = urllib.parse.parse_qs(init_data)
        if "user" not in parsed_data:
            return None

        return None  # TODO:
    except Exception:
        return None
