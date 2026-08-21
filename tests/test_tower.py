import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from tower import Tower, Side
from level import Level
from box_face import Boxface


def make_face(x1=0, y1=0, x2=10, y2=10, is_hole=False, id=1):
    return Boxface(x1, y1, x2, y2, is_hole, id)


def test_tower_initializes_sides_none():
    tower = Tower(levels=3)
    assert tower.front is None
    assert tower.right is None
    assert tower.back is None
    assert tower.left is None
    assert tower.levels_num == 3


def test_side_add_level_and_sort():
    side = Side()
    level_low = Level()
    level_low.add_box(make_face(0, 20, 10, 30, id=1))
    level_high = Level()
    level_high.add_box(make_face(0, 0, 10, 10, id=2))
    side.add_level(level_low)
    side.add_level(level_high)
    side.sort()
    assert side.levels[0].boxes[0].id == 2
    assert side.levels[1].boxes[0].id == 1


def test_tower_add_side_creates_levels():
    tower = Tower(levels=2)
    faces = [
        make_face(0, 0, 10, 10, id=1),
        make_face(0, 100, 10, 110, id=2),
    ]
    # Provide a dummy image path; cv2.imread will fail silently in add_side
    # but the clustering still works.
    tower.add_side("front", faces, "/nonexistent/image.jpg")
    assert tower.front is not None
    assert len(tower.front.levels) == 2


def test_tower_add_side_assigns_front():
    tower = Tower(levels=2)
    tower.add_side("front", [make_face(0, 0, 10, 10), make_face(0, 100, 10, 110)], "/nonexistent/image.jpg")
    assert tower.front is not None
    assert tower.right is None


def test_tower_add_side_assigns_right():
    tower = Tower(levels=2)
    tower.add_side("right", [make_face(0, 0, 10, 10), make_face(0, 100, 10, 110)], "/nonexistent/image.jpg")
    assert tower.right is not None


def test_tower_add_side_assigns_back():
    tower = Tower(levels=2)
    tower.add_side("back", [make_face(0, 0, 10, 10), make_face(0, 100, 10, 110)], "/nonexistent/image.jpg")
    assert tower.back is not None


def test_tower_add_side_assigns_left():
    tower = Tower(levels=2)
    tower.add_side("left", [make_face(0, 0, 10, 10), make_face(0, 100, 10, 110)], "/nonexistent/image.jpg")
    assert tower.left is not None
