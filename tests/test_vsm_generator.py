import os
import time
import re
import datetime
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

# --- Configuration ---
# !!! IMPORTANT: Set this to an existing directory where Chrome can download files !!!
# You might need to create this directory first. Use absolute paths.
# Example Windows: DOWNLOAD_DIR = "C:\\Users\\YourUser\\Downloads\\vsm_test_downloads"
# Example macOS/Linux: DOWNLOAD_DIR = "/Users/youruser/Downloads/vsm_test_downloads"
DOWNLOAD_DIR = "/mnt/a/tmp/vsm_test_downloads/" # CHANGE THIS PATH

BASE_URL = "http://localhost:8080"
EXPECTED_MERMAID_OUTPUT = """
graph LR
    S0["Feature Request"]
    S0 -->|1| S1
    S1["Work Order"]
    S1 -->|3 days| S2
    S2["Requirement"]
    S2 -->|3| S3
    S3["Development"]
    S3 -->|14| S4
    S4["Test"]
    S4 -->|5| S5
    S5["Production"]

    %% Add wait times
    S0 -.->|Wait: 5| S1
    S1 -.->|Wait: 5| S2
    S2 -.->|Wait: 14| S3
    S3 -.->|Wait: 12| S4
    S4 -.->|Wait: 14| S5

    %% Add process metrics
    subgraph Metrics
        PT[Process Time: 27 units]
        LT[Lead Time: 77 units]
        FE[Flow Efficiency: 35%]
    end
""".strip() # Use strip() to remove leading/trailing whitespace from the expected string

# Test data: List of tuples (Step Name, Process Time, Wait Time)
# Wait time for step 1 (index 0) will be ignored but provided for structure.
# Wait time for subsequent steps is required.
TEST_STEPS_DATA = [
    ("Feature Request", "1", ""),       # Step 1 (Wait time ignored)
    ("Work Order", "3 days", "5"),      # Step 2
    ("Requirement", "3", "5"),          # Step 3
    ("Development", "14", "14"),        # Step 4
    ("Test", "5", "12"),                # Step 5
    ("Production", "1", "14")           # Step 6 (Process time used for calc, not shown on arrow)
                                        # Note: The expected output has PT=27 (1+3+3+14+5+1=27), Wait=5+5+14+12+14=50, LT=77. FE=27/77=35%
]

# --- Helper Functions ---

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def setup_driver(download_dir):
    """Sets up the Chrome WebDriver with specific download options."""
    print(f"Setting up Chrome WebDriver. Download directory: {download_dir}")
    # Ensure download directory exists
    if not os.path.exists(download_dir):
        print(f"Creating download directory: {download_dir}")
        os.makedirs(download_dir)
    elif not os.path.isdir(download_dir):
         print(f"Error: Provided download path '{download_dir}' exists but is not a directory.")
         return None

    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False, # Disable download prompt
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True # Enable safe browsing (recommended)
    }
    options.add_experimental_option("prefs", prefs)
    # options.add_argument("--headless")  # Run headless (no visible browser window) - uncomment for CI/automation
    options.add_argument("--no-sandbox") # Often needed in CI environments
    options.add_argument("--disable-dev-shm-usage") # Overcome resource limitations
    options.add_argument("--window-size=1920,1080") # Specify window size

    try:
        # Use webdriver_manager to handle driver installation
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("WebDriver initialized successfully.")
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        print("Ensure Chrome is installed correctly.")
        return None
    
