from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
import threading
import keyboard
import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Number of sessions to open
NUM_SESSIONS = 1

# Path to ChromeDriver
CHROMEDRIVER_PATH = r"C:\\Selenium\\chromedriver.exe"

# Path to your Chrome extension
EXTENSION_PATH = r""

# Proxy ph residential credentials
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")

# List to store browser instances
browsers = []
executor = ThreadPoolExecutor(max_workers=NUM_SESSIONS)
lock = threading.Lock()  # Prevents race conditions when modifying the browsers list

def start_browser(session_id):
    profile_path = f"C:\\Selenium\\xProxyTokenChromeProfile_{session_id}"

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument(f"--load-extension={EXTENSION_PATH}")

    # Use your own proxy instead of Selenium Wire's proxy
    options.add_argument(f"--proxy-server=http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}")

    # Enable headless mode
    options.add_argument("--headless=new")  # New headless mode for better performance
    options.add_argument("--disable-gpu")  # Needed for some environments
    options.add_argument("--no-sandbox")  # Helps prevent permission issues
    options.add_argument("--disable-dev-shm-usage")  # Helps with memory issues

    # UI Optimizations (Headless Mode)
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--process-per-site")
    options.add_argument("--disk-cache-size=5000000")
    options.add_argument("--enable-low-res-tiling")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Start browser with Selenium Wire (but using your own proxy)
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # Open the target site
    driver.get("https://smtickets.com/events/view/14363")
    print(f"[INFO] Browser Session {session_id} started with profile {profile_path} (Headless) using your proxy.")

    # Add browser instance to the global list safely
    with lock:
        browsers.append(driver)

    # Start monitoring network requests
    threading.Thread(target=monitor_requests, args=(driver, session_id), daemon=True).start()

    return driver

def monitor_requests(driver, session_id):
    """
    Waits for 'queueittoken=' in the network requests, then prints the request URL and closes the browser.
    """
    print(f"[INFO] Monitoring network requests in Session {session_id}...")

    while driver.service.is_connectable():
        try:
            for request in driver.requests:
                url = request.url.lower()  # Convert to lowercase for consistency
                
                if "queueittoken=" in url:
                    print(f"[SESSION {session_id}] Matching Request Found: {request.url}")
                    
                    # Close browser after detecting the request
                    driver.quit()
                    print(f"[INFO] Browser Session {session_id} closed.")

                    # Remove from active browsers list safely
                    with lock:
                        if driver in browsers:
                            browsers.remove(driver)
                    return  # Stop monitoring this session
        except Exception:
            pass  # Keep looping until request appears

def launch_browsers():
    for i in range(NUM_SESSIONS):
        executor.submit(start_browser, i + 1)

def close_all_browsers():
    with lock:
        if not browsers:  # If no active browsers, just exit
            print("\n[INFO] No active browsers. Exiting...")
            os._exit(0)

        print("\n[INFO] Closing all browsers...")
        for browser in browsers:
            try:
                browser.quit()
            except Exception as e:
                print(f"[ERROR] Failed to close a browser: {e}")

        browsers.clear()
    
    print("[INFO] All sessions closed.")
    os._exit(0)

# Start browser sessions in threads
threading.Thread(target=launch_browsers, daemon=True).start()

print("[INFO] Press 'Home' on your keyboard to close all browsers.")
keyboard.wait("home")  
close_all_browsers()
