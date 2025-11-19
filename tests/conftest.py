"""Shared fixtures for crius-swiss tests."""

import pytest
import os
from datetime import datetime, timezone
from pathlib import Path

from crius_ephemeris_core import EphemerisSettings, GeoLocation
from crius_swiss import SwissEphemerisAdapter


@pytest.fixture
def sample_settings() -> EphemerisSettings:
    """Sample ephemeris settings for testing."""
    return {
        "zodiac_type": "tropical",
        "ayanamsa": None,
        "house_system": "placidus",
        "include_objects": ["sun", "moon", "mercury", "venus", "mars"],
    }


@pytest.fixture
def sample_location() -> GeoLocation:
    """Sample geographic location (New York)."""
    return {
        "lat": 40.7128,
        "lon": -74.0060,
    }


@pytest.fixture
def sample_datetime() -> datetime:
    """Sample datetime for testing."""
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def ephemeris_path(monkeypatch, tmp_path):
    """Fixture for ephemeris path configuration."""
    # Try to use environment variable or default
    default_path = os.getenv("SWISS_EPHEMERIS_PATH", "/usr/local/share/swisseph")
    
    # If default path exists, use it; otherwise use tmp_path
    if os.path.exists(default_path):
        return default_path
    
    # Create a temporary directory structure
    test_path = tmp_path / "swisseph"
    test_path.mkdir(parents=True, exist_ok=True)
    
    # Set environment variable for tests
    monkeypatch.setenv("SWISS_EPHEMERIS_PATH", str(test_path))
    
    return str(test_path)


@pytest.fixture
def adapter(ephemeris_path):
    """Create adapter instance for testing."""
    # Note: This will fail if Swiss Ephemeris files are not available
    # Tests should be marked appropriately
    try:
        return SwissEphemerisAdapter(ephemeris_path=ephemeris_path)
    except Exception:
        # If adapter creation fails, return None and let tests handle it
        pytest.skip("Swiss Ephemeris files not available")


@pytest.fixture
def adapter_with_default_path():
    """Create adapter with default path."""
    try:
        return SwissEphemerisAdapter()
    except Exception:
        pytest.skip("Swiss Ephemeris files not available")


@pytest.fixture
def all_planets_settings() -> EphemerisSettings:
    """Settings including all supported planets."""
    return {
        "zodiac_type": "tropical",
        "ayanamsa": None,
        "house_system": "placidus",
        "include_objects": [
            "sun",
            "moon",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "uranus",
            "neptune",
            "pluto",
            "chiron",
            "north_node",
            "south_node",
        ],
    }


@pytest.fixture
def sidereal_settings() -> EphemerisSettings:
    """Settings for sidereal zodiac."""
    return {
        "zodiac_type": "sidereal",
        "ayanamsa": "lahiri",
        "house_system": "placidus",
        "include_objects": ["sun", "moon"],
    }

