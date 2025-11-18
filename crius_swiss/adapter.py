"""
Swiss Ephemeris adapter implementation.

This module provides a Swiss Ephemeris adapter that conforms to the
crius-ephemeris-core EphemerisAdapter protocol.
"""

from datetime import datetime
from typing import Optional
import swisseph as swe
import pytz

from crius_ephemeris_core import (
    EphemerisSettings,
    GeoLocation,
    PlanetPosition,
    HousePositions,
    LayerPositions,
    EphemerisAdapter,
)

# Swiss Ephemeris planet IDs
SWEPH_PLANET_IDS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO,
    "chiron": swe.CHIRON,
    "north_node": swe.TRUE_NODE,
}

# House system mapping
HOUSE_SYSTEM_MAP = {
    "placidus": b"P",
    "whole_sign": b"W",
    "koch": b"K",
    "equal": b"E",
    "regiomontanus": b"R",
    "campanus": b"C",
    "alcabitius": b"A",
    "morinus": b"M",
}

# Common ayanamsa mappings for Swiss Ephemeris
DEFAULT_AYANAMSA = swe.SIDM_LAHIRI
AYANAMSA_MAP = {
    "lahiri": swe.SIDM_LAHIRI,
    "chitrapaksha": swe.SIDM_LAHIRI,
    "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
    "de_luce": swe.SIDM_DELUCE,
    "raman": swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "yukteshwar": swe.SIDM_YUKTESHWAR,
    "djwhal_khul": swe.SIDM_DJWHAL_KHUL,
    "true_citra": swe.SIDM_TRUE_CITRA,
    "true_revati": swe.SIDM_TRUE_REVATI,
    "aryabhata": swe.SIDM_ARYABHATA,
    "aryabhata_mean_sun": swe.SIDM_ARYABHATA_MSUN,
}

# Sign names
SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]


def _get_sign(longitude: float) -> str:
    """Get sign name from longitude (0-360)."""
    normalized = longitude % 360
    if normalized == 360:
        normalized = 0
    sign_index = int(normalized / 30)
    sign_index = min(max(0, sign_index), 11)
    return SIGNS[sign_index]


def _datetime_to_jd(dt_utc: datetime) -> float:
    """Convert UTC datetime to Julian Day."""
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
        swe.GREG_CAL
    )


def _get_house_system_bytes(house_system: str) -> bytes:
    """Convert house system string to bytes format."""
    return HOUSE_SYSTEM_MAP.get(house_system.lower(), b'P')  # Default to Placidus


