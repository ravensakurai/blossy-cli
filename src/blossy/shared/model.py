"""Shared models for Blossy."""

from datetime import date, datetime, time
from typing import Any

TomlValue = str | int | float | bool | datetime | date | time | list[Any]

SUPPORTED_CONFIG_TYPES = frozenset({str, int, float, bool, datetime, date, time, list})
