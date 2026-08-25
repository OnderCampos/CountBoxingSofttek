"""
Membership Card Scan Login on Mobile

Implements the business logic for scanning a membership card barcode/QR code
on a mobile login screen, including device compatibility checks, data parsing,
error handling and manual fallback.
"""

from dataclasses import dataclass
from enum import Enum
import re


class Platform(Enum):
    IOS = "ios"
    ANDROID = "android"
    OTHER = "other"


@dataclass(frozen=True)
class DeviceInfo:
    """Represents the mobile device where the scan feature runs."""

    platform: Platform
    os_version: str
    has_camera: bool


@dataclass(frozen=True)
class ScanResult:
    """Result of a successful scan or manual entry."""

    membership_number: str
    source: str  # "scan" or "manual"


class ScanError(Exception):
    """Raised when a scan cannot be processed successfully."""

    def __init__(self, message_key: str, message: str):
        self.message_key = message_key
        self.message = message
        super().__init__(message)


class MembershipScanner:
    """
    Encapsulates the membership card scan flow for mobile login.

    Responsibilities:
    - Decide whether the scan option should be presented based on the device.
    - Parse scanned barcode/QR data into a membership number.
    - Replace any manual entry with the scanned value on success.
    - Provide localized error messages and a manual fallback on failure.
    """

    LOCALIZED_MESSAGES = {
        "en": {
            "unreadable": (
                "Unable to read the code. Please try again or enter your membership number manually."
            ),
            "invalid": (
                "Invalid membership code. Please try again or enter your membership number manually."
            ),
            "no_camera": "Camera not available.",
            "unsupported_os": "Your device or operating system version is not supported.",
        },
        "es": {
            "unreadable": (
                "No se puede leer el código. Intente de nuevo o ingrese su número de membresía manualmente."
            ),
            "invalid": (
                "Código de membresía inválido. Intente de nuevo o ingrese su número de membresía manualmente."
            ),
            "no_camera": "Cámara no disponible.",
            "unsupported_os": "Su dispositivo o versión de sistema operativo no es compatible.",
        },
    }

    def __init__(self, language: str = "en"):
        self.language = language
        self.membership_number = ""
        self.last_error: ScanError | None = None
        self.step = "login"  # login | password_or_biometric

    # ------------------------------------------------------------------
    # Device / OS compatibility
    # ------------------------------------------------------------------
    @classmethod
    def _localized(cls, key: str, language: str) -> str:
        """Return a localized message for the given key."""
        return (
            cls.LOCALIZED_MESSAGES.get(language, cls.LOCALIZED_MESSAGES["en"])
            .get(key, key)
        )

    @classmethod
    def is_device_supported(
        cls, device_info: DeviceInfo, language: str = "en"
    ) -> tuple[bool, str | None]:
        """
        Determine whether the scan option should be presented.

        Returns:
            (supported: bool, error_message: str | None)

        The error message is only returned for supported platforms that fail
        the OS/camera requirement. For unsupported platforms it is None so the
        UI can silently omit the scan option.
        """
        if device_info.platform == Platform.IOS:
            try:
                major = int(device_info.os_version.split(".")[0])
                if major >= 15 and device_info.has_camera:
                    return True, None
            except (ValueError, IndexError):
                pass
            return False, cls._localized("unsupported_os", language)

        if device_info.platform == Platform.ANDROID:
            try:
                major = int(device_info.os_version.split(".")[0])
                if major >= 10 and device_info.has_camera:
                    return True, None
            except (ValueError, IndexError):
                pass
            return False, cls._localized("unsupported_os", language)

        # Unknown platforms are unsupported but the scan option is omitted silently.
        return False, None

    # ------------------------------------------------------------------
    # Data parsing
    # ------------------------------------------------------------------
    @classmethod
    def parse_scanned_data(cls, raw_data: str | None, language: str = "en") -> str:
        """
        Extract and validate a membership number from raw scanned data.

        Raises:
            ScanError: when the input is empty or contains no valid membership number.
        """
        if raw_data is None or not raw_data.strip():
            raise ScanError(
                "unreadable", cls._localized("unreadable", language)
            )

        text = raw_data.strip()
        match = re.search(r"\d+", text)
        if not match:
            raise ScanError(
                "unreadable", cls._localized("unreadable", language)
            )

        membership_number = match.group(0)

        # A membership number must be between 5 and 20 digits.
        if len(membership_number) < 5 or len(membership_number) > 20:
            raise ScanError("invalid", cls._localized("invalid", language))

        return membership_number

    # ------------------------------------------------------------------
    # Scan flow
    # ------------------------------------------------------------------
    def scan(self, raw_data: str) -> ScanResult:
        """
        Process scanned data.

        On success the scanned value fully replaces any previous manual entry,
        the membership number field is populated and the flow advances to the
        password / biometric step.
        """
        self.last_error = None
        membership_number = self.parse_scanned_data(raw_data, self.language)
        self.membership_number = membership_number
        self.step = "password_or_biometric"
        return ScanResult(membership_number, "scan")

    def set_manual_entry(self, membership_number: str) -> ScanResult:
        """Fallback to manual membership number entry."""
        self.last_error = None
        self.membership_number = membership_number
        self.step = "password_or_biometric"
        return ScanResult(membership_number, "manual")

    def retry(self) -> None:
        """Prepare the scanner for a new scan attempt after a failure."""
        self.last_error = None
        self.step = "login"

    def reset(self) -> None:
        """Reset the scanner to its initial state."""
        self.membership_number = ""
        self.last_error = None
        self.step = "login"
