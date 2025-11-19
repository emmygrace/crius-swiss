"""
Caching layer for Swiss Ephemeris calculations.

Provides LRU cache implementation for caching planet positions and house calculations.
"""

from typing import Optional, Dict, Tuple, Any
from functools import lru_cache
from datetime import datetime

from crius_ephemeris_core import LayerPositions, EphemerisSettings, GeoLocation


class EphemerisCache:
    """
    LRU cache for ephemeris calculations.

    Caches planet positions and house calculations to improve performance
    for repeated calculations.
    """

    def __init__(self, maxsize: int = 128):
        """
        Initialize cache.

        Args:
            maxsize: Maximum number of cached entries (default: 128)
        """
        self.maxsize = maxsize
        self._planet_cache: Dict[Tuple[float, str, int], Dict[str, Any]] = {}
        self._house_cache: Dict[Tuple[float, float, float, bytes, int], Dict[str, Any]] = {}
        self._hits = 0
        self._misses = 0

    def _get_planet_key(self, jd: float, planet_id: str, flags: int) -> Tuple[float, str, int]:
        """Generate cache key for planet position."""
        # Round JD to nearest minute for caching (reduces cache size)
        jd_rounded = round(jd * 1440) / 1440  # Round to nearest minute
        return (jd_rounded, planet_id, flags)

    def _get_house_key(
        self, jd: float, lat: float, lon: float, house_system_bytes: bytes, flags: int
    ) -> Tuple[float, float, float, bytes, int]:
        """Generate cache key for house calculation."""
        # Round JD to nearest minute
        jd_rounded = round(jd * 1440) / 1440
        # Round coordinates to 4 decimal places (about 11 meters precision)
        lat_rounded = round(lat * 10000) / 10000
        lon_rounded = round(lon * 10000) / 10000
        return (jd_rounded, lat_rounded, lon_rounded, house_system_bytes, flags)

    def get_planet_position(
        self, jd: float, planet_id: str, flags: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached planet position.

        Args:
            jd: Julian Day
            planet_id: Planet ID
            flags: Calculation flags

        Returns:
            Cached position or None if not found
        """
        key = self._get_planet_key(jd, planet_id, flags)
        if key in self._planet_cache:
            self._hits += 1
            return self._planet_cache[key]
        self._misses += 1
        return None

    def set_planet_position(
        self, jd: float, planet_id: str, flags: int, position: Dict[str, Any]
    ) -> None:
        """
        Cache planet position.

        Args:
            jd: Julian Day
            planet_id: Planet ID
            flags: Calculation flags
            position: Planet position to cache
        """
        key = self._get_planet_key(jd, planet_id, flags)
        
        # Evict oldest entries if cache is full
        if len(self._planet_cache) >= self.maxsize:
            # Remove oldest entry (simple FIFO, could be improved with LRU)
            oldest_key = next(iter(self._planet_cache))
            del self._planet_cache[oldest_key]
        
        self._planet_cache[key] = position

    def get_house_positions(
        self, jd: float, lat: float, lon: float, house_system_bytes: bytes, flags: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached house positions.

        Args:
            jd: Julian Day
            lat: Latitude
            lon: Longitude
            house_system_bytes: House system bytes
            flags: Calculation flags

        Returns:
            Cached house positions or None if not found
        """
        key = self._get_house_key(jd, lat, lon, house_system_bytes, flags)
        if key in self._house_cache:
            self._hits += 1
            return self._house_cache[key]
        self._misses += 1
        return None

    def set_house_positions(
        self,
        jd: float,
        lat: float,
        lon: float,
        house_system_bytes: bytes,
        flags: int,
        houses: Dict[str, Any],
    ) -> None:
        """
        Cache house positions.

        Args:
            jd: Julian Day
            lat: Latitude
            lon: Longitude
            house_system_bytes: House system bytes
            flags: Calculation flags
            houses: House positions to cache
        """
        key = self._get_house_key(jd, lat, lon, house_system_bytes, flags)
        
        # Evict oldest entries if cache is full
        if len(self._house_cache) >= self.maxsize:
            oldest_key = next(iter(self._house_cache))
            del self._house_cache[oldest_key]
        
        self._house_cache[key] = houses

    def clear(self) -> None:
        """Clear all cached entries."""
        self._planet_cache.clear()
        self._house_cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
        
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "planet_cache_size": len(self._planet_cache),
            "house_cache_size": len(self._house_cache),
            "maxsize": self.maxsize,
        }


