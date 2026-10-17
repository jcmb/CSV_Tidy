"""Remove ID/code columns when a matching display column exists."""

from __future__ import annotations

import re

from csv_tidy.cleanups._util import is_empty, normalize
from csv_tidy.report import RemovedColumn
from csv_tidy.table import Table

# More specific first: "{Prefix} User ID" pairs with column "{Prefix}"
_USER_ID_SUFFIX = re.compile(r"^(?P<prefix>.+?)\s+user\s+id$", re.IGNORECASE)
_ID_SUFFIX = re.compile(r"^(?P<prefix>.+?)\s+id$", re.IGNORECASE)
_CODE_SUFFIX = re.compile(r"^(?P<prefix>.+?)\s+code$", re.IGNORECASE)
_NUMBER_SUFFIX = re.compile(r"^(?P<prefix>.+?)\s+number$", re.IGNORECASE)
# Display / label sides (ID-like pairs use these as the kept column)
_NAME_SUFFIX = re.compile(r"^(?P<prefix>.+?)\s+name$", re.IGNORECASE)
_MEANING_SUFFIX = re.compile(r"^(?P<prefix>.+?)\s+meaning$", re.IGNORECASE)
_DESCRIPTION_SUFFIX = re.compile(
    r"^(?P<prefix>.+?)\s+description$", re.IGNORECASE
)
_DESC_SUFFIX = re.compile(r"^(?P<prefix>.+?)\s+desc$", re.IGNORECASE)

# Prefer longer/clearer labels first when resolving a display column.
_DISPLAY_SUFFIXES = (
    _MEANING_SUFFIX,
    _DESCRIPTION_SUFFIX,
    _DESC_SUFFIX,
    _NAME_SUFFIX,
)
_WHITESPACE = re.compile(r"\s+")
# Normalize common abbreviation variants so prefixes compare equal.
# Longer forms first. Example: "Ship From Org" == "Ship From Organization".
_PREFIX_SYNONYMS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\borganisations?\b"), "org"),
    (re.compile(r"\borganizations?\b"), "org"),
)


def _norm_header(header: str) -> str:
    """Collapse internal whitespace for reliable header matching."""
    return _WHITESPACE.sub(" ", header.strip())


def _prefix_key(prefix: str) -> str:
    key = _norm_header(prefix).casefold()
    for pattern, replacement in _PREFIX_SYNONYMS:
        key = pattern.sub(replacement, key)
    return key


def _find_paired_index(
    headers: list[str],
    prefix: str,
    pattern: re.Pattern[str],
) -> int | None:
    for i, header in enumerate(headers):
        match = pattern.match(_norm_header(header))
        if match and _prefix_key(match.group("prefix")) == prefix:
            return i
    return None


def _find_display_index(
    headers: list[str],
    prefix: str,
    headers_by_key: dict[str, int],
) -> int | None:
    """Find a display column for a coded ID / Code / Number column.

    Preference order:
    1. ``{Prefix} Meaning``
    2. ``{Prefix} Description``
    3. ``{Prefix} Desc``
    4. ``{Prefix} Name``
    5. bare ``{Prefix}`` (e.g. ``Invoice To Customer Number`` + ``Invoice To Customer``)
    """
    for pattern in _DISPLAY_SUFFIXES:
        idx = _find_paired_index(headers, prefix, pattern)
        if idx is not None:
            return idx
    return headers_by_key.get(prefix)


def _mapping_is_consistent(id_values: list[str], display_values: list[str]) -> bool:
    """Return True when each non-empty ID always maps to the same display value.

    Different IDs may share a display label (common in exports). At least one
    non-empty pair is required. Same ID with conflicting displays blocks removal.
    """
    id_to_display: dict[str, str] = {}
    saw_pair = False

    for raw_id, raw_display in zip(id_values, display_values, strict=True):
        id_n = normalize(raw_id)
        display_n = normalize(raw_display)
        if is_empty(id_n) or is_empty(display_n):
            continue
        saw_pair = True
        if id_n in id_to_display and id_to_display[id_n] != display_n:
            return False
        id_to_display[id_n] = display_n

    return saw_pair


def remove_id_columns(
    table: Table,
) -> tuple[Table, list[RemovedColumn], list[str]]:
    """Drop coded columns when a paired display column exists and matches.

    Coded columns (removed when each ID/code maps to one display value):
    - ``{Prefix} User ID`` paired with ``{Prefix}``
    - ``{Prefix} ID`` / ``{Prefix} Code`` / ``{Prefix} Number`` paired with
      ``{Prefix} Meaning``, ``{Prefix} Description``, ``{Prefix} Desc``,
      ``{Prefix} Name``, or bare ``{Prefix}``
      (e.g. ``Invoice To Customer Number`` + ``Invoice To Customer``)

    Prefix matching treats ``Org`` / ``Organization`` (and ``Organisation``) as
    the same token, e.g. ``Ship From Org ID`` + ``Ship From Organization Name``.
    """
    headers_by_key: dict[str, int] = {}
    for i, header in enumerate(table.headers):
        headers_by_key.setdefault(_prefix_key(header), i)

    drop: set[int] = set()
    removed: list[RemovedColumn] = []
    notes: list[str] = []

    def _try_mark(id_index: int, display_index: int) -> bool:
        if id_index == display_index:
            return False
        id_name = table.headers[id_index]
        display_name = table.headers[display_index]
        if not _mapping_is_consistent(
            table.columns[id_index],
            table.columns[display_index],
        ):
            notes.append(
                f"Kept {id_name} (inconsistent mapping with {display_name})"
            )
            return False
        drop.add(id_index)
        removed.append(
            RemovedColumn(
                name=id_name,
                reason=f"paired with {display_name}",
                index=id_index,
            )
        )
        return True

    for i, header in enumerate(table.headers):
        if i in drop:
            continue
        stripped = _norm_header(header)

        user_id_match = _USER_ID_SUFFIX.match(stripped)
        if user_id_match:
            prefix = _prefix_key(user_id_match.group("prefix"))
            paired_idx = headers_by_key.get(prefix)
            if paired_idx is not None and _try_mark(i, paired_idx):
                continue
            # Bare "{Prefix}" present but mapping inconsistent — stop.
            if paired_idx is not None:
                continue
            # No bare "{Prefix}" — fall through to ID + Meaning/Name
            # (e.g. "Foo User ID" + "Foo User Name").

        for coded_pattern in (_ID_SUFFIX, _CODE_SUFFIX, _NUMBER_SUFFIX):
            coded_match = coded_pattern.match(stripped)
            if not coded_match:
                continue
            prefix = _prefix_key(coded_match.group("prefix"))
            paired_idx = _find_display_index(
                table.headers, prefix, headers_by_key
            )
            if paired_idx is not None:
                _try_mark(i, paired_idx)
            break

    return table.drop_indices(drop), removed, notes
