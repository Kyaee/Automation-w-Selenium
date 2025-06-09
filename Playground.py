from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time 

service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.get("https://www.google.com")
time.sleep(5)  # Wait for 5 seconds to see the page
driver.quit()  # Close the browser

# This code initializes a Chrome browser, navigates to Google, waits for 5 seconds, and then closes the browser.
