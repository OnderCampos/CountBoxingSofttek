import pytest
import json
from unittest.mock import patch, mock_open, MagicMock
from algorithms.algorithm2 import Algorithm2
from box_face import Boxface
from level import Level


class TestAlgorithm2CreateFaces:
    """Unit tests for Algorithm2.__create_faces."""

    def test_create_faces_default_not_hole(self):
        algo = Algorithm2()
        raw = [{"x1": 0, "y1": 0, "x2": 10, "y2": 10}]
        faces = algo._Algorithm2__create_faces(raw)
        assert len(faces) == 1
        assert faces[0].is_hole() is False

    def test_create_faces_hole_preserved(self):
        algo = Algorithm2()
        raw = [{"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": True}]
        faces = algo._Algorithm2__create_faces(raw)
        assert faces[0].is_hole() is True


class TestAlgorithm2SeparateInColumns:
    """Unit tests for separate_in_columns."""

    def test_single_column(self):
        algo = Algorithm2()
        level = Level()
        level.add_box(Boxface(0, 0, 10, 10, False, 1))
        columns = algo.separate_in_columns(level)
        assert len(columns) == 1
        assert columns[0]["faces"][0].id == 1

    def test_overlapping_x_columns_merge(self):
        algo = Algorithm2()
        level = Level()
        # b2's horizontal span must contain b1's xcenter so they merge.
        level.add_box(Boxface(0, 0, 20, 10, False, 1))
        level.add_box(Boxface(5, 0, 25, 10, False, 2))
        columns = algo.separate_in_columns(level)
        assert len(columns) == 1
        assert len(columns[0]["faces"]) == 2

    def test_non_overlapping_columns(self):
        algo = Algorithm2()
        level = Level()
        level.add_box(Boxface(0, 0, 10, 10, False, 1))
        level.add_box(Boxface(20, 0, 30, 10, False, 2))
        columns = algo.separate_in_columns(level)
        assert len(columns) == 2


class FakeTowerForAlgo2:
    """Minimal fake Tower whose levels contain several boxes per level
    so that right/back/left slices still iterate over columns."""

    def __init__(self, levels, boxes_per_level):
        self.front = MagicMock()
        self.front.levels = self._make_levels(boxes_per_level)
        self.right = MagicMock()
        self.right.levels = self._make_levels(boxes_per_level)
        self.back = MagicMock()
        self.back.levels = self._make_levels(boxes_per_level)
        self.left = MagicMock()
        self.left.levels = self._make_levels(boxes_per_level)

    def _make_levels(self, boxes_per_level):
        levels = []
        for boxes in boxes_per_level:
            level = Level()
            for box in boxes:
                level.add_box(box)
            levels.append(level)
        return levels

    def add_side(self, *args, **kwargs):
        pass


class TestAlgorithm2Solve:
    """Unit tests for solve with mocked filesystem and Tower."""

    @patch("algorithms.algorithm2.Tower")
    @patch("builtins.open", new_callable=mock_open)
    @patch("algorithms.algorithm2.json.load")
    def test_solve_simple_no_holes(self, mock_json_load, mock_open_file, mock_tower_cls):
        algo = Algorithm2()
        mock_json_load.return_value = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": False},
            {"x1": 40, "y1": 0, "x2": 50, "y2": 10, "is_hole": False},
        ]

        boxes = [
            Boxface(0, 0, 10, 10, False, 1),
            Boxface(20, 0, 30, 10, False, 2),
            Boxface(40, 0, 50, 10, False, 3),
        ]
        mock_tower_cls.side_effect = lambda levels: FakeTowerForAlgo2(levels, [boxes])

        result = algo.solve("towers/tower_test")
        # front 3 + right 2 + back 2 + left 1 = 8 per level, one level
        assert result == 8

    @patch("algorithms.algorithm2.Tower")
    @patch("builtins.open", new_callable=mock_open)
    @patch("algorithms.algorithm2.json.load")
    def test_solve_holes_excluded(self, mock_json_load, mock_open_file, mock_tower_cls):
        algo = Algorithm2()
        mock_json_load.return_value = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": True},
            {"x1": 40, "y1": 0, "x2": 50, "y2": 10, "is_hole": False},
        ]

        boxes = [
            Boxface(0, 0, 10, 10, False, 1),
            Boxface(20, 0, 30, 10, True, 2),
            Boxface(40, 0, 50, 10, False, 3),
        ]
        mock_tower_cls.side_effect = lambda levels: FakeTowerForAlgo2(levels, [boxes])

        result = algo.solve("towers/tower_test")
        # front counts all 3 columns -> 2 non-holes
        # right counts columns[1::] -> 1 non-hole (column index 2)
        # back counts columns[1::] -> 1 non-hole (column index 2)
        # left counts columns[1:-1] -> 0 non-holes (column index 1 is a hole)
        assert result == 4
