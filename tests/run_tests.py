#!/usr/bin/env python3
"""
VSM Generator Test Runner
Provides easy commands to run different test scenarios
"""

import sys
import os
import subprocess
import argparse

def get_python_executable():
    """Get the appropriate Python executable (venv if available, otherwise system)"""
    test_dir = os.path.dirname(__file__)
    venv_path = os.path.join(test_dir, "test_env")
    
    if os.path.exists(venv_path):
        if os.name == 'nt':  # Windows
            venv_python = os.path.join(venv_path, "Scripts", "python.exe")
        else:  # Unix/Linux/Mac
            venv_python = os.path.join(venv_path, "bin", "python")
        
        if os.path.exists(venv_python):
            print(f"Using virtual environment: {venv_python}")
            return venv_python
    
    print("Virtual environment not found, using system Python")
    print("Run 'python tests/setup_selenium_tests.py' first to create isolated environment")
    return sys.executable

def run_basic_test():
    """Run the original basic test"""
    print("Running basic VSM creation test...")
    python_exe = get_python_executable()
    result = subprocess.run([python_exe, "test_vsm_generator.py"], 
                          cwd=os.path.dirname(__file__))
    return result.returncode == 0

def run_comprehensive_tests():
    """Run the full comprehensive test suite"""
    print("Running comprehensive test suite...")
    python_exe = get_python_executable()
    result = subprocess.run([python_exe, "test_vsm_generator.py", "--comprehensive"], 
                          cwd=os.path.dirname(__file__))
    return result.returncode == 0

def run_specific_test(test_name):
    """Run a specific test by name"""
    print(f"Running specific test: {test_name}")
    python_exe = get_python_executable()
    result = subprocess.run([
        python_exe, "-m", "unittest", 
        f"test_vsm_generator.VSMGeneratorTestSuite.{test_name}"
    ], cwd=os.path.dirname(__file__))
    return result.returncode == 0

def list_available_tests():
    """List all available tests"""
    tests = [
        "test_01_basic_vsm_creation",
        "test_02_preview_functionality", 
        "test_03_step_management",
        "test_04_input_validation",
        "test_05_complex_workflow",
        "test_06_export_functionality",
        "test_07_keyboard_shortcuts",
        "test_08_responsive_design",
        "test_09_error_recovery",
        "test_10_performance_large_dataset"
    ]
    
    print("Available tests:")
    for i, test in enumerate(tests, 1):
        print(f"  {i:2d}. {test}")
    
    return tests

def main():
    parser = argparse.ArgumentParser(description="VSM Generator Test Runner")
    parser.add_argument("--basic", action="store_true", 
                       help="Run basic test only")
    parser.add_argument("--comprehensive", action="store_true",
                       help="Run comprehensive test suite")
    parser.add_argument("--test", type=str,
                       help="Run specific test by name")
    parser.add_argument("--list", action="store_true",
                       help="List available tests")
    
    args = parser.parse_args()
    
    if args.list:
        list_available_tests()
        return
        
    if args.test:
        success = run_specific_test(args.test)
    elif args.comprehensive:
        success = run_comprehensive_tests()
    elif args.basic:
        success = run_basic_test()
    else:
        # Interactive mode
        print("VSM Generator Test Runner")
        print("========================")
        print("1. Basic test (original)")
        print("2. Comprehensive test suite")
        print("3. List available tests")
        print("4. Run specific test")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            success = run_basic_test()
        elif choice == "2":
            success = run_comprehensive_tests()
        elif choice == "3":
            tests = list_available_tests()
            test_choice = input(f"\nEnter test number (1-{len(tests)}) or name: ").strip()
            
            if test_choice.isdigit():
                test_idx = int(test_choice) - 1
                if 0 <= test_idx < len(tests):
                    success = run_specific_test(tests[test_idx])
                else:
                    print("Invalid test number")
                    return
            else:
                success = run_specific_test(test_choice)
        elif choice == "4":
            test_name = input("Enter test name: ").strip()
            success = run_specific_test(test_name)
        else:
            print("Invalid choice")
            return
    
    if success:
        print("\n✅ Tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()