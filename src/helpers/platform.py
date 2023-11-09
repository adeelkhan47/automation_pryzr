import logging
import re
import time

import pytesseract
import undetected_chromedriver as uc
from PIL import Image, ImageFilter
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from helpers.common import extract_using_GBC


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


def taichi(userid, amount, username, password):
    # Start a new instance of the Chrome browser
    # options = ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = '/usr/bin/google-chrome-stable'
    driver = uc.Chrome(options=options)

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
        try:
            print("Switching to iframe")
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frm_main_content")))
            print("Searching for user")
            usersearch_elem = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='ID,Account or Name']")))
            usersearch_elem.send_keys(userid)

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
    tries = 2
    while (tries >= 1):
        # options = ChromeOptions()
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # path_to_driver = ChromeDriverManager().install()
        # driver = webdriver.Chrome(options=options)
        ##
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = '/usr/bin/google-chrome-stable'
        driver = uc.Chrome(options=options)
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
                msg = "User Not Found"
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
            tries -= 1
            if status:
                return status, msg
            if msg == "Internal Server Error" and tries < 1:
                return status, msg


def vblink(userid, amount, username, password):
    # Start a new instance of the Chrome browser
    # options = ChromeOptions()
    # #options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    ##
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = '/usr/bin/google-chrome-stable'
    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 2)

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
        try:

            player_account_radio_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//span[text()='Player account']/preceding-sibling::span[contains(@class, 'el-radio__input')]")))
            player_account_radio_btn.click()

            usersearch_elem = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='Fill In AmountPlayer ID/Phone Number/Third Party Login']")))
            usersearch_elem.send_keys(userid)
            # Wait for the OK button to be clickable and then click on it
            # ok_btn = wait.until(EC.element_to_be_clickable(
            #     (By.XPATH, "//button[contains(@class, 'el-button--primary') and .//span[text()='OK']]")))
            # ok_btn.click()
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


def acebook(userid, amount, username, password):
    # Start a new instance of the Chrome browser
    # options = ChromeOptions()
    # #options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # path_to_driver = ChromeDriverManager().install()
    # driver = webdriver.Chrome(options=options)
    ##
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = '/usr/bin/google-chrome-stable'
    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 2)

    status = False
    msg = ""
    try:
        # Navigate to the login page
        driver.get("https://djwae.playacebook.mobi/#/login")
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
        driver.get("https://djwae.playacebook.mobi/#/manage-user/search")

        # Wait for the radio button to be clickable and then click on it
        try:

            player_account_radio_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//span[text()='Player account']/preceding-sibling::span[contains(@class, 'el-radio__input')]")))
            player_account_radio_btn.click()

            usersearch_elem = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='Fill In AmountPlayer ID/Phone Number/Third Party Login']")))
            usersearch_elem.send_keys(userid)
            # Wait for the OK button to be clickable and then click on it
            # ok_btn = wait.until(EC.element_to_be_clickable(
            #     (By.XPATH, "//button[contains(@class, 'el-button--primary') and .//span[text()='OK']]")))
            # ok_btn.click()
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


def orionstar(userid, amount, username, password):
    # Start a new instance of the Chrome browser
    # options = ChromeOptions()
    # #options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # path_to_driver = ChromeDriverManager().install()
    # driver = webdriver.Chrome( options=options)
    ##
    tries = 2
    while (tries >= 1):
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = '/usr/bin/google-chrome-stable'
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 2)

        status = False
        msg = ""
        try:
            # Navigate to the login page
            driver.get("https://orionstars.vip:8781/")

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
                    driver.get("https://orionstars.vip:8781/")
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
                msg = "User Not Found"
            driver.switch_to.default_content()

            # Switch to the new iframe using its `src` attribute
            iframe_xpath = "//iframe[contains(@src, 'https://orionstars.vip:8781/Module/AccountManager/GrantTreasure.aspx?param=')]"
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
            tries -= 1
            if status:
                return status, msg
            if msg == "Internal Server Error" and tries < 1:
                return status, msg


def gamevault999(userid, amount, username, password):
    tries = 3
    while (tries >= 1):

        ##
        # options = ChromeOptions()
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # path_to_driver = ChromeDriverManager().install()
        # driver = webdriver.Chrome(options=options)
        ##

        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = '/usr/bin/google-chrome-stable'
        driver = uc.Chrome(options=options)

        wait = WebDriverWait(driver, 3)

        status = False
        msg = ""
        try:

            driver.get("https://agent.gamevault999.com/login")
            while True:  # Start a loop to handle incorrect captchas
                # Find the username, password, and captcha input fields
                username_elem = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='username']")))
                password_elem = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='password']")))
                code_elem = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/div/div[3]/form/div[3]/div/div[1]/input")))
                # username_elem.send_keys("")
                # password_elem.send_keys("")
                # print("Sending captcha")
                # code_elem.send_keys("")

                # Extract text from the captcha image
                time.sleep(1)
                captcha_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "imgCode")))
                time.sleep(1)
                captcha_element.screenshot('captcha.png')
                # image = Image.open('captcha.png')
                #
                # # Apply the blur filter to the image.
                # blurred_image = image.filter(ImageFilter.GaussianBlur(radius=1.1))
                #
                # # Save the blurred image.
                # blurred_image.save('blurred_captcha.png')
                captcha_text = extract_using_GBC("captcha.png")
                # Fill in the login form and submit
                username_elem.send_keys(username)
                password_elem.send_keys(password)
                print("Sending captcha")
                code_elem.send_keys(str(captcha_text))
                print("Sent captcha")
                submit_btn = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[3]/form/div[4]/button")))
                submit_btn.click()
                # Check if the incorrect captcha message is displayed
                try:
                    time.sleep(1)
                    caution = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[5]/div/div[3]/button/span")))
                    caution.click()
                    break
                except Exception as e:

                    # If the error message is not found, it means login was successful, so break out of the loop
                    driver.get("https://agent.gamevault999.com/login")

            print("here")

            try:
                search_user = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//input[@placeholder='Please enter your search content']")))
                search_user.send_keys(userid)
                search_button = wait.until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "/html/body/div[1]/div/div[4]/div[2]/div[2]/section/div[2]/form/div[2]/div/button[1]")))
                search_button.click()
                edit_user = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                       "/html/body/div[1]/div/div[4]/div[2]/div[2]/section/div[4]/div[3]/table/tbody/tr/td[1]/div/button")))
                edit_user.click()


            except Exception as e:
                msg = "User Not Found"
            recharge_button = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                         "/html/body/div[1]/div/div[4]/div[2]/div[2]/section/div[1]/div[1]/div[2]/div/button[2]")))
            recharge_button.click()
            set_price = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                   "/html/body/div[1]/div/div[4]/div[2]/div[2]/section/div[1]/div[4]/div/div[2]/form/div[5]/div/div/input")))
            set_price.send_keys(amount)
            submit = wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[2]/section/div[1]/div[4]/div/div[3]/button[2]")))
            submit.click()

            status = True
        except Exception as e:
            logging.exception(e)
            if msg == "":
                msg = "Internal Server Error"

        finally:
            close_and_quit_driver(driver)
            tries -= 1
            if status:
                return status, msg
            if msg == "Internal Server Error" and tries < 1:
                return status, msg
