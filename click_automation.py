import pyautogui
import time
import numpy as np 
import cv2
from image_processing import load_image

def find_and_click(images, confidence=0.8):
    templates = [load_image(img) for img in images]
    while True:
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        for template in templates:
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val >= confidence:
                top_left = max_loc
                h, w = template.shape[:2]
                center_x = top_left[0] + w // 2
                center_y = top_left[1] + h // 2
                pyautogui.moveTo(center_x, center_y)
                pyautogui.click()
                return True
        time.sleep(0.5)
