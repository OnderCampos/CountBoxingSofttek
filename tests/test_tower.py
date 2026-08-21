import math
import pytest
from unittest.mock import patch
from tower import Side, Tower
from level import Level
from box_face import Boxface


class TestSide:
    def test_add_and_sort_levels(self):
        side = Side()
        level_top = Level()
        level_top.add_box(Boxface(0, 0, 10, 10, False, 1))
        level_bottom = Level()
        level_bottom.add_box(Boxface(0, 100, 10, 110, False, 2))
        side.add_level(level_bottom)
        side.add_level(level_top)
        side.sort()
        assert side.levels == [level_top, level_bottom]


class TestTower:
    def test_constructor_initializes_sides_none(self):
        tower = Tower(levels=3)
        assert tower.front is None
        assert tower.right is None
        assert tower.back is None
        assert tower.left is None
        assert tower.levels_num == 3

    @patch('tower.kmeans1')
    @patch('tower.cv2.imread')
    def test_add_side_front_assigns_side(self, mock_imread, mock_kmeans1):
        mock_kmeans1.return_value = ([0, 0, 1, 1], [100, 300])
        mock_imread.return_value = None
        tower = Tower(levels=2)
        faces = [
            Boxface(0, 80, 10, 120, False, 1),
            Boxface(0, 90, 10, 110, False, 2),
            Boxface(0, 280, 10, 320, False, 3),
            Boxface(0, 290, 10, 310, False, 4),
        ]
        tower.add_side('front', faces, 'fake/path.jpg')
        assert tower.front is not None
        assert len(tower.front.levels) == 2
        assert isinstance(tower.front.levels[0], Level)

    @patch('tower.kmeans1')
    @patch('tower.cv2.imread')
    def test_add_side_right_assigns_side(self, mock_imread, mock_kmeans1):
        mock_kmeans1.return_value = ([0, 1], [50, 150])
        mock_imread.return_value = None
        tower = Tower(levels=2)
        faces = [Boxface(0, 40, 10, 60, False, 1), Boxface(0, 140, 10, 160, False, 2)]
        tower.add_side('right', faces, 'fake/path.jpg')
        assert tower.right is not None

    @patch('tower.kmeans1')
    @patch('tower.cv2.imread')
    def test_add_side_back_assigns_side(self, mock_imread, mock_kmeans1):
        mock_kmeans1.return_value = ([0, 1], [50, 150])
        mock_imread.return_value = None
        tower = Tower(levels=2)
        faces = [Boxface(0, 40, 10, 60, False, 1), Boxface(0, 140, 10, 160, False, 2)]
        tower.add_side('back', faces, 'fake/path.jpg')
        assert tower.back is not None

    @patch('tower.kmeans1')
    @patch('tower.cv2.imread')
    def test_add_side_left_assigns_side(self, mock_imread, mock_kmeans1):
        mock_kmeans1.return_value = ([0, 1], [50, 150])
        mock_imread.return_value = None
        tower = Tower(levels=2)
        faces = [Boxface(0, 40, 10, 60, False, 1), Boxface(0, 140, 10, 160, False, 2)]
        tower.add_side('left', faces, 'fake/path.jpg')
        assert tower.left is not None

    @patch('tower.kmeans1')
    @patch('tower.cv2.imread')
    def test_add_side_levels_are_sorted_by_y_center(self, mock_imread, mock_kmeans1):
        mock_kmeans1.return_value = ([1, 1, 0, 0], [300, 100])
        mock_imread.return_value = None
        tower = Tower(levels=2)
        faces = [
            Boxface(0, 280, 10, 320, False, 3),
            Boxface(0, 290, 10, 310, False, 4),
            Boxface(0, 80, 10, 120, False, 1),
            Boxface(0, 90, 10, 110, False, 2),
        ]
        tower.add_side('front', faces, 'fake/path.jpg')
        centers = [level.getYcenter() for level in tower.front.levels]
        assert centers == sorted(centers)
