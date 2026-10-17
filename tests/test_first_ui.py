import pytest
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
def test_login_success(driver):
    page = LoginPage(driver)
    page.open()
    page.login("standard_user", "secret_sauce")
    assert driver.find_element(By.CLASS_NAME, "title").text == "Products"


@pytest.mark.parametrize("username, password, expected", [
    ("locked_out_user", "secret_sauce", "Sorry, this user has been locked out."),
    ("standard_user", "wrong_pass", "Username and password do not match"),
    ("", "", "Username is required"),
])
def test_login_failure(driver, username, password, expected):
    page = LoginPage(driver)
    page.open()
    page.login(username, password)
    assert expected in page.error_message()