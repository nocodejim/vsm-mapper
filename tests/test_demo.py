#!/usr/bin/env python3
"""
Demo User Acceptance Test for VSM Generator

This is a simplified demonstration of the user acceptance testing framework
that shows how the tests work with realistic business scenarios.
"""

import os
import time
import json
from datetime import datetime

# Mock test results to demonstrate the framework
class MockVSMTest:
    def __init__(self):
        self.test_results = []
        
    def run_demo_tests(self):
        """Run demonstration tests with mock results"""
        
        # Define realistic test scenarios
        scenarios = [
            {
                'name': 'Agile Feature Development',
                'industry': 'Software Development',
                'description': 'Complete feature lifecycle from backlog to production',
                'steps': [
                    ('Backlog Item', '0.5', ''),
                    ('Sprint Planning', '2', '3'),
                    ('Development', '5', '1'),
                    ('Code Review', '1', '0.5'),
                    ('QA Testing', '3', '2'),
                    ('Deployment', '0.5', '1')
                ],
                'expected_metrics': {'PT': 12, 'LT': 19.5, 'FE': 62}
            },
            {
                'name': 'Electronics Assembly Line',
                'industry': 'Manufacturing',
                'description': 'Consumer electronics production workflow',
                'steps': [
                    ('Component Prep', '15', ''),
                    ('PCB Assembly', '45', '30'),
                    ('Testing', '20', '60'),
                    ('Case Assembly', '25', '15'),
                    ('Final QC', '10', '45'),
                    ('Packaging', '5', '30')
                ],
                'expected_metrics': {'PT': 120, 'LT': 300, 'FE': 40}
            },
            {
                'name': 'Emergency Department Patient Flow',
                'industry': 'Healthcare',
                'description': 'Patient journey through emergency care',
                'steps': [
                    ('Registration', '5', ''),
                    ('Triage', '10', '15'),
                    ('Waiting Room', '0', '45'),
                    ('Doctor Exam', '20', '30'),
                    ('Lab/Imaging', '15', '60'),
                    ('Treatment', '30', '20'),
                    ('Discharge', '10', '15')
                ],
                'expected_metrics': {'PT': 90, 'LT': 275, 'FE': 33}
            },
            {
                'name': 'Online Order Fulfillment',
                'industry': 'E-commerce',
                'description': 'Complete order processing from placement to delivery',
                'steps': [
                    ('Order Placed', '1', ''),
                    ('Payment Processing', '2', '5'),
                    ('Inventory Check', '3', '30'),
                    ('Picking', '15', '60'),
                    ('Packing', '10', '15'),
                    ('Shipping', '5', '1440'),
                    ('Delivery', '2', '480')
                ],
                'expected_metrics': {'PT': 38, 'LT': 2068, 'FE': 2}
            }
        ]
        
        print("VSM Generator User Acceptance Test Demo")
        print("=" * 50)
        print(f"Running {len(scenarios)} test scenarios...")
        print()
        
        # Simulate running each test
        for i, scenario in enumerate(scenarios, 1):
            print(f"Test {i}/{len(scenarios)}: {scenario['name']}")
            print(f"Industry: {scenario['industry']}")
            print(f"Description: {scenario['description']}")
            print()
            
            # Simulate test execution time
            start_time = time.time()
            time.sleep(0.5)  # Simulate test execution
            
            # Calculate metrics from steps
            calculated_metrics = self.calculate_metrics(scenario['steps'])
            
            # Simulate test validation
            metrics_match = self.validate_metrics(calculated_metrics, scenario['expected_metrics'])
            
            # Mock other test results
            result = {
                'name': scenario['name'],
                'industry': scenario['industry'],
                'description': scenario['description'],
                'steps': scenario['steps'],
                'expected_metrics': scenario['expected_metrics'],
                'calculated_metrics': calculated_metrics,
                'passed': metrics_match,
                'metrics_valid': metrics_match,
                'preview_works': True,  # Mock success
                'export_works': True,   # Mock success
                'execution_time': time.time() - start_time,
                'errors': [] if metrics_match else ['Metrics calculation mismatch']
            }
            
            self.test_results.append(result)
            
            # Display results
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            print(f"Result: {status}")
            print(f"Expected: PT={scenario['expected_metrics']['PT']}, "
                  f"LT={scenario['expected_metrics']['LT']}, "
                  f"FE={scenario['expected_metrics']['FE']}%")
            print(f"Calculated: PT={calculated_metrics['PT']}, "
                  f"LT={calculated_metrics['LT']}, "
                  f"FE={calculated_metrics['FE']}%")
            print(f"Execution time: {result['execution_time']:.2f}s")
            print("-" * 50)
            print()
        
        # Generate summary
        self.generate_summary()
        
    def calculate_metrics(self, steps):
        """Calculate PT, LT, FE from step data"""
        process_times = []
        wait_times = []
        
        for i, (name, process_time, wait_time) in enumerate(steps):
            # Extract numeric value from process time
            try:
                pt = float(process_time)
                process_times.append(pt)
            except ValueError:
                process_times.append(0)
            
            # Extract wait time (skip first step)
            if i > 0 and wait_time:
                try:
                    wt = float(wait_time)
                    wait_times.append(wt)
                except ValueError:
                    pass
        
        total_pt = sum(process_times)
        total_wt = sum(wait_times)
        total_lt = total_pt + total_wt
        flow_efficiency = round((total_pt / total_lt * 100)) if total_lt > 0 else 0
        
        return {
            'PT': total_pt,
            'LT': total_lt,
            'FE': flow_efficiency
        }
    
    def validate_metrics(self, calculated, expected):
        """Validate calculated metrics against expected"""
        tolerance = 0.1
        pt_ok = abs(calculated['PT'] - expected['PT']) <= tolerance
        lt_ok = abs(calculated['LT'] - expected['LT']) <= tolerance
        fe_ok = abs(calculated['FE'] - expected['FE']) <= 1
        
        return pt_ok and lt_ok and fe_ok
    
    def generate_summary(self):
        """Generate test summary report"""
        print("=" * 60)
        print("TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Group by industry
        by_industry = {}
        for result in self.test_results:
            industry = result['industry']
            if industry not in by_industry:
                by_industry[industry] = []
            by_industry[industry].append(result)
        
        print("RESULTS BY INDUSTRY:")
        print("-" * 30)
        for industry, results in by_industry.items():
            industry_passed = sum(1 for r in results if r['passed'])
            print(f"{industry}: {industry_passed}/{len(results)} passed")
            
            for result in results:
                status = "✅" if result['passed'] else "❌"
                print(f"  {status} {result['name']} ({result['execution_time']:.2f}s)")
        
        print()
        print("FEATURE VALIDATION:")
        print("-" * 20)
        metrics_passed = sum(1 for r in self.test_results if r['metrics_valid'])
        preview_passed = sum(1 for r in self.test_results if r['preview_works'])
        export_passed = sum(1 for r in self.test_results if r['export_works'])
        
        print(f"✅ Metrics Calculation: {metrics_passed}/{total_tests} ({(metrics_passed/total_tests)*100:.1f}%)")
        print(f"✅ Preview Functionality: {preview_passed}/{total_tests} ({(preview_passed/total_tests)*100:.1f}%)")
        print(f"✅ Export Functionality: {export_passed}/{total_tests} ({(export_passed/total_tests)*100:.1f}%)")
        
        # Save report
        report_data = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': (passed_tests/total_tests)*100,
                'timestamp': datetime.now().isoformat(),
                'test_type': 'Demo User Acceptance Tests'
            },
            'results': self.test_results
        }
        
        # Create output directory
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        report_file = os.path.join(output_dir, f"vsm_demo_report_{datetime.now():%Y%m%d_%H%M%S}.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print()
        print(f"📊 Detailed report saved to: {report_file}")
        
        # Generate sample Mermaid output
        self.generate_sample_mermaid()
    
    def generate_sample_mermaid(self):
        """Generate sample Mermaid code for demonstration"""
        sample_scenario = self.test_results[0]  # Use first scenario
        
        print()
        print("SAMPLE GENERATED MERMAID CODE:")
        print("=" * 40)
        print(f"Scenario: {sample_scenario['name']}")
        print()
        
        mermaid_code = "graph LR\n"
        
        # Generate step connections
        steps = sample_scenario['steps']
        for i, (name, process_time, wait_time) in enumerate(steps):
            step_id = f"S{i}"
            mermaid_code += f'    {step_id}["{name}"]\n'
            
            if i < len(steps) - 1:
                next_step = f"S{i+1}"
                if i == len(steps) - 2:  # Last arrow shows process time
                    mermaid_code += f"    {step_id} -->|{process_time}| {next_step}\n"
                else:
                    mermaid_code += f"    {step_id} -->|{process_time}| {next_step}\n"
        
        # Add wait times
        mermaid_code += "\n    %% Add wait times\n"
        for i, (name, process_time, wait_time) in enumerate(steps[1:], 1):
            if wait_time:
                prev_step = f"S{i-1}"
                curr_step = f"S{i}"
                mermaid_code += f"    {prev_step} -.->|Wait: {wait_time}| {curr_step}\n"
        
        # Add metrics
        metrics = sample_scenario['calculated_metrics']
        mermaid_code += f"""
    %% Add process metrics
    subgraph Metrics
        PT[Process Time: {metrics['PT']} units]
        LT[Lead Time: {metrics['LT']} units]
        FE[Flow Efficiency: {metrics['FE']}%]
    end"""
        
        print("```mermaid")
        print(mermaid_code)
        print("```")
        
        # Save sample to file
        output_dir = "test_output"
        sample_file = os.path.join(output_dir, f"sample_mermaid_{datetime.now():%Y%m%d_%H%M%S}.md")
        with open(sample_file, 'w') as f:
            f.write(f"# {sample_scenario['name']}\n\n")
            f.write(f"**Industry:** {sample_scenario['industry']}\n\n")
            f.write(f"**Description:** {sample_scenario['description']}\n\n")
            f.write("## Value Stream Map\n\n")
            f.write("```mermaid\n")
            f.write(mermaid_code)
            f.write("\n```\n")
        
        print()
        print(f"📄 Sample Mermaid file saved to: {sample_file}")

def main():
    """Run the demo tests"""
    print("🚀 Starting VSM Generator User Acceptance Test Demo")
    print()
    print("This demonstration shows how the comprehensive user acceptance")
    print("test suite validates the VSM Generator application against")
    print("real-world business scenarios across multiple industries.")
    print()
    
    demo = MockVSMTest()
    demo.run_demo_tests()
    
    print()
    print("🎉 Demo completed successfully!")
    print()
    print("To run the full test suite against a live application:")
    print("1. Start the VSM Generator: docker run -d -p 8080:8080 buckeye90/vsm-generator-app")
    print("2. Run: python tests/test_user_acceptance.py")
    print("3. Or use: ./scripts/run_acceptance_tests.sh")

if __name__ == "__main__":
    main()