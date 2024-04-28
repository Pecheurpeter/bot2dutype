import cv2
import numpy as np
from PIL import Image
from PIL import ImageGrab

def load_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    if image.shape[2] == 4: 
        alpha_channel = image[:, :, 3]
        _, mask = cv2.threshold(alpha_channel, 254, 255, cv2.THRESH_BINARY)
        color = image[:, :, :3]
        image = cv2.bitwise_and(color, color, mask=mask)
    return image

def preprocess_image(image):
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh_image)

def is_bar_90_percent_full(region):
    screenshot = ImageGrab.grab(bbox=region)
    screenshot_np = np.array(screenshot)

    filled_lower = np.array([52, 190, 96])
    filled_upper = np.array([52, 190, 96])
    unfilled_lower = np.array([60, 74, 81])
    unfilled_upper = np.array([60, 74, 81])

    screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)
    filled_mask = cv2.inRange(screenshot_rgb, filled_lower, filled_upper)
    unfilled_mask = cv2.inRange(screenshot_rgb, unfilled_lower, unfilled_upper)

    filled_area = cv2.countNonZero(filled_mask)
    total_area = filled_area + cv2.countNonZero(unfilled_mask)
    percentage_filled = (filled_area / total_area) * 100

    return percentage_filled >= 90