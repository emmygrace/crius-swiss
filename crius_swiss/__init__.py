"""
Crius Swiss - Swiss Ephemeris adapter implementation.

Named after Crius, the Titan of constellations and measuring the year.
"""

from .adapter import SwissEphemerisAdapter
from .exceptions import (
    CriusSwissError,
    EphemerisFileNotFoundError,
    EphemerisCalculationError,
    InvalidHouseSystemError,
    InvalidAyanamsaError,
)
from .cache import EphemerisCache, CachedSwissEphemerisAdapter
from .validation import (
    validate_ephemeris_path,
    validate_ephemeris_files,
    check_file_integrity,
    find_ephemeris_files,
)

__all__ = [
    "SwissEphemerisAdapter",
    "CriusSwissError",
    "EphemerisFileNotFoundError",
    "EphemerisCalculationError",
    "InvalidHouseSystemError",
    "InvalidAyanamsaError",
    "EphemerisCache",
    "CachedSwissEphemerisAdapter",
    "validate_ephemeris_path",
    "validate_ephemeris_files",
    "check_file_integrity",
    "find_ephemeris_files",
]

__version__ = "0.1.0"

