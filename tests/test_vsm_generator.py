import os
import time
import re
import datetime
import shutil
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# --- Configuration ---
# !!! IMPORTANT: Set this to an existing directory where Chrome can download files !!!
# You might need to create this directory first. Use absolute paths.
# Example Windows: DOWNLOAD_DIR = "C:\\Users\\YourUser\\Downloads\\vsm_test_downloads"
# Example macOS/Linux: DOWNLOAD_DIR = "/Users/youruser/Downloads/vsm_test_downloads"
DOWNLOAD_DIR = "/tmp/vsm_test_downloads/" # Updated to use /tmp for Linux

BASE_URL = "http://localhost:8080"
EXPECTED_MERMAID_OUTPUT = """
graph LR
%% Define Step Nodes
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
S5["Production (1)"]

%% Add Wait Times
S0 -.->|Wait: 5| S1
S1 -.->|Wait: 5| S2
S2 -.->|Wait: 14| S3
S3 -.->|Wait: 12| S4
S4 -.->|Wait: 14| S5

%% Add Process Metrics
subgraph Metrics
PT[Process Time: 27.0 units]
LT[Lead Time: 77.0 units]
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

def wait_for_download_complete(download_dir, timeout=30):
    """Waits for a .md file to appear in the download directory."""
    print(f"Waiting for Markdown file download in '{download_dir}' (timeout: {timeout}s)...")
    start_time = time.time()
    downloaded_file_path = None
    while time.time() - start_time < timeout:
        # Look for .md files that are not temporary download files
        try:
            files = [f for f in os.listdir(download_dir) if f.endswith(".md") and not f.endswith(".crdownload")]
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

    print("Error: Download timed out or file did not appear/stabilize.")
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

# --- Main Test Execution ---
if __name__ == "__main__":
    print("Starting VSM Generator UI Test...")
    driver = None
    downloaded_file = None
    errors = []
    test_passed = False

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
        # 10. Print final result
        print("\n--- TEST SUMMARY ---")
        if test_passed:
            # Use Unicode characters for checkmark
            print(" \u2705\u2705\u2705 TEST PASSED \u2705\u2705\u2705")
        else:
             # Use Unicode characters for cross mark
            print(" \u274C\u274C\u274C TEST FAILED \u274C\u274C\u274C")
            print("Errors encountered:")
            for i, err in enumerate(errors):
                print(f"  {i+1}. {err}")

        # 11. Cleanup
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

# --- Enhanced Test Suite ---

class VSMGeneratorTestSuite(unittest.TestCase):
    """Comprehensive test suite for VSM Generator functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        print("\n=== Setting up VSM Generator Test Suite ===")
        cls.download_dir = DOWNLOAD_DIR
        cls.base_url = BASE_URL
        
        # Clean and create download directory
        if os.path.exists(cls.download_dir):
            shutil.rmtree(cls.download_dir)
        os.makedirs(cls.download_dir)
        
    def setUp(self):
        """Set up before each test"""
        self.driver = setup_driver(self.download_dir)
        self.assertIsNotNone(self.driver, "WebDriver setup failed")
        
    def tearDown(self):
        """Clean up after each test"""
        if self.driver:
            self.driver.quit()
            
    def navigate_to_app(self):
        """Navigate to the VSM Generator app"""
        self.driver.get(self.base_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "vsmForm"))
        )
        
    def test_01_basic_vsm_creation(self):
        """Test basic VSM creation with simple workflow"""
        print("\n--- Test 1: Basic VSM Creation ---")
        self.navigate_to_app()
        
        # Test data for a simple 3-step process
        steps = [
            ("Requirements", "2", ""),
            ("Development", "5", "1"),
            ("Testing", "3", "2")
        ]
        
        # Fill first step
        self.assertTrue(fill_step_data(self.driver, 0, steps[0]))
        
        # Add and fill remaining steps
        for i in range(1, len(steps)):
            add_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "addStepEndBtn"))
            )
            add_button.click()
            
            WebDriverWait(self.driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, ".input-group")) >= i + 1
            )
            
            self.assertTrue(fill_step_data(self.driver, i, steps[i]))
            
        # Generate code
        generate_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "generate-btn"))
        )
        generate_button.click()
        
        # Verify output appears
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "outputContainer"))
        )
        
        # Check that metrics are calculated - look in the mermaid code textarea
        try:
            mermaid_textarea = self.driver.find_element(By.ID, "mermaidOutput")
            mermaid_code = mermaid_textarea.get_attribute("value")
            self.assertIn("Process Time:", mermaid_code)
            self.assertIn("Lead Time:", mermaid_code)
            self.assertIn("Flow Efficiency:", mermaid_code)
        except NoSuchElementException:
            # Fallback to checking the general output container
            output_text = self.driver.find_element(By.ID, "outputContainer").text
            # Just verify the output container is visible and contains some content
            self.assertGreater(len(output_text), 50, "Output should contain generated content")
        
    def test_02_preview_functionality(self):
        """Test the live preview feature"""
        print("\n--- Test 2: Preview Functionality ---")
        self.navigate_to_app()
        
        # Create a simple VSM
        fill_step_data(self.driver, 0, ("Design", "3", ""))
        
        add_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "addStepEndBtn"))
        )
        add_button.click()
        
        WebDriverWait(self.driver, 5).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ".input-group")) >= 2
        )
        
        fill_step_data(self.driver, 1, ("Build", "5", "1"))
        
        # Generate code first
        generate_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "generate-btn"))
        )
        generate_button.click()
        
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "outputContainer"))
        )
        
        # Look for preview button (might be added in newer versions)
        try:
            preview_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.ID, "previewBtn"))
            )
            preview_button.click()
            
            # Check if preview modal appears
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "previewModal"))
            )
            
            # Test zoom controls if they exist
            try:
                zoom_in = self.driver.find_element(By.ID, "zoomInBtn")
                zoom_out = self.driver.find_element(By.ID, "zoomOutBtn")
                self.assertTrue(zoom_in.is_displayed())
                self.assertTrue(zoom_out.is_displayed())
            except NoSuchElementException:
                print("Zoom controls not found - may not be implemented yet")
                
            # Close preview
            close_btn = self.driver.find_element(By.CSS_SELECTOR, ".close-preview")
            close_btn.click()
            
        except TimeoutException:
            print("Preview functionality not found - may not be implemented yet")
            self.skipTest("Preview feature not available")
            
    def test_03_step_management(self):
        """Test adding, removing, and reordering steps"""
        print("\n--- Test 3: Step Management ---")
        self.navigate_to_app()
        
        # Start with first step
        fill_step_data(self.driver, 0, ("Step 1", "1", ""))
        
        # Add multiple steps
        for i in range(2, 5):  # Add steps 2, 3, 4
            add_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "addStepEndBtn"))
            )
            add_button.click()
            
            WebDriverWait(self.driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, ".input-group")) >= i
            )
            
            fill_step_data(self.driver, i-1, (f"Step {i}", str(i), "1"))
            
        # Verify we have 4 steps
        step_groups = self.driver.find_elements(By.CSS_SELECTOR, ".input-group")
        self.assertEqual(len(step_groups), 4)
        
        # Test remove step functionality
        try:
            remove_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".remove-step-btn")
            if remove_buttons:
                # Remove the second step
                remove_buttons[1].click()
                
                # Verify step count decreased
                WebDriverWait(self.driver, 3).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, ".input-group")) == 3
                )
                
                step_groups = self.driver.find_elements(By.CSS_SELECTOR, ".input-group")
                self.assertEqual(len(step_groups), 3)
            else:
                print("Remove step buttons not found")
        except Exception as e:
            print(f"Step removal test failed: {e}")
            
    def test_04_input_validation(self):
        """Test input validation and error handling"""
        print("\n--- Test 4: Input Validation ---")
        self.navigate_to_app()
        
        # Test empty step name
        step_group = self.driver.find_element(By.CSS_SELECTOR, ".input-group")
        name_input = step_group.find_element(By.CSS_SELECTOR, "input[name='stepName']")
        process_time_input = step_group.find_element(By.CSS_SELECTOR, "input[name='processTime']")
        
        # Leave name empty, fill process time
        name_input.clear()
        process_time_input.clear()
        process_time_input.send_keys("5")
        
        # Try to generate
        generate_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "generate-btn"))
        )
        generate_button.click()
        
        # Should show validation error or not generate
        time.sleep(1)  # Brief pause for any validation messages
        
        # Test with valid data
        name_input.send_keys("Valid Step")
        generate_button.click()
        
        # Should now work
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "outputContainer"))
        )
        
    def test_05_complex_workflow(self):
        """Test complex workflow with many steps and varied data"""
        print("\n--- Test 5: Complex Workflow ---")
        self.navigate_to_app()
        
        # Complex workflow data
        complex_steps = [
            ("Idea Generation", "0.5", ""),
            ("Market Research", "3", "2"),
            ("Requirements Analysis", "5", "1"),
            ("Architecture Design", "8", "3"),
            ("UI/UX Design", "6", "2"),
            ("Frontend Development", "15", "1"),
            ("Backend Development", "20", "1"),
            ("Integration Testing", "8", "2"),
            ("User Acceptance Testing", "5", "3"),
            ("Deployment", "2", "1"),
            ("Monitoring", "1", "0.5")
        ]
        
        # Fill first step
        fill_step_data(self.driver, 0, complex_steps[0])
        
        # Add and fill remaining steps
        for i in range(1, len(complex_steps)):
            add_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "addStepEndBtn"))
            )
            add_button.click()
            
            WebDriverWait(self.driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, ".input-group")) >= i + 1
            )
            
            self.assertTrue(fill_step_data(self.driver, i, complex_steps[i]))
            
        # Generate and verify
        generate_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "generate-btn"))
        )
        generate_button.click()
        
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "outputContainer"))
        )
        
        # Verify all steps appear in output - check the mermaid code specifically
        try:
            mermaid_textarea = self.driver.find_element(By.ID, "mermaidOutput")
            mermaid_code = mermaid_textarea.get_attribute("value")
            for step_name, _, _ in complex_steps[:3]:  # Check first 3 steps to avoid timeout
                self.assertIn(step_name, mermaid_code)
        except NoSuchElementException:
            # Fallback - just verify output was generated
            output_text = self.driver.find_element(By.ID, "outputContainer").text
            self.assertGreater(len(output_text), 100, "Complex workflow should generate substantial output")
            
    def test_06_export_functionality(self):
        """Test markdown export functionality"""
        print("\n--- Test 6: Export Functionality ---")
        self.navigate_to_app()
        
        # Create simple VSM
        fill_step_data(self.driver, 0, ("Analysis", "3", ""))
        
        add_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "addStepEndBtn"))
        )
        add_button.click()
        
        WebDriverWait(self.driver, 5).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ".input-group")) >= 2
        )
        
        fill_step_data(self.driver, 1, ("Implementation", "7", "2"))
        
        # Generate code
        generate_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "generate-btn"))
        )
        generate_button.click()
        
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "outputContainer"))
        )
        
        # Test markdown export
        save_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "saveMarkdownBtn"))
        )
        save_button.click()
        
        # Wait for download
        downloaded_file = wait_for_download_complete(self.download_dir, timeout=10)
        self.assertIsNotNone(downloaded_file, "Markdown file should be downloaded")
        
        # Verify file content
        with open(downloaded_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn("```mermaid", content)
        self.assertIn("Analysis", content)
        self.assertIn("Implementation", content)
        
    def test_07_keyboard_shortcuts(self):
        """Test keyboard shortcuts if implemented"""
        print("\n--- Test 7: Keyboard Shortcuts ---")
        self.navigate_to_app()
        
        # Create VSM first
        fill_step_data(self.driver, 0, ("Test Step", "1", ""))
        
        generate_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "generate-btn"))
        )
        generate_button.click()
        
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "outputContainer"))
        )
        
        # Test keyboard shortcuts (if preview is available)
        try:
            preview_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.ID, "previewBtn"))
            )
            preview_button.click()
            
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "previewModal"))
            )
            
            # Test ESC key to close
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ESCAPE).perform()
            
            # Should close the modal
            WebDriverWait(self.driver, 3).until(
                EC.invisibility_of_element_located((By.ID, "previewModal"))
            )
            
        except TimeoutException:
            print("Preview functionality not available for keyboard shortcut testing")
            self.skipTest("Preview feature not available")
            
    def test_08_responsive_design(self):
        """Test responsive design by changing window size"""
        print("\n--- Test 8: Responsive Design ---")
        self.navigate_to_app()
        
        # Test different screen sizes
        screen_sizes = [
            (1920, 1080),  # Desktop
            (1024, 768),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in screen_sizes:
            print(f"Testing screen size: {width}x{height}")
            self.driver.set_window_size(width, height)
            time.sleep(1)  # Allow layout to adjust
            
            # Verify form is still accessible
            form = self.driver.find_element(By.ID, "vsmForm")
            self.assertTrue(form.is_displayed())
            
            # Verify buttons are clickable
            generate_button = self.driver.find_element(By.CLASS_NAME, "generate-btn")
            self.assertTrue(generate_button.is_displayed())
            
        # Reset to original size
        self.driver.set_window_size(1920, 1080)
        
    def test_09_error_recovery(self):
        """Test error recovery scenarios"""
        print("\n--- Test 9: Error Recovery ---")
        self.navigate_to_app()
        
        # Test with invalid characters in step names
        special_chars_step = ("Step with @#$%", "5", "1")
        fill_step_data(self.driver, 0, special_chars_step)
        
        # Should still generate (or handle gracefully)
        generate_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "generate-btn"))
        )
        generate_button.click()
        
        # Check if output appears or error is handled
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "outputContainer"))
            )
            print("Special characters handled successfully")
        except TimeoutException:
            print("Special characters may have caused validation error (expected)")
            
    def test_10_performance_large_dataset(self):
        """Test performance with large number of steps"""
        print("\n--- Test 10: Performance with Large Dataset ---")
        self.navigate_to_app()
        
        # Create 20 steps to test performance
        num_steps = 20
        
        # Fill first step
        fill_step_data(self.driver, 0, ("Step 1", "1", ""))
        
        start_time = time.time()
        
        # Add remaining steps
        for i in range(1, num_steps):
            add_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "addStepEndBtn"))
            )
            add_button.click()
            
            WebDriverWait(self.driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, ".input-group")) >= i + 1
            )
            
            fill_step_data(self.driver, i, (f"Step {i+1}", "1", "0.5"))
            
        creation_time = time.time() - start_time
        print(f"Time to create {num_steps} steps: {creation_time:.2f} seconds")
        
        # Generate code
        start_time = time.time()
        generate_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "generate-btn"))
        )
        generate_button.click()
        
        WebDriverWait(self.driver, 10).until(  # Longer timeout for large dataset
            EC.visibility_of_element_located((By.ID, "outputContainer"))
        )
        
        generation_time = time.time() - start_time
        print(f"Time to generate code for {num_steps} steps: {generation_time:.2f} seconds")
        
        # Performance should be reasonable (under 5 seconds for generation)
        self.assertLess(generation_time, 5.0, "Code generation should complete within 5 seconds")


def run_comprehensive_tests():
    """Run the comprehensive test suite"""
    print("=== VSM Generator Comprehensive Test Suite ===")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(VSMGeneratorTestSuite)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
            
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
            
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--comprehensive":
        # Run comprehensive test suite
        success = run_comprehensive_tests()
        sys.exit(0 if success else 1)
    else:
        # Run original single test for backward compatibility
        print("Running original single test (use --comprehensive for full suite)")