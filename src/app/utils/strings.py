import re
import unicodedata

_WHITESPACE = re.compile(r"\s+")

def normalize_whitespace(value: str) -> str:
    return _WHITESPACE.sub(" ", value).strip()

def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
