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

    def __build_tower(self, tower_path):
        front_side_faces, right_side_faces, back_side_faces, left_side_faces = (
            self.__get_sides(tower_path)
        )

        tower = Tower(levels=3)
        tower.add_side("front", front_side_faces, f"{tower_path}/images/front.jpg")
        tower.add_side("right", right_side_faces, f"{tower_path}/images/right.jpg")
        tower.add_side("back", back_side_faces, f"{tower_path}/images/back.jpg")
        tower.add_side("left", left_side_faces, f"{tower_path}/images/left.jpg")

        return tower

    def __sides_have_equal_levels(self, tower):
        levels = [
            len(tower.front.levels),
            len(tower.right.levels),
            len(tower.back.levels),
            len(tower.left.levels),
        ]
        return len(set(levels)) == 1

    def __count_non_holes_in_columns(self, columns, start=0, end=None):
        count = 0
        for column in columns[start:end]:
            for face in column["faces"]:
                if not face.is_hole():
                    count += 1
        return count

    def __count_level(self, front_columns, right_columns, back_columns, left_columns):
        count = 0
        count += self.__count_non_holes_in_columns(front_columns)
        count += self.__count_non_holes_in_columns(right_columns, 1)
        count += self.__count_non_holes_in_columns(back_columns, 1)
        count += self.__count_non_holes_in_columns(left_columns, 1, -1)
        return count

    def __count_boxes(self, tower):
        levels_size = len(tower.front.levels)
        count = 0
        for level_index in range(levels_size):
            front_columns = self.separate_in_columns(tower.front.levels[level_index])
            right_columns = self.separate_in_columns(tower.right.levels[level_index])
            back_columns = self.separate_in_columns(tower.back.levels[level_index])
            left_columns = self.separate_in_columns(tower.left.levels[level_index])
            count += self.__count_level(
                front_columns, right_columns, back_columns, left_columns
            )
        return count

    def solve(self, tower_path):
        tower = self.__build_tower(tower_path)
        if not self.__sides_have_equal_levels(tower):
            return None
        return self.__count_boxes(tower)
