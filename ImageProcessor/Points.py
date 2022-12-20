from dataclasses import dataclass
from typing import List
import numpy as np
import cv2

@dataclass
class Points: 
    """
    Points Arrengement
    C  --  D
    |      |
    A  --  B
    """
    Point_A: List[int]
    Point_B: List[int]
    Point_C: List[int]
    Point_D: List[int]
    img_H: int
    img_W: int

    @property
    def Source(self):
        return np.int32([
            self.Point_A,
            self.Point_B,
            self.Point_C,
            self.Point_D 
        ])

    @property
    def Destination(self):
        return np.int32([
            [0, self.img_H],
            [self.img_W, self.img_H],
            [0, 0],
            [self.img_W, 0] 
        ])

    @property
    def src(self):
        return self.Source.astype('float32')

    @property
    def dst(self):
        return self.Destination.astype('float32')

    @property
    def M(self):
        return cv2.getPerspectiveTransform(self.src, self.dst)
    
    @property
    def Minv(self):
        return cv2.getPerspectiveTransform(self.dst, self.src)