import json
import cv2
import numpy as np

# Get boxes tower1/json/front_json.json

tower_path = "towers/tower6"
side = "right"

with open(f"{tower_path}/json/{side}.json") as f:
    front_boxes = json.load(f)

image = cv2.imread(f"{tower_path}/images/{side}.jpg")
background = np.zeros(image.shape, dtype=np.uint8)


# Sort the rectangles from up then right
def custom_sort(rectangle):
    return rectangle["y1"], rectangle["x1"]


sorted_rectangles = sorted(front_boxes, key=custom_sort)
# get the first line of boxes in every side


for i, box in enumerate(sorted_rectangles, start=1):
    # Define rectangle
    color = (0, 255, 0)  # Green color
    thickness = 2
    print(i,box)
    label_text = f"Rectangle {i}"
    label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 3, 3)[0]
    center_x = int((box["x1"] + box["x2"]) // 2)
    center_y = int((box["y1"] + box["y2"]) // 2)
    text_origin = (center_x - label_size[0] // 2, center_y + label_size[1] // 2)
    cv2.putText(
        background,
        label_text,
        text_origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        3,
        (255, 255, 255),
        3,
    )
    cv2.rectangle(
        background,
        (int(box["x1"]), int(box["y1"])),
        (int(box["x2"]), int(box["y2"])),
        color,
        thickness,
    )

cv2.imshow("Black Image with Rectangle", cv2.resize(background, (0, 0), fx=0.25, fy=0.25))
cv2.waitKey(0)
cv2.destroyAllWindows()
