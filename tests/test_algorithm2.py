import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, MagicMock
from algorithms.algorithm2 import Algorithm2
from box_face import Boxface
from level import Level


def create_tower_data(tmpdir, sides):
    json_dir = os.path.join(tmpdir, "json")
    os.makedirs(json_dir)
    for side_name, boxes in sides.items():
        with open(os.path.join(json_dir, f"{side_name}.json"), "w") as f:
            json.dump(boxes, f)
    return tmpdir


def box(x1, y1, x2, y2, is_hole=False):
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "is_hole": is_hole}


def _build_levels_from_sides(sides):
    """Create mocked Tower levels from raw side dicts, one level per side.
    Replicates the structure produced by Tower.add_side + kmeans clustering
    but without running cv2/kmeans.
    """
    from tower import Side as TowerSide
    from level import Level

    tower = MagicMock()
    tower.front = TowerSide()
    tower.right = TowerSide()
    tower.back = TowerSide()
    tower.left = TowerSide()

    for side_name, raw_boxes in sides.items():
        level = Level()
        for raw in raw_boxes:
            level.add_box(Boxface(
                int(raw["x1"]), int(raw["y1"]),
                int(raw["x2"]), int(raw["y2"]),
                raw.get("is_hole", False), 0
            ))
        getattr(tower, side_name).add_level(level)
    return tower


def test_algorithm2_reads_four_sides():
    tmpdir = tempfile.mkdtemp()
    try:
        sides = {
            "front": [box(0, 0, 10, 10)],
            "right": [box(0, 0, 10, 10)],
            "back": [box(0, 0, 10, 10)],
            "left": [box(0, 0, 10, 10)],
        }
        tower_path = create_tower_data(tmpdir, sides)
        algo = Algorithm2()
        mocked_tower = _build_levels_from_sides(sides)
        with patch("algorithms.algorithm2.Tower", return_value=mocked_tower):
            result = algo.solve(tower_path)
        # All four sides have one non-hole box; front all => 1, others slices => 0
        assert result == 1
    finally:
        shutil.rmtree(tmpdir)


def test_separate_in_columns_groups_by_xcenter():
    algo = Algorithm2()
    level = Level()
    level.add_box(Boxface(0, 0, 10, 10, False, 1))
    level.add_box(Boxface(20, 0, 30, 10, False, 2))
    level.add_box(Boxface(0, 20, 10, 30, False, 3))
    columns = algo.separate_in_columns(level)
    assert len(columns) == 2


def test_separate_in_columns_sorts_left_to_right():
    algo = Algorithm2()
    level = Level()
    # All boxes must share the same cast vertical line (xcenter) so they are grouped.
    # xcenter of each box must fall inside the x-range of every other box.
    level.add_box(Boxface(100, 0, 110, 10, False, 1))  # xcenter=105
    level.add_box(Boxface(0, 0, 120, 10, False, 2))    # xcenter=60, overlaps 105
    level.add_box(Boxface(50, 0, 115, 10, False, 3))   # xcenter=82, overlaps both
    columns = algo.separate_in_columns(level)
    assert len(columns) == 1
    ids = [face.id for face in columns[0]["faces"]]
    assert ids == [2, 3, 1]


def test_algorithm2_counts_non_hole_faces():
    tmpdir = tempfile.mkdtemp()
    try:
        sides = {
            "front": [box(0, 0, 10, 10), box(10, 0, 20, 10)],
            "right": [box(0, 0, 10, 10), box(10, 0, 20, 10)],
            "back": [box(0, 0, 10, 10), box(10, 0, 20, 10)],
            "left": [box(0, 0, 10, 10), box(10, 0, 20, 10)],
        }
        tower_path = create_tower_data(tmpdir, sides)
        algo = Algorithm2()
        mocked_tower = _build_levels_from_sides(sides)
        with patch("algorithms.algorithm2.Tower", return_value=mocked_tower):
            result = algo.solve(tower_path)
        # Per level: front all 2 + right[1:] 1 + back[1:] 1 + left[1:-1] 0 => 4
        assert result == 4
    finally:
        shutil.rmtree(tmpdir)


def test_algorithm2_skips_holes_in_count():
    tmpdir = tempfile.mkdtemp()
    try:
        sides = {
            "front": [box(0, 0, 10, 10), box(10, 0, 20, 10, is_hole=True)],
            "right": [box(0, 0, 10, 10), box(10, 0, 20, 10)],
            "back": [box(0, 0, 10, 10), box(10, 0, 20, 10)],
            "left": [box(0, 0, 10, 10), box(10, 0, 20, 10)],
        }
        tower_path = create_tower_data(tmpdir, sides)
        algo = Algorithm2()
        mocked_tower = _build_levels_from_sides(sides)
        with patch("algorithms.algorithm2.Tower", return_value=mocked_tower):
            result = algo.solve(tower_path)
        # front 1 non-hole + right[1:] 1 + back[1:] 1 + left[1:-1] 0 => 3
        assert result == 3
    finally:
        shutil.rmtree(tmpdir)
