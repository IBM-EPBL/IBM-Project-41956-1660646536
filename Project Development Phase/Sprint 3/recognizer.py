# importing required libraries
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
import math
from keras.models import load_model

# loading pre trained model
model = load_model("models/digit_classifier.h5")

# predicting the digit
def predict_digit(img):
    test_image = img.reshape(-1, 28, 28, 1)
    return np.argmax(model.predict(test_image))


# refining each digit
def image_refiner(gray):
    org_size = 22
    img_size = 28
    rows, cols = gray.shape

    if rows > cols:
        factor = org_size / rows
        rows = org_size
        cols = int(round(cols * factor))
    else:
        factor = org_size / cols
        cols = org_size
        rows = int(round(rows * factor))
    gray = cv2.resize(gray, (cols, rows))

    # get padding
    colsPadding = (
        int(math.ceil((img_size - cols) / 2.0)),
        int(math.floor((img_size - cols) / 2.0)),
    )
    rowsPadding = (
        int(math.ceil((img_size - rows) / 2.0)),
        int(math.floor((img_size - rows) / 2.0)),
    )

    # apply padding
    gray = np.lib.pad(gray, (rowsPadding, colsPadding), "constant")
    return gray


# getting the predicted
def get_output(path):
    img = cv2.imread(path, 2)
    img_org = cv2.imread(path)

    ret, thresh = cv2.threshold(img, 127, 255, 0)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
    )

    predicted_values = []

    for j, cnt in enumerate(contours):
        epsilon = 0.01 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        hull = cv2.convexHull(cnt)
        k = cv2.isContourConvex(cnt)
        x, y, w, h = cv2.boundingRect(cnt)

        if hierarchy[0][j][3] != -1 and w > 10 and h > 10:
            # cropping each image and process
            roi = img[y : y + h, x : x + w]
            roi = cv2.bitwise_not(roi)
            roi = image_refiner(roi)
            th, fnl = cv2.threshold(roi, 127, 255, cv2.THRESH_BINARY)

            # getting prediction of cropped image
            pred = predict_digit(roi)
            predicted_values.append(pred)

    return predicted_values


if __name__ == "__main__":
    recognized_digits = get_output(path="static/images/1.png")
    print(recognized_digits)
