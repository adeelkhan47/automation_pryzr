import logging
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common import extract_using_GBC, close_and_quit_driver, get_ubuntu_chrome_driver, get_mac_chrome_driver



def run_script(userid, amount, username, password):
    driver = get_mac_chrome_driver()
    #driver = get_ubuntu_chrome_driver()
    wait = WebDriverWait(driver, 5)

    status = False
    found = False
    msg = ""
    try:
        # Navigate to the login page
        driver.get("https://river-pay.com/office/login")

        username_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Login']")))
        password_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))

        username_elem.send_keys(username)
        password_elem.send_keys(password)

        submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value='Log in']")))
        submit_btn.click()


        try:
            time.sleep(1)
            # ignore_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Close']")))
            # ignore_btn.click()
            search = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main-content']/div[2]/form/div/span/span[1]/span/ul/li/input")))
            search.send_keys(userid)
            time.sleep(1)

            count = 1
            while not found:
                logging.error(count)
                time.sleep(1)

                record = wait.until(
                    EC.presence_of_element_located((By.XPATH, f"//*[@id='select2-usersIds-results']/li[{count}]")))
                logging.error(record.text.lower())
                if record.text.lower() == userid.lower():
                    record.click()
                    search_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Search']")))
                    search_btn.click()
                    recharge_btn = wait.until(EC.presence_of_element_located(
                        (By.XPATH, f"//*[@id='table-accounts']/tbody/tr[2]/td[7]/button")))
                    recharge_btn.click()
                    found = True
                    break
                count += 1
            driver.switch_to.default_content()
        except Exception as eee:
            logging.exception(eee)
            msg = "User Not Found"
        # Switch to the new iframe using its `src` attribute
        if found:
            time.sleep(1)
            input_amount = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='modal-deposite-amount']")))
            input_amount.send_keys(str(amount))
            # time.sleep(1)
            recharge_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value='Apply']")))
            recharge_btn.click()
            time.sleep(1)
            status = True
    except Exception as e:
        logging.exception(e)
        msg = "Internal Server Error"
    finally:
        close_and_quit_driver(driver)
        return status, msg
