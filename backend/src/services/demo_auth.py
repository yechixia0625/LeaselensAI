import base64
import hashlib
import hmac
import json
import time


class DemoAuthService:
    def __init__(
        self,
        username: str,
        password: str,
        secret: str,
        cookie_name: str,
        ttl_seconds: int = 60 * 60 * 12,
    ):
        self._username = username
        self._password = password
        self._secret = secret.encode("utf-8")
        self.cookie_name = cookie_name
        self._ttl_seconds = ttl_seconds

    def verify_credentials(self, username: str, password: str) -> bool:
        return hmac.compare_digest(username, self._username) and hmac.compare_digest(
            password, self._password
        )

    def issue_cookie_value(self) -> str:
        payload = {
            "username": self._username,
            "exp": int(time.time()) + self._ttl_seconds,
        }
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        body = base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")
        sig = hmac.new(
            self._secret, body.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return f"{body}.{sig}"

    def read_cookie_value(self, value: str | None) -> str | None:
        if not value or "." not in value:
            return None

        body, supplied_sig = value.rsplit(".", 1)
        expected_sig = hmac.new(
            self._secret, body.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(supplied_sig, expected_sig):
            return None

        try:
            padded = body + "=" * (-len(body) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded.encode("utf-8")))
        except (ValueError, json.JSONDecodeError):
            return None

        if payload.get("exp", 0) < int(time.time()):
            return None
        username = payload.get("username")
        if not isinstance(username, str) or not username:
            return None
        return username
