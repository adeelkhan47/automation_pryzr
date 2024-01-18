import logging
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common import extract_using_GBC, close_and_quit_driver, get_ubuntu_chrome_driver, get_mac_chrome_driver


def run_script(userid, amount, username, password):
    #driver = get_mac_chrome_driver()
    driver = get_ubuntu_chrome_driver()
    wait = WebDriverWait(driver, 2)

    status = False
    msg = ""
    try:
        # Navigate to the login page
        driver.get("https://ht.ultrapanda.mobi/#/login?redirect=%2Fmanage-user%2Faccount")
        wait = WebDriverWait(driver, 15)
        username_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='User Name']")))
        password_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))
        username_elem.send_keys(username)
        password_elem.send_keys(password)
        submit_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "el-button--primary")))
        submit_btn.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "openSidebar")))
        driver.get("https://ht.ultrapanda.mobi/#/manage-user/search")
        try:
            player_account_radio_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//span[text()='Player account']/preceding-sibling::span[contains(@class, 'el-radio__input')]")))
            player_account_radio_btn.click()
            usersearch_elem = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='Fill In AmountPlayer ID/Phone Number/Third Party Login']")))
            usersearch_elem.send_keys(userid)
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
        amount_elem.send_keys(amount)
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
