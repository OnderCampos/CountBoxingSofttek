"""Lightweight self-contained runner for membership_scan tests.

This runner is used when pytest is not available in the sandbox. It executes the
same test cases defined in test_membership_scan.py and reports pass/fail.
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from membership_scan import (
    MembershipScanner,
    MobileLoginScreen,
    DeviceInfo,
    DeviceCompatibility,
    ScanError,
)


PASS = 0
FAIL = 0


def make_supported_device(has_camera=True):
    return DeviceInfo(os_name="android", os_version=12, has_camera=has_camera)


def record(name, fn):
    global PASS, FAIL
    try:
        fn()
        PASS += 1
        print(f"  PASS: {name}")
    except Exception as exc:  # noqa: BLE001
        FAIL += 1
        print(f"  FAIL: {name}")
        traceback.print_exception(type(exc), exc, exc.__traceback__)


def main():
    print("Task: Membership Card Scan Login on Mobile")
    print("=" * 60)

    print("\nSubtask-7-1: Build scan membership card option on the mobile login screen")
    record("scan option visible on supported device", lambda: assert_true(
        MobileLoginScreen(DeviceInfo(os_name="ios", os_version=16, has_camera=True)).should_show_scan_option()
    ))
    record("successful scan extracts membership number", lambda: assert_eq(
        MobileLoginScreen(make_supported_device()).on_scan_success("12345678")["membership_number"], "12345678"
    ))
    record("scanned value replaces manual entry", lambda: replace_manual_entry())
    record("successful scan clears previous error", lambda: scan_clears_error())
    record("prefixed barcode is parsed correctly", lambda: assert_eq(
        MobileLoginScreen(make_supported_device()).on_scan_success("MEMBER:12345678")["membership_number"], "12345678"
    ))

    print("\nSubtask-7-2: Implement scan error handling and manual fallback")
    record("empty scan raises UNREADABLE_CODE", lambda: assert_raises(lambda: MembershipScanner.scan(""), "UNREADABLE_CODE"))
    record("None scan raises UNREADABLE_CODE", lambda: assert_raises(lambda: MembershipScanner.scan(None), "UNREADABLE_CODE"))
    record("garbled scan raises INVALID_MEMBERSHIP_NUMBER", lambda: assert_raises(lambda: MembershipScanner.scan("@@#$%"), "INVALID_MEMBERSHIP_NUMBER"))
    record("wrong-length membership raises INVALID_MEMBERSHIP_NUMBER", lambda: assert_raises(lambda: MembershipScanner.scan("1234567"), "INVALID_MEMBERSHIP_NUMBER"))
    record("scan failure offers retry and manual_entry", lambda: assert_contains_all(
        MobileLoginScreen(make_supported_device()).on_scan_failure(ScanError("UNREADABLE_CODE"))["actions"],
        ["retry", "manual_entry"]
    ))
    record("scan failure message is localized", lambda: assert_contains(
        MobileLoginScreen(make_supported_device()).on_scan_failure(ScanError("INVALID_MEMBERSHIP_NUMBER"))["error"],
        "Invalid membership number"
    ))
    record("manual entry allowed after scan failure", lambda: manual_entry_after_failure())

    print("\nSubtask-7-3: Enforce device and OS compatibility")
    record("iOS 15+ with camera shows scan option", lambda: assert_true(
        MobileLoginScreen(DeviceInfo(os_name="ios", os_version=15, has_camera=True)).should_show_scan_option()
    ))
    record("iOS 14 hides scan option without error", lambda: assert_hidden_without_error(DeviceInfo(os_name="ios", os_version=14, has_camera=True)))
    record("Android 10+ with camera shows scan option", lambda: assert_true(
        MobileLoginScreen(DeviceInfo(os_name="android", os_version=10, has_camera=True)).should_show_scan_option()
    ))
    record("Android 9 hides scan option without error", lambda: assert_hidden_without_error(DeviceInfo(os_name="android", os_version=9, has_camera=True)))
    record("no camera hides scan option without error", lambda: assert_hidden_without_error(DeviceInfo(os_name="android", os_version=12, has_camera=False)))
    record("unsupported OS hides scan option", lambda: assert_false(
        MobileLoginScreen(DeviceInfo(os_name="windows", os_version=11, has_camera=True)).should_show_scan_option()
    ))
    record("compatibility matrix", run_compatibility_matrix)

    print("\nSubtask-7-4: Unit test coverage summary")
    record("successful scan populates membership field", lambda: assert_eq(
        MobileLoginScreen(make_supported_device()).on_scan_success("QR:12345678")["membership_number"], "12345678"
    ))
    record("invalid scan data triggers error handling", lambda: assert_raises(
        lambda: MobileLoginScreen(make_supported_device()).on_scan_success("1234"), "INVALID_MEMBERSHIP_NUMBER"
    ))
    record("fallback to manual entry on scan failure", lambda: fallback_to_manual_entry())
    record("scan option suppressed on unsupported device", lambda: assert_false(
        MobileLoginScreen(DeviceInfo(os_name="ios", os_version=14, has_camera=True)).should_show_scan_option()
    ))

    print("\n" + "=" * 60)
    print(f"Results: {PASS} passed, {FAIL} failed")
    sys.exit(0 if FAIL == 0 else 1)


def replace_manual_entry():
    s = MobileLoginScreen(make_supported_device())
    s.update_membership_number("99999999")
    s.on_scan_success("12345678")
    assert_eq(s.membership_number, "12345678")


def scan_clears_error():
    s = MobileLoginScreen(make_supported_device())
    s.error_message = "prev"
    s.on_scan_success("12345678")
    assert_eq(s.error_message, "")


def manual_entry_after_failure():
    s = MobileLoginScreen(make_supported_device())
    s.membership_number = ""
    s.update_membership_number("11112222")
    assert_eq(s.membership_number, "11112222")


def fallback_to_manual_entry():
    s = MobileLoginScreen(make_supported_device())
    result = s.on_scan_failure(ScanError("UNREADABLE_CODE"))
    assert_contains_all(result["actions"], ["manual_entry", "retry"])
    s.update_membership_number("11112222")
    assert_eq(s.membership_number, "11112222")


def assert_hidden_without_error(device):
    s = MobileLoginScreen(device)
    assert_false(s.should_show_scan_option())
    assert_eq(s.error_message, "")


def assert_true(value):
    if not value:
        raise AssertionError(f"Expected True, got {value}")


def assert_false(value):
    if value:
        raise AssertionError(f"Expected False, got {value}")


def assert_eq(actual, expected):
    if actual != expected:
        raise AssertionError(f"Expected {expected!r}, got {actual!r}")


def assert_contains(text, substring):
    if substring not in text:
        raise AssertionError(f"Expected {text!r} to contain {substring!r}")


def assert_contains_all(container, items):
    missing = [item for item in items if item not in container]
    if missing:
        raise AssertionError(f"Expected {container!r} to contain all of {items!r}; missing {missing}")


def assert_raises(callable, expected_message):
    try:
        callable()
    except ScanError as exc:
        if str(exc) != expected_message:
            raise AssertionError(f"Expected ScanError({expected_message!r}), got ScanError({str(exc)!r})")
        return
    raise AssertionError("Expected ScanError to be raised")


def run_compatibility_matrix():
    cases = [
        ("ios", 15, True, True),
        ("ios", 14, True, False),
        ("android", 10, True, True),
        ("android", 9, True, False),
        ("android", 12, False, False),
        ("unknown", 1, True, False),
    ]
    for os_name, os_version, has_camera, expected in cases:
        device = DeviceInfo(os_name=os_name, os_version=os_version, has_camera=has_camera)
        actual = DeviceCompatibility.is_scan_supported(device)
        if actual != expected:
            raise AssertionError(f"Compat failed for {os_name} {os_version} camera={has_camera}: expected {expected}, got {actual}")


if __name__ == "__main__":
    main()
