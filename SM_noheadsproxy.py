from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
import threading
import keyboard
import os
from concurrent.futures import ThreadPoolExecutor

# Number of sessions to open
NUM_SESSIONS = 3

# Path to ChromeDriver
CHROMEDRIVER_PATH = r"chromedriver.exe"

# ------------------------------------------

# List to store browser instances
browsers = []
executor = ThreadPoolExecutor(max_workers=NUM_SESSIONS)
lock = threading.Lock()  # Prevents race conditions when modifying the browsers list

def start_browser(session_id):
    profile_path = f"C:\\Selenium\\xProxyTokenChromeProfile_{session_id}"

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_path}")

    # --- Proxy selection logic ---
    if USE_WEB_UNLOCKER:
        proxy_url = f"http://{WEB_UNLOCKER_USER}:{WEB_UNLOCKER_PASS}@{WEB_UNLOCKER_PROXY}"
        options.add_argument(f"--proxy-server={proxy_url}")
        print(f"[INFO] Using Oxylabs Web Unlocker proxy for Session {session_id}.")
    else:
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY}"
        options.add_argument(f"--proxy-server={proxy_url}")
        print(f"[INFO] Using Oxylabs Residential proxy for Session {session_id}.")
    # ----------------------------

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

    # Add custom header for Oxylabs Web Unlocker
    driver.header_overrides = {
        "x-oxylabs-render": "html"
    }

    # Open the target site
    driver.get("https://smtickets.com/events/view/14889")
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
    If using a web unlocker, also checks the current URL as a fallback.
    """
    print(f"[INFO] Monitoring network requests in Session {session_id}...")

    while driver.service.is_connectable():
        try:
            # Check Selenium Wire requests (works with standard proxies)
            for request in driver.requests:
                url = request.url.lower()
                if "queueittoken=" in url:
                    print(f"[SESSION {session_id}] Matching Request Found: {request.url}")
                    driver.quit()
                    print(f"[INFO] Browser Session {session_id} closed.")
                    with lock:
                        if driver in browsers:
                            browsers.remove(driver)
                    return

            # Fallback: Check current URL (works with web unlocker)
            current_url = driver.current_url.lower()
            if "queueittoken=" in current_url:
                print(f"[SESSION {session_id}] Matching URL Found in browser: {driver.current_url}")
                driver.quit()
                print(f"[INFO] Browser Session {session_id} closed.")
                with lock:
                    if driver in browsers:
                        browsers.remove(driver)
                return

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
