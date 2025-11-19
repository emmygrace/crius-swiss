# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-01

### Added
- Initial release of crius-swiss
- `SwissEphemerisAdapter` - Swiss Ephemeris adapter implementation
- Support for all major planets (Sun, Moon, Mercury through Pluto)
- Support for Chiron
- Support for lunar nodes (north and south)
- Support for multiple house systems:
  - Placidus
  - Whole Sign
  - Koch
  - Equal
  - Regiomontanus
  - Campanus
  - Alcabitius
  - Morinus
- Support for tropical and sidereal zodiac
- Support for multiple ayanamsas:
  - Lahiri (default)
  - Fagan-Bradley
  - De Luce
  - Raman
  - Krishnamurti
  - Yukteshwar
  - Djwhal Khul
  - True Citra
  - True Revati
  - Aryabhata
  - Aryabhata Mean Sun
- Configuration via environment variable (`SWISS_EPHEMERIS_PATH`)
- Custom ephemeris path support

### Security
- This package is licensed under AGPL-3.0 due to Swiss Ephemeris dependency
- Users must comply with Swiss Ephemeris licensing requirements

[0.1.0]: https://github.com/gaia-tools/crius-swiss/releases/tag/v0.1.0