def fill_step_data(driver, step_index, step_data):
    """Fills the input fields for a specific step."""
    print(f"Filling data for Step {step_index + 1}: {step_data[0]}")
    name, process_time, wait_time = step_data
    try:
        # Find all input groups and get the one at the specified index
        step_groups = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".input-group"))
        )
        
        if step_index >= len(step_groups):
            print(f"Error: Not enough step groups found. Needed index {step_index}, found {len(step_groups)} groups.")
            return False
            
        step_group = step_groups[step_index]
        step_id = step_group.get_attribute("data-step-id")
        
        # Find inputs within the specific step group
        name_input = step_group.find_element(By.CSS_SELECTOR, f"input[name='stepName']")
        process_time_input = step_group.find_element(By.CSS_SELECTOR, f"input[name='processTime']")
        wait_time_input = step_group.find_element(By.CSS_SELECTOR, f"input[name='waitTime']")

        name_input.clear()
        name_input.send_keys(name)

        process_time_input.clear()
        process_time_input.send_keys(process_time)

        # Only fill wait time if it's provided (and not the first step conceptually)
        if wait_time:
             wait_time_input.clear()
             wait_time_input.send_keys(wait_time)
        return True
    except (NoSuchElementException, TimeoutException) as e: # Catch specific Selenium exceptions
        print(f"Error finding input elements for Step {step_index + 1}: {e}")
        return False
    except Exception as e:
        print(f"Error filling data for Step {step_index + 1}: {e}")
        return False

def wait_for_download_complete(download_dir, timeout=30, file_extension=".md"):
    """Waits for a file with specified extension to appear in the download directory."""
    print(f"Waiting for {file_extension} file download in '{download_dir}' (timeout: {timeout}s)...")
    start_time = time.time()
    downloaded_file_path = None
    while time.time() - start_time < timeout:
        # Look for files with specified extension that are not temporary download files
        try:
            files = [f for f in os.listdir(download_dir) 
                    if f.endswith(file_extension) and not f.endswith(".crdownload")]
            if files:
                # Assume the latest downloaded file is the correct one
                latest_file = max([os.path.join(download_dir, f) for f in files], key=os.path.getctime)
                # Check if file size is stable (simple check)
                initial_size = os.path.getsize(latest_file)
                time.sleep(0.5) # Wait a bit for write to complete
                # Check again if file still exists (might be deleted quickly)
                if os.path.exists(latest_file) and os.path.getsize(latest_file) == initial_size > 0:
                    downloaded_file_path = latest_file
                    print(f"Download detected: {downloaded_file_path}")
                    return downloaded_file_path
        except FileNotFoundError:
             print(f"Warning: Download directory '{download_dir}' not found during check. Retrying...")
             # Directory might be created slightly later, keep checking
        except Exception as e:
            print(f"Warning: Error checking download directory: {e}. Retrying...")
        time.sleep(0.5) # Check every half second

    print(f"Error: {file_extension} download timed out or file did not appear/stabilize.")
    return None

def extract_mermaid_block(markdown_content):
    """Extracts the content within the ```mermaid block."""
    print("Extracting Mermaid code block from Markdown content...")
    # Use regex to find the block, ignoring leading/trailing whitespace and case for 'mermaid'
    # DOTALL flag makes '.' match newlines
    match = re.search(r"```mermaid\s*\n(.*?)\n\s*```", markdown_content, re.IGNORECASE | re.DOTALL)
    if match:
        extracted_code = match.group(1).strip()
        print("Mermaid block found.")
        # print(f"--- Extracted Code ---\n{extracted_code}\n----------------------") # Uncomment for debugging
        return extracted_code
    else:
        print("Error: Could not find ```mermaid block in the downloaded file.")
        print("--- File Content ---") # Log content for debugging
        print(markdown_content)
        print("--------------------")
        return None

def normalize_whitespace(text):
    """Normalizes whitespace for comparison: strips lines, removes blank lines."""
    if not text:
        return ""
    # Split by newline, strip whitespace from each line, filter out empty lines
    lines = [line.strip() for line in text.strip().split('\n')]
    non_empty_lines = [line for line in lines if line]
    return "\n".join(non_empty_lines)

