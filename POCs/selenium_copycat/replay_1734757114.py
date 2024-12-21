
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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
        logging.error(f"Failed to initialize WebDriver: {e}")
        return None

def replay_events():
    driver = setup_driver()
    if driver is None:
        return

    try:
        # Search for "wikipedia" on Google
        driver.get("https://www.google.com")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys("wikiepdia")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # Navigate to Wikipedia main page
        try:
            wiki_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/wiki/Main_Page')]"))
            )
            wiki_link.click()
            time.sleep(3)
        except (NoSuchElementException, TimeoutException) as e:
            logging.warning(f"Could not find Wikipedia link in Google search results: {e}")
            return


        # Search for "warren buffet" on Wikipedia
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_box.send_keys("warren buffet")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        #Robustly handle potential errors during navigation
        try:
          buffet_link = WebDriverWait(driver, 10).until(
              EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/wiki/Warren_Buffett')]"))
          )
          buffet_link.click()
          time.sleep(3)
        except (NoSuchElementException, TimeoutException) as e:
            logging.warning(f"Could not find Warren Buffett link in Wikipedia search results: {e}")


        print("Replay completed successfully!")

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Element not found or timeout: {e}")
    except WebDriverException as e:
        logging.error(f"WebDriver error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    replay_events()
