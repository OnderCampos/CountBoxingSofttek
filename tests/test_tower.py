import pytest
import math
from unittest.mock import patch, MagicMock
from tower import Tower, Side
from box_face import Boxface
from level import Level


class TestSide:
    """Unit tests for the Side helper class."""

    def test_add_level(self):
        side = Side()
        level = Level()
        side.add_level(level)
        assert side.levels == [level]

    def test_sort_orders_by_y_center(self):
        side = Side()
        top = Level()
        top.y1 = 0
        top.y2 = 10
        bottom = Level()
        bottom.y1 = 20
        bottom.y2 = 30
        side.add_level(bottom)
        side.add_level(top)
        side.sort()
        assert side.levels == [top, bottom]


class TestTowerAddSide:
    """Unit tests for Tower.add_side clustering logic."""

    @patch("tower.kmeans1")
    def test_add_side_front(self, mock_kmeans1):
        tower = Tower(levels=1)
        box = Boxface(0, 5, 10, 15, False, 1)
        mock_kmeans1.return_value = ([0], [10])
        tower.add_side("front", [box], "dummy.jpg")
        assert tower.front is not None
        assert len(tower.front.levels) == 1
        assert tower.front.levels[0].boxes == [box]

    @patch("tower.kmeans1")
    def test_add_side_right(self, mock_kmeans1):
        tower = Tower(levels=1)
        box = Boxface(0, 5, 10, 15, False, 1)
        mock_kmeans1.return_value = ([0], [10])
        tower.add_side("right", [box], "dummy.jpg")
        assert tower.right is not None

    @patch("tower.kmeans1")
    def test_add_side_back(self, mock_kmeans1):
        tower = Tower(levels=1)
        box = Boxface(0, 5, 10, 15, False, 1)
        mock_kmeans1.return_value = ([0], [10])
        tower.add_side("back", [box], "dummy.jpg")
        assert tower.back is not None

    @patch("tower.kmeans1")
    def test_add_side_left(self, mock_kmeans1):
        tower = Tower(levels=1)
        box = Boxface(0, 5, 10, 15, False, 1)
        mock_kmeans1.return_value = ([0], [10])
        tower.add_side("left", [box], "dummy.jpg")
        assert tower.left is not None

    @patch("tower.kmeans1")
    def test_add_side_unknown_name_ignored(self, mock_kmeans1):
        tower = Tower(levels=1)
        box = Boxface(0, 5, 10, 15, False, 1)
        mock_kmeans1.return_value = ([0], [10])
        tower.add_side("top", [box], "dummy.jpg")
        assert tower.front is None
        assert tower.right is None
        assert tower.back is None
        assert tower.left is None

    @patch("tower.kmeans1")
    def test_add_side_creates_multiple_levels(self, mock_kmeans1):
        tower = Tower(levels=2)
        low = Boxface(0, 0, 10, 10, False, 1)
        high = Boxface(0, 100, 10, 110, False, 2)
        # low gets label 0, high gets label 1
        mock_kmeans1.return_value = ([0, 1], [5, 105])
        tower.add_side("front", [low, high], "dummy.jpg")
        assert tower.front is not None
        assert len(tower.front.levels) == 2

    @patch("tower.kmeans1")
    def test_add_side_levels_sorted(self, mock_kmeans1):
        tower = Tower(levels=1)
        boxes = [
            Boxface(0, 20, 10, 30, False, 1),
            Boxface(0, 0, 10, 10, False, 2),
        ]
        mock_kmeans1.return_value = ([0, 0], [10])
        tower.add_side("back", boxes, "dummy.jpg")
        y_centers = [level.getYcenter() for level in tower.back.levels]
        assert y_centers == sorted(y_centers)


class TestTowerInit:
    """Unit tests for Tower initialization."""

    def test_init_defaults(self):
        tower = Tower(levels=3)
        assert tower.front is None
        assert tower.right is None
        assert tower.back is None
        assert tower.left is None
        assert tower.levels_num == 3
