import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


def json_default(value: object) -> Any:
    """Convert supported non-JSON values into JSON-compatible values."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def dumps(value: object) -> str:
    return json.dumps(value, default=json_default, separators=(",", ":"))
