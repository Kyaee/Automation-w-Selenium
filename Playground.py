from selenium import webdriver
from selenium.webdriver.chrome.options import Options # allows customization of web driver

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.browser_version = "latest"  # specify the browser version if needed

driver = webdriver.Chrome(options=chrome_options)
driver.get("http://selenium.dev")
driver.quit()

