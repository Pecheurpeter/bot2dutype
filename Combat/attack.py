import cv2
import numpy as np
import pyautogui
import time
import keyboard

def find_blue_circle(region):
    left, top, width, height = region
    while True:
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        for x in range(screenshot.shape[1]):
            for y in range(screenshot.shape[0]):
                if is_blue_outline_pixel(screenshot, x, y):
                    pyautogui.moveTo(left + x, top + y, duration=0)
                    time.sleep(1)
                    pyautogui.click(left + x, top + y)
                    return

def is_blue_outline_pixel(image, x, y):
    if is_blue(image[y, x]):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    if not is_blue(image[y + dy, x + dx]):
                        return True
        return False
    return False

def is_blue(pixel):
    return pixel[0] > 180 and pixel[1] < 100 and pixel[2] < 100

def find_and_click_image():
    keyboard.press_and_release('&')
    time.sleep(1)

    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    region_to_capture = (282, 23, 1353, 783)  
    find_blue_circle(region_to_capture)

    pyautogui.press('f1') 
    time.sleep(1)

if __name__ == "__main__":
    find_and_click_image()
