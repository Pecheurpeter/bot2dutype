import cv2
import numpy as np
import pyautogui
import time
import json
from PIL import ImageGrab
from click_automation import find_and_click
from ocr_utils import ocr_region
import ocr_utils
import re
import io
from image_processing import *
from bank_operations import go_to_bank
import sniffer  
import threading
import traceback
import pytesseract
from PIL import Image
import Combat.fight_utils
from bank_operations import *
import requests
import asyncio
from Combat.fight_utils import fight_mode

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

with open('script.json', 'r') as file:
    script_config = json.load(file)

jobs = script_config["jobs"]
initial_actions = script_config["actions"].copy()  
banking_actions = script_config.get("banking", []).copy()

current_map_id = "1332"  
previous_map_id = current_map_id
new_map_id = True  
banking_done = False  
last_clicked_job = None
image_cache = {}
fight_mode = False

region = (639, 239, 331, 363)

sniffer_thread = threading.Thread(target=sniffer.start_sniffing)
sniffer_thread.daemon = True
sniffer_thread.start()
threading.Thread(target=Combat.fight_utils.main).start()

job_images = {
    'chataigne': {'images': ['bois/chataigne.png','bois/chataigne2.png','bois/chataigne3.png','bois/chataigne4.png'], 'confidence': 0.9},
    'bombu': {'images': ['bois/bombu.png','bois/bombu2.png','bois/bombu3.png','bois/bombu4.png','bois/bombu5.png'], 'confidence': 0.9},
    'erable': {'images': ['bois/erable.png','bois/erable2.png','bois/erable3.png','bois/erable4.png'], 'confidence': 0.9},
    'if': {'images': ['bois/if.png'], 'confidence': 0.9},
    'merisier': {'images': ['bois/merisier.png','bois/merisier2.png','bois/merisier3.png','bois/merisier4.png'], 'confidence': 0.9},
    'ebene': {'images': ['bois/ebene.png','bois/ebene2.png','bois/ebene3.png'], 'confidence': 0.9},
    'noyer': {'images': ['bois/noyer.png','bois/noyer2.png','bois/noyer3.png','bois/noyer4.png'], 'confidence': 0.9},
    'olivet': {'images': ['bois/olivet.png','bois/olivet2.png'], 'confidence': 0.9},
    'chene': {'images': ['bois/chene.png','bois/chene2.png','bois/chene3.png'], 'confidence': 0.9},
    'frene': {'images': ['bois/frene.png', 'bois/frene2.png', 'bois/frene3.png', 'bois/frene4.png'], 'confidence': 0.9},
    'charme': {'images': ['bois/charme.png', 'bois/charme2.png', 'bois/charme3.png', 'bois/charme4.png'], 'confidence': 0.9},
    'orme': {'images': ['bois/orme.png', 'bois/orme2.png', 'bois/orme3.png', 'bois/orme4.png'], 'confidence': 0.9},
}

couper_image = {'path': 'bois/couper.png', 'confidence': 0.8}

def ocr_region_and_click(region, target_text):
    screenshot = pyautogui.screenshot(region=region)
    grayscale_image = screenshot.convert('L')
    ocr_data = pytesseract.image_to_data(grayscale_image, output_type=pytesseract.Output.DICT)

    print("Detected text and coordinates:")
    for i, text in enumerate(ocr_data['text']):
        if text.strip():
            x = ocr_data['left'][i] + region[0]
            y = ocr_data['top'][i] + region[1]
            print(f"'{text}' at ({x}, {y})")

    for i, text in enumerate(ocr_data['text']):
        if target_text in text:
            x = ocr_data['left'][i] + ocr_data['width'][i] // 2 + region[0]
            y = ocr_data['top'][i] + ocr_data['height'][i] // 2 + region[1]
            pyautogui.click(x, y)
            print(f"Clicked on '{text}' at ({x}, {y})")
            return True

    print(f"Text '{target_text}' not detected. Clicking 8 times on a designated point.")

    pyautogui.click(1287, 572)
    time.sleep(1)  

    pyautogui.click(1287, 572)
    time.sleep(1)  

    pyautogui.click(1287, 572)
    time.sleep(1)  

    pyautogui.click(1287, 572)
    time.sleep(1)  

    screenshot = pyautogui.screenshot(region=region)
    grayscale_image = screenshot.convert('L')
    ocr_data = pytesseract.image_to_data(grayscale_image, output_type=pytesseract.Output.DICT)

    for i, text in enumerate(ocr_data['text']):
        if target_text in text:
            x = ocr_data['left'][i] + ocr_data['width'][i] // 2 + region[0]
            y = ocr_data['top'][i] + ocr_data['height'][i] // 2 + region[1]
            pyautogui.click(x, y)
            print(f"Clicked on '{text}' at ({x}, {y}) after clicking 8 times on designated point.")
            return True

    print(f"Text '{target_text}' still not detected after clicking 8 times.")
    return False

