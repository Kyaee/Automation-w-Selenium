from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def custom_options(): 
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    return options

def main():
    service = Service(executable_path='chromedriver.exe')
    options = custom_options()
    
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get("https://www.google.com")
        print("Page title is:", driver.title)
        
        # Example interaction: search for 'Selenium'
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("Selenium" + Keys.RETURN)
        
        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        print("Search completed successfully.")
        
    except Exception as e:
        print("An error occurred:", e)
    
    finally:
        time.sleep(5)  # Wait for a while before closing
        driver.quit()  # Close the browser