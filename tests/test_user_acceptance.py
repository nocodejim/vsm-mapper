#!/usr/bin/env python3
"""
Comprehensive User Acceptance Tests for VSM Generator Application

This test suite covers realistic business scenarios across different industries
with known metrics and expected outcomes. Each test case represents a real-world
value stream mapping scenario that users would encounter.

Test Categories:
1. Software Development Workflows
2. Manufacturing Processes  
3. Healthcare Patient Flow
4. Financial Services
5. E-commerce Order Processing
6. Customer Support Workflows
7. Edge Cases and Error Handling
"""

import os
import time
import re
import datetime
import shutil
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configuration
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', "/tmp/vsm_test_downloads/")
BASE_URL = os.getenv('BASE_URL', "http://localhost:8080")
TEST_TIMEOUT = int(os.getenv('TEST_TIMEOUT', '30'))
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'

class VSMTestCase:
    """Represents a single VSM test scenario with expected metrics"""
    
    def __init__(self, name, description, steps, expected_metrics, industry="General"):
        self.name = name
        self.description = description
        self.steps = steps  # List of (step_name, process_time, wait_time)
        self.expected_metrics = expected_metrics  # Dict with PT, LT, FE
        self.industry = industry
        
    def calculate_expected_metrics(self):
        """Calculate expected metrics from step data for validation"""
        process_times = []
        wait_times = []
        
        for i, (name, process_time, wait_time) in enumerate(self.steps):
            # Extract numeric value from process time
            pt_match = re.search(r'(\d+(?:\.\d+)?)', str(process_time))
            if pt_match:
                process_times.append(float(pt_match.group(1)))
            
            # Extract numeric value from wait time (skip first step)
            if i > 0 and wait_time:
                wt_match = re.search(r'(\d+(?:\.\d+)?)', str(wait_time))
                if wt_match:
                    wait_times.append(float(wt_match.group(1)))
        
        total_pt = sum(process_times)
        total_wt = sum(wait_times)
        total_lt = total_pt + total_wt
        flow_efficiency = (total_pt / total_lt * 100) if total_lt > 0 else 0
        
        return {
            'PT': total_pt,
            'LT': total_lt, 
            'FE': round(flow_efficiency)
        }