def test_preview_functionality(driver):
    """Tests the preview modal functionality."""
    print("\n--- Testing Preview Functionality ---")
    test_results = {"preview_button": False, "modal_open": False, "zoom_controls": False, 
                   "fullscreen": False, "close_modal": False, "screenshot": False}
    
    try:
        # Test 1: Check if preview button is enabled after generating code
        print("Test 1: Checking preview button availability...")
        preview_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "previewBtn"))
        )
        test_results["preview_button"] = True
        print("✓ Preview button is enabled")
        
        # Test 2: Click preview button and check if modal opens
        print("Test 2: Opening preview modal...")
        preview_btn.click()
        
        # Wait for modal to be visible
        preview_modal = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "previewModal"))
        )
        
        # Wait for Mermaid diagram to render
        mermaid_preview = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mermaidPreview"))
        )
        
        # Check if SVG is rendered
        svg_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mermaidPreview svg"))
        )
        test_results["modal_open"] = True
        print("✓ Preview modal opened and diagram rendered")
        
        # Test 3: Test zoom controls
        print("Test 3: Testing zoom controls...")
        zoom_in_btn = driver.find_element(By.ID, "zoomInBtn")
        zoom_out_btn = driver.find_element(By.ID, "zoomOutBtn")
        zoom_level = driver.find_element(By.ID, "zoomLevel")
        
        initial_zoom = zoom_level.text
        print(f"  Initial zoom: {initial_zoom}")
        
        # Zoom in
        zoom_in_btn.click()
        time.sleep(0.5)
        zoomed_in = zoom_level.text
        print(f"  After zoom in: {zoomed_in}")
        
        # Zoom out
        zoom_out_btn.click()
        time.sleep(0.5)
        zoomed_out = zoom_level.text
        print(f"  After zoom out: {zoomed_out}")
        
        # Reset zoom
        reset_zoom_btn = driver.find_element(By.ID, "resetZoomBtn")
        reset_zoom_btn.click()
        time.sleep(0.5)
        reset_zoom = zoom_level.text
        print(f"  After reset: {reset_zoom}")
        
        test_results["zoom_controls"] = (initial_zoom != zoomed_in and 
                                       zoomed_in != zoomed_out and 
                                       reset_zoom == initial_zoom)
        if test_results["zoom_controls"]:
            print("✓ Zoom controls working correctly")
        else:
            print("✗ Zoom controls not working as expected")
        
        # Test 4: Test fullscreen toggle
        print("Test 4: Testing fullscreen toggle...")
        fullscreen_btn = driver.find_element(By.ID, "fullscreenBtn")
        minimize_btn = driver.find_element(By.ID, "minimizeBtn")
        preview_container = driver.find_element(By.ID, "previewContainer")
        
        # Enter fullscreen
        fullscreen_btn.click()
        time.sleep(0.5)
        has_fullscreen_class = "fullscreen" in preview_container.get_attribute("class")
        minimize_visible = minimize_btn.is_displayed()
        fullscreen_hidden = not fullscreen_btn.is_displayed()
        
        # Exit fullscreen
        minimize_btn.click()
        time.sleep(0.5)
        no_fullscreen_class = "fullscreen" not in preview_container.get_attribute("class")
        
        test_results["fullscreen"] = (has_fullscreen_class and minimize_visible and 
                                    fullscreen_hidden and no_fullscreen_class)
        if test_results["fullscreen"]:
            print("✓ Fullscreen toggle working correctly")
        else:
            print("✗ Fullscreen toggle not working as expected")
        
        # Test 5: Test screenshot functionality
        print("Test 5: Testing screenshot (PNG save) functionality...")
        camera_btn = driver.find_element(By.ID, "cameraBtn")
        
        # Clean PNG files before test
        png_files_before = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".png")]
        for png in png_files_before:
            try:
                os.remove(os.path.join(DOWNLOAD_DIR, png))
            except:
                pass
        
        camera_btn.click()
        
        # Wait for PNG download
        png_file = wait_for_download_complete(DOWNLOAD_DIR, timeout=10, file_extension=".png")
        if png_file:
            test_results["screenshot"] = True
            print(f"✓ Screenshot saved successfully: {os.path.basename(png_file)}")
            # Verify PNG file size
            file_size = os.path.getsize(png_file)
            print(f"  PNG file size: {file_size} bytes")
        else:
            print("✗ Screenshot save failed or timed out")
        
        # Test 6: Test close modal
        print("Test 6: Testing modal close...")
        close_btn = driver.find_element(By.ID, "closePreviewBtn")
        close_btn.click()
        time.sleep(0.5)
        
        # Check if modal is hidden
        modal_hidden = driver.find_element(By.ID, "previewModal").get_attribute("style") == "display: none;"
        test_results["close_modal"] = modal_hidden
        if test_results["close_modal"]:
            print("✓ Modal closed successfully")
        else:
            print("✗ Modal did not close properly")
        
    except TimeoutException as e:
        print(f"Timeout error during preview testing: {e}")
    except Exception as e:
        print(f"Unexpected error during preview testing: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n--- Preview Test Summary ---")
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    print(f"Passed: {passed_tests}/{total_tests}")
    for test_name, passed in test_results.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    return passed_tests == total_tests

