import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common import close_and_quit_driver, get_mac_chrome_driver, get_ubuntu_chrome_driver, \
    extract_text_from_image,extract_using_GBC


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
            driver.get("https://dl.bigwplay.com/admin/login/index.html?lang=en-us")
            while True:
                username_elem = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
                password_elem = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))
                captcha_elem = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Captcha']")))
                # captcha_element = wait.until(EC.presence_of_element_located((By.ID, "captcha")))
                # captcha_element.screenshot('captcha.png')
                # captcha_text = extract_using_GBC('captcha.png')
                username_elem.send_keys(username)
                password_elem.send_keys(password)
                captcha_elem.send_keys("123445")
                submit_btn = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='doLoginbtn']")))
                submit_btn.click()
                try :
                    ok_button = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//a[text()='ok']")))
                    ok_button.click()
                    drawer = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//span[text()='Player management']")))

                    drawer.click()
                    break
                except Exception as e:
                    try:
                        drawer = wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//span[text()='Player management']")))
                        drawer.click()
                    except Exception as ee:
                        driver.get("https://dl.bigwplay.com/admin/login/index.html?lang=en-us")

            drawer = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//span[text()='My player']")))
            drawer.click()
            time.sleep(1)
            print("Switching to iframe")
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@src='/admin/agent_manage/agentUserList.html']")))
            username_elem = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Username']")))
            username_elem.send_keys(userid)
            time.sleep(1)
            search_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div[1]/div[6]/button")))
            search_btn.click()
            count = 0
            while not found:
                try:
                    count += 1
                    time.sleep(1)
                    account_xpath = f"/html/body/div[2]/div/div/div[2]/div[2]/div[2]/table/tbody/tr[{count}]/td[3]/div"
                    account_xpath = wait.until(EC.presence_of_element_located((By.XPATH, account_xpath)))
                    logging.info(f"{userid} : search_account = {account_xpath.text}")
                    print(f"{userid} : search_account = {account_xpath.text}")
                    if account_xpath.text.lower() == userid.lower():
                        account = account_xpath.text
                        sell_score_xpath = f"/html/body/div[2]/div/div/div[2]/div[2]/div[2]/table/tbody/tr[{count}]/td[1]/div/a[1]"
                        sell_score = wait.until(EC.presence_of_element_located((By.XPATH, sell_score_xpath)))
                        sell_score.click()
                        # time.sleep(100)
                        found = True
                except Exception as ee:
                    msg = "User Not Found"
                    break
            if found:
                time.sleep(1)
                number_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//input[@name='ChangeScore']")))
                number_field.send_keys(str(amount))
                submit_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,f"//button[text()='Submit']"))
                )
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
