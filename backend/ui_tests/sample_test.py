from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def _get_driver():
    try:
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        return webdriver.Chrome(options=options)
    except Exception:
        options = FirefoxOptions()
        options.add_argument("--headless")
        try:
            return webdriver.Firefox(options=options)
        except Exception:
            return None


def run_sample(base_url: str):
    driver = _get_driver()
    if driver is None:
        print("no supported browser found")
        return
    try:
        driver.set_page_load_timeout(30)
        driver.get(base_url)
        print(driver.title)
    finally:
        try:
            driver.quit()
        except Exception:
            pass
