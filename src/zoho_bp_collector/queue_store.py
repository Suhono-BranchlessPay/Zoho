"""Persist failed BP posts for later replay."""

import json
import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class FailedQueue:
    def __init__(self, directory: str | None = None):
        if directory is None:
            directory = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "data",
                "failed_queue",
            )
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def save(self, payload: dict[str, Any], error: dict[str, Any]) -> str:
        record = {
            "id": str(uuid4()),
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
            "error": error,
        }
        path = os.path.join(self.directory, "%s.json" % record["id"])
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2, ensure_ascii=False)
        return path
