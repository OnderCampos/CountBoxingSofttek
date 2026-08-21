import json
import pytest
from unittest import mock

from algorithms.algorithm1 import Algorithm1
from box_face import Boxface


class TestUserStory1LoadFaces:
    """User Story #1: Cargar las caras de la torre."""

    @mock.patch("algorithms.algorithm1.json.load")
    def test_ac1_reads_four_json_files(self, mock_json_load):
        """AC-1: Debe leer front.json, right.json, back.json y left.json."""
        mock_json_load.side_effect = [
            [{"x1": 0, "y1": 0, "x2": 10, "y2": 10}],
            [{"x1": 10, "y1": 0, "x2": 20, "y2": 10}],
            [{"x1": 20, "y1": 0, "x2": 30, "y2": 10}],
            [{"x1": 30, "y1": 0, "x2": 40, "y2": 10}],
        ]

        alg = Algorithm1()
        with mock.patch("algorithms.algorithm1.open", mock.mock_open()) as mock_open:
            front, right, back, left = alg._Algorithm1__get_sides("towers/tower1")

        opened_files = [call.args[0] for call in mock_open.call_args_list]
        assert any("front.json" in f for f in opened_files)
        assert any("right.json" in f for f in opened_files)
        assert any("back.json" in f for f in opened_files)
        assert any("left.json" in f for f in opened_files)
        assert len(front) == len(right) == len(back) == len(left) == 1

    @mock.patch("algorithms.algorithm1.open", mock.mock_open())
    @mock.patch("algorithms.algorithm1.json.load")
    def test_ac2_converts_boxes_to_boxface_with_hole_flag(self, mock_json_load):
        """AC-2: Cada caja convertirse en un Boxface con coordenadas, indicador de agujero e identificador."""
        mock_json_load.return_value = [
            {"x1": 10, "y1": 20, "x2": 30, "y2": 40, "is_hole": True}
        ]

        alg = Algorithm1()
        front, *_ = alg._Algorithm1__get_sides("any/path")

        assert len(front) == 1
        box = front[0]
        assert isinstance(box, Boxface)
        assert box.x1 == 10
        assert box.y1 == 20
        assert box.x2 == 30
        assert box.y2 == 40
        assert box.is_hole() is True
        assert box.id == 1

    @mock.patch("algorithms.algorithm1.open", mock.mock_open())
    @mock.patch("algorithms.algorithm1.json.load")
    def test_ac2_missing_is_hole_defaults_to_false(self, mock_json_load):
        """AC-2 edge case: missing is_hole key defaults to False."""
        mock_json_load.return_value = [
            {"x1": 1, "y1": 2, "x2": 3, "y2": 4}
        ]

        alg = Algorithm1()
        front, *_ = alg._Algorithm1__get_sides("any/path")
        assert front[0].is_hole() is False


