# processors/translation/context_store.py
from __future__ import annotations
import json
import os
from typing import Dict, Any

class ContextStore:
    """
    JSON-backed context memory for translations.
    Structure:
    {
      "_global": {...},
      "One Piece": {
         "_series": {...},
         "ch_001": {...},
         "ch_002": {...}
      },
      "Naruto": { ... }
    }
    """
    def __init__(self, path: str):
        self.path = path
        self._ctx: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self._ctx = json.load(f)
        else:
            self._ctx = {"_global": {}}
            self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._ctx, f, ensure_ascii=False, indent=2)

    def get(self, manga: str | None, chapter: str | None) -> Dict[str, Any]:
        """
        Return a merged view: global, series, chapter (later wins).
        """
        result: Dict[str, Any] = {}
        # global
        result.update(self._ctx.get("_global", {}))
        if manga:
            series_blob = self._ctx.get(manga, {})
            result.update(series_blob.get("_series", {}))
            if chapter:
                result.update(series_blob.get(chapter, {}))
        return result

    def update(self, manga: str | None, chapter: str | None, data: Dict[str, Any]):
        """
        Merge keys into the chosen level. Use chapter if provided,
        else series, else global.
        """
        target: Dict[str, Any]
        if manga:
            if manga not in self._ctx:
                self._ctx[manga] = {}
            if chapter:
                if chapter not in self._ctx[manga]:
                    self._ctx[manga][chapter] = {}
                target = self._ctx[manga][chapter]
            else:
                if "_series" not in self._ctx[manga]:
                    self._ctx[manga]["_series"] = {}
                target = self._ctx[manga]["_series"]
        else:
            target = self._ctx["_global"]

        target.update(data)
        self._save()
