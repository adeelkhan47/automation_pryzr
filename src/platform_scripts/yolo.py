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
        found = False
        msg = ""
        try:
            # Navigate to the login page
            driver.get("https://agent.yolo777.game/admin/auth/login")
            wait = WebDriverWait(driver, 15)
            # Find the username and password fields (replace with actual element identifiers)
            # btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Buy')]")))
            username_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
            password_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))
            username_elem.send_keys(username)
            password_elem.send_keys(password)

            # Find the submit button and click it (replace with actual element identifier)
            # submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Login')]")))
            submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='login-form']/button")))
            submit_btn.click()


            # Wait for the radio button to be clickable and then click on it
            time.sleep(2)
            driver.get("https://agent.yolo777.game/admin/player_list")
            search = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Account']")))
            search.send_keys(userid)

            submit = wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 "/html/body/div/div/div[2]/section/div/div/div/div[2]/div/form/div/button/span")))
            submit.click()
            count = 0
            while not found:
                try:
                    count += 1
                    time.sleep(1)
                    account_xpath = f"/html/body/div/div/div[2]/section/div/div/div/div[3]/div/div/table/tbody/tr[{count}]/td[3]"
                    account_xpath = wait.until(EC.presence_of_element_located((By.XPATH, account_xpath)))
                    logging.info(f"{userid} : search_account = {account_xpath.text}")
                    print(f"{userid} : search_account = {account_xpath.text}")
                    search_account = account_xpath.text.lower().strip()
                    if search_account == userid.lower():
                        sell_score_xpath = f"//*[@id='grid-table']/tbody/tr[{count}]/td[1]/div/a"
                        sell_score = wait.until(EC.presence_of_element_located((By.XPATH, sell_score_xpath)))
                        sell_score.click()
                        time.sleep(1)

                        # time.sleep(100)
                        sell_score_xpath = f"//*[@id='grid-table']/tbody/tr[{count}]/td[1]/div/ul/li[1]/a/span/div"
                        sell_score = wait.until(EC.presence_of_element_located((By.XPATH, sell_score_xpath)))
                        sell_score.click()

                        found = True
                except Exception as ee:
                    logging.exception(ee)
                    msg = "User Not Found"
                    break

            if found:
                amount_elem = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Input score']")))
                time.sleep(1)
                amount_elem.send_keys(amount)

                # Wait for the OK button to be clickable and then click on it
                submit_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[@id[starts-with(., 'form-')]]/div[2]/div[2]/button[2]")))
                submit_button.click()
                time.sleep(1)

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