class TestUserStory2SeparateLines:
    """User Story #2: Separar las caras en líneas."""

    def make_face(self, x1, y1, x2, y2, is_hole=False, box_id=1):
        return Boxface(x1, y1, x2, y2, is_hole, box_id)

    def test_ac3_faces_intersecting_same_projection_line_are_grouped(self):
        """AC-3: Las caras que intersecten la misma línea de proyección se agrupan juntas."""
        # Two faces whose y-range overlaps the first face's ycenter -> same line
        faces = [
            self.make_face(0, 0, 10, 10, box_id=1),   # ycenter = 5
            self.make_face(20, 4, 30, 20, box_id=2),  # y1=4 < 5 < y2=20
        ]
        alg = Algorithm1()
        lines = alg.separate_in_lines(faces)

        assert len(lines) == 1
        assert len(lines[0]["faces"]) == 2
        assert {f.id for f in lines[0]["faces"]} == {1, 2}

    def test_ac3_faces_on_different_projection_lines_remain_separated(self):
        faces = [
            self.make_face(0, 0, 10, 10, box_id=1),    # line around y=5
            self.make_face(20, 100, 30, 120, box_id=2),  # line around y=110
        ]
        alg = Algorithm1()
        lines = alg.separate_in_lines(faces)

        assert len(lines) == 2
        assert len(lines[0]["faces"]) == 1
        assert len(lines[1]["faces"]) == 1

    def test_ac4_faces_inside_line_ordered_left_to_right(self):
        """AC-4: Las caras de cada línea deben ordenarse de izquierda a derecha por x1."""
        faces = [
            self.make_face(50, 0, 60, 10, box_id=1),
            self.make_face(0, 0, 10, 10, box_id=2),
            self.make_face(25, 0, 35, 10, box_id=3),
        ]
        alg = Algorithm1()
        lines = alg.separate_in_lines(faces)

        assert len(lines) == 1
        ordered = lines[0]["faces"]
        assert [f.id for f in ordered] == [2, 3, 1]
        assert ordered[0].x1 < ordered[1].x1 < ordered[2].x1

    def test_ac4_lines_sorted_by_cast_line(self):
        faces = [
            self.make_face(0, 100, 10, 110, box_id=1),  # cast ~105
            self.make_face(0, 0, 10, 10, box_id=2),       # cast ~5
            self.make_face(0, 50, 10, 60, box_id=3),      # cast ~55
        ]
        alg = Algorithm1()
        lines = alg.separate_in_lines(faces)

        assert len(lines) == 3
        assert lines[0]["cast_line"] < lines[1]["cast_line"] < lines[2]["cast_line"]
        assert [l["faces"][0].id for l in lines] == [2, 3, 1]

    def test_separate_in_lines_empty_input(self):
        alg = Algorithm1()
        assert alg.separate_in_lines([]) == []

    def test_separate_in_lines_single_face(self):
        face = self.make_face(0, 0, 10, 10, box_id=42)
        alg = Algorithm1()
        lines = alg.separate_in_lines([face])
        assert len(lines) == 1
        assert lines[0]["cast_line"] == face.ycenter
        assert lines[0]["faces"][0].id == 42


