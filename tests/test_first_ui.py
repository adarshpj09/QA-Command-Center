from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_login_success():
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.saucedemo.com")
        driver.find_element(By.ID, "user-name").send_keys("standard_user")
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        driver.find_element(By.ID, "login-button").click()

        title = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "title"))
        )
        assert title.text == "Products"
    finally:
        driver.quit()