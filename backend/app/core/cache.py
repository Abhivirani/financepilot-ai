"""
Cache Interface — future AI response caching.

Responsibilities:
  1. Provide a key-value cache interface for storing LLM responses.
  2. Allow cache invalidation when underlying data changes
     (e.g. after a new reconciliation run).
  3. Support TTL-based expiry for stale responses.

This module defines the abstract interface only. Concrete implementations
(in-memory, Redis, SQLite) will be added when the AI Copilot is activated.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class CacheEntry:
    """A single cached value with metadata."""

    key: str
    value: Any
    ttl_seconds: int
    created_at: float  # epoch timestamp


class CacheBackend(ABC):
    """Abstract cache backend interface."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached value by key.  Returns None on miss."""
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Store a value with the given TTL."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove a single entry."""
        ...

    @abstractmethod
    async def invalidate_prefix(self, prefix: str) -> int:
        """Remove all entries whose key starts with ``prefix``.  Returns count deleted."""
        ...

    @abstractmethod
    async def clear(self) -> None:
        """Flush the entire cache."""
        ...


class InMemoryCache(CacheBackend):
    """
    Simple in-memory dict-based cache.

    Suitable for single-process deployments and development.
    Will be replaced with Redis for production if needed.
    """

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    async def get(self, key: str) -> Optional[Any]:
        import time

        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() - entry.created_at > entry.ttl_seconds:
            del self._store[key]
            return None
        return entry.value

    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        import time

        self._store[key] = CacheEntry(
            key=key, value=value, ttl_seconds=ttl_seconds, created_at=time.time()
        )

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def invalidate_prefix(self, prefix: str) -> int:
        keys = [k for k in self._store if k.startswith(prefix)]
        for k in keys:
            del self._store[k]
        return len(keys)

    async def clear(self) -> None:
        self._store.clear()
