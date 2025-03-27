Unifi Stock Checker

A Python-based automation script that monitors the stock status of the Cloud Gateway Fiber product. The script uses Selenium to navigate to the product page, checks for “Sold Out” indicators, and sends notifications via Pushover if the product is available. Additionally, it logs the status to a file and takes a screenshot when the product might be in stock.

Note: This script is designed to run inside a Docker container and interacts via Bluetooth with an ESP32 board that controls LED indicators (based on the .log file), providing a physical alert system in addition to digital notifications.

Features
	•	Automated Stock Checking: Uses Selenium WebDriver to load the product page and search for “Sold Out” indicators.
	•	Notification System: Integrates with Pushover to send alerts when the product is available or if any errors occur.
	•	Status Logging: Writes the availability status to a log file specified by an environment variable (that will be used to update the ESP32 leds).
	•	Error Handling: Comprehensive error and exception handling with detailed logging.
	•	Headless Operation: Configured to run headless for use on servers or cron jobs.
	•	Docker-Ready: Preconfigured for deployment within a Docker container.
	•	Bluetooth Interaction: Communicates via Bluetooth with an ESP32 board to control LED indicators for real-time physical alerts.

Prerequisites

Before running the script, ensure you have:
	•	Python 3.6 or later
	•	Google Chrome installed
	•	Chrome WebDriver that is compatible with your Chrome version
	•	A Pushover account for notifications
	•	Docker installed (if deploying in a container, optional)
	•	An ESP32 board with Bluetooth capability and connected LEDs for physical notifications (optional)

Installation
	1.	Clone the Repository:

git clone https://github.com/yourusername/unifi-stock-checker.git
cd unifi-stock-checker


	2.	Set Up a Virtual Environment (optional but recommended):

python3 -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`


	3.	Install Dependencies:
Install the required Python packages with pip:

pip install -r requirements.txt

If you don’t have a requirements.txt, you can create one with the following contents:

selenium
requests
PyYAML
python-dotenv



Configuration

Environment Variables

Create a .env file in the project root and set the following variable:

STATUS_LOG_PATH=/path/to/your/status_log.txt

This variable defines the location where the script will write the stock status logs.

YAML Configuration

Create a config.yaml file in the project root with the following structure:

# config.yaml
URL_GATEWAY: "https://example.com/path-to-cloud-gateway-fiber"  # Replace with the actual URL
DRIVER_PATH: "/path/to/chromedriver"  # Absolute path to your Chrome WebDriver executable
PUSHOVER_API_TOKEN: "your_pushover_app_token"
PUSHOVER_USER_KEY: "your_pushover_user_key"

	•	URL_GATEWAY: URL of the product page.
	•	DRIVER_PATH: Path to the ChromeDriver executable.
	•	PUSHOVER_API_TOKEN: Your Pushover API token.
	•	PUSHOVER_USER_KEY: Your Pushover user key.

Usage

Once configured, you can run the script directly from the command line:

python3 stock_check.py

The script will:
	1.	Introduce a random delay to avoid detection.
	2.	Launch a headless Chrome browser session.
	3.	Navigate to the product page specified by URL_GATEWAY.
	4.	Check for “Sold Out” indicators.
	5.	Log the product status to the file defined in STATUS_LOG_PATH (this will be used to update the ESP32 leds).
	6.	Send a notification via Pushover based on the product’s availability.



Logging and Screenshots
	•	Logging: All actions, including errors and status messages, are logged to both the console and a stock_check.log file in the project directory.
	•	Screenshots: If the product might be in stock (i.e., “Sold Out” is not detected), the script saves a screenshot in the project directory for further verification.

Troubleshooting
	•	ChromeDriver Issues: Ensure the version of ChromeDriver matches your installed version of Google Chrome.
	•	Notification Errors: Double-check your Pushover API and User tokens in the config.yaml.
	•	Environment Variables: Verify that the .env file is properly configured and located in the project root.
	•	Docker Issues: Confirm that your Docker environment is correctly set up and that the Dockerfile paths match your project structure.
	•	Bluetooth/ESP32 Communication: Ensure your ESP32 board is correctly configured for Bluetooth communication and that the necessary drivers and libraries are installed.
