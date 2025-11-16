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

## License

**AGPL-3.0** - This package uses Swiss Ephemeris, which is dual-licensed under AGPL or a commercial license. Users must comply with Swiss Ephemeris licensing requirements.

See the [Swiss Ephemeris licensing information](https://www.astro.com/swisseph/swephinfo_e.htm) for details.

## Dependencies

- `crius-ephemeris-core` - Core types and interfaces
- `pyswisseph` - Python bindings for Swiss Ephemeris
- `pytz` - Timezone support

## Related Packages

- `crius-ephemeris-core` - Core types and interfaces (MIT licensed)

