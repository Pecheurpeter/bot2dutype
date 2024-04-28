from PIL import ImageGrab
import pyautogui
import time
import math

def is_red(pixel):
    r, g, b = pixel
    return r > 200 and g < 100 and b < 100

def is_blue(pixel):
    r, g, b = pixel
    return r < 100 and g < 100 and b > 180

def is_orange(pixel):
    r, g, b = pixel
    return r > 200 and g > 100 and b < 100

def is_green(pixel):
    r, g, b = pixel
    tolerance = 10
    return (85 - tolerance <= r <= 85 + tolerance) and \
           (137 - tolerance <= g <= 137 + tolerance) and \
           (91 - tolerance <= b <= 91 + tolerance)

def is_outline_pixel(image, x, y, color_check_function):
    if color_check_function(image.getpixel((x, y))):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    nx, ny = x + dx, y + dy
                    if nx < 0 or ny < 0 or nx >= image.width or ny >= image.height:
                        return True
                    if not color_check_function(image.getpixel((nx, ny))):
                        return True
    return False

def find_circle(region, color_check_function):
    left, top, width, height = region
    screenshot = pyautogui.screenshot(region=region)
    for x in range(screenshot.width):
        for y in range(screenshot.height):
            if is_outline_pixel(screenshot, x, y, color_check_function):
                return (left + x, top + y)
    return None

def is_not_gray(pixel, tolerance=10):
    r, g, b = pixel
    return not (abs(r - g) <= tolerance and abs(g - b) <= tolerance and abs(b - r) <= tolerance)

def find_nearest_green_to_blue(region, blue_position):
    screenshot = pyautogui.screenshot(region=region)
    green_positions = []  

    for x in range(0, screenshot.width, 20):
        for y in range(0, screenshot.height, 20):
            if is_green(screenshot.getpixel((x, y))):
                green_position = (region[0] + x, region[1] + y)
                green_positions.append(green_position)

    green_positions.sort(key=lambda pos: ((pos[0] - blue_position[0]) ** 2 + (pos[1] - blue_position[1]) ** 2) ** 0.5)

    orange_detected = False

    for green_position in green_positions:
        pyautogui.moveTo(green_position[0], green_position[1])  
        time.sleep(1)  

        wider_region = (green_position[0] - 20, green_position[1] - 20, 40, 40)
        screenshot_region = pyautogui.screenshot(region=wider_region)

        for x in range(screenshot_region.width):
            for y in range(screenshot_region.height):
                if is_orange(screenshot_region.getpixel((x, y))):
                    print("Orange color detected at:", green_position)
                    return green_position

        print("No orange color detected at:", green_position)

    print("No orange color detected in any of the green pixel locations.")
    return None

def adjust_click_position(nearest_green, blue_position):

    direction_x = blue_position[0] - nearest_green[0]
    direction_y = blue_position[1] - nearest_green[1]

    norm = (direction_x ** 2 + direction_y ** 2) ** 0.5
    direction_x /= norm
    direction_y /= norm

    adjustment_distance = -5  
    click_x = int(nearest_green[0] + direction_x * adjustment_distance)
    click_y = int(nearest_green[1] + direction_y * adjustment_distance)
    return click_x, click_y

region_to_capture = (282, 23, 1353, 783)
red_circle_position = find_circle(region_to_capture, is_red)
blue_circle_position = find_circle(region_to_capture, is_blue)

if red_circle_position and blue_circle_position:
    distance = math.sqrt((red_circle_position[0] - blue_circle_position[0]) ** 2 + (red_circle_position[1] - blue_circle_position[1]) ** 2)
    print("Distance between red and blue circles:", distance)
    if distance >= 55:
        pyautogui.moveTo(red_circle_position[0], red_circle_position[1])
        time.sleep(1)
        nearest_green_position = find_nearest_green_to_blue(region_to_capture, blue_circle_position)
        if nearest_green_position:
            click_position = adjust_click_position(nearest_green_position, blue_circle_position)
            pyautogui.click(click_position[0], click_position[1])
    else:
        print("Red and blue circles are too close to each other. Skipping further processing.")
else:
    print("Red or blue circle not found. Skipping further processing.")
