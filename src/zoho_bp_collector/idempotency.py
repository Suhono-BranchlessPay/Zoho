"""Idempotent anchor — skip duplicate Zoho resource + event pairs."""

import json
import os
from typing import Any


class AnchorIdempotencyStore:
    def __init__(self, directory: str | None = None):
        if directory is None:
            directory = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "data",
                "anchor_cache",
            )
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def _path(self, key: str) -> str:
        safe = key.replace(":", "_").replace("/", "_")
        return os.path.join(self.directory, "%s.json" % safe)

    @staticmethod
    def make_key(organization_id: str, event_type: str, resource_id: str) -> str:
        return "%s:%s:%s" % (organization_id, event_type, resource_id)

    def get(self, key: str) -> dict[str, Any] | None:
        path = self._path(key)
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, key: str, record: dict[str, Any]) -> None:
        path = self._path(key)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2, ensure_ascii=False)
