import math


class Boxface:
    def __init__(self, x1: int, y1: int, x2: int, y2: int, is_hole: bool, id: int) -> None:
        self.id = id
        self.__is_hole = is_hole
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.id = id
        self.xcenter = self.__cal_center(self.x1, self.x2)
        self.ycenter = self.__cal_center(self.y1, self.y2)

    def __cal_center(self, v1: int, v2: int):
        return v1 + (abs(v1 - v2) // 2)
    
    def get_center(self):
        return (self.xcenter, self.ycenter)
    
    def set_id(self, id: int):
        self.id = id
        
    def is_hole(self):
        return self.__is_hole
    
    def __repr__(self) -> str:
        return str(self.id)
    
