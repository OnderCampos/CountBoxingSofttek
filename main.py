import os
import json
from box_face import Boxface
from kmeans import kmeans, kmeans1, points_in_centroids
from algorithms.algorithm1 import Algorithm1
from algorithms.algorithm2 import Algorithm2
import matplotlib.pyplot as plt
from tower import Tower
import numpy as np
import cv2


class Main:

    def full_test(self, algorithm):
        tests = {
            "towers/tower1": 20,
            "towers/tower2": 30,
            "towers/tower3": 22,
            "towers/tower4": 24,
            "towers/tower5": 45,
            "towers/tower6": 28,
            "towers/tower7": 24,
            "towers/tower8": 33,
            "towers/tower9": 35,
            "towers/tower10": 37,
            "towers/tower11": 0,
        }

        total_correct = 0
        for test in tests:
            predicted_count = algorithm.solve(test)
            correct_count = tests[test]
            total_correct += int(predicted_count == correct_count)
            print(
                f"[{test}] predicted count: {predicted_count}, correct count: {correct_count}    venedict: {predicted_count==correct_count}"
            )
        print(f"Total: {total_correct}/{len(tests)}")


main = Main()
main.full_test(Algorithm1())
