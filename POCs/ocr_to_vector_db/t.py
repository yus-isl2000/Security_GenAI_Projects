import pyautogui

# Capture the screenshot
screenshot = pyautogui.screenshot()

# Define the file path
file_path = '/Users/samuelmarticotte/tests/test.png'

# Save the screenshot
screenshot.save(file_path)

print(f"Screenshot saved to {file_path}")

from ocrmac import ocrmac
annotations = ocrmac.OCR('test.png').recognize()
print(annotations)
