import json
import logging
import re
import email.utils
import pytesseract
import undetected_chromedriver as uc
from PIL import Image
from deathbycaptcha import deathbycaptcha
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_emails(user_auth, count=5):
    try:
        creds_data = json.loads(user_auth)
        creds = Credentials(
            token=creds_data["token"],
            refresh_token=creds_data["refresh_token"],
            token_uri=creds_data["token_uri"],
            client_id=creds_data["client_id"],
            client_secret=creds_data["client_secret"],
            scopes=creds_data["scopes"]
        )
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", maxResults=count).execute()
        messages = results.get("messages", [])

        emails = []
        for message in messages:
            email_data = service.users().messages().get(userId="me", id=message["id"]).execute()
            # emails.append(email_data)
            headers = email_data['payload']['headers']
            email_id = message["id"]
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
            sender_full = next((header['value'] for header in headers if header['name'] == 'From'), None)
            match = re.search(r'(?:"?(.*?)"?\s)?<(.*?)>', sender_full)
            sender_name = match.group(1) if match and match.group(1) else None
            sender_email = match.group(2) if match else sender_full
            email_date = next((header['value'] for header in headers if header['name'] == 'Date'), None)
            if email_date:
                email_datetime = email.utils.parsedate_to_datetime(email_date)
            else:
                email_datetime = None
            emails.append({
                'email_id': email_id,
                'subject': subject,
                'sender': sender_email,
                'sender_name': sender_name,
                'email_datetime': email_datetime

            })
        return emails
    except Exception as e:
        logging.exception(e)
        return None


def extract_using_GBC(path):
    username = "adeelkhan47"
    password = "Adeelk47!"

    # Initialize the client with your credentials
    client = deathbycaptcha.SocketClient(username, password)
    try:
        # Get your current balance
        # balance = client.get_balance()
        # print(f"Current Balance: {balance}")

        # Send the CAPTCHA for solving
        captcha = client.decode(path, timeout=60)  # Increased timeout for better chance of accurate solution
        if captcha:
            # The CAPTCHA was solved
            print(f"CAPTCHA {captcha['captcha']} solved: {captcha['text']}")
            return captcha['text']
        else:
            print("CAPTCHA was not solved")
            return "0000"

    except deathbycaptcha.AccessDeniedException as e:
        print(f"Access denied: {e}")
        return "0000"
    except Exception as e:
        # Handle any other errors that might occur
        logging.exception(f"An error occurred: {e}")
        return "0000"


def close_and_quit_driver(driver):
    try:
        driver.close()
    except Exception as e:
        print("Error while closing the browser:", e)

    try:
        driver.quit()
    except Exception as e:
        print("Error while quitting the driver:", e)


def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR.

    Args:
    - image_path (str): path to the image from which text needs to be extracted

    Returns:
    - str: extracted text from the image
    """
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, config='outputbase digits')
    numeric_text = ''.join(re.findall(r'\d', text))

    if not numeric_text:
        return 0000

    return numeric_text


def get_mac_chrome_driver():
    options = ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    path_to_driver = ChromeDriverManager().install()
    driver = webdriver.Chrome(options=options)
    return driver


def get_ubuntu_chrome_driver() -> object:
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = '/usr/bin/google-chrome-stable'
    driver = uc.Chrome(options=options)
    return driver
