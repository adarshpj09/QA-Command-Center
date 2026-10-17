import os
import pytest
from selenium import webdriver

from app_under_test.chat_server import start_server


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)


@pytest.fixture
def driver(request):
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        os.makedirs("reports/screenshots", exist_ok=True)
        driver.save_screenshot(f"reports/screenshots/{request.node.name}.png")
    driver.quit()


@pytest.fixture(scope="session")
def ws_url():
    server = start_server(port=0)
    port = server.socket.getsockname()[1]
    yield f"ws://127.0.0.1:{port}"
    server.shutdown()