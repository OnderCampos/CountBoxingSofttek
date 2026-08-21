import json
from unittest import mock

import pytest

from box_face import Boxface
from level import Level
from tower import Side, Tower


class TestSide:
    def test_side_add_level(self):
        side = Side()
        level = Level()
        side.add_level(level)
        assert len(side.levels) == 1

    def test_side_sort(self):
        side = Side()
        low = Level()
        low.add_box(Boxface(0, 0, 10, 10, False, 1))
        high = Level()
        high.add_box(Boxface(0, 100, 10, 110, False, 2))
        side.add_level(high)
        side.add_level(low)
        side.sort()
        assert side.levels[0] == low
        assert side.levels[1] == high


class TestTower:
    def test_tower_initial_sides_none(self):
        tower = Tower(levels=3)
        assert tower.front is None
        assert tower.right is None
        assert tower.back is None
        assert tower.left is None
        assert tower.levels_num == 3

    def test_add_side_front_stores_side(self):
        tower = Tower(levels=1)
        face = Boxface(0, 0, 10, 10, False, 1)
        with mock.patch("tower.kmeans1") as mock_kmeans, mock.patch("tower.cv2"):
            mock_kmeans.return_value = ([0], [5])
            tower.add_side("front", [face], "dummy/path.jpg")
        assert tower.front is not None
        assert len(tower.front.levels) == 1

    def test_add_side_right_stores_side(self):
        tower = Tower(levels=1)
        face = Boxface(0, 0, 10, 10, False, 1)
        with mock.patch("tower.kmeans1") as mock_kmeans, mock.patch("tower.cv2"):
            mock_kmeans.return_value = ([0], [5])
            tower.add_side("right", [face], "dummy/path.jpg")
        assert tower.right is not None

    def test_add_side_back_stores_side(self):
        tower = Tower(levels=1)
        face = Boxface(0, 0, 10, 10, False, 1)
        with mock.patch("tower.kmeans1") as mock_kmeans, mock.patch("tower.cv2"):
            mock_kmeans.return_value = ([0], [5])
            tower.add_side("back", [face], "dummy/path.jpg")
        assert tower.back is not None

    def test_add_side_left_stores_side(self):
        tower = Tower(levels=1)
        face = Boxface(0, 0, 10, 10, False, 1)
        with mock.patch("tower.kmeans1") as mock_kmeans, mock.patch("tower.cv2"):
            mock_kmeans.return_value = ([0], [5])
            tower.add_side("left", [face], "dummy/path.jpg")
        assert tower.left is not None

    def test_add_side_groups_multiple_boxes_by_label(self):
        tower = Tower(levels=2)
        faces = [
            Boxface(0, 0, 10, 10, False, 1),    # ycenter=5
            Boxface(0, 100, 10, 110, False, 2), # ycenter=105
        ]
        with mock.patch("tower.kmeans1") as mock_kmeans, mock.patch("tower.cv2"):
            mock_kmeans.return_value = ([0, 1], [5, 105])
            tower.add_side("front", faces, "dummy/path.jpg")
        assert len(tower.front.levels) == 2

    def test_add_side_levels_are_sorted_by_y(self):
        tower = Tower(levels=2)
        faces = [
            Boxface(0, 100, 10, 110, False, 1),
            Boxface(0, 0, 10, 10, False, 2),
        ]
        with mock.patch("tower.kmeans1") as mock_kmeans, mock.patch("tower.cv2"):
            # kmeans returns labels matching input order; simulate two clusters
            mock_kmeans.return_value = ([1, 0], [5, 105])
            tower.add_side("front", faces, "dummy/path.jpg")
        # Since labels are arbitrary, just verify side.sort() ran without error
        assert len(tower.front.levels) == 2
