# VSM Generator Test Suite

This directory contains a comprehensive Selenium-based test suite for the VSM (Value Stream Map) Generator web application.

## Overview

The test suite validates all major functionality of the VSM Generator, including:
- Basic VSM creation workflows
- Step management (add, remove, reorder)
- Input validation and error handling
- Export functionality (Markdown files)
- Responsive design across different screen sizes
- Performance with large datasets
- Preview features (when available)
- Keyboard shortcuts

**Default Mode**: Tests run in headless mode for faster execution and better CI/CD compatibility. Use `--windowed` flag for debugging with visible browser window.

## Files

- `test_vsm_generator.py` - Main test file with comprehensive test suite
- `run_tests.py` - Test runner with multiple execution options
- `setup_selenium_tests.py` - Environment setup script (creates virtual environment)
- `test_env/` - Virtual environment for test dependencies (created by setup)

## Environment Isolation

**Important**: This test suite follows strict environment isolation rules:
- All dependencies are installed in a virtual environment (`test_env/`)
- No system-level packages are installed
- Chrome/Chromium browser is the only system requirement

## Quick Start

1. **Setup test environment** (one-time):
   ```bash
   python3 tests/setup_selenium_tests.py
   ```

2. **Ensure VSM app is running**:
   ```bash
   ./scripts/deploy.sh
   ```

3. **Run tests**:
   ```bash
   # Interactive menu (headless by default)
   python tests/run_tests.py
   
   # Specific test types (headless by default)
   python tests/run_tests.py --basic
   python tests/run_tests.py --comprehensive
   python tests/run_tests.py --test test_01_basic_vsm_creation
   
   # Run with visible browser window (for debugging)
   python tests/run_tests.py --windowed --basic
   python tests/run_tests.py --windowed --comprehensive
   
   # Explicitly run headless (default behavior)
   python tests/run_tests.py --headless --basic
   ```

## Test Categories

### Core Functionality Tests
- **test_01_basic_vsm_creation**: Simple 3-step VSM workflow
- **test_04_input_validation**: Form validation and error handling
- **test_06_export_functionality**: Markdown file export

### Advanced Feature Tests
- **test_02_preview_functionality**: Live preview modal (if implemented)
- **test_07_keyboard_shortcuts**: Preview keyboard shortcuts (if implemented)

### User Interface Tests
- **test_03_step_management**: Add, remove, reorder steps
- **test_08_responsive_design**: Multiple screen sizes
- **test_09_error_recovery**: Special characters and edge cases

### Performance Tests
- **test_05_complex_workflow**: 11-step complex workflow
- **test_10_performance_large_dataset**: 20-step performance test

## Test Results

Recent test run results:
- ✅ 8 tests passed
- ⏭️ 2 tests skipped (preview features not yet implemented)
- ❌ 0 tests failed (after fixes)

### Performance Benchmarks
- Creating 20 steps: ~28 seconds
- Generating code for 20 steps: ~0.5 seconds
- Export functionality: <2 seconds

## Requirements

### System Requirements
- Python 3.7+
- Google Chrome or Chromium browser
- Docker (for running the VSM app)

### Python Dependencies (installed in virtual environment)
- selenium==4.35.0
- webdriver-manager==4.0.2

## Configuration

### Download Directory
Tests use `/tmp/vsm_test_downloads/` for file downloads. This is automatically created and cleaned.

### App URL
Tests expect the VSM Generator to be running at `http://localhost:8080`.

### Browser Settings
- **Default Mode**: Headless (no browser window, faster execution)
- **Debug Mode**: Windowed mode available with `--windowed` flag
- Window size: 1920x1080 (adjustable in responsive tests)
- Downloads are automatically handled
- GPU acceleration disabled in headless mode for stability

## Troubleshooting

### Common Issues

1. **"WebDriver setup failed"**
   - Ensure Chrome/Chromium is installed
   - Run setup script: `python3 tests/setup_selenium_tests.py`

2. **"VSM Generator app not detected"**
   - Start the app: `./scripts/deploy.sh`
   - Verify at http://localhost:8080

3. **"Virtual environment not found"**
   - Run setup: `python3 tests/setup_selenium_tests.py`
   - Or manually activate: `source tests/test_env/bin/activate`

4. **Tests timeout or fail**
   - Check if app is responsive
   - Verify Chrome browser is working
   - Check download directory permissions

### Debug Mode

For debugging failed tests:
- **Use windowed mode**: `python tests/run_tests.py --windowed --test test_name`
- **Environment variable**: Set `VSM_TEST_HEADLESS=false` to show browser window
- Screenshots are automatically saved on failures
- Browser console logs can be accessed via F12 (in windowed mode)
- Increase timeouts in test code if needed

#### Switching Between Modes
```bash
# Run in headless mode (default, faster)
python tests/run_tests.py --basic

# Run in windowed mode (for debugging)
python tests/run_tests.py --windowed --basic

# Set environment variable for entire session
export VSM_TEST_HEADLESS=false  # Linux/Mac
set VSM_TEST_HEADLESS=false     # Windows
python tests/run_tests.py --basic
```

## Extending Tests

To add new tests:

1. Add test method to `VSMGeneratorTestSuite` class
2. Follow naming convention: `test_##_descriptive_name`
3. Use existing helper functions (`fill_step_data`, etc.)
4. Include proper assertions and error handling

Example:
```python
def test_11_new_feature(self):
    """Test description"""
    print("\n--- Test 11: New Feature ---")
    self.navigate_to_app()
    
    # Test implementation
    # ...
    
    # Assertions
    self.assertTrue(condition, "Error message")
```

## Contributing

When modifying tests:
1. Maintain environment isolation (no system installs)
2. Update expected outputs if app behavior changes
3. Add appropriate timeouts for UI interactions
4. Include descriptive error messages in assertions
5. Test on different screen sizes when relevant

## License

Same as parent project (MIT License)