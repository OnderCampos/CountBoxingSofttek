import pytest
import math
from level import Level
from box_face import Boxface


class TestLevel:
    """Unit tests for the Level aggregation helper."""

    def test_empty_level_bounds(self):
        level = Level()
        assert level.boxes == []
        assert level.x1 == math.inf
        assert level.x2 == -math.inf
        assert level.y1 == math.inf
        assert level.y2 == -math.inf

    def test_add_box_updates_bounds(self):
        level = Level()
        level.add_box(Boxface(10, 20, 30, 40, False, 1))
        level.add_box(Boxface(5, 25, 35, 45, False, 2))
        assert level.x1 == 5
        assert level.y1 == 20
        assert level.x2 == 35
        assert level.y2 == 45
        assert len(level.boxes) == 2

    def test_getYcenter(self):
        level = Level()
        level.add_box(Boxface(10, 20, 30, 40, False, 1))
        assert level.getYcenter() == 20 + abs(20 - 40) // 2

    def test_sort_orders_boxes_by_vertical_center(self):
        level = Level()
        bottom = Boxface(0, 100, 10, 110, False, 1)
        top = Boxface(0, 0, 10, 10, False, 2)
        middle = Boxface(0, 50, 10, 60, False, 3)
        level.add_box(bottom)
        level.add_box(top)
        level.add_box(middle)
        level.sort()
        assert [box.id for box in level.boxes] == [2, 3, 1]

    def test_repr_contains_boxes(self):
        level = Level()
        level.add_box(Boxface(0, 0, 10, 10, False, 7))
        assert "7" in repr(level)
