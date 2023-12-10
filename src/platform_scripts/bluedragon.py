import logging
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common import extract_using_GBC, close_and_quit_driver, get_ubuntu_chrome_driver, get_mac_chrome_driver, \
    extract_text_from_image


def run_script(userid, amount, username, password):

    tries = 3
    while tries >= 1:
        #driver = get_mac_chrome_driver()
        driver = get_ubuntu_chrome_driver()
        wait = WebDriverWait(driver, 5)
        status = False
        msg = ""
        try:
            # Navigate to the login page
            driver.get("https://agent.bluedragon777.com/Login.aspx")


            # Find the username, password, and captcha input fields
            username_elem = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='User Name']")))
            password_elem = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))

            username_elem.send_keys(username)
            password_elem.send_keys(password)

            submit_btn = wait.until(EC.presence_of_element_located((By.ID, "loginButton")))
            submit_btn.click()

            try:
                time.sleep(1)
                driver.get("https://agent.bluedragon777.com/Work/com_Search.aspx")
                print("Switching to iframe")
                element = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value='1']")))
                element.click()
                input_user = wait.until(EC.presence_of_element_located((By.ID, 'txt_UserName')))
                input_user.send_keys(userid)
                ok_button = wait.until(EC.presence_of_element_located((By.ID, "Button_OK")))
                ok_button.click()
                set_score = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[1]/section[2]/div[1]/div[2]/div/table/tbody/tr/td[8]/button[1]")))
                set_score.click()
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
