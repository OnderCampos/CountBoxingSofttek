import pytest
from box_face import Boxface


class TestBoxface:
    """Tests for the core Boxface data model (User Story #1 building block)."""

    def test_constructor_stores_coordinates(self):
        box = Boxface(10, 20, 30, 40, False, 1)
        assert box.x1 == 10
        assert box.y1 == 20
        assert box.x2 == 30
        assert box.y2 == 40

    def test_constructor_calculates_center_even_distance(self):
        # Center of (10, 30) -> 10 + (20 // 2) = 20
        box = Boxface(10, 20, 30, 60, False, 2)
        assert box.xcenter == 20
        # Center of (20, 60) -> 20 + (40 // 2) = 40
        assert box.ycenter == 40
        assert box.get_center() == (20, 40)

    def test_constructor_calculates_center_odd_distance(self):
        # x center -> 5 + (abs(5-12) // 2) = 5 + 3 = 8
        box = Boxface(5, 5, 12, 14, False, 3)
        assert box.xcenter == 8
        assert box.ycenter == 9

    def test_hole_flag_false(self):
        box = Boxface(0, 0, 10, 10, False, 4)
        assert box.is_hole() is False

    def test_hole_flag_true(self):
        box = Boxface(0, 0, 10, 10, True, 5)
        assert box.is_hole() is True

    def test_id_roundtrip(self):
        box = Boxface(0, 0, 10, 10, False, 99)
        assert box.id == 99
        box.set_id(100)
        assert box.id == 100

    def test_repr(self):
        box = Boxface(0, 0, 10, 10, False, 7)
        assert repr(box) == "7"

    def test_zero_width_box_center(self):
        box = Boxface(5, 5, 5, 15, False, 8)
        assert box.xcenter == 5

    def test_negative_coordinates(self):
        # x center -> -10 + (abs(-10 - -5) // 2) = -10 + 2 = -8
        # y center -> -20 + (abs(-20 - -8) // 2) = -20 + 6 = -14
        box = Boxface(-10, -20, -5, -8, True, 9)
        assert box.xcenter == -8
        assert box.ycenter == -14