def read_zaap_mappings():
    with open('zaap.json', 'r') as file:
        return json.load(file)

def open_zaap_menu():
    zaap_images = ['zaap/zaap.png', 'zaap/zaap2.png', 'zaap/zaap3.png', 'zaap/zaap4.png', 'zaap/zaap5.png']
    for image_path in zaap_images:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=0.8)
            if location:
                pyautogui.click(pyautogui.center(location))
                print(f"Clicked on {image_path} to open zaap menu.")
                time.sleep(1)  

                utiliser_location = pyautogui.locateOnScreen('zaap/utiliser.png', confidence=0.8)
                if utiliser_location:
                    pyautogui.click(pyautogui.center(utiliser_location))
                    print("Clicked on utiliser.png after opening zaap menu.")
                    time.sleep(5)  
                    return True
                else:
                    print("Failed to find utiliser.png after opening zaap menu.")
                    return False

        except pyautogui.ImageNotFoundException:
            continue  
    print("Failed to find zaap menu button.")
    return False

def teleport_to_location(tp_coordinates):
    zaap_mappings = read_zaap_mappings()
    target_location = zaap_mappings.get(tp_coordinates)
    if not target_location:
        print(f"Destination {tp_coordinates} not found in zaap mappings.")
        return

    if not open_zaap_menu():
        print("Opening zaap menu failed.")
        return

    if not ocr_region_and_click(region, target_location):
        print(f"Failed to teleport to {target_location}.")
    else:
        print(f"Teleported to {target_location} successfully.")

def execute_actions(actions, current_map_id):
    for action in actions:
        if action['type'] == 'click' and str(action.get('mapid', '')) == current_map_id:
            if 'coordinates' in action:
                coordinates = action['coordinates']
                for coordinate in coordinates:
                    pyautogui.click(x=coordinate['x'], y=coordinate['y'])
                    print(f"Clicked at coordinates ({coordinate['x']}, {coordinate['y']}) on map {current_map_id}")
                    if 'delay' in coordinate:
                        time.sleep(coordinate['delay'])
                    else:
                        time.sleep(1)  
            else:
                pyautogui.click(x=action['x'], y=action['y'])
                print(f"Clicked at coordinates ({action['x']}, {action['y']}) on map {current_map_id}")
        elif action['type'] == 'zaap' and str(action.get('mapid', '')) == current_map_id:
            teleport_to_location(action['tp'])
            time.sleep(1)  

def execute_banking_actions(banking_actions, current_map_id):
    for action in banking_actions:
        if action['type'] == 'banking' and str(action.get('mapid', '')) == current_map_id:
            place = action.get('place', '')
            print(f"Executing banking operations for place: {place} on map {current_map_id}")

            if go_to_bank():
                print("Banking operation completed.")

                sniffer.current_pods_percentage = 0  
                print("Pods reset to empty after banking.")
            else:
                print("Failed to complete banking operation.")

            break

        elif action['type'] == 'click' and str(action.get('mapid', '')) == current_map_id:
            if 'coordinates' in action:
                coordinates = action['coordinates']
                for coordinate in coordinates:
                    pyautogui.click(x=coordinate['x'], y=coordinate['y'])
                    print(f"Clicked at coordinates ({coordinate['x']}, {coordinate['y']}) on map {current_map_id}")
                    if 'delay' in coordinate:
                        time.sleep(coordinate['delay'])
                    else:
                        time.sleep(1)
            else:
                pyautogui.click(x=action['x'], y=action['y'])
                print(f"Clicked at coordinates ({action['x']}, {action['y']}) on map {current_map_id}")

def get_map_id():
    return sniffer.get_last_map_id()

def check_for_and_interact_with_images():
    global fight_mode
    
    try:
        if fight_mode:
            print("Currently in fight mode. Skipping interaction with job images.")
            return False

        resources_found = False  
        while True:
            found_resource_in_this_iteration = False

            for job in jobs:
                job_info = job_images.get(job, {})
                for image_name in job_info.get('images', []):
                    if fight_mode:
                        print("Entered fight mode. Stopping interaction with job images.")
                        return resources_found

                    found = interact_with_images(image_name, job_info.get('confidence', 0.8))
                    if found:
                        print(f"Clicked on an image for job: {job}")
                        handle_lvl_up_popup()
                        resources_found = True
                        found_resource_in_this_iteration = True

                        if job in ['chataigne', 'bombu', 'erable', 'if', 'merisier', 'ebene', 'noyer', 'olivet', 'chene', 'frene', 'charme', 'orme']:
                            couper_found = interact_with_images(couper_image['path'], couper_image['confidence'])
                            if couper_found:
                                print("Clicked on 'couper' image after '{job}'. Waiting for packet event.")
                                event_is_set = sniffer.general_packet_received_event.wait(timeout=15)
                                if event_is_set:
                                    print("General packet received. Continuing.")
                                else:
                                    print("Timeout reached without packet. Continuing.")
                                time.sleep(1)
                                sniffer.general_packet_received_event.clear()

                    if found_resource_in_this_iteration:
                        break

                if found_resource_in_this_iteration:
                    break

            if not found_resource_in_this_iteration:
                break

        return resources_found
    except Exception as e:
        print(f"Error in check_for_and_interact_with_images: {e}")
        traceback.print_exc()
        return False

