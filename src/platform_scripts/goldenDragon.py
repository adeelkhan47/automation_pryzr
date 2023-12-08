import logging
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common import extract_using_GBC, close_and_quit_driver, get_ubuntu_chrome_driver, get_mac_chrome_driver, \
    extract_text_from_image


def run_script(userid, amount, username, password,url_key):

    tries = 3
    while tries >= 1:
        driver = get_mac_chrome_driver()
        #driver = get_ubuntu_chrome_driver()
        wait = WebDriverWait(driver, 5)
        status = False
        msg = ""
        try:
            # Navigate to the login page
            driver.get(f"https://pos.goldendragoncity.com/pos/{url_key}")


            # Find the username, password, and captcha input fields
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[starts-with(@id, 'fancybox-frame')]")))
            username_elem = wait.until(
                EC.presence_of_element_located((By.ID, "username")))
            password_elem = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your password']")))

            username_elem.send_keys(username)
            password_elem.send_keys("")
            xyz = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your password']")))
            xyz.send_keys(password)
            time.sleep(1)
            xyz.send_keys(password)

            submit_btn = wait.until(
                EC.presence_of_element_located((By.ID, "login_email")))
            submit_btn.click()

            try:
                time.sleep(1)
                driver.get("https://pos.goldendragoncity.com/CustomerAccount/")

                select = wait.until(EC.presence_of_element_located((By.ID, 'search_type'))).click()

                search = wait.until(EC.presence_of_element_located((By.ID, "searchPin")))
                search.send_keys(userid)
                ok_button = wait.until(EC.presence_of_element_located((By.ID, "ok_button")))
                ok_button.click()
                purchase = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[4]/div/div[1]/div/div[2]/div/div[2]/button[2]")))
                purchase.click()
                try:
                    temp_button = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div[7]/div/button")))
                    temp_button.click()
                except:
                    print("-")
                add_amount = wait.until(EC.presence_of_element_located((By.ID, "txt_scoreNum")))
                add_amount.send_keys(amount)
                add_amountsubmit = wait.until(EC.presence_of_element_located((By.ID, "Button_OK")))
                add_amountsubmit.click()
                status = True
            except:
                msg = "User Not Found"

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
