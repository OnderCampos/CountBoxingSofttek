import json
from box_face import Boxface


def create_faces(boxes: list):
    return [
        Boxface(
            int(box["x1"]),
            int(box["y1"]),
            int(box["x2"]),
            int(box["y2"]),
            False if "is_hole" not in box else box["is_hole"],
            i,
        )
        for i, box in enumerate(boxes, start=1)
    ]


def get_sides(tower_path):
    with open(f"{tower_path}/json/front.json") as f:
        front_side = create_faces(json.load(f))
    with open(f"{tower_path}/json/right.json") as f:
        right_side = create_faces(json.load(f))
    with open(f"{tower_path}/json/back.json") as f:
        back_side = create_faces(json.load(f))
    with open(f"{tower_path}/json/left.json") as f:
        left_side = create_faces(json.load(f))
    return front_side, right_side, back_side, left_side
