import json
import pytest
from box_face import Boxface
from algorithms.algorithm1 import Algorithm1


def make_side_json(line_boxes: list):
    """Helper to build a JSON-serializable list of boxes."""
    return [
        {"x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3], "is_hole": box[4]}
        for box in line_boxes
    ]


def write_tower(tmp_path, front, right, back, left):
    json_dir = tmp_path / "json"
    json_dir.mkdir(exist_ok=True)
    (json_dir / "front.json").write_text(json.dumps(front))
    (json_dir / "right.json").write_text(json.dumps(right))
    (json_dir / "back.json").write_text(json.dumps(back))
    (json_dir / "left.json").write_text(json.dumps(left))


# ---------------------------------------------------------------------------
# User Story #1: Cargar las caras de la torre
# ---------------------------------------------------------------------------

class TestUserStory1CargarLasCarasDeLaTorre:
    def test_ac_1_debe_leer_los_cuatro_archivos_json(self, tmp_path):
        for side in ["front", "right", "back", "left"]:
            json_dir = tmp_path / "json"
            json_dir.mkdir(exist_ok=True)
            (json_dir / f"{side}.json").write_text(json.dumps([]))
        algo = Algorithm1()
        front, right, back, left = algo._Algorithm1__get_sides(str(tmp_path))
        assert front == []
        assert right == []
        assert back == []
        assert left == []

    def test_ac_2_cada_caja_se_convierte_en_boxface_con_sus_atributos(self):
        algo = Algorithm1()
        boxes = [{"x1": 10, "y1": 20, "x2": 30, "y2": 40, "is_hole": True}]
        faces = algo._Algorithm1__create_faces(boxes)
        assert len(faces) == 1
        face = faces[0]
        assert isinstance(face, Boxface)
        assert face.x1 == 10
        assert face.y1 == 20
        assert face.x2 == 30
        assert face.y2 == 40
        assert face.is_hole() is True
        assert face.id == 1


# ---------------------------------------------------------------------------
# User Story #2: Separar las caras en líneas
# ---------------------------------------------------------------------------

class TestUserStory2SepararLasCarasEnLineas:
    def test_ac_3_caras_en_la_misma_linea_de_proyeccion_se_agrupan(self):
        algo = Algorithm1()
        faces = [
            Boxface(0, 100, 10, 200, False, 1),
            Boxface(30, 100, 40, 200, False, 2),
            Boxface(0, 300, 10, 400, False, 3),
        ]
        lines = algo.separate_in_lines(faces)
        assert len(lines) == 2
        assert {box.id for box in lines[0]["faces"]} == {1, 2}
        assert {box.id for box in lines[1]["faces"]} == {3}

    def test_ac_4_caras_de_cada_linea_ordenadas_izquierda_a_derecha(self):
        algo = Algorithm1()
        faces = [
            Boxface(100, 0, 110, 10, False, 1),
            Boxface(0, 0, 10, 10, False, 2),
            Boxface(50, 0, 60, 10, False, 3),
        ]
        lines = algo.separate_in_lines(faces)
        assert len(lines) == 1
        assert [box.id for box in lines[0]["faces"]] == [2, 3, 1]


# ---------------------------------------------------------------------------
# User Story #3: Calcular cajas y agujeros
# ---------------------------------------------------------------------------

class TestUserStory3CalcularCajasYAgujeros:
    def test_ac_5_verifica_misma_cantidad_de_lineas_en_los_cuatro_lados(self, tmp_path):
        line = [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10, "is_hole": False},
            {"x1": 20, "y1": 0, "x2": 30, "y2": 10, "is_hole": False},
        ]
        write_tower(tmp_path, line, line, line, line)
        algo = Algorithm1()
        result = algo.solve(str(tmp_path))
        # 1 line * 2*2 = 4 boxes, 0 holes
        assert result == 4

    def test_ac_6_calcula_cajas_multiplicando_frontal_por_derecha(self, tmp_path):
        front = make_side_json([
            (0, 0, 10, 10, False),
            (20, 0, 30, 10, False),
        ])
        right = make_side_json([
            (0, 0, 10, 10, False),
            (20, 0, 30, 10, False),
            (40, 0, 50, 10, False),
        ])
        write_tower(tmp_path, front, right, front, front)
        algo = Algorithm1()
        result = algo.solve(str(tmp_path))
        # 1 line * 2 front * 3 right = 6 boxes, 0 holes
        assert result == 6

    def test_ac_7_resultado_final_es_cantidad_calculada_menos_agujeros(self, tmp_path):
        # Use boxes whose y-ranges do NOT overlap across lines, ensuring one line per side.
        # Each side has 3 boxes in a single line:
        #   [hole=False, hole=True, hole=False]
        # Inner holes per side = 1 (the middle box).
        # Corner holes: for each adjacent pair, the last face of sideA and the first face
        # of sideB are both non-holes, so corner holes = 0.
        side = make_side_json([
            (0, 0, 10, 10, False),
            (20, 0, 30, 10, True),
            (40, 0, 50, 10, False),
        ])
        write_tower(tmp_path, side, side, side, side)
        algo = Algorithm1()
        result = algo.solve(str(tmp_path))
        # 1 line * 3*3 = 9 boxes
        # inner holes: 1 per side = 4 holes
        # corner holes: 0
        assert result == 5
