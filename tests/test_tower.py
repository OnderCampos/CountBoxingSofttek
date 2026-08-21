import pytest
from unittest import mock

from tower import Tower, Side
from level import Level
from box_face import Boxface


class TestSide:
    def test_add_level(self):
        side = Side()
        level = Level()
        side.add_level(level)
        assert side.levels == [level]

    def test_sort_levels_by_y_center(self):
        side = Side()
        low = Level()
        low.add_box(Boxface(0, 100, 10, 110, False, 1))
        high = Level()
        high.add_box(Boxface(0, 0, 10, 10, False, 2))
        side.add_level(low)
        side.add_level(high)
        side.sort()
        assert side.levels[0] == high
        assert side.levels[1] == low


class TestTowerAddSide:
    def make_face(self, x1, y1, x2, y2, is_hole=False, box_id=1):
        return Boxface(x1, y1, x2, y2, is_hole, box_id)

    @mock.patch("tower.kmeans1")
    def test_add_side_front_assigns_to_tower_front(self, mock_kmeans1):
        mock_kmeans1.return_value = ([0, 0, 0], [50.0])
        tower = Tower(levels=1)
        faces = [
            self.make_face(0, 40, 10, 60, box_id=1),
            self.make_face(20, 40, 30, 60, box_id=2),
        ]
        tower.add_side("front", faces, "dummy.jpg")
        assert tower.front is not None
        assert tower.right is None
        assert len(tower.front.levels) == 1

    @mock.patch("tower.kmeans1")
    def test_add_side_all_sides(self, mock_kmeans1):
        mock_kmeans1.return_value = ([0, 0], [50.0])
        tower = Tower(levels=1)
        for side_name in ["front", "right", "back", "left"]:
            tower.add_side(side_name, [self.make_face(0, 40, 10, 60, box_id=1)], "dummy.jpg")
        assert tower.front is not None
        assert tower.right is not None
        assert tower.back is not None
        assert tower.left is not None

    @mock.patch("tower.kmeans1")
    def test_add_side_creates_levels_from_labels(self, mock_kmeans1):
        mock_kmeans1.return_value = ([0, 1, 0], [45.0, 100.0])
        tower = Tower(levels=2)
        faces = [
            self.make_face(0, 40, 10, 50, box_id=1),
            self.make_face(0, 90, 10, 110, box_id=2),
            self.make_face(0, 45, 10, 55, box_id=3),
        ]
        tower.add_side("front", faces, "dummy.jpg")
        assert len(tower.front.levels) == 2

    def test_tower_initial_sides_are_none(self):
        tower = Tower(levels=3)
        assert tower.front is None
        assert tower.right is None
        assert tower.back is None
        assert tower.left is None
        assert tower.levels_num == 3
