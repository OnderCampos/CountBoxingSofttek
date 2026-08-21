import pytest
from unittest import mock

from algorithms.algorithm2 import Algorithm2
from box_face import Boxface
from level import Level


class TestAlgorithm2UserStory1:
    """Algorithm2 also loads tower faces from JSON (User Story #1)."""

    @mock.patch("algorithms.algorithm2.json.load")
    def test_ac1_reads_four_json_files(self, mock_json_load):
        mock_json_load.side_effect = [
            [{"x1": 0, "y1": 0, "x2": 10, "y2": 10}],
            [{"x1": 10, "y1": 0, "x2": 20, "y2": 10}],
            [{"x1": 20, "y1": 0, "x2": 30, "y2": 10}],
            [{"x1": 30, "y1": 0, "x2": 40, "y2": 10}],
        ]
        alg = Algorithm2()
        with mock.patch("algorithms.algorithm2.open", mock.mock_open()) as mock_open:
            front, right, back, left = alg._Algorithm2__get_sides("towers/tower1")

        opened_files = [call.args[0] for call in mock_open.call_args_list]
        assert any("front.json" in f for f in opened_files)
        assert any("right.json" in f for f in opened_files)
        assert any("back.json" in f for f in opened_files)
        assert any("left.json" in f for f in opened_files)
        assert len(front) == len(right) == len(back) == len(left) == 1

    @mock.patch("algorithms.algorithm2.open", mock.mock_open())
    @mock.patch("algorithms.algorithm2.json.load")
    def test_ac2_boxface_conversion(self, mock_json_load):
        mock_json_load.return_value = [
            {"x1": 5, "y1": 6, "x2": 7, "y2": 8, "is_hole": True}
        ]
        alg = Algorithm2()
        front, *_ = alg._Algorithm2__get_sides("any/path")
        box = front[0]
        assert box.x1 == 5
        assert box.y1 == 6
        assert box.x2 == 7
        assert box.y2 == 8
        assert box.is_hole() is True
        assert box.id == 1


class TestAlgorithm2SeparateColumns:
    """Algorithm2 separates a level into vertical columns instead of horizontal lines."""

    def make_face(self, x1, y1, x2, y2, is_hole=False, box_id=1):
        return Boxface(x1, y1, x2, y2, is_hole, box_id)

    def test_separate_in_columns_groups_by_x_overlap(self):
        level = Level()
        level.add_box(self.make_face(0, 0, 10, 10, box_id=1))   # xcenter=5
        level.add_box(self.make_face(8, 20, 18, 30, box_id=2))   # xcenter=13
        level.add_box(self.make_face(4, 40, 12, 50, box_id=3))   # xcenter=8, overlaps first (4<5<12)

        alg = Algorithm2()
        columns = alg.separate_in_columns(level)
        assert len(columns) == 2

    def test_separate_in_columns_orders_left_to_right(self):
        level = Level()
        level.add_box(self.make_face(50, 0, 60, 10, box_id=1))
        level.add_box(self.make_face(0, 0, 10, 10, box_id=2))
        level.add_box(self.make_face(25, 0, 35, 10, box_id=3))

        alg = Algorithm2()
        columns = alg.separate_in_columns(level)
        # All non-overlapping in x, each in its own column, sorted by xcenter/x1
        ids = [col["faces"][0].id for col in columns]
        assert ids == [2, 3, 1]

    def test_separate_in_columns_empty_level(self):
        level = Level()
        alg = Algorithm2()
        columns = alg.separate_in_columns(level)
        assert columns == []


class TestAlgorithm2Solve:
    """End-to-end solve path for Algorithm2 using mocks."""

    def make_face(self, x1, y1, x2, y2, is_hole=False, box_id=1):
        return Boxface(x1, y1, x2, y2, is_hole, box_id)

    def make_level(self, boxes):
        level = Level()
        for box in boxes:
            level.add_box(box)
        return level

    @mock.patch("algorithms.algorithm2.Tower")
    @mock.patch("algorithms.algorithm2.json.load")
    def test_solve_counts_non_hole_faces(self, mock_json_load, mock_tower):
        mock_json_load.return_value = []
        alg = Algorithm2()

        tower_instance = mock_tower.return_value
        # One level per side, each with two non-overlapping boxes in x
        front_level = self.make_level([
            self.make_face(0, 0, 10, 10, is_hole=False, box_id=1),
            self.make_face(20, 0, 30, 10, is_hole=False, box_id=2),
        ])
        other_level = self.make_level([
            self.make_face(0, 0, 10, 10, is_hole=False, box_id=3),
            self.make_face(20, 0, 30, 10, is_hole=False, box_id=4),
        ])
        tower_instance.front.levels = [front_level]
        tower_instance.right.levels = [other_level]
        tower_instance.back.levels = [other_level]
        tower_instance.left.levels = [other_level]

        with mock.patch("algorithms.algorithm2.open", mock.mock_open()):
            result = alg.solve("any/path")
        # front columns count all non-holes: 2
        # right columns[1::] -> second column only: 1
        # back columns[1::] -> 1
        # left columns[1:-1] -> empty (only 2 columns => [1:-1] is empty)
        # total = 2 + 1 + 1 + 0 = 3
        assert result == 3

    @mock.patch("algorithms.algorithm2.Tower")
    @mock.patch("algorithms.algorithm2.json.load")
    def test_solve_skips_holes(self, mock_json_load, mock_tower):
        mock_json_load.return_value = []
        alg = Algorithm2()

        tower_instance = mock_tower.return_value
        front_level = self.make_level([
            self.make_face(0, 0, 10, 10, is_hole=True, box_id=1),
            self.make_face(20, 0, 30, 10, is_hole=False, box_id=2),
        ])
        tower_instance.front.levels = [front_level]
        tower_instance.right.levels = [self.make_level([])]
        tower_instance.back.levels = [self.make_level([])]
        tower_instance.left.levels = [self.make_level([])]

        with mock.patch("algorithms.algorithm2.open", mock.mock_open()):
            result = alg.solve("any/path")
        assert result == 1