# --- Main Test Execution ---
if __name__ == "__main__":
    print("Starting VSM Generator UI Test...")
    driver = None
    downloaded_file = None
    errors = []
    test_passed = False
    preview_tests_passed = False

    try:
        # 0. Clean download directory (optional: ensures only test file is present)
        if os.path.exists(DOWNLOAD_DIR):
             print(f"Cleaning download directory: {DOWNLOAD_DIR}")
             for filename in os.listdir(DOWNLOAD_DIR):
                 file_path = os.path.join(DOWNLOAD_DIR, filename)
                 try:
                     if os.path.isfile(file_path) or os.path.islink(file_path):
                         os.unlink(file_path)
                     elif os.path.isdir(file_path):
                         shutil.rmtree(file_path)
                 except Exception as e:
                     print(f'Failed to delete {file_path}. Reason: {e}')
        else:
            # If cleaning is desired but dir doesn't exist, create it now
            print(f"Creating download directory before test: {DOWNLOAD_DIR}")
            os.makedirs(DOWNLOAD_DIR)


        # 1. Setup WebDriver
        driver = setup_driver(DOWNLOAD_DIR)
        if not driver:
            raise Exception("WebDriver setup failed.")

        # 2. Navigate to the page
        print(f"Navigating to {BASE_URL}...")
        driver.get(BASE_URL)
        # Use WebDriverWait instead of time.sleep() for page load confirmation
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "vsmForm")) # Wait for form element
            )
            print("Page loaded successfully.")
        except TimeoutException:
            print("Error: Page did not load within timeout.")
            errors.append("Page load timeout.")
            raise

        # 3. Fill the form data
        print("Filling form data...")
        # First step is already created by default in the new version
        # Just fill the first step data
        if not fill_step_data(driver, 0, TEST_STEPS_DATA[0]):
            errors.append(f"Failed to fill data for Step 1.")
            raise Exception(f"Data entry failed for Step 1.") # Stop test
            
        # Add and fill the remaining steps
        for i in range(1, len(TEST_STEPS_DATA)):
            try:
                # Click "Add Step at End" button for steps after the first
                add_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "addStepEndBtn"))
                )
                add_button.click()
                print(f"Clicked 'Add Step at End' for Step {i + 1}")
                
                # Wait for all step groups to be updated
                WebDriverWait(driver, 5).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, ".input-group")) >= i + 1
                )
                
                if not fill_step_data(driver, i, TEST_STEPS_DATA[i]):
                    errors.append(f"Failed to fill data for Step {i + 1}.")
                    raise Exception(f"Data entry failed for Step {i + 1}.") # Stop test
                    
            except TimeoutException:
                print(f"Error: Could not find/click 'Add Step at End' or new step group did not appear before Step {i + 1}")
                errors.append("Could not click 'Add Step at End' button or step group missing.")
                raise # Stop test if essential button fails

        # 4. Generate the code
        print("Clicking 'Generate Mermaid Code'...")
        try:
            generate_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "generate-btn"))
            )
            generate_button.click()
            # Wait for output area to become visible AND the save button to be enabled
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "outputContainer"))
            )
            WebDriverWait(driver, 5).until(
                 EC.element_to_be_clickable((By.ID, "saveMarkdownBtn")) # Check if save button is clickable
            )
            print("Output container appeared and save button enabled.")
        except TimeoutException:
            print("Error: Could not click 'Generate' or output/save button did not appear/enable.")
            errors.append("Generate button/output failed.")
            raise

        # 5. Save the Markdown file
        print("Clicking 'Save as Markdown (.md)'...")
        try:
            # Re-find save button to avoid stale element reference
            save_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "saveMarkdownBtn"))
            )
            save_button.click()
        except TimeoutException:
            print("Error: Could not click 'Save as Markdown' button.")
            errors.append("Save button failed.")
            raise

        # 6. Wait for download and verify file
        downloaded_file = wait_for_download_complete(DOWNLOAD_DIR)
        if not downloaded_file:
            errors.append("Markdown file download failed or timed out.")
            raise Exception("Download failed.")

        # 7. Read downloaded file content
        print(f"Reading content from {downloaded_file}...")
        try:
            # Add a small delay before reading, sometimes helps with filesystem lag
            time.sleep(0.5)
            with open(downloaded_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except Exception as e:
             print(f"Error reading downloaded file: {e}")
             errors.append(f"Could not read downloaded file: {e}")
             raise

        # 8. Extract Mermaid block
        actual_mermaid_output = extract_mermaid_block(markdown_content)
        if actual_mermaid_output is None:
            errors.append("Could not extract Mermaid block from downloaded file.")
            raise Exception("Mermaid block extraction failed.")

        # 9. Compare actual vs expected (after normalizing whitespace)
        print("Comparing generated Mermaid code with expected output...")
        normalized_actual = normalize_whitespace(actual_mermaid_output)
        normalized_expected = normalize_whitespace(EXPECTED_MERMAID_OUTPUT)

        # print(f"--- Normalized Actual ---\n{normalized_actual}\n-------------------------") # Uncomment for debugging
        # print(f"--- Normalized Expected ---\n{normalized_expected}\n-------------------------") # Uncomment for debugging

        if normalized_actual == normalized_expected:
            print("Comparison successful: Mermaid code matches expected output.")
            test_passed = True
        else:
            print("Comparison failed: Mermaid code does NOT match expected output.")
            errors.append("Generated Mermaid code mismatch.")
            # Optional: Print diff or detailed mismatch info here
            print("\n--- DIFFERENCE ---")
            print("Expected:")
            print(normalized_expected)
            print("\nActual:")
            print(normalized_actual)
            print("----------------\n")

        # 10. Test Preview Functionality (NEW)
        if test_passed:
            preview_tests_passed = test_preview_functionality(driver)
            if not preview_tests_passed:
                errors.append("Preview functionality tests failed.")

    except Exception as e:
        print(f"\n--- TEST FAILED ---")
        print(f"An error occurred during the test: {e}")
        # Attempt to capture screenshot on failure
        if driver:
            try:
                screenshot_path = os.path.join(DOWNLOAD_DIR, f"failure_screenshot_{datetime.datetime.now():%Y%m%d_%H%M%S}.png")
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved to: {screenshot_path}")
            except Exception as se:
                print(f"Could not save screenshot: {se}")

        if not errors: # Add the exception itself if no specific error was logged
             errors.append(str(e))

    finally:
        # 11. Print final result
        print("\n--- TEST SUMMARY ---")
        if test_passed and preview_tests_passed:
            # Use Unicode characters for checkmark
            print(" \u2705\u2705\u2705 ALL TESTS PASSED \u2705\u2705\u2705")
        else:
             # Use Unicode characters for cross mark
            print(" \u274C\u274C\u274C TEST FAILED \u274C\u274C\u274C")
            print("Errors encountered:")
            for i, err in enumerate(errors):
                print(f"  {i+1}. {err}")

        # 12. Cleanup
        if driver:
            print("Closing WebDriver...")
            driver.quit()

        # # Optional: Delete the downloaded file after test (keep for debugging if failed?)
        # if test_passed and downloaded_file and os.path.exists(downloaded_file):
        #      print(f"Deleting downloaded file: {downloaded_file}")
        #      os.remove(downloaded_file)
        # elif not test_passed and downloaded_file:
        #      print(f"Keeping failed downloaded file for inspection: {downloaded_file}")

        print("--------------------\nTest finished.")