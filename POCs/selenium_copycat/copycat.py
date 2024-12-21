import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Setup the WebDriver with performance logging
def setup_driver():
    chrome_options = Options()
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Inject JavaScript to capture DOM interactions
def inject_event_listeners(driver):
    script = """
    window.capturedEvents = [];
    document.addEventListener('click', function(e) {
        window.capturedEvents.push({type: 'click', target: e.target.outerHTML});
    });
    document.addEventListener('keydown', function(e) {
        window.capturedEvents.push({type: 'keydown', key: e.key});
    });
    """
    driver.execute_script(script)

# Log user interactions and navigations
def capture_and_log_events(driver, duration):
    start_time = time.time()
    actions = []
    last_url = driver.current_url  # Track the current URL

    while time.time() - start_time < duration:
        # Capture network events for URLs
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if log["method"] == "Network.requestWillBeSent":
                    url = log["params"]["request"]["url"]
                    actions.append(f"driver.get('{url}')")
            except Exception:
                pass

        # Check if the URL has changed
        current_url = driver.current_url
        if current_url != last_url:
            print(f"Page navigation detected: {current_url}")
            inject_event_listeners(driver)  # Reinject event listeners
            last_url = current_url

        # Capture DOM events (clicks, inputs, etc.)
        user_events = driver.execute_script("return window.capturedEvents || []; window.capturedEvents = [];")
        for event in user_events:
            if event.get("type") == "click":
                actions.append(f"Simulated click on {event['target']}")
                print(f"Captured Click: {event}")
            elif event.get("type") == "keydown":
                actions.append(f"Typed '{event['key']}'")
                print(f"Captured Keydown: {event}")
        
        time.sleep(1)  # Poll every second

    return actions

# Main function
def main():
    driver = setup_driver()
    try:
        driver.get("https://google.com")
        inject_event_listeners(driver)
        print("Capturing events for 60 seconds...")
        actions = capture_and_log_events(driver, 60)
        
        # Save captured actions to a file
        output_file = "captured_actions.json"
        with open(output_file, "w") as f:
            json.dump(actions, f, indent=2)
        print(f"Captured actions saved to {output_file}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
