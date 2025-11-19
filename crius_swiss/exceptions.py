"""Custom exceptions for crius-swiss."""


class CriusSwissError(Exception):
    """Base exception for crius-swiss errors."""

    pass


class EphemerisFileNotFoundError(CriusSwissError):
    """Raised when Swiss Ephemeris data files are not found."""

    def __init__(self, path: str, message: str = None):
        """
        Initialize exception.

        Args:
            path: Path where files were expected
            message: Optional custom message
        """
        self.path = path
        if message is None:
            message = (
                f"Swiss Ephemeris data files not found at: {path}\n"
                f"Please ensure Swiss Ephemeris data files (.se1 files) are installed.\n"
                f"You can:\n"
                f"  1. Set SWISS_EPHEMERIS_PATH environment variable to the correct path\n"
                f"  2. Install Swiss Ephemeris files to {path}\n"
                f"  3. Pass ephemeris_path parameter to SwissEphemerisAdapter\n"
                f"\n"
                f"For licensing and download information, see:\n"
                f"  https://www.astro.com/swisseph/swephinfo_e.htm"
            )
        super().__init__(message)


class EphemerisCalculationError(CriusSwissError):
    """Raised when an ephemeris calculation fails."""

    def __init__(self, message: str, planet_id: str = None, datetime=None):
        """
        Initialize exception.

        Args:
            message: Error message
            planet_id: Optional planet ID that failed
            datetime: Optional datetime that failed
        """
        self.planet_id = planet_id
        self.datetime = datetime
        full_message = message
        if planet_id:
            full_message += f" (planet: {planet_id})"
        if datetime:
            full_message += f" (datetime: {datetime})"
        super().__init__(full_message)


class InvalidHouseSystemError(CriusSwissError):
    """Raised when an invalid house system is specified."""

    def __init__(self, house_system: str, valid_systems: list = None):
        """
        Initialize exception.

        Args:
            house_system: Invalid house system name
            valid_systems: List of valid house system names
        """
        self.house_system = house_system
        self.valid_systems = valid_systems or []
        message = f"Invalid house system: {house_system}"
        if valid_systems:
            message += f"\nValid house systems: {', '.join(valid_systems)}"
        super().__init__(message)


class InvalidAyanamsaError(CriusSwissError):
    """Raised when an invalid ayanamsa is specified."""

    def __init__(self, ayanamsa: str, valid_ayanamsas: list = None):
        """
        Initialize exception.

        Args:
            ayanamsa: Invalid ayanamsa name
            valid_ayanamsas: List of valid ayanamsa names
        """
        self.ayanamsa = ayanamsa
        self.valid_ayanamsas = valid_ayanamsas or []
        message = f"Invalid ayanamsa: {ayanamsa}"
        if valid_ayanamsas:
            message += f"\nValid ayanamsas: {', '.join(valid_ayanamsas)}"
        super().__init__(message)

