import hashlib
import hmac
import json
import sys
from dataclasses import asdict, dataclass

import requests

KEY = "hg2026_python_engineer@!"
ENDPOINT = "https://howgood-apply-api.howgood.workers.dev/apply"
SUCCESS_STATUS_CODES = {200, 201}


@dataclass(frozen=True)
class ApplicationPayload:
    name: str
    email: str
    resume: str
    location: str
    linkedin: str
    codeLink: str
    yearsPython: int = 0
    yearsDjango: int = 0
    repos: str = ""
    notes: str = ""


payload = ApplicationPayload(
    name="Khanh Theresa Mai",
    email="khanhmai@creighton.edu",
    resume="https://drive.google.com/file/d/1NY9vSyJIdWZPVS2PaIQQpF-4qiU6EH7D/view?usp=sharing",
    location="Corpus Christi, Texas, USA",
    linkedin="https://www.linkedin.com/in/astropharmacist/",
    codeLink="https://github.com/khanderz/how-good-repo",
    yearsPython=5,
    yearsDjango=4,
    repos="https://github.com/khanderz",
    notes=(
        "Clinical pharmacist turned fullstack software engineer with experience "
        "building healthcare and product-focused systems across Python, Django, "
        "TypeScript, React, and React Native."
    ),
)


def build_raw_json(payload_data: ApplicationPayload) -> str:
    """
    Serialize the payload into a stable JSON string for signing and submission.
    Compact separators avoid signature mismatches caused by extra whitespace.
    """
    return json.dumps(asdict(payload_data), separators=(",", ":"), ensure_ascii=False)


def sign_body(raw_body: str, secret: str) -> str:
    """
    Return the hex-encoded HMAC-SHA256 signature for the raw request body.
    """
    return hmac.new(
        secret.encode("utf-8"),
        raw_body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def validate_payload(payload_data: ApplicationPayload) -> None:
    """
    Validate required string fields before submitting.
    """
    required_fields = ("name", "email", "resume", "location", "linkedin", "codeLink")
    missing_fields = [
        field_name
        for field_name in required_fields
        if not str(getattr(payload_data, field_name)).strip()
    ]

    if missing_fields:
        raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}")

    if payload_data.yearsPython < 0 or payload_data.yearsDjango < 0:
        raise ValueError("Years of experience cannot be negative.")


def submit_application(payload_data: ApplicationPayload) -> requests.Response:
    """
    Validate, sign, and submit the application payload.
    """
    validate_payload(payload_data)

    raw_body = build_raw_json(payload_data)
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
        response.raise_for_status()
    except ValueError as exc:
        print(f"Payload error: {exc}", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        try:
            print(json.dumps(exc.response.json(), indent=2), file=sys.stderr)
        except ValueError:
            print(exc.response.text, file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Status: {response.status_code}")

    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print("Response text:")
        print(response.text)

    if response.status_code not in SUCCESS_STATUS_CODES:
        sys.exit(1)


if __name__ == "__main__":
    main()