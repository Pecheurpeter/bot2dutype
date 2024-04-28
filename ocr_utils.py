import pytesseract
from PIL import ImageGrab
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_region(x, y, width, height, preprocess=False):
    screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    if preprocess:
        screenshot = preprocess_image(screenshot)
    text = pytesseract.image_to_string(screenshot)
    return text
