import logging
import re

import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# import traceback
# from google_auth_oauthlib.flow import  InstalledAppFlow
# from googleapiclient.discovery import build
# from google.auth.transport.requests import Request


def close_and_quit_driver(driver):
    try:
        driver.close()
    except Exception as e:
        print("Error while closing the browser:", e)

    try:
        driver.quit()
    except Exception as e:
        print("Error while quitting the driver:", e)


# def save_last_checked_email_id(email_id):
#     print(f"Saving last checked email id: {email_id}")
#     with open('last_email_id.txt', 'w') as f:
#         f.write(email_id)
#
# def get_last_checked_email_id():
#     print("Getting last checked email id")
#     if os.path.exists('last_email_id.txt'):
#         with open('last_email_id.txt', 'r') as f:
#             print(f"Last checked email id: {f.read().strip()}")
#             return f.read().strip()
#     return None
# #
# def send_email(message):
#     message = MIMEText(message)
#     message['to'] = "Vpower99999@gmail.com"
#     message['from'] = "Vpower99999@gmail.com"
#     message['subject'] = "Error With Automation Script"
#     message = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}
#     message = (service.users().messages().send(userId="me", body=message).execute())
#     print('Message Id: %s' % message['id'])
#     return


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


# error_details = None
# # Set up Gmail API
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
# creds = None
#
# # Load the credentials
# if os.path.exists('token.pickle'):
#     with open('token.pickle', 'rb') as token:
#         creds = pickle.load(token)
#
# # If there are no valid credentials, authenticate
# if not creds or not creds.valid:
#     if creds and creds.expired and creds.refresh_token:
#         creds.refresh(Request())
#     else:
#         flow = InstalledAppFlow.from_client_secrets_file('creds.json', SCOPES)
#         creds = flow.run_local_server(port=0)
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#
# service = build('gmail', 'v1', credentials=creds)
#
# # The interval in seconds to check for new emails
# CHECK_INTERVAL = 10
# last_checked_email_id = get_last_checked_email_id()
#
# specific_email_address = "cash@square.com"
# query = f"from:{specific_email_address}"

def taichi(userid, amount, username, password):
    # Start a new instance of the Chrome browser
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 2)
    status = False
    msg = ""
    try:
        # Navigate to the login page
        driver.get("https://taichimasterpay.com/")

        username_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
        password_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))

        username_elem.send_keys(username)
        password_elem.send_keys(password)

        submit_btn = wait.until(EC.presence_of_element_located((By.ID, "btnLogin")))
        submit_btn.click()

        print("Switching to iframe")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frm_main_content")))
        print("Searching for user")
        usersearch_elem = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='ID,Account or Name']")))
        usersearch_elem.send_keys(userid)
        try:
            search_btn = wait.until(EC.presence_of_element_located((By.ID, "Button4")))
            search_btn.click()

            recharge_btn = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                      "//a[contains(@class, 'btn12') and contains(@class, 'btn-danger1') and contains(text(), 'Deposit')]")))
            recharge_btn.click()

            driver.switch_to.default_content()
        except:
            msg = "User Not Found"

        # Switch to the new iframe using its `src` attribute
        iframe_xpath = "//iframe[contains(@src, 'https://taichimasterpay.com/Module/AccountManager/GrantTreasure.aspx?param=')]"
        # driver.switch_to.frame(driver.find_element(By.XPATH, iframe_xpath))
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, iframe_xpath)))

        # Now, locate and interact with the desired element inside the iframe
        gold_elem = wait.until(EC.presence_of_element_located((By.ID, "txtAddGold")))
        gold_elem.send_keys(amount)

        recharge_btn = wait.until(EC.presence_of_element_located((By.ID, "Button1")))
        recharge_btn.click()
        status = True
    except Exception as e:
        logging.exception(e)
        msg = "Internal Server Error"
    finally:
        close_and_quit_driver(driver)
        return status, msg