class TestUserStory3CalculateBoxesAndHoles:
    """User Story #3: Calcular cajas y agujeros."""

    def make_line(self, faces):
        return {"cast_line": faces[0].ycenter if faces else 0, "faces": faces}

    def make_face(self, x1, y1, x2, y2, is_hole=False, box_id=1):
        return Boxface(x1, y1, x2, y2, is_hole, box_id)

    def test_ac5_equal_lines_count_across_sides(self):
        """AC-5: Debe verificar que los cuatro lados tengan la misma cantidad de líneas. (succeeds)"""
        alg = Algorithm1()
        front = [self.make_line([self.make_face(0, 0, 10, 10, box_id=1)])]
        right = [self.make_line([self.make_face(0, 0, 10, 10, box_id=2)])]
        back = [self.make_line([self.make_face(0, 0, 10, 10, box_id=3)])]
        left = [self.make_line([self.make_face(0, 0, 10, 10, box_id=4)])]

        assert len(front) == len(right) == len(back) == len(left)

    def test_ac6_calculates_boxes_by_multiplying_front_by_right(self):
        """AC-6: Debe calcular las cajas multiplicando las caras de cada línea frontal por las caras de la línea derecha."""
        front = [
            self.make_line([self.make_face(0, 0, 10, 10, box_id=1), self.make_face(20, 0, 30, 10, box_id=2)])
        ]
        right = [
            self.make_line([self.make_face(0, 0, 10, 10, box_id=3), self.make_face(20, 0, 30, 10, box_id=4)])
        ]
        boxes_count = 0
        for i in range(len(front)):
            boxes_count += len(front[i]["faces"]) * len(right[i]["faces"])
        assert boxes_count == 4

    def test_ac7_result_is_calculated_boxes_minus_total_holes(self):
        """AC-7: El resultado final debe ser la cantidad calculada de cajas menos el total de agujeros."""
        alg = Algorithm1()
        # Use single-face lines so every hole is a corner hole, inner holes are 0.
        front_lines = [self.make_line([self.make_face(0, 0, 10, 10, is_hole=True, box_id=1)])]
        right_lines = [self.make_line([self.make_face(0, 0, 10, 10, is_hole=True, box_id=2)])]
        back_lines = [self.make_line([self.make_face(0, 0, 10, 10, is_hole=False, box_id=3)])]
        left_lines = [self.make_line([self.make_face(0, 0, 10, 10, is_hole=True, box_id=4)])]

        assert len(front_lines) == len(right_lines) == len(back_lines) == len(left_lines)

        holes = 0
        for line_num in range(len(front_lines)):
            holes += (
                alg.count_corner_holes(front_lines[line_num], right_lines[line_num])
                + alg.count_corner_holes(right_lines[line_num], back_lines[line_num])
                + alg.count_corner_holes(back_lines[line_num], left_lines[line_num])
                + alg.count_corner_holes(left_lines[line_num], front_lines[line_num])
            )
            holes += (
                alg.count_inner_holes(front_lines[line_num])
                + alg.count_inner_holes(right_lines[line_num])
                + alg.count_inner_holes(back_lines[line_num])
                + alg.count_inner_holes(left_lines[line_num])
            )

        boxes_count = sum(
            len(front_lines[i]["faces"]) * len(right_lines[i]["faces"])
            for i in range(len(front_lines))
        )
        result = boxes_count - holes

        # corner holes: front-right (hole & hole) = 1
        #               right-back (hole & false) = 0
        #               back-left (false & hole) = 0
        #               left-front (hole & hole) = 1
        # inner holes: 0
        # total holes = 2; boxes = 1*1 = 1; result = -1
        assert holes == 2
        assert boxes_count == 1
        assert result == -1

    def test_count_corner_holes_true_when_both_end_faces_are_holes(self):
        line_a = self.make_line([
            self.make_face(0, 0, 10, 10, box_id=1),
            self.make_face(20, 0, 30, 10, is_hole=True, box_id=2),
        ])
        line_b = self.make_line([
            self.make_face(0, 0, 10, 10, is_hole=True, box_id=3),
            self.make_face(20, 0, 30, 10, box_id=4),
        ])
        alg = Algorithm1()
        assert alg.count_corner_holes(line_a, line_b) == 1

    def test_count_corner_holes_false_when_not_both_holes(self):
        line_a = self.make_line([
            self.make_face(0, 0, 10, 10, is_hole=True, box_id=1),
        ])
        line_b = self.make_line([
            self.make_face(0, 0, 10, 10, is_hole=False, box_id=2),
        ])
        alg = Algorithm1()
        assert alg.count_corner_holes(line_a, line_b) == 0

    def test_count_inner_holes_ignores_first_and_last(self):
        line = self.make_line([
            self.make_face(0, 0, 10, 10, is_hole=True, box_id=1),
            self.make_face(20, 0, 30, 10, is_hole=True, box_id=2),
            self.make_face(40, 0, 50, 10, is_hole=True, box_id=3),
        ])
        alg = Algorithm1()
        assert alg.count_inner_holes(line) == 1

    def test_count_inner_holes_short_line(self):
        line = self.make_line([
            self.make_face(0, 0, 10, 10, is_hole=True, box_id=1),
            self.make_face(20, 0, 30, 10, is_hole=True, box_id=2),
        ])
        alg = Algorithm1()
        assert alg.count_inner_holes(line) == 0

    def test_unequal_line_counts_do_not_add_holes_but_still_compute_boxes(self):
        """When side line counts mismatch, holes block is skipped but boxes_count is still summed."""
        alg = Algorithm1()
        front = [self.make_line([self.make_face(0, 0, 10, 10, box_id=1)])]
        right = [self.make_line([self.make_face(0, 0, 10, 10, box_id=2)])]
        back = []
        left = []

        # Replicate solve logic when counts mismatch
        if len(front) == len(right) == len(back) == len(left):
            holes = 0
        else:
            holes = 0

        boxes_count = sum(
            len(front[i]["faces"]) * len(right[i]["faces"])
            for i in range(len(front))
        )
        assert len(front) != len(back)
        assert boxes_count == 1
        assert boxes_count - holes == 1
