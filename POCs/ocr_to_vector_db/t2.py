# pip install pyautogui ocrmac

import pyautogui
import time
from ocrmac import ocrmac
import os

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
        # Capture and save the screenshot
        pyautogui.screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        # Perform OCR on the saved screenshot
        annotations = ocrmac.OCR(screenshot_path).recognize()

        # Extract and compile the recognized text
        extracted_text = ' '.join([text for text, confidence, bbox in annotations])

        # Append the extracted text to the output file
        with open(output_file, 'a') as f:
            f.write(extracted_text + '\n')

        print(f"Extracted text appended to {output_file}")
        os.system("open /Users/samuelmarticotte/tests/ocr_output.txt")
        # Wait for 10 seconds before the next capture
        time.sleep(10)

except KeyboardInterrupt:
    print("\nProcess terminated by user.")

