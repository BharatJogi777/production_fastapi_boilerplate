from datetime import datetime
import pytest
from app.shared.pagination.schemas import Page, PaginationParams
from app.utils.datetime import ensure_utc, utc_now
from app.utils.identifiers import is_valid_uuid
from app.utils.strings import normalize_whitespace, slugify

def test_pagination_offset_and_metadata():
    params = PaginationParams(page=3, page_size=10)
    assert params.offset == 20
    page = Page[int].build([1, 2], page=1, page_size=10, total_items=21)
    assert page.metadata.total_pages == 3

def test_pagination_rejects_unbounded_page_size():
    with pytest.raises(ValueError):
        PaginationParams(page_size=1000)

def test_datetime_is_timezone_aware():
    assert utc_now().utcoffset().total_seconds() == 0
    with pytest.raises(ValueError):
        ensure_utc(datetime(2026, 1, 1))

def test_string_and_uuid_helpers():
    assert normalize_whitespace("  a  b \n c ") == "a b c"
    assert slugify("Hello, World!") == "hello-world"
    assert is_valid_uuid("a3bb189e-8bf9-3888-9912-ace4e6543002")
    assert not is_valid_uuid("not-a-uuid")
