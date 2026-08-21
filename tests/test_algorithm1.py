import json
import pytest
from unittest.mock import patch, mock_open
from algorithms.algorithm1 import Algorithm1
from box_face import Boxface


class TestAlgorithm1CreateFaces:
    def test_create_faces_with_missing_is_hole_defaults_to_false(self):
        algo = Algorithm1()
        boxes = [{"x1": 0, "y1": 0, "x2": 10, "y2": 10}]
        faces = algo._Algorithm1__create_faces(boxes)
        assert len(faces) == 1
        assert isinstance(faces[0], Boxface)
        assert faces[0].is_hole() is False
        assert faces[0].id == 1

    def test_create_faces_preserves_hole_flag(self):
        algo = Algorithm1()
        boxes = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": True},
            {"x1": 20, "y1": 20, "x2": 30, "y2": 30, "is_hole": False},
        ]
        faces = algo._Algorithm1__create_faces(boxes)
        assert faces[0].is_hole() is True
        assert faces[1].is_hole() is False
        assert faces[1].id == 2

    def test_create_faces_casts_strings_to_int(self):
        algo = Algorithm1()
        boxes = [{"x1": "5", "y1": "5", "x2": "15", "y2": "15"}]
        faces = algo._Algorithm1__create_faces(boxes)
        assert faces[0].x1 == 5
        assert faces[0].x2 == 15


class TestAlgorithm1GetSides:
    def test_get_sides_reads_four_files(self, tmp_path):
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        sides = ["front", "right", "back", "left"]
        for side in sides:
            (json_dir / f"{side}.json").write_text(json.dumps([
                {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False}
            ]))
        algo = Algorithm1()
        front, right, back, left = algo._Algorithm1__get_sides(str(tmp_path))
        assert len(front) == len(right) == len(back) == len(left) == 1
        assert front[0].is_hole() is False


class TestAlgorithm1SeparateInLines:
    def test_separates_non_overlapping_vertical_lines(self):
        algo = Algorithm1()
        faces = [
            Boxface(0, 100, 10, 200, False, 1),   # line around ycenter 150
            Boxface(20, 100, 30, 200, False, 2),  # same line
            Boxface(0, 300, 10, 400, False, 3),   # line around 350
        ]
        lines = algo.separate_in_lines(faces)
        assert len(lines) == 2
        assert {box.id for box in lines[0]["faces"]} == {1, 2}
        assert [box.id for box in lines[0]["faces"]] == [1, 2]
        assert [box.id for box in lines[1]["faces"]] == [3]

    def test_lines_sorted_by_cast_line(self):
        algo = Algorithm1()
        faces = [
            Boxface(0, 300, 10, 400, False, 1),
            Boxface(0, 100, 10, 200, False, 2),
        ]
        lines = algo.separate_in_lines(faces)
        assert lines[0]["cast_line"] < lines[1]["cast_line"]

    def test_faces_within_same_line_sorted_left_to_right(self):
        algo = Algorithm1()
        faces = [
            Boxface(100, 0, 110, 20, False, 1),
            Boxface(0, 0, 10, 20, False, 2),
            Boxface(50, 0, 60, 20, False, 3),
        ]
        lines = algo.separate_in_lines(faces)
        assert len(lines) == 1
        assert [box.id for box in lines[0]["faces"]] == [2, 3, 1]


class TestAlgorithm1CountCornerHoles:
    def test_count_corner_holes_when_both_are_holes(self):
        algo = Algorithm1()
        line_a = {"faces": [Boxface(0, 0, 10, 10, False, 1), Boxface(20, 0, 30, 10, True, 2)]}
        line_b = {"faces": [Boxface(40, 0, 50, 10, True, 3), Boxface(60, 0, 70, 10, False, 4)]}
        assert algo.count_corner_holes(line_a, line_b) == 1

    def test_count_corner_holes_when_only_last_is_hole(self):
        algo = Algorithm1()
        line_a = {"faces": [Boxface(0, 0, 10, 10, False, 1), Boxface(20, 0, 30, 10, True, 2)]}
        line_b = {"faces": [Boxface(40, 0, 50, 10, False, 3)]}
        assert algo.count_corner_holes(line_a, line_b) == 0


class TestAlgorithm1CountInnerHoles:
    def test_counts_only_inner_faces(self):
        algo = Algorithm1()
        line = {"faces": [
            Boxface(0, 0, 10, 10, True, 1),
            Boxface(20, 0, 30, 10, True, 2),
            Boxface(40, 0, 50, 10, False, 3),
            Boxface(60, 0, 70, 10, True, 4),
        ]}
        # inner faces are index 1 and 2; only index 1 is a hole
        assert algo.count_inner_holes(line) == 1

    def test_short_line_returns_zero(self):
        algo = Algorithm1()
        line = {"faces": [Boxface(0, 0, 10, 10, True, 1)]}
        assert algo.count_inner_holes(line) == 0


class TestAlgorithm1Solve:
    def _write_side_files(self, tmp_path, front, right, back, left):
        json_dir = tmp_path / "json"
        json_dir.mkdir(exist_ok=True)
        (json_dir / "front.json").write_text(json.dumps(front))
        (json_dir / "right.json").write_text(json.dumps(right))
        (json_dir / "back.json").write_text(json.dumps(back))
        (json_dir / "left.json").write_text(json.dumps(left))

    def test_solve_with_uniform_lines_no_holes(self, tmp_path):
        # Each side has two clearly separated horizontal lines with two boxes each.
        line1 = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": False},
        ]
        line2 = [
            {"x1": 0, "y1": 100, "x2": 10, "y2": 110, "is_hole": False},
            {"x1": 20, "y1": 100, "x2": 30, "y2": 110, "is_hole": False},
        ]
        side_data = line1 + line2
        self._write_side_files(tmp_path, side_data, side_data, side_data, side_data)
        algo = Algorithm1()
        result = algo.solve(str(tmp_path))
        # 2 lines * (2 faces front * 2 faces right) = 8 boxes, 0 holes
        assert result == 8

    def test_solve_with_inner_holes(self, tmp_path):
        line1 = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": True},
            {"x1": 40, "y1": 0, "x2": 50, "y2": 10, "is_hole": False},
        ]
        line2 = [
            {"x1": 0, "y1": 100, "x2": 10, "y2": 110, "is_hole": False},
            {"x1": 20, "y1": 100, "x2": 30, "y2": 110, "is_hole": True},
            {"x1": 40, "y1": 100, "x2": 50, "y2": 110, "is_hole": False},
        ]
        side_data = line1 + line2
        self._write_side_files(tmp_path, side_data, side_data, side_data, side_data)
        algo = Algorithm1()
        result = algo.solve(str(tmp_path))
        # 2 lines * (3*3)=18 boxes; one inner hole per side per line -> 8 holes
        assert result == 10

    def test_solve_mismatched_line_counts_returns_zero_or_raises(self, tmp_path):
        front = [{"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False}]
        empty = []
        self._write_side_files(tmp_path, front, empty, empty, empty)
        algo = Algorithm1()
        # The current implementation does not guard against mismatched line counts
        # before computing boxes_count, so it raises an IndexError.
        with pytest.raises(IndexError):
            algo.solve(str(tmp_path))
