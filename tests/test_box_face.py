import pytest
from box_face import Boxface


class TestBoxface:
    def test_constructor_sets_properties_and_center(self):
        box = Boxface(10, 20, 30, 40, False, 1)
        assert box.x1 == 10
        assert box.y1 == 20
        assert box.x2 == 30
        assert box.y2 == 40
        assert box.id == 1
        assert box.xcenter == 20
        assert box.ycenter == 30
        assert box.is_hole() is False

    def test_get_center(self):
        box = Boxface(0, 0, 10, 10, False, 2)
        assert box.get_center() == (5, 5)

    def test_set_id(self):
        box = Boxface(0, 0, 10, 10, False, 1)
        box.set_id(42)
        assert box.id == 42

    def test_is_hole_true(self):
        box = Boxface(0, 0, 10, 10, True, 1)
        assert box.is_hole() is True

    def test_repr(self):
        box = Boxface(0, 0, 10, 10, False, 7)
        assert repr(box) == "7"

    def test_center_calculation_with_negative_coords(self):
        box = Boxface(-10, -20, -2, -4, False, 3)
        assert box.xcenter == -6
        assert box.ycenter == -12

    def test_center_calculation_with_odd_distance(self):
        box = Boxface(0, 0, 11, 9, False, 4)
        assert box.xcenter == 5
        assert box.ycenter == 4

    def test_default_is_hole_when_private_name_collision_ignored(self):
        # __is_hole name-mangling protects the attribute; public access goes via is_hole().
        box = Boxface(0, 0, 10, 10, False, 1)
        # A public attribute 'is_hole' could accidentally be set; ensure behavior is consistent.
        assert box.is_hole() is False
