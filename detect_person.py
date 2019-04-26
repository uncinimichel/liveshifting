from __future__ import print_function

import cv2

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

images_path = './test/test_images'
temp_boxes = './test/temp'


def convert_to_gaussian_blur(image):
    # Converting color image to gray_scale image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Converting gray scale image to GaussianBlur
    # so that change can be find easily
    return cv2.GaussianBlur(gray, (21, 21), 0)


# Return
def is_detection(base_image, current_image):
    motion = 0

    original_image = current_image.copy()
    base_image = convert_to_gaussian_blur(base_image)
    current_image = convert_to_gaussian_blur(current_image)

    # Difference between static background
    # and current frame(which is GaussianBlur)
    diff_frame = cv2.absdiff(base_image, current_image)

    # If change in between static background and
    # current frame is greater than 30 it will show white color(255)
    thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # Finding contour of moving object
    (cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in cnts:
        if cv2.contourArea(contour) < 8000:
            continue
        motion = 1
        (x, y, w, h) = cv2.boundingRect(contour)
        # making green rectangle around the moving object
        cv2.rectangle(original_image, (x, y), (x + w, y + h), (0, 255, 0), 3)

    if motion > 0:
        return True, original_image
    else:
        return False, None


def detect_persons_between_frames():
    # Assigning our static_back to None
    base_image = cv2.imread(images_path + "/no_person.jpeg")

    # for imagePath in paths.list_images(images_path):
    imagePath = images_path + "/no_person.jpeg"
    frame = cv2.imread(imagePath)

    filename = imagePath[imagePath.rfind("/") + 1:]

    detected, image = is_detection(base_image, frame)
    print(str(detected) + "  detecteddetecteddetected")
    if detected:
        cv2.imwrite(temp_boxes + "/" + filename + "_withBoxes.jpeg", image)


if __name__ == "__main__":
    detect_persons_between_frames()
