import pytesseract
from PIL import Image, ImageFilter
import requests
from io import BytesIO


def extract_text_from_image(image):
    # Convert to grayscale
    image = image.convert('L')

    # Apply adaptive thresholding
    image = image.filter(ImageFilter.MedianFilter())
    threshold_image = Image.new("L", image.size, 255)
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            pix = image.getpixel((x, y))
            threshold_image.putpixel((x, y), 0 if pix < 128 else 255)

    # OCR with config options
    config = '--psm 6'  # Assume a uniform block of text
    text = pytesseract.image_to_string(threshold_image, config=config)
    return text.strip()


image = Image.open(BytesIO(requests.get("https://agent.gamevault999.com/api/agent/captcha?t=1263").content))
print(extract_text_from_image(image))
