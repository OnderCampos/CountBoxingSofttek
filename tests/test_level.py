import math
import pytest
from level import Level
from box_face import Boxface


class TestLevel:
    def test_add_box_updates_boundaries(self):
        level = Level()
        level.add_box(Boxface(10, 20, 30, 40, False, 1))
        assert level.x1 == 10
        assert level.y1 == 20
        assert level.x2 == 30
        assert level.y2 == 40

    def test_add_multiple_boxes_expands_boundaries(self):
        level = Level()
        level.add_box(Boxface(10, 20, 30, 40, False, 1))
        level.add_box(Boxface(5, 15, 35, 45, False, 2))
        assert level.x1 == 5
        assert level.y1 == 15
        assert level.x2 == 35
        assert level.y2 == 45

    def test_getYcenter(self):
        level = Level()
        level.add_box(Boxface(0, 10, 20, 30, False, 1))
        assert level.getYcenter() == 20

    def test_sort_orders_by_ycenter(self):
        level = Level()
        bottom = Boxface(0, 100, 10, 110, False, 1)
        top = Boxface(0, 0, 10, 10, False, 2)
        mid = Boxface(0, 50, 10, 60, False, 3)
        level.add_box(bottom)
        level.add_box(top)
        level.add_box(mid)
        level.sort()
        assert [b.id for b in level.boxes] == [2, 3, 1]

    def test_sort_stable_for_equal_ycenter(self):
        """Level.sort uses ycenter; for equal y ranges the original insertion order is preserved (stable sort)."""
        level = Level()
        a = Boxface(50, 0, 60, 10, False, 1)
        b = Boxface(0, 0, 10, 10, False, 2)
        level.add_box(a)
        level.add_box(b)
        level.sort()
        # Both boxes have the same ycenter; Python's sorted is stable, so [a, b] remains.
        assert [b.id for b in level.boxes] == [1, 2]

    def test_empty_level_boundaries(self):
        level = Level()
        assert level.x1 == math.inf
        assert level.x2 == -math.inf
        assert level.y1 == math.inf
        assert level.y2 == -math.inf

    def test_repr(self):
        level = Level()
        level.add_box(Boxface(0, 0, 10, 10, False, 5))
        assert repr(level) == "[5]"