def kirin(userid, amount, username, password):
    # Start a new instance of the Chrome browser
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 2)
    status = False
    msg = ""
    try:
        # Navigate to the login page
        driver.get("https://firekirin.xyz:8888/")

        while True:  # Start a loop to handle incorrect captchas
            # Find the username, password, and captcha input fields
            username_elem = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your username']")))
            password_elem = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your password']")))
            code_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Code']")))

            # Extract text from the captcha image
            captcha_element = wait.until(EC.presence_of_element_located((By.ID, "ImageCheck")))
            captcha_element.screenshot('captcha.png')
            captcha_text = extract_text_from_image('captcha.png')

            # Fill in the login form and submit
            username_elem.send_keys(username)
            password_elem.send_keys(password)
            print("Sending captcha")
            code_elem.send_keys(captcha_text)
            print("Sent captcha")
            submit_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "login-button-box")))
            submit_btn.click()

            # Check if the incorrect captcha message is displayed
            try:
                error_message = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//*[text()='The validation code you filled in is incorrect.']")))
                # If the message is found, clear the input fields and retry the loop
                driver.get("https://firekirin.xyz:8888/")
            except Exception as e:
                # If the error message is not found, it means login was successful, so break out of the loop
                break

        # Switch to iframe
        print("Switching to iframe")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frm_main_content")))
        print("Searching for user")
        try:
            usersearch_elem = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='ID,Account or NickName']")))
            usersearch_elem.send_keys(userid)

            search_btn = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                    "//a[contains(@class, 'btn13') and contains(@class, 'btn-danger1') and contains(text(), 'Search')]")))
            search_btn.click()

            update_btn_xpath = "//a[@style='padding:6px; display: inline-block; text-align: center;font-family: sans-serif; cursor: pointer; background-color: #007dce; color: white; font-size: 14px; border-radius: 8px;height:16px;width:48px' and starts-with(@onclick, 'updateSelect')]"
            update_btn = wait.until(EC.presence_of_element_located((By.XPATH, update_btn_xpath)))
            update_btn.click()

            recharge_btn = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                      "//a[contains(@class, 'btn12') and contains(@class, 'btn-danger') and contains(text(), 'Recharge')]")))
            recharge_btn.click()
        except:
            msg = ""
        driver.switch_to.default_content()

        # Switch to the new iframe using its `src` attribute
        iframe_xpath = "//iframe[contains(@src, 'https://firekirin.xyz:8888/Module/AccountManager/GrantTreasure.aspx?param=')]"
        # driver.switch_to.frame(driver.find_element(By.XPATH, iframe_xpath))
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, iframe_xpath)))

        # Now, locate and interact with the desired element inside the iframe
        gold_elem = wait.until(EC.presence_of_element_located((By.ID, "txtAddGold")))
        gold_elem.send_keys(amount)

        recharge_btn = wait.until(EC.presence_of_element_located((By.ID, "Button1")))
        recharge_btn.click()
        status = True
    except Exception as e:
        logging.exception(e)
        if msg == "":
            msg = "Internal Server Error"

    finally:
        close_and_quit_driver(driver)
        return status, msg


def vblink(userid, amount, username, password):
    # Start a new instance of the Chrome browser
    options = ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    status = False
    msg = ""
    try:
        # Navigate to the login page
        driver.get("https://gm.vblink777.club/#/login?redirect=%2Fmanage-user%2Faccount")
        wait = WebDriverWait(driver, 15)
        # Find the username and password fields (replace with actual element identifiers)
        # btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Buy')]")))
        username_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='User Name']")))
        password_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))

        # Input your credentials
        print("adding credentials")
        username_elem.send_keys(username)
        password_elem.send_keys(password)

        # Find the submit button and click it (replace with actual element identifier)
        # submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Login')]")))
        submit_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "el-button--primary")))
        submit_btn.click()

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "openSidebar")))

        # Redirect to a different page
        driver.get("https://gm.vblink777.club/#/manage-user/search")

        # Wait for the radio button to be clickable and then click on it
        player_account_radio_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[text()='Player account']/preceding-sibling::span[contains(@class, 'el-radio__input')]")))
        player_account_radio_btn.click()

        usersearch_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='Fill In AmountPlayer ID/Phone Number/Third Party Login']")))
        usersearch_elem.send_keys(userid)

        print("searching for user")
        # Wait for the OK button to be clickable and then click on it
        # ok_btn = wait.until(EC.element_to_be_clickable(
        #     (By.XPATH, "//button[contains(@class, 'el-button--primary') and .//span[text()='OK']]")))
        # ok_btn.click()
        try:
            ok_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[1]/div/div[2]/section/div/div[1]/form/div[3]/div/button")))

            ok_btn.click()
            set_score_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'el-button--warning') and .//span[text()='Set Score']]")))
            set_score_btn.click()
        except:
            msg = "User Not Found"
        amount_elem = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Set points : ie 100']")))
        amount_elem.send_keys(amount)

        # Wait for the OK button to be clickable and then click on it
        ok_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='m-ct-fm']//button/span[text()='OK']")))
        ok_button.click()
        status = True
    except Exception as e:
        logging.exception(e)
        if msg == "":
            msg = "Internal Server Error"

    finally:
        close_and_quit_driver(driver)
        return status, msg
