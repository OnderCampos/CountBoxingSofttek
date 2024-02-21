import json
from box_face import Boxface

class Algorithm1:

    def __create_faces(self, boxes: list):
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
    
    def __get_sides(self, tower_path):
        front_side = []
        right_side = []
        back_side = []
        left_side = []
        with open(f"{tower_path}/json/front.json") as f:
            front_side = self.__create_faces(json.load(f))
        with open(f"{tower_path}/json/right.json") as f:
            right_side = self.__create_faces(json.load(f))
        with open(f"{tower_path}/json/back.json") as f:
            back_side = self.__create_faces(json.load(f))
        with open(f"{tower_path}/json/left.json") as f:
            left_side = self.__create_faces(json.load(f))
        return front_side, right_side, back_side, left_side

    def separate_in_lines(self, side_faces: list):
        """
        This algorithm runs in O(n*n)
        """
        lines = []
        while side_faces:
            current = side_faces.pop(0)
            cast_line = current.ycenter
            line = [current]
            remaining_faces = []
            for face in side_faces:
                if face.y1 < cast_line < face.y2:
                    line.append(face)
                else:
                    remaining_faces.append(face)
            side_faces = remaining_faces
            lines.append(
                {"cast_line": cast_line, "faces": sorted(line, key=lambda x: x.x1)}
            )

        return sorted(lines, key=lambda x: x["cast_line"])

    # Get the 4 sides
    def count_corner_holes(self, lineA, lineB):
        if lineA["faces"][-1].is_hole() and lineB["faces"][0].is_hole():
            return 1
        return 0

    def count_inner_holes(self, line):
        holes = 0
        for i in range(1, len(line["faces"]) - 1):
            if line["faces"][i].is_hole():
                holes += 1
        return holes

    def solve(self, tower_path):

        front_side_faces, right_side_faces, back_side_faces, left_side_faces = (
            self.__get_sides(tower_path)
        )
        # separete every side into lines
        front_lines = self.separate_in_lines(front_side_faces)
        right_lines = self.separate_in_lines(right_side_faces)
        back_lines = self.separate_in_lines(back_side_faces)
        left_lines = self.separate_in_lines(left_side_faces)

        # Count holes
        holes = 0
        if len(front_lines) == len(right_lines) == len(back_lines) == len(left_lines):
            for line_num in range(len(front_lines)):
                # check corners
                holes += (
                    self.count_corner_holes(
                        front_lines[line_num], right_lines[line_num]
                    )
                    + self.count_corner_holes(
                        right_lines[line_num], back_lines[line_num]
                    )
                    + self.count_corner_holes(
                        back_lines[line_num], left_lines[line_num]
                    )
                    + self.count_corner_holes(
                        left_lines[line_num], front_lines[line_num]
                    )
                )

                holes += (
                    self.count_inner_holes(front_lines[line_num])
                    + self.count_inner_holes(right_lines[line_num])
                    + self.count_inner_holes(back_lines[line_num])
                    + self.count_inner_holes(left_lines[line_num])
                )

        boxes_count = 0

        # Best case when are simetrical without holes
        for i in range(len(front_lines)):
            aprox_size = len(front_lines[i]["faces"]) * len(right_lines[i]["faces"])
            boxes_count += aprox_size

        # Adress holes
        return boxes_count - holes
