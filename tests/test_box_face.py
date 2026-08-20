import pytest
import math
from box_face import Boxface


class TestBoxface:
    """Unit tests for the Boxface data model."""

    def test_center_positive_coordinates(self):
        box = Boxface(0, 0, 10, 20, False, 1)
        assert box.get_center() == (5, 10)

    def test_center_negative_offset(self):
        box = Boxface(-10, -20, 10, 20, False, 2)
        assert box.get_center() == (0, 0)

    def test_center_integer_truncation(self):
        box = Boxface(0, 0, 11, 21, False, 3)
        # (11 // 2) = 5, (21 // 2) = 10
        assert box.get_center() == (5, 10)

    def test_is_hole(self):
        box_with_hole = Boxface(0, 0, 10, 10, True, 4)
        box_without_hole = Boxface(0, 0, 10, 10, False, 5)
        assert box_with_hole.is_hole() is True
        assert box_without_hole.is_hole() is False

    def test_set_id_updates_id(self):
        box = Boxface(0, 0, 10, 10, False, 1)
        box.set_id(99)
        assert box.id == 99

    def test_repr_returns_id_string(self):
        box = Boxface(0, 0, 10, 10, False, 42)
        assert repr(box) == "42"

    def test_zero_size_box(self):
        box = Boxface(5, 5, 5, 5, False, 6)
        assert box.get_center() == (5, 5)

    def test_large_coordinates(self):
        box = Boxface(0, 0, 10_000, 20_000, False, 7)
        assert box.get_center() == (5_000, 10_000)
