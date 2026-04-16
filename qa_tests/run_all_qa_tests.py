#!/usr/bin/env python3
"""
QA Test Runner - Run all QA tests in sequence

This script runs all QA tests to catch deployment issues BEFORE release:
1. Data Integrity Tests
2. API Endpoints Tests
3. Filter Functionality Tests
4. UI Elements Tests
5. Deployment Integrity Tests

Usage:
    python3 run_all_qa_tests.py
    python3 run_all_qa_tests.py --api-url http://localhost:8000

Exit codes:
    0 - All tests passed
    1 - Some tests failed
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
import time

# Test modules in order of execution
TEST_MODULES = [
    ('test_deployment_integrity.py', 'Deployment Integrity'),
    ('test_data_integrity.py', 'Data Integrity'),
    ('test_api_endpoints.py', 'API Endpoints'),
    ('test_filter_functionality.py', 'Filter Functionality'),
    ('test_ui_elements.py', 'UI Elements'),
]

def print_banner(text):
    """Print a formatted banner"""
    width = 70
    print("\n" + "=" * width)
    print(f" {text}".center(width))
    print("=" * width + "\n")

def print_section(text):
    """Print a section header"""
    print(f"\n{'─' * 70}")
    print(f" {text}")
    print(f"{'─' * 70}\n")

def run_test(test_file, test_name, qa_dir):
    """Run a single test module and return result"""
    test_path = qa_dir / test_file
    
    if not test_path.exists():
        print(f"❌ Test file not found: {test_file}")
        return False, f"File not found: {test_path}"
    
    print_section(f"Running: {test_name}")
    print(f"File: {test_file}\n")
    
    start_time = time.time()
    
    try:
        # Run the test as a subprocess
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per test
            cwd=str(qa_dir)
        )
        
        elapsed = time.time() - start_time
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        
        print(f"\n⏱️  Time: {elapsed:.2f}s")
        
        if success:
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED (exit code: {result.returncode})")
        
        return success, result.stdout
        
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name} TIMEOUT (>5 minutes)")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ {test_name} ERROR: {e}")
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(
        description='Run all QA tests before deployment'
    )
    parser.add_argument(
        '--api-url',
        default='http://localhost:8010',
        help='Base URL for API tests (default: http://localhost:8010)'
    )
    parser.add_argument(
        '--skip',
        nargs='+',
        choices=['integrity', 'data', 'api', 'filter', 'ui', 'deployment'],
        help='Skip specific test categories'
    )
    parser.add_argument(
        '--only',
        nargs='+',
        choices=['integrity', 'data', 'api', 'filter', 'ui', 'deployment'],
        help='Only run specific test categories'
    )
    
    args = parser.parse_args()
    
    # Set environment variable for API tests
    os.environ['API_BASE_URL'] = args.api_url
    
    # Find QA tests directory
    qa_dir = Path(__file__).parent
    
    print_banner("PRE-DEPLOYMENT QA TEST SUITE")
    print("This test suite catches deployment issues BEFORE release.")
    print("\nIssues caught by these tests:")
    print("  1. Data/Research Mismatch (3 conflicts found, only 1 deployed)")
    print("  2. Missing API Endpoint (/api/stats/quality caused 'chargement')")
    print("  3. Filter/Display Logic Mismatch")
    print(f"\nAPI Base URL: {args.api_url}")
    
    # Filter tests if needed
    tests_to_run = TEST_MODULES.copy()
    
    if args.only:
        name_map = {
            'integrity': 'test_deployment_integrity.py',
            'data': 'test_data_integrity.py',
            'api': 'test_api_endpoints.py',
            'filter': 'test_filter_functionality.py',
            'ui': 'test_ui_elements.py',
            'deployment': 'test_deployment_integrity.py',
        }
        tests_to_run = [(name_map[o], o.title()) for o in args.only if o in name_map]
    
    if args.skip:
        skip_files = {
            'integrity': 'test_deployment_integrity.py',
            'data': 'test_data_integrity.py',
            'api': 'test_api_endpoints.py',
            'filter': 'test_filter_functionality.py',
            'ui': 'test_ui_elements.py',
            'deployment': 'test_deployment_integrity.py',
        }
        tests_to_run = [
            (f, n) for f, n in tests_to_run 
            if f not in [skip_files[s] for s in args.skip]
        ]
    
    # Run all tests
    results = {}
    start_time = time.time()
    
    for test_file, test_name in tests_to_run:
        success, output = run_test(test_file, test_name, qa_dir)
        results[test_name] = success
    
    total_time = time.time() - start_time
    
    # Print summary
    print_banner("QA TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n{'─' * 70}")
    print(f"Results: {passed}/{total} test suites passed")
    print(f"Time: {total_time:.2f}s")
    print(f"{'─' * 70}\n")
    
    # Pre-deployment checklist
    print("Pre-Deployment Checklist:")
    checklist = [
        ("All QA tests pass", all(results.values())),
        ("No 'chargement' or loading states", results.get('UI Elements', True)),
        ("All filters return expected counts", results.get('Filter Functionality', True)),
        ("Workspace files match deployment", results.get('Deployment Integrity', True)),
        ("All research conflicts in deployed data", results.get('Data Integrity', True)),
    ]
    
    for item, status in checklist:
        mark = "✅" if status else "❌"
        print(f"  {mark} {item}")
    
    print()
    
    if all(results.values()):
        print("=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\nYou can proceed with deployment.")
        print("\nNext steps:")
        print("  1. Review test output above")
        print("  2. Commit any pending changes: git add -A && git commit -m '...'")
        print("  3. Push to GitHub: git push origin main")
        print("  4. Deploy: python3 deploy_enhanced.py")
        return 0
    else:
        print("=" * 70)
        print("❌ SOME TESTS FAILED!")
        print("=" * 70)
        print("\nPlease fix the issues above before deploying.")
        print("\nCommon fixes:")
        print("  - Missing API endpoint: Add the endpoint to server.py")
        print("  - Data mismatch: Sync research findings to data file")
        print("  - Loading states: Check API responses have actual values")
        return 1

if __name__ == '__main__':
    sys.exit(main())
