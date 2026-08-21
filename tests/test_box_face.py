import sys
import os

# Ensure repository root is on path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from box_face import Boxface


def make_face(x1=0, y1=0, x2=10, y2=10, is_hole=False, id=1):
    return Boxface(x1, y1, x2, y2, is_hole, id)


describe = globals().get("describe", lambda x, f=None: f())


def test_user_story_1_ac_2_boxface_object_has_coordinates_hole_and_id():
    """AC-2 / US-1: Cada caja debe convertirse en un objeto Boxface con sus coordenadas, indicador de agujero e identificador."""
    face = make_face(10, 20, 30, 40, is_hole=True, id=5)
    assert face.x1 == 10
    assert face.y1 == 20
    assert face.x2 == 30
    assert face.y2 == 40
    assert face.is_hole() is True
    assert face.id == 5


def test_boxface_center_calculation():
    face = make_face(0, 0, 10, 20)
    assert face.xcenter == 5
    assert face.ycenter == 10
    assert face.get_center() == (5, 10)


def test_boxface_center_calculation_with_negative_coordinates():
    face = make_face(-10, -20, 10, 20)
    assert face.xcenter == 0
    assert face.ycenter == 0
    assert face.get_center() == (0, 0)


def test_boxface_is_hole_defaults_to_false():
    face = make_face()
    assert face.is_hole() is False


def test_boxface_set_id():
    face = make_face(id=1)
    face.set_id(99)
    assert face.id == 99


def test_boxface_repr_is_stringified_id():
    face = make_face(id=42)
    assert repr(face) == "42"
