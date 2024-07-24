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
    wait = WebDriverWait(driver, 5)

    status = False
    found = False
    msg = ""
    try:
        # Navigate to the login page
        driver.get("https://agent.candyland.mobi/")

        username_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
        password_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))

        username_elem.send_keys(username)
        password_elem.send_keys(password)

        submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Log in']")))
        submit_btn.click()

        try:
            time.sleep(1)

            search = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Account # or Username']")))
            search.send_keys(userid)

            search_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Search']")))

            search_btn.click()
            time.sleep(1)

            count = 2
            while not found:
                record = wait.until(
                    EC.presence_of_element_located((By.XPATH, f"/html/body/div[1]/div[2]/div/div/div/section[2]/div/div[7]/table/tbody/tr[{count}]/td[4]")))
                if record.text.lower() == userid.lower():
                    recharge_btn = wait.until(EC.presence_of_element_located(
                        (By.XPATH, f"/html/body/div[1]/div[2]/div/div/div/section[2]/div/div[7]/table/tbody/tr[{count}]/td[8]/div/button[1]")))
                    recharge_btn.click()
                    found = True
                    break
                count += 1
            driver.switch_to.default_content()
        except:
            msg = "User Not Found"
        # Switch to the new iframe using its `src` attribute
        if found:
            time.sleep(1)
            input_amount = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='modal-deposite-amount']")))
            input_amount.send_keys(str(amount))
            time.sleep(1)
            recharge_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value='Deposit']")))
            recharge_btn.click()
            time.sleep(1)
            status = True
    except Exception as e:
        logging.exception(e)
        msg = "Internal Server Error"
    finally:
        close_and_quit_driver(driver)
        return status, msg
