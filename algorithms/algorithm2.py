import os
import json
from box_face import Boxface
from kmeans import kmeans, kmeans1, points_in_centroids
import matplotlib.pyplot as plt
from tower import Tower
import numpy as np
import cv2

class Algorithm2:

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

    def separate_in_columns(self, level: list):
        """
        This algorithm runs in O(n*n)
        """
        lines = []
        aux_level = level.boxes
        while aux_level:
            current = aux_level.pop(0)
            cast_line = current.xcenter
            line = [current]
            remaining_faces = []
            for face in aux_level:
                if face.x1 < cast_line < face.x2:
                    line.append(face)
                else:
                    remaining_faces.append(face)
            aux_level = remaining_faces
            lines.append(
                {"cast_line": cast_line, "faces": sorted(line, key=lambda x: x.x1)}
            )

        return sorted(lines, key=lambda x: x["cast_line"])

    def solve(self, tower_path):

        front_side_faces, right_side_faces, back_side_faces, left_side_faces = (
            self.__get_sides(tower_path)
        )

        tower = Tower(levels=3)
        tower.add_side("front", front_side_faces, f"{tower_path}/images/front.jpg")
        tower.add_side("right", right_side_faces, f"{tower_path}/images/right.jpg")
        tower.add_side("back", back_side_faces, f"{tower_path}/images/back.jpg")
        tower.add_side("left", left_side_faces, f"{tower_path}/images/left.jpg")

        front_levels = tower.front.levels
        right_levels = tower.right.levels
        back_levels = tower.back.levels
        left_levels = tower.left.levels

        if (
            len(front_levels)
            == len(right_levels)
            == len(back_levels)
            == len(left_levels)
        ):
            # fronts levels with rights
            levels_size = len(front_levels)
            count = 0

            for level in range(levels_size):

                front_columns = self.separate_in_columns(front_levels[level])
                right_columns = self.separate_in_columns(right_levels[level])
                back_columns = self.separate_in_columns(back_levels[level])
                left_columns = self.separate_in_columns(left_levels[level])

                for column in front_columns:
                    for box_face in column["faces"]:
                        if not box_face.is_hole():
                            count += 1

                for column in right_columns[1::]:
                    for box_face in column["faces"]:
                        if not box_face.is_hole():
                            count += 1

                for column in back_columns[1::]:
                    for box_face in column["faces"]:
                        if not box_face.is_hole():
                            count += 1

                for column in left_columns[1:-1]:
                    for box_face in column["faces"]:
                        if not box_face.is_hole():
                            count += 1

            return count
