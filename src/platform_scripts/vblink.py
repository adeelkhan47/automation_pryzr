import logging
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common import extract_using_GBC, close_and_quit_driver, get_ubuntu_chrome_driver, get_mac_chrome_driver


def run_script(userid, amount, username, password):
    #driver = get_mac_chrome_driver()
    tries = 5
    while tries >= 1:
        driver = get_ubuntu_chrome_driver()
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
                time.sleep(3)
            except:
                msg = "User Not Found"

            amount_elem = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Set points : ie 100']")))
            time.sleep(1)
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
            tries -= 1
            if status:
                return status, msg
            if msg == "Internal Server Error" and tries < 1:
                return status, msg