class SwissEphemerisAdapter:
    """
    Swiss Ephemeris adapter implementation.
    
    Thin wrapper around Swiss Ephemeris library calls that conforms to
    the EphemerisAdapter protocol from crius-ephemeris-core.
    """
    
    def __init__(self, ephemeris_path: Optional[str] = None):
        """
        Initialize adapter with optional ephemeris path.
        
        Args:
            ephemeris_path: Path to Swiss Ephemeris data files.
                           If None, uses default /usr/local/share/swisseph
                           or SWISS_EPHEMERIS_PATH environment variable.
        """
        if ephemeris_path is None:
            import os

            ephemeris_path = os.getenv("SWISS_EPHEMERIS_PATH", "/usr/local/share/swisseph")
        swe.set_ephe_path(ephemeris_path)
        self.ephemeris_path = ephemeris_path
        self._current_sidereal_mode: Optional[int] = None

    def calc_positions(
        self,
        dt_utc: datetime,
        location: Optional[GeoLocation],
        settings: EphemerisSettings,
    ) -> LayerPositions:
        """
        Calculate planetary and house positions using Swiss Ephemeris.
        
        Direct calls to Swiss Ephemeris library. No caching, no DB.
        
        Args:
            dt_utc: UTC datetime for calculation
            location: Optional geographic location (required for houses)
            settings: Ephemeris calculation settings
            
        Returns:
            LayerPositions with planetary positions and optionally house positions
        """
        jd = _datetime_to_jd(dt_utc)
        house_system_bytes = _get_house_system_bytes(settings["house_system"])
        flags = self._configure_flags(settings)

        # Calculate planets
        planets: dict[str, PlanetPosition] = {}
        include_objects = settings.get("include_objects", [])

        for obj_id in include_objects:
            obj_id_lower = obj_id.lower()

            # Handle special cases
            if obj_id_lower == "south_node":
                # South Node is 180 degrees from North Node
                north_node_pos = self._calc_planet_position("north_node", jd, flags)
                if north_node_pos:
                    south_lon = (north_node_pos["lon"] + 180) % 360
                    planets["south_node"] = {
                        "lon": south_lon,
                        "lat": 0.0,
                        "speed_lon": north_node_pos["speed_lon"],
                        "retrograde": north_node_pos["retrograde"],
                    }
                continue

            if obj_id_lower not in SWEPH_PLANET_IDS:
                continue

            planet_pos = self._calc_planet_position(obj_id_lower, jd, flags)
            if planet_pos:
                planets[obj_id_lower] = planet_pos

        # Calculate houses if location is provided
        houses: Optional[HousePositions] = None
        if location:
            houses = self._calc_houses(
                jd,
                location["lat"],
                location["lon"],
                house_system_bytes,
                settings["house_system"],
                flags,
            )

        return {
            "planets": planets,
            "houses": houses,
        }

    def _calc_planet_position(self, planet_id: str, jd: float, flags: int) -> Optional[PlanetPosition]:
        """Calculate position for a single planet."""
        if planet_id not in SWEPH_PLANET_IDS:
            return None

        try:
            result = swe.calc_ut(jd, SWEPH_PLANET_IDS[planet_id], flags)
            if result and len(result) > 0:
                positions = result[0]
                longitude = positions[0] % 360
                latitude = positions[1] if len(positions) > 1 else 0.0
                speed_longitude = positions[3] if len(positions) > 3 else 0.0
                is_retrograde = speed_longitude < 0

                return {
                    "lon": longitude,
                    "lat": latitude,
                    "speed_lon": speed_longitude,
                    "retrograde": is_retrograde,
                }
        except Exception as e:
            # Log error but don't fail the entire calculation
            # In a package context, we might want to use a logger if available
            # For now, we'll just return None
            pass
        return None

    def _calc_houses(
        self,
        jd: float,
        lat: float,
        lon: float,
        house_system_bytes: bytes,
        house_system_str: str,
        flags: int,
    ) -> HousePositions:
        """Calculate house cusps and angles."""
        result = swe.houses_ex2(jd, lat, lon, house_system_bytes, flags)

        if not result or len(result) == 0:
            return {
                "system": house_system_str,
                "cusps": {},
                "angles": {},
            }

        cusps = result[0]
        ascmc = result[1]

        # Extract house cusps
        cusps_dict: dict[str, float] = {}
        
        if len(cusps) == 12:
            # Whole Sign: cusps are indices 0-11 for houses 1-12
            for i in range(12):
                cusps_dict[str(i + 1)] = cusps[i] % 360
        else:
            # Placidus or other: indices 1-12 are houses 1-12
            for i in range(1, 13):
                if i < len(cusps):
                    cusps_dict[str(i)] = cusps[i] % 360

        # Extract angles
        asc = ascmc[0] % 360 if len(ascmc) > 0 else 0.0
        mc = ascmc[1] % 360 if len(ascmc) > 1 else 0.0
        ic = (mc + 180) % 360
        dc = (asc + 180) % 360

        return {
            "system": house_system_str,
            "cusps": cusps_dict,
            "angles": {
                "asc": asc,
                "mc": mc,
                "ic": ic,
                "dc": dc,
            },
        }

    def _configure_flags(self, settings: EphemerisSettings) -> int:
        """Prepare Swiss Ephemeris flags for the requested zodiac."""
        flags = swe.FLG_SWIEPH
        zodiac_type = settings.get("zodiac_type", "tropical")

        if zodiac_type == "sidereal":
            mode = self._resolve_ayanamsa(settings.get("ayanamsa"))
            self._ensure_sidereal_mode(mode)
            flags |= swe.FLG_SIDEREAL

        return flags

    def _resolve_ayanamsa(self, ayanamsa: Optional[str]) -> int:
        """Map ayanamsa string to Swiss constant."""
        if not ayanamsa:
            return DEFAULT_AYANAMSA
        return AYANAMSA_MAP.get(ayanamsa.lower(), DEFAULT_AYANAMSA)

    def _ensure_sidereal_mode(self, mode: int) -> None:
        """Cache sidereal mode configuration to avoid redundant calls."""
        if self._current_sidereal_mode == mode:
            return
        swe.set_sid_mode(mode, 0, 0)
        self._current_sidereal_mode = mode