# Test Scenarios - Real World Business Cases
TEST_SCENARIOS = [
    # Software Development Scenarios
    VSMTestCase(
        name="Agile Feature Development",
        description="Typical agile software development cycle from backlog to production",
        industry="Software Development",
        steps=[
            ("Backlog Item", "0.5", ""),
            ("Sprint Planning", "2", "3"),
            ("Development", "5", "1"),
            ("Code Review", "1", "0.5"),
            ("QA Testing", "3", "2"),
            ("Deployment", "0.5", "1")
        ],
        expected_metrics={'PT': 12, 'LT': 19.5, 'FE': 62}
    ),
    
    VSMTestCase(
        name="Bug Fix Workflow", 
        description="Critical bug fix from report to production deployment",
        industry="Software Development",
        steps=[
            ("Bug Report", "0.25", ""),
            ("Triage", "0.5", "4"),
            ("Investigation", "2", "0.5"),
            ("Fix Development", "3", "1"),
            ("Testing", "1.5", "0.5"),
            ("Hotfix Deploy", "0.25", "2")
        ],
        expected_metrics={'PT': 7.5, 'LT': 15.75, 'FE': 48}
    ),
    
    # Manufacturing Scenarios
    VSMTestCase(
        name="Electronics Assembly Line",
        description="Consumer electronics manufacturing from components to packaging",
        industry="Manufacturing", 
        steps=[
            ("Component Prep", "15", ""),
            ("PCB Assembly", "45", "30"),
            ("Testing", "20", "60"),
            ("Case Assembly", "25", "15"),
            ("Final QC", "10", "45"),
            ("Packaging", "5", "30")
        ],
        expected_metrics={'PT': 120, 'LT': 300, 'FE': 40}
    ),
    
    VSMTestCase(
        name="Automotive Parts Production",
        description="High-volume automotive component manufacturing process",
        industry="Manufacturing",
        steps=[
            ("Raw Material", "5", ""),
            ("Machining", "30", "120"),
            ("Heat Treatment", "60", "240"),
            ("Finishing", "20", "60"),
            ("Quality Check", "15", "30"),
            ("Shipping Prep", "10", "180")
        ],
        expected_metrics={'PT': 140, 'LT': 770, 'FE': 18}
    ),
    
    # Healthcare Scenarios  
    VSMTestCase(
        name="Emergency Department Patient Flow",
        description="Patient journey through emergency department from arrival to discharge",
        industry="Healthcare",
        steps=[
            ("Registration", "5", ""),
            ("Triage", "10", "15"),
            ("Waiting Room", "0", "45"),
            ("Doctor Exam", "20", "30"),
            ("Lab/Imaging", "15", "60"),
            ("Treatment", "30", "20"),
            ("Discharge", "10", "15")
        ],
        expected_metrics={'PT': 90, 'LT': 275, 'FE': 33}
    ),
    
    VSMTestCase(
        name="Surgical Procedure Workflow",
        description="Elective surgery process from scheduling to recovery",
        industry="Healthcare", 
        steps=[
            ("Scheduling", "15", ""),
            ("Pre-op Prep", "60", "10080"), # 7 days wait
            ("Surgery", "180", "120"),
            ("Recovery", "240", "60"),
            ("Discharge Planning", "30", "480"), # 8 hours
            ("Follow-up", "20", "720") # 12 hours
        ],
        expected_metrics={'PT': 545, 'LT': 12005, 'FE': 5}
    ),
    
    # Financial Services
    VSMTestCase(
        name="Loan Application Process",
        description="Personal loan application from submission to approval",
        industry="Financial Services",
        steps=[
            ("Application", "30", ""),
            ("Document Review", "45", "2880"), # 2 days
            ("Credit Check", "15", "60"),
            ("Underwriting", "120", "1440"), # 1 day
            ("Approval Decision", "30", "480"), # 8 hours
            ("Funding", "15", "240") # 4 hours
        ],
        expected_metrics={'PT': 255, 'LT': 5355, 'FE': 5}
    ),
    
    # E-commerce
    VSMTestCase(
        name="Online Order Fulfillment",
        description="E-commerce order from placement to customer delivery",
        industry="E-commerce",
        steps=[
            ("Order Placed", "1", ""),
            ("Payment Processing", "2", "5"),
            ("Inventory Check", "3", "30"),
            ("Picking", "15", "60"),
            ("Packing", "10", "15"),
            ("Shipping", "5", "1440"), # 1 day transit
            ("Delivery", "2", "480") # 8 hours
        ],
        expected_metrics={'PT': 38, 'LT': 2068, 'FE': 2}
    ),
    
    # Customer Support
    VSMTestCase(
        name="Technical Support Ticket",
        description="Customer support ticket resolution workflow",
        industry="Customer Support",
        steps=[
            ("Ticket Created", "2", ""),
            ("Initial Response", "15", "240"), # 4 hours
            ("Investigation", "45", "60"),
            ("Solution Development", "90", "480"), # 8 hours
            ("Customer Testing", "30", "1440"), # 1 day
            ("Resolution", "10", "120") # 2 hours
        ],
        expected_metrics={'PT': 192, 'LT': 2532, 'FE': 8}
    ),
    
    # Edge Cases
    VSMTestCase(
        name="Single Step Process",
        description="Minimal process with just one step",
        industry="Testing",
        steps=[
            ("Complete Task", "60", "")
        ],
        expected_metrics={'PT': 60, 'LT': 60, 'FE': 100}
    ),
    
    VSMTestCase(
        name="Zero Wait Times",
        description="Optimized process with no wait times between steps",
        industry="Testing", 
        steps=[
            ("Step 1", "10", ""),
            ("Step 2", "15", "0"),
            ("Step 3", "20", "0"),
            ("Step 4", "5", "0")
        ],
        expected_metrics={'PT': 50, 'LT': 50, 'FE': 100}
    )
]

