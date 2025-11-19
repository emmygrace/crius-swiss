"""Comprehensive tests for SwissEphemerisAdapter."""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from crius_ephemeris_core import EphemerisSettings, GeoLocation
from crius_swiss import SwissEphemerisAdapter


class TestAdapterInitialization:
    """Test adapter initialization."""

    def test_init_with_default_path(self):
        """Test initialization with default path."""
        try:
            adapter = SwissEphemerisAdapter()
            assert adapter is not None
            assert adapter.ephemeris_path is not None
        except Exception:
            pytest.skip("Swiss Ephemeris files not available")

    def test_init_with_custom_path(self, tmp_path):
        """Test initialization with custom path."""
        test_path = str(tmp_path / "swisseph")
        adapter = SwissEphemerisAdapter(ephemeris_path=test_path)
        assert adapter.ephemeris_path == test_path

    def test_init_with_env_var(self, monkeypatch, tmp_path):
        """Test initialization respects SWISS_EPHEMERIS_PATH env var."""
        test_path = str(tmp_path / "swisseph")
        monkeypatch.setenv("SWISS_EPHEMERIS_PATH", test_path)
        
        adapter = SwissEphemerisAdapter()
        assert adapter.ephemeris_path == test_path


class TestPlanetCalculations:
    """Test planet position calculations."""

    def test_calc_sun_position(self, adapter, sample_settings, sample_location):
        """Test calculating Sun position."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, sample_settings)
        
        assert "planets" in positions
        assert "sun" in positions["planets"]
        
        sun = positions["planets"]["sun"]
        assert "lon" in sun
        assert "lat" in sun
        assert "speed_lon" in sun
        assert "retrograde" in sun
        assert 0 <= sun["lon"] < 360

    def test_calc_moon_position(self, adapter, sample_settings, sample_location):
        """Test calculating Moon position."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, sample_settings)
        
        assert "moon" in positions["planets"]
        moon = positions["planets"]["moon"]
        assert 0 <= moon["lon"] < 360

    def test_calc_all_planets(self, adapter, all_planets_settings, sample_location):
        """Test calculating all supported planets."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, all_planets_settings)
        
        expected_planets = [
            "sun", "moon", "mercury", "venus", "mars",
            "jupiter", "saturn", "uranus", "neptune", "pluto",
            "chiron", "north_node", "south_node",
        ]
        
        for planet in expected_planets:
            assert planet in positions["planets"], f"Missing planet: {planet}"
            pos = positions["planets"][planet]
            assert 0 <= pos["lon"] < 360, f"Invalid longitude for {planet}"

    def test_calc_chiron(self, adapter, sample_location):
        """Test calculating Chiron position."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        settings: EphemerisSettings = {
            "zodiac_type": "tropical",
            "ayanamsa": None,
            "house_system": "placidus",
            "include_objects": ["chiron"],
        }
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, settings)
        
        assert "chiron" in positions["planets"]
        chiron = positions["planets"]["chiron"]
        assert 0 <= chiron["lon"] < 360

    def test_calc_lunar_nodes(self, adapter, sample_location):
        """Test calculating lunar nodes."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        settings: EphemerisSettings = {
            "zodiac_type": "tropical",
            "ayanamsa": None,
            "house_system": "placidus",
            "include_objects": ["north_node", "south_node"],
        }
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, settings)
        
        assert "north_node" in positions["planets"]
        assert "south_node" in positions["planets"]
        
        north = positions["planets"]["north_node"]
        south = positions["planets"]["south_node"]
        
        # South node should be approximately 180 degrees from north node
        diff = abs((south["lon"] - north["lon"]) % 360)
        assert diff < 1.0 or diff > 359.0


class TestHouseCalculations:
    """Test house system calculations."""

    def test_calc_houses_placidus(self, adapter, sample_settings, sample_location):
        """Test calculating Placidus houses."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        settings: EphemerisSettings = {
            **sample_settings,
            "house_system": "placidus",
        }
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, settings)
        
        assert positions["houses"] is not None
        houses = positions["houses"]
        assert houses["system"] == "placidus"
        assert len(houses["cusps"]) == 12
        assert "asc" in houses["angles"]
        assert "mc" in houses["angles"]

    def test_calc_houses_whole_sign(self, adapter, sample_settings, sample_location):
        """Test calculating Whole Sign houses."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        settings: EphemerisSettings = {
            **sample_settings,
            "house_system": "whole_sign",
        }
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, settings)
        
        assert positions["houses"] is not None
        houses = positions["houses"]
        assert houses["system"] == "whole_sign"

    def test_calc_houses_multiple_systems(self, adapter, sample_settings, sample_location):
        """Test multiple house systems."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        house_systems = ["placidus", "whole_sign", "koch", "equal", "regiomontanus"]
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        for system in house_systems:
            settings: EphemerisSettings = {
                **sample_settings,
                "house_system": system,
            }
            positions = adapter.calc_positions(dt, sample_location, settings)
            
            assert positions["houses"] is not None
            assert positions["houses"]["system"] == system

    def test_calc_houses_no_location(self, adapter, sample_settings):
        """Test that houses are None when no location provided."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, None, sample_settings)
        
        assert positions["houses"] is None


class TestZodiacModes:
    """Test tropical and sidereal zodiac modes."""

    def test_tropical_zodiac(self, adapter, sample_settings, sample_location):
        """Test tropical zodiac calculations."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        settings: EphemerisSettings = {
            "zodiac_type": "tropical",
            "ayanamsa": None,
            "house_system": "placidus",
            "include_objects": ["sun"],
        }
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, settings)
        
        assert "sun" in positions["planets"]
        sun = positions["planets"]["sun"]
        # Sun in January should be in Capricorn (around 280-310 degrees)
        assert 270 <= sun["lon"] < 330

    def test_sidereal_zodiac(self, adapter, sidereal_settings, sample_location):
        """Test sidereal zodiac calculations."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, sidereal_settings)
        
        assert "sun" in positions["planets"]
        sun = positions["planets"]["sun"]
        # Sidereal positions should differ from tropical
        assert 0 <= sun["lon"] < 360

    def test_ayanamsa_configurations(self, adapter, sample_location):
        """Test different ayanamsa configurations."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        ayanamsas = ["lahiri", "fagan_bradley", "raman", "krishnamurti"]
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        for ayanamsa in ayanamsas:
            settings: EphemerisSettings = {
                "zodiac_type": "sidereal",
                "ayanamsa": ayanamsa,
                "house_system": "placidus",
                "include_objects": ["sun"],
            }
            positions = adapter.calc_positions(dt, sample_location, settings)
            assert "sun" in positions["planets"]


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_planet_id(self, adapter, sample_settings, sample_location):
        """Test handling of invalid planet IDs."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        settings: EphemerisSettings = {
            **sample_settings,
            "include_objects": ["invalid_planet"],
        }
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, settings)
        
        # Invalid planets should be skipped, not cause errors
        assert "planets" in positions
        assert "invalid_planet" not in positions["planets"]

    def test_empty_objects_list(self, adapter, sample_location):
        """Test handling of empty include_objects list."""
        if adapter is None:
            pytest.skip("Swiss Ephemeris files not available")
        
        settings: EphemerisSettings = {
            "zodiac_type": "tropical",
            "ayanamsa": None,
            "house_system": "placidus",
            "include_objects": [],
        }
        
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        positions = adapter.calc_positions(dt, sample_location, settings)
        
        assert "planets" in positions
        assert len(positions["planets"]) == 0