# while True:
#     # Fetch the latest email from the specific address
#     results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
#     try:
#
#         message = results.get('messages', [])[0]
#     except IndexError:
#         print("No emails")
#         continue
#
#     # If the latest email ID is different from the last checked email ID, run your main script
#     if message['id'] != last_checked_email_id:
#         msg = service.users().messages().get(userId='me', id=message['id']).execute()
#         # Get the subject line
#         for headers in msg['payload']['headers']:
#             if headers['name'] == 'Subject':
#                 subject = headers['value']
#                 print(f"Subject: {subject}", message['id'])
#                 # Subject format Alexandra Williams sent you $15, if it is not in this format, skip (make sure sent you is there)
#                 if 'sent you' not in subject or 'You accepted' not in subject:
#                     print("Invalid subject")
#                     last_checked_email_id = message['id']
#                     save_last_checked_email_id(last_checked_email_id)
#                     continue
#
#
#         # Decode the email body
#         email_body = subject
#         # Extract the amount and description
#         amount_pattern = r"sent you \$(\d+)"
#         reason_pattern = r"for (\w+)\s+(\w+)"
#
#         # Extracting the amount and reason from the decoded_body
#         amount_match = re.search(amount_pattern, email_body)
#         reason_match = re.search(reason_pattern, email_body)
#         try:
#             amount = str(int(amount_match.group(1))) if amount_match else None
#             userid = reason_match.group(1) if reason_match else None
#             platform = reason_match.group(2)[0] if reason_match and len(reason_match.group(2)) > 0 else None
#
#             if not amount or not userid or not platform:
#                 # Regular expression pattern to extract the amount
#                 amount_pattern = r"\$(\d+)"
#                 # Regular expression pattern to extract the reason (user ID and platform)
#                 reason_pattern = r"for (\w+)(?: \w+)*"
#                 amount_match = re.search(amount_pattern, email_body)
#                 reason_match = re.search(reason_pattern, email_body)
#                 amount = str(int(amount_match.group(1))) if amount_match else None
#                 userid = reason_match.group(1) if reason_match else None
#                 platform = reason_match.group(2)[0] if reason_match and len(reason_match.group(2)) > 0 else None
#
#             # convert so small letter
#             platform = platform.lower()
#             print(amount, userid, platform)
#         except Exception as e:
#             print("Error:", e, userid)
#             error_details = f'Email Content: {email_body}. Invalid platform for user:{userid} with amount: amount'
#             send_email(error_details)
#             last_checked_email_id = message['id']
#             save_last_checked_email_id(last_checked_email_id)
#             continue
#
#         # platform = 't' # Testing
#
#         print(f"Amount: ${amount}")
#         print(f"Description: {userid}")
#
#         if platform == 'v' or platform == 'vblink' or platform == 'blink':
#             try:
#                 vblink(userid, amount)
#             except Exception as e:
#                 print("Error V", e)
#                 traceback.print_exc()
#                 error_details = "Error occurred while updating VBLink platform for user: " + userid + " with amount: " + amount + " Error: " + str(e)
#                 send_email(error_details)
#                 last_checked_email_id = message['id']
#                 save_last_checked_email_id(last_checked_email_id)
#                 continue
#         elif platform == 'f' or platform == 'firekirin' or platform == 'fire kirin' or platform == 'fire k':
#             try:
#                 kirin(userid, amount)
#             except Exception as e:
#                 print("Error F", e)
#                 traceback.print_exc()
#                 error_details = "Error occurred while updating Kirin platform for user: " + userid + " with amount: " + amount + " Error: " + str(e)
#                 send_email(error_details)
#                 last_checked_email_id = message['id']
#                 save_last_checked_email_id(last_checked_email_id)
#                 continue
#         elif platform == 't':
#             try:
#                 taichi(userid, amount)
#             except Exception as e:
#                 print("Error T", e)
#                 traceback.print_exc()
#                 error_details = "Error occurred while updating Taichi platform for user: " + userid + " with amount: " + amount + " Error: " + str(e)
#                 send_email(error_details)
#                 last_checked_email_id = message['id']
#                 save_last_checked_email_id(last_checked_email_id)
#                 continue
#         else:
#             print("Invalid platform")
#             error_details = f'Email Content: {email_body}. Invalid platform for user:{userid} with amount: amount'
#             send_email(error_details)
#             last_checked_email_id = message['id']
#             save_last_checked_email_id(last_checked_email_id)
#             continue
#         last_checked_email_id = message['id']
#         save_last_checked_email_id(last_checked_email_id)
#     else:
#         print("No new emails found.")
#
#     # Sleep for the specified interval before checking again
#
#     time.sleep(CHECK_INTERVAL)
