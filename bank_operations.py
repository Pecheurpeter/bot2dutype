import pyautogui
import time
from PIL import ImageGrab
import traceback

bank_locations = {
    'astrub': ['bank/PNJ6.png', 'bank/PNJ7.png'],
    'bonta': ['bank/PNJ3.png', 'bank/PNJ1.png'],
    'brakmar': ['bank/PNJ3.png', 'bank/PNJ1.png'],
    'sufokia': ['bank/PNJ14.png', 'bank/PNJ13.png'],
    'amakna': ['bank/PNJ1.png', 'bank/PNJ2.png']
}

def find_and_click_bank_image():
    for location, image_path in bank_locations.items():
        for path in image_path:
            location = pyautogui.locateCenterOnScreen(path, confidence=0.8)
            if location:
                print(f"Found image {path} at location: {location}")
                pyautogui.click(location)
                time.sleep(1)
                return True
                time.sleep(1)
            else:
                print(f"Image {path} not found.")
            time.sleep(1)
    return False


def click_talk():
    try:
        location = pyautogui.locateCenterOnScreen('bank/parler.png')
        if location:
            pyautogui.click(location)
            print("Clicked on 'talk' button.")
            time.sleep(1)
    except Exception as e:
        print(f"Error in click_talk: {e}")
        traceback.print_exc()


def click_in_region():
    try:
        region = (319, 446, 572, 44)
        x, y = pyautogui.center(region)
        pyautogui.click(x, y)
        print("Clicked in specified region.")
        time.sleep(1)
    except Exception as e:
        print(f"Error in click_in_region: {e}")

def hold_alt_shift_and_drag(points):
    try:
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('shift')
        for start, end in points:
            pyautogui.moveTo(*start)
            pyautogui.moveTo(*end, duration=1)
        pyautogui.keyUp('shift')
        pyautogui.keyUp('ctrl')
        print("Completed alt-shift dragging.")
    except Exception as e:
        print(f"Error in hold_alt_shift_and_drag: {e}")

def ctrl_double_click_at(x, y):
    try:
        pyautogui.keyDown('ctrl')
        pyautogui.click(x, y, clicks=2)
        pyautogui.keyUp('ctrl')
        print(f"Control-double-clicked at ({x}, {y}).")
    except Exception as e:
        print(f"Error in ctrl_double_click_at: {e}")

def click_image(image_path):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
        if location:
            pyautogui.click(location)
            print(f"Clicked on {image_path}.")
            time.sleep(1)
            return True
    except Exception as e:
        print(f"Error in click_image with {image_path}: {e}")
    return False

def click_image_in_region(image_path, region):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, region=region, confidence=0.8)
        if location:
            pyautogui.click(location)
            print(f"Clicked on {image_path}.")
            time.sleep(1)
            return True
    except Exception as e:
        print(f"Error in click_image_in_region with {image_path}: {e}")
    return False

def go_to_bank():
    try:
        if find_and_click_bank_image():
            time.sleep(1)
            click_talk()
            time.sleep(1)
            click_in_region()

            # Define points for dragging
            points = [
                ((1312, 342), (1549, 353)), ((1547, 403), (1312, 405)),
                ((1314, 460), (1548, 459)), ((1550, 521), (1313, 518)),
                ((1312, 580), (1545, 578)), ((1548, 636), (1318, 634)),
                ((1317, 697), (1545, 700))
            ]

            search_region = (1270, 163, 352, 633)

            # Actions for 'divers.png'
            if click_image_in_region('bank/divers.png', search_region):
                hold_alt_shift_and_drag(points)
                ctrl_double_click_at(1316, 343)

            # Actions for 'ressources.png'
            if click_image_in_region('bank/ressources.png', search_region):
                hold_alt_shift_and_drag(points)
                ctrl_double_click_at(1316, 343)

            # Actions for 'equipement.png'
            if click_image_in_region('bank/equipement.png', search_region):
                hold_alt_shift_and_drag(points)
                ctrl_double_click_at(1316, 343)

            time.sleep(1)
            pyautogui.press('esc')

            print("Banking operation completed.")
            return True
    except Exception as e:
        print(f"Error in go_to_bank: {e}")
        return False