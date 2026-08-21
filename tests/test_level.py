import pytest
from level import Level
from box_face import Boxface


class TestLevel:
    def test_level_initial_bounds(self):
        level = Level()
        assert level.x1 == float("inf")
        assert level.x2 == -float("inf")
        assert level.y1 == float("inf")
        assert level.y2 == -float("inf")
        assert level.boxes == []

    def test_add_box_updates_bounds(self):
        level = Level()
        level.add_box(Boxface(10, 20, 30, 40, False, 1))
        assert level.x1 == 10
        assert level.y1 == 20
        assert level.x2 == 30
        assert level.y2 == 40

    def test_add_multiple_boxes_expands_bounds(self):
        level = Level()
        level.add_box(Boxface(0, 0, 10, 10, False, 1))
        level.add_box(Boxface(-5, -10, 20, 30, False, 2))
        assert level.x1 == -5
        assert level.y1 == -10
        assert level.x2 == 20
        assert level.y2 == 30

    def test_get_y_center(self):
        level = Level()
        level.add_box(Boxface(0, 0, 10, 20, False, 1))
        assert level.getYcenter() == 10

    def test_sort_orders_by_ycenter(self):
        level = Level()
        level.add_box(Boxface(0, 100, 10, 110, False, 1))
        level.add_box(Boxface(0, 0, 10, 10, False, 2))
        level.add_box(Boxface(0, 50, 10, 60, False, 3))
        level.sort()
        assert [box.id for box in level.boxes] == [2, 3, 1]

    def test_repr(self):
        level = Level()
        level.add_box(Boxface(0, 0, 10, 10, False, 5))
        assert repr(level) == "[5]"
