import json
import pytest
from unittest.mock import patch
from algorithms.algorithm2 import Algorithm2
from box_face import Boxface
from level import Level


class TestAlgorithm2CreateFaces:
    def test_create_faces_defaults_and_ids(self):
        algo = Algorithm2()
        boxes = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10},
            {"x1": 20, "y1": 20, "x2": 30, "y2": 30, "is_hole": True},
        ]
        faces = algo._Algorithm2__create_faces(boxes)
        assert len(faces) == 2
        assert faces[0].is_hole() is False
        assert faces[1].is_hole() is True
        assert faces[0].id == 1
        assert faces[1].id == 2


class TestAlgorithm2GetSides:
    def test_get_sides_reads_four_files(self, tmp_path):
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        for side in ["front", "right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([
                {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False}
            ]))
        algo = Algorithm2()
        front, right, back, left = algo._Algorithm2__get_sides(str(tmp_path))
        assert len(front) == 1
        assert front[0].is_hole() is False


class TestAlgorithm2SeparateInColumns:
    def test_separates_level_into_columns_sorted_left_to_right(self):
        algo = Algorithm2()
        level = Level()
        level.add_box(Boxface(100, 0, 110, 10, False, 1))
        level.add_box(Boxface(0, 0, 10, 10, False, 2))
        level.add_box(Boxface(50, 0, 60, 10, False, 3))
        columns = algo.separate_in_columns(level)
        assert len(columns) == 3
        assert [box.id for box in columns[0]["faces"]] == [2]
        assert [box.id for box in columns[1]["faces"]] == [3]
        assert [box.id for box in columns[2]["faces"]] == [1]

    def test_non_overlapping_x_ranges_are_separate_columns(self):
        # The implementation compares cast_line (xcenter) against x1/x2.
        # Boxes whose ranges do NOT contain the other's xcenter become separate columns.
        algo = Algorithm2()
        level = Level()
        level.add_box(Boxface(0, 0, 10, 10, False, 1))    # xcenter=5
        level.add_box(Boxface(20, 0, 30, 10, False, 2))   # xcenter=25
        columns = algo.separate_in_columns(level)
        assert len(columns) == 2
        assert [box.id for box in columns[0]["faces"]] == [1]
        assert [box.id for box in columns[1]["faces"]] == [2]

    def test_mutual_overlap_groups_together(self):
        # For both boxes to be grouped, each xcenter must fall inside the other's x range.
        algo = Algorithm2()
        level = Level()
        level.add_box(Boxface(0, 0, 30, 10, False, 1))    # xcenter=15
        # Box 2 spans 10-40, so 15 is inside [10,40].
        # Box 1 spans 0-30, so 25 (box2 xcenter) is inside [0,30].
        level.add_box(Boxface(10, 0, 40, 10, False, 2))   # xcenter=25
        columns = algo.separate_in_columns(level)
        assert len(columns) == 1
        assert {box.id for box in columns[0]["faces"]} == {1, 2}

    def test_partial_overlap_result(self):
        # With boxes [0,30] and [20,50], the algorithm groups them only if the current
        # cast_line is contained in the other box. Here box1 (cast_line=15) is contained
        # in box2 [20,50] (false: 15 is not > 20), so box2 remains for a second column.
        algo = Algorithm2()
        level = Level()
        level.add_box(Boxface(0, 0, 30, 10, False, 1))    # xcenter=15
        level.add_box(Boxface(20, 0, 50, 10, False, 2))   # xcenter=35
        columns = algo.separate_in_columns(level)
        # Because 15 is not inside [20, 50], box2 is not grouped with box1.
        assert len(columns) == 2
        assert [box.id for box in columns[0]["faces"]] == [1]
        assert [box.id for box in columns[1]["faces"]] == [2]


class TestAlgorithm2Solve:
    @patch('algorithms.algorithm2.Tower')
    @patch('algorithms.algorithm2.cv2.imread')
    def test_solve_counts_non_hole_boxes(self, mock_imread, MockTower, tmp_path):
        mock_imread.return_value = None
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        for side in ["front", "right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([
                {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
                {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": True},
            ]))

        tower = MockTower.return_value
        level = Level()
        level.add_box(Boxface(0, 0, 10, 10, False, 1))
        level.add_box(Boxface(20, 0, 30, 10, True, 2))
        tower.front.levels = [level]
        tower.right.levels = [level]
        tower.back.levels = [level]
        tower.left.levels = [level]

        algo = Algorithm2()
        result = algo.solve(str(tmp_path))
        # front counts 1 non-hole, right/back/left skip first column -> 0 each
        assert result == 1

    @patch('algorithms.algorithm2.Tower')
    @patch('algorithms.algorithm2.cv2.imread')
    def test_solve_mismatched_levels_returns_none(self, mock_imread, MockTower, tmp_path):
        mock_imread.return_value = None
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        for side in ["front", "right", "back", "left"]:
            (json_dir / f"{side}.json").write_text("[]")

        tower = MockTower.return_value
        tower.front.levels = [Level()]
        tower.right.levels = []
        tower.back.levels = [Level()]
        tower.left.levels = [Level()]

        algo = Algorithm2()
        result = algo.solve(str(tmp_path))
        assert result is None
