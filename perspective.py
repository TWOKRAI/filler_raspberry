import cv2
import numpy as np
import math


class Perspective:
    def __init__(self, image, point_img, point_real) -> None:
        self.image = image 
        self.img_width =  self.image.shape[1]
        self.img_height = self.image.shape[0]

        self.point = (0, 0)

        self.point1 = point_img[0]
        self.point2 = point_img[1]

        self.point3 = point_img[2]
        self.point4 = point_img[3]

        self.point_real_1 = point_real[0]
        self.point_real_2 = point_real[1]

        self.point_real_3 = point_real[2]
        self.point_real_4 = point_real[3]

        self.new_point = (0, 0)
        self.scale_point = (0, 0)

        self.center_1 = ((self.point1[0] + self.point3[0]) // 2, (self.point1[1] + self.point3[1]) // 2)
        self.center_2 = ((self.point2[0] + self.point4[0]) // 2, (self.point2[1] + self.point4[1]) // 2)

        self.angle_perspective = self.angle_between_segments((self.point1, self.point2),(self.center_1, self.center_2))
        self.angle = 0

        self.intersection_point = self.line_intersection([self.center_1, self.center_2], [self.point1, self.point2])

        self.intersection_point2 = (0, 0)

        self.intersection_point3 = self.line_intersection([(0, self.img_height),(self.img_width, self.img_height)], [self.point1, self.point2])
        self.intersection_point4 = self.line_intersection([(0, self.img_height),(self.img_width, self.img_height)], [self.point3, self.point4])
        self.intersection_point5 = (0, 0)


    # Вычисление точки пересечения отрезков
    def line_intersection(self, line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)

        if div == 0:
            return None

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div

        return (int(round(x)), int(round(y)))


    def angle_between_segments(self, segment1, segment2):
        # Вычисление векторов для отрезков
        vector1 = np.array(segment1[1]) - np.array(segment1[0])
        vector2 = np.array(segment2[1]) - np.array(segment2[0])

        # Вычисление длин векторов
        length1 = np.linalg.norm(vector1)
        length2 = np.linalg.norm(vector2)

        # Вычисление скалярного произведения векторов
        dot_product = np.dot(vector1, vector2)

        # Вычисление угла в радианах
        angle_rad = math.acos(dot_product / (length1 * length2))

        # Перевод угла в градусы
        angle_deg = round(math.degrees(angle_rad), 2)

        return angle_deg


    def get_sin_cos(self, point1, point2, angle_degrees):
        # Находим длину отрезка
        length = math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

        # Преобразуем угол из градусов в радианы
        angle_radians = angle_degrees * math.pi / 180.0

        # Находим синус и косинус угла
        sin_value = math.sin(angle_radians)
        cos_value = math.cos(angle_radians)

        # Находим новые координаты конца отрезка
        if point1[0] <= self.center_1[0]:
            new_x = point1[0] - length * sin_value
        else: 
            new_x = point1[0] + length * sin_value

        new_y = point2[1] - length * cos_value

        return  int(new_x), int(new_y)
    

    def transform_coord(self, point):
        self.point = point 

        self.intersection_point2 = self.line_intersection([(0, self.img_height),(self.img_width, self.img_height)], [point, self.intersection_point])
        
        self.intersection_point5 = self.line_intersection([self.point1, self.point3], [self.intersection_point, self.point])
        
        #self.angle = self.angle_between_segments((self.intersection_point2, point),(self.center_1, self.center_2))
        self.angle = self.angle_between_segments((self.intersection_point5, self.intersection_point),(self.center_1, self.center_2))

        new_x, new_y = self.get_sin_cos(self.point, self.intersection_point5, self.angle)
        #new_x, new_y = self.get_sin_cos(self.intersection_point2, point, self.angle)

        self.new_point = (new_x, new_y)

        return self.new_point
    

    def scale(self, pixel_point):
        # Вычисляем коэффициенты преобразования
        sx = (self.point_real_3[0] - self.point_real_1[0]) / (self.point3[0] - self.point1[0])
        sy = (self.point_real_2[1] - self.point_real_1[1]) / (self.point2[1] - self.point1[1])
        tx = self.point_real_1[0] - sx * self.point1[0]
        ty = self.point_real_1[1] - sy * self.point1[1]

        # Преобразуем точку
        x = sx * pixel_point[0] + tx
        y = sy * pixel_point[1] + ty

        y = y / (1.6 + y/1000)

        x = round(x, 1)
        y = round(y, 1)

        self.scale_point = (x, y)

        return self.scale_point


    def draw(self, image):
        cv2.line(image, self.center_1, self.center_2, (255, 0, 0), 2)
        cv2.line(image, self.point1, self.point2, (0, 255, 0), 2)
        cv2.line(image, self.point3, self.point4, (0, 255, 0), 2)

        cv2.circle(image, self.point1, 5, (120, 90, 255), -1)
        cv2.circle(image, self.point2, 5, (120, 90, 255), -1)
        cv2.circle(image, self.point3, 5, (120, 90, 255), -1)
        cv2.circle(image, self.point4, 5, (120, 90, 255), -1)

        cv2.circle(image, self.intersection_point, 8, (255, 0, 255), -1)
        cv2.circle(image, self.intersection_point2, 8, (255, 0, 255), -1)

        cv2.circle(image, self.intersection_point3, 8, (255, 0, 255), -1)
        cv2.circle(image, self.intersection_point4, 8, (255, 0, 255), -1)

        cv2.line(image, self.point1, self.point3, (70, 160, 160), 2)
        

        cv2.circle(image, self.intersection_point5, 8, (255, 0, 255), -1)

        cv2.line(image, self.intersection_point, self.point, (70, 160, 160), 2)

        cv2.circle(image, self.point, 5, (0, 90, 255),-1)
        cv2.line(image, self.intersection_point2, self.point, (120, 100, 160), 2)

        cv2.circle(image, (self.new_point[0], self.new_point[1]), 7, (0, 90, 255), -1)
        cv2.putText(image, f"{self.scale_point[0]}, {self.scale_point[1]}", (self.new_point[0] - 20, self.new_point[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.putText(image, f"1", (self.point1[0] + 5, self.point1[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(image, f"2", (self.point2[0] + 5, self.point2[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(image, f"3", (self.point3[0] + 5, self.point3[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(image, f"4", (self.point4[0] + 5, self.point4[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Вычисление высоты в точке пересечения
        height = self.img_height - self.intersection_point[1]

        cv2.putText(image, f"Height: {height} {self.intersection_point[1]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(image, f"Angle: {self.angle_perspective} ", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(image, f"Angle2: {self.angle} ", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)



# if __name__ == '__main__':
#     def nothing(x):
#         pass

#     # Размеры изображения
#     img_width = 640
#     img_height = 800

#     cv2.namedWindow( "Image" )
#     cv2.createTrackbar("x", "Image" , 220, img_height, nothing)
#     cv2.createTrackbar("y", "Image" , 700, img_height, nothing)

#     image = np.zeros((img_height, img_width, 3), dtype=np.uint8)

#     point1 = (180, 700)
#     point2 = (220, 540)

#     point3 = (460, 700)
#     point4 = (420, 540)

#     point_pixel = [(180, 700), (220, 540), (460, 700), (420, 540)]
#     point_real = [(10, 20), (10, 90), (70, 20), (70, 90)]

#     matrix = Perspective(image, point_pixel, point_real)


#     while True:
#         image = np.zeros((img_height, img_width, 3), dtype=np.uint8)

#         x = cv2.getTrackbarPos('x', "Image")
#         y = cv2.getTrackbarPos('y', "Image")
        
#         point = (x, y)

#         point = matrix.transform_coord(point)
#         point = matrix.scale(point)

#         matrix.draw(image)

#         cv2.imshow("Image", image)
#         cv2.waitKey(1)
