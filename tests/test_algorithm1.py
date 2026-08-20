import pytest
import json
from unittest.mock import patch, mock_open
from algorithms.algorithm1 import Algorithm1
from box_face import Boxface


class TestAlgorithm1CreateFaces:
    """Unit tests for __create_faces helper."""

    def test_create_faces_without_is_hole(self):
        algo = Algorithm1()
        raw = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10},
            {"x1": 20, "y1": 20, "x2": 30, "y2": 30},
        ]
        faces = algo._Algorithm1__create_faces(raw)
        assert len(faces) == 2
        assert all(not face.is_hole() for face in faces)
        assert faces[0].id == 1
        assert faces[1].id == 2

    def test_create_faces_with_is_hole(self):
        algo = Algorithm1()
        raw = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": True},
            {"x1": 20, "y1": 20, "x2": 30, "y2": 30, "is_hole": False},
        ]
        faces = algo._Algorithm1__create_faces(raw)
        assert faces[0].is_hole() is True
        assert faces[1].is_hole() is False


class TestAlgorithm1SeparateInLines:
    """Unit tests for separate_in_lines."""

    def test_single_line(self):
        algo = Algorithm1()
        boxes = [
            Boxface(0, 0, 10, 10, False, 1),
            Boxface(5, 0, 15, 10, False, 2),
        ]
        lines = algo.separate_in_lines(boxes)
        assert len(lines) == 1
        assert len(lines[0]["faces"]) == 2

    def test_two_non_overlapping_lines(self):
        algo = Algorithm1()
        # Two boxes on different y bands so cast lines do not intersect
        top = Boxface(0, 0, 10, 10, False, 1)
        bottom = Boxface(0, 20, 10, 30, False, 2)
        lines = algo.separate_in_lines([top, bottom])
        assert len(lines) == 2

    def test_overlapping_boxes_merge_into_same_line(self):
        algo = Algorithm1()
        # b2's vertical span must contain b1's center (and vice-versa)
        # so they are placed on the same line by the algorithm.
        b1 = Boxface(0, 0, 20, 20, False, 1)
        b2 = Boxface(5, 5, 15, 15, False, 2)
        lines = algo.separate_in_lines([b1, b2])
        assert len(lines) == 1
        assert len(lines[0]["faces"]) == 2

    def test_sorted_by_x1(self):
        algo = Algorithm1()
        left = Boxface(10, 0, 20, 10, False, 1)
        right = Boxface(0, 0, 10, 10, False, 2)
        lines = algo.separate_in_lines([left, right])
        assert [face.id for face in lines[0]["faces"]] == [2, 1]


class TestAlgorithm1HoleCounting:
    """Unit tests for corner and inner hole counting."""

    def test_count_corner_holes_true(self):
        algo = Algorithm1()
        line_a = {"faces": [Boxface(0, 0, 10, 10, True, 1)]}
        line_b = {"faces": [Boxface(20, 0, 30, 10, True, 2)]}
        assert algo.count_corner_holes(line_a, line_b) == 1

    def test_count_corner_holes_false(self):
        algo = Algorithm1()
        line_a = {"faces": [Boxface(0, 0, 10, 10, True, 1)]}
        line_b = {"faces": [Boxface(20, 0, 30, 10, False, 2)]}
        assert algo.count_corner_holes(line_a, line_b) == 0

    def test_count_inner_holes_basic(self):
        algo = Algorithm1()
        line = {
            "faces": [
                Boxface(0, 0, 10, 10, False, 1),
                Boxface(20, 0, 30, 10, True, 2),
                Boxface(40, 0, 50, 10, False, 3),
            ]
        }
        assert algo.count_inner_holes(line) == 1

    def test_count_inner_holes_only_two_faces(self):
        algo = Algorithm1()
        line = {
            "faces": [
                Boxface(0, 0, 10, 10, True, 1),
                Boxface(20, 0, 30, 10, True, 2),
            ]
        }
        assert algo.count_inner_holes(line) == 0


class TestAlgorithm1Solve:
    """Unit tests for solve with mocked filesystem access."""

    @patch("builtins.open", new_callable=mock_open)
    @patch("algorithms.algorithm1.json.load")
    def test_solve_no_holes(self, mock_json_load, mock_open_file):
        algo = Algorithm1()
        # Each side has one line with two boxes -> 2*2 = 4 boxes, no holes
        side_data = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": False},
        ]
        mock_json_load.return_value = side_data
        result = algo.solve("towers/tower_test")
        assert result == 4

    @patch("builtins.open", new_callable=mock_open)
    @patch("algorithms.algorithm1.json.load")
    def test_solve_with_inner_hole(self, mock_json_load, mock_open_file):
        algo = Algorithm1()
        # Construct sides that separate into exactly one line of three boxes
        # with the middle box being a hole.
        side_data = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 100, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 100, "is_hole": True},
            {"x1": 40, "y1": 0, "x2": 50, "y2": 100, "is_hole": False},
        ]
        mock_json_load.return_value = side_data
        result = algo.solve("towers/tower_test")
        # Naive count = 3*3 = 9 per line, one line only. Holes = 4 inner holes.
        assert result == 9 - 4

    @patch("builtins.open", new_callable=mock_open)
    @patch("algorithms.algorithm1.json.load")
    def test_solve_mismatched_line_counts(self, mock_json_load, mock_open_file):
        algo = Algorithm1()

        def side_data_side_effect(file):
            # front/right/back -> 1 line; left -> 2 lines
            file_name = file.name if hasattr(file, "name") else str(file)
            if "left.json" in file_name:
                return [
                    {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
                    {"x1": 0, "y1": 20, "x2": 10, "y2": 30, "is_hole": False},
                ]
            return [
                {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
                {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": False},
            ]

        mock_json_load.side_effect = side_data_side_effect
        result = algo.solve("towers/tower_test")
        # Mismatched line counts skip hole correction but still compute aprox_size
        # front: 2 boxes -> 2*2 per side * len(front_lines) = 4
        assert result == 4
