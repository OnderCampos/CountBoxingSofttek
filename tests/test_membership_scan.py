"""Unit tests for membership card scan login logic (task-7).

Subtasks:
  - subtask-7-1: Build scan membership card option on the mobile login screen.
  - subtask-7-2: Implement scan error handling and manual fallback.
  - subtask-7-3: Enforce device and OS compatibility for scan feature.
  - subtask-7-4: Create unit tests for membership card scan logic.
"""

import pytest
from membership_scan import (
    MembershipScanner,
    MobileLoginScreen,
    DeviceInfo,
    DeviceCompatibility,
    ScanError,
)


def make_supported_device(has_camera=True):
    return DeviceInfo(os_name="android", os_version=12, has_camera=has_camera)


# ============================================================================
# Task: Membership Card Scan Login on Mobile (task-7)
# ============================================================================


describe("Task: Membership Card Scan Login on Mobile")


class TestSubtask7_1_BuildScanOption:
    """Subtask-7-1: Implement a scan option on the mobile login screen."""

    def test_scan_button_visible_on_supported_device(self):
        """Subtask: 7-1 - Scan option is shown when device is compatible."""
        device = DeviceInfo(os_name="ios", os_version=16, has_camera=True)
        screen = MobileLoginScreen(device)

        assert screen.should_show_scan_option() is True

    def test_on_scan_success_extracts_membership_number(self):
        """Subtask: 7-1 - Successful scan extracts membership number."""
        screen = MobileLoginScreen(make_supported_device())
        result = screen.on_scan_success("12345678")

        assert result["membership_number"] == "12345678"
        assert result["next_step"] == "password_or_biometric"

    def test_on_scan_success_replaces_manual_entry(self):
        """Subtask: 7-1 - Scanned value fully replaces manual entry."""
        screen = MobileLoginScreen(make_supported_device())
        screen.update_membership_number("99999999")

        screen.on_scan_success("12345678")

        assert screen.membership_number == "12345678"

    def test_on_scan_success_clears_previous_error(self):
        """Subtask: 7-1 - A successful scan clears any previous error state."""
        screen = MobileLoginScreen(make_supported_device())
        screen.error_message = "Some previous error"

        screen.on_scan_success("12345678")

        assert screen.error_message == ""

    def test_on_scan_success_supports_prefixed_barcode(self):
        """Subtask: 7-1 - Barcodes with prefixes are parsed correctly."""
        screen = MobileLoginScreen(make_supported_device())

        screen.on_scan_success("MEMBER:12345678")

        assert screen.membership_number == "12345678"


class TestSubtask7_2_ErrorHandlingAndManualFallback:
    """Subtask-7-2: Implement scan error handling and manual fallback."""

    def test_empty_scan_raises_unreadable_error(self):
        """Subtask: 7-2 - Empty scan yields an UNREADABLE_CODE error."""
        with pytest.raises(ScanError) as exc_info:
            MembershipScanner.scan("")

        assert str(exc_info.value) == "UNREADABLE_CODE"

    def test_none_scan_raises_unreadable_error(self):
        """Subtask: 7-2 - None scan data yields an UNREADABLE_CODE error."""
        with pytest.raises(ScanError) as exc_info:
            MembershipScanner.scan(None)

        assert str(exc_info.value) == "UNREADABLE_CODE"

    def test_garbled_scan_raises_invalid_error(self):
        """Subtask: 7-2 - Garbled scan without digits yields INVALID_MEMBERSHIP_NUMBER."""
        with pytest.raises(ScanError) as exc_info:
            MembershipScanner.scan("@@#$%")

        assert str(exc_info.value) == "INVALID_MEMBERSHIP_NUMBER"

    def test_wrong_length_membership_raises_invalid_error(self):
        """Subtask: 7-2 - Wrong-length membership number is invalid."""
        with pytest.raises(ScanError) as exc_info:
            MembershipScanner.scan("1234567")

        assert str(exc_info.value) == "INVALID_MEMBERSHIP_NUMBER"

    def test_scan_failure_returns_retry_and_manual_actions(self):
        """Subtask: 7-2 - Failure result offers retry and manual entry."""
        screen = MobileLoginScreen(make_supported_device())
        error = ScanError("UNREADABLE_CODE")

        result = screen.on_scan_failure(error)

        assert "retry" in result["actions"]
        assert "manual_entry" in result["actions"]
        assert result["error"] != ""

    def test_scan_failure_localizes_error_message(self):
        """Subtask: 7-2 - Error message is localized and user-facing."""
        screen = MobileLoginScreen(make_supported_device())

        result = screen.on_scan_failure(ScanError("INVALID_MEMBERSHIP_NUMBER"))

        assert "Invalid membership number" in result["error"]

    def test_manual_entry_allowed_after_scan_failure(self):
        """Subtask: 7-2 - User can still enter membership number manually."""
        screen = MobileLoginScreen(make_supported_device())

        try:
            MembershipScanner.scan("BAD")
        except ScanError:
            pass

        screen.update_membership_number("87654321")

        assert screen.membership_number == "87654321"


