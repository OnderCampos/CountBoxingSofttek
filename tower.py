from level import Level
from kmeans import kmeans1
import cv2


class Side:
    def __init__(self) -> None:
        self.levels = []

    def add_level(self, level):
        self.levels.append(level)
    
    def sort(self):
        self.levels = sorted(self.levels, key=lambda level: level.getYcenter())


class Tower:
    def __init__(self, levels: 3) -> None:
        # Front, Right, Back, Left
        self.front = None
        self.right = None
        self.back = None
        self.left = None
        self.levels_num = levels

    def show_image(self,side_name ,levels, labels, image_path):
        image = cv2.imread(image_path)
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for level in levels:
            print("--------")
            for i, box in enumerate(level.boxes):
                # Define rectangle

                color = colors[1]  # Green color
                thickness = 5
                label_text = f"Rectangle {i}"
                print(i,box.x1)
                label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 3, 3)[0]
                center_x = int((box.x1 + box.x2) // 2)
                center_y = int((box.y1 + box.y2) // 2)
                text_origin = (center_x - label_size[0] // 2, center_y + label_size[1] // 2)
                cv2.putText(
                    image,
                    label_text,
                    text_origin,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    3,
                    (0, 0, 255),
                    3,
                )
                cv2.rectangle(
                    image,
                    (int(box.x1), int(box.y1)),
                    (int(box.x2), int(box.y2)),
                    color,
                    thickness,
                )

        cv2.imshow(side_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def show_levels(self, levels, image_path):
        image = cv2.imread(image_path)
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for i, level in enumerate(levels):
            # Define rectangle

            color = colors[1]  # Green color
            thickness = 10
            
            cv2.rectangle(
                image,
                (int(level.x1), int(level.y1)),
                (int(level.x2), int(level.y2)),
                color,
                thickness,
            )

        cv2.imshow("Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def add_side(self, side_name, side_box, image_path):
        # Cluster the boxes using only the ypos
        data = [box.ycenter for box in side_box]
        labels, centers = kmeans1(data, self.levels_num)
        label_dict = {label: [] for label in set(labels)}

        for label, number in zip(labels, side_box):
            label_dict[label].append(number)

        # Create levels and sides
        side = Side()
        # This is wrong

        for l in label_dict.keys():
            level = Level()
            for box in label_dict[l]:
                level.add_box(box)
            level.sort()
            side.add_level(level)
        side.sort()

        #self.show_levels(levels_list, image_path)
        #self.show_image(side_name, side.levels, labels, image_path)
        if side_name == "front":
            self.front = side
        if side_name == "right":
            self.right = side
        if side_name == "back":
            self.back = side
        if side_name == "left":
            self.left = side
