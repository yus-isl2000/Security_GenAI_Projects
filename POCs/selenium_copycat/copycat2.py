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
    actions = []
    last_url = driver.current_url  # Track the current URL

    while time.time() - start_time < duration:
        # Check if the URL has changed
        current_url = driver.current_url
        if current_url != last_url:
            print(f"Page change: {current_url}")
            inject_event_listeners(driver)  # Reinject event listeners
            last_url = current_url

        # Capture DOM events (clicks, inputs, etc.)
        try:
            user_events = driver.execute_script("return window.capturedEvents || []; window.capturedEvents = [];")
        except Exception as e:
            print(f"Error retrieving events: {e}")
            user_events = []

        for event in user_events:
            if event.get("type") == "click":
                target = event.get("target", "")
                if len(target) > 500:  # Truncate overly verbose targets
                    target = target[:500] + "..."
                actions.append(f"Simulated click on {target}")
                print(f"Click: {event}")
            elif event.get("type") == "keydown":
                actions.append(f"Typed '{event['key']}'")
                print(f"Key: {event}")
        
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
