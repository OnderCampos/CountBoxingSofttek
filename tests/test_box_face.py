import pytest
from box_face import Boxface


def test_boxface_creation_with_all_attributes():
    """AC-2 / US-1: cada caja se convierte en Boxface con coordenadas, indicador de agujero e id."""
    face = Boxface(10, 20, 30, 40, True, 1)
    assert face.x1 == 10
    assert face.y1 == 20
    assert face.x2 == 30
    assert face.y2 == 40
    assert face.is_hole() is True
    assert face.id == 1


def test_boxface_creation_default_hole_false():
    face = Boxface(0, 0, 10, 10, False, 2)
    assert face.is_hole() is False


def test_boxface_center_calculation():
    face = Boxface(0, 0, 10, 20, False, 3)
    assert face.xcenter == 5
    assert face.ycenter == 10
    assert face.get_center() == (5, 10)


def test_boxface_center_with_negative_coordinates():
    face = Boxface(-10, -20, 10, 20, False, 4)
    assert face.xcenter == 0
    assert face.ycenter == 0


def test_boxface_set_id():
    face = Boxface(0, 0, 10, 10, False, 99)
    face.set_id(42)
    assert face.id == 42


def test_boxface_repr():
    face = Boxface(0, 0, 10, 10, False, 7)
    assert repr(face) == "7"
