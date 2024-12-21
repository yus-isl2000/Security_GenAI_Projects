from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

# Setup the WebDriver
def setup_driver():
    options = Options()
    driver = webdriver.Chrome(options=options)
    return driver

# Main function to replay events
def replay_events():
    driver = setup_driver()
    try:
        # Start at the initial URL
        driver.get("https://www.google.com")

        # Simulate key presses
        search_box = driver.find_element("name", "q")  # Google's search input box
        search_box.send_keys("h")
        search_box.send_keys("i")
        search_box.send_keys(Keys.SHIFT, "!")
        search_box.send_keys(Keys.RETURN)  # Submit the form
        
        # Wait for navigation
        time.sleep(3)
        
        # Page navigation detected: Clicking on 'Dictionary'
        dictionary_heading = driver.find_element("xpath", '//div[@class="gJBeNe d2F2Td" and @aria-level="2"]')
        dictionary_heading.click()
        dictionary_heading.click()  # Repeat the click as per the log
        
        # Wait for navigation to Merriam-Webster
        time.sleep(3)
        driver.get("https://www.merriam-webster.com/dictionary/hi")  # Final page navigation
        
        print("Replay completed successfully!")
    finally:
        driver.quit()

if __name__ == "__main__":
    replay_events()
