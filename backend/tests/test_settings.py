import pytest
from pydantic import ValidationError

from app.settings import Settings


def test_missing_database_url_fails_clearly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)  # pyright: ignore[reportCallIssue]

    assert "database_url" in str(exc_info.value)
