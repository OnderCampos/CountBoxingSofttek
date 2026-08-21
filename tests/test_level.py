import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import math
from level import Level
from box_face import Boxface


def make_face(x1=0, y1=0, x2=10, y2=10, is_hole=False, id=1):
    return Boxface(x1, y1, x2, y2, is_hole, id)


def test_level_initial_state():
    level = Level()
    assert level.boxes == []
    assert level.x1 == math.inf
    assert level.x2 == -math.inf
    assert level.y1 == math.inf
    assert level.y2 == -math.inf


def test_level_add_box_updates_bounds():
    level = Level()
    level.add_box(make_face(10, 20, 30, 40))
    assert level.x1 == 10
    assert level.y1 == 20
    assert level.x2 == 30
    assert level.y2 == 40
    level.add_box(make_face(5, 15, 35, 45))
    assert level.x1 == 5
    assert level.y1 == 15
    assert level.x2 == 35
    assert level.y2 == 45


def test_level_getYcenter():
    level = Level()
    level.add_box(make_face(0, 0, 10, 20))
    assert level.getYcenter() == 10


def test_level_sort_orders_by_ycenter():
    level = Level()
    box_top = make_face(0, 0, 10, 10, id=1)
    box_bottom = make_face(0, 20, 10, 30, id=2)
    level.add_box(box_bottom)
    level.add_box(box_top)
    level.sort()
    assert level.boxes[0].id == 1
    assert level.boxes[1].id == 2


def test_level_repr_shows_boxes():
    level = Level()
    box = make_face(id=7)
    level.add_box(box)
    assert "7" in repr(level)
