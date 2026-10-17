"""Shared helpers for cleanup passes."""

from __future__ import annotations


def is_empty(value: str) -> bool:
    return value.strip() == ""


def normalize(value: str) -> str:
    """Normalize for equality checks: strip whitespace; empty stays empty."""
    stripped = value.strip()
    return stripped
