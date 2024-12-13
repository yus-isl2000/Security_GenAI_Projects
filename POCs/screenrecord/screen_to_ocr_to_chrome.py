import pyautogui
import time
from ocrmac import ocrmac
import chromadb
import os
import pywinctl

# Initialize Chroma client with persistent storage
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create or retrieve a collection
collection = chroma_client.get_or_create_collection(name="screenshot_texts")

# Define the file paths
screenshot_path = '/Users/samuelmarticotte/tests/test.png'
output_file = '/Users/samuelmarticotte/tests/ocr_output.txt'

# Ensure the output file exists
if not os.path.exists(output_file):
    with open(output_file, 'w') as f:
        pass

print("Starting the automated screenshot and OCR process. Press Ctrl+C to stop.")

try:
    while True:

        # Retrieve the active window's title
        active_window = pywinctl.getActiveWindow()
        window_title = active_window.title if active_window else "Unknown Window"
        if "Slack" not in window_title:
            time.sleep(1)
            continue

        print("Found Slack window! Starting process...")

        # Capture and save the screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        # Perform OCR on the saved screenshot
        annotations = ocrmac.OCR(screenshot_path).recognize()

        # Extract and compile the recognized text
        extracted_text = ' '.join([text for text, confidence, bbox in annotations])
        extracted_text = extracted_text.split("All Bookmarks")[1]
        print(extracted_text)

        # Generate a unique ID for the document
        doc_id = f"doc_{int(time.time())}"

        # Add the extracted text to the Chroma collection
        collection.add(documents=[extracted_text], ids=[doc_id])
        print(f"Extracted text added to ChromaDB with ID: {doc_id}")

        # Append the extracted text and window title to the output file with separators
        with open(output_file, 'a') as f:
            f.write(f"\n{'='*40}\n")
            f.write(f"Window Title: {window_title}\n")
            f.write(f"Timestamp: {time.ctime()}\n")
            f.write(f"{'-'*40}\n")
            f.write(f"{extracted_text}\n")
            f.write(f"{'='*40}\n")
        print(f"Extracted text appended to {output_file}")

        # Open the output file for quick review
        os.system(f"open {output_file}")

        # Wait for 10 seconds before the next capture
        time.sleep(10)

except KeyboardInterrupt:
    print("\nProcess terminated by user.")

