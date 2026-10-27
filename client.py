"""Minimal Equiply Round 2 API client."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("EQUIPLY_BASE_URL", "https://equiply.io/api/v2").rstrip("/")


class ApiError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


def _request(method, path, auth=True, **kwargs):
    headers = kwargs.pop("headers", {})
    if auth:
        key = os.getenv("EQUIPLY_API_KEY")
        if not key:
            raise RuntimeError("EQUIPLY_API_KEY not set (set .env)")
        headers["API-KEY"] = key
    resp = requests.request(method, f"{BASE_URL}/{path.lstrip('/')}",
                            headers=headers, timeout=30, **kwargs)
    try:
        body = resp.json()
    except ValueError:
        body = resp.text
    if not resp.ok:
        raise ApiError(resp.status_code, body)
    return body


def get(path, **params):
    return _request("GET", path, params=params)


def post(path, payload=None, auth=True):
    return _request("POST", path, auth=auth, json=payload)
