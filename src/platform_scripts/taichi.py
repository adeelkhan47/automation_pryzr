import logging
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common import close_and_quit_driver, get_ubuntu_chrome_driver, get_mac_chrome_driver


def run_script(userid, amount, username, password):
    #driver = get_mac_chrome_driver()
    driver = get_ubuntu_chrome_driver()
    wait = WebDriverWait(driver, 2)

    status = False
    found = False
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
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frm_main_content")))
            usersearch_elem = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='ID,Account or Name']")))
            usersearch_elem.send_keys(userid)

            search_btn = wait.until(EC.presence_of_element_located((By.ID, "Button4")))
            search_btn.click()
            count = 2
            while not found:
                record = wait.until(
                    EC.presence_of_element_located((By.XPATH, f"/html/body/form/table[4]/tbody/tr[{count}]/td[2]")))
                if record.text.lower() == userid.lower():
                    recharge_btn = wait.until(EC.presence_of_element_located(
                        (By.XPATH, f"/html/body/form/table[4]/tbody/tr[{count}]/td[5]/a")))
                    recharge_btn.click()
                    found = True
                    break
                count += 1
            driver.switch_to.default_content()
        except:
            msg = "User Not Found"
        # Switch to the new iframe using its `src` attribute
        if found:
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