def handle_lvl_up_popup():
    try:
        print("Checking for level-up popup...")

        print("Looking for popup image at 'utils/lvlup.png' with higher confidence.")
        lvl_up_location = pyautogui.locateCenterOnScreen('utils/lvlup.png', confidence=0.8)
        if lvl_up_location:
            print("Level-up popup found at location:", lvl_up_location)
            print("Clicking on level-up popup...")
            pyautogui.click(lvl_up_location)
            print("Clicked on level-up popup.")
            time.sleep(2)  
        else:
            print("Level-up popup not found.")
    except pyautogui.ImageNotFoundException as e:
        print("Level-up popup image not found. Exception:", e)
    except Exception as e:
        print(f"Unhandled error in handle_lvl_up_popup: {e}")

def load_and_cache_image(image_path):
    global image_cache
    if image_path not in image_cache:
        try:
            image = Image.open(image_path)
            image_cache[image_path] = image
            print(f"Image loaded and cached: {image_path}")
        except FileNotFoundError:
            print(f"File not found: {image_path}")
            return None
    return image_cache[image_path]

def interact_with_images(image_name, confidence):
    global last_clicked_job  

    try:

        image = load_and_cache_image(image_name)
        if image is None:
            return False  

        location = pyautogui.locateCenterOnScreen(image, confidence=confidence)
        if location:
            pyautogui.click(location)
            time.sleep(1)  

            if 'couper.png' in image_name and last_clicked_job:

                try:
                    asyncio.run(update_click_count_in_database_async(last_clicked_job))
                except RuntimeError as e:
                    print(f"Error running async database update: {e}")
                last_clicked_job = None  
            else:

                job_name = image_name.split('/')[1].split('.')[0]
                last_clicked_job = job_name

            return True
    except pyautogui.ImageNotFoundException:
        return False

async def update_click_count_in_database_async(job_name):
    SUPABASE_URL = ''
    SUPABASE_KEY = ''
    TABLE_NAME = 'job_clicks'

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"

    response = requests.get(url + f"?job_name=eq.{job_name}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            record = data[0]
            click_count = record['click_count'] + 1
            record_id = record['id']

            update_response = requests.patch(url + f"?id=eq.{record_id}",
                                             json={"click_count": click_count},
                                             headers=headers)
            if update_response.status_code in (200, 201):
                print(f"Successfully updated click count for {job_name}")
            else:
                print("Failed to update click count")
        else:

            create_response = requests.post(url,
                                            json={"job_name": job_name, "click_count": 1},
                                            headers=headers)
            if create_response.status_code in (200, 201):
                print(f"Successfully created new click count record for {job_name}")
            else:
                print("Failed to create new click count record")
    else:
        print("Failed to retrieve job click count from database")

last_executed_map_id = None

try:
    while True:

        fight_mode = Combat.fight_utils.fight_mode

        if fight_mode:
            continue  

        if not sniffer.map_id_queue.empty():
            current_map_id = sniffer.map_id_queue.get()
            print(f"Updated current map ID: {current_map_id}")
            banking_done = False
            new_map_id = True
            print(f"Map ID changed to {current_map_id}. Sleeping for 2 seconds...")
            time.sleep(2)

        if sniffer.general_packet_received_event.is_set():
            sniffer.general_packet_received_event.clear()  
            print("Resuming actions post-fight...")

            new_map_id = True

        if sniffer.current_pods_percentage > 90 and not banking_done:
            print("90% PODS, going banking!")
            execute_banking_actions(banking_actions, current_map_id)
            banking_done = True
            print("Banking operation executed.")

        if banking_done and sniffer.current_pods_percentage <= 90:
            banking_done = False
            print("Inventory not full. Resuming normal actions.")

        if not banking_done and new_map_id:
            interacted_with_jobs = check_for_and_interact_with_images()
            if interacted_with_jobs:
                handle_lvl_up_popup()
                print("Interacted with job images. Checking for new map ID or more images.")

            map_ids_in_actions = [str(action.get('mapid', '')) for action in initial_actions]
            if current_map_id in map_ids_in_actions:
                execute_actions(initial_actions, current_map_id)
                handle_lvl_up_popup()

            new_map_id = False

        initial_actions = script_config["actions"].copy()  
        time.sleep(1)  

except FileNotFoundError as e:
    print("File not found:", e.filename)
except Exception as e:
    print("An error occurred:", str(e))