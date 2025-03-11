#!/usr/bin/env python3
import os
import sys
import datetime
import time
import traceback
import logging
import random
import tempfile
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import yaml

# Define base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(BASE_DIR, 'stock_check.log'))
    ]
)

# Load configuration
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yaml')
with open(CONFIG_PATH, 'r') as file_config:
    config = yaml.safe_load(file_config)

# Product URLs - update these in your config.yaml
URL_SWITCH = config['URL_SWITCH']
URL_WIFI = config['URL_WIFI']
URL_GATEWAY = config['URL_GATEWAY']  # Added gateway URL from config
DRIVER_PATH = config['DRIVER_PATH']  # Adjust if your path is different

# Configure Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def send_notification(message, priority=-1, title="Unifi Stock Check"):
    """Send notification via Pushover."""
    try:
        pushover_app_token = config['PUSHOVER_API_TOKEN']
        pushover_user_token = config['PUSHOVER_USER_KEY']
        
        if not pushover_app_token or not pushover_user_token:
            logging.error("Pushover tokens not configured in config.yaml")
            return
            
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": pushover_app_token,
                "user": pushover_user_token,
                "message": message,
                "title": title,
                "priority": priority
            }
        )
        if response.status_code == 200:
            logging.info(f"Notification sent: {message}")
        else:
            logging.error(f"Failed to send notification: {response.text}")
    except Exception as e:
        logging.error(f"Error sending notification: {str(e)}")

def check_product_availability(driver, url, product_name):
    """
    Check if a product is available by checking for 'Sold Out' text.
    """
    try:
        logging.info(f"Checking availability of {product_name} at {url}")
        
        # Navigate to the product page
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Allow time for dynamic content to load
        time.sleep(5)
        
        # Look for "Sold Out" text using different possible selectors
        sold_out_selectors = [
            '.sc-190ba8g-4',  # Text within span
            'button[label="Sold Out"]',  # Button with label attribute
            'div.sc-1x3sjmh-0',  # Div with sold out class
        ]
        
        sold_out_found = False
        for selector in sold_out_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if 'Sold Out' in element.text:
                        sold_out_found = True
                        logging.info(f"Found 'Sold Out' indicator for {product_name}")
                        break
                if sold_out_found:
                    break
            except NoSuchElementException:
                continue
        
        if sold_out_found:
            logging.info(f"{product_name} is SOLD OUT")
            return False, None
        else:
            # Take a screenshot for verification if "Sold Out" not found
            screenshot_path = os.path.join(BASE_DIR, f"{product_name.replace(' ', '_')}_screenshot.png")
            driver.save_screenshot(screenshot_path)
            logging.info(f"Could not find 'Sold Out' indicator. {product_name} might be IN STOCK! Screenshot saved to {screenshot_path}")
            return True, None
            
    except TimeoutException:
        error_msg = f"Timeout while loading the page for {product_name}"
        logging.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error checking {product_name} availability: {str(e)}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        return False, error_msg

def main():
    """
    Main function to check product availability and send notifications.
    """
    try:
        # Introduce a random delay
        wait_time = random.randint(1, 30)
        logging.info("Waiting for %d seconds before starting automation", wait_time)
        time.sleep(wait_time)

        # Create a unique temporary directory for Chrome's user data
        chrome_data_dir = tempfile.mkdtemp()
        chrome_options.add_argument("--user-data-dir=" + chrome_data_dir)

        # Set up the Chrome service
        if sys.platform.startswith('linux'):
            service = ChromeService(executable_path=DRIVER_PATH)
        else:
            service = ChromeService()
            logging.info("Non-linux platform detected. Using default ChromeService configuration.")

        # Initialize the WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Check availability of products
            switch_available, switch_error = check_product_availability(
                driver, URL_SWITCH, "Pro Max 16 PoE Switch"
            )
            
            wifi_available, wifi_error = check_product_availability(
                driver, URL_WIFI, "U7 Pro Max WiFi AP"
            )
            
            gateway_available, gateway_error = check_product_availability(
                driver, URL_GATEWAY, "Cloud Gateway Fiber"
            )
            
            # Create and send notifications
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Switch notification
            if switch_error:
                switch_message = f"Error checking Pro Max 16 PoE Switch: {switch_error}"
                send_notification(switch_message, priority=-1, title="Error - Unifi Stock Check")
            else:
                switch_status = "IN STOCK! 🎉" if switch_available else "still sold out 😢"
                switch_message = f"Pro Max 16 PoE Switch is {switch_status} as of {now}"
                priority = 1 if switch_available else -2
                send_notification(switch_message, priority=priority, title="Unifi Stock Check")
                
            # WiFi AP notification
            if wifi_error:
                wifi_message = f"Error checking U7 Pro Max WiFi AP: {wifi_error}"
                send_notification(wifi_message, priority=-1, title="Error - Unifi Stock Check")
            else:
                wifi_status = "IN STOCK! 🎉" if wifi_available else "still sold out 😢"
                wifi_message = f"U7 Pro Max WiFi AP is {wifi_status} as of {now}"
                priority = 1 if wifi_available else -2
                send_notification(wifi_message, priority=priority, title="Unifi Stock Check")
            
            # Gateway notification
            if gateway_error:
                gateway_message = f"Error checking Cloud Gateway Fiber: {gateway_error}"
                send_notification(gateway_message, priority=-1, title="Error - Unifi Stock Check")
            else:
                gateway_status = "IN STOCK! 🎉" if gateway_available else "still sold out 😢"
                gateway_message = f"Cloud Gateway Fiber is {gateway_status} as of {now}"
                priority = 1 if gateway_available else -2
                send_notification(gateway_message, priority=priority, title="Unifi Stock Check")
                
        finally:
            # Clean up
            driver.quit()
            
    except Exception as e:
        error_message = f"Fatal error in stock check script: {str(e)}"
        logging.error(error_message)
        logging.error(traceback.format_exc())
        send_notification(error_message, priority=-1, title="Fatal Error - Unifi Stock Check")

if __name__ == "__main__":
    main()