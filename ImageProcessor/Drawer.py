import numpy as np
import cv2
from ImageProcessor import Points

class Drawer:
    def __init__(self, img: np.ndarray, pts: Points) -> None:
        self.color_map = [(0, 255, 0), (255, 0, 0), (0, 128, 255), (0, 0, 255), (0,0,0)]
        self.img = img
        self.img_canvas = img.copy()
        self.pts = pts
        self.thickness = 2
        self.line_thickness = -1
        self.line_radius = 8

    def draw_line(self, level):
        self.color = self.color_map[level]
        self.img_canvas= cv2.line(self.img_canvas, self.pts.Point_C, self.pts.Point_D, color = self.color, thickness = self.thickness) 
        self.img_canvas = cv2.line(self.img_canvas, self.pts.Point_A, self.pts.Point_B, color = self.color, thickness = self.thickness)
        self.img_canvas = cv2.line(self.img_canvas, self.pts.Point_C, self.pts.Point_A, color = self.color, thickness = self.thickness)
        self.img_canvas = cv2.line(self.img_canvas, self.pts.Point_D, self.pts.Point_B, color = self.color, thickness = self.thickness)

    def draw_dot(self, level):
        self.color = self.color_map[level]
        for point in self.pts.Source:
            self.img_canvas = cv2.circle(self.img_canvas, point, radius=self.line_radius, color= self.color, thickness=self.line_thickness) 

    def get_warped_image(self):
        return cv2.warpPerspective(self.img, self.pts.M, (self.pts.img_W, self.pts.img_H))

    def get_segmented_image(self):
        return cv2.warpPerspective(self.get_warped_image(), self.pts.Minv, (self.pts.img_W, self.pts.img_H))

    def get_image(self):
        return self.img
        
    def get_image_canvas(self):
        return self.img_canvas