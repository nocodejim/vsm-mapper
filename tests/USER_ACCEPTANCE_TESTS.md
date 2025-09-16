# User Acceptance Tests for VSM Generator

This document describes the comprehensive user acceptance test suite for the Value Stream Map (VSM) Mermaid Generator application.

## Overview

The user acceptance tests validate the application against real-world business scenarios across multiple industries. Each test case represents a typical value stream mapping use case with known metrics and expected outcomes.

## Test Categories

### 1. Software Development Workflows
- **Agile Feature Development**: Complete feature lifecycle from backlog to production
- **Bug Fix Workflow**: Critical bug resolution process with tight timelines

### 2. Manufacturing Processes
- **Electronics Assembly Line**: Consumer electronics production workflow
- **Automotive Parts Production**: High-volume manufacturing with quality gates

### 3. Healthcare Patient Flow
- **Emergency Department**: Patient journey through emergency care
- **Surgical Procedure**: Elective surgery from scheduling to recovery

### 4. Financial Services
- **Loan Application Process**: Personal loan approval workflow with compliance checks

### 5. E-commerce Operations
- **Online Order Fulfillment**: Complete order processing from placement to delivery

### 6. Customer Support
- **Technical Support Ticket**: Customer issue resolution workflow

### 7. Edge Cases & Validation
- **Single Step Process**: Minimal workflow validation
- **Zero Wait Times**: Optimized process with no delays

## Test Scenarios Detail

### Software Development - Agile Feature Development
```
Steps: Backlog Item → Sprint Planning → Development → Code Review → QA Testing → Deployment
Process Times: 0.5, 2, 5, 1, 3, 0.5 (total: 12 units)
Wait Times: -, 3, 1, 0.5, 2, 1 (total: 7.5 units)
Expected Metrics:
- Process Time: 12 units
- Lead Time: 19.5 units  
- Flow Efficiency: 62%
```

### Manufacturing - Electronics Assembly Line
```
Steps: Component Prep → PCB Assembly → Testing → Case Assembly → Final QC → Packaging
Process Times: 15, 45, 20, 25, 10, 5 (total: 120 minutes)
Wait Times: -, 30, 60, 15, 45, 30 (total: 180 minutes)
Expected Metrics:
- Process Time: 120 minutes
- Lead Time: 300 minutes
- Flow Efficiency: 40%
```

### Healthcare - Emergency Department Patient Flow
```
Steps: Registration → Triage → Waiting Room → Doctor Exam → Lab/Imaging → Treatment → Discharge
Process Times: 5, 10, 0, 20, 15, 30, 10 (total: 90 minutes)
Wait Times: -, 15, 45, 30, 60, 20, 15 (total: 185 minutes)
Expected Metrics:
- Process Time: 90 minutes
- Lead Time: 275 minutes
- Flow Efficiency: 33%
```

## Test Features Validated

### Core Functionality
- ✅ **Form Input Validation**: Step names, process times, wait times
- ✅ **Dynamic Step Management**: Add, remove, insert steps
- ✅ **Mermaid Code Generation**: Syntactically correct output
- ✅ **Metrics Calculation**: Accurate PT, LT, FE calculations

### User Interface
- ✅ **Responsive Design**: Works across different screen sizes
- ✅ **Input Validation**: Proper error handling and user feedback
- ✅ **Step Management**: Intuitive add/remove/reorder functionality

### Preview Functionality
- ✅ **Modal Display**: Preview opens and renders correctly
- ✅ **Diagram Rendering**: Mermaid diagrams display properly
- ✅ **Zoom Controls**: Zoom in/out/reset functionality
- ✅ **Fullscreen Mode**: Expand to full screen view
- ✅ **Screenshot Capture**: Save diagrams as PNG images

### Export Capabilities
- ✅ **Markdown Export**: Download complete .md files
- ✅ **Code Copy**: Copy Mermaid syntax to clipboard
- ✅ **File Naming**: Proper filename generation with timestamps

### Import/Load Features
- ✅ **Text Import**: Load existing Mermaid code
- ✅ **Form Population**: Parse and populate form fields
- ✅ **Error Handling**: Graceful handling of invalid input

## Running the Tests

### Prerequisites
- Docker (for running the application)
- Python 3.7+ (for test execution)
- Chrome browser (for Selenium WebDriver)
- Internet connection (for downloading WebDriver)

### Quick Start

#### Linux/macOS
```bash
# Make script executable
chmod +x scripts/run_acceptance_tests.sh

# Run all tests
./scripts/run_acceptance_tests.sh

# Run with custom port
./scripts/run_acceptance_tests.sh --port 8081

# Run in headless mode
./scripts/run_acceptance_tests.sh --headless
```

