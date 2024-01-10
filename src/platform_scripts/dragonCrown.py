import logging
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common import close_and_quit_driver, get_ubuntu_chrome_driver, get_mac_chrome_driver, \
    extract_text_from_image


def run_script(userid, amount, username, password):
    #
    tries = 5
    while tries >= 1:
        #driver = get_mac_chrome_driver()
        driver = get_ubuntu_chrome_driver()
        wait = WebDriverWait(driver, 5)
        status = False
        found = False
        msg = ""
        try:
            # Navigate to the login page
            driver.get("https://gm.dragoncrown.win/admin/auth/login")

            username_elem = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
            password_elem = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))
            username_elem.send_keys(username)
            password_elem.send_keys(password)
            submit_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/form/div[3]/div[2]/button")))
            submit_btn.click()
            search = wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div/div[1]/section[2]/div/div/div/div[1]/div[2]/div/label/span")))
            search.click()
            searchField = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Account']")))
            searchField.send_keys(userid)
            searchButton = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "submit")))
            searchButton.click()
            count = 1
            while not found:
                try:
                    account_xpath = f"/html/body/div/div/div[1]/section[2]/div/div/div/div[4]/table/tbody/tr[{count}]/td[2]"
                    account_xpath = wait.until(EC.presence_of_element_located((By.XPATH, account_xpath)))
                    account = account_xpath.text
                    if account.lower() == userid.lower():
                        found = True
                        sell_score_xpath = f"/html/body/div/div/div[1]/section[2]/div/div/div/div[4]/table/tbody/tr[{count}]/td[4]/a/i"
                        sell_score = wait.until(EC.presence_of_element_located((By.XPATH, sell_score_xpath)))
                        sell_score.click()
                    count += 1
                except Exception as ee:
                    msg = "User Not Found"
                    break
            if found:
                number_field = wait.until(EC.presence_of_element_located((By.ID,"number")))
                number_field.send_keys(amount)
                submit = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[4]/div/div/form/div[2]/button[2]")))
                submit.click()
                status = True
        except Exception as e:
            logging.exception(e)
            if msg == "":
                msg = "Internal Server Error"

        finally:
            close_and_quit_driver(driver)
            tries -= 1
            if not found:
                return status, msg
            if status:
                return status, msg
            if msg == "Internal Server Error" and tries < 1:
                return status, msg
