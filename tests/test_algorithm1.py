import json
import os
from unittest import mock

import pytest

from algorithms.algorithm1 import Algorithm1
from box_face import Boxface


class TestUserStory1LoadTowerFaces:
    """User Story #1: Cargar las caras de la torre."""

    def test_ac1_reads_four_side_json_files(self, tmp_path):
        """AC-1 / US-1: Debe leer front.json, right.json, back.json y left.json."""
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        for side in ["front", "right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([{"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False}]))

        alg = Algorithm1()
        front, right, back, left = alg._Algorithm1__get_sides(str(tmp_path))
        assert len(front) == 1
        assert len(right) == 1
        assert len(back) == 1
        assert len(left) == 1

    def test_ac1_missing_file_raises_error(self, tmp_path):
        """AC-1 / US-1: Si falta algún archivo JSON debe lanzar FileNotFoundError."""
        alg = Algorithm1()
        with pytest.raises(FileNotFoundError):
            alg._Algorithm1__get_sides(str(tmp_path))

    def test_ac2_creates_boxface_objects_with_attributes(self, tmp_path):
        """AC-2 / US-1: Cada caja se convierte en Boxface con coordenadas, indicador de agujero e id."""
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        boxes = [
            {"x1": 10, "y1": 20, "x2": 30, "y2": 40, "is_hole": False},
            {"x1": 50, "y1": 60, "x2": 70, "y2": 80, "is_hole": True},
        ]
        (json_dir / "front.json").write_text(json.dumps(boxes))
        for side in ["right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([]))

        alg = Algorithm1()
        front, *_ = alg._Algorithm1__get_sides(str(tmp_path))
        assert len(front) == 2
        assert all(isinstance(face, Boxface) for face in front)
        assert front[0].x1 == 10 and front[0].y1 == 20 and front[0].x2 == 30 and front[0].y2 == 40
        assert front[0].is_hole() is False
        assert front[1].is_hole() is True
        assert front[0].id == 1
        assert front[1].id == 2

    def test_ac2_default_hole_false_when_key_missing(self, tmp_path):
        """AC-2 / US-1: Si no existe 'is_hole' debe asumir False."""
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        (json_dir / "front.json").write_text(json.dumps([{"x1": 0, "y1": 0, "x2": 10, "y2": 10}]))
        for side in ["right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([]))

        alg = Algorithm1()
        front, *_ = alg._Algorithm1__get_sides(str(tmp_path))
        assert front[0].is_hole() is False

    def test_ac2_float_coordinates_are_converted_to_int(self, tmp_path):
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        (json_dir / "front.json").write_text(json.dumps([{"x1": 10.9, "y1": 20.1, "x2": 30.9, "y2": 40.1}]))
        for side in ["right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([]))

        alg = Algorithm1()
        front, *_ = alg._Algorithm1__get_sides(str(tmp_path))
        assert front[0].x1 == 10
        assert front[0].y2 == 40


class TestUserStory2SeparateInLines:
    """User Story #2: Separar las caras en líneas."""

    def test_ac3_faces_intersecting_same_projection_line_grouped(self):
        """AC-3 / US-2: Caras que intersectan la misma línea de proyección se agrupan juntas."""
        alg = Algorithm1()
        faces = [
            Boxface(0, 0, 10, 10, False, 1),    # ycenter = 5
            Boxface(20, 0, 30, 10, False, 2),   # ycenter = 5, intersects line 5
            Boxface(0, 20, 10, 30, False, 3),   # ycenter = 25
            Boxface(20, 20, 30, 30, False, 4),  # ycenter = 25, intersects line 25
        ]
        lines = alg.separate_in_lines(faces)
        assert len(lines) == 2
        assert {len(line["faces"]) for line in lines} == {2}

    def test_ac3_faces_not_intersecting_different_lines(self):
        """AC-3 / US-2: Caras en diferentes líneas no se mezclan."""
        alg = Algorithm1()
        faces = [
            Boxface(0, 0, 10, 10, False, 1),    # ycenter = 5
            Boxface(0, 100, 10, 110, False, 2), # ycenter = 105
        ]
        lines = alg.separate_in_lines(faces)
        assert len(lines) == 2
        assert len(lines[0]["faces"]) == 1
        assert len(lines[1]["faces"]) == 1

    def test_ac4_faces_sorted_left_to_right_by_x1(self):
        """AC-4 / US-2: Las caras de cada línea se ordenan de izquierda a derecha por x1."""
        alg = Algorithm1()
        faces = [
            Boxface(100, 0, 110, 10, False, 1),
            Boxface(0, 0, 10, 10, False, 2),
            Boxface(50, 0, 60, 10, False, 3),
        ]
        lines = alg.separate_in_lines(faces)
        assert len(lines) == 1
        x1s = [face.x1 for face in lines[0]["faces"]]
        assert x1s == [0, 50, 100]

    def test_ac4_lines_sorted_by_cast_line(self):
        """AC-4 / US-2: Las líneas se ordenan por cast_line (vertical)."""
        alg = Algorithm1()
        faces = [
            Boxface(0, 100, 10, 110, False, 1), # line 105
            Boxface(0, 0, 10, 10, False, 2),    # line 5
        ]
        lines = alg.separate_in_lines(faces)
        assert lines[0]["cast_line"] == 5
        assert lines[1]["cast_line"] == 105


class TestUserStory3CalculateBoxesAndHoles:
    """User Story #3: Calcular cajas y agujeros."""

    def test_ac5_all_sides_same_line_count(self, tmp_path):
        """AC-5 / US-3: Cuatro lados con la misma cantidad de líneas permiten continuar."""
        alg = Algorithm1()
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        for side in ["front", "right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([
                {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
                {"x1": 0, "y1": 20, "x2": 10, "y2": 30, "is_hole": False},
            ]))
        result = alg.solve(str(tmp_path))
        assert result >= 0

    def test_ac5_different_line_count_raises_index_error(self, tmp_path):
        """AC-5 / US-3: Diferente cantidad de líneas genera IndexError en el cálculo actual."""
        alg = Algorithm1()
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        (json_dir / "front.json").write_text(json.dumps([
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 0, "y1": 20, "x2": 10, "y2": 30, "is_hole": False},
        ]))
        for side in ["right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([
                {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            ]))
        with pytest.raises(IndexError):
            alg.solve(str(tmp_path))

    def test_ac6_multiply_front_faces_by_right_faces(self, tmp_path):
        """AC-6 / US-3: Cálculo base = caras frontal * caras derecha por línea."""
        alg = Algorithm1()
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        # Una sola línea, front=2, right=3, back=2, left=2 -> 2*3 = 6
        (json_dir / "front.json").write_text(json.dumps([
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": False},
        ]))
        (json_dir / "right.json").write_text(json.dumps([
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": False},
            {"x1": 40, "y1": 0, "x2": 50, "y2": 10, "is_hole": False},
        ]))
        for side in ["back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([
                {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            ]))
        result = alg.solve(str(tmp_path))
        assert result == 6

    def test_ac7_final_result_is_calculated_minus_holes(self, tmp_path):
        """AC-7 / US-3: El resultado final es cantidad calculada menos agujeros."""
        alg = Algorithm1()
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        # Una línea, front=2 (ambas agujero en esquina), right=2 (primera agujero)
        # corner front-right: face front[-1] hole && face right[0] hole -> 1
        # total base = 2*2 = 4, holes = 1 -> result = 3
        (json_dir / "front.json").write_text(json.dumps([
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": True},
        ]))
        (json_dir / "right.json").write_text(json.dumps([
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": True},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": False},
        ]))
        for side in ["back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([
                {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
                {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": False},
            ]))
        result = alg.solve(str(tmp_path))
        assert result == 3

    def test_ac7_inner_holes_are_subtracted(self, tmp_path):
        """AC-7 / US-3: Los agujeros internos se descuentan del total."""
        alg = Algorithm1()
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        # front=3 (middle hole), right=1 -> base=3; inner holes=1; result=2
        (json_dir / "front.json").write_text(json.dumps([
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": True},
            {"x1": 40, "y1": 0, "x2": 50, "y2": 10, "is_hole": False},
        ]))
        for side in ["right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([
                {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            ]))
        result = alg.solve(str(tmp_path))
        assert result == 2

    def test_ac7_empty_tower_returns_zero(self, tmp_path):
        alg = Algorithm1()
        json_dir = tmp_path / "json"
        json_dir.mkdir()
        for side in ["front", "right", "back", "left"]:
            (json_dir / f"{side}.json").write_text(json.dumps([]))
        result = alg.solve(str(tmp_path))
        assert result == 0
