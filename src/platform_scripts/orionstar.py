import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common import close_and_quit_driver, get_ubuntu_chrome_driver, extract_text_from_image


def run_script(userid, amount, username, password):
    tries = 3
    while tries >= 1:
        # driver = get_mac_chrome_driver()
        driver = get_ubuntu_chrome_driver()
        wait = WebDriverWait(driver, 2)
        found = False
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
                code_elem.send_keys(captcha_text)
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
            usersearch_elem = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='ID,Account or NickName']")))
            usersearch_elem.send_keys(userid)

            search_btn = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                    "//a[contains(@class, 'btn13') and contains(@class, 'btn-danger1') and contains(text(), 'Search')]")))
            search_btn.click()
            ##

            count = 2
            while not found:
                try:
                    update_btn_xpath = f"/html/body/form/div[3]/div[2]/table[1]/tbody/tr[{count}]/td[1]/a"
                    update_btn = wait.until(EC.presence_of_element_located((By.XPATH, update_btn_xpath)))
                    update_btn.click()

                    result = wait.until(EC.presence_of_element_located((By.ID,
                                                                        "txtAccount")))
                    acocunt = result.text
                    count += 1
                    if acocunt.lower() == userid.lower():
                        found = True
                except Exception as eee:
                    msg = "User Not Found"
                    break

            ##
            if found:
                recharge_btn = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                          "//a[contains(@class, 'btn12') and contains(@class, 'btn-danger') and contains(text(), 'Recharge')]")))
                recharge_btn.click()
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
            if not found:
                return status, msg
            if status:
                return status, msg
            if msg == "Internal Server Error" and tries < 1:
                return status, msg
