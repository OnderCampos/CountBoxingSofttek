import math
import pytest
from level import Level
from box_face import Boxface


class TestLevel:
    def test_initial_bounds(self):
        level = Level()
        assert level.x1 == math.inf
        assert level.y1 == math.inf
        assert level.x2 == -math.inf
        assert level.y2 == -math.inf
        assert level.boxes == []

    def test_add_box_updates_bounds(self):
        level = Level()
        box = Boxface(10, 20, 30, 40, False, 1)
        level.add_box(box)
        assert level.x1 == 10
        assert level.y1 == 20
        assert level.x2 == 30
        assert level.y2 == 40
        assert level.boxes == [box]

    def test_add_multiple_boxes(self):
        level = Level()
        b1 = Boxface(100, 100, 200, 200, False, 1)
        b2 = Boxface(50, 150, 150, 250, False, 2)
        level.add_box(b1)
        level.add_box(b2)
        assert level.x1 == 50
        assert level.y1 == 100
        assert level.x2 == 200
        assert level.y2 == 250

    def test_getYcenter(self):
        level = Level()
        level.add_box(Boxface(0, 10, 20, 30, False, 1))
        assert level.getYcenter() == 20

    def test_sort_orders_by_ycenter(self):
        level = Level()
        top = Boxface(0, 0, 10, 10, False, 1)
        bottom = Boxface(0, 50, 10, 60, False, 2)
        middle = Boxface(0, 25, 10, 35, False, 3)
        level.add_box(top)
        level.add_box(bottom)
        level.add_box(middle)
        level.sort()
        assert [box.id for box in level.boxes] == [1, 3, 2]

    def test_repr(self):
        level = Level()
        box = Boxface(0, 0, 10, 10, False, 9)
        level.add_box(box)
        assert repr(level) == "[9]"
