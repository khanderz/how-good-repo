import hashlib
import hmac
import json
import sys
from typing import Any

import requests

KEY = "hg2026_python_engineer@!"
ENDPOINT = "https://howgood-apply-api.howgood.workers.dev/apply"

payload: dict[str, Any] = {
    "name": "Khanh Theresa Mai",
    "email": "khanhmai@creighton.edu",
    "resume": "https://drive.google.com/file/d/1NY9vSyJIdWZPVS2PaIQQpF-4qiU6EH7D/view?usp=sharing",
    "location": "Corpus Christi, Texas, USA",
    "linkedin": "https://www.linkedin.com/in/astropharmacist/",
    "codeLink": "https://github.com/khanderz/how-good-repo",
    "yearsPython": 5,
    "yearsDjango": 4,
    "repos": "https://github.com/khanderz",
    "notes": (
        "Clinical pharmacist turned fullstack software engineer with experience "
        "building healthcare and product-focused systems across Python, Django, "
        "TypeScript, React, and React Native."
    ),
}


def build_raw_json(data: dict[str, Any]) -> str:
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def sign_body(raw_body: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        raw_body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def validate_payload(data: dict[str, Any]) -> None:
    required_fields = ["name", "email", "resume", "location", "linkedin", "codeLink"]
    missing = [field for field in required_fields if not str(data.get(field, "")).strip()]

    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")


def submit_application(data: dict[str, Any]) -> requests.Response:
    validate_payload(data)

    raw_body = build_raw_json(data)
    signature = sign_body(raw_body, KEY)

    headers = {
        "Content-Type": "application/json",
        "X-HMAC-Signature": signature,
    }

    return requests.post(
        ENDPOINT,
        data=raw_body,
        headers=headers,
        timeout=30,
    )


def main() -> None:
    try:
        response = submit_application(payload)
    except ValueError as exc:
        print(f"Payload error: {exc}")
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"Request failed: {exc}")
        sys.exit(1)

    print(f"Status: {response.status_code}")

    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print("Response text:")
        print(response.text)

    if response.status_code not in (200, 201):
        sys.exit(1)


if __name__ == "__main__":
    main()