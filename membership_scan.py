"""Membership card scan logic for mobile login.

This module implements the business rules for scanning a membership
barcode/QR code on a mobile device, handling scan errors, and
determining device/OS compatibility for presenting the scan option.
"""

from dataclasses import dataclass
from typing import Dict, Any


class ScanError(Exception):
    """Raised when a scan cannot be processed or yields invalid data."""
    pass


@dataclass(frozen=True)
class DeviceInfo:
    """Represents the mobile device capabilities relevant to scanning."""
    os_name: str
    os_version: int
    has_camera: bool


class DeviceCompatibility:
    """Checks whether the scan option should be presented on a device."""

    SUPPORTED_OS = {"ios": 15, "android": 10}

    @staticmethod
    def is_scan_supported(device: DeviceInfo) -> bool:
        """Return True only on iOS 15+, Android 10+ with an available camera."""
        os_name = device.os_name.lower()
        if os_name not in DeviceCompatibility.SUPPORTED_OS:
            return False
        if device.os_version < DeviceCompatibility.SUPPORTED_OS[os_name]:
            return False
        return device.has_camera


class MembershipScanner:
    """Parses raw scanned data and extracts a membership number."""

    MEMBERSHIP_LENGTH = 8

    @staticmethod
    def parse_scanned_data(raw_data: str) -> str:
        """Validate and extract a membership number from scanned text.

        Supported formats:
        - Plain digits such as "12345678"
        - Prefixed values such as "MEMBER:12345678" or "QR:12345678"

        Raises:
            ScanError: If the input is empty/undecipherable or the extracted
                number does not match the expected membership length.
        """
        if raw_data is None:
            raise ScanError("UNREADABLE_CODE")

        cleaned = raw_data.strip()
        if not cleaned:
            raise ScanError("UNREADABLE_CODE")

        # Strip a prefix if present, e.g. "MEMBER:12345678"
        if ":" in cleaned:
            cleaned = cleaned.split(":", 1)[1]

        digits = "".join(ch for ch in cleaned if ch.isdigit())
        if len(digits) != MembershipScanner.MEMBERSHIP_LENGTH:
            raise ScanError("INVALID_MEMBERSHIP_NUMBER")

        return digits

    @classmethod
    def scan(cls, raw_data: str) -> str:
        """Convenience wrapper around parse_scanned_data."""
        return cls.parse_scanned_data(raw_data)


class MobileLoginScreen:
    """Mobile login screen state and scan interactions."""

    def __init__(self, device: DeviceInfo):
        self.device = device
        self.membership_number = ""
        self.error_message = ""
        self.scan_option_visible = DeviceCompatibility.is_scan_supported(device)

    def should_show_scan_option(self) -> bool:
        """Return whether the scan button should be rendered."""
        return self.scan_option_visible

    def update_membership_number(self, value: str) -> None:
        """Manually update the membership number field."""
        self.membership_number = value

    def on_scan_success(self, raw_data: str) -> Dict[str, Any]:
        """Process a successful scan, replacing any manual entry.

        Returns:
            A dict indicating the next step and the extracted membership number.
        """
        number = MembershipScanner.scan(raw_data)
        self.membership_number = number
        self.error_message = ""
        return {
            "next_step": "password_or_biometric",
            "membership_number": number,
        }

    def on_scan_failure(self, error: ScanError) -> Dict[str, Any]:
        """Process a failed scan and provide recovery actions.

        Returns:
            A dict with a localized error message and available actions.
        """
        self.error_message = self._localize_error(str(error))
        return {
            "error": self.error_message,
            "actions": ["retry", "manual_entry"],
        }

    @staticmethod
    def _localize_error(error_key: str) -> str:
        """Return a user-facing localized message for a scan error key."""
        messages = {
            "UNREADABLE_CODE": (
                "Unable to read the code. Please retry or enter your membership number manually."
            ),
            "INVALID_MEMBERSHIP_NUMBER": (
                "Invalid membership number. Please retry or enter your membership number manually."
            ),
        }
        return messages.get(
            error_key,
            "Scan failed. Please retry or enter your membership number manually.",
        )
