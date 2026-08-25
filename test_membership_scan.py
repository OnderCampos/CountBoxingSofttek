"""
Unit tests for the Membership Card Scan Login on Mobile logic.

Subtasks covered:
- subtask-7-1: Build scan membership card option on the mobile login screen.
- subtask-7-2: Implement scan error handling and manual fallback.
- subtask-7-3: Enforce device and OS compatibility for scan feature.
- subtask-7-4: Create unit tests for membership card scan logic.
"""

import pytest

from membership_scan import (
    DeviceInfo,
    MembershipScanner,
    Platform,
    ScanError,
    ScanResult,
)


class TestSubtask71BuildScanOptionOnMobileLoginScreen:
    """Subtask-7-1: scan button, camera launch, extraction and auto-populate."""

    def test_scan_replaces_manual_entry_and_populates_field(self):
        scanner = MembershipScanner(language="en")
        scanner.set_manual_entry("12345")  # previous manual value
        assert scanner.membership_number == "12345"

        result = scanner.scan("MEMBER-678901234")

        assert result == ScanResult("678901234", "scan")
        assert scanner.membership_number == "678901234"

    def test_scan_advances_to_password_or_biometric_step(self):
        scanner = MembershipScanner()
        assert scanner.step == "login"

        scanner.scan("55555")

        assert scanner.step == "password_or_biometric"

    def test_scan_of_plain_number_works(self):
        scanner = MembershipScanner()
        result = scanner.scan("1234567890")

        assert result.membership_number == "1234567890"
        assert scanner.membership_number == "1234567890"

    def test_scan_of_qr_payload_with_prefix_and_suffix_works(self):
        scanner = MembershipScanner()
        result = scanner.scan("https://gym.example.com/member?id=9876543210&club=5")

        assert result.membership_number == "9876543210"


class TestSubtask72ScanErrorHandlingAndManualFallback:
    """Subtask-7-2: error handling for unreadable/invalid codes and manual fallback."""

    def test_empty_scan_raises_unreadable_error(self):
        scanner = MembershipScanner(language="en")

        with pytest.raises(ScanError) as exc_info:
            scanner.scan("")

        assert exc_info.value.message_key == "unreadable"
        assert "Unable to read" in exc_info.value.message
        assert scanner.membership_number == ""

    def test_whitespace_only_scan_raises_unreadable_error(self):
        scanner = MembershipScanner(language="en")

        with pytest.raises(ScanError) as exc_info:
            scanner.scan("   ")

        assert exc_info.value.message_key == "unreadable"

    def test_scan_without_any_digits_raises_unreadable_error(self):
        scanner = MembershipScanner(language="en")

        with pytest.raises(ScanError) as exc_info:
            scanner.scan("not-a-code")

        assert exc_info.value.message_key == "unreadable"

    def test_scan_with_too_short_number_raises_invalid_error(self):
        scanner = MembershipScanner(language="en")

        with pytest.raises(ScanError) as exc_info:
            scanner.scan("1234")

        assert exc_info.value.message_key == "invalid"
        assert "Invalid membership code" in exc_info.value.message

    def test_scan_with_too_long_number_raises_invalid_error(self):
        scanner = MembershipScanner(language="en")

        with pytest.raises(ScanError) as exc_info:
            scanner.scan("1" * 21)

        assert exc_info.value.message_key == "invalid"

    def test_error_messages_are_localized_to_spanish(self):
        scanner = MembershipScanner(language="es")

        with pytest.raises(ScanError) as exc_info:
            scanner.scan("")

        assert "No se puede leer" in exc_info.value.message

        with pytest.raises(ScanError) as exc_info:
            scanner.scan("1234")

        assert "inválido" in exc_info.value.message

    def test_manual_fallback_populates_membership_number(self):
        scanner = MembershipScanner()
        result = scanner.set_manual_entry("1122334455")

        assert result == ScanResult("1122334455", "manual")
        assert scanner.membership_number == "1122334455"
        assert scanner.step == "password_or_biometric"

    def test_retry_clears_error_and_returns_to_login_step(self):
        scanner = MembershipScanner()
        try:
            scanner.scan("bad")
        except ScanError:
            pass

        scanner.retry()

        assert scanner.step == "login"
        assert scanner.last_error is None


class TestSubtask73DeviceAndOSCompatibility:
    """Subtask-7-3: camera availability and supported OS versions."""

    @pytest.mark.parametrize(
        "os_version, has_camera, expected_supported",
        [
            ("15.0", True, True),
            ("16.2", True, True),
            ("14.9", True, False),
            ("15.0", False, False),
        ],
    )
    def test_ios_compatibility(self, os_version, has_camera, expected_supported):
        device = DeviceInfo(Platform.IOS, os_version, has_camera)
        supported, error = MembershipScanner.is_device_supported(device)
        assert supported is expected_supported
        assert (error is None) == supported

    @pytest.mark.parametrize(
        "os_version, has_camera, expected_supported",
        [
            ("10.0", True, True),
            ("13.1", True, True),
            ("9.0", True, False),
            ("10.0", False, False),
        ],
    )
    def test_android_compatibility(self, os_version, has_camera, expected_supported):
        device = DeviceInfo(Platform.ANDROID, os_version, has_camera)
        supported, error = MembershipScanner.is_device_supported(device)
        assert supported is expected_supported
        assert (error is None) == supported

    def test_unsupported_platform_is_silently_omitted(self):
        device = DeviceInfo(Platform.OTHER, "1.0", True)
        supported, error = MembershipScanner.is_device_supported(device)

        assert supported is False
        assert error is None  # no error shown; scan option is simply omitted

    def test_unsupported_device_does_not_raise_on_scan_disabled_check(self):
        device = DeviceInfo(Platform.ANDROID, "8.0", True)
        supported, error = MembershipScanner.is_device_supported(device, language="es")

        assert supported is False
        assert error is not None
        assert "no es compatible" in error


class TestSubtask74UnitTestsForMembershipCardScanLogic:
    """Subtask-7-4: broad coverage requested for the scan logic."""

    def test_successful_barcode_extraction_populates_field(self):
        scanner = MembershipScanner()
        result = scanner.scan("BARCODE:1234567890123")

        assert result.membership_number == "1234567890123"
        assert scanner.membership_number == "1234567890123"

    def test_error_handling_for_unreadable_data(self):
        scanner = MembershipScanner()
        with pytest.raises(ScanError) as exc_info:
            scanner.scan(None)  # type: ignore[arg-type]
        assert exc_info.value.message_key == "unreadable"

    def test_fallback_to_manual_entry_on_scan_failure(self):
        scanner = MembershipScanner()
        with pytest.raises(ScanError):
            scanner.scan("no-digits")

        result = scanner.set_manual_entry("9999900000")

        assert result.source == "manual"
        assert scanner.membership_number == "9999900000"

    def test_scan_option_suppressed_on_unsupported_device(self):
        unsupported_device = DeviceInfo(Platform.IOS, "14.5", True)
        supported, _ = MembershipScanner.is_device_supported(unsupported_device)
        assert supported is False

    def test_scan_option_suppressed_on_unsupported_os(self):
        unsupported_device = DeviceInfo(Platform.ANDROID, "7.0", True)
        supported, _ = MembershipScanner.is_device_supported(unsupported_device)
        assert supported is False

    def test_reset_returns_scanner_to_initial_state(self):
        scanner = MembershipScanner()
        scanner.scan("1234567890")
        scanner.reset()

        assert scanner.membership_number == ""
        assert scanner.step == "login"
        assert scanner.last_error is None