#### Windows PowerShell
```powershell
# Run all tests
.\scripts\run_acceptance_tests.ps1

# Run with custom port
.\scripts\run_acceptance_tests.ps1 -Port 8081

# Run in headless mode
.\scripts\run_acceptance_tests.ps1 -Headless
```

### Manual Test Execution

1. **Start the Application**
   ```bash
   docker run -d -p 8080:8080 --name vsm-generator buckeye90/vsm-generator-app:latest
   ```

2. **Setup Python Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   
   pip install selenium webdriver-manager
   ```

3. **Run Tests**
   ```bash
   python tests/test_user_acceptance.py
   ```

## Test Configuration

### Environment Variables
- `HEADLESS_MODE`: Set to "true" for headless browser execution
- `TEST_TIMEOUT`: Override default timeout (30 seconds)
- `DOWNLOAD_DIR`: Custom download directory for test artifacts

### Test Parameters
```python
# In test_user_acceptance.py
DOWNLOAD_DIR = "/tmp/vsm_test_downloads/"  # Customize download location
BASE_URL = "http://localhost:8080"         # Application URL
TEST_TIMEOUT = 30                          # Default timeout in seconds
```

## Expected Test Results

### Success Criteria
- **100% Pass Rate**: All test scenarios should pass
- **Metrics Accuracy**: Calculated values match expected within tolerance
- **Feature Completeness**: All UI features function correctly
- **Performance**: Tests complete within reasonable time (< 5 minutes total)

### Tolerance Levels
- **Process/Lead Time**: ±0.1 units
- **Flow Efficiency**: ±1%
- **Response Time**: < 5 seconds per operation

## Test Output

### Console Output
```
========================================
Testing: Agile Feature Development
Industry: Software Development
Description: Typical agile software development cycle from backlog to production
========================================
✓ Metrics validated: PT=12.0, LT=19.5, FE=62%
✓ Preview functionality tested
✓ Export successful: Agile_Feature_Development_20250915_143022.md

Result: PASSED (took 8.3s)
```

### Generated Reports
- **JSON Report**: Detailed test results with timestamps
- **Downloaded Files**: Markdown exports and PNG screenshots
- **Error Logs**: Detailed failure information when tests fail

### Report Location
Test artifacts are saved to the configured download directory:
- Test report: `vsm_test_report_YYYYMMDD_HHMMSS.json`
- Exported files: `{TestName}_{Timestamp}.md`
- Screenshots: `{TestName}_{Timestamp}.png`

## Troubleshooting

### Common Issues

#### Application Not Starting
```
[ERROR] Application is not accessible at http://localhost:8080
```
**Solution**: Ensure Docker is running and port 8080 is available

#### WebDriver Issues
```
[ERROR] WebDriver setup failed
```
**Solution**: Ensure Chrome browser is installed and internet connection is available

#### Test Failures
```
[ERROR] Metric mismatch - Expected: {...}, Actual: {...}
```
**Solution**: Check application logic for calculation errors

### Debug Mode
Enable verbose logging by modifying the test file:
```python
# Uncomment debug lines in test_user_acceptance.py
print(f"--- Extracted Code ---\n{extracted_code}\n----------------------")
```

### Manual Verification
For failed tests, manually verify by:
1. Opening the application in a browser
2. Entering the test data manually
3. Comparing generated output with expected results

## Continuous Integration

### GitHub Actions Example
```yaml
name: User Acceptance Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run UAT
        run: |
          chmod +x scripts/run_acceptance_tests.sh
          ./scripts/run_acceptance_tests.sh --headless
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('User Acceptance Tests') {
            steps {
                sh 'chmod +x scripts/run_acceptance_tests.sh'
                sh './scripts/run_acceptance_tests.sh --headless'
            }
            post {
                always {
                    archiveArtifacts artifacts: '**/vsm_test_report_*.json'
                }
            }
        }
    }
}
```

## Contributing

### Adding New Test Scenarios
1. Define new `VSMTestCase` in `test_user_acceptance.py`
2. Include realistic business context and metrics
3. Add to `TEST_SCENARIOS` list
4. Update this documentation

### Test Case Template
```python
VSMTestCase(
    name="Your Test Name",
    description="Brief description of the business scenario",
    industry="Industry Category",
    steps=[
        ("Step Name", "Process Time", "Wait Time"),
        # ... more steps
    ],
    expected_metrics={'PT': X, 'LT': Y, 'FE': Z}
)
```

## Metrics Validation

### Calculation Logic
- **Process Time (PT)**: Sum of all step process times
- **Lead Time (LT)**: Process Time + Sum of all wait times
- **Flow Efficiency (FE)**: (Process Time / Lead Time) × 100

### Validation Rules
- All numeric values must be positive
- Flow Efficiency must be between 0% and 100%
- Lead Time must be greater than or equal to Process Time
- Wait times are optional for the first step

---

**Last Updated**: September 2025  
**Version**: 1.0  
**Maintainer**: VSM Generator Team