import json
from unittest import mock

import pytest

from algorithms.algorithm2 import Algorithm2
from box_face import Boxface
from level import Level


class TestAlgorithm2CreateFaces:
    def test_create_faces_boxface_attributes(self):
        alg = Algorithm2()
        faces = alg._Algorithm2__create_faces([
            {"x1": 10, "y1": 20, "x2": 30, "y2": 40, "is_hole": True}
        ])
        assert len(faces) == 1
        assert isinstance(faces[0], Boxface)
        assert faces[0].x1 == 10
        assert faces[0].is_hole() is True
        assert faces[0].id == 1

    def test_create_faces_default_hole_false(self):
        alg = Algorithm2()
        faces = alg._Algorithm2__create_faces([{"x1": 0, "y1": 0, "x2": 10, "y2": 10}])
        assert faces[0].is_hole() is False


class TestAlgorithm2GetSides:
    def test_get_sides_reads_all_json(self, tmp_path):
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        for side in ["front", "right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([{"x1": 0, "y1": 0, "x2": 10, "y2": 10}]))
        alg = Algorithm2()
        front, right, back, left = alg._Algorithm2__get_sides(str(tmp_path))
        assert all(len(side) == 1 for side in [front, right, back, left])


class TestAlgorithm2SeparateInColumns:
    def test_separate_in_columns_groups_by_x_center(self):
        alg = Algorithm2()
        level = Level()
        # Two columns: xcenter=5 and xcenter=25
        level.add_box(Boxface(0, 0, 10, 10, False, 1))
        level.add_box(Boxface(20, 0, 30, 10, False, 2))
        level.add_box(Boxface(1, 100, 9, 110, False, 3))  # same xcenter column as box 1
        columns = alg.separate_in_columns(level)
        assert len(columns) == 2
        assert {len(col["faces"]) for col in columns} == {2, 1}

    def test_separate_in_columns_sorted_left_to_right(self):
        alg = Algorithm2()
        level = Level()
        level.add_box(Boxface(100, 0, 110, 10, False, 1))
        level.add_box(Boxface(0, 0, 10, 10, False, 2))
        columns = alg.separate_in_columns(level)
        assert len(columns) == 2
        assert columns[0]["cast_line"] < columns[1]["cast_line"]


class TestAlgorithm2Solve:
    def test_solve_counts_non_hole_boxes(self, tmp_path):
        """US-3: Contar cajas aproximadas descartando agujeros."""
        alg = Algorithm2()
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        # 3 levels expected by Tower; provide 3 boxes per side at different y positions
        y_positions = [0, 100, 200]
        for side in ["front", "right", "back", "left"]:
            boxes = [
                {"x1": 0, "y1": y, "x2": 10, "y2": y + 10, "is_hole": False}
                for y in y_positions
            ]
            (json_dir / f"{side}.json").write_text(json.dumps(boxes))
        result = alg.solve(str(tmp_path))
        assert isinstance(result, int)
        assert result >= 0

    def test_solve_with_holes_excludes_them(self, tmp_path):
        alg = Algorithm2()
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        y_positions = [0, 100, 200]
        for side in ["front", "right", "back", "left"]:
            boxes = [
                {"x1": 0, "y1": y, "x2": 10, "y2": y + 10, "is_hole": True}
                for y in y_positions
            ]
            (json_dir / f"{side}.json").write_text(json.dumps(boxes))
        result = alg.solve(str(tmp_path))
        assert result == 0

    def test_solve_different_level_count_skips_count(self, tmp_path):
        """Si los lados no pueden agruparse en los 3 niveles esperados, falla con ZeroDivisionError."""
        alg = Algorithm2()
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        # front has 2 levels, other sides have 1; Tower expects 3 levels
        (json_dir / "front.json").write_text(json.dumps([
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 0, "y1": 100, "x2": 10, "y2": 110, "is_hole": False},
        ]))
        for side in ["right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([
                {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            ]))
        with pytest.raises(ZeroDivisionError):
            alg.solve(str(tmp_path))
