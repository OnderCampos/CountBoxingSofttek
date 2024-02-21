import math
import cv2

class Level:
    def __init__(self) -> None:
        self.boxes = []
        self.x1 = math.inf
        self.x2 = -math.inf
        self.y1 = math.inf
        self.y2 = -math.inf

    def add_box(self, box):
        self.x1 = min(self.x1, box.x1)
        self.y1 = min(self.y1, box.y1)
        self.x2 = max(self.x2, box.x2)
        self.y2 = max(self.y2, box.y2)
        self.boxes.append(box)

    def getYcenter(self):
        return self.y1 + abs(self.y1 - self.y2) // 2
    
    def sort(self):
        self.boxes = sorted(self.boxes, key = lambda box: box.ycenter)
    
    def __repr__(self):
        return str(self.boxes)