class CachedSwissEphemerisAdapter:
    """
    Wrapper around SwissEphemerisAdapter that adds caching.

    This is a convenience class that wraps the adapter with caching.
    For more control, you can use the cache directly with the adapter.
    """

    def __init__(self, adapter, cache: Optional[EphemerisCache] = None):
        """
        Initialize cached adapter.

        Args:
            adapter: SwissEphemerisAdapter instance
            cache: Optional EphemerisCache instance (creates default if None)
        """
        from .adapter import SwissEphemerisAdapter
        
        if not isinstance(adapter, SwissEphemerisAdapter):
            raise TypeError("adapter must be a SwissEphemerisAdapter instance")
        
        self.adapter = adapter
        self.cache = cache or EphemerisCache()

    def calc_positions(
        self,
        dt_utc: datetime,
        location: Optional[GeoLocation],
        settings: EphemerisSettings,
    ) -> LayerPositions:
        """
        Calculate positions with caching.

        Uses cache for planet positions and house calculations.
        """
        from .adapter import _datetime_to_jd, _get_house_system_bytes
        
        jd = _datetime_to_jd(dt_utc)
        house_system_bytes = _get_house_system_bytes(settings["house_system"])
        flags = self.adapter._configure_flags(settings)

        # Calculate planets with caching
        planets: dict[str, Any] = {}
        include_objects = settings.get("include_objects", [])

        for obj_id in include_objects:
            obj_id_lower = obj_id.lower()

            # Handle special cases (south node, etc.)
            if obj_id_lower == "south_node":
                # Check cache for north node
                north_node_pos = self.cache.get_planet_position(jd, "north_node", flags)
                if north_node_pos is None:
                    # Calculate north node
                    north_node_pos = self.adapter._calc_planet_position("north_node", jd, flags)
                    if north_node_pos:
                        self.cache.set_planet_position(jd, "north_node", flags, north_node_pos)
                
                if north_node_pos:
                    south_lon = (north_node_pos["lon"] + 180) % 360
                    planets["south_node"] = {
                        "lon": south_lon,
                        "lat": 0.0,
                        "speed_lon": north_node_pos["speed_lon"],
                        "retrograde": north_node_pos["retrograde"],
                    }
                continue

            # Import here to avoid circular dependency
            from .adapter import SWEPH_PLANET_IDS
            if obj_id_lower not in SWEPH_PLANET_IDS:
                continue

            # Check cache
            cached_pos = self.cache.get_planet_position(jd, obj_id_lower, flags)
            if cached_pos is not None:
                planets[obj_id_lower] = cached_pos
            else:
                # Calculate and cache
                # Access the method through the adapter
                planet_pos = self.adapter._calc_planet_position(obj_id_lower, jd, flags)
                if planet_pos:
                    self.cache.set_planet_position(jd, obj_id_lower, flags, planet_pos)
                    planets[obj_id_lower] = planet_pos

        # Calculate houses with caching
        houses: Optional[dict[str, Any]] = None
        if location:
            cached_houses = self.cache.get_house_positions(
                jd, location["lat"], location["lon"], house_system_bytes, flags
            )
            if cached_houses is not None:
                houses = cached_houses
            else:
                # Access the method through the adapter
                houses = self.adapter._calc_houses(
                    jd,
                    location["lat"],
                    location["lon"],
                    house_system_bytes,
                    settings["house_system"],
                    flags,
                )
                self.cache.set_house_positions(
                    jd, location["lat"], location["lon"], house_system_bytes, flags, houses
                )

        return {
            "planets": planets,
            "houses": houses,
        }

    def clear_cache(self) -> None:
        """Clear the cache."""
        self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()

