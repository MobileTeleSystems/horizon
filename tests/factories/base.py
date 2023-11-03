from __future__ import annotations

import secrets
from datetime import datetime, timezone
from random import randrange


def random_string(length: int = 16) -> str:
    return secrets.token_hex(length // 2)


def random_datetime(
    start: datetime | None = None,
    end: datetime | None = None,
) -> datetime:
    if not start:
        start = datetime.fromtimestamp(0, tz=timezone.utc)
    if not end:
        end = datetime.now(tz=timezone.utc)
    return datetime.fromtimestamp(randrange(int(start.timestamp()), int(end.timestamp())), tz=start.tzinfo)