class VSMUserAcceptanceTest:
    """Main test class for running comprehensive user acceptance tests"""
    
    def __init__(self):
        self.driver = None
        self.test_results = []
        self.setup_download_dir()
        
    def setup_download_dir(self):
        """Ensure download directory exists and is clean"""
        if os.path.exists(DOWNLOAD_DIR):
            shutil.rmtree(DOWNLOAD_DIR)
        os.makedirs(DOWNLOAD_DIR)
        print(f"Created clean download directory: {DOWNLOAD_DIR}")
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with download settings"""
        print("Setting up Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        if HEADLESS_MODE:
            options.add_argument("--headless")
            print("Running in headless mode")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("WebDriver initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            return False
            
    def navigate_to_app(self):
        """Navigate to the VSM application"""
        print(f"Navigating to {BASE_URL}...")
        self.driver.get(BASE_URL)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "vsmForm"))
            )
            print("Application loaded successfully")
            return True
        except TimeoutException:
            print("Error: Application failed to load")
            return False
            
    def clear_form(self):
        """Clear the form to start fresh"""
        try:
            # Remove all steps except the first one
            while True:
                remove_buttons = self.driver.find_elements(By.CLASS_NAME, "remove-btn")
                if not remove_buttons:
                    break
                remove_buttons[0].click()
                time.sleep(0.2)
                
            # Clear the remaining step
            step_groups = self.driver.find_elements(By.CSS_SELECTOR, ".input-group")
            if step_groups:
                step_group = step_groups[0]
                inputs = step_group.find_elements(By.TAG_NAME, "input")
                for input_field in inputs:
                    input_field.clear()
                    
            # Clear title
            title_input = self.driver.find_element(By.ID, "diagramTitle")
            title_input.clear()
            
        except Exception as e:
            print(f"Warning: Error clearing form: {e}")
            
    def fill_test_case(self, test_case):
        """Fill the form with test case data"""
        print(f"Filling form for: {test_case.name}")
        
        # Set title
        title_input = self.driver.find_element(By.ID, "diagramTitle")
        title_input.clear()
        title_input.send_keys(test_case.name)
        
        # Fill first step
        self.fill_step_data(0, test_case.steps[0])
        
        # Add and fill remaining steps
        for i in range(1, len(test_case.steps)):
            # Add new step
            add_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "addStepEndBtn"))
            )
            add_button.click()
            
            # Wait for step to be added
            WebDriverWait(self.driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, ".input-group")) >= i + 1
            )
            
            # Fill step data
            self.fill_step_data(i, test_case.steps[i])
            
    def fill_step_data(self, step_index, step_data):
        """Fill data for a specific step"""
        name, process_time, wait_time = step_data
        
        step_groups = self.driver.find_elements(By.CSS_SELECTOR, ".input-group")
        if step_index >= len(step_groups):
            raise Exception(f"Step {step_index + 1} not found")
            
        step_group = step_groups[step_index]
        
        # Fill step name
        name_input = step_group.find_element(By.CSS_SELECTOR, "input[name='stepName']")
        name_input.clear()
        name_input.send_keys(name)
        
        # Fill process time
        process_input = step_group.find_element(By.CSS_SELECTOR, "input[name='processTime']")
        process_input.clear()
        process_input.send_keys(str(process_time))
        
        # Fill wait time (if provided and not first step)
        if wait_time and step_index > 0:
            wait_input = step_group.find_element(By.CSS_SELECTOR, "input[name='waitTime']")
            wait_input.clear()
            wait_input.send_keys(str(wait_time))
            
    def generate_and_validate(self, test_case):
        """Generate Mermaid code and validate output"""
        print(f"Generating code for: {test_case.name}")
        
        # Click generate button
        generate_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "generate-btn"))
        )
        generate_button.click()
        
        # Wait for output
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "outputContainer"))
        )
        
        # Get generated output
        output_element = self.driver.find_element(By.ID, "mermaidOutput")
        generated_code = output_element.text
        
        # Validate metrics in output
        return self.validate_metrics(generated_code, test_case)
        
    def validate_metrics(self, generated_code, test_case):
        """Validate that generated metrics match expected values"""
        expected = test_case.calculate_expected_metrics()
        
        # Extract metrics from generated code
        pt_match = re.search(r'Process Time:\s*(\d+(?:\.\d+)?)', generated_code)
        lt_match = re.search(r'Lead Time:\s*(\d+(?:\.\d+)?)', generated_code)
        fe_match = re.search(r'Flow Efficiency:\s*(\d+)%', generated_code)
        
        if not all([pt_match, lt_match, fe_match]):
            return False, "Could not extract metrics from generated code"
            
        actual = {
            'PT': float(pt_match.group(1)),
            'LT': float(lt_match.group(1)),
            'FE': int(fe_match.group(1))
        }
        
        # Compare with tolerance for floating point
        tolerance = 0.1
        pt_ok = abs(actual['PT'] - expected['PT']) <= tolerance
        lt_ok = abs(actual['LT'] - expected['LT']) <= tolerance
        fe_ok = abs(actual['FE'] - expected['FE']) <= 1  # 1% tolerance for FE
        
        if pt_ok and lt_ok and fe_ok:
            return True, f"Metrics validated: PT={actual['PT']}, LT={actual['LT']}, FE={actual['FE']}%"
        else:
            return False, f"Metric mismatch - Expected: {expected}, Actual: {actual}"
            
    def test_preview_functionality(self):
        """Test the preview modal functionality"""
        print("Testing preview functionality...")
        
        try:
            # Click preview button
            preview_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "previewBtn"))
            )
            preview_btn.click()
            
            # Wait for modal to open
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "previewModal"))
            )
            
            # Wait for diagram to render
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#mermaidPreview svg"))
            )
            
            # Test zoom controls
            zoom_in_btn = self.driver.find_element(By.ID, "zoomInBtn")
            zoom_level = self.driver.find_element(By.ID, "zoomLevel")
            
            initial_zoom = zoom_level.text
            zoom_in_btn.click()
            time.sleep(0.5)
            new_zoom = zoom_level.text
            
            zoom_works = initial_zoom != new_zoom
            
            # Close modal
            close_btn = self.driver.find_element(By.ID, "closePreviewBtn")
            close_btn.click()
            time.sleep(0.5)
            
            return zoom_works, "Preview functionality tested"
            
        except Exception as e:
            return False, f"Preview test failed: {e}"
            
    def test_export_functionality(self):
        """Test markdown export functionality"""
        print("Testing export functionality...")
        
        try:
            # Clear any existing downloads
            for file in os.listdir(DOWNLOAD_DIR):
                os.remove(os.path.join(DOWNLOAD_DIR, file))
                
            # Click save markdown button
            save_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "saveMarkdownBtn"))
            )
            save_btn.click()
            
            # Wait for download
            start_time = time.time()
            while time.time() - start_time < 10:
                files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.md')]
                if files:
                    return True, f"Export successful: {files[0]}"
                time.sleep(0.5)
                
            return False, "Export timed out"
            
        except Exception as e:
            return False, f"Export test failed: {e}"
            
    def run_test_case(self, test_case):
        """Run a complete test for a single test case"""
        print(f"\n{'='*60}")
        print(f"Testing: {test_case.name}")
        print(f"Industry: {test_case.industry}")
        print(f"Description: {test_case.description}")
        print(f"{'='*60}")
        
        result = {
            'name': test_case.name,
            'industry': test_case.industry,
            'description': test_case.description,
            'passed': False,
            'errors': [],
            'metrics_valid': False,
            'preview_works': False,
            'export_works': False,
            'execution_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Clear form and fill with test data
            self.clear_form()
            self.fill_test_case(test_case)
            
            # Generate and validate
            metrics_valid, metrics_msg = self.generate_and_validate(test_case)
            result['metrics_valid'] = metrics_valid
            if not metrics_valid:
                result['errors'].append(metrics_msg)
            else:
                print(f"✓ {metrics_msg}")
                
            # Test preview
            preview_works, preview_msg = self.test_preview_functionality()
            result['preview_works'] = preview_works
            if not preview_works:
                result['errors'].append(preview_msg)
            else:
                print(f"✓ {preview_msg}")
                
            # Test export
            export_works, export_msg = self.test_export_functionality()
            result['export_works'] = export_works
            if not export_works:
                result['errors'].append(export_msg)
            else:
                print(f"✓ {export_msg}")
                
            # Overall pass/fail
            result['passed'] = metrics_valid and preview_works and export_works
            
        except Exception as e:
            result['errors'].append(f"Test execution failed: {e}")
            print(f"✗ Test failed: {e}")
            
        result['execution_time'] = time.time() - start_time
        
        status = "PASSED" if result['passed'] else "FAILED"
        print(f"\nResult: {status} (took {result['execution_time']:.1f}s)")
        
        return result
        
    def run_all_tests(self):
        """Run all test scenarios"""
        print("Starting comprehensive user acceptance tests...")
        print(f"Total scenarios: {len(TEST_SCENARIOS)}")
        
        if not self.setup_driver():
            print("Failed to setup WebDriver")
            return False
            
        if not self.navigate_to_app():
            print("Failed to load application")
            return False
            
        # Run each test scenario
        for test_case in TEST_SCENARIOS:
            result = self.run_test_case(test_case)
            self.test_results.append(result)
            
        # Generate summary report
        self.generate_report()
        
        return True
        
    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("USER ACCEPTANCE TEST REPORT")
        print(f"{'='*80}")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group by industry
        by_industry = {}
        for result in self.test_results:
            industry = result['industry']
            if industry not in by_industry:
                by_industry[industry] = []
            by_industry[industry].append(result)
            
        print(f"\n{'='*40}")
        print("RESULTS BY INDUSTRY")
        print(f"{'='*40}")
        
        for industry, results in by_industry.items():
            industry_passed = sum(1 for r in results if r['passed'])
            print(f"\n{industry}: {industry_passed}/{len(results)} passed")
            
            for result in results:
                status = "✓" if result['passed'] else "✗"
                print(f"  {status} {result['name']} ({result['execution_time']:.1f}s)")
                
                if result['errors']:
                    for error in result['errors']:
                        print(f"    - {error}")
                        
        # Feature-specific results
        print(f"\n{'='*40}")
        print("FEATURE TEST RESULTS")
        print(f"{'='*40}")
        
        metrics_passed = sum(1 for r in self.test_results if r['metrics_valid'])
        preview_passed = sum(1 for r in self.test_results if r['preview_works'])
        export_passed = sum(1 for r in self.test_results if r['export_works'])
        
        print(f"Metrics Calculation: {metrics_passed}/{total_tests} ({(metrics_passed/total_tests)*100:.1f}%)")
        print(f"Preview Functionality: {preview_passed}/{total_tests} ({(preview_passed/total_tests)*100:.1f}%)")
        print(f"Export Functionality: {export_passed}/{total_tests} ({(export_passed/total_tests)*100:.1f}%)")
        
        # Save detailed report to file
        report_file = os.path.join(DOWNLOAD_DIR, f"vsm_test_report_{datetime.datetime.now():%Y%m%d_%H%M%S}.json")
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'success_rate': (passed_tests/total_tests)*100,
                    'timestamp': datetime.datetime.now().isoformat()
                },
                'results': self.test_results
            }, f, indent=2)
            
        print(f"\nDetailed report saved to: {report_file}")
        
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            print("WebDriver closed")

def main():
    """Main test execution"""
    tester = VSMUserAcceptanceTest()
    
    try:
        success = tester.run_all_tests()
        if success:
            print("\n🎉 User acceptance testing completed successfully!")
        else:
            print("\n❌ User acceptance testing failed to complete")
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()