class TestSubtask7_3_DeviceAndOSCompatibility:
    """Subtask-7-3: Enforce device and OS compatibility for scan feature."""

    def test_supported_ios_version_shows_scan_option(self):
        """Subtask: 7-3 - iOS 15+ with camera shows scan option."""
        device = DeviceInfo(os_name="ios", os_version=15, has_camera=True)
        screen = MobileLoginScreen(device)

        assert screen.should_show_scan_option() is True

    def test_old_ios_hides_scan_option_without_error(self):
        """Subtask: 7-3 - iOS 14 hides scan option without displaying an error."""
        device = DeviceInfo(os_name="ios", os_version=14, has_camera=True)
        screen = MobileLoginScreen(device)

        assert screen.should_show_scan_option() is False
        assert screen.error_message == ""

    def test_supported_android_version_shows_scan_option(self):
        """Subtask: 7-3 - Android 10+ with camera shows scan option."""
        device = DeviceInfo(os_name="android", os_version=10, has_camera=True)
        screen = MobileLoginScreen(device)

        assert screen.should_show_scan_option() is True

    def test_old_android_hides_scan_option_without_error(self):
        """Subtask: 7-3 - Android 9 hides scan option without displaying an error."""
        device = DeviceInfo(os_name="android", os_version=9, has_camera=True)
        screen = MobileLoginScreen(device)

        assert screen.should_show_scan_option() is False
        assert screen.error_message == ""

    def test_no_camera_hides_scan_option(self):
        """Subtask: 7-3 - Missing camera hides scan option without error."""
        device = DeviceInfo(os_name="android", os_version=12, has_camera=False)
        screen = MobileLoginScreen(device)

        assert screen.should_show_scan_option() is False
        assert screen.error_message == ""

    def test_unsupported_os_hides_scan_option(self):
        """Subtask: 7-3 - Unknown OS hides scan option without error."""
        device = DeviceInfo(os_name="windows", os_version=11, has_camera=True)
        screen = MobileLoginScreen(device)

        assert screen.should_show_scan_option() is False
        assert screen.error_message == ""

    @pytest.mark.parametrize(
        "os_name,os_version,has_camera,expected",
        [
            ("ios", 15, True, True),
            ("ios", 14, True, False),
            ("android", 10, True, True),
            ("android", 9, True, False),
            ("android", 12, False, False),
            ("unknown", 1, True, False),
        ],
    )
    def test_compatibility_matrix(self, os_name, os_version, has_camera, expected):
        """Subtask: 7-3 - Compatibility matrix across OS versions and camera."""
        device = DeviceInfo(
            os_name=os_name, os_version=os_version, has_camera=has_camera
        )

        assert DeviceCompatibility.is_scan_supported(device) is expected


class TestSubtask7_4_CreateUnitTests:
    """Subtask-7-4: Additional assertions directly covering the requested scenarios."""

    def test_successful_scan_populates_membership_number_field(self):
        """Subtask: 7-4 - Successful barcode scan populates the membership field."""
        screen = MobileLoginScreen(make_supported_device())

        result = screen.on_scan_success("QR:12345678")

        assert screen.membership_number == "12345678"
        assert result["membership_number"] == "12345678"

    def test_error_handling_on_invalid_scan_data(self):
        """Subtask: 7-4 - Invalid scan data triggers error handling with retry."""
        screen = MobileLoginScreen(make_supported_device())

        with pytest.raises(ScanError):
            screen.on_scan_success("1234")

    def test_fallback_to_manual_entry_on_scan_failure(self):
        """Subtask: 7-4 - Manual entry remains available after scan failure."""
        screen = MobileLoginScreen(make_supported_device())

        failure = screen.on_scan_failure(ScanError("UNREADABLE_CODE"))

        assert "manual_entry" in failure["actions"]
        screen.update_membership_number("11112222")
        assert screen.membership_number == "11112222"

    def test_scan_option_suppressed_on_unsupported_device(self):
        """Subtask: 7-4 - Scan option omitted on unsupported device/OS."""
        device = DeviceInfo(os_name="ios", os_version=14, has_camera=True)
        screen = MobileLoginScreen(device)

        assert screen.should_show_scan_option() is False


def describe(label):
    """No-op marker used to label the task in test output."""


def it(label):
    """No-op marker used to label subtasks in test output."""
