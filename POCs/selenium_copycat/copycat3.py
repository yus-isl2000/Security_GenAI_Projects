import json
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

API_KEY = os.getenv('API_KEY')  # Replace with your actual API key if not using environment variable

log_file = "user_actions.log"

# Call Gemini API
def call_gemini_api(prompt, api_key):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'contents': [
            {
                'parts': [
                    {
                        'text': prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        candidates = result.get('candidates', [])
        if candidates:
            first_candidate = candidates[0]
            content = first_candidate.get('content', {})
            parts = content.get('parts', [])
            if parts:
                return parts[0].get('text', '')
        return "No valid response from the API."
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

# Setup the WebDriver with performance logging
def setup_driver():
    chrome_options = Options()
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Inject JavaScript to capture DOM interactions
def inject_event_listeners(driver):
    script = """
    if (!window.capturedEvents) {
        window.capturedEvents = [];
        document.addEventListener('click', function(e) {
            try {
                window.capturedEvents.push({type: 'click', target: e.target.outerHTML});
            } catch (error) {
                window.capturedEvents.push({type: 'click', target: 'Error capturing target'});
            }
        });
        document.addEventListener('keydown', function(e) {
            window.capturedEvents.push({type: 'keydown', key: e.key});
        });
    }
    """
    driver.execute_script(script)

# Log user interactions and navigations
def capture_and_log_events(driver, duration):
    start_time = time.time()
    last_url = driver.current_url
    with open(log_file, "w") as log:
        log.write("User Actions Log:\n")
        while time.time() - start_time < duration:
            current_url = driver.current_url
            if current_url != last_url:
                log.write(f"Page navigation: {current_url}\n")
                inject_event_listeners(driver)
                last_url = current_url

            try:
                user_events = driver.execute_script("return window.capturedEvents || []; window.capturedEvents = [];")
            except Exception:
                user_events = []

            for event in user_events:
                if event.get("type") == "click":
                    target = event.get("target", "")
                    if len(target) > 500:
                        target = target[:500] + "..."
                    log.write(f"Click: {target}\n")
                elif event.get("type") == "keydown":
                    log.write(f"Key: {event['key']}\n")
            time.sleep(1)

# Main function
def main():
    driver = setup_driver()
    try:
        driver.get("https://google.com")
        inject_event_listeners(driver)
        print(f"Logging events to {log_file} for 20 seconds...")
        capture_and_log_events(driver, 20)

        # Read log file and call Gemini API
        with open(log_file, "r") as log:
            log_data = log.read()
        prompt = f"""Here is an example of automation using python3 and selenium: from selenium import webdriver

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    options = Options()
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        logging.error(f"Failed to initialize WebDriver: " + e)
        return None

def replay_events():
    driver = setup_driver()
    if driver is None:
        return

    try:
        # Search for "I'm samuel" on Google
        driver.get("https://www.google.com")
        search_box = driver.find_element("name", "q")
        search_box.send_keys("I'm samuel")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for search results

        #Simulate clicking on a search result (this part needs to be adapted based on actual search result structure)
        try:
          search_result = driver.find_element("xpath", "//a[contains(text(),'Samuel')]") #Example xpath, adjust as needed.
          search_result.click()
          time.sleep(3)
        except NoSuchElementException:
          logging.warning("Could not find expected search result.")

        #Search for "wikipedia" on Google
        driver.get("https://www.URL....")
        search_box = driver.find_element("name", "q")
        search_box.send_keys("......")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # Navigate to Wikipedia main page (this part needs to be adapted based on actual search result structure)
        try:
          wiki_link = driver.find_element("xpath", "//a[contains(@href, '....')]") #Example xpath, adjust as needed
          wiki_link.click()
          time.sleep(3)
        except NoSuchElementException:
          logging.warning("Could not find Wikipedia link in search results.")

        # Search for "warrior" on Wikipedia
        driver.get("......") # Assuming landing on main page after clicking wikipedia link.
        search_box = driver.find_element("id", "searchInput") #Example ID, adjust as needed.
        search_box.send_keys(".....")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)


        print("Replay completed successfully!")
    except NoSuchElementException as e:
        logging.error(f"Element not found: " + e )
    except WebDriverException as e:
        logging.error(f"WebDriver error: " + e)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    replay_events()

Based on the following log, GET THE GENERAL INTENT OF THE USER ACTIONS, then generate a Selenium replay script using python3:\n{log_data}\nOnly return the python3 script. add robust error handling, ensure that exceptions during WebDriver operations are caught, logged, and handled gracefully. Only write the script. Script:"""
        script = call_gemini_api(prompt, API_KEY)
        script = script.split("python")[1]
        script = script.split("```")[0]
        print(script)
        input("Press to continue...")

        # Save the generated script
        timestamp = int(time.time())
        replay_script_file = f"replay_{timestamp}.py"
        with open(replay_script_file, "w") as replay_file:
            replay_file.write(script)
        print(f"Generated replay script saved as {replay_script_file}")

        # Execute the generated replay script
        os.system(f"/Users/samuelmarticotte/Security_GenAI_Projects/POCs/.venv/bin/python {replay_script_file}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
