# crius-swiss

**Crius** - Swiss Ephemeris adapter implementation for astrological calculations.

Named after [Crius](https://en.wikipedia.org/wiki/Crius), the Titan of constellations and measuring the year in Greek mythology.

## Overview

This package provides a Swiss Ephemeris adapter implementation that conforms to the `crius-ephemeris-core` protocol.

**⚠️ License Notice**: This package is licensed under AGPL-3.0 due to its dependency on Swiss Ephemeris. Users must comply with Swiss Ephemeris licensing requirements.

## Installation

```bash
pip install crius-swiss
```

Or for development:

```bash
pip install -e packages/crius-swiss
```

**Note**: You must provide your own Swiss Ephemeris data files (`.se1` files). See the [Swiss Ephemeris documentation](https://www.astro.com/swisseph/swephinfo_e.htm) for licensing and data file requirements.

## Usage

```python
from crius_swiss import SwissEphemerisAdapter
from crius_ephemeris_core import EphemerisSettings, GeoLocation
from datetime import datetime

# Initialize adapter (optionally specify ephemeris path)
adapter = SwissEphemerisAdapter(ephemeris_path="/path/to/swisseph")

# Define settings and location
settings: EphemerisSettings = {
    "zodiac_type": "tropical",
    "ayanamsa": None,
    "house_system": "placidus",
    "include_objects": ["sun", "moon", "mercury", "venus", "mars"],
}

location: GeoLocation = {
    "lat": 40.7128,
    "lon": -74.0060,
}

# Calculate positions
dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
positions = adapter.calc_positions(dt, location, settings)

print(positions["planets"]["sun"])
```

## Configuration

The adapter looks for Swiss Ephemeris data files in:
1. The path specified in the constructor (`ephemeris_path`)
2. The `SWISS_EPHEMERIS_PATH` environment variable
3. The default path: `/usr/local/share/swisseph`

### Caching

For improved performance with repeated calculations, you can use the caching layer:

```python
from crius_swiss import SwissEphemerisAdapter, CachedSwissEphemerisAdapter, EphemerisCache

# Create adapter
adapter = SwissEphemerisAdapter()

# Wrap with caching
cache = EphemerisCache(maxsize=256)  # Cache up to 256 entries
cached_adapter = CachedSwissEphemerisAdapter(adapter, cache=cache)

# Use cached adapter
positions = cached_adapter.calc_positions(dt, location, settings)

# Check cache statistics
stats = cached_adapter.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")
```

## Supported House Systems

The adapter supports the following house systems:

- **placidus** - Placidus house system (default)
- **whole_sign** - Whole Sign houses
- **koch** - Koch house system
- **equal** - Equal house system
- **regiomontanus** - Regiomontanus house system
- **campanus** - Campanus house system
- **alcabitius** - Alcabitius house system
- **morinus** - Morinus house system

Example:

```python
settings: EphemerisSettings = {
    "zodiac_type": "tropical",
    "ayanamsa": None,
    "house_system": "whole_sign",  # Use whole sign houses
    "include_objects": ["sun", "moon"],
}
```

## Chiron Support

Chiron is fully supported in crius-swiss:

```python
settings: EphemerisSettings = {
    "zodiac_type": "tropical",
    "ayanamsa": None,
    "house_system": "placidus",
    "include_objects": ["chiron"],
}

positions = adapter.calc_positions(dt, location, settings)
chiron_pos = positions["planets"]["chiron"]
```

Chiron calculations use Swiss Ephemeris's built-in Chiron support, which provides accurate positions for this minor planet.

## Validation

You can validate ephemeris file presence before using the adapter:

```python
from crius_swiss import validate_ephemeris_path, validate_ephemeris_files

# Check if path is valid
is_valid, errors = validate_ephemeris_path("/path/to/swisseph")
if not is_valid:
    print("Errors:", errors)

# Check for specific files
is_valid, errors = validate_ephemeris_files(
    "/path/to/swisseph",
    required_files=["sepl_18.se1", "seplm_18.se1"]
)
```

## Troubleshooting

### Ephemeris Files Not Found

**Error**: `EphemerisFileNotFoundError`

**Solutions**:
1. Verify Swiss Ephemeris files are installed:
   ```python
   from crius_swiss import validate_ephemeris_path
   is_valid, errors = validate_ephemeris_path("/path/to/swisseph")
   ```

2. Set the `SWISS_EPHEMERIS_PATH` environment variable:
   ```bash
   export SWISS_EPHEMERIS_PATH=/path/to/swisseph
   ```

3. Specify the path explicitly:
   ```python
   adapter = SwissEphemerisAdapter(ephemeris_path="/path/to/swisseph")
   ```

4. Download Swiss Ephemeris files from:
   https://www.astro.com/swisseph/swephinfo_e.htm

### Calculation Errors

**Error**: `EphemerisCalculationError`

This usually indicates:
- Date is outside the supported range (Swiss Ephemeris supports 6000 BCE - 10000 CE)
- Invalid planet ID in `include_objects`
- Corrupted ephemeris data files

**Solutions**:
- Check that the date is within the supported range
- Verify planet IDs are valid (see supported objects below)
- Re-download Swiss Ephemeris files if corruption is suspected

### Invalid House System

**Error**: `InvalidHouseSystemError`

**Solution**: Use one of the supported house systems listed above.

### Invalid Ayanamsa

**Error**: `InvalidAyanamsaError`

**Solution**: Use one of the supported ayanamsas:
- `lahiri` (default)
- `fagan_bradley`
- `de_luce`
- `raman`
- `krishnamurti`
- `yukteshwar`
- `djwhal_khul`
- `true_citra`
- `true_revati`
- `aryabhata`
- `aryabhata_mean_sun`

## Supported Objects

The adapter supports the following celestial objects:

- **Planets**: `sun`, `moon`, `mercury`, `venus`, `mars`, `jupiter`, `saturn`, `uranus`, `neptune`, `pluto`
- **Minor Planets**: `chiron`
- **Lunar Nodes**: `north_node`, `south_node`

## Performance Tips

1. **Use Caching**: For repeated calculations, use `CachedSwissEphemerisAdapter` to cache results
2. **Batch Calculations**: Calculate multiple positions in one call rather than multiple calls
3. **Skip Validation**: If you're certain files exist, set `validate_files=False` in the constructor:
   ```python
   adapter = SwissEphemerisAdapter(validate_files=False)
   ```

## Thread Safety

Swiss Ephemeris is generally thread-safe for read operations. However, the adapter maintains internal state (sidereal mode caching). For concurrent use:

- Each thread should use its own adapter instance, OR
- Use thread synchronization if sharing an adapter instance

## License

**AGPL-3.0** - This package uses Swiss Ephemeris, which is dual-licensed under AGPL or a commercial license. Users must comply with Swiss Ephemeris licensing requirements.

See the [Swiss Ephemeris licensing information](https://www.astro.com/swisseph/swephinfo_e.htm) for details.

## Dependencies

- `crius-ephemeris-core` - Core types and interfaces
- `pyswisseph` - Python bindings for Swiss Ephemeris
- `pytz` - Timezone support

## Related Packages

- `crius-ephemeris-core` - Core types and interfaces (MIT licensed)

