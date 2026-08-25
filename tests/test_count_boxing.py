"""
Unit tests for the core modules of CountBoxingSofttek.

NOTE: The repository contains Python source code for counting boxes in tower
images. The requested task "Membership Card Scan Login on Mobile" does not
exist in this codebase. Therefore, these tests target the actual core modules
present in the repository (Boxface, Level, kmeans, and the tower algorithms)
and verify the business logic implied by the provided user stories.

External computer-vision/plotting dependencies (cv2, numpy, matplotlib) are not
required for the unit tests and are mocked before importing the modules under
test.
"""

import sys
from unittest.mock import MagicMock

# Mock heavy/optional dependencies so the tests can run without cv2/numpy/etc.
for _mod in (
    "cv2",
    "numpy",
    "matplotlib",
    "matplotlib.pyplot",
):
    sys.modules[_mod] = MagicMock()

import json
import math
import unittest
from unittest.mock import patch

from box_face import Boxface
from level import Level
from kmeans import distance, kmeans, kmeans1, mean, points_in_centroids, separate_into_bins
from algorithms.algorithm1 import Algorithm1
from algorithms.algorithm2 import Algorithm2
from tower import Side, Tower


class TestBoxface(unittest.TestCase):
    """Tests for box_face.Boxface (User Story #1 / AC-2)."""

    def test_boxface_creation_and_getters(self):
        face = Boxface(x1=10, y1=20, x2=30, y2=40, is_hole=False, id=1)
        self.assertEqual(face.x1, 10)
        self.assertEqual(face.y1, 20)
        self.assertEqual(face.x2, 30)
        self.assertEqual(face.y2, 40)
        self.assertEqual(face.id, 1)
        self.assertFalse(face.is_hole())

    def test_boxface_center_calculation(self):
        face = Boxface(x1=10, y1=20, x2=30, y2=50, is_hole=True, id=2)
        # __cal_center uses v1 + abs(v1 - v2) // 2
        self.assertEqual(face.xcenter, 10 + abs(10 - 30) // 2)
        self.assertEqual(face.ycenter, 20 + abs(20 - 50) // 2)
        self.assertEqual(face.get_center(), (face.xcenter, face.ycenter))

    def test_boxface_is_hole_property_is_private(self):
        face = Boxface(x1=0, y1=0, x2=10, y2=10, is_hole=True, id=3)
        self.assertTrue(face.is_hole())
        # The private attribute should not be directly accessible.
        with self.assertRaises(AttributeError):
            _ = face.__is_hole

    def test_boxface_set_id_and_repr(self):
        face = Boxface(x1=0, y1=0, x2=10, y2=10, is_hole=False, id=5)
        face.set_id(99)
        self.assertEqual(face.id, 99)
        self.assertEqual(repr(face), "99")


class TestLevel(unittest.TestCase):
    """Tests for level.Level (User Story #2 grouping/ordering support)."""

    def test_empty_level_bounds(self):
        level = Level()
        self.assertEqual(level.x1, math.inf)
        self.assertEqual(level.y1, math.inf)
        self.assertEqual(level.x2, -math.inf)
        self.assertEqual(level.y2, -math.inf)
        self.assertEqual(level.boxes, [])

    def test_add_box_updates_bounds(self):
        level = Level()
        level.add_box(Boxface(x1=10, y1=20, x2=30, y2=40, is_hole=False, id=1))
        level.add_box(Boxface(x1=5, y1=25, x2=35, y2=45, is_hole=False, id=2))
        self.assertEqual(level.x1, 5)
        self.assertEqual(level.y1, 20)
        self.assertEqual(level.x2, 35)
        self.assertEqual(level.y2, 45)
        self.assertEqual(len(level.boxes), 2)

    def test_get_ycenter(self):
        level = Level()
        level.add_box(Boxface(x1=0, y1=10, x2=10, y2=20, is_hole=False, id=1))
        level.add_box(Boxface(x1=0, y1=12, x2=10, y2=18, is_hole=False, id=2))
        self.assertEqual(level.y1, 10)
        self.assertEqual(level.y2, 20)
        self.assertEqual(level.getYcenter(), 10 + abs(10 - 20) // 2)

    def test_level_sort_orders_by_ycenter(self):
        level = Level()
        b1 = Boxface(x1=0, y1=50, x2=10, y2=60, is_hole=False, id=1)
        b2 = Boxface(x1=0, y1=10, x2=10, y2=20, is_hole=False, id=2)
        b3 = Boxface(x1=0, y1=30, x2=10, y2=40, is_hole=False, id=3)
        for b in (b1, b2, b3):
            level.add_box(b)
        level.sort()
        self.assertEqual([box.id for box in level.boxes], [2, 3, 1])


class TestKmeans(unittest.TestCase):
    """Tests for kmeans helpers."""

    def test_distance(self):
        self.assertAlmostEqual(distance([0, 0], [3, 4]), 5.0)
        self.assertAlmostEqual(distance([1, 2, 3], [4, 5, 6]), math.sqrt(27))

    def test_mean(self):
        self.assertEqual(mean([[1, 2], [3, 4], [5, 6]]), [3.0, 4.0])

    def test_separate_into_bins(self):
        data = [0, 1, 2, 10, 11, 12, 20, 21, 22]
        means = separate_into_bins(data, 3)
        self.assertEqual(len(means), 3)
        self.assertAlmostEqual(means[0], 1.0)
        self.assertAlmostEqual(means[1], 11.0)
        self.assertAlmostEqual(means[2], 21.0)

    def test_kmeans_basic_clustering(self):
        data = [[0], [1], [2], [10], [11], [12]]
        labels, centroids = kmeans(data, 2, max_iters=100)
        self.assertEqual(len(labels), len(data))
        self.assertEqual(len(centroids), 2)
        # Points from the same cluster should share a label.
        self.assertEqual(labels[0], labels[1])
        self.assertEqual(labels[0], labels[2])
        self.assertEqual(labels[3], labels[4])
        self.assertEqual(labels[3], labels[5])
        self.assertNotEqual(labels[0], labels[3])

    def test_kmeans1_basic_clustering(self):
        data = [0, 1, 2, 10, 11, 12, 20, 21, 22]
        labels, centroids = kmeans1(data, 3, max_iters=200)
        self.assertEqual(len(labels), len(data))
        self.assertEqual(len(centroids), 3)
        # Verify the three natural groups share labels.
        self.assertEqual(labels[0], labels[1])
        self.assertEqual(labels[0], labels[2])
        self.assertEqual(labels[3], labels[4])
        self.assertEqual(labels[3], labels[5])
        self.assertEqual(labels[6], labels[7])
        self.assertEqual(labels[6], labels[8])

    def test_points_in_centroids(self):
        data = [1, 2, 10, 11]
        labels = [0, 0, 1, 1]
        result = points_in_centroids(data, labels, [5, 15])
        self.assertEqual(result, {0: [1, 2], 1: [10, 11]})


class TestAlgorithm1(unittest.TestCase):
    """Tests for algorithms/algorithm1.py (User Stories #1-#3)."""

    def test_create_faces_default_non_hole(self):
        boxes = [{"x1": 0, "y1": 0, "x2": 10, "y2": 10}]
        faces = Algorithm1()._Algorithm1__create_faces(boxes)
        self.assertEqual(len(faces), 1)
        self.assertFalse(faces[0].is_hole())
        self.assertEqual(faces[0].id, 1)

    def test_create_faces_preserves_hole_flag(self):
        boxes = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": True},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": False},
        ]
        faces = Algorithm1()._Algorithm1__create_faces(boxes)
        self.assertTrue(faces[0].is_hole())
        self.assertFalse(faces[1].is_hole())
        self.assertEqual(faces[1].id, 2)

    def test_separate_in_lines_groups_intersecting_y(self):
        # Two horizontal lines: y ~15 and y ~45
        faces = [
            Boxface(x1=10, y1=10, x2=20, y2=20, is_hole=False, id=1),
            Boxface(x1=30, y1=12, x2=40, y2=18, is_hole=False, id=2),
            Boxface(x1=5, y1=40, x2=15, y2=50, is_hole=False, id=3),
            Boxface(x1=50, y1=42, x2=60, y2=48, is_hole=False, id=4),
        ]
        lines = Algorithm1().separate_in_lines(faces)
        self.assertEqual(len(lines), 2)
        # Lower line first after sorting by cast_line.
        self.assertEqual([f.id for f in lines[0]["faces"]], [1, 2])
        self.assertEqual([f.id for f in lines[1]["faces"]], [3, 4])

    def test_separate_in_lines_sorts_left_to_right(self):
        faces = [
            Boxface(x1=30, y1=10, x2=40, y2=20, is_hole=False, id=1),
            Boxface(x1=5, y1=12, x2=15, y2=18, is_hole=False, id=2),
            Boxface(x1=18, y1=11, x2=28, y2=19, is_hole=False, id=3),
        ]
        lines = Algorithm1().separate_in_lines(faces)
        self.assertEqual(len(lines), 1)
        self.assertEqual([f.id for f in lines[0]["faces"]], [2, 3, 1])

    def test_count_corner_holes(self):
        algo = Algorithm1()
        line_a = {"faces": [Boxface(0, 0, 10, 10, False, 1), Boxface(20, 0, 30, 10, True, 2)]}
        line_b = {"faces": [Boxface(0, 0, 10, 10, True, 3), Boxface(20, 0, 30, 10, False, 4)]}
        self.assertEqual(algo.count_corner_holes(line_a, line_b), 1)
        self.assertEqual(algo.count_corner_holes(line_b, line_a), 0)

    def test_count_inner_holes(self):
        algo = Algorithm1()
        line = {
            "faces": [
                Boxface(0, 0, 10, 10, False, 1),
                Boxface(20, 0, 30, 10, True, 2),
                Boxface(40, 0, 50, 10, True, 3),
                Boxface(60, 0, 70, 10, False, 4),
            ]
        }
        self.assertEqual(algo.count_inner_holes(line), 2)

    def _make_side(self, count, y_offset, hole_indices=None):
        hole_indices = hole_indices or set()
        faces = []
        for i in range(count):
            x1 = i * 10
            faces.append(
                Boxface(
                    x1=x1,
                    y1=y_offset,
                    x2=x1 + 8,
                    y2=y_offset + 8,
                    is_hole=(i in hole_indices),
                    id=i + 1,
                )
            )
        return faces

    def test_solve_counts_boxes_and_holes(self):
        algo = Algorithm1()
        # 2 lines x 3 front boxes x 2 right boxes = 12 total.
        front = self._make_side(3, 10) + self._make_side(3, 30)
        right = self._make_side(2, 10) + self._make_side(2, 30)
        back = self._make_side(3, 10) + self._make_side(3, 30)
        left = self._make_side(3, 10) + self._make_side(3, 30)
        algo._Algorithm1__get_sides = lambda _path: (front, right, back, left)
        self.assertEqual(algo.solve("dummy_tower"), 12)

    def test_solve_subtracts_holes(self):
        algo = Algorithm1()
        # One line only: 3x3=9 boxes. Put a corner hole on the join between
        # front/right (last front face, first right face).
        front = self._make_side(3, 10, hole_indices={2})
        right = self._make_side(3, 10, hole_indices={0})
        back = self._make_side(3, 10)
        left = self._make_side(3, 10)
        algo._Algorithm1__get_sides = lambda _path: (front, right, back, left)
        # One corner hole is counted once (front/right pair).
        self.assertEqual(algo.solve("dummy_tower"), 8)

    def test_solve_subtracts_inner_holes(self):
        algo = Algorithm1()
        front = self._make_side(4, 10, hole_indices={1, 2})
        right = self._make_side(2, 10)
        back = self._make_side(4, 10)
        left = self._make_side(4, 10)
        algo._Algorithm1__get_sides = lambda _path: (front, right, back, left)
        # 4*2 = 8 boxes. Inner holes only in front line = 2 holes.
        self.assertEqual(algo.solve("dummy_tower"), 6)

    def test_solve_unequal_line_counts_still_returns_product(self):
        algo = Algorithm1()
        front = self._make_side(3, 10)  # 1 line
        right = self._make_side(2, 10) + self._make_side(2, 30)  # 2 lines
        back = self._make_side(3, 10)
        left = self._make_side(3, 10)
        algo._Algorithm1__get_sides = lambda _path: (front, right, back, left)
        # Holes verification skipped, but product computed.
        self.assertEqual(algo.solve("dummy_tower"), 3 * 2)

    @patch("builtins.open", unittest.mock.mock_open(read_data="[]"))
    @patch("json.load", return_value=[])
    def test_get_sides_opens_four_json_files(self, mock_json_load):
        algo = Algorithm1()
        front, right, back, left = algo._Algorithm1__get_sides("towers/tower1")
        self.assertEqual(front, [])
        self.assertEqual(right, [])
        self.assertEqual(back, [])
        self.assertEqual(left, [])
        self.assertEqual(mock_json_load.call_count, 4)


class TestAlgorithm2(unittest.TestCase):
    """Tests for algorithms/algorithm2.py (alternative counting approach)."""

    def test_separate_in_columns_groups_intersecting_x(self):
        level = Level()
        # Three boxes: first two overlap in x, third is separate. Boxes are
        # wide enough that their x-ranges intersect each other's centers.
        level.add_box(Boxface(x1=10, y1=0, x2=30, y2=10, is_hole=False, id=1))
        level.add_box(Boxface(x1=15, y1=0, x2=35, y2=10, is_hole=False, id=2))
        level.add_box(Boxface(x1=60, y1=0, x2=80, y2=10, is_hole=False, id=3))
        columns = Algorithm2().separate_in_columns(level)
        self.assertEqual(len(columns), 2)
        # First column should contain the two overlapping boxes sorted by x1.
        self.assertEqual([f.id for f in columns[0]["faces"]], [1, 2])
        self.assertEqual([f.id for f in columns[1]["faces"]], [3])

    def test_solve_counts_non_hole_faces(self):
        algo = Algorithm2()

        def make_box(x1, y1, x2, y2, is_hole=False):
            return Boxface(x1, y1, x2, y2, is_hole, id=1)

        # Algorithm2 uses Tower(levels=3); provide three distinct y bands and
        # two x-separated columns to satisfy kmeans1 and the column slicing.
        front, right, back, left = [], [], [], []
        for y in (5, 25, 45):
            front.extend([make_box(0, y, 8, y + 8, False), make_box(20, y, 28, y + 8, False)])
            right.extend([make_box(0, y, 8, y + 8, False), make_box(20, y, 28, y + 8, False)])
            back.extend([make_box(0, y, 8, y + 8, False), make_box(20, y, 28, y + 8, False)])
            left.extend([make_box(0, y, 8, y + 8, False), make_box(20, y, 28, y + 8, False)])

        algo._Algorithm2__get_sides = lambda _path: (front, right, back, left)

        # Per level: front 2 cols * 1 box = 2; right/back skip first col => 1 each;
        # left skips first+last col => 0. Three levels => 3 * 4 = 12.
        self.assertEqual(algo.solve("dummy_tower"), 12)

    def test_solve_ignores_hole_faces(self):
        algo = Algorithm2()

        def make_box(x1, y1, x2, y2, is_hole=False):
            return Boxface(x1, y1, x2, y2, is_hole, id=1)

        front, right, back, left = [], [], [], []
        for y in (5, 25, 45):
            front.extend([make_box(0, y, 8, y + 8, False), make_box(20, y, 28, y + 8, True)])
            right.extend([make_box(0, y, 8, y + 8, False), make_box(20, y, 28, y + 8, False)])
            back.extend([make_box(0, y, 8, y + 8, False), make_box(20, y, 28, y + 8, False)])
            left.extend([make_box(0, y, 8, y + 8, False), make_box(20, y, 28, y + 8, False)])

        algo._Algorithm2__get_sides = lambda _path: (front, right, back, left)

        # Per level: front only first col non-hole => 1; right first col => 1;
        # back first col => 1; left no cols => 0. Three levels => 3 * 3 = 9.
        self.assertEqual(algo.solve("dummy_tower"), 9)


class TestTower(unittest.TestCase):
    """Tests for tower.Tower side/level construction (User Story #2)."""

    def test_tower_initialization(self):
        tower = Tower(levels=3)
        self.assertIsNone(tower.front)
        self.assertIsNone(tower.right)
        self.assertIsNone(tower.back)
        self.assertIsNone(tower.left)
        self.assertEqual(tower.levels_num, 3)

    def test_add_side_groups_boxes_into_levels(self):
        tower = Tower(levels=2)
        boxes = [
            Boxface(x1=0, y1=10, x2=10, y2=20, is_hole=False, id=1),
            Boxface(x1=20, y1=12, x2=30, y2=18, is_hole=False, id=2),
            Boxface(x1=0, y1=50, x2=10, y2=60, is_hole=False, id=3),
            Boxface(x1=20, y1=52, x2=30, y2=58, is_hole=False, id=4),
        ]
        tower.add_side("front", boxes, "fake/path.jpg")
        self.assertIsNotNone(tower.front)
        self.assertEqual(len(tower.front.levels), 2)
        lower_level = tower.front.levels[0]
        upper_level = tower.front.levels[1]
        self.assertEqual([b.id for b in lower_level.boxes], [1, 2])
        self.assertEqual([b.id for b in upper_level.boxes], [3, 4])


if __name__ == "__main__":
    unittest.main(verbosity=2)
