import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common import extract_using_GBC, close_and_quit_driver, get_mac_chrome_driver, get_ubuntu_chrome_driver


def run_script(userid, amount, username, password):
    tries = 5
    while tries >= 1:
        #driver = get_mac_chrome_driver()
        driver = get_ubuntu_chrome_driver()
        wait = WebDriverWait(driver, 2)
        status = False
        msg = ""
        try:

            driver.get("https://ht.juwa777.com/login")
            while True:  # Start a loop to handle incorrect captchas
                # Find the username, password, and captcha input fields
                username_elem = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Please enter your account']")))
                password_elem = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Please enter your password']")))
                vc_elem = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//input[@placeholder='Please enter the verification code']")))
                # Extract text from the captcha image
                time.sleep(1)
                captcha_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "imgCode")))
                time.sleep(1)
                captcha_element.screenshot('captcha_jw.png')
                # image = Image.open('captcha.png')
                #
                # # Apply the blur filter to the image.
                # blurred_image = image.filter(ImageFilter.GaussianBlur(radius=1.1))
                #
                # # Save the blurred image.
                # blurred_image.save('blurred_captcha.png')
                captcha_text = extract_using_GBC("captcha_jw.png")
                # Fill in the login form and submit
                username_elem.send_keys(username)
                password_elem.send_keys(password)
                print("Sending captcha")
                vc_elem.send_keys(str(captcha_text))
                print("Sent captcha")
                submit_btn = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[2]/form/div[4]/div/button")))
                time.sleep(1)
                submit_btn.click()
                # Check if the incorrect captcha message is displayed
                #
                try:
                    time.sleep(3)
                    driver.get("https://ht.juwa777.com/userManagement")
                    search_btn = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div/div/div[2]/section/div/div[3]/section/div[2]/form/div[2]/div/button[1]")))
                    search_btn.click()
                    break
                except Exception as e:
                    driver.get("https://ht.juwa777.com/login")
            try:
                search_user = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//input[@placeholder='Please enter your search content']")))
                search_user.send_keys(userid)
                editor = wait.until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "/html/body/div/div/div[2]/section/div/div[3]/section/div[4]/div[3]/table/tbody/tr/td[1]/div/div/span")))
                editor.click()
                recharge_button = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                       "/html/body/ul/li[2]")))
                recharge_button.click()


            except Exception as e:
                msg = "User Not Found"
            recharge_price = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                         "/html/body/div[1]/div/div[2]/section/div/div[3]/section/div[9]/div/div[2]/form/div[5]/div/div/input")))
            recharge_price.send_keys(amount)

            submit = wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/div[2]/section/div/div[3]/section/div[9]/div/div[3]/div/button[2]")))
            submit.click()
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